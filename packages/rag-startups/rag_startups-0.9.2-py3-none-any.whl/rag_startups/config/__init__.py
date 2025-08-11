"""Enhanced configuration management system for RAG Startups.

This module provides a comprehensive configuration management system with:
- Environment-based configuration
- Validation and type checking
- Migration utilities
- Health checking
- Backward compatibility

Usage:
    from rag_startups.config import get_settings

    settings = get_settings()
    token = settings.huggingface_token
    model = settings.embedding_model
"""

from .migration import ConfigurationMigrator
from .settings import (
    Environment,
    LogLevel,
    RAGSettings,
    get_chunk_size,
    get_embedding_model,
    get_huggingface_token,
    get_retriever_config,
    get_settings,
    reload_settings,
)
from .validator import ConfigurationValidator

__all__ = [
    # Core settings
    "Environment",
    "LogLevel",
    "RAGSettings",
    "get_settings",
    "reload_settings",
    # Convenience functions
    "get_huggingface_token",
    "get_embedding_model",
    "get_chunk_size",
    "get_retriever_config",
    # Utilities
    "ConfigurationValidator",
    "ConfigurationMigrator",
]

# Version info
__version__ = "2.0.0"
__author__ = "RAG Startups Team"
__description__ = "Enhanced configuration management system"
