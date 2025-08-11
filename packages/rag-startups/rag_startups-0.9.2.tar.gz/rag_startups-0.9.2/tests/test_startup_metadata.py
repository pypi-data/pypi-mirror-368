"""Tests for startup metadata functionality."""

import sys
from pathlib import Path

import pytest

from src.rag_startups.core.startup_metadata import StartupLookup

# Add src directory to Python path
sys.path.append(str(Path(__file__).parent.parent))


@pytest.fixture
def sample_startup_data():
    """Sample startup data for testing."""
    return [
        {
            "name": "AI Company",
            "description": "An AI company that does machine learning.",
            "long_desc": "An AI company that does machine learning. Using cutting-edge algorithms to solve complex problems. Targeting enterprise customers.",
            "industry": "AI",
        },
        {
            "name": "Blockchain Startup",
            "description": "A blockchain company for secure transactions.",
            "long_desc": "A blockchain company for secure transactions. Providing decentralized solutions for financial services. Focused on institutional clients.",
            "industry": "Blockchain",
        },
    ]


def test_startup_lookup_initialization(sample_startup_data):
    """Test StartupLookup initialization."""
    lookup = StartupLookup(sample_startup_data)
    assert lookup is not None
    assert len(lookup.get_all_names()) == 2


def test_get_by_name(sample_startup_data):
    """Test getting startup by name."""
    lookup = StartupLookup(sample_startup_data)

    # Test exact match
    result = lookup.get_by_name("AI Company")
    assert result is not None
    assert result["name"] == "AI Company"
    assert "long_desc" in result

    # Test case insensitive
    result = lookup.get_by_name("ai company")
    assert result is not None
    assert result["name"] == "AI Company"
    assert "long_desc" in result

    # Test non-existent company
    result = lookup.get_by_name("Non Existent")
    assert result is None


def test_get_by_description(sample_startup_data):
    """Test getting startup by description."""
    lookup = StartupLookup(sample_startup_data)

    # Test exact match with long_desc
    result = lookup.get_by_description(
        "An AI company that does machine learning. Using cutting-edge algorithms to solve complex problems. Targeting enterprise customers."
    )
    assert result is not None
    assert result["name"] == "AI Company"

    # Test case insensitive with long_desc
    result = lookup.get_by_description(
        "an ai company that does machine learning. using cutting-edge algorithms to solve complex problems. targeting enterprise customers."
    )
    assert result is not None
    assert result["name"] == "AI Company"

    # Test non-existent description
    result = lookup.get_by_description("Non existent description")
    assert result is None


def test_get_all_names(sample_startup_data):
    """Test getting all startup names."""
    lookup = StartupLookup(sample_startup_data)
    names = lookup.get_all_names()

    assert len(names) == 2
    assert "ai company" in names
    assert "blockchain startup" in names
