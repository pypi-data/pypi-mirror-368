"""
Integration tests for RAG chain functionality.
These tests ensure safe refactoring of the RAG pipeline.
"""

from unittest.mock import Mock, patch

import pandas as pd
import pytest

import src.rag_startups.core.rag_chain as rag_chain_module
from src.rag_startups.core.rag_chain import (
    format_startup_idea,
    initialize_rag,
    rag_chain_local,
)
from src.rag_startups.core.startup_metadata import StartupLookup


class TestRAGIntegration:
    """Integration tests for the complete RAG workflow."""

    @pytest.fixture
    def sample_df(self):
        """Sample DataFrame for testing."""
        return pd.DataFrame(
            {
                "description": [
                    "AI-powered customer service platform for e-commerce",
                    "Blockchain-based supply chain tracking system",
                    "Mobile app for food delivery optimization",
                ],
                "name": ["ServiceAI", "ChainTrack", "FoodFast"],
                "industry": ["AI", "Blockchain", "Food Tech"],
            }
        )

    @pytest.fixture
    def sample_json_data(self):
        """Sample JSON data for startup lookup."""
        return [
            {
                "name": "ServiceAI",
                "description": "AI-powered customer service platform for e-commerce",
                "industry": "AI",
                "founded": "2020",
            },
            {
                "name": "ChainTrack",
                "description": "Blockchain-based supply chain tracking system",
                "industry": "Blockchain",
                "founded": "2021",
            },
        ]

    def test_end_to_end_idea_generation(self, sample_df, sample_json_data):
        """Test complete workflow from input to output."""
        # Test that the RAG chain can be initialized and used
        retriever, lookup = initialize_rag(sample_df, sample_json_data)

        assert retriever is not None, "Retriever should be initialized"
        assert lookup is not None, "Startup lookup should be initialized"

        # Test that we can format a startup idea
        test_description = "AI-powered customer service platform"
        formatted_idea = format_startup_idea(test_description, retriever, lookup)

        assert isinstance(formatted_idea, dict), "Should return a dictionary"
        assert "Company" in formatted_idea, "Should have Company field"
        assert "Problem" in formatted_idea, "Should have Problem field"
        assert "Solution" in formatted_idea, "Should have Solution field"

    def test_rag_chain_with_different_inputs(self, sample_df, sample_json_data):
        """Test RAG chain behavior with various input types."""
        retriever, lookup = initialize_rag(sample_df, sample_json_data)

        # Test with different question formats
        questions = [
            "Find AI startup ideas",
            "innovative blockchain solutions",
            "food technology startups",
            "",  # Empty string
        ]

        mock_generator = Mock()
        prompt_template = "Test template: {question} {context}"

        for question in questions:
            try:
                result = rag_chain_local(
                    question, mock_generator, prompt_template, retriever
                )
                if question:  # Non-empty questions should work
                    assert isinstance(
                        result, str
                    ), f"Should return string for question: {question}"
                else:  # Empty question might raise an exception
                    pass
            except Exception as e:
                # Document the behavior for empty/invalid inputs
                assert (
                    question == ""
                ), f"Only empty questions should raise exceptions, got: {e}"

    def test_error_handling_in_rag_pipeline(self, sample_df, sample_json_data):
        """Test error scenarios in RAG processing."""
        # Test with None retriever - should work gracefully with new implementation
        result = format_startup_idea("test description", None, None)
        assert isinstance(result, dict)
        assert "Company" in result

        # Test with invalid DataFrame
        with pytest.raises((ValueError, TypeError)):
            initialize_rag(None, sample_json_data)

        # Test with None json_data - should raise TypeError due to iteration
        with pytest.raises(TypeError):
            initialize_rag(sample_df, None)

    def test_global_state_behavior(self, sample_df, sample_json_data):
        """Test that global state is properly maintained for backward compatibility."""
        # Access global variable through module to avoid stale import issue
        initial_global_state = rag_chain_module.startup_lookup

        retriever, lookup = initialize_rag(sample_df, sample_json_data)

        # Verify global state is properly set after initialization
        assert (
            rag_chain_module.startup_lookup is not None
        ), "Global startup_lookup should be set"
        assert (
            rag_chain_module.startup_lookup != initial_global_state
        ), "Global state should have changed"
        assert lookup is not None, "Returned startup_lookup should be set"
        assert (
            rag_chain_module.startup_lookup is lookup
        ), "Global and returned lookup should be the same"

        # Test that both approaches work with backward compatibility
        test_description = "AI startup"
        formatted_with_global = format_startup_idea(test_description, retriever)
        formatted_with_explicit = format_startup_idea(
            test_description, retriever, lookup
        )

        # Both should work and return valid dictionaries
        assert isinstance(formatted_with_global, dict)
        assert isinstance(formatted_with_explicit, dict)
        assert "Company" in formatted_with_global
        assert "Company" in formatted_with_explicit

    def test_startup_lookup_isolation(self, sample_json_data):
        """Test that startup lookup can be injected independently."""
        # Create independent lookup instances
        lookup1 = StartupLookup(sample_json_data)
        lookup2 = StartupLookup(sample_json_data[:1])  # Subset of data

        # Test they work independently
        result1 = lookup1.get_by_name("ServiceAI")
        result2 = lookup2.get_by_name("ServiceAI")

        assert result1 is not None, "First lookup should find ServiceAI"
        assert result2 is not None, "Second lookup should find ServiceAI"

        # Test with data that only exists in first lookup
        result1_chain = lookup1.get_by_name("ChainTrack")
        result2_chain = lookup2.get_by_name("ChainTrack")

        assert result1_chain is not None, "First lookup should find ChainTrack"
        assert result2_chain is None, "Second lookup should not find ChainTrack"

    @patch("src.rag_startups.core.rag_chain.startup_lookup")
    def test_dependency_injection_preparation(
        self, mock_global_lookup, sample_df, sample_json_data
    ):
        """Test preparation for dependency injection pattern."""
        # Test that we can mock the global dependency
        mock_global_lookup.get_by_description.return_value = {
            "name": "MockedStartup",
            "description": "Mocked description",
        }

        # Create a local lookup for comparison
        local_lookup = StartupLookup(sample_json_data)

        # Test that format_startup_idea can work with explicit dependency
        test_description = "test startup description"

        # This should use the mocked global lookup
        with patch(
            "src.rag_startups.core.rag_chain.get_similar_description"
        ) as mock_similar:
            mock_similar.return_value = "similar description"

            result_with_mock = format_startup_idea(test_description, None)
            assert isinstance(result_with_mock, dict)

            # This should use the explicit local lookup
            result_with_explicit = format_startup_idea(
                test_description, None, local_lookup
            )
            assert isinstance(result_with_explicit, dict)
