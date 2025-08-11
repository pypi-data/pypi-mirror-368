"""Tests for data loading functionality."""

import json
import tempfile
from pathlib import Path

import pandas as pd
import pytest

from src.rag_startups.data.loader import load_data
from src.rag_startups.utils.exceptions import DataLoadError


@pytest.fixture
def sample_data():
    """Create sample startup data."""
    return [
        {"long_desc": "A startup that helps people find homes"},
        {"long_desc": "An AI company that revolutionizes healthcare"},
        {"long_desc": "A platform for connecting freelancers"},
        {"long_desc": None},  # Test handling of null values
        {"long_desc": "A startup that helps people find homes"},  # Duplicate
    ]


@pytest.fixture
def temp_json_file(sample_data):
    """Create a temporary JSON file with sample data."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(sample_data, f)
    temp_path = Path(f.name)
    yield temp_path
    temp_path.unlink()


def test_load_data_success(temp_json_file):
    """Test successful data loading."""
    df, json_data = load_data(temp_json_file)

    # Test DataFrame
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 3  # After removing duplicates and null values
    assert list(df.columns) == ["long_desc"]
    assert df["long_desc"].isna().sum() == 0

    # Test JSON data
    assert isinstance(json_data, list)
    assert len(json_data) == 5  # Original data before cleaning


def test_load_data_with_limit(temp_json_file):
    """Test data loading with line limit."""
    df, json_data = load_data(temp_json_file, max_lines=2)

    assert len(df) == 2
    assert len(json_data) == 2


def test_load_data_file_not_found():
    """Test handling of non-existent file."""
    with pytest.raises(DataLoadError):
        load_data("nonexistent.json")


def test_load_data_invalid_json(tmp_path):
    """Test handling of invalid JSON file."""
    invalid_json = tmp_path / "invalid.json"
    invalid_json.write_text("invalid json content")

    with pytest.raises(DataLoadError):
        load_data(invalid_json)
