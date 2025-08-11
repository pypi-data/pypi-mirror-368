#!/usr/bin/env python3
"""Convert YC startup data from CSV to JSON format."""
import argparse
import csv
import json
from pathlib import Path
from typing import Any, Dict, List


def clean_description(desc: str) -> str:
    """Clean and format description text."""
    if not desc:
        return ""
    # Remove extra whitespace and newlines
    return " ".join(desc.split())


def clean_text(text: str) -> str:
    """Clean and format any text field."""
    if not text:
        return ""
    # Remove extra whitespace and newlines
    return " ".join(text.split())


def extract_year_from_batch(batch: str) -> str:
    """Extract year from YC batch string (e.g., 'S08' -> '2008', 'W20' -> '2020')."""
    if not batch:
        return ""
    # Extract the year part (last 2 digits)
    year_str = "".join(c for c in batch if c.isdigit())
    if not year_str:
        return ""
    # Convert 2-digit year to 4-digit year
    year_num = int(year_str)
    if year_num < 50:  # Assume 00-49 means 2000-2049
        return f"20{year_str:0>2}"
    else:  # Assume 50-99 means 1950-1999
        return f"19{year_str:0>2}"


def convert_csv_to_json(csv_path: str, output_path: str = None) -> List[Dict[str, Any]]:
    """
    Convert YC startup data from CSV to JSON format.

    Args:
        csv_path: Path to input CSV file
        output_path: Optional path to save JSON output

    Returns:
        List of startup data dictionaries
    """
    if not Path(csv_path).exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    startups = []

    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        # Use csv.reader with custom quoting to handle multiline fields
        reader = csv.DictReader(
            f, quoting=csv.QUOTE_ALL, quotechar='"', skipinitialspace=True
        )
        for row in reader:
            print(f"Processing row: {row}")  # Debug print
            startup = {
                "name": clean_text((row.get("Company Name", "") or "").strip()),
                "description": clean_description(row.get("Description", "")),
                "category": (row.get("Category", "") or "").strip(),
                "year": extract_year_from_batch((row.get("Batch", "") or "").strip()),
            }
            print(f"Created startup entry: {startup}")  # Debug print
            # Only include startups with name and description
            if startup["name"] and startup["description"]:
                startups.append(startup)

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(startups, f, indent=2, ensure_ascii=False)

    return startups


def main():
    parser = argparse.ArgumentParser(
        description="Convert YC startup data from CSV to JSON"
    )
    parser.add_argument("csv_file", help="Input CSV file path")
    parser.add_argument("--output", "-o", help="Output JSON file path")

    args = parser.parse_args()

    try:
        startups = convert_csv_to_json(args.csv_file, args.output)
        print(f"Processed {len(startups)} startups")
        if args.output:
            print(f"Saved to {args.output}")
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
