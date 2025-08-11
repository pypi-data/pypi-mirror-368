"""Tests for startup idea generator."""

from unittest.mock import patch

import backoff
import pytest

from rag_startups.analysis.market_analyzer import MarketInsights
from rag_startups.idea_generator.generator import RateLimitError, StartupIdeaGenerator


@pytest.fixture(autouse=True)
def _disable_backoff_sleep(monkeypatch):
    """Make backoff retries fast by removing sleep."""
    monkeypatch.setattr(backoff, "_sleep", lambda details: None, raising=False)
    # Avoid any real sleeps in code under test
    monkeypatch.setattr("time.sleep", lambda s: None)
    # Unwrap backoff-decorated generate to avoid repeated retries
    import rag_startups.idea_generator.generator as gen_mod

    gen_fn = gen_mod.StartupIdeaGenerator.generate
    wrapped = getattr(gen_fn, "__wrapped__", None)
    if wrapped is not None:
        monkeypatch.setattr(gen_mod.StartupIdeaGenerator, "generate", wrapped)


@pytest.fixture
def generator():
    """Create a generator instance with mock token."""
    with patch.dict("os.environ", {"HUGGINGFACE_TOKEN": "mock_token"}):
        return StartupIdeaGenerator()


@pytest.fixture
def mock_market_insights():
    """Create mock market insights."""
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


def test_generator_initialization():
    """Test generator initialization with token."""
    with patch.dict("os.environ", {"HUGGINGFACE_TOKEN": "mock_token"}):
        generator = StartupIdeaGenerator()
        assert generator.token == "mock_token"
        # Test that a valid model name is selected (don't hardcode specific model)
        assert generator.model_name is not None
        assert isinstance(generator.model_name, str)
        assert len(generator.model_name) > 0
        assert generator.market_analyzer is not None


def test_generator_initialization_no_token():
    """Test generator initialization without token."""
    with patch.dict("os.environ", {"HUGGINGFACE_TOKEN": ""}, clear=True):
        with pytest.raises(ValueError):
            StartupIdeaGenerator(token=None)


def test_rate_limit_check(generator):
    """Test rate limit checking."""
    assert generator._check_rate_limit() is True
    # Add max number of requests
    for _ in range(generator.max_requests_per_hour):
        generator._update_rate_limit()
    assert generator._check_rate_limit() is False


@patch("huggingface_hub.InferenceClient.text_generation")
def test_generate_basic(mock_text_generation, generator):
    """Test basic idea generation without market analysis."""
    mock_text_generation.return_value = "Test response"

    response, insights = generator.generate(num_ideas=1, include_market_analysis=False)

    assert response is not None
    assert insights is None
    mock_text_generation.assert_called_once()


@patch("huggingface_hub.InferenceClient.text_generation")
@patch("rag_startups.idea_generator.generator.parse_ideas")
@patch("rag_startups.analysis.market_analyzer.MarketAnalyzer.analyze_startup_idea")
def test_generate_with_market_analysis(
    mock_analyze, mock_parse, mock_text_generation, generator, mock_market_insights
):
    """Test idea generation with market analysis."""
    mock_text_generation.return_value = "Test response"
    mock_parse.return_value = [
        {
            "name": "TestStartup",
            "problem": "Test problem",
            "solution": "Test solution",
            "target_market": "Test market",
        }
    ]
    mock_analyze.return_value = mock_market_insights

    response, insights = generator.generate(num_ideas=1, include_market_analysis=True)

    assert response is not None
    assert insights is not None
    assert "TestStartup" in insights
    assert insights["TestStartup"].market_size == mock_market_insights.market_size
    mock_text_generation.assert_called_once()
    mock_analyze.assert_called_once()


def test_invalid_num_ideas(generator):
    """Test invalid number of ideas."""
    with pytest.raises(ValueError):
        generator.generate(num_ideas=0)
    with pytest.raises(ValueError):
        generator.generate(num_ideas=6)


@patch("huggingface_hub.InferenceClient.text_generation")
def test_rate_limit_error(mock_text_generation, generator):
    """Test rate limit error handling."""
    # Fill up rate limit
    for _ in range(generator.max_requests_per_hour):
        generator._update_rate_limit()

    with pytest.raises(RateLimitError):
        generator.generate()


@patch("huggingface_hub.InferenceClient.text_generation")
@patch("rag_startups.idea_generator.generator.parse_ideas")
@patch("rag_startups.idea_generator.generator.StartupIdeaGenerator._analyze_market")
def test_market_analysis_error_handling(
    mock_analyze_market, mock_parse, mock_text_generation, generator
):
    """Test handling of market analysis errors."""
    mock_text_generation.return_value = "Test response"
    mock_parse.return_value = [
        {
            "name": "TestStartup",
            "problem": "Test problem",
            "solution": "Test solution",
            "target_market": "Test market",
        }
    ]
    # Mock the cached _analyze_market method to return None (simulating failure)
    mock_analyze_market.return_value = None

    response, insights = generator.generate(num_ideas=1, include_market_analysis=True)

    assert response is not None
    assert insights == {}
