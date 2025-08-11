"""Tests for enhanced configuration management system."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from src.rag_startups.config import (
    ConfigurationMigrator,
    ConfigurationValidator,
    Environment,
    LogLevel,
    RAGSettings,
    get_settings,
    reload_settings,
)


class TestRAGSettings:
    """Test the RAGSettings configuration class."""

    def test_default_settings(self):
        """Test default configuration values."""
        with patch.dict(os.environ, {"HUGGINGFACE_TOKEN": "test-token"}, clear=True):
            settings = RAGSettings()

            assert settings.environment == Environment.DEVELOPMENT
            assert settings.huggingface_token == "test-token"
            assert settings.embedding_model == "all-MiniLM-L6-v2"
            assert settings.language_model == "gpt2"
            assert settings.chunk_size == 1000
            assert settings.chunk_overlap == 200
            assert settings.retriever_top_k == 4
            assert settings.search_type == "similarity"
            assert settings.log_level == LogLevel.INFO

    def test_environment_variables_override(self):
        """Test that environment variables override defaults."""
        env_vars = {
            "HUGGINGFACE_TOKEN": "custom-token",
            "RAG_ENVIRONMENT": "production",
            "RAG_EMBEDDING_MODEL": "custom-model",
            "RAG_CHUNK_SIZE": "2000",
            "RAG_CHUNK_OVERLAP": "400",
            "RAG_RETRIEVER_TOP_K": "8",
            "RAG_LOG_LEVEL": "DEBUG",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = RAGSettings()

            assert settings.huggingface_token == "custom-token"
            assert settings.environment == Environment.PRODUCTION
            assert settings.embedding_model == "custom-model"
            assert settings.chunk_size == 2000
            assert settings.chunk_overlap == 400
            assert settings.retriever_top_k == 8
            assert settings.log_level == LogLevel.DEBUG

    def test_validation_chunk_overlap_less_than_size(self):
        """Test validation that chunk overlap must be less than chunk size."""
        with patch.dict(os.environ, {"HUGGINGFACE_TOKEN": "test-token"}, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                RAGSettings(chunk_size=1000, chunk_overlap=1000)

            assert "chunk_overlap must be less than chunk_size" in str(exc_info.value)

    def test_validation_chunk_size_range(self):
        """Test validation of chunk size range."""
        with patch.dict(os.environ, {"HUGGINGFACE_TOKEN": "test-token"}, clear=True):
            # Test minimum
            with pytest.raises(ValidationError):
                RAGSettings(chunk_size=50)  # Below minimum of 100

            # Test maximum
            with pytest.raises(ValidationError):
                RAGSettings(chunk_size=5000)  # Above maximum of 4000

    def test_validation_retriever_top_k_range(self):
        """Test validation of retriever top_k range."""
        with patch.dict(os.environ, {"HUGGINGFACE_TOKEN": "test-token"}, clear=True):
            # Test minimum
            with pytest.raises(ValidationError):
                RAGSettings(retriever_top_k=0)  # Below minimum of 1

            # Test maximum
            with pytest.raises(ValidationError):
                RAGSettings(retriever_top_k=25)  # Above maximum of 20

    def test_validation_search_type_enum(self):
        """Test validation of search type enum."""
        with patch.dict(os.environ, {"HUGGINGFACE_TOKEN": "test-token"}, clear=True):
            # Valid values should work
            settings = RAGSettings(search_type="similarity")
            assert settings.search_type == "similarity"

            settings = RAGSettings(search_type="mmr")
            assert settings.search_type == "mmr"

            # Invalid value should fail
            with pytest.raises(ValidationError):
                RAGSettings(search_type="invalid_search_type")

    def test_missing_required_token(self):
        """Test that missing HuggingFace token raises validation error."""
        # Test by trying to create settings with explicitly empty token
        with pytest.raises(ValidationError) as exc_info:
            RAGSettings(huggingface_token="")

        assert "huggingface_token" in str(exc_info.value).lower()

    def test_property_methods(self):
        """Test property methods for derived values."""
        with patch.dict(os.environ, {"HUGGINGFACE_TOKEN": "test-token"}, clear=True):
            settings = RAGSettings()

            # Test directory properties
            assert settings.data_dir == settings.project_root / "data"
            assert settings.models_dir == settings.project_root / "models"
            assert settings.cache_dir == settings.project_root / ".cache"

            # Test environment checks
            assert settings.is_development is True
            assert settings.is_testing is False
            assert settings.is_production is False

    def test_langchain_config_property(self):
        """Test LangChain configuration property."""
        env_vars = {
            "HUGGINGFACE_TOKEN": "test-token",
            "LANGCHAIN_TRACING_V2": "true",
            "LANGCHAIN_API_KEY": "test-langchain-key",
            "LANGCHAIN_PROJECT": "test-project",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = RAGSettings()
            config = settings.langchain_config

            assert config["tracing_v2"] is True
            assert config["api_key"] == "test-langchain-key"
            assert config["project"] == "test-project"
            assert config["endpoint"] == "https://api.smith.langchain.com"

    def test_prompt_template_by_environment(self):
        """Test that prompt template varies by environment."""
        # Development environment
        with patch.dict(
            os.environ,
            {"HUGGINGFACE_TOKEN": "test-token", "RAG_ENVIRONMENT": "development"},
            clear=True,
        ):
            settings = RAGSettings()
            dev_template = settings.get_prompt_template()
            assert "detailed explanations" in dev_template

        # Production environment
        with patch.dict(
            os.environ,
            {"HUGGINGFACE_TOKEN": "test-token", "RAG_ENVIRONMENT": "production"},
            clear=True,
        ):
            settings = RAGSettings()
            prod_template = settings.get_prompt_template()
            assert "detailed explanations" not in prod_template


class TestConfigurationSingleton:
    """Test the global settings singleton pattern."""

    def test_get_settings_singleton(self):
        """Test that get_settings returns the same instance."""
        with patch.dict(os.environ, {"HUGGINGFACE_TOKEN": "test-token"}, clear=True):
            settings1 = get_settings()
            settings2 = get_settings()

            assert settings1 is settings2

    def test_reload_settings(self):
        """Test that reload_settings creates a new instance."""
        with patch.dict(os.environ, {"HUGGINGFACE_TOKEN": "test-token"}, clear=True):
            settings1 = get_settings()
            settings2 = reload_settings()

            # Should be different instances but same values
            assert settings1 is not settings2
            assert settings1.huggingface_token == settings2.huggingface_token


class TestConfigurationValidator:
    """Test the configuration validator."""

    def test_validator_initialization(self):
        """Test validator can be initialized."""
        validator = ConfigurationValidator()
        assert validator is not None

    def test_validate_environment_success(self):
        """Test successful environment validation."""
        with patch.dict(os.environ, {"HUGGINGFACE_TOKEN": "test-token"}, clear=True):
            validator = ConfigurationValidator()

            # Mock the data directory to exist
            with patch.object(Path, "exists", return_value=True):
                # Mock SentenceTransformer to avoid actual model loading
                with patch("sentence_transformers.SentenceTransformer"):
                    is_valid, errors = validator.validate_environment()

                    assert is_valid is True
                    assert len(errors) == 0

    def test_validate_environment_missing_token(self):
        """Test validation failure with missing token."""
        with patch.dict(os.environ, {}, clear=True):
            # Mock .env file to not exist so token is truly missing
            with patch("pathlib.Path.is_file", return_value=False):
                validator = ConfigurationValidator()
                is_valid, errors = validator.validate_environment()

                assert is_valid is False
                assert any("huggingface_token" in error.lower() for error in errors)

    def test_generate_env_template(self):
        """Test environment template generation."""
        validator = ConfigurationValidator()

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / ".env.test"
            result_path = validator.generate_env_template(output_path)

            assert result_path == output_path
            assert output_path.exists()

            content = output_path.read_text()
            assert "HUGGINGFACE_TOKEN" in content
            assert "RAG_ENVIRONMENT" in content
            assert "RAG_EMBEDDING_MODEL" in content


class TestConfigurationMigrator:
    """Test the configuration migrator."""

    def test_migrator_initialization(self):
        """Test migrator can be initialized."""
        migrator = ConfigurationMigrator()
        assert migrator is not None

    def test_detect_old_config_missing(self):
        """Test detection when no old config exists."""
        migrator = ConfigurationMigrator()

        # Mock the old config path to not exist
        with patch.object(Path, "exists", return_value=False):
            old_config = migrator.detect_old_config()
            assert old_config == {}

    def test_detect_old_config_present(self):
        """Test detection of old configuration values."""
        migrator = ConfigurationMigrator()

        # Mock old config content
        old_config_content = """
DEFAULT_EMBEDDING_MODEL = "test-model"
CHUNK_SIZE = 1500
CHUNK_OVERLAP = 300
DEFAULT_RETRIEVER_TOP_K = 6
        """

        with patch.object(Path, "exists", return_value=True):
            with patch.object(Path, "read_text", return_value=old_config_content):
                old_config = migrator.detect_old_config()

                assert old_config["DEFAULT_EMBEDDING_MODEL"] == "test-model"
                assert old_config["CHUNK_SIZE"] == 1500
                assert old_config["CHUNK_OVERLAP"] == 300
                assert old_config["DEFAULT_RETRIEVER_TOP_K"] == 6

    def test_generate_migration_env(self):
        """Test migration .env file generation."""
        migrator = ConfigurationMigrator()

        old_config = {
            "DEFAULT_EMBEDDING_MODEL": "test-model",
            "CHUNK_SIZE": 1500,
            "CHUNK_OVERLAP": 300,
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock project root
            migrator.project_root = Path(temp_dir)

            env_path = migrator.generate_migration_env(old_config)

            assert env_path.exists()
            content = env_path.read_text()

            assert "RAG_EMBEDDING_MODEL=test-model" in content
            assert "RAG_CHUNK_SIZE=1500" in content
            assert "RAG_CHUNK_OVERLAP=300" in content
            assert "HUGGINGFACE_TOKEN=" in content


class TestBackwardCompatibility:
    """Test backward compatibility functions."""

    def test_convenience_functions(self):
        """Test that convenience functions work with new settings."""
        from src.rag_startups.config import (
            get_chunk_size,
            get_embedding_model,
            get_huggingface_token,
            get_retriever_config,
        )

        with patch.dict(os.environ, {"HUGGINGFACE_TOKEN": "test-token"}, clear=True):
            # Test convenience functions
            assert get_huggingface_token() == "test-token"
            assert get_embedding_model() == "all-MiniLM-L6-v2"
            assert get_chunk_size() == 1000

            retriever_config = get_retriever_config()
            assert retriever_config["top_k"] == 4
            assert retriever_config["search_type"] == "similarity"


@pytest.fixture(autouse=True)
def reset_settings_singleton():
    """Reset the global settings singleton between tests."""
    from src.rag_startups.config.settings import _settings

    # Store original state
    original_settings = _settings

    yield

    # Reset to original state
    import src.rag_startups.config.settings as settings_module

    settings_module._settings = original_settings
