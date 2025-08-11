"""Main entry point for the RAG Startups application.

This application combines RAG-based startup research with AI idea generation:
1. First, it finds relevant existing startups from the YC database
2. Then uses these as examples to generate new, innovative startup ideas

Required Environment Variables:
-----------------------------
For LangSmith integration:
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
LANGCHAIN_API_KEY="your_langsmith_api_key"
LANGCHAIN_PROJECT="rag_startups"

For idea generation:
HUGGINGFACE_TOKEN="your_huggingface_token"

Optional Environment Variables:
----------------------------
LOCAL_LANGUAGE_MODEL: Name of the local language model to use (default: gpt2)
MAX_LINES: Maximum number of lines to process from the data file (default: 500000)
"""

import sys

from .cli import app


def main():
    """
    Main entry point that uses the CLI interface
    """
    return app()


if __name__ == "__main__":
    sys.exit(main())
