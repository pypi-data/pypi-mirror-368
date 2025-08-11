"""Tests for market analysis functionality."""

from unittest.mock import Mock, patch

import pytest

from rag_startups.analysis.external_data import IndustryMetrics, MultiMarketInsights
from rag_startups.analysis.market_analyzer import MarketAnalyzer, MarketInsights


@pytest.fixture
def sample_idea():
    return {
        "name": "TechStartup",
        "problem": "Complex data analysis is hard",
        "solution": "AI-powered analytics platform",
        "target_market": "Enterprise software companies",
        "unique_value": ["Easy to use", "AI-powered", "Cost-effective"],
    }


@pytest.fixture
def sample_market_data():
    metrics = IndustryMetrics(
        industry_code="541511",  # Custom Computer Programming Services
        gdp_contribution=1_000_000_000,  # $1B
        employment=50000,
        growth_rate=15.0,
        market_size=5_000_000_000,  # $5B
        confidence_score=0.8,
        year=2023,
        sources=["World Bank", "BLS"],
    )
    return MultiMarketInsights(
        primary_market=metrics,
        related_markets=[metrics],
        relationships=[],
        combined_market_size=5_000_000_000,
        combined_growth_rate=15.0,
        confidence_score=0.8,
        year=2023,
        sources=["World Bank", "BLS"],
    )


def test_market_analyzer_initialization():
    """Test that MarketAnalyzer initializes correctly."""
    analyzer = MarketAnalyzer()
    assert analyzer.world_bank is not None
    assert analyzer.bls is not None


@patch("rag_startups.analysis.market_analyzer.BLSData")
def test_analyze_startup_idea(mock_bls, sample_idea, sample_market_data):
    """Test basic market analysis functionality."""
    mock_instance = Mock()
    mock_instance.get_industry_analysis.return_value = sample_market_data
    mock_bls.return_value = mock_instance

    analyzer = MarketAnalyzer()
    result = analyzer.analyze_startup_idea(sample_idea)

    assert isinstance(result, MarketInsights)
    assert result.market_size == sample_market_data.combined_market_size
    assert result.growth_rate == sample_market_data.combined_growth_rate
    assert isinstance(result.competition_level, str)
    assert isinstance(result.barriers_to_entry, list)
    assert isinstance(result.key_trends, list)
    assert isinstance(result.risk_factors, list)
    assert 0 <= result.opportunity_score <= 1
    assert result.year == sample_market_data.year
    assert result.sources == sample_market_data.sources


def test_opportunity_score_calculation(sample_market_data):
    """Test that opportunity score is calculated correctly."""
    analyzer = MarketAnalyzer()
    score = analyzer._calculate_opportunity_score(sample_market_data)
    assert 0 <= score <= 1


def test_competition_assessment(sample_market_data):
    """Test competition level assessment."""
    analyzer = MarketAnalyzer()
    competition = analyzer._assess_competition(sample_market_data)
    assert competition in ["Low", "Medium", "High"]


def test_error_handling():
    """Test error handling in market analysis."""
    analyzer = MarketAnalyzer()
    result = analyzer.analyze_startup_idea({})  # Empty idea should return None
    assert result is None
