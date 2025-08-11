"""Core RAG chain functionality with backward compatibility.

This module provides backward compatibility for the old global state pattern
while internally using the new dependency injection approach via RAGService.
"""

from typing import Any, Optional

import pandas as pd

from ..config.config import MAX_LINES
from ..data.loader import create_documents, initialize_startup_lookup, split_documents
from ..embeddings.embedding import create_vectorstore, setup_retriever
from ..utils.exceptions import ModelError
from ..utils.timing import timing_decorator
from .rag_service import RAGService

# Global RAG service instance for backward compatibility
# TODO: Remove this global state in future versions
_global_rag_service = None

# Backward compatibility - maintain the old global lookup reference
startup_lookup = None


@timing_decorator
def initialize_rag(df: pd.DataFrame, json_data: list):
    """Initialize RAG system and lookup.

    This function maintains backward compatibility while using the new RAGService internally.

    Args:
        df: DataFrame containing startup data
        json_data: Raw JSON data for startup lookup

    Returns:
        Tuple of (retriever, startup_lookup) for backward compatibility
    """
    global startup_lookup, _global_rag_service

    # Initialize lookup first
    startup_lookup = initialize_startup_lookup(json_data)

    # Create and prepare documents
    documents = create_documents(df)
    splits = split_documents(documents)

    # Setup retriever
    vectorstore = create_vectorstore(splits)
    retriever = setup_retriever(vectorstore)

    # Create RAG service instance with the lookup and retriever
    _global_rag_service = RAGService(startup_lookup)
    _global_rag_service.retriever = retriever

    return retriever, startup_lookup


def get_similar_description(description: str, retriever: Any) -> Optional[str]:
    """Get most similar description from the vector store.

    This function maintains backward compatibility while delegating to RAGService.
    """
    # If we have a global service, use it
    if _global_rag_service:
        return _global_rag_service.get_similar_description(description)

    # Fallback to original implementation for backward compatibility
    if not retriever:
        return None
    if not description:
        return None

    similar_docs = retriever.invoke(description)
    return similar_docs[0].page_content if similar_docs else None


def format_startup_idea(
    description: str, retriever: Any = None, startup_lookup: Optional[Any] = None
) -> dict:
    """Format a startup description into a structured format.

    This function maintains backward compatibility while using RAGService internally.
    """
    # If we have a global service, use it
    if _global_rag_service:
        return _global_rag_service.format_startup_idea(description)

    # Fallback to original implementation for backward compatibility
    # Use the parameter if provided, otherwise use global
    # Access global variable through globals() to avoid shadowing issues
    global_startup_lookup = globals().get("startup_lookup")
    lookup_to_use = (
        startup_lookup if startup_lookup is not None else global_startup_lookup
    )

    # Ensure description is a string
    if not isinstance(description, str):
        if hasattr(description, "page_content"):
            description = description.page_content
        elif hasattr(description, "__str__"):
            description = str(description)
        else:
            raise ValueError(f"Cannot process description of type {type(description)}")

    # Get similar description from RAG if retriever is available
    similar_desc = (
        get_similar_description(description, retriever) if retriever else None
    )

    # Get metadata if we found a similar description and have a lookup
    metadata = (
        lookup_to_use.get_by_description(similar_desc)
        if (similar_desc and lookup_to_use)
        else None
    )

    # Use actual company name from metadata if available
    company_name = metadata["name"] if metadata else ""

    # Clean and join lines, removing empty ones
    lines = [line.strip() for line in description.split("\n") if line.strip()]
    content = " ".join(lines)

    # Try to identify the main components
    parts = content.split(".")
    main_desc = parts[0].strip()

    # Get main description
    main_desc = main_desc.rstrip(".") + "."

    # Analyze the remaining parts for additional details
    remaining_text = ". ".join(parts[1:]).strip()

    # Try to identify solution details (often follows the main description)
    solution_details = ""
    market_details = ""
    value_details = ""

    if remaining_text:
        remaining_parts = remaining_text.split(".")
        if len(remaining_parts) > 0:
            solution_details = remaining_parts[0].strip()
        if len(remaining_parts) > 1:
            market_details = remaining_parts[1].strip()
        if len(remaining_parts) > 2:
            value_details = ". ".join(remaining_parts[2:]).strip()

    # Try to extract target market from description
    target_market = "Organizations and stakeholders in this space"
    if "for" in main_desc.lower():
        extracted_market = main_desc.lower().split("for", 1)[1].strip()
        if len(extracted_market) > 3:  # Only use if meaningful
            target_market = extracted_market
    elif market_details:
        target_market = market_details

    # Format value details
    value_details = format_value_details(value_details)
    if not value_details:
        value_details = solution_details if solution_details else main_desc

    # Ensure proper sentence endings
    solution_details = (
        solution_details.rstrip(".") + "."
        if solution_details
        else f"Provides innovative solutions for {target_market.lower()}"
    )
    target_market = target_market.rstrip(".") + "."

    return {
        "Company": company_name,
        "Problem": main_desc,
        "Solution": solution_details,
        "Market": target_market,
        "Value": value_details,
    }


def format_value_details(value_details):
    """Format value details, handling quotes and bullet points."""
    if not value_details:
        return ""

    # Remove quotes at start and end while preserving internal quotes
    value_details = value_details.strip()
    while value_details.startswith('"'):
        value_details = value_details[1:].lstrip()
    while value_details.endswith('"'):
        value_details = value_details[:-1].rstrip()

    # Format bullet points if multiple sentences
    sentences = [s.strip() for s in value_details.split(".") if s.strip()]
    if len(sentences) > 1:
        formatted_sentences = []
        for sentence in sentences:
            if sentence:  # Skip empty sentences
                # Capitalize first letter if it's not already
                if sentence[0].islower():
                    sentence = sentence[0].upper() + sentence[1:]
                formatted_sentences.append(f"• {sentence}")
        value_details = "\n".join(formatted_sentences)

    return value_details


@timing_decorator
def rag_chain_local(
    question: str,
    generator: Any,
    prompt_template: str,
    retriever: Any,
    max_lines: int = MAX_LINES,
) -> str:
    """Execute the RAG chain locally.

    This function maintains backward compatibility while using RAGService internally.
    """
    # If we have a global service, use it
    if _global_rag_service:
        return _global_rag_service.execute_rag_chain(
            question, generator, prompt_template, max_lines
        )

    # Fallback to original implementation for backward compatibility
    try:
        # Get relevant documents
        context_docs = retriever.invoke(question)

        # Format the startup ideas
        formatted_ideas = []
        seen_companies = set()  # Track companies we've already seen

        for doc in context_docs:
            # Format the idea
            sections = format_startup_idea(doc.page_content, retriever, startup_lookup)

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

            # Stop after 3 unique companies
            if len(formatted_ideas) >= 3:
                break

        return (
            "Here are the most relevant startup ideas from YC companies:\n"
            + "\n".join(formatted_ideas)
        )

    except Exception as e:
        raise ModelError(f"Error in RAG chain execution: {str(e)}")
