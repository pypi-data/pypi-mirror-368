"""Embedding functionality for text processing."""

from typing import Any, List, Union

import numpy as np
from langchain.docstore.document import Document
from langchain_community.vectorstores.chroma import Chroma
from sentence_transformers import SentenceTransformer

from ..config.config import (
    DEFAULT_EMBEDDING_MODEL,
    DEFAULT_RETRIEVER_TOP_K,
    DEFAULT_SEARCH_TYPE,
)
from ..utils.exceptions import EmbeddingError
from ..utils.timing import timing_decorator


class CustomEmbeddingFunction:
    """Custom embedding function using SentenceTransformer."""

    def __init__(self, model_name: str = DEFAULT_EMBEDDING_MODEL):
        """
        Initialize the embedding function.

        Args:
            model_name: Name of the SentenceTransformer model to use
        """
        try:
            self.model = SentenceTransformer(model_name)
        except Exception as e:
            raise EmbeddingError(f"Failed to load embedding model: {e}")

    def embed_documents(self, texts: List[str]) -> List[np.ndarray]:
        """
        Embed a list of documents.

        Args:
            texts: List of texts to embed

        Returns:
            List of embeddings as numpy arrays
        """
        try:
            return [self.model.encode(text) for text in texts]
        except Exception as e:
            raise EmbeddingError(f"Failed to embed documents: {e}")

    def embed_query(self, text: str) -> np.ndarray:
        """
        Embed a single query text.

        Args:
            text: Text to embed

        Returns:
            Embedding as numpy array
        """
        try:
            return self.model.encode(text)
        except Exception as e:
            raise EmbeddingError(f"Failed to embed query: {e}")


@timing_decorator
def create_vectorstore(
    texts: Union[List[str], List[Document]], model_name: str = DEFAULT_EMBEDDING_MODEL
) -> Chroma:
    """
    Create a vector store from texts using custom embeddings.

    Args:
        texts: List of texts or Documents to embed
        model_name: Name of the embedding model to use

    Returns:
        Chroma vector store

    Raises:
        EmbeddingError: If there's an error during embedding
    """
    try:
        embedding_fn = CustomEmbeddingFunction(model_name)

        # Use appropriate method based on input type
        if texts and isinstance(texts[0], Document):
            return Chroma.from_documents(
                documents=texts, embedding=embedding_fn, persist_directory=".chroma"
            )
        else:
            return Chroma.from_texts(
                texts=texts, embedding=embedding_fn, persist_directory=".chroma"
            )
    except Exception as e:
        raise EmbeddingError(f"Failed to create vector store: {e}")


@timing_decorator
def setup_retriever(
    vectorstore: Chroma,
    search_type: str = DEFAULT_SEARCH_TYPE,
    top_k: int = DEFAULT_RETRIEVER_TOP_K,
) -> Union[None, Any]:
    """
    Set up a retriever from a vector store.

    Args:
        vectorstore: Chroma vector store
        search_type: Type of search to perform (default: from config)
        top_k: Number of documents to retrieve (default: from config)

    Returns:
        Retriever object or None if setup fails
    """
    try:
        return vectorstore.as_retriever(
            search_type=search_type, search_kwargs={"k": top_k}
        )
    except Exception as e:
        raise EmbeddingError(f"Failed to set up retriever: {e}")
