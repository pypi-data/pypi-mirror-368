"""
RAG Service with dependency injection.
This replaces the global state pattern with proper dependency injection.
"""

from typing import Any, Optional, Tuple

import pandas as pd

from ..config.config import MAX_LINES
from ..data.loader import create_documents, split_documents
from ..embeddings.embedding import create_vectorstore, setup_retriever
from ..utils.exceptions import ModelError
from ..utils.timing import timing_decorator
from .startup_metadata import StartupLookup


class RAGService:
    """
    RAG service with dependency injection.

    This class encapsulates all RAG functionality and removes the need for global state.
    Dependencies are injected through the constructor, making the service testable and modular.
    """

    def __init__(self, startup_lookup: Optional[StartupLookup] = None):
        """
        Initialize RAG service with optional startup lookup.

        Args:
            startup_lookup: Optional StartupLookup instance for metadata retrieval
        """
        self.startup_lookup = startup_lookup
        self.retriever = None

    @timing_decorator
    def initialize(
        self, df: pd.DataFrame, json_data: list
    ) -> Tuple[Any, StartupLookup]:
        """
        Initialize RAG system and lookup.

        Args:
            df: DataFrame containing startup data
            json_data: Raw JSON data for startup lookup

        Returns:
            Tuple of (retriever, startup_lookup)
        """
        # Initialize lookup if not provided
        if self.startup_lookup is None:
            from ..data.loader import initialize_startup_lookup

            self.startup_lookup = initialize_startup_lookup(json_data)

        # Create and prepare documents
        documents = create_documents(df)
        splits = split_documents(documents)

        # Setup retriever
        vectorstore = create_vectorstore(splits)
        self.retriever = setup_retriever(vectorstore)

        return self.retriever, self.startup_lookup

    def get_similar_description(self, description: str) -> Optional[str]:
        """
        Get most similar description from the vector store.

        Args:
            description: Input description to find similar content for

        Returns:
            Most similar description or None if not found
        """
        if not self.retriever:
            return None
        if not description:
            return None

        similar_docs = self.retriever.invoke(description)
        return similar_docs[0].page_content if similar_docs else None

    def format_startup_idea(self, description: str) -> dict:
        """
        Format a startup description into a structured format.

        Args:
            description: Raw startup description

        Returns:
            Dictionary with structured startup idea fields
        """
        # Ensure description is a string
        if not isinstance(description, str):
            if hasattr(description, "page_content"):
                description = description.page_content
            elif hasattr(description, "__str__"):
                description = str(description)
            else:
                raise ValueError(
                    f"Cannot process description of type {type(description)}"
                )

        # Get similar description from RAG if retriever is available
        similar_desc = self.get_similar_description(description)

        # Get metadata if we found a similar description and have a lookup
        metadata = (
            self.startup_lookup.get_by_description(similar_desc)
            if (similar_desc and self.startup_lookup)
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
        value_details = self._format_value_details(value_details)
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

    def _format_value_details(self, value_details: str) -> str:
        """
        Format value details, handling quotes and bullet points.

        Args:
            value_details: Raw value details text

        Returns:
            Formatted value details
        """
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
    def execute_rag_chain(
        self,
        question: str,
        generator: Any,
        prompt_template: str,
        max_lines: int = MAX_LINES,
    ) -> str:
        """
        Execute the RAG chain locally.

        Args:
            question: Question to process
            generator: Text generator instance
            prompt_template: Template for prompts
            max_lines: Maximum lines to process

        Returns:
            Generated response text

        Raises:
            ModelError: If RAG chain execution fails
        """
        if not self.retriever:
            raise ModelError("RAG service not initialized. Call initialize() first.")

        try:
            # Get relevant documents
            context_docs = self.retriever.invoke(question)

            # Format the startup ideas
            formatted_ideas = []
            seen_companies = set()  # Track companies we've already seen

            for doc in context_docs:
                # Format the idea
                sections = self.format_startup_idea(doc.page_content)

                # Skip if we've already seen this company
                if sections["Company"] in seen_companies:
                    continue

                seen_companies.add(sections["Company"])

                # Format the idea with proper sections
                formatted_idea = (
                    f"\n{'='*50}\nStartup Idea #{len(formatted_ideas)+1}:\n"
                )
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


# Factory function for backward compatibility
def create_rag_service(startup_lookup: Optional[StartupLookup] = None) -> RAGService:
    """
    Factory function to create a RAG service instance.

    Args:
        startup_lookup: Optional StartupLookup instance

    Returns:
        Configured RAGService instance
    """
    return RAGService(startup_lookup)
