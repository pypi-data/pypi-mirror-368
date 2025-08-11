"""Test with real YC startup data."""

import json
import os
import random
import sys

from src.rag_startups.core.rag_chain import format_startup_idea
from src.rag_startups.core.startup_metadata import StartupLookup
from src.rag_startups.data.loader import create_documents, split_documents
from src.rag_startups.embeddings.embedding import create_vectorstore, setup_retriever

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_test_data():
    """Load test data and handle potential errors."""
    try:
        with open("data/yc_startups.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: data/yc_startups.json not found")
        return []
    except json.JSONDecodeError:
        print("Error: Invalid JSON in data file")
        return []
    except Exception as e:
        print(f"Unexpected error loading data: {str(e)}")
        return []


def setup_test_retriever(data):
    """Setup test retriever with given data."""
    # Convert data to DataFrame format
    texts = [item.get("long_desc", item.get("description", "")) for item in data]
    texts = [t for t in texts if t]  # Remove empty descriptions

    documents = create_documents(texts)
    splits = split_documents(documents)

    # Create vectorstore and retriever
    vectorstore = create_vectorstore([doc.page_content for doc in splits])
    return setup_retriever(vectorstore)


def setup_test_lookup(data):
    """Setup test startup lookup with given data."""
    lookup = StartupLookup()
    for item in data:
        desc = item.get("long_desc", item.get("description", ""))
        if desc:
            lookup.add_startup(desc, item)
    return lookup


def test_basic_lookup():
    """Test basic lookup functionality with real data."""
    print("\nTesting basic lookup with real data:")
    print("-" * 50)

    data = load_test_data()
    if not data:
        print("No data available for testing")
        return

    retriever = setup_test_retriever(data[:10])  # Test with first 10 items
    lookup = setup_test_lookup(data[:10])  # Initialize lookup with same data

    for item in data[:10]:
        desc = item.get("long_desc", item.get("description", ""))
        if desc:
            result = format_startup_idea(desc, retriever, lookup)
            print(f"\nActual company: {item['name']}")
            print(f"Found company: {result['Company']}")
            print(f"Match: {'✓' if result['Company'] == item['name'] else '✗'}")


def test_edge_cases():
    """Test edge cases in real data."""
    print("\nTesting edge cases in real data:")
    print("-" * 50)

    data = load_test_data()
    if not data:
        return

    # Find interesting edge cases in real data
    edge_cases = []
    for item in data:
        desc = item.get("long_desc", item.get("description", ""))

        # Look for various edge cases
        if desc and any(
            [
                len(desc) > 1000,  # Very long description
                "\n" in desc,  # Multi-line
                "@" in desc or "#" in desc,  # Special characters
                "<" in desc or ">" in desc,  # HTML-like content
                any(ord(c) > 127 for c in desc),  # Unicode characters
            ]
        ):
            edge_cases.append(item)

    if edge_cases:
        retriever = setup_test_retriever(edge_cases[:5])  # Test with first 5 edge cases

        print(f"\nFound {len(edge_cases)} edge cases in real data")
        for item in edge_cases[:5]:
            desc = item.get("long_desc", item.get("description", ""))
            try:
                result = format_startup_idea(desc, retriever)
                print(
                    f"\nEdge case type: "
                    f"{'Long' if len(desc) > 1000 else 'Special chars'}"
                )
                print(f"Company: {item['name']}")
                print(f"Description: {desc[:100]}...")
                print(f"Result: {result['Company']}")
            except Exception as e:
                print(f"Error processing edge case: {str(e)}")


def test_random_samples():
    """Test random samples from the dataset."""
    print("\nTesting random samples:")
    print("-" * 50)

    data = load_test_data()
    if not data:
        return

    # Get 5 random samples
    samples = random.sample(data, min(5, len(data)))
    retriever = setup_test_retriever(samples)

    for item in samples:
        desc = item.get("long_desc", item.get("description", ""))
        if desc:
            try:
                result = format_startup_idea(desc, retriever)
                print("\nRandom sample:")
                print(f"Company: {item['name']}")
                print(f"Description: {desc[:100]}...")
                print(f"Result: {result['Company']}")
            except Exception as e:
                print(f"Error processing random sample: {str(e)}")


def test_error_handling():
    """Test error handling with real data."""
    print("\nTesting error handling:")
    print("-" * 50)

    data = load_test_data()
    if not data:
        return

    retriever = setup_test_retriever(data[:5])  # Use first 5 items for testing

    # Test various error cases
    error_cases = [
        None,
        "",
        "A" * 10000,  # Very long input
        "🚀" * 100,  # Lots of emojis
        "<script>alert('test')</script>",  # Script injection attempt
        {"name": "Invalid", "desc": "Invalid input type"},  # Wrong type
    ]

    for case in error_cases:
        try:
            result = format_startup_idea(case, retriever)
            print(f"\nInput type: {type(case)}")
            print(f"Result: {result}")
        except Exception as e:
            print(f"Expected error for {type(case)}: {str(e)}")


if __name__ == "__main__":
    test_basic_lookup()
    test_edge_cases()
    test_random_samples()
    test_error_handling()
