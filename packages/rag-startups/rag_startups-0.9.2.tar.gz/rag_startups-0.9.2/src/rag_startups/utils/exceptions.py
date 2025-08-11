"""Custom exceptions for the RAG Startups project."""


class RAGStartupsError(Exception):
    """Base exception for RAG Startups project."""


class DataLoadError(RAGStartupsError):
    """Raised when there is an error loading data."""


class EmbeddingError(RAGStartupsError):
    """Raised when there is an error during embedding."""


class ModelError(RAGStartupsError):
    """Raised when there is an error with the language model."""


class ConfigError(RAGStartupsError):
    """Raised when there is a configuration error."""
