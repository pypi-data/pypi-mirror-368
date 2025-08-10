"""
Vector Mode Configuration.

Manages configuration settings for vector mode features including API keys,
batch sizes, similarity thresholds, and daemon settings.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import yaml

@dataclass
class VectorConfig:
    """Configuration for vector mode operations."""
    
    # API Configuration
    voyage_api_key: Optional[str] = None
    turbopuffer_api_key: Optional[str] = None
    
    # Embedding Configuration  
    embedding_model: str = "voyage-code-2"
    batch_size: int = 128
    max_tokens_per_chunk: int = 1024
    
    # Search Configuration
    similarity_threshold: float = 0.5
    max_search_results: int = 20
    enable_recency_boost: bool = True
    
    # Chunking Configuration
    max_chunk_size: int = 1500
    chunk_overlap: int = 100
    prefer_semantic_chunks: bool = True
    
    # File Monitoring Configuration
    watch_debounce_ms: int = 100
    ignore_patterns: list[str] = field(default_factory=lambda: [
        "*.log", "*.tmp", "*~", ".git/*", "__pycache__/*", "node_modules/*",
        "*.pyc", "*.pyo", ".DS_Store", "Thumbs.db"
    ])
    
    # Daemon Configuration
    daemon_enabled: bool = True
    daemon_poll_interval: int = 5
    max_queue_size: int = 1000
    worker_count: int = 3
    
    # Security Configuration
    redact_secrets: bool = True
    redaction_patterns_file: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> "VectorConfig":
        """Create config from environment variables."""
        return cls(
            voyage_api_key=os.getenv("VOYAGE_API_KEY"),
            turbopuffer_api_key=os.getenv("TURBOPUFFER_API_KEY"),
            embedding_model=os.getenv("VECTOR_EMBEDDING_MODEL", "voyage-code-2"),
            batch_size=int(os.getenv("VECTOR_BATCH_SIZE", "128")),
            max_tokens_per_chunk=int(os.getenv("VECTOR_MAX_TOKENS", "1024")),
            similarity_threshold=float(os.getenv("VECTOR_SIMILARITY_THRESHOLD", "0.5")),
            max_search_results=int(os.getenv("VECTOR_MAX_RESULTS", "20")),
            enable_recency_boost=os.getenv("VECTOR_RECENCY_BOOST", "true").lower() == "true",
            max_chunk_size=int(os.getenv("VECTOR_CHUNK_SIZE", "1500")),
            chunk_overlap=int(os.getenv("VECTOR_CHUNK_OVERLAP", "100")),
            watch_debounce_ms=int(os.getenv("VECTOR_DEBOUNCE_MS", "100")),
            daemon_enabled=os.getenv("VECTOR_DAEMON_ENABLED", "true").lower() == "true",
            daemon_poll_interval=int(os.getenv("VECTOR_POLL_INTERVAL", "5")),
            max_queue_size=int(os.getenv("VECTOR_MAX_QUEUE", "1000")),
            worker_count=int(os.getenv("VECTOR_WORKERS", "3")),
            redact_secrets=os.getenv("VECTOR_REDACT_SECRETS", "true").lower() == "true",
        )
    
    @classmethod
    def from_file(cls, config_path: Path) -> "VectorConfig":
        """Load config from YAML file."""
        if not config_path.exists():
            return cls.from_env()
        
        try:
            with open(config_path, "r") as f:
                data = yaml.safe_load(f) or {}
            
            # Merge with environment variables (env takes precedence)
            env_config = cls.from_env()
            
            # Update with file values only if env variable not set
            for key, value in data.items():
                if hasattr(env_config, key):
                    env_value = getattr(env_config, key)
                    # Use file value if env value is None or default
                    if env_value is None or (key == "voyage_api_key" and env_value is None):
                        setattr(env_config, key, value)
            
            return env_config
            
        except Exception as e:
            raise ValueError(f"Failed to load config from {config_path}: {e}")
    
    def to_file(self, config_path: Path) -> None:
        """Save config to YAML file."""
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Don't save API keys to file for security
        data = {
            k: v for k, v in self.__dict__.items() 
            if not k.endswith("_api_key")
        }
        
        with open(config_path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=True)
    
    def validate(self) -> list[str]:
        """Validate configuration and return list of errors."""
        errors = []
        
        if self.daemon_enabled:
            if not self.voyage_api_key:
                errors.append("VOYAGE_API_KEY environment variable required for vector mode")
            if not self.turbopuffer_api_key:
                errors.append("TURBOPUFFER_API_KEY environment variable required for vector mode")
        
        if self.batch_size <= 0:
            errors.append("batch_size must be positive")
        if self.max_tokens_per_chunk <= 0:
            errors.append("max_tokens_per_chunk must be positive")
        if not 0 <= self.similarity_threshold <= 1:
            errors.append("similarity_threshold must be between 0 and 1")
        if self.max_search_results <= 0:
            errors.append("max_search_results must be positive")
        if self.max_chunk_size <= 0:
            errors.append("max_chunk_size must be positive")
        if self.chunk_overlap < 0:
            errors.append("chunk_overlap cannot be negative")
        if self.worker_count <= 0:
            errors.append("worker_count must be positive")
        
        return errors

def load_vector_config(config_path: Optional[Path] = None) -> VectorConfig:
    """Load vector configuration from file or environment."""
    if config_path is None:
        from . import get_vector_config_path
        config_path = get_vector_config_path()
    
    config = VectorConfig.from_file(config_path)
    
    # Validate configuration
    errors = config.validate()
    if errors:
        raise ValueError(f"Invalid vector configuration: {'; '.join(errors)}")
    
    return config
