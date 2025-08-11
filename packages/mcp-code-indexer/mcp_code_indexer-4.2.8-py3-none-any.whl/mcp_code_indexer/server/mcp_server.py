"""
MCP Server implementation for the Code Indexer.

This module provides the main MCP server that handles JSON-RPC communication
for file description management tools.
"""

import asyncio
import html
import json
import logging
import random
import re
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, cast

from mcp import types
from mcp.server import Server
from pydantic import ValidationError

from mcp_code_indexer.cleanup_manager import CleanupManager
from mcp_code_indexer.database.database import DatabaseManager
from mcp_code_indexer.database.database_factory import DatabaseFactory
from mcp_code_indexer.database.models import (
    FileDescription,
    Project,
    ProjectOverview,
)
from mcp_code_indexer.error_handler import setup_error_handling
from mcp_code_indexer.file_scanner import FileScanner
from mcp_code_indexer.logging_config import get_logger
from mcp_code_indexer.middleware.error_middleware import (
    AsyncTaskManager,
    create_tool_middleware,
)
from mcp_code_indexer.token_counter import TokenCounter

logger = logging.getLogger(__name__)


class MCPCodeIndexServer:
    """
    MCP Code Index Server.

    Provides file description tracking and codebase navigation tools
    through the Model Context Protocol.
    """

    def __init__(
        self,
        token_limit: int = 32000,
        db_path: Optional[Path] = None,
        cache_dir: Optional[Path] = None,
        db_pool_size: int = 3,
        db_retry_count: int = 5,
        db_timeout: float = 10.0,
        enable_wal_mode: bool = True,
        health_check_interval: float = 30.0,
        retry_min_wait: float = 0.1,
        retry_max_wait: float = 2.0,
        retry_jitter: float = 0.2,
        transport: Optional[Any] = None,
        vector_mode: bool = False,
    ):
        """
        Initialize the MCP Code Index Server.

        Args:
            token_limit: Maximum tokens before recommending search over overview
            db_path: Path to SQLite database
            cache_dir: Directory for caching
            db_pool_size: Database connection pool size
            db_retry_count: Maximum database operation retry attempts
            db_timeout: Database transaction timeout in seconds
            enable_wal_mode: Enable WAL mode for better concurrent access
            health_check_interval: Database health check interval in seconds
            retry_min_wait: Minimum wait time between retries in seconds
            retry_max_wait: Maximum wait time between retries in seconds
            retry_jitter: Maximum jitter to add to retry delays in seconds
            transport: Optional transport instance (if None, uses default stdio)
            vector_mode: Enable vector search capabilities and tools
        """
        self.token_limit = token_limit
        self.db_path = db_path or Path.home() / ".mcp-code-index" / "tracker.db"
        self.cache_dir = cache_dir or Path.home() / ".mcp-code-index" / "cache"
        self.vector_mode = vector_mode

        # Store database configuration
        self.db_config = {
            "pool_size": db_pool_size,
            "retry_count": db_retry_count,
            "timeout": db_timeout,
            "enable_wal_mode": enable_wal_mode,
            "health_check_interval": health_check_interval,
            "retry_min_wait": retry_min_wait,
            "retry_max_wait": retry_max_wait,
            "retry_jitter": retry_jitter,
        }

        # Initialize components
        self.db_factory = DatabaseFactory(
            global_db_path=self.db_path,
            pool_size=db_pool_size,
            retry_count=db_retry_count,
            timeout=db_timeout,
            enable_wal_mode=enable_wal_mode,
            health_check_interval=health_check_interval,
            retry_min_wait=retry_min_wait,
            retry_max_wait=retry_max_wait,
            retry_jitter=retry_jitter,
        )
        # Keep reference to global db_manager for backwards compatibility
        self.db_manager: Optional[DatabaseManager] = None  # Will be set during run()
        self.token_counter = TokenCounter(token_limit)
        self.cleanup_manager: Optional[CleanupManager] = (
            None  # Will be set during initialize()
        )
        self.transport = transport

        # Setup error handling
        self.logger = get_logger(__name__)
        self.error_handler = setup_error_handling(self.logger)
        self.middleware = create_tool_middleware(self.error_handler)
        self.task_manager = AsyncTaskManager(self.error_handler)

        # Create MCP server
        self.server: Server = Server("mcp-code-indexer")

        # Register handlers
        self._register_handlers()

        # Background cleanup task tracking
        self._cleanup_task: Optional[asyncio.Task] = None
        self._last_cleanup_time: Optional[float] = None
        self._cleanup_running: bool = False

        # Add debug logging for server events
        self.logger.debug("MCP server instance created and handlers registered")

        self.logger.info(
            "MCP Code Index Server initialized",
            extra={"structured_data": {"initialization": {"token_limit": token_limit}}},
        )

    def _clean_html_entities(self, text: str) -> str:
        """
        Clean HTML entities from text to prevent encoding issues.

        Args:
            text: Text that may contain HTML entities

        Returns:
            Text with HTML entities decoded to proper characters
        """
        if not text:
            return text

        # Decode HTML entities like &lt; &gt; &amp; etc.
        return html.unescape(text)

    def _clean_arguments(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean HTML entities from all text arguments.

        Args:
            arguments: Dictionary of arguments to clean

        Returns:
            Dictionary with HTML entities decoded in all string values
        """
        cleaned: Dict[str, Any] = {}

        for key, value in arguments.items():
            if isinstance(value, str):
                cleaned[key] = self._clean_html_entities(value)
            elif isinstance(value, list):
                # Clean strings in lists (like conflict resolutions)
                cleaned[key] = [
                    self._clean_html_entities(item) if isinstance(item, str) else item
                    for item in value
                ]
            elif isinstance(value, dict):
                # Recursively clean nested dictionaries
                cleaned[key] = self._clean_arguments(value)
            else:
                # Pass through other types unchanged
                cleaned[key] = value

        return cleaned

    def _parse_json_robust(self, json_str: str) -> Dict[str, Any]:
        """
        Parse JSON with automatic repair for common issues.

        Args:
            json_str: JSON string that may have formatting issues

        Returns:
            Parsed JSON dictionary

        Raises:
            ValueError: If JSON cannot be parsed even after repair attempts
        """
        # First try normal parsing
        try:
            result = json.loads(json_str)
            if isinstance(result, dict):
                return result
            else:
                raise ValueError(f"Parsed JSON is not a dictionary: {type(result)}")
        except json.JSONDecodeError as original_error:
            logger.warning(f"Initial JSON parse failed: {original_error}")

            # Try to repair common issues
            repaired = json_str

            # Fix 1: Quote unquoted URLs and paths
            # Look for patterns like: "key": http://... or "key": /path/...
            url_pattern = r'("[\w]+"):\s*([a-zA-Z][a-zA-Z0-9+.-]*://[^\s,}]+|/[^\s,}]*)'
            repaired = re.sub(url_pattern, r'\1: "\2"', repaired)

            # Fix 2: Quote unquoted boolean-like strings
            # Look for: "key": true-ish-string or "key": false-ish-string
            bool_pattern = (
                r'("[\w]+"):\s*([a-zA-Z][a-zA-Z0-9_-]*[a-zA-Z0-9])(?=\s*[,}])'
            )
            repaired = re.sub(bool_pattern, r'\1: "\2"', repaired)

            # Fix 3: Remove trailing commas
            repaired = re.sub(r",(\s*[}\]])", r"\1", repaired)

            # Fix 4: Ensure proper string quoting for common unquoted values
            # Handle cases like: "key": value (where value should be "value")
            unquoted_pattern = r'("[\w]+"):\s*([a-zA-Z0-9_-]+)(?=\s*[,}])'
            repaired = re.sub(unquoted_pattern, r'\1: "\2"', repaired)

            try:
                result = json.loads(repaired)
                if isinstance(result, dict):
                    logger.info(
                        f"Successfully repaired JSON. Original: {json_str[:100]}..."
                    )
                    logger.info(f"Repaired: {repaired[:100]}...")
                    return result
                else:
                    raise ValueError(
                        f"Repaired JSON is not a dictionary: {type(result)}"
                    )
            except json.JSONDecodeError as repair_error:
                logger.error(f"JSON repair failed. Original: {json_str}")
                logger.error(f"Repaired attempt: {repaired}")
                raise ValueError(
                    f"Could not parse JSON even after repair attempts. "
                    f"Original error: {original_error}, Repair error: {repair_error}"
                )

    async def initialize(self) -> None:
        """Initialize database and other resources."""
        # Initialize global database manager for backwards compatibility
        self.db_manager = await self.db_factory.get_database_manager()
        # Update cleanup manager with initialized db_manager
        if self.db_manager is not None:
            self.cleanup_manager = CleanupManager(self.db_manager, retention_months=6)
        self._start_background_cleanup()
        logger.info("Server initialized successfully")

    def _register_handlers(self) -> None:
        """Register MCP tool and resource handlers."""

        @self.server.list_tools()  # type: ignore[misc]
        async def list_tools() -> List[types.Tool]:
            """Return list of available tools."""
            return [
                types.Tool(
                    name="get_file_description",
                    description=(
                        "Retrieves the stored description for a specific file in a "
                        "codebase. Use this to quickly understand what a file "
                        "contains without reading its full contents."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "projectName": {
                                "type": "string",
                                "description": "The name of the project",
                            },
                            "folderPath": {
                                "type": "string",
                                "description": (
                                    "Absolute path to the project folder on disk"
                                ),
                            },
                            "filePath": {
                                "type": "string",
                                "description": (
                                    "Relative path to the file from project root"
                                ),
                            },
                        },
                        "required": ["projectName", "folderPath", "filePath"],
                        "additionalProperties": False,
                    },
                ),
                types.Tool(
                    name="update_file_description",
                    description=(
                        "Creates or updates the description for a file. Use this "
                        "after analyzing a file's contents to store a detailed summary."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "projectName": {
                                "type": "string",
                                "description": "The name of the project",
                            },
                            "folderPath": {
                                "type": "string",
                                "description": (
                                    "Absolute path to the project folder on disk"
                                ),
                            },
                            "filePath": {
                                "type": "string",
                                "description": (
                                    "Relative path to the file from project root"
                                ),
                            },
                            "description": {
                                "type": "string",
                                "description": (
                                    "Detailed description of the file's contents"
                                ),
                            },
                            "fileHash": {
                                "type": "string",
                                "description": (
                                    "SHA-256 hash of the file contents (optional)"
                                ),
                            },
                        },
                        "required": [
                            "projectName",
                            "folderPath",
                            "filePath",
                            "description",
                        ],
                        "additionalProperties": False,
                    },
                ),
                types.Tool(
                    name="check_codebase_size",
                    description=(
                        "Checks the total token count of a codebase's file structure "
                        "and descriptions. Returns whether the codebase is 'large' "
                        "and recommends using search instead of the full overview."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "projectName": {
                                "type": "string",
                                "description": "The name of the project",
                            },
                            "folderPath": {
                                "type": "string",
                                "description": (
                                    "Absolute path to the project folder on disk"
                                ),
                            },
                            "tokenLimit": {
                                "type": "integer",
                                "description": (
                                    "Optional token limit override "
                                    "(defaults to server configuration)"
                                ),
                            },
                        },
                        "required": ["projectName", "folderPath"],
                        "additionalProperties": False,
                    },
                ),
                types.Tool(
                    name="find_missing_descriptions",
                    description=(
                        "Scans the project folder to find files that don't have "
                        "descriptions yet. Use update_file_description to add "
                        "descriptions for individual files."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "projectName": {
                                "type": "string",
                                "description": "The name of the project",
                            },
                            "folderPath": {
                                "type": "string",
                                "description": (
                                    "Absolute path to the project folder on disk"
                                ),
                            },
                            "limit": {
                                "type": "integer",
                                "description": (
                                    "Maximum number of missing files to return "
                                    "(optional)"
                                ),
                            },
                            "randomize": {
                                "type": "boolean",
                                "description": (
                                    "Randomly shuffle files before applying limit "
                                    "(useful for parallel processing, optional)"
                                ),
                            },
                        },
                        "required": ["projectName", "folderPath"],
                        "additionalProperties": False,
                    },
                ),
                types.Tool(
                    name="search_descriptions",
                    description=(
                        "Searches through all file descriptions in a project to find "
                        "files related to specific functionality. Use this for large "
                        "codebases instead of loading the entire structure. Always "
                        "start with the fewest terms possible (1 to 3 words AT MOST); "
                        "if the tool returns a lot of results (more than 20) or the "
                        "results are not relevant, then narrow it down by increasing "
                        "the number of search words one at a time and calling the tool "
                        "again. Start VERY broad, then narrow the focus only if needed!"
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "projectName": {
                                "type": "string",
                                "description": "The name of the project",
                            },
                            "folderPath": {
                                "type": "string",
                                "description": (
                                    "Absolute path to the project folder on disk"
                                ),
                            },
                            "query": {
                                "type": "string",
                                "description": (
                                    "Search query (e.g., 'authentication middleware', "
                                    "'database models')"
                                ),
                            },
                            "maxResults": {
                                "type": "integer",
                                "default": 20,
                                "description": "Maximum number of results to return",
                            },
                        },
                        "required": ["projectName", "folderPath", "query"],
                        "additionalProperties": False,
                    },
                ),
                types.Tool(
                    name="get_all_descriptions",
                    description=(
                        "Returns the complete file-by-file structure of a codebase "
                        "with individual descriptions for each file. For large "
                        "codebases, consider using get_codebase_overview for a "
                        "condensed summary instead."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "projectName": {
                                "type": "string",
                                "description": "The name of the project",
                            },
                            "folderPath": {
                                "type": "string",
                                "description": (
                                    "Absolute path to the project folder on disk"
                                ),
                            },
                        },
                        "required": ["projectName", "folderPath"],
                        "additionalProperties": False,
                    },
                ),
                types.Tool(
                    name="get_codebase_overview",
                    description=(
                        "Returns a condensed, interpretive overview of the entire "
                        "codebase. This is a single comprehensive narrative that "
                        "captures the architecture, key components, relationships, "
                        "and design patterns. Unlike get_all_descriptions which "
                        "lists every file, this provides a holistic view suitable "
                        "for understanding the codebase's structure and purpose. "
                        "If no overview exists, returns empty string."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "projectName": {
                                "type": "string",
                                "description": "The name of the project",
                            },
                            "folderPath": {
                                "type": "string",
                                "description": (
                                    "Absolute path to the project folder on disk"
                                ),
                            },
                        },
                        "required": ["projectName", "folderPath"],
                        "additionalProperties": False,
                    },
                ),
                types.Tool(
                    name="update_codebase_overview",
                    description=(
                        "Creates a concise codebase overview for AI agents. Focus on "
                        "essential navigation and context in 3500-7000 words. Include: "
                        "(1) One-paragraph system summary - what it does and its core "
                        "purpose, (2) Directory tree with one-line descriptions for "
                        "each major folder, (3) Key architectural patterns (e.g., MVC, "
                        "microservices, event-driven) in 2-3 sentences, (4) Critical "
                        "file locations (entry points, config, main business logic), "
                        "(5) Essential conventions (naming, file organization, error "
                        "handling), (6) Important gotchas or non-obvious connections. "
                        "Keep it scannable and action-oriented.\n\n"
                        "Example:\n\n"
                        "````\n"
                        "## System Summary\n"
                        "E-commerce platform handling product catalog, orders, "
                        "and payments with React frontend and Node.js API.\n\n"
                        "## Directory Structure\n"
                        "```\n"
                        "src/\n"
                        "├── api/          # REST endpoints "
                        "(auth in auth.js, orders in orders/)\n"
                        "├── models/       # Sequelize models "
                        "(User, Product, Order)\n"
                        "├── services/     # Stripe (payments/), "
                        "SendGrid (email/)\n"
                        "├── client/       # React app "
                        "(components/, pages/, hooks/)\n"
                        "└── shared/       # Types and constants used "
                        "by both API and client\n"
                        "```\n\n"
                        "## Architecture\n"
                        "RESTful API with JWT auth. React frontend calls API. "
                        "Background jobs via Bull queue. PostgreSQL with "
                        "Sequelize ORM.\n\n"
                        "## Key Files\n"
                        "- Entry: `src/index.js` "
                        "(starts Express server)\n"
                        "- Config: `src/config/` "
                        "(env-specific settings)\n"
                        "- Routes: `src/api/routes.js` "
                        "(all endpoints defined here)\n"
                        "- Auth: `src/middleware/auth.js` "
                        "(JWT validation)\n\n"
                        "## Conventions\n"
                        "- Files named `[entity].service.js` "
                        "handle business logic\n"
                        "- All API routes return "
                        "`{ success: boolean, data?: any, error?: string }`\n"
                        "- Database migrations in `migrations/` - "
                        "run before adding models\n\n"
                        "## Important Notes\n"
                        "- Payment webhooks MUST be idempotent "
                        "(check `processedWebhooks` table)\n"
                        "- User emails are case-insensitive "
                        "(lowercase in DB)\n"
                        "- Order status transitions enforced in "
                        "`Order.beforeUpdate` hook\n"
                        "````"
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "projectName": {
                                "type": "string",
                                "description": "The name of the project",
                            },
                            "folderPath": {
                                "type": "string",
                                "description": (
                                    "Absolute path to the project folder on disk"
                                ),
                            },
                            "overview": {
                                "type": "string",
                                "description": (
                                    "Concise codebase overview "
                                    "(aim for 3500-7500 words / 5k-10k tokens)"
                                ),
                            },
                        },
                        "required": ["projectName", "folderPath", "overview"],
                        "additionalProperties": False,
                    },
                ),
                types.Tool(
                    name="get_word_frequency",
                    description=(
                        "Analyzes all file descriptions to find the most frequently "
                        "used technical terms. Filters out common English stop words "
                        "and symbols, returning the top 200 meaningful terms. Useful "
                        "for understanding the codebase's domain vocabulary and "
                        "finding all functions/files related to specific concepts."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "projectName": {
                                "type": "string",
                                "description": "The name of the project",
                            },
                            "folderPath": {
                                "type": "string",
                                "description": (
                                    "Absolute path to the project folder on disk"
                                ),
                            },
                            "limit": {
                                "type": "integer",
                                "default": 200,
                                "description": "Number of top terms to return",
                            },
                        },
                        "required": ["projectName", "folderPath"],
                        "additionalProperties": False,
                    },
                ),
                types.Tool(
                    name="check_database_health",
                    description=(
                        "Perform health diagnostics for the MCP Code Indexer's SQLite "
                        "database and connection pool. Returns database resilience "
                        "metrics, connection pool status, WAL mode performance, and "
                        "file description storage statistics for monitoring the code "
                        "indexer's database locking improvements."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False,
                    },
                ),
                types.Tool(
                    name="search_codebase_overview",
                    description=(
                        "Search for a single word in the codebase overview and return "
                        "2 sentences before and after where the word is found. Useful "
                        "for quickly finding specific information in large overviews."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "projectName": {
                                "type": "string",
                                "description": "The name of the project",
                            },
                            "folderPath": {
                                "type": "string",
                                "description": (
                                    "Absolute path to the project folder on disk"
                                ),
                            },
                            "searchWord": {
                                "type": "string",
                                "description": (
                                    "Single word to search for in the overview"
                                ),
                            },
                        },
                        "required": ["projectName", "folderPath", "searchWord"],
                        "additionalProperties": False,
                    },
                ),
            ]

        @self.server.call_tool()  # type: ignore[misc]
        async def call_tool(
            name: str, arguments: Dict[str, Any]
        ) -> List[types.TextContent]:
            """Handle tool calls with middleware."""
            import time

            start_time = time.time()

            logger.info(f"=== MCP Tool Call: {name} ===")
            logger.info(f"Arguments: {', '.join(arguments.keys())}")

            # Map tool names to handler methods
            tool_handlers = {
                "get_file_description": self._handle_get_file_description,
                "update_file_description": self._handle_update_file_description,
                "check_codebase_size": self._handle_check_codebase_size,
                "find_missing_descriptions": self._handle_find_missing_descriptions,
                "search_descriptions": self._handle_search_descriptions,
                "get_all_descriptions": self._handle_get_codebase_overview,
                "get_codebase_overview": self._handle_get_condensed_overview,
                "update_codebase_overview": self._handle_update_codebase_overview,
                "get_word_frequency": self._handle_get_word_frequency,
                "check_database_health": self._handle_check_database_health,
                "search_codebase_overview": self._handle_search_codebase_overview,
            }

            if name not in tool_handlers:
                logger.error(f"Unknown tool requested: {name}")
                from ..error_handler import ValidationError

                raise ValidationError(f"Unknown tool: {name}")

            # Wrap handler with middleware
            wrapped_handler = self.middleware.wrap_tool_handler(name)(
                lambda args: self._execute_tool_handler(tool_handlers[name], args)
            )

            try:
                result = await wrapped_handler(arguments)

                elapsed_time = time.time() - start_time
                logger.info(
                    f"MCP Tool '{name}' completed successfully in {elapsed_time:.2f}s"
                )

                # Ensure result is List[types.TextContent]
                if isinstance(result, list) and all(
                    isinstance(item, types.TextContent) for item in result
                ):
                    return result
                else:
                    # Fallback: convert to proper format
                    return [types.TextContent(type="text", text=str(result))]
            except Exception as e:
                elapsed_time = time.time() - start_time
                logger.error(f"MCP Tool '{name}' failed after {elapsed_time:.2f}s: {e}")
                logger.error(f"Exception details: {type(e).__name__}: {str(e)}")
                raise

    async def _execute_tool_handler(
        self, handler: Callable[[Dict[str, Any]], Any], arguments: Dict[str, Any]
    ) -> List[types.TextContent]:
        """Execute a tool handler and format the result."""
        # Clean HTML entities from all arguments before processing
        cleaned_arguments = self._clean_arguments(arguments)

        result = await handler(cleaned_arguments)

        return [
            types.TextContent(
                type="text", text=json.dumps(result, indent=2, default=str)
            )
        ]

    async def _get_or_create_project_id(self, arguments: Dict[str, Any]) -> str:
        """
        Get or create a project ID using intelligent matching.

        For local databases: Uses the single project in the database (ignores paths).
        For global databases: Matches projects based on name and folder path aliases.
        """
        project_name = arguments["projectName"]
        folder_path = arguments["folderPath"]

        # Get the appropriate database manager for this folder
        db_manager = await self.db_factory.get_database_manager(folder_path)

        # Check if this is a local database
        is_local = self.db_factory.get_path_resolver().is_local_database(folder_path)

        if is_local:
            # For local databases: just get the single project (there should only be one)
            all_projects = await db_manager.get_all_projects()
            if all_projects:
                project = all_projects[0]  # Use the first (and should be only) project
                # Update last accessed time
                await db_manager.update_project_access_time(project.id)
                logger.info(
                    f"Using existing local project: {project.name} (ID: {project.id})"
                )
                return project.id
            else:
                # No project in local database - create one
                project_id = str(uuid.uuid4())
                project = Project(
                    id=project_id,
                    name=project_name.lower(),
                    aliases=[
                        folder_path
                    ],  # Store for reference but don't rely on it for matching
                    created=datetime.utcnow(),
                    last_accessed=datetime.utcnow(),
                )
                await db_manager.create_project(project)
                logger.info(
                    f"Created new local project: {project_name} (ID: {project_id})"
                )
                return project_id
        else:
            # For global databases: use the existing matching logic
            normalized_name = project_name.lower()

            # Find potential project matches
            project = await self._find_matching_project(  # type: ignore[assignment]
                normalized_name, folder_path, db_manager
            )
            if project:
                # Update project metadata and aliases
                await self._update_existing_project(
                    project, normalized_name, folder_path, db_manager
                )
            else:
                # Create new project with UUID
                project_id = str(uuid.uuid4())
                project = Project(
                    id=project_id,
                    name=normalized_name,
                    aliases=[folder_path],
                    created=datetime.utcnow(),
                    last_accessed=datetime.utcnow(),
                )
                await db_manager.create_project(project)
                logger.info(
                    f"Created new global project: {normalized_name} (ID: {project_id})"
                )

            if project is None:
                raise RuntimeError("Project should always be set in if/else branches above")
            return project.id

    async def _find_matching_project(
        self, normalized_name: str, folder_path: str, db_manager: DatabaseManager
    ) -> Optional[Project]:
        """
        Find a matching project using name and folder path matching.

        Returns the best matching project or None if no sufficient match is found.
        """
        all_projects = await db_manager.get_all_projects()

        best_match = None
        best_score = 0

        for project in all_projects:
            score = 0
            match_factors = []

            # Factor 1: Project name match (primary identifier)
            if project.name.lower() == normalized_name:
                score += 2  # Higher weight for name match
                match_factors.append("name")

            # Factor 2: Folder path in aliases
            project_aliases = project.aliases
            if folder_path in project_aliases:
                score += 1
                match_factors.append("folder_path")

            # If we have a name match, it's a strong candidate
            if score >= 2:
                if score > best_score:
                    best_score = score
                    best_match = project
                    logger.info(
                        f"Match for project {project.name} "
                        f"(score: {score}, factors: {match_factors})"
                    )

            # If only name matches, check file similarity for potential matches
            elif score == 1 and "name" in match_factors:
                if await self._check_file_similarity(project, folder_path):
                    logger.info(
                        f"File similarity match for project {project.name} "
                        f"(factor: {match_factors[0]})"
                    )
                    if score > best_score:
                        best_score = score
                        best_match = project

        return best_match

    async def _check_file_similarity(self, project: Project, folder_path: str) -> bool:
        """
        Check if the files in the folder are similar to files already indexed
        for this project.
        Returns True if 80%+ of files match.
        """
        try:
            # Get files currently in the folder
            scanner = FileScanner(Path(folder_path))
            if not scanner.is_valid_project_directory():
                return False

            current_files = scanner.scan_directory()
            current_basenames = {f.name for f in current_files}

            if not current_basenames:
                return False

            # Get appropriate database manager for this folder
            db_manager = await self.db_factory.get_database_manager(folder_path)

            # Get files already indexed for this project
            indexed_files = await db_manager.get_all_file_descriptions(project.id)
            indexed_basenames = {Path(fd.file_path).name for fd in indexed_files}

            if not indexed_basenames:
                return False

            # Calculate similarity
            intersection = current_basenames & indexed_basenames
            similarity = len(intersection) / len(current_basenames)

            logger.debug(
                f"File similarity for {project.name}: {similarity:.2%} "
                f"({len(intersection)}/{len(current_basenames)} files match)"
            )

            return similarity >= 0.8
        except Exception as e:
            logger.warning(f"Error checking file similarity: {e}")
            return False

    async def _update_existing_project(
        self,
        project: Project,
        normalized_name: str,
        folder_path: str,
        db_manager: DatabaseManager,
    ) -> None:
        """Update an existing project with new metadata and folder alias."""
        # Update last accessed time
        await db_manager.update_project_access_time(project.id)

        should_update = False

        # Update name if different
        if project.name != normalized_name:
            project.name = normalized_name
            should_update = True

        # Add folder path to aliases if not already present
        project_aliases = project.aliases
        if folder_path not in project_aliases:
            project_aliases.append(folder_path)
            project.aliases = project_aliases
            should_update = True
            logger.info(
                f"Added new folder alias to project {project.name}: {folder_path}"
            )

        if should_update:
            await db_manager.update_project(project)
            logger.debug(f"Updated project metadata for {project.name}")

    async def _handle_get_file_description(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle get_file_description tool calls."""
        folder_path = arguments["folderPath"]
        db_manager = await self.db_factory.get_database_manager(folder_path)
        project_id = await self._get_or_create_project_id(arguments)

        file_desc = await db_manager.get_file_description(
            project_id=project_id, file_path=arguments["filePath"]
        )

        if file_desc:
            return {
                "exists": True,
                "description": file_desc.description,
                "lastModified": file_desc.last_modified.isoformat(),
                "fileHash": file_desc.file_hash,
                "version": file_desc.version,
            }
        else:
            return {
                "exists": False,
                "message": f"No description found for {arguments['filePath']}",
            }

    async def _handle_update_file_description(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle update_file_description tool calls."""
        logger.info(f"Updating file description for: {arguments['filePath']}")
        logger.info(f"Project: {arguments.get('projectName', 'Unknown')}")

        description_length = len(arguments.get("description", ""))
        logger.info(f"Description length: {description_length} characters")

        folder_path = arguments["folderPath"]
        db_manager = await self.db_factory.get_database_manager(folder_path)
        project_id = await self._get_or_create_project_id(arguments)

        logger.info(f"Resolved project_id: {project_id}")

        file_desc = FileDescription(
            id=None,  # Will be set by database
            project_id=project_id,
            file_path=arguments["filePath"],
            description=arguments["description"],
            file_hash=arguments.get("fileHash"),
            last_modified=datetime.utcnow(),
            version=1,
            source_project_id=None,
            to_be_cleaned=None,
        )

        await db_manager.create_file_description(file_desc)

        logger.info(f"Successfully updated description for: {arguments['filePath']}")

        return {
            "success": True,
            "message": f"Description updated for {arguments['filePath']}",
            "filePath": arguments["filePath"],
            "lastModified": file_desc.last_modified.isoformat(),
        }

    async def _handle_check_codebase_size(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle check_codebase_size tool calls."""
        logger.info(
            f"Checking codebase size for: {arguments.get('projectName', 'Unknown')}"
        )
        logger.info(f"Folder path: {arguments.get('folderPath', 'Unknown')}")

        folder_path = arguments["folderPath"]
        db_manager = await self.db_factory.get_database_manager(folder_path)
        project_id = await self._get_or_create_project_id(arguments)
        folder_path_obj = Path(folder_path)

        logger.info(f"Resolved project_id: {project_id}")

        # Run cleanup if needed (respects 30-minute cooldown)
        cleaned_up_count = await self._run_cleanup_if_needed(
            project_id=project_id, project_root=folder_path_obj
        )

        # Get file descriptions for this project (after cleanup)
        logger.info("Retrieving file descriptions...")
        file_descriptions = await db_manager.get_all_file_descriptions(
            project_id=project_id
        )
        logger.info(f"Found {len(file_descriptions)} file descriptions")

        # Use provided token limit or fall back to server default
        token_limit = arguments.get("tokenLimit", self.token_limit)

        # Calculate total tokens for descriptions
        logger.info("Calculating total token count...")
        descriptions_tokens = self.token_counter.calculate_codebase_tokens(
            file_descriptions
        )

        # Get overview tokens if available
        overview = await db_manager.get_project_overview(project_id)
        overview_tokens = 0
        if overview and overview.overview:
            overview_tokens = self.token_counter.count_tokens(overview.overview)

        total_tokens = descriptions_tokens + overview_tokens
        is_large = total_tokens > token_limit

        # Smart recommendation logic:
        # - If total is small, use overview
        # - If total is large but overview is reasonable (< 8k tokens), recommend viewing overview + search
        # - If both are large, use search only
        overview_size_limit = 32000

        if not is_large:
            recommendation = "use_overview"
        elif overview_tokens > 0 and overview_tokens <= overview_size_limit:
            recommendation = "view_overview_then_search"
        else:
            recommendation = "use_search"

        logger.info(
            f"Codebase analysis complete: {total_tokens} tokens total "
            f"({descriptions_tokens} descriptions + {overview_tokens} overview), "
            f"{len(file_descriptions)} files"
        )
        logger.info(
            f"Size assessment: {'LARGE' if is_large else 'SMALL'} "
            f"(limit: {token_limit})"
        )
        logger.info(f"Recommendation: {recommendation}")

        return {
            "fileDescriptionTokens": descriptions_tokens,
            "overviewTokens": overview_tokens,
            "isLarge": is_large,
            "recommendation": recommendation,
            "tokenLimit": token_limit,
            "totalFiles": len(file_descriptions),
            "cleanedUpCount": cleaned_up_count,
        }

    async def _handle_find_missing_descriptions(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle find_missing_descriptions tool calls."""
        logger.info(
            f"Finding missing descriptions for: "
            f"{arguments.get('projectName', 'Unknown')}"
        )
        logger.info(f"Folder path: {arguments.get('folderPath', 'Unknown')}")

        folder_path = arguments["folderPath"]
        db_manager = await self.db_factory.get_database_manager(folder_path)
        project_id = await self._get_or_create_project_id(arguments)
        folder_path_obj = Path(folder_path)

        logger.info(f"Resolved project_id: {project_id}")

        # Get existing file descriptions
        logger.info("Retrieving existing file descriptions...")
        existing_descriptions = await db_manager.get_all_file_descriptions(
            project_id=project_id
        )
        existing_paths = {desc.file_path for desc in existing_descriptions}
        logger.info(f"Found {len(existing_paths)} existing descriptions")

        # Scan directory for files
        logger.info(f"Scanning project directory: {folder_path_obj}")
        scanner = FileScanner(folder_path_obj)
        if not scanner.is_valid_project_directory():
            logger.error(
                f"Invalid or inaccessible project directory: {folder_path_obj}"
            )
            return {
                "error": f"Invalid or inaccessible project directory: {folder_path_obj}"
            }

        missing_files = scanner.find_missing_files(existing_paths)
        missing_paths = [scanner.get_relative_path(f) for f in missing_files]

        logger.info(f"Found {len(missing_paths)} files without descriptions")

        # Apply randomization if specified
        randomize = arguments.get("randomize", False)
        if randomize:
            random.shuffle(missing_paths)
            logger.info("Randomized file order for parallel processing")

        # Apply limit if specified
        limit = arguments.get("limit")
        total_missing = len(missing_paths)
        if limit is not None and isinstance(limit, int) and limit > 0:
            missing_paths = missing_paths[:limit]
            logger.info(f"Applied limit {limit}, returning {len(missing_paths)} files")

        # Get project stats
        stats = scanner.get_project_stats()
        logger.info(f"Project stats: {stats.get('total_files', 0)} total files")

        return {
            "missingFiles": missing_paths,
            "totalMissing": total_missing,
            "returnedCount": len(missing_paths),
            "existingDescriptions": len(existing_paths),
            "projectStats": stats,
        }

    async def _handle_search_descriptions(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle search_descriptions tool calls."""
        folder_path = arguments["folderPath"]
        db_manager = await self.db_factory.get_database_manager(folder_path)
        project_id = await self._get_or_create_project_id(arguments)
        max_results = arguments.get("maxResults", 20)

        # Perform search
        search_results = await db_manager.search_file_descriptions(
            project_id=project_id, query=arguments["query"], max_results=max_results
        )

        # Format results
        formatted_results = []
        for result in search_results:
            formatted_results.append(
                {
                    "filePath": result.file_path,
                    "description": result.description,
                    "relevanceScore": result.relevance_score,
                }
            )

        return {
            "results": formatted_results,
            "totalResults": len(formatted_results),
            "query": arguments["query"],
            "maxResults": max_results,
        }

    async def _handle_get_codebase_overview(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle get_codebase_overview tool calls."""
        folder_path = arguments["folderPath"]
        db_manager = await self.db_factory.get_database_manager(folder_path)
        project_id = await self._get_or_create_project_id(arguments)

        # Get all file descriptions
        file_descriptions = await db_manager.get_all_file_descriptions(
            project_id=project_id
        )

        # Calculate total tokens
        total_tokens = self.token_counter.calculate_codebase_tokens(file_descriptions)
        is_large = self.token_counter.is_large_codebase(total_tokens)

        # Always build and return the folder structure - if the AI called this
        # tool, it wants the overview
        structure = self._build_folder_structure(file_descriptions)

        return {
            "projectName": arguments["projectName"],
            "totalFiles": len(file_descriptions),
            "totalTokens": total_tokens,
            "isLarge": is_large,
            "tokenLimit": self.token_counter.token_limit,
            "structure": structure,
        }

    def _build_folder_structure(
        self, file_descriptions: List[FileDescription]
    ) -> Dict[str, Any]:
        """Build hierarchical folder structure from file descriptions."""
        root = {"path": "", "files": [], "folders": {}}

        for file_desc in file_descriptions:
            path_parts = cast(List[str], list(Path(file_desc.file_path).parts))
            current = root

            # Navigate/create folder structure
            for i, part in enumerate(path_parts[:-1]):
                folder_path = "/".join(path_parts[: i + 1])
                if part not in current["folders"]:
                    current["folders"][part] = {  # type: ignore[index]
                        "path": folder_path,
                        "files": [],
                        "folders": {},
                    }
                current = current["folders"][part]  # type: ignore[index]

            # Add file to current folder
            if path_parts:  # Handle empty paths
                current["files"].append(  # type: ignore[attr-defined]
                    {"path": file_desc.file_path, "description": file_desc.description}
                )

        # Convert nested dict structure to list format, skipping empty folders
        def convert_structure(node: Dict[str, Any]) -> Dict[str, Any]:
            folders = []
            for folder in node["folders"].values():
                converted_folder = convert_structure(folder)
                # Only include folders that have files or non-empty subfolders
                if converted_folder["files"] or converted_folder["folders"]:
                    folders.append(converted_folder)

            return {"path": node["path"], "files": node["files"], "folders": folders}

        return convert_structure(root)

    async def _handle_get_condensed_overview(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle get_codebase_overview tool calls for condensed overviews."""
        folder_path = arguments["folderPath"]
        db_manager = await self.db_factory.get_database_manager(folder_path)
        project_id = await self._get_or_create_project_id(arguments)

        # Try to get existing overview
        overview = await db_manager.get_project_overview(project_id)

        if overview:
            return {
                "overview": overview.overview,
                "lastModified": overview.last_modified.isoformat(),
                "totalFiles": overview.total_files,
                "totalTokensInFullDescriptions": overview.total_tokens,
            }
        else:
            return {
                "overview": "",
                "lastModified": "",
                "totalFiles": 0,
                "totalTokensInFullDescriptions": 0,
            }

    async def _handle_update_codebase_overview(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle update_codebase_overview tool calls."""
        folder_path = arguments["folderPath"]
        db_manager = await self.db_factory.get_database_manager(folder_path)
        project_id = await self._get_or_create_project_id(arguments)

        # Get current file count and total tokens for context
        file_descriptions = await db_manager.get_all_file_descriptions(
            project_id=project_id
        )

        total_files = len(file_descriptions)
        total_tokens = self.token_counter.calculate_codebase_tokens(file_descriptions)

        # Create overview record
        overview = ProjectOverview(
            project_id=project_id,
            overview=arguments["overview"],
            last_modified=datetime.utcnow(),
            total_files=total_files,
            total_tokens=total_tokens,
        )

        await db_manager.create_project_overview(overview)

        return {
            "success": True,
            "message": f"Overview updated for {total_files} files",
            "totalFiles": total_files,
            "totalTokens": total_tokens,
            "overviewLength": len(arguments["overview"]),
        }

    async def _handle_get_word_frequency(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle get_word_frequency tool calls."""
        folder_path = arguments["folderPath"]
        db_manager = await self.db_factory.get_database_manager(folder_path)
        project_id = await self._get_or_create_project_id(arguments)
        limit = arguments.get("limit", 200)

        # Analyze word frequency
        result = await db_manager.analyze_word_frequency(
            project_id=project_id, limit=limit
        )

        return {
            "topTerms": [
                {"term": term.term, "frequency": term.frequency}
                for term in result.top_terms
            ],
            "totalTermsAnalyzed": result.total_terms_analyzed,
            "totalUniqueTerms": result.total_unique_terms,
        }

    async def _handle_search_codebase_overview(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle search_codebase_overview tool calls."""
        folder_path = arguments["folderPath"]
        db_manager = await self.db_factory.get_database_manager(folder_path)
        project_id = await self._get_or_create_project_id(arguments)
        search_word = arguments["searchWord"].lower()

        # Get the overview
        overview = await db_manager.get_project_overview(project_id)

        if not overview or not overview.overview:
            return {
                "found": False,
                "message": "No overview found for this project",
                "searchWord": arguments["searchWord"],
            }

        # Split overview into sentences
        import re

        sentences = re.split(r"[.!?]+", overview.overview)
        sentences = [s.strip() for s in sentences if s.strip()]

        # Find matches
        matches = []
        for i, sentence in enumerate(sentences):
            if search_word in sentence.lower():
                # Get context: 2 sentences before and after
                start_idx = max(0, i - 2)
                end_idx = min(len(sentences), i + 3)

                context_sentences = sentences[start_idx:end_idx]
                context = ". ".join(context_sentences) + "."

                matches.append(
                    {
                        "matchIndex": i,
                        "matchSentence": sentence,
                        "context": context,
                        "contextStartIndex": start_idx,
                        "contextEndIndex": end_idx - 1,
                    }
                )

        return {
            "found": len(matches) > 0,
            "searchWord": arguments["searchWord"],
            "matches": matches,
            "totalMatches": len(matches),
            "totalSentences": len(sentences),
        }

    async def _handle_check_database_health(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle check_database_health tool calls with comprehensive diagnostics.

        Returns detailed database health information including retry statistics,
        performance analysis, and resilience indicators.
        """
        # Get comprehensive health diagnostics from the enhanced monitor
        if (
            self.db_manager
            and hasattr(self.db_manager, "_health_monitor")
            and self.db_manager._health_monitor
        ):
            comprehensive_diagnostics = (
                self.db_manager._health_monitor.get_comprehensive_diagnostics()
            )
        elif self.db_manager:
            # Fallback to basic health check if monitor not available
            health_check = await self.db_manager.check_health()
            comprehensive_diagnostics = {
                "basic_health_check": health_check,
                "note": "Enhanced health monitoring not available",
            }
        else:
            comprehensive_diagnostics = {
                "error": "Database manager not initialized",
            }

        # Get additional database-level statistics
        database_stats = self.db_manager.get_database_stats() if self.db_manager else {}

        return {
            "is_healthy": comprehensive_diagnostics.get("current_status", {}).get(
                "is_healthy", True
            ),
            "status": comprehensive_diagnostics.get("current_status", {}),
            "performance": {
                "avg_response_time_ms": comprehensive_diagnostics.get(
                    "metrics", {}
                ).get("avg_response_time_ms", 0),
                "success_rate": comprehensive_diagnostics.get("current_status", {}).get(
                    "recent_success_rate_percent", 100
                ),
            },
            "database": {
                "total_operations": database_stats.get("retry_executor", {}).get(
                    "total_operations", 0
                ),
                "pool_size": database_stats.get("connection_pool", {}).get(
                    "current_size", 0
                ),
            },
            "server_info": {
                "token_limit": self.token_limit,
                "db_path": str(self.db_path),
                "cache_dir": str(self.cache_dir),
                "health_monitoring_enabled": (
                    self.db_manager is not None
                    and hasattr(self.db_manager, "_health_monitor")
                    and self.db_manager._health_monitor is not None
                ),
            },
            "timestamp": datetime.utcnow().isoformat(),
            "status_summary": self._generate_health_summary(comprehensive_diagnostics),
        }

    def _generate_health_summary(self, diagnostics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a concise health summary from comprehensive diagnostics."""
        if "resilience_indicators" not in diagnostics:
            return {"status": "limited_diagnostics_available"}

        resilience = diagnostics["resilience_indicators"]
        performance = diagnostics.get("performance_analysis", {})

        # Overall status based on health score
        health_score = resilience.get("overall_health_score", 0)
        if health_score >= 90:
            status = "excellent"
        elif health_score >= 75:
            status = "good"
        elif health_score >= 50:
            status = "fair"
        else:
            status = "poor"

        return {
            "overall_status": status,
            "health_score": health_score,
            "retry_effectiveness": resilience.get("retry_effectiveness", {}).get(
                "is_effective", False
            ),
            "connection_stability": resilience.get("connection_stability", {}).get(
                "is_stable", False
            ),
            "key_recommendations": resilience.get("recommendations", [])[
                :3
            ],  # Top 3 recommendations
            "performance_trend": performance.get("health_check_performance", {}).get(
                "recent_performance_trend", "unknown"
            ),
        }

    async def _run_session_with_retry(
        self, read_stream: Any, write_stream: Any, initialization_options: Any
    ) -> None:
        """Run a single MCP session with error handling and retry logic."""
        max_retries = 3
        base_delay = 1.0  # seconds

        for attempt in range(max_retries + 1):
            try:
                logger.info(
                    f"Starting MCP server protocol session (attempt {attempt + 1})..."
                )
                await self.server.run(read_stream, write_stream, initialization_options)
                logger.info("MCP server session completed normally")
                return  # Success, exit retry loop

            except ValidationError as e:
                # Handle malformed requests gracefully
                logger.warning(
                    f"Received malformed request (attempt {attempt + 1}): {e}",
                    extra={
                        "structured_data": {
                            "error_type": "ValidationError",
                            "validation_errors": (
                                e.errors() if hasattr(e, "errors") else str(e)
                            ),
                            "attempt": attempt + 1,
                            "max_retries": max_retries,
                        }
                    },
                )

                if attempt < max_retries:
                    delay = base_delay * (2**attempt)  # Exponential backoff
                    logger.info(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        "Max retries exceeded for validation errors. Server will "
                        "continue but this session failed."
                    )
                    return

            except (ConnectionError, BrokenPipeError, EOFError) as e:
                # Handle client disconnection gracefully
                logger.info(f"Client disconnected: {e}")
                return

            except Exception as e:
                # Handle other exceptions with full logging
                import traceback

                if "unhandled errors in a TaskGroup" in str(
                    e
                ) and "ValidationError" in str(e):
                    # This is likely a ValidationError wrapped in a TaskGroup exception
                    logger.warning(
                        f"Detected wrapped validation error "
                        f"(attempt {attempt + 1}): {e}",
                        extra={
                            "structured_data": {
                                "error_type": type(e).__name__,
                                "error_message": str(e),
                                "attempt": attempt + 1,
                                "max_retries": max_retries,
                                "likely_validation_error": True,
                            }
                        },
                    )

                    if attempt < max_retries:
                        delay = base_delay * (2**attempt)
                        logger.info(f"Retrying in {delay} seconds...")
                        await asyncio.sleep(delay)
                    else:
                        logger.error(
                            "Max retries exceeded for validation errors. Server will "
                            "continue but this session failed."
                        )
                        return
                else:
                    # This is a genuine error, log and re-raise
                    logger.error(
                        f"MCP server session error: {e}",
                        extra={
                            "structured_data": {
                                "error_type": type(e).__name__,
                                "error_message": str(e),
                                "traceback": traceback.format_exc(),
                            }
                        },
                    )
                    raise

    async def _periodic_cleanup(self) -> None:
        """Background task that performs cleanup every 6 hours."""
        while True:
            try:
                await asyncio.sleep(6 * 60 * 60)  # 6 hours
                await self._run_cleanup_if_needed()

            except asyncio.CancelledError:
                logger.info("Periodic cleanup task cancelled")
                break
            except Exception as e:
                logger.error(f"Error in periodic cleanup: {e}")
                # Continue running despite errors

    async def _run_cleanup_if_needed(
        self, project_id: Optional[str] = None, project_root: Optional[Path] = None
    ) -> int:
        """Run cleanup if conditions are met (not running, not run recently)."""
        current_time = time.time()

        # Check if cleanup is already running
        if self._cleanup_running:
            logger.debug("Cleanup already running, skipping")
            return 0

        # Check if cleanup was run in the last 30 minutes
        if self._last_cleanup_time and current_time - self._last_cleanup_time < 30 * 60:
            logger.debug("Cleanup ran recently, skipping")
            return 0

        # Set running flag and update time
        self._cleanup_running = True
        self._last_cleanup_time = current_time

        try:
            logger.info("Starting cleanup")
            total_cleaned = 0

            if project_id and project_root:
                # Single project cleanup - use appropriate database for this project's folder
                try:
                    folder_db_manager = await self.db_factory.get_database_manager(
                        str(project_root)
                    )
                    missing_files = await folder_db_manager.cleanup_missing_files(
                        project_id=project_id, project_root=project_root
                    )
                    total_cleaned = len(missing_files)

                    # Perform permanent cleanup (retention policy)
                    deleted_count = 0
                    if self.cleanup_manager:
                        deleted_count = await self.cleanup_manager.perform_cleanup(
                            project_id=project_id
                        )

                    if missing_files or deleted_count:
                        logger.info(
                            f"Cleanup: {len(missing_files)} marked, "
                            f"{deleted_count} permanently deleted"
                        )
                except Exception as e:
                    logger.error(f"Error during cleanup: {e}")
            else:
                # All projects cleanup (for periodic task) - start with global database
                if not self.db_manager:
                    logger.error("Database manager not initialized")
                    return 0
                projects = await self.db_manager.get_all_projects()

                for project in projects:
                    try:
                        # Skip projects without folder paths in aliases
                        if not project.aliases:
                            continue

                        # Use first alias as folder path
                        folder_path = Path(project.aliases[0])
                        if not folder_path.exists():
                            continue

                        # Get appropriate database manager for this project's folder
                        project_db_manager = await self.db_factory.get_database_manager(
                            str(folder_path)
                        )
                        missing_files = await project_db_manager.cleanup_missing_files(
                            project_id=project.id, project_root=folder_path
                        )
                        total_cleaned += len(missing_files)

                        # Perform permanent cleanup (retention policy)
                        deleted_count = 0
                        if self.cleanup_manager:
                            deleted_count = await self.cleanup_manager.perform_cleanup(
                                project_id=project.id
                            )

                        if missing_files or deleted_count:
                            logger.info(
                                f"Cleanup for {project.name}: "
                                f"{len(missing_files)} marked, "
                                f"{deleted_count} permanently deleted"
                            )
                    except Exception as e:
                        logger.error(
                            f"Error during cleanup for project {project.name}: {e}"
                        )

            logger.info(f"Cleanup completed: {total_cleaned} files processed")
            return total_cleaned

        finally:
            self._cleanup_running = False

    def _start_background_cleanup(self) -> None:
        """Start the background cleanup task."""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = self.task_manager.create_task(
                self._periodic_cleanup(), name="periodic_cleanup"
            )
            logger.info("Started background cleanup task (6-hour interval)")

    async def run(self) -> None:
        """Run the MCP server with transport abstraction."""
        logger.info("Starting server initialization...")
        await self.initialize()
        logger.info("Server initialization completed, starting transport...")

        try:
            if self.transport:
                # Use provided transport
                await self.transport.initialize()
                await self.transport._run_with_retry()
            else:
                # Fall back to default stdio transport
                from ..transport.stdio_transport import StdioTransport

                transport = StdioTransport(self)
                await transport.initialize()
                await transport._run_with_retry()

        except KeyboardInterrupt:
            logger.info("Server stopped by user interrupt")
        except Exception as e:
            logger.error(
                f"Transport error: {e}",
                extra={
                    "structured_data": {
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                    }
                },
            )
            raise
        finally:
            # Clean shutdown
            await self.shutdown()

    async def shutdown(self) -> None:
        """Clean shutdown of server resources."""
        try:
            # Cancel background cleanup task
            if self._cleanup_task and not self._cleanup_task.done():
                self._cleanup_task.cancel()
                try:
                    await self._cleanup_task
                except asyncio.CancelledError:
                    pass

            # Cancel any running tasks
            self.task_manager.cancel_all()

            # Close database connections
            if self.db_manager:
                await self.db_manager.close_pool()

            self.logger.info("Server shutdown completed successfully")

        except Exception as e:
            self.error_handler.log_error(e, context={"phase": "shutdown"})


async def main() -> None:
    """Main entry point for the MCP server."""
    import sys

    # Setup logging to stderr (stdout is used for MCP communication)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stderr)],
    )

    # Create and run server
    server = MCPCodeIndexServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
