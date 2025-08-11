"""Tests for the CLI interface."""

import json
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from rag_startups.analysis.market_analyzer import MarketInsights
from rag_startups.cli import app

runner = CliRunner()


@pytest.fixture(autouse=True)
def mock_model_info_autouse():
    """Avoid real HF calls during CLI preflight by mocking model_info."""
    with patch("rag_startups.cli.model_info") as mi:
        mi.return_value = object()
        yield mi


@pytest.fixture
def mock_market_insights():
    """Create mock market insights for testing."""
    return MarketInsights(
        market_size=1_000_000_000,
        growth_rate=15.0,
        competition_level="Medium",
        barriers_to_entry=["High initial capital", "Technical expertise"],
        key_trends=["Rapid market growth", "AI adoption"],
        risk_factors=["Competitive market"],
        opportunity_score=0.75,
        confidence_score=0.8,
        year=2023,
        sources=["World Bank", "BLS"],
    )


@pytest.fixture
def mock_generator():
    """Create a mock generator that returns test data."""
    with patch("rag_startups.cli.StartupIdeaGenerator") as mock:
        instance = mock.return_value
        instance.generate.return_value = (
            "Test startup idea content",
            {
                "TestStartup": MarketInsights(
                    market_size=1_000_000_000,
                    growth_rate=15.0,
                    competition_level="Medium",
                    barriers_to_entry=["High initial capital"],
                    key_trends=["AI adoption"],
                    risk_factors=["Competitive market"],
                    opportunity_score=0.75,
                    confidence_score=0.8,
                    year=2023,
                    sources=["Test"],
                )
            },
        )
        yield instance


@pytest.fixture
def mock_startup_file(tmp_path):
    """Create a temporary startup data file for testing."""
    file_path = tmp_path / "test_startups.json"
    mock_data = [
        {
            "name": "Test Startup",
            "description": "A test startup description",
            "long_desc": "A longer test startup description for testing purposes",
        }
    ]
    file_path.write_text(json.dumps(mock_data))
    return str(file_path)


def test_generate_command_success(mock_generator, mock_startup_file):
    """Test successful idea generation."""
    with patch.dict("os.environ", {"HUGGINGFACE_TOKEN": "test_token"}):
        result = runner.invoke(
            app,
            ["generate-all", "AI/ML", "--num-ideas", "1", "--file", mock_startup_file],
        )
        assert result.exit_code == 0
        assert "Generated Startup Idea" in result.stdout
        assert "Market Analysis" in result.stdout
        mock_generator.generate.assert_called_once()


def test_generate_command_no_market(mock_generator, mock_startup_file):
    """Test idea generation without market analysis."""
    with patch.dict("os.environ", {"HUGGINGFACE_TOKEN": "test_token"}):
        result = runner.invoke(
            app,
            [
                "generate-all",
                "AI/ML",
                "--num-ideas",
                "1",
                "--no-market",
                "--file",
                mock_startup_file,
            ],
        )
        assert result.exit_code == 0
        assert "Generated Startup Idea" in result.stdout
        assert "Market Analysis" not in result.stdout


def test_generate_command_no_token(mock_startup_file):
    """Test handling of missing API token."""
    with patch.dict("os.environ", {}, clear=True):
        result = runner.invoke(
            app, ["generate-all", "AI/ML", "--file", mock_startup_file]
        )
        assert result.exit_code == 1
        assert "HUGGINGFACE_TOKEN environment variable not set" in result.stdout


def test_analyze_command_success(mock_generator):
    """Test successful market analysis."""
    with patch.dict("os.environ", {"HUGGINGFACE_TOKEN": "test_token"}):
        result = runner.invoke(
            app,
            [
                "analyze",
                "TestStartup",
                "A test startup description",
                "Test market",
            ],
        )
        assert result.exit_code == 0
        assert "Market Analysis" in result.stdout
        mock_generator.generate.assert_called_once()


def test_clear_command_success():
    """Test successful cache clearing."""
    with patch("rag_startups.cli.clear_cache") as mock_clear:
        result = runner.invoke(app, ["clear"])
        assert result.exit_code == 0
        assert "Successfully cleared cache" in result.stdout
        mock_clear.assert_called_once()


def test_clear_command_error():
    """Test error handling in cache clearing."""
    with patch("rag_startups.cli.clear_cache", side_effect=Exception("Test error")):
        result = runner.invoke(app, ["clear"])
        assert result.exit_code == 1
        assert "Failed to clear cache" in result.stdout


def test_invalid_num_ideas(mock_generator, mock_startup_file):
    """Test validation of number of ideas."""
    with patch.dict("os.environ", {"HUGGINGFACE_TOKEN": "test_token"}):
        result = runner.invoke(
            app,
            ["generate-all", "AI/ML", "--num-ideas", "10", "--file", mock_startup_file],
        )
        assert result.exit_code == 1
        assert "num_ideas must be between 1 and 5" in result.stdout


def test_missing_startup_file(mock_generator):
    """Test handling of missing startup data file."""
    with patch.dict("os.environ", {"HUGGINGFACE_TOKEN": "test_token"}):
        result = runner.invoke(
            app, ["generate-all", "AI/ML", "--file", "nonexistent.json"]
        )
        assert result.exit_code == 1
        assert "Startup data file 'nonexistent.json' not found" in result.stdout
