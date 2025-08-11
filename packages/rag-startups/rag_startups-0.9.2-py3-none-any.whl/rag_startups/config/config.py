"""Backward-compatibility shim.

Legacy code imported constants from ``config.config``. This module proxies those
constants to the new settings system so old imports keep working without
spreading absolute import paths outside the package.
"""

from __future__ import annotations

import os
from typing import cast

# Import lazily to avoid validation errors at import time
try:
    from .settings import get_settings  # type: ignore

    _settings = get_settings()
    MAX_LINES: int = cast(int, _settings.max_lines)
    CHUNK_SIZE: int = cast(int, _settings.chunk_size)
    CHUNK_OVERLAP: int = cast(int, _settings.chunk_overlap)
    DEFAULT_EMBEDDING_MODEL: str = cast(str, _settings.embedding_model)
    DEFAULT_RETRIEVER_TOP_K: int = cast(int, _settings.retriever_top_k)
    DEFAULT_SEARCH_TYPE: str = cast(str, _settings.search_type)
except Exception:
    # Safe fall-back; env var allows override for tests
    MAX_LINES = int(os.getenv("RAG_MAX_LINES", 500_000))  # noqa: N816
    CHUNK_SIZE = int(os.getenv("RAG_CHUNK_SIZE", 1000))  # noqa: N816
    CHUNK_OVERLAP = int(os.getenv("RAG_CHUNK_OVERLAP", 200))  # noqa: N816
    DEFAULT_EMBEDDING_MODEL = os.getenv(
        "RAG_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
    )
    DEFAULT_RETRIEVER_TOP_K = int(os.getenv("RAG_RETRIEVER_TOP_K", 3))  # noqa: N816
    DEFAULT_SEARCH_TYPE = os.getenv("RAG_SEARCH_TYPE", "similarity")

    # Prompt template and default local model expected by legacy tests
DEFAULT_PROMPT_TEMPLATE = (
    "Find startup ideas related to: {question}\n"
    "Respond in tight, business-pitch style."
)  # noqa: N816
LOCAL_LANGUAGE_MODEL = os.getenv("RAG_LOCAL_LLM", "gpt2")  # noqa: N816

__all__: list[str] = [
    # legacy prompt/model
    "DEFAULT_PROMPT_TEMPLATE",
    "LOCAL_LANGUAGE_MODEL",
    "MAX_LINES",
    "CHUNK_SIZE",
    "CHUNK_OVERLAP",
    "DEFAULT_EMBEDDING_MODEL",
    "DEFAULT_RETRIEVER_TOP_K",
    "DEFAULT_SEARCH_TYPE",
]
