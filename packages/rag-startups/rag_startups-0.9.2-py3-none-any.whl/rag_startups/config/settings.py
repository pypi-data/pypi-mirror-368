"""Enhanced configuration management with validation and environment support."""

import os
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    """Supported environments."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class LogLevel(str, Enum):
    """Supported log levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class RAGSettings(BaseSettings):
    """Comprehensive RAG system configuration with validation."""

    # Environment
    environment: Environment = Field(
        default=Environment.DEVELOPMENT,
        validation_alias=AliasChoices("environment", "RAG_ENVIRONMENT"),
        description="Application environment",
    )

    # Project paths
    project_root: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent.parent.parent,
        description="Project root directory",
    )

    # API Configuration
    huggingface_token: str = Field(
        ...,
        validation_alias=AliasChoices("huggingface_token", "HUGGINGFACE_TOKEN"),
        min_length=1,
        description="HuggingFace API token (required)",
    )

    huggingface_api_url: str = Field(
        default="https://api-inference.huggingface.co/models",
        validation_alias=AliasChoices("huggingface_api_url", "HUGGINGFACE_API_URL"),
        description="HuggingFace API base URL",
    )

    # Model Configuration
    embedding_model: str = Field(
        default="all-MiniLM-L6-v2",
        validation_alias=AliasChoices("embedding_model", "RAG_EMBEDDING_MODEL"),
        description="Default embedding model (fallback if smart selection fails)",
    )

    language_model: str = Field(
        default="gpt2",
        validation_alias=AliasChoices("language_model", "RAG_LANGUAGE_MODEL"),
        description="Default language model (fallback if smart selection fails)",
    )

    # Smart Model Management
    enable_smart_model_selection: bool = Field(
        default=True,
        validation_alias=AliasChoices(
            "enable_smart_model_selection", "RAG_SMART_MODELS"
        ),
        description="Enable automatic model selection with fallback hierarchy",
    )

    model_health_check_interval: int = Field(
        default=3600,
        validation_alias=AliasChoices(
            "model_health_check_interval", "RAG_MODEL_CHECK_INTERVAL"
        ),
        ge=300,
        le=86400,
        description="Model health check interval in seconds (5min-24h)",
    )

    model_timeout: int = Field(
        default=10,
        validation_alias=AliasChoices("model_timeout", "RAG_MODEL_TIMEOUT"),
        ge=5,
        le=60,
        description="Model availability check timeout in seconds",
    )

    # Text Processing
    chunk_size: int = Field(
        default=1000,
        validation_alias=AliasChoices("chunk_size", "RAG_CHUNK_SIZE"),
        ge=100,
        le=4000,
        description="Text chunk size for document splitting",
    )

    chunk_overlap: int = Field(
        default=200,
        validation_alias=AliasChoices("chunk_overlap", "RAG_CHUNK_OVERLAP"),
        ge=0,
        le=1000,
        description="Overlap between text chunks",
    )

    max_lines: int = Field(
        default=500_000,
        validation_alias=AliasChoices("max_lines", "RAG_MAX_LINES"),
        ge=1000,
        description="Maximum lines to process from data files",
    )

    # Retriever Configuration
    retriever_top_k: int = Field(
        default=4,
        validation_alias=AliasChoices("retriever_top_k", "RAG_RETRIEVER_TOP_K"),
        ge=1,
        le=20,
        description="Number of documents to retrieve",
    )

    search_type: str = Field(
        default="similarity",
        pattern="^(similarity|mmr|similarity_score_threshold)$",
        description="Type of search to perform",
    )

    # Rate Limiting
    rate_limit_requests: int = Field(
        default=120, ge=1, description="Requests per hour for API calls"
    )

    rate_limit_window: int = Field(
        default=3600, ge=60, description="Rate limit window in seconds"
    )

    # Caching
    enable_caching: bool = Field(default=True, description="Enable response caching")

    cache_ttl: int = Field(default=3600, ge=60, description="Cache TTL in seconds")

    # Logging
    log_level: LogLevel = Field(
        default=LogLevel.INFO,
        validation_alias=AliasChoices("log_level", "RAG_LOG_LEVEL"),
        description="Logging level",
    )

    log_file: Optional[Path] = Field(
        default=None, description="Log file path (optional)"
    )

    # LangSmith Integration
    langchain_tracing: bool = Field(
        default=False,
        validation_alias=AliasChoices("langchain_tracing", "LANGCHAIN_TRACING_V2"),
        description="Enable LangChain tracing",
    )

    langchain_endpoint: str = Field(
        default="https://api.smith.langchain.com",
        validation_alias=AliasChoices("langchain_endpoint", "LANGCHAIN_ENDPOINT"),
        description="LangChain API endpoint",
    )

    langchain_api_key: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("langchain_api_key", "LANGCHAIN_API_KEY"),
        description="LangChain API key",
    )

    langchain_project: str = Field(
        default="rag_startups",
        validation_alias=AliasChoices("langchain_project", "LANGCHAIN_PROJECT"),
        description="LangChain project name",
    )

    # Database Configuration
    database_url: str = Field(
        default="sqlite:///./rag_startups.db", description="Database connection URL"
    )

    # Performance
    max_workers: int = Field(
        default=4, ge=1, le=16, description="Maximum worker threads"
    )

    batch_size: int = Field(
        default=32, ge=1, le=128, description="Batch size for processing"
    )

    @field_validator("chunk_overlap")
    @classmethod
    def validate_chunk_overlap(cls, v, info):
        """Ensure chunk overlap is less than chunk size."""
        chunk_size = info.data.get("chunk_size", 1000)
        if v >= chunk_size:
            raise ValueError("chunk_overlap must be less than chunk_size")
        return v

    @field_validator("project_root")
    @classmethod
    def validate_project_root(cls, v):
        """Ensure project root exists."""
        if not v.exists():
            raise ValueError(f"Project root directory does not exist: {v}")
        return v

    @field_validator("log_file")
    @classmethod
    def validate_log_file(cls, v):
        """Ensure log file directory exists."""
        if v is not None:
            v = Path(v)
            v.parent.mkdir(parents=True, exist_ok=True)
        return v

    @property
    def data_dir(self) -> Path:
        """Get data directory path."""
        return self.project_root / "data"

    @property
    def models_dir(self) -> Path:
        """Get models directory path."""
        return self.project_root / "models"

    @property
    def cache_dir(self) -> Path:
        """Get cache directory path."""
        return self.project_root / ".cache"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == Environment.DEVELOPMENT

    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.environment == Environment.TESTING

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == Environment.PRODUCTION

    @property
    def langchain_config(self) -> Dict[str, Any]:
        """Get LangChain configuration dictionary."""
        return {
            "tracing_v2": self.langchain_tracing,
            "endpoint": self.langchain_endpoint,
            "api_key": self.langchain_api_key or "",
            "project": self.langchain_project,
        }

    def get_prompt_template(self) -> str:
        """Get environment-appropriate prompt template."""
        if self.is_development:
            return """Find startup ideas related to: {question}

Context examples:
{context}

Return the most relevant examples with detailed explanations."""
        else:
            return """Find startup ideas related to: {question}

Context examples:
{context}

Return the most relevant examples."""

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        validate_assignment=True,
        extra="ignore",  # Ignore extra environment variables
        env_prefix="",  # No prefix for environment variables
    )


# Global settings instance
_settings: Optional[RAGSettings] = None


def _env_fingerprint() -> str:
    """Return a string fingerprint of critical env vars that influence settings."""
    return os.getenv("HUGGINGFACE_TOKEN", "")


def get_settings() -> RAGSettings:
    """Get global settings instance (singleton with smart reload).

    If critical environment variables have changed since the cached instance
    was created, build a fresh instance so that tests using ``patch.dict`` or
    dynamic configuration changes behave as expected.
    """
    global _settings
    if _settings is None:
        _settings = RAGSettings()
        _settings._fingerprint = _env_fingerprint()  # type: ignore[attr-defined]
    else:
        # If the fingerprint changed, rebuild settings
        current_fp = _env_fingerprint()
        cached_fp = getattr(_settings, "_fingerprint", None)
        if cached_fp != current_fp:
            _settings = RAGSettings()
            _settings._fingerprint = current_fp  # type: ignore[attr-defined]
    return _settings


def reload_settings() -> RAGSettings:
    """Reload settings (useful for testing)."""
    global _settings
    _settings = RAGSettings()
    _settings._fingerprint = _env_fingerprint()  # type: ignore[attr-defined]
    return _settings


# Convenience functions for backward compatibility
def get_huggingface_token() -> str:
    """Get HuggingFace token."""
    return get_settings().huggingface_token


def get_embedding_model() -> str:
    """Get embedding model name."""
    return get_settings().embedding_model


def get_chunk_size() -> int:
    """Get chunk size."""
    return get_settings().chunk_size


def get_retriever_config() -> Dict[str, Any]:
    """Get retriever configuration."""
    settings = get_settings()
    return {
        "top_k": settings.retriever_top_k,
        "search_type": settings.search_type,
    }
