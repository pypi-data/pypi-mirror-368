"""
Unit tests for CLI integration with smart model management.

These tests cover the integration issues discovered during performance testing,
ensuring robust CLI behavior with model fallback scenarios.
"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from typer.testing import CliRunner

from rag_startups.cli import app
from rag_startups.config.settings import get_settings
from rag_startups.core.model_manager import ModelConfig, ModelStatus, ModelType
from rag_startups.core.model_service import ModelService


class TestCLIIntegration:
    """Test CLI integration with smart model management."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.sample_startup_data = [
            {
                "name": "TestStartup",
                "description": "AI-powered test platform",
                "location": "San Francisco, CA",
                "tags": ["b2b", "ai"],
                "founders": [{"name": "Test Founder"}],
            }
        ]

    def create_temp_startup_file(self):
        """Create temporary startup data file for testing."""
        temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        json.dump(self.sample_startup_data, temp_file, indent=2)
        temp_file.close()
        return temp_file.name

    @patch("rag_startups.config.settings.get_settings")
    @patch("rag_startups.cli.ModelService")
    @patch("rag_startups.cli.load_data")
    @patch("rag_startups.cli.StartupLookup")
    @patch("rag_startups.cli.find_relevant_startups")
    @patch("rag_startups.cli.StartupIdeaGenerator")
    @patch("rag_startups.cli.validate_token")
    def test_cli_with_smart_model_management(
        self,
        mock_validate_token,
        mock_generator_class,
        mock_find_relevant,
        mock_lookup_class,
        mock_load_data,
        mock_model_service_class,
        mock_get_settings,
    ):
        """Test CLI integration with smart model management."""
        # Setup mocks
        mock_validate_token.return_value = "test_token"
        mock_settings = Mock()
        mock_get_settings.return_value = mock_settings

        # Mock model service and model selection
        mock_model_service = Mock()
        mock_language_model = ModelConfig(
            name="test-model",
            model_type=ModelType.LANGUAGE_GENERATION,
            provider="huggingface",
            fallback_priority=1,
        )
        mock_model_service.get_language_model.return_value = mock_language_model
        mock_model_service_class.return_value = mock_model_service

        # Mock data loading
        mock_df = Mock()
        mock_json_data = self.sample_startup_data
        mock_load_data.return_value = (mock_df, mock_json_data)

        # Mock startup lookup
        mock_lookup = Mock()
        mock_lookup_class.return_value = mock_lookup

        # Mock relevant startups finding
        mock_find_relevant.return_value = "Sample startup examples"

        # Mock idea generator
        mock_generator = Mock()
        mock_generator.generate.return_value = ("Generated idea", None)
        mock_generator_class.return_value = mock_generator

        # Create temporary startup file
        temp_file = self.create_temp_startup_file()

        try:
            # Test CLI command
            result = self.runner.invoke(
                app,
                [
                    "generate-all",
                    "AI tools",
                    "--file",
                    temp_file,
                    "--num-ideas",
                    "1",
                    "--no-market",
                ],
            )

            # Verify CLI executed successfully
            assert result.exit_code == 0

            # Verify smart model management was used
            mock_model_service_class.assert_called_once_with(mock_settings)
            mock_model_service.get_language_model.assert_called_once()

            # Verify generator was created with selected model
            mock_generator_class.assert_called_once()
            call_args = mock_generator_class.call_args
            assert call_args[1]["model_name"] == "test-model"
            assert call_args[1]["token"] == "test_token"

        finally:
            # Clean up temporary file
            os.unlink(temp_file)

    @patch("rag_startups.config.settings.get_settings")
    @patch("rag_startups.cli.ModelService")
    @patch("rag_startups.cli.validate_token")
    def test_cli_model_fallback_scenario(
        self, mock_validate_token, mock_model_service_class, mock_get_settings
    ):
        """Test CLI behavior when models fall back to local alternatives."""
        # Setup mocks
        mock_validate_token.return_value = "test_token"
        mock_settings = Mock()
        mock_get_settings.return_value = mock_settings

        # Mock model service with local fallback
        mock_model_service = Mock()
        mock_local_model = ModelConfig(
            name="local-gpt2",
            model_type=ModelType.LANGUAGE_GENERATION,
            provider="local",
            fallback_priority=99,
        )
        mock_model_service.get_language_model.return_value = mock_local_model
        mock_model_service_class.return_value = mock_model_service

        # Create temporary startup file
        temp_file = self.create_temp_startup_file()

        try:
            with (
                patch("rag_startups.cli.load_data") as mock_load_data,
                patch("rag_startups.cli.StartupLookup") as mock_lookup_class,
                patch("rag_startups.cli.find_relevant_startups") as mock_find_relevant,
                patch("rag_startups.cli.StartupIdeaGenerator") as mock_generator_class,
            ):

                # Setup remaining mocks
                mock_load_data.return_value = (Mock(), self.sample_startup_data)
                mock_lookup_class.return_value = Mock()
                mock_find_relevant.return_value = "Sample startup examples"

                mock_generator = Mock()
                mock_generator.generate.return_value = ("Generated idea", None)
                mock_generator_class.return_value = mock_generator

                # Test CLI command
                result = self.runner.invoke(
                    app,
                    [
                        "generate-all",
                        "AI tools",
                        "--file",
                        temp_file,
                        "--num-ideas",
                        "1",
                        "--no-market",
                    ],
                )

                # Verify CLI handled local model correctly
                assert result.exit_code == 0

                # Verify local model was selected
                call_args = mock_generator_class.call_args
                assert call_args[1]["model_name"] == "local-gpt2"

        finally:
            # Clean up temporary file
            os.unlink(temp_file)

    def test_cli_invalid_startup_file(self):
        """Test CLI behavior with invalid startup file."""
        result = self.runner.invoke(
            app,
            [
                "generate-all",
                "AI tools",
                "--file",
                "nonexistent_file.json",
                "--num-ideas",
                "1",
            ],
        )

        # Verify CLI exits with error for missing file
        assert result.exit_code == 1
        assert "not found" in result.stdout

    def test_cli_invalid_num_ideas(self):
        """Test CLI behavior with invalid number of ideas."""
        temp_file = self.create_temp_startup_file()

        try:
            result = self.runner.invoke(
                app,
                [
                    "generate-all",
                    "AI tools",
                    "--file",
                    temp_file,
                    "--num-ideas",
                    "10",  # Invalid: > 5
                ],
            )

            # Verify CLI exits with error for invalid num_ideas
            assert result.exit_code == 1
            assert "must be between 1 and 5" in result.stdout

        finally:
            os.unlink(temp_file)

    @patch("rag_startups.cli.validate_token")
    def test_cli_missing_token(self, mock_validate_token):
        """Test CLI behavior when HuggingFace token is missing."""
        # Mock token validation failure
        mock_validate_token.side_effect = ValueError("HuggingFace token not provided")

        temp_file = self.create_temp_startup_file()

        try:
            result = self.runner.invoke(
                app,
                [
                    "generate-all",
                    "AI tools",
                    "--file",
                    temp_file,
                    "--num-ideas",
                    "1",
                ],
            )

            # Verify CLI handles token error gracefully
            assert result.exit_code != 0

        finally:
            os.unlink(temp_file)


class TestModelServiceIntegration:
    """Test model service integration scenarios."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_settings = Mock()
        self.mock_settings.enable_smart_model_selection = True
        self.mock_settings.model_health_check_interval = 3600
        self.mock_settings.model_timeout = 10
        self.mock_settings.project_root = Path("/tmp")

    @patch("rag_startups.core.model_service.ModelManager")
    def test_model_service_initialization(self, mock_manager_class):
        """Test ModelService initialization with mocked ModelManager."""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager

        settings = get_settings()
        model_service = ModelService(settings)

        # Verify ModelManager was initialized with cache_dir
        mock_manager_class.assert_called_once()
        assert hasattr(model_service, "model_manager")
        assert model_service.settings == settings

    @patch("rag_startups.core.model_service.ModelManager")
    def test_get_language_model_with_smart_selection(self, mock_manager_class):
        """Test getting language model with smart selection enabled."""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager

        # Mock a successful model
        mock_model = Mock()
        mock_model.name = "mistralai/Mistral-7B-Instruct-v0.3"
        mock_model.model_type = ModelType.LANGUAGE_GENERATION
        mock_manager.get_best_model.return_value = mock_model

        settings = get_settings()
        settings.enable_smart_model_selection = True
        model_service = ModelService(settings)

        language_model = model_service.get_language_model()

        # Verify smart selection was used
        mock_manager.get_best_model.assert_called_once_with(
            ModelType.LANGUAGE_GENERATION, force_check=False
        )
        assert language_model == mock_model

    def test_get_language_model_with_smart_selection_disabled(self):
        """Test language model selection with smart management disabled."""
        self.mock_settings.enable_smart_model_selection = False
        self.mock_settings.language_model = "fallback-model"

        with patch("rag_startups.core.model_service.ModelManager"):
            service = ModelService(self.mock_settings)
            result = service.get_language_model()

            # Verify fallback to configured model
            assert result.name == "fallback-model"
            assert result.model_type == ModelType.LANGUAGE_GENERATION

    @patch("rag_startups.core.model_service.ModelManager")
    def test_model_health_check(self, mock_manager_class):
        """Test model health check functionality."""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager

        # Mock health check results
        mock_manager.check_model_health.side_effect = [
            ModelStatus.AVAILABLE,  # language model
            ModelStatus.AVAILABLE,  # embedding model
        ]

        settings = get_settings()
        model_service = ModelService(settings)

        health_info = model_service.check_model_health()

        # Verify health checks were performed and results are reasonable
        assert mock_manager.check_model_health.call_count >= 1
        assert health_info is not None
        assert isinstance(health_info, dict)
