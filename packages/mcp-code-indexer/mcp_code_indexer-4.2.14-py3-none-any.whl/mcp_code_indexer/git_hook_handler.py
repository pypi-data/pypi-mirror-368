#!/usr/bin/env python3
"""
Git Hook Handler for MCP Code Indexer

Handles automated analysis of git changes and updates file descriptions
and project overview using OpenRouter API integration.
"""

import asyncio
import json
import logging
import os
import subprocess  # nosec B404
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, cast

import aiohttp
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .database.database import DatabaseManager
from .token_counter import TokenCounter


class GitHookError(Exception):
    """Custom exception for git hook operations."""

    pass


class ThrottlingError(Exception):
    """Exception for rate limiting scenarios."""

    pass


class GitHookHandler:
    """
    Handles git hook integration for automated code indexing.

    This class provides functionality to:
    - Analyze git diffs to identify changed files
    - Use OpenRouter API to update file descriptions
    - Update project overview when structural changes occur
    """

    # OpenRouter configuration
    OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
    OPENROUTER_MODEL = "anthropic/claude-sonnet-4"

    def __init__(
        self,
        db_manager: DatabaseManager,
        cache_dir: Path,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize GitHookHandler.

        Args:
            db_manager: Database manager instance
            cache_dir: Cache directory for temporary files
            logger: Logger instance to use (optional, creates default if not provided)
        """
        self.db_manager = db_manager
        self.cache_dir = cache_dir
        self.logger = logger if logger is not None else logging.getLogger(__name__)
        self.token_counter = TokenCounter()

        # Git hook specific settings
        self.config: Dict[str, Union[str, int, float]] = {
            "model": os.getenv("MCP_GITHOOK_MODEL", self.OPENROUTER_MODEL),
            "max_diff_tokens": 136000,  # Skip if diff larger than this (in tokens)
            "chunk_token_limit": 100000,  # Target token limit per chunk
            "timeout": 300,  # 5 minutes
            "temperature": 0.3,  # Lower temperature for consistent updates
        }

        # Validate OpenRouter API key
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise GitHookError(
                "OPENROUTER_API_KEY environment variable is required for git hook mode"
            )

    def _log_and_print(self, message: str, level: str = "info") -> None:
        """
        Log message and also print to stdout for user visibility.

        Args:
            message: Message to log and print
            level: Log level (info, warning, error)
        """
        # Log to logger
        getattr(self.logger, level)(message)

        # Also print to stdout with prefix for visibility
        prefix = "🔍" if level == "info" else "⚠️" if level == "warning" else "❌"
        print(f"{prefix} {message}")

    async def run_githook_mode(
        self,
        commit_hash: Optional[str] = None,
        commit_range: Optional[Tuple[str, str]] = None,
    ) -> None:
        """
        Run in git hook mode - analyze changes and update descriptions.

        Args:
            commit_hash: Process a specific commit by hash
            commit_range: Process commits in range (start_hash, end_hash)

        This is the main entry point for git hook functionality.
        """
        try:
            self._log_and_print("=== Git Hook Analysis Started ===")
            if commit_hash:
                self._log_and_print(f"Mode: Single commit ({commit_hash})")
            elif commit_range:
                self._log_and_print(
                    f"Mode: Commit range ({commit_range[0]}..{commit_range[1]})"
                )
            else:
                self._log_and_print("Mode: Staged changes")

            # Get git info from current directory
            project_info = await self._identify_project_from_git()
            self._log_and_print(f"Project: {project_info.get('name', 'Unknown')}")

            # Get git diff and commit message based on mode
            if commit_hash:
                git_diff = await self._get_git_diff_for_commit(commit_hash)
                commit_message = await self._get_commit_message_for_commit(commit_hash)
            elif commit_range:
                git_diff = await self._get_git_diff_for_range(
                    commit_range[0], commit_range[1]
                )
                commit_message = await self._get_commit_messages_for_range(
                    commit_range[0], commit_range[1]
                )
            else:
                git_diff = await self._get_git_diff()
                commit_message = await self._get_commit_message()

            # Log diff details
            if not git_diff:
                self._log_and_print("No changes detected, skipping analysis")
                return

            diff_tokens = self.token_counter.count_tokens(git_diff)
            self._log_and_print(f"Analyzing diff: {diff_tokens:,} tokens")

            # Fetch current state
            self._log_and_print("Fetching current project state...")
            current_overview = await self._get_project_overview(project_info)
            current_descriptions = await self._get_all_descriptions(project_info)
            changed_files = self._extract_changed_files(git_diff)

            if not changed_files:
                self._log_and_print("No files changed, skipping analysis")
                return

            self._log_and_print(f"Found {len(changed_files)} changed files")
            overview_tokens = (
                self.token_counter.count_tokens(current_overview)
                if current_overview
                else 0
            )
            self.logger.info(f"Current overview: {overview_tokens} tokens")
            self.logger.info(f"Current descriptions count: {len(current_descriptions)}")

            # Try single-stage first, fall back to two-stage if needed
            updates = await self._analyze_with_smart_staging(
                git_diff,
                commit_message,
                current_overview,
                current_descriptions,
                changed_files,
            )

            # Apply updates to database
            await self._apply_updates(project_info, updates)

            # Count actual updates
            file_update_count = len(updates.get("file_updates", {}))
            overview_updated = bool(updates.get("overview_update"))

            if file_update_count > 0 or overview_updated:
                update_parts = []
                if file_update_count > 0:
                    update_parts.append(f"{file_update_count} file descriptions")
                if overview_updated:
                    update_parts.append("project overview")
                self._log_and_print(f"✅ Updated {' and '.join(update_parts)}")
            else:
                self._log_and_print("✅ Analysis complete, no updates needed")

        except Exception as e:
            self._log_and_print(f"Git hook analysis failed: {e}", "error")
            self.logger.error(f"Exception details: {type(e).__name__}: {str(e)}")
            import traceback

            self.logger.error(f"Full traceback:\n{traceback.format_exc()}")
            # Don't fail the git operation - just log the error
            raise GitHookError(f"Git hook processing failed: {e}")

    async def _analyze_with_smart_staging(
        self,
        git_diff: str,
        commit_message: str,
        current_overview: str,
        current_descriptions: Dict[str, str],
        changed_files: List[str],
    ) -> Dict[str, Any]:
        """
        Smart staging: Try single-stage first, fall back to two-stage,
        then chunked processing if needed.

        Args:
            git_diff: Git diff content
            commit_message: Commit message explaining the changes
            current_overview: Current project overview
            current_descriptions: Current file descriptions
            changed_files: List of changed file paths

        Returns:
            Dict containing file_updates and overview_update
        """
        # Build single-stage prompt and check token count
        single_stage_prompt = self._build_single_stage_prompt(
            git_diff,
            commit_message,
            current_overview,
            current_descriptions,
            changed_files,
        )

        prompt_tokens = self.token_counter.count_tokens(single_stage_prompt)
        token_limit = self.config.get(
            "max_diff_tokens", 130000
        )  # Conservative limit under 136k

        self.logger.info(f"Single-stage prompt: {prompt_tokens} tokens")
        self.logger.info(f"Token limit: {token_limit}")

        if prompt_tokens <= int(token_limit):
            # Use single-stage approach
            self._log_and_print("Using single-stage analysis")
            result = await self._call_openrouter(single_stage_prompt)
            return result
        else:
            # Fall back to two-stage approach
            self._log_and_print("Using two-stage analysis (large diff)")

            # Try two-stage analysis first
            try:
                return await self._analyze_with_two_stage(
                    git_diff,
                    commit_message,
                    current_overview,
                    current_descriptions,
                    changed_files,
                )
            except GitHookError as e:
                if "too large" in str(e).lower():
                    # Fall back to chunked processing
                    self._log_and_print("Using chunked processing (very large diff)")
                    return await self._analyze_with_chunking(
                        git_diff,
                        commit_message,
                        current_overview,
                        current_descriptions,
                        changed_files,
                    )
                else:
                    raise

    def _build_single_stage_prompt(
        self,
        git_diff: str,
        commit_message: str,
        current_overview: str,
        current_descriptions: Dict[str, str],
        changed_files: List[str],
    ) -> str:
        """
        Build single-stage prompt that handles both overview and file updates.

        Args:
            git_diff: Git diff content
            commit_message: Commit message explaining the changes
            current_overview: Current project overview
            current_descriptions: Current file descriptions
            changed_files: List of changed file paths

        Returns:
            Complete single-stage prompt
        """
        # Only include descriptions for changed files to reduce token usage
        relevant_descriptions = {
            path: desc
            for path, desc in current_descriptions.items()
            if path in changed_files
        }

        return f"""Analyze this git commit and update both the project overview
(if needed) and file descriptions.

COMMIT MESSAGE:
{commit_message or "No commit message available"}

CURRENT PROJECT OVERVIEW:
{current_overview or "No overview available"}

CURRENT FILE DESCRIPTIONS (for changed files only):
{json.dumps(relevant_descriptions, indent=2)}

CHANGED FILES:
{", ".join(changed_files)}

GIT DIFF:
{git_diff}

INSTRUCTIONS:

1. OVERVIEW UPDATE: Update project overview ONLY if there are major
   structural changes like:
   - New major features or components (indicated by commit message or new
     directories)
   - Architectural changes (new patterns, frameworks, or approaches)
   - Significant dependency additions (Cargo.toml, package.json,
   pyproject.toml changes)
   - New API endpoints or workflows
   - Changes to build/deployment processes

   Do NOT update for: bug fixes, small refactors, documentation updates, version bumps.

   If updating, provide comprehensive narrative (10-20 pages of text) with
   directory structure, architecture, components, and workflows.

2. FILE UPDATES: Update descriptions for files that have changed
   significantly. Consider both the diff content and commit message context.
   Only include files that need actual description updates.

Return ONLY a JSON object:
{{
  "overview_update": "Updated overview text" or null,
  "file_updates": {{
    "path/to/file1.py": "Updated description for file1",
    "path/to/file2.js": "Updated description for file2"
  }}
}}"""

    async def _identify_project_from_git(self) -> Dict[str, Any]:
        """
        Identify project information from git repository.

        Returns:
            Dict containing project identification info
        """
        try:
            # Get current working directory as project root
            project_root = Path.cwd()

            # Use directory name as project name
            project_name = project_root.name

            return {"projectName": project_name, "folderPath": str(project_root)}

        except Exception as e:
            raise GitHookError(f"Failed to identify project from git: {e}")

    async def _get_git_diff(self) -> str:
        """
        Get git diff for recent changes.

        Returns:
            Git diff content as string
        """
        try:
            # Get diff from last commit
            diff_result = await self._run_git_command(
                ["diff", "--no-color", "--no-ext-diff", "HEAD~1..HEAD"]
            )
            return diff_result

        except subprocess.CalledProcessError:
            # If HEAD~1 doesn't exist (first commit), get diff against empty tree
            try:
                diff_result = await self._run_git_command(
                    ["diff", "--no-color", "--no-ext-diff", "--cached"]
                )
                return diff_result
            except subprocess.CalledProcessError as e:
                raise GitHookError(f"Failed to get git diff: {e}")

    async def _get_commit_message(self) -> str:
        """
        Get the commit message for context about what was changed.

        Returns:
            Commit message as string
        """
        try:
            # Get the commit message from the latest commit
            message_result = await self._run_git_command(["log", "-1", "--pretty=%B"])
            return message_result.strip()

        except subprocess.CalledProcessError:
            # If no commits exist yet, return empty string
            return ""

    async def _get_git_diff_for_commit(self, commit_hash: str) -> str:
        """
        Get git diff for a specific commit.

        Args:
            commit_hash: The commit hash to analyze

        Returns:
            Git diff content as string
        """
        try:
            # Get diff for the specific commit compared to its parent
            diff_result = await self._run_git_command(
                [
                    "diff",
                    "--no-color",
                    "--no-ext-diff",
                    f"{commit_hash}~1..{commit_hash}",
                ]
            )
            return diff_result

        except subprocess.CalledProcessError:
            # If parent doesn't exist (first commit), diff against empty tree
            try:
                diff_result = await self._run_git_command(
                    [
                        "diff",
                        "--no-color",
                        "--no-ext-diff",
                        "4b825dc642cb6eb9a060e54bf8d69288fbee4904",
                        commit_hash,
                    ]
                )
                return diff_result
            except subprocess.CalledProcessError as e:
                raise GitHookError(
                    f"Failed to get git diff for commit {commit_hash}: {e}"
                )

    async def _get_git_diff_for_range(self, start_hash: str, end_hash: str) -> str:
        """
        Get git diff for a range of commits.

        Args:
            start_hash: Starting commit hash (exclusive)
            end_hash: Ending commit hash (inclusive)

        Returns:
            Git diff content as string
        """
        try:
            diff_result = await self._run_git_command(
                ["diff", "--no-color", "--no-ext-diff", f"{start_hash}..{end_hash}"]
            )
            return diff_result
        except subprocess.CalledProcessError as e:
            raise GitHookError(
                f"Failed to get git diff for range {start_hash}..{end_hash}: {e}"
            )

    async def _get_commit_message_for_commit(self, commit_hash: str) -> str:
        """
        Get the commit message for a specific commit.

        Args:
            commit_hash: The commit hash

        Returns:
            Commit message as string
        """
        try:
            message_result = await self._run_git_command(
                ["log", "-1", "--pretty=%B", commit_hash]
            )
            return message_result.strip()
        except subprocess.CalledProcessError as e:
            raise GitHookError(f"Failed to get commit message for {commit_hash}: {e}")

    async def _get_commit_messages_for_range(
        self, start_hash: str, end_hash: str
    ) -> str:
        """
        Get commit messages for a range of commits.

        Args:
            start_hash: Starting commit hash (exclusive)
            end_hash: Ending commit hash (inclusive)

        Returns:
            Combined commit messages as string
        """
        try:
            # Get all commit messages in the range
            message_result = await self._run_git_command(
                ["log", "--pretty=%B", f"{start_hash}..{end_hash}"]
            )

            # Clean up and format the messages
            messages = message_result.strip()
            if messages:
                return (
                    f"Combined commit messages for range "
                    f"{start_hash}..{end_hash}:\n\n{messages}"
                )
            else:
                return f"No commits found in range {start_hash}..{end_hash}"

        except subprocess.CalledProcessError as e:
            raise GitHookError(
                f"Failed to get commit messages for range {start_hash}..{end_hash}: {e}"
            )

    def _extract_changed_files(self, git_diff: str) -> List[str]:
        """
        Extract list of changed files from git diff.

        Args:
            git_diff: Git diff content

        Returns:
            List of file paths that changed
        """
        changed_files = []
        lines = git_diff.split("\n")

        for line in lines:
            if line.startswith("diff --git a/"):
                # Parse file path from diff header
                # Format: diff --git a/path/to/file b/path/to/file
                parts = line.split(" ")
                if len(parts) >= 4:
                    file_path = parts[2][2:]  # Remove 'a/' prefix
                    changed_files.append(file_path)

        return changed_files

    async def _get_project_overview(self, project_info: Dict[str, Any]) -> str:
        """Get current project overview from database."""
        try:
            # Try to find existing project
            project = await self.db_manager.find_matching_project(
                project_info["projectName"], project_info["folderPath"]
            )

            if project:
                overview = await self.db_manager.get_project_overview(project.id)
                return overview.overview if overview else ""

            return ""

        except Exception as e:
            self.logger.warning(f"Failed to get project overview: {e}")
            return ""

    async def _get_all_descriptions(
        self, project_info: Dict[str, Any]
    ) -> Dict[str, str]:
        """Get all current file descriptions from database."""
        try:
            # Try to find existing project
            project = await self.db_manager.find_matching_project(
                project_info["projectName"], project_info["folderPath"]
            )

            if project:
                descriptions = await self.db_manager.get_all_file_descriptions(
                    project.id
                )
                return {desc.file_path: desc.description for desc in descriptions}

            return {}

        except Exception as e:
            self.logger.warning(f"Failed to get file descriptions: {e}")
            return {}

    async def _analyze_with_two_stage(
        self,
        git_diff: str,
        commit_message: str,
        current_overview: str,
        current_descriptions: Dict[str, str],
        changed_files: List[str],
    ) -> Dict[str, Any]:
        """
        Two-stage analysis: overview updates first, then file updates.

        Args:
            git_diff: Git diff content
            commit_message: Commit message explaining the changes
            current_overview: Current project overview
            current_descriptions: Current file descriptions
            changed_files: List of changed file paths

        Returns:
            Dict containing file_updates and overview_update
        """
        # Stage 1: Check if overview needs updating
        overview_updates = await self._analyze_overview_updates(
            git_diff, commit_message, current_overview, changed_files
        )

        # Stage 2: Update file descriptions
        file_updates = await self._analyze_file_updates(
            git_diff, commit_message, current_descriptions, changed_files
        )

        # Combine updates
        updates = {
            "file_updates": file_updates.get("file_updates", {}),
            "overview_update": overview_updates.get("overview_update"),
        }

        self.logger.info("Two-stage analysis completed")
        return updates

    async def _analyze_with_chunking(
        self,
        git_diff: str,
        commit_message: str,
        current_overview: str,
        current_descriptions: Dict[str, str],
        changed_files: List[str],
    ) -> Dict[str, Any]:
        """
        Chunked processing: Break large diffs into manageable chunks.

        Args:
            git_diff: Git diff content
            commit_message: Commit message explaining the changes
            current_overview: Current project overview
            current_descriptions: Current file descriptions
            changed_files: List of changed file paths

        Returns:
            Dict containing file_updates and overview_update
        """
        self._log_and_print(
            f"Starting chunked processing for {len(changed_files)} files"
        )

        # First, handle overview separately if needed
        overview_update = None
        if current_overview:
            overview_update = await self._analyze_overview_lightweight(
                commit_message, current_overview, changed_files
            )

        # Break changed files into chunks and process file descriptions
        chunk_size = await self._calculate_optimal_chunk_size(git_diff, changed_files)

        self._log_and_print(f"Processing in {chunk_size}-file chunks")

        all_file_updates = {}

        for i in range(0, len(changed_files), chunk_size):
            chunk_files = changed_files[i : i + chunk_size]
            chunk_number = (i // chunk_size) + 1
            total_chunks = (len(changed_files) + chunk_size - 1) // chunk_size

            self._log_and_print(
                f"Processing chunk {chunk_number}/{total_chunks} "
                f"({len(chunk_files)} files)"
            )

            # Extract diff content for this chunk
            chunk_diff = self._extract_chunk_diff(git_diff, chunk_files)

            # Process this chunk
            chunk_updates = await self._analyze_file_chunk(
                chunk_diff, commit_message, current_descriptions, chunk_files
            )

            # Merge results
            if chunk_updates and "file_updates" in chunk_updates:
                all_file_updates.update(chunk_updates["file_updates"])

        self.logger.info(
            f"Chunked processing completed: updated {len(all_file_updates)} files"
        )

        return {"file_updates": all_file_updates, "overview_update": overview_update}

    async def _analyze_overview_updates(
        self,
        git_diff: str,
        commit_message: str,
        current_overview: str,
        changed_files: List[str],
    ) -> Dict[str, Any]:
        """
        Stage 1: Analyze if project overview needs updating.

        Args:
            git_diff: Git diff content
            commit_message: Commit message explaining the changes
            current_overview: Current project overview
            changed_files: List of changed file paths

        Returns:
            Dict with overview_update key
        """
        self.logger.info("Stage 1: Analyzing overview updates...")

        prompt = f"""Analyze this git commit to determine if the project overview
needs updating.

COMMIT MESSAGE:
{commit_message or "No commit message available"}

CURRENT PROJECT OVERVIEW:
{current_overview or "No overview available"}

CHANGED FILES:
{", ".join(changed_files)}

GIT DIFF:
{git_diff}

INSTRUCTIONS:

Update project overview ONLY if there are major structural changes like:
- New major features or components (indicated by commit message or new directories)
- Architectural changes (new patterns, frameworks, or approaches)
- Significant dependency additions (Cargo.toml, package.json,
  pyproject.toml changes)
- New API endpoints or workflows
- Changes to build/deployment processes

Do NOT update for: bug fixes, small refactors, documentation updates, version bumps.

If updating, provide comprehensive narrative (10-20 pages of text) with
directory structure, architecture, components, and workflows.

Return ONLY a JSON object:
{{
  "overview_update": "Updated overview text" or null
}}"""

        # Log prompt details
        prompt_tokens = self.token_counter.count_tokens(prompt)
        self.logger.info(f"Stage 1 prompt: {prompt_tokens} tokens")

        if prompt_tokens > int(self.config["max_diff_tokens"]):
            raise GitHookError(f"Stage 1 prompt too large ({prompt_tokens} tokens)")

        # Call OpenRouter API
        result = await self._call_openrouter(prompt)
        self.logger.info("Stage 1 completed: overview analysis")

        return result

    async def _analyze_file_updates(
        self,
        git_diff: str,
        commit_message: str,
        current_descriptions: Dict[str, str],
        changed_files: List[str],
    ) -> Dict[str, Any]:
        """
        Stage 2: Analyze file description updates.

        Args:
            git_diff: Git diff content
            commit_message: Commit message explaining the changes
            current_descriptions: Current file descriptions for changed files only
            changed_files: List of changed file paths

        Returns:
            Dict with file_updates key
        """
        self.logger.info("Stage 2: Analyzing file description updates...")

        # Only include descriptions for changed files to reduce token usage
        relevant_descriptions = {
            path: desc
            for path, desc in current_descriptions.items()
            if path in changed_files
        }

        prompt = f"""Analyze this git commit and update file descriptions for
changed files.

COMMIT MESSAGE:
{commit_message or "No commit message available"}

CURRENT FILE DESCRIPTIONS (for changed files only):
{json.dumps(relevant_descriptions, indent=2)}

CHANGED FILES:
{", ".join(changed_files)}

GIT DIFF:
{git_diff}

INSTRUCTIONS:

Use the COMMIT MESSAGE to understand the intent and context of the changes.

Update descriptions for files that have changed significantly. Consider both the
diff content and commit message context. Only include files that need actual
description updates.

Return ONLY a JSON object:
{{
  "file_updates": {{
    "path/to/file1.py": "Updated description for file1",
    "path/to/file2.js": "Updated description for file2"
  }}
}}"""

        # Log prompt details
        prompt_tokens = self.token_counter.count_tokens(prompt)
        self.logger.info(f"Stage 2 prompt: {prompt_tokens} tokens")

        if prompt_tokens > int(self.config["max_diff_tokens"]):
            raise GitHookError(f"Stage 2 prompt too large ({prompt_tokens} tokens)")

        # Call OpenRouter API
        result = await self._call_openrouter(prompt)
        self.logger.info("Stage 2 completed: file description analysis")

        return result

    async def _analyze_overview_lightweight(
        self,
        commit_message: str,
        current_overview: str,
        changed_files: List[str],
    ) -> Optional[str]:
        """
        Lightweight overview analysis without including full diff.

        Args:
            commit_message: Commit message explaining the changes
            current_overview: Current project overview
            changed_files: List of changed file paths

        Returns:
            Updated overview text or None
        """
        self.logger.info("Lightweight overview analysis...")

        prompt = f"""Analyze this commit to determine if project overview needs updating.

COMMIT MESSAGE:
{commit_message or "No commit message available"}

CURRENT PROJECT OVERVIEW:
{current_overview or "No overview available"}

CHANGED FILES:
{", ".join(changed_files)}

INSTRUCTIONS:
Update project overview ONLY if there are major structural changes like:
- New major features or components (indicated by commit message or new directories)
- Architectural changes (new patterns, frameworks, or approaches)
- Significant dependency additions (Cargo.toml, package.json, pyproject.toml changes)
- New API endpoints or workflows
- Changes to build/deployment processes

Do NOT update for: bug fixes, small refactors, documentation updates, version bumps.

Return ONLY a JSON object:
{{
  "overview_update": "Updated overview text" or null
}}"""

        try:
            result = await self._call_openrouter(prompt)
            return result.get("overview_update")
        except Exception as e:
            self.logger.warning(f"Lightweight overview analysis failed: {e}")
            return None

    async def _calculate_optimal_chunk_size(
        self, git_diff: str, changed_files: List[str]
    ) -> int:
        """
        Calculate optimal chunk size based on diff content.

        Args:
            git_diff: Full git diff content
            changed_files: List of changed file paths

        Returns:
            Optimal number of files per chunk
        """
        if not changed_files:
            return 10  # Default chunk size

        # Estimate average diff size per file
        total_diff_tokens = self.token_counter.count_tokens(git_diff)
        avg_tokens_per_file = total_diff_tokens / len(changed_files)

        # Target chunk token limit
        chunk_limit = self.config.get("chunk_token_limit", 100000)

        # Calculate chunk size with buffer for overhead
        overhead_factor = 0.7  # Reserve 30% for prompt overhead
        effective_limit = int(chunk_limit) * overhead_factor

        chunk_size = max(1, int(effective_limit / avg_tokens_per_file))

        # Cap at reasonable limits
        chunk_size = min(chunk_size, 50)  # Max 50 files per chunk
        chunk_size = max(chunk_size, 5)  # Min 5 files per chunk

        self.logger.info(
            f"Calculated chunk size: {chunk_size} files "
            f"(avg {avg_tokens_per_file:.0f} tokens/file, "
            f"target {chunk_limit} tokens/chunk)"
        )

        return chunk_size

    def _extract_chunk_diff(self, git_diff: str, chunk_files: List[str]) -> str:
        """
        Extract diff content for specific files.

        Args:
            git_diff: Full git diff content
            chunk_files: List of files to include in chunk

        Returns:
            Filtered diff content for chunk files only
        """
        lines = git_diff.split("\n")
        chunk_lines = []
        include_section = False

        for line in lines:
            if line.startswith("diff --git"):
                # Parse file path from diff header
                parts = line.split(" ")
                if len(parts) >= 4:
                    file_path = parts[2][2:]  # Remove 'a/' prefix
                    include_section = file_path in chunk_files

            if include_section:
                chunk_lines.append(line)

        return "\n".join(chunk_lines)

    async def _analyze_file_chunk(
        self,
        chunk_diff: str,
        commit_message: str,
        current_descriptions: Dict[str, str],
        chunk_files: List[str],
    ) -> Dict[str, Any]:
        """
        Analyze a chunk of files for description updates.

        Args:
            chunk_diff: Git diff for this chunk only
            commit_message: Commit message explaining the changes
            current_descriptions: Current file descriptions
            chunk_files: List of files in this chunk

        Returns:
            Dict with file_updates for this chunk
        """
        # Only include descriptions for files in this chunk
        relevant_descriptions = {
            path: desc
            for path, desc in current_descriptions.items()
            if path in chunk_files
        }

        prompt = f"""Analyze this git commit chunk and update file descriptions.

COMMIT MESSAGE:
{commit_message or "No commit message available"}

CURRENT FILE DESCRIPTIONS (for chunk files only):
{json.dumps(relevant_descriptions, indent=2)}

CHUNK FILES:
{", ".join(chunk_files)}

GIT DIFF (chunk only):
{chunk_diff}

INSTRUCTIONS:
Use the COMMIT MESSAGE to understand the intent and context of the changes.
Update descriptions for files that have changed significantly.
Only include files that need actual description updates.

Return ONLY a JSON object:
{{
  "file_updates": {{
    "path/to/file1.py": "Updated description for file1",
    "path/to/file2.js": "Updated description for file2"
  }}
}}"""

        # Check token count
        prompt_tokens = self.token_counter.count_tokens(prompt)
        self.logger.info(f"Chunk prompt: {prompt_tokens} tokens")

        if prompt_tokens > int(self.config.get("chunk_token_limit", 100000)):
            self.logger.warning(
                f"Chunk still too large ({prompt_tokens} tokens), "
                f"skipping {len(chunk_files)} files"
            )
            return {"file_updates": {}}

        # Call OpenRouter API
        try:
            result = await self._call_openrouter(prompt)
            return result
        except Exception as e:
            self.logger.error(f"Failed to analyze chunk: {e}")
            return {"file_updates": {}}

    @retry(
        wait=wait_exponential(multiplier=1, min=4, max=60),
        stop=stop_after_attempt(5),
        retry=retry_if_exception_type(ThrottlingError),
    )
    async def _call_openrouter(self, prompt: str) -> Dict[str, Any]:
        """
        Call OpenRouter API to analyze changes.

        Args:
            prompt: Analysis prompt

        Returns:
            Parsed response with file updates and overview update
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/fluffypony/mcp-code-indexer",
            "X-Title": "MCP Code Indexer Git Hook",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.config["model"],
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a technical assistant that analyzes code "
                        "changes and updates file descriptions accurately "
                        "and concisely."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": self.config["temperature"],
            "max_tokens": 24000,
        }

        timeout = aiohttp.ClientTimeout(total=float(self.config["timeout"]))

        self.logger.info("Sending request to OpenRouter API...")
        self.logger.info(f"  Model: {self.config['model']}")
        self.logger.info(f"  Temperature: {self.config['temperature']}")
        self.logger.info("  Max tokens: 24000")
        self.logger.info(f"  Timeout: {self.config['timeout']}s")

        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    self.OPENROUTER_API_URL, headers=headers, json=payload
                ) as response:
                    self.logger.info(
                        f"OpenRouter API response status: {response.status}"
                    )

                    if response.status == 429:
                        retry_after = int(response.headers.get("Retry-After", 60))
                        self.logger.warning(
                            f"Rate limited by OpenRouter, retry after {retry_after}s"
                        )
                        raise ThrottlingError(
                            f"Rate limited. Retry after {retry_after}s"
                        )

                    response.raise_for_status()

                    response_data = await response.json()

                    if "choices" not in response_data:
                        self.logger.error(
                            f"Invalid API response format: {response_data}"
                        )
                        raise GitHookError(
                            f"Invalid API response format: {response_data}"
                        )

                    content = response_data["choices"][0]["message"]["content"]
                    self.logger.info(
                        f"OpenRouter response content length: {len(content)} characters"
                    )

                    return self._validate_githook_response(content)

        except aiohttp.ClientError as e:
            self.logger.error(f"OpenRouter API request failed: {e}")
            self.logger.error(f"ClientError details: {type(e).__name__}: {str(e)}")
            raise GitHookError(f"OpenRouter API request failed: {e}")
        except asyncio.TimeoutError:
            self.logger.error(
                f"OpenRouter API request timed out after {self.config['timeout']}s"
            )
            raise GitHookError("OpenRouter API request timed out")

    def _validate_githook_response(self, response_text: str) -> Dict[str, Any]:
        """
        Validate and parse JSON response from OpenRouter.

        Args:
            response_text: Raw response content

        Returns:
            Validated response data
        """

        def extract_json_from_response(text: str) -> str:
            """Extract JSON from response that might have extra text before/after."""
            text = text.strip()

            # Try to find JSON in the response
            json_start = -1
            json_end = -1

            # Look for opening brace
            for i, char in enumerate(text):
                if char == "{":
                    json_start = i
                    break

            if json_start == -1:
                return text  # No JSON found, return original

            # Find matching closing brace
            brace_count = 0
            for i in range(json_start, len(text)):
                if text[i] == "{":
                    brace_count += 1
                elif text[i] == "}":
                    brace_count -= 1
                    if brace_count == 0:
                        json_end = i + 1
                        break

            if json_end == -1:
                return text  # No matching brace found, return original

            return text[json_start:json_end]

        try:
            # First try parsing as-is
            try:
                data = json.loads(response_text.strip())
            except json.JSONDecodeError:
                # Try extracting JSON from response
                extracted_json = extract_json_from_response(response_text)
                if extracted_json != response_text.strip():
                    self.logger.debug(f"Extracted JSON from response: {extracted_json}")
                data = json.loads(extracted_json)

            # Handle both single-stage and two-stage responses
            if "file_updates" in data and "overview_update" in data:
                # Original single-stage format
                if not isinstance(data["file_updates"], dict):
                    raise ValueError("'file_updates' must be a dictionary")

                # Validate descriptions
                for path, desc in data["file_updates"].items():
                    if not isinstance(desc, str) or not desc.strip():
                        raise ValueError(f"Invalid description for {path}")

            elif "file_updates" in data:
                # Stage 2 format (file updates only)
                if not isinstance(data["file_updates"], dict):
                    raise ValueError("'file_updates' must be a dictionary")

                # Validate descriptions
                for path, desc in data["file_updates"].items():
                    if not isinstance(desc, str) or not desc.strip():
                        raise ValueError(f"Invalid description for {path}")

            elif "overview_update" in data:
                # Stage 1 format (overview only) - overview_update can be null
                pass
            else:
                raise ValueError(
                    "Response must contain 'file_updates' and/or 'overview_update'"
                )

            return cast(Dict[str, Any], data)

        except json.JSONDecodeError as e:
            self.logger.error(f"Raw response content: {repr(response_text)}")
            raise GitHookError(f"Invalid JSON response from API: {e}")
        except ValueError as e:
            self.logger.error(f"Raw response content: {repr(response_text)}")
            raise GitHookError(f"Invalid response structure: {e}")

    async def _apply_updates(
        self, project_info: Dict[str, Any], updates: Dict[str, Any]
    ) -> None:
        """
        Apply updates to database.

        Args:
            project_info: Project identification info
            updates: Updates from OpenRouter API
        """
        try:
            # Get or create project
            project = await self.db_manager.get_or_create_project(
                project_info["projectName"], project_info["folderPath"]
            )

            # Update file descriptions
            file_updates = updates.get("file_updates", {})
            for file_path, description in file_updates.items():
                from datetime import datetime

                from mcp_code_indexer.database.models import FileDescription

                file_desc = FileDescription(
                    id=None,
                    project_id=project.id,
                    source_project_id=None,
                    to_be_cleaned=None,
                    file_path=file_path,
                    description=description,
                    file_hash=None,
                    last_modified=datetime.utcnow(),
                    version=1,
                )
                await self.db_manager.create_file_description(file_desc)
                self.logger.info(f"Updated description for {file_path}")

            # Update project overview if provided
            overview_update = updates.get("overview_update")
            if overview_update and overview_update.strip():
                from datetime import datetime

                from mcp_code_indexer.database.models import ProjectOverview

                overview = ProjectOverview(
                    project_id=project.id,
                    overview=overview_update,
                    last_modified=datetime.utcnow(),
                    total_files=len(file_updates),
                    total_tokens=len(overview_update.split()),
                )
                await self.db_manager.create_project_overview(overview)
                self.logger.info("Updated project overview")

        except Exception as e:
            raise GitHookError(f"Failed to apply updates to database: {e}")

    async def _run_git_command(self, cmd: List[str]) -> str:
        """
        Run a git command and return output.

        Args:
            cmd: Git command arguments

        Returns:
            Command output as string
        """
        full_cmd = ["git"] + cmd

        try:
            process = await asyncio.create_subprocess_exec(
                *full_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=Path.cwd(),
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                returncode = process.returncode if process.returncode is not None else 1
                raise subprocess.CalledProcessError(
                    returncode, full_cmd, stdout, stderr
                )

            return stdout.decode("utf-8")

        except FileNotFoundError:
            raise GitHookError(
                "Git command not found - ensure git is installed and in PATH"
            )
