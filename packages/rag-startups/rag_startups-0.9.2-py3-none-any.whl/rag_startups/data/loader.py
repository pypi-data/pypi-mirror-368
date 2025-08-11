"""Data loading and processing functionality."""

from pathlib import Path
from typing import List, Optional, Tuple, Union

import pandas as pd
from langchain_community.docstore.document import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from ..config.config import CHUNK_OVERLAP, CHUNK_SIZE
from ..core.startup_metadata import StartupLookup
from ..utils.exceptions import DataLoadError
from ..utils.timing import timing_decorator


@timing_decorator
def load_data(
    file_path: str | Path, max_lines: Optional[int] = None
) -> Tuple[pd.DataFrame, list]:
    """
    Load and preprocess startup data from a JSON file.

    Args:
        file_path: Path to the JSON file
        max_lines: Maximum number of lines to load (optional)

    Returns:
        Tuple of (preprocessed DataFrame, raw JSON data)

    Raises:
        DataLoadError: If there's an error loading or processing the data
    """
    try:
        # Convert to Path object for consistent handling
        file_path = Path(file_path)

        # Load raw JSON first
        with open(file_path, "r", encoding="utf-8") as f:
            raw_data = pd.read_json(f)
            raw_data = raw_data.fillna("")
            json_data = raw_data.to_dict("records")

        # Create DataFrame for RAG
        df = raw_data.copy()

        if not max_lines:
            max_lines = len(json_data)
        df = df.head(max_lines)
        json_data = json_data[:max_lines]

        # Keep only necessary columns for RAG
        if "long_desc" in df.columns:
            df = df[["long_desc"]]
        elif "description" in df.columns:
            df = df[["description"]]
        else:
            raise DataLoadError("No description column found in data")

        # Remove duplicates and null values before filling remaining nulls
        df.drop_duplicates(subset=df.columns[0], inplace=True)
        first_col = df.columns[0]
        df = df[df[first_col].notna() & (df[first_col] != "")]
        df = df.fillna("")

        return df, json_data
    except ValueError as e:
        raise DataLoadError(f"Invalid JSON format: {e}")
    except FileNotFoundError as e:
        raise DataLoadError(f"File not found: {e}")
    except Exception as e:
        raise DataLoadError(f"Unexpected error loading data: {e}")


@timing_decorator
def create_documents(texts: Union[pd.DataFrame, List[str]]) -> list[Document]:
    """
    Create Document objects from texts.

    Args:
        texts: Either a DataFrame containing startup descriptions or a list of text strings

    Returns:
        List of Document objects
    """
    if isinstance(texts, pd.DataFrame):
        return [
            Document(page_content=row[texts.columns[0]]) for _, row in texts.iterrows()
        ]
    else:
        return [Document(page_content=text) for text in texts if text]


@timing_decorator
def split_documents(documents: list[Document]) -> list[Document]:
    """
    Split documents into smaller chunks for processing.

    Args:
        documents: List of Document objects

    Returns:
        List of split Document objects
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
    )
    return text_splitter.split_documents(documents)


@timing_decorator
def initialize_startup_lookup(json_data: list) -> StartupLookup:
    """
    Initialize the startup lookup from JSON data.

    Args:
        json_data: List of startup JSON records

    Returns:
        Populated StartupLookup instance
    """
    return StartupLookup(json_data)
