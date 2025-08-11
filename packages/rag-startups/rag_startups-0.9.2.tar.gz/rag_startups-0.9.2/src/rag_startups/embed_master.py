"""
To use langsmith set up the enviromnent variables :

LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
LANGCHAIN_API_KEY="your lansmith api key"
LANGCHAIN_PROJECT="the name of your langsmith project"

"""

import logging
import os
from typing import Any, List, Optional, Tuple

import pandas as pd
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from sentence_transformers import SentenceTransformer
from transformers import pipeline


def _get_local_language_model() -> str:
    """Return the local language model to use.

    Priority order:
    1. RAG settings (requires env vars fully loaded)
    2. `LOCAL_LANGUAGE_MODEL` environment variable
    3. Safe fallback: ``gpt2``
    """
    # Try settings lazily so we don't explode at import-time
    try:
        from .config import get_settings  # local import to avoid hard dependency

        return get_settings().language_model  # type: ignore[attr-defined]
    except Exception:
        return os.getenv("LOCAL_LANGUAGE_MODEL", "gpt2")


from .core.rag_chain import format_startup_idea  # noqa: E402
from .data.loader import StartupLookup, create_documents, split_documents  # noqa: E402
from .utils.spinner import Spinner  # noqa: E402
from .utils.timing import timing_decorator  # noqa: E402

# Configure logging to suppress batch processing messages
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
logging.getLogger("chromadb").setLevel(logging.WARNING)
logging.basicConfig(level=logging.INFO)
# logging.basicConfig(level=logging.DEBUG)


class CustomEmbeddingFunction:
    def __init__(self, model):
        self.model = model

    def embed_documents(self, texts):
        return self.model.encode(texts)

    def embed_query(self, text):
        return self.model.encode(text)


@timing_decorator
def create_and_split_document(df: pd.DataFrame):
    docs = create_documents(df)
    return split_documents(docs)


@timing_decorator
def embed(splits, model_name):
    try:
        embedding_model = SentenceTransformer(model_name)
        custom_embedder = CustomEmbeddingFunction(embedding_model)
        texts = [doc.page_content for doc in splits]
        return Chroma.from_texts(texts, embedding=custom_embedder)
    except Exception as e:
        logging.error(f"Error during embedding: {e}")
        return None


@timing_decorator
def setup_retriever(vectorstore):
    try:
        return vectorstore.as_retriever()
    except Exception as e:
        logging.error(f"Error setting up retriever: {e}")
        return None


@timing_decorator
def initialize_embeddings(df: pd.DataFrame, model_name: str = "all-MiniLM-L6-v2"):
    """Initialize embeddings and retriever. This should be called once at startup."""
    splits = create_and_split_document(df)
    if not splits:
        raise ValueError("Failed to split documents.")

    print("\nInitializing embeddings for faster startup idea generation...")
    with Spinner("Computing embeddings and setting up retriever"):
        vectorstore = embed(splits, model_name)
        if vectorstore is None:
            raise ValueError("Failed to create vectorstore.")

        retriever = setup_retriever(vectorstore)
        if retriever is None:
            raise ValueError("Failed to set up retriever.")
    print("Initialization complete!\n")

    return retriever


def get_prompt_content(prompt, question, context_docs):
    formatted_context = "\n\n".join(doc.page_content for doc in context_docs)
    prompt_input = prompt.format_messages(question=question, context=formatted_context)
    return prompt_input[0].content


@timing_decorator
def rag_chain_local(question, generator, prompt, retriever, lookup=None, num_ideas=3):
    try:
        context_docs = retriever.invoke(question)
        logging.debug(f"Retrieved documents: {context_docs}")
        logging.debug(
            f"First document type: {type(context_docs[0] if context_docs else None)}"
        )
        logging.debug(
            f"First document content: "
            f"{context_docs[0].page_content if context_docs else None}"
        )

        formatted_ideas = []
        seen_companies = set()

        for doc in context_docs:
            # Format the idea using the correct function
            sections = format_startup_idea(doc.page_content, retriever, lookup)

            # Skip if we've already seen this company
            if sections["Company"] in seen_companies:
                continue

            seen_companies.add(sections["Company"])

            # Format the idea with proper sections
            formatted_idea = f"\n{'='*50}\nStartup Idea #{len(formatted_ideas)+1}:\n"
            formatted_idea += f"Company: {sections['Company']}\n\n"
            formatted_idea += f"PROBLEM/OPPORTUNITY:\n{sections['Problem']}\n\n"
            formatted_idea += f"SOLUTION:\n{sections['Solution']}\n\n"
            formatted_idea += f"TARGET MARKET:\n{sections['Market']}\n\n"
            formatted_idea += f"UNIQUE VALUE:\n{sections['Value']}"

            formatted_ideas.append(formatted_idea)

            # Stop after num_ideas unique companies
            if len(formatted_ideas) >= num_ideas:
                break

        return (
            "Here are the most relevant startup ideas from YC companies:\n"
            + "\n".join(formatted_ideas)
        )
    except Exception as e:
        logging.error(f"Error in RAG chain: {e}")
        return ""


@timing_decorator
def calculate_result(
    question: str,
    retriever: Any,
    json_data: list,
    prompt_messages: List[Tuple[str, str]],
    language_model_name: Optional[str] = None,
    lookup: Optional[StartupLookup] = None,
    num_ideas: int = 3,
) -> str:
    """Calculate result using the RAG pipeline."""
    # Initialize lookup if not provided
    if lookup is None:
        lookup = StartupLookup(json_data)

    # Choose language model: prefer provided selection, otherwise fallback
    lm_name = language_model_name or _get_local_language_model()
    generator = pipeline("text-generation", model=lm_name, pad_token_id=50256)
    prompt = ChatPromptTemplate.from_messages(prompt_messages)
    result = rag_chain_local(
        question, generator, prompt, retriever, lookup=lookup, num_ideas=num_ideas
    )
    return result
