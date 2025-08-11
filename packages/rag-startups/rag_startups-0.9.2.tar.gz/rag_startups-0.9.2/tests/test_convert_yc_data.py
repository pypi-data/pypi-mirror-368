"""Tests for YC data conversion script."""

import json
import sys
from pathlib import Path

import pytest

from rag_startups.data.convert_yc_data import clean_description, convert_csv_to_json

# Add src directory to Python path
sys.path.append(str(Path(__file__).parent.parent / "src"))


# Get the test data directory
TEST_DIR = Path(__file__).parent
DATA_DIR = TEST_DIR / "data"
SAMPLE_CSV = DATA_DIR / "sample_yc.csv"


def test_clean_description():
    """Test description cleaning function."""
    # Test multiline description
    multiline = """This description
    has multiple
    lines"""
    assert clean_description(multiline) == "This description has multiple lines"

    # Test empty description
    assert clean_description("") == ""
    assert clean_description(None) == ""

    # Test extra whitespace
    assert clean_description("  extra   spaces  ") == "extra spaces"


def test_convert_csv_to_json(tmp_path):
    """Test CSV to JSON conversion."""
    # Test with output file
    output_file = tmp_path / "output.json"
    startups = convert_csv_to_json(str(SAMPLE_CSV), str(output_file))

    # Check returned data
    assert (
        len(startups) == 4
    )  # Should only include entries with both name and description

    # Verify specific entries
    airbnb = next(s for s in startups if s["name"] == "Airbnb")
    assert airbnb["year"] == "2008"
    assert airbnb["category"] == "Marketplace"
    assert "trusted community marketplace" in airbnb["description"]

    stripe = next(s for s in startups if s["name"] == "Stripe")
    assert stripe["year"] == "2009"
    assert stripe["category"] == "Fintech"

    # Check multiline description handling
    weird = next(
        s for s in startups if "description has multiple lines" in s["description"]
    )
    assert weird["category"] == "Other"
    assert weird["year"] == "2020"

    # Verify output file
    assert output_file.exists()
    with open(output_file, "r", encoding="utf-8") as f:
        saved_data = json.load(f)
    assert len(saved_data) == len(startups)


def test_missing_file():
    """Test handling of missing input file."""
    with pytest.raises(FileNotFoundError):
        convert_csv_to_json("nonexistent.csv")


def test_empty_csv(tmp_path):
    """Test handling of empty CSV file."""
    empty_csv = tmp_path / "empty.csv"
    empty_csv.write_text("Company Name,Description,Category,Batch\n")

    startups = convert_csv_to_json(str(empty_csv))
    assert len(startups) == 0


def test_malformed_csv(tmp_path):
    """Test handling of malformed CSV."""
    bad_csv = tmp_path / "bad.csv"
    bad_csv.write_text("Bad,CSV,File\nNo,Headers,Here\n")

    # Should handle gracefully, returning empty list
    startups = convert_csv_to_json(str(bad_csv))
    assert len(startups) == 0
