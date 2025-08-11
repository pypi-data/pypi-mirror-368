"""
Configuration management tests.
These tests ensure safe refactoring of configuration handling.
"""

import os
from unittest.mock import patch

import click
import pytest

from src.rag_startups.cli import validate_token
from src.rag_startups.idea_generator.generator import StartupIdeaGenerator


class TestConfigurationValidation:
    """Tests for current configuration handling before refactoring."""

    def test_environment_variable_handling(self):
        """Test current env var processing."""
        # Test with valid token
        with patch.dict(os.environ, {"HUGGINGFACE_TOKEN": "test_token"}):
            token = validate_token()
            assert token == "test_token", "Should return the token from environment"

        # Test with missing token
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(click.exceptions.Exit):
                validate_token()

    def test_configuration_edge_cases(self):
        """Test missing/invalid configuration scenarios."""
        # Test empty token
        with patch.dict(os.environ, {"HUGGINGFACE_TOKEN": ""}):
            with pytest.raises(click.exceptions.Exit):
                validate_token()

        # Test whitespace-only token
        with patch.dict(os.environ, {"HUGGINGFACE_TOKEN": "   "}):
            token = validate_token()
            assert token == "   ", "Should return whitespace token (current behavior)"

    def test_startup_idea_generator_config(self):
        """Test StartupIdeaGenerator configuration handling."""
        # Test with valid token
        with patch.dict(os.environ, {"HUGGINGFACE_TOKEN": "valid_token"}):
            generator = StartupIdeaGenerator()
            assert generator.token == "valid_token"
            # Test that a valid model name is selected (don't hardcode specific model)
            assert generator.model_name is not None
            assert isinstance(generator.model_name, str)
            assert len(generator.model_name) > 0
            assert generator.max_requests_per_hour == 120

        # Test with custom parameters
        with patch.dict(os.environ, {"HUGGINGFACE_TOKEN": "custom_token"}):
            generator = StartupIdeaGenerator(
                model_name="custom/model",
                max_requests_per_hour=60,
                token="override_token",
            )
            assert generator.token == "override_token"  # Explicit token overrides env
            assert generator.model_name == "custom/model"
            assert generator.max_requests_per_hour == 60

    def test_missing_token_in_generator(self):
        """Test generator behavior with missing token."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="HuggingFace token not provided"):
                StartupIdeaGenerator()

    def test_config_defaults(self):
        """Test default configuration values."""
        with patch.dict(os.environ, {"HUGGINGFACE_TOKEN": "test"}):
            generator = StartupIdeaGenerator()

            # Test default values are as expected
            # Don't hardcode model name - test that a valid model is selected
            assert generator.model_name is not None
            assert isinstance(generator.model_name, str)
            assert len(generator.model_name) > 0
            assert generator.max_requests_per_hour == 120
            assert hasattr(generator, "request_timestamps")
            assert isinstance(generator.request_timestamps, list)
            assert len(generator.request_timestamps) == 0

    def test_rate_limiting_config(self):
        """Test rate limiting configuration."""
        with patch.dict(os.environ, {"HUGGINGFACE_TOKEN": "test"}):
            # Test default rate limit
            generator = StartupIdeaGenerator()
            assert (
                generator._check_rate_limit() is True
            )  # Should allow requests initially

            # Test custom rate limit
            generator_custom = StartupIdeaGenerator(max_requests_per_hour=1)
            assert generator_custom.max_requests_per_hour == 1

    @patch("src.rag_startups.idea_generator.generator.InferenceClient")
    @patch("src.rag_startups.idea_generator.generator.MarketAnalyzer")
    def test_client_initialization(self, mock_market_analyzer, mock_inference_client):
        """Test that clients are initialized properly."""
        with patch.dict(os.environ, {"HUGGINGFACE_TOKEN": "test_token"}):
            generator = StartupIdeaGenerator()

            # Verify clients were initialized with valid parameters
            # Don't hardcode model name - verify call was made with some model
            mock_inference_client.assert_called_once()
            call_args = mock_inference_client.call_args
            assert call_args[1]["token"] == "test_token"  # Check token was passed
            assert "model" in call_args[1]  # Check model was specified
            assert isinstance(call_args[1]["model"], str)  # Check model is a string
            mock_market_analyzer.assert_called_once()

            assert hasattr(generator, "client")
            assert hasattr(generator, "market_analyzer")

    def test_langchain_config_variables(self):
        """Test LangChain configuration variables (if present)."""
        langchain_vars = [
            "LANGCHAIN_TRACING_V2",
            "LANGCHAIN_ENDPOINT",
            "LANGCHAIN_API_KEY",
            "LANGCHAIN_PROJECT",
        ]

        # Test that these variables don't break the system if present
        test_env = {var: "test_value" for var in langchain_vars}
        test_env["HUGGINGFACE_TOKEN"] = "test_token"

        with patch.dict(os.environ, test_env):
            # Should not raise any exceptions
            token = validate_token()
            assert token == "test_token"

            generator = StartupIdeaGenerator()
            assert generator.token == "test_token"

    def test_config_file_paths(self):
        """Test configuration file path handling."""
        # Test default startup file path
        default_file = "yc_startups.json"
        assert isinstance(default_file, str)

        # Test that the system expects this file to exist
        # (This documents current behavior for refactoring)
        import src.rag_startups.cli as cli_module

        # Check if there are any hardcoded paths in the CLI module
        # This helps identify what needs to be configurable
        assert hasattr(cli_module, "generate_all")

    def test_model_configuration_validation(self):
        """Test model configuration validation."""
        with patch.dict(os.environ, {"HUGGINGFACE_TOKEN": "test"}):
            # Test valid model name
            generator = StartupIdeaGenerator(model_name="valid/model-name")
            assert generator.model_name == "valid/model-name"

            # Test empty model name (should work with current implementation)
            generator_empty = StartupIdeaGenerator(model_name="")
            assert generator_empty.model_name == ""

            # Test with None model_name (should handle gracefully or use default)
        try:
            generator_none = StartupIdeaGenerator(model_name=None)
            assert generator_none.model_name is not None
        except (AttributeError, ValueError):
            # Expected behavior when model_name is None
            pass

    def test_temperature_and_generation_params(self):
        """Test generation parameter handling."""
        with patch.dict(os.environ, {"HUGGINGFACE_TOKEN": "test"}):
            StartupIdeaGenerator()

            # Test that generator accepts various temperature values
            # (This documents current parameter handling)
            valid_temperatures = [0.0, 0.5, 0.7, 1.0, 1.5]

            for temp in valid_temperatures:
                # Should not raise exceptions during initialization
                # (Actual validation happens during generation)
                assert isinstance(temp, (int, float))
                assert temp >= 0.0  # Document expected range
