"""
Unit tests for Docker runtime fixes.

Tests for issues encountered and fixed during Docker development:
1. HuggingFace client initialization (local vs remote models)
2. NumPy compatibility in embedding generation
3. Mock response parsing for local model fallbacks
"""

from unittest.mock import Mock, patch

import numpy as np
import pytest

from rag_startups.idea_generator.generator import StartupIdeaGenerator
from rag_startups.idea_generator.processors import parse_ideas


class TestHuggingFaceClientInitialization:
    """Test HuggingFace client initialization for local vs remote models."""

    def test_remote_model_initialization_with_token(self):
        """Test that remote models initialize HuggingFace client with token."""
        with patch.dict("os.environ", {"HUGGINGFACE_TOKEN": "test_token"}):
            with patch(
                "rag_startups.idea_generator.generator.InferenceClient"
            ) as mock_client:
                generator = StartupIdeaGenerator(
                    model_name="mistralai/Mistral-7B-Instruct-v0.3", use_local=False
                )

                # Should initialize InferenceClient for remote models
                mock_client.assert_called_once_with(
                    model="mistralai/Mistral-7B-Instruct-v0.3", token="test_token"
                )
                assert generator.client is not None
                assert not generator.use_local

    def test_remote_model_initialization_without_token_raises_error(self):
        """Test that remote models without token raise ValueError."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="HuggingFace token not provided"):
                StartupIdeaGenerator(
                    model_name="mistralai/Mistral-7B-Instruct-v0.3", use_local=False
                )

    def test_local_model_initialization(self):
        """Test that local models set client to None and use_local to True."""
        generator = StartupIdeaGenerator(model_name="local-test-model", use_local=True)

        # Should set client to None for local models
        assert generator.client is None
        assert generator.use_local
        assert generator._local_model is None

    def test_auto_detect_local_model_from_name(self):
        """Test auto-detection of local models from name prefix."""
        generator = StartupIdeaGenerator(
            model_name="local-test-model", use_local=None  # Auto-detect
        )

        # Should auto-detect as local model
        assert generator.use_local
        assert generator.client is None


class TestLocalModelGeneration:
    """Test local model generation and fallback mechanisms."""

    def test_generate_local_with_transformers(self):
        """Test _generate_local method with mocked transformers."""
        generator = StartupIdeaGenerator(model_name="local-test", use_local=True)

        # Mock transformers pipeline
        mock_pipeline = Mock()
        mock_pipeline.return_value = [{"generated_text": "Test generated text"}]

        with patch("transformers.pipeline", return_value=mock_pipeline):
            result = generator._generate_local(
                "test prompt", max_new_tokens=100, temperature=0.7
            )

            assert result == "Test generated text"
            mock_pipeline.assert_called_once_with(
                "test prompt",
                max_new_tokens=100,
                temperature=0.7,
                do_sample=True,
                repetition_penalty=1.2,
                return_full_text=True,
            )

    def test_generate_local_raises_on_error(self):
        """_generate_local should raise on model loading error (no mock fallback)."""
        generator = StartupIdeaGenerator(model_name="local-test", use_local=True)

        # Mock transformers to raise an exception
        with patch(
            "transformers.pipeline", side_effect=Exception("Model loading failed")
        ):
            with pytest.raises(RuntimeError, match="Failed to load local model"):
                _ = generator._generate_local(
                    "Generate fintech startup ideas", max_new_tokens=100
                )

    def test_mock_structured_response_format(self):
        """Test that mock structured response has correct format."""
        generator = StartupIdeaGenerator(model_name="local-test", use_local=True)

        result = generator._generate_mock_structured_response(
            "Generate fintech startup ideas"
        )

        # Should contain all required fields for parsing
        assert "Startup Idea 1:" in result
        assert "Name: MockTech-Fintech" in result
        assert "Problem/Opportunity:" in result
        assert "Solution:" in result
        assert "Target Market:" in result
        assert "Unique Value:" in result

    def test_mock_response_topic_detection(self):
        """Test topic detection in mock response generation."""
        generator = StartupIdeaGenerator(model_name="local-test", use_local=True)

        # Test different topics
        fintech_result = generator._generate_mock_structured_response(
            "Generate fintech ideas"
        )
        healthcare_result = generator._generate_mock_structured_response(
            "Generate healthcare solutions"
        )
        education_result = generator._generate_mock_structured_response(
            "Generate education platforms"
        )

        assert "MockTech-Fintech" in fintech_result
        assert "MockTech-Healthcare" in healthcare_result
        assert "MockTech-Education" in education_result


class TestResponseParsing:
    """Test response parsing for structured startup ideas."""

    def test_parse_ideas_with_valid_structured_response(self):
        """Test parsing of properly structured response."""
        structured_response = """Startup Idea 1:

Name: TestTech-Fintech
Problem/Opportunity: Traditional fintech solutions are outdated and inefficient.
Solution: An innovative platform that leverages AI to streamline processes.
Target Market: Small to medium businesses in the fintech sector.
Unique Value: First-to-market AI integration with user-friendly interface.
"""

        result = parse_ideas(structured_response)

        assert result is not None
        assert len(result) == 1
        assert result[0]["name"].startswith("TestTech-Fintech")
        assert "Traditional fintech solutions" in result[0]["problem"]
        assert "innovative platform" in result[0]["solution"]
        assert "Small to medium businesses" in result[0]["target_market"]

    def test_parse_ideas_with_empty_response(self):
        """Test parsing of empty response returns None."""
        result = parse_ideas("")
        assert result is None

        result = parse_ideas(None)
        assert result is None

    def test_parse_ideas_with_malformed_response(self):
        """Test parsing of malformed response returns None."""
        malformed_response = "This is just plain text without proper structure"

        result = parse_ideas(malformed_response)
        assert result is None

    def test_parse_ideas_with_missing_required_fields(self):
        """Test parsing fails when required fields are missing."""
        incomplete_response = """Startup Idea 1:

Name: TestTech
Problem/Opportunity: Some problem description.
"""  # Missing Solution and Target Market

        result = parse_ideas(incomplete_response)
        assert result is None


class TestNumpyCompatibility:
    """Test NumPy compatibility fixes for embedding generation."""

    @pytest.mark.skipif(
        not pytest.importorskip("sentence_transformers", minversion=None),
        reason="sentence_transformers not available",
    )
    def test_sentence_transformer_import(self):
        """Test that sentence_transformers can be imported without NumPy errors."""
        try:
            from sentence_transformers import SentenceTransformer  # noqa: F401

            # If we get here, import succeeded
            assert True
        except RuntimeError as e:
            if "Numpy is not available" in str(e):
                pytest.fail("NumPy compatibility issue still exists")
            else:
                # Some other error, re-raise
                raise

    @pytest.mark.skipif(
        not pytest.importorskip("sentence_transformers", minversion=None),
        reason="sentence_transformers not available",
    )
    def test_embedding_generation_basic(self):
        """Test basic embedding generation works without NumPy errors."""
        try:
            from sentence_transformers import SentenceTransformer

            # Use a small model for testing
            model = SentenceTransformer("all-MiniLM-L6-v2")
            test_text = "This is a test sentence."

            # This should not raise "Numpy is not available" error
            embedding = model.encode(test_text)

            # Verify embedding properties
            assert isinstance(embedding, np.ndarray)
            assert embedding.shape == (384,)  # Expected dimension for all-MiniLM-L6-v2

        except RuntimeError as e:
            if "Numpy is not available" in str(e):
                pytest.fail("NumPy compatibility issue in embedding generation")
            else:
                # Some other error, re-raise
                raise


class TestGeneratorIntegration:
    """Integration tests for the complete generator workflow."""

    def test_generate_raises_when_local_model_unavailable(self):
        """Generator should surface errors when local model cannot load."""
        generator = StartupIdeaGenerator(model_name="local-test", use_local=True)

        # Mock the transformers pipeline to fail, triggering error
        with patch("transformers.pipeline", side_effect=Exception("Model failed")):
            # Mock market analyzer to avoid external dependencies
            generator.market_analyzer = Mock()
            generator.market_analyzer.analyze_startup_idea.return_value = None

            with pytest.raises(RuntimeError, match="Failed to load local model"):
                _ = generator.generate(
                    num_ideas=1,
                    temperature=0.7,
                    include_market_analysis=False,
                )

    def test_generate_handles_parsing_errors_gracefully(self):
        """Test that generator handles parsing errors gracefully."""
        generator = StartupIdeaGenerator(model_name="local-test", use_local=True)

        # Mock _generate_local to return unparseable response
        generator._generate_local = Mock(return_value="Unparseable response")
        generator.market_analyzer = Mock()

        # Should not raise exception, should handle gracefully
        result, market_insights = generator.generate(
            num_ideas=1, include_market_analysis=False
        )

        # Should still return the raw response even if parsing fails
        assert result == "Unparseable response"
        assert market_insights is None
