import os
import sys

from src.rag_startups.core.rag_chain import format_startup_idea

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Test cases
TEST_CASES = [
    "Link helps fintech risk and AML compliance teams automate their workflows.",
    "Help desk software for modern teams.",
    "Deel helps companies hire anyone, anywhere.",
    "We build software for healthcare.",
    "The platform for all your needs.",
    "Stripe is a technology company that builds economic infrastructure.",
    "Link exists to help businesses grow.",
    "Platform that helps businesses scale.",
]


def test_format_startup_idea_structure():
    """Test that format_startup_idea returns correct structure for each test case."""
    for text in TEST_CASES:
        result = format_startup_idea(text, None)

        # Check that all required fields are present
        assert isinstance(result, dict), f"Result should be a dict for input: {text}"
        assert "Problem" in result, f"Missing 'Problem' field for input: {text}"
        assert "Solution" in result, f"Missing 'Solution' field for input: {text}"
        assert "Market" in result, f"Missing 'Market' field for input: {text}"
        assert "Value" in result, f"Missing 'Value' field for input: {text}"

        # Check that fields are non-empty strings
        assert isinstance(
            result["Problem"], str
        ), f"'Problem' should be string for input: {text}"
        assert isinstance(
            result["Solution"], str
        ), f"'Solution' should be string for input: {text}"
        assert isinstance(
            result["Market"], str
        ), f"'Market' should be string for input: {text}"
        assert isinstance(
            result["Value"], str
        ), f"'Value' should be string for input: {text}"

        # Check that fields are not empty
        assert result[
            "Problem"
        ].strip(), f"'Problem' should not be empty for input: {text}"
        assert result[
            "Solution"
        ].strip(), f"'Solution' should not be empty for input: {text}"
        assert result[
            "Market"
        ].strip(), f"'Market' should not be empty for input: {text}"
        assert result["Value"].strip(), f"'Value' should not be empty for input: {text}"
