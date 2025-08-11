"""Configuration validation and migration utilities."""

import os
import sys
from pathlib import Path
from typing import List, Optional, Tuple

from pydantic import ValidationError
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .settings import get_settings


class ConfigurationValidator:
    """Validate and migrate configuration settings."""

    def __init__(self, console: Optional[Console] = None):
        """Initialize validator with optional console for output."""
        self.console = console or Console()

    def validate_environment(self) -> Tuple[bool, List[str]]:
        """Validate current environment configuration.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        try:
            settings = get_settings()
            self.console.print("[green]✓[/green] Configuration loaded successfully")

            # Validate critical paths
            if not settings.data_dir.exists():
                errors.append(f"Data directory does not exist: {settings.data_dir}")

            # Validate API token
            if (
                not settings.huggingface_token
                or settings.huggingface_token == "your-token-here"
            ):
                errors.append("Invalid HuggingFace token - please set a real token")

            # Validate model accessibility
            try:
                from sentence_transformers import SentenceTransformer

                SentenceTransformer(settings.embedding_model)
                self.console.print(
                    f"[green]✓[/green] Embedding model '{settings.embedding_model}' is accessible"
                )
            except Exception as e:
                errors.append(
                    f"Cannot load embedding model '{settings.embedding_model}': {e}"
                )

            # Validate chunk configuration
            if settings.chunk_overlap >= settings.chunk_size:
                errors.append(
                    f"Chunk overlap ({settings.chunk_overlap}) must be less than chunk size ({settings.chunk_size})"
                )

            return len(errors) == 0, errors

        except ValidationError as e:
            for error in e.errors():
                field = " -> ".join(str(loc) for loc in error["loc"])
                errors.append(f"{field}: {error['msg']}")
            return False, errors
        except Exception as e:
            errors.append(f"Unexpected error: {e}")
            return False, errors

    def display_current_config(self) -> None:
        """Display current configuration in a formatted table."""
        try:
            settings = get_settings()

            # Create configuration table
            table = Table(title="Current RAG Configuration")
            table.add_column("Setting", style="cyan", no_wrap=True)
            table.add_column("Value", style="magenta")
            table.add_column("Source", style="green")

            # Environment settings
            table.add_row("Environment", settings.environment.value, "RAG_ENVIRONMENT")
            table.add_row("Log Level", settings.log_level.value, "RAG_LOG_LEVEL")

            # API settings
            token_display = (
                f"{settings.huggingface_token[:8]}..."
                if len(settings.huggingface_token) > 8
                else "***"
            )
            table.add_row("HuggingFace Token", token_display, "HUGGINGFACE_TOKEN")

            # Model settings
            table.add_row(
                "Embedding Model", settings.embedding_model, "RAG_EMBEDDING_MODEL"
            )
            table.add_row(
                "Language Model", settings.language_model, "RAG_LANGUAGE_MODEL"
            )

            # Processing settings
            table.add_row("Chunk Size", str(settings.chunk_size), "RAG_CHUNK_SIZE")
            table.add_row(
                "Chunk Overlap", str(settings.chunk_overlap), "RAG_CHUNK_OVERLAP"
            )
            table.add_row("Max Lines", str(settings.max_lines), "RAG_MAX_LINES")

            # Retriever settings
            table.add_row(
                "Retriever Top K", str(settings.retriever_top_k), "RAG_RETRIEVER_TOP_K"
            )
            table.add_row("Search Type", settings.search_type, "RAG_SEARCH_TYPE")

            # Performance settings
            table.add_row(
                "Rate Limit",
                f"{settings.rate_limit_requests}/hour",
                "RAG_RATE_LIMIT_REQUESTS",
            )
            table.add_row(
                "Caching Enabled", str(settings.enable_caching), "RAG_ENABLE_CACHING"
            )
            table.add_row("Cache TTL", f"{settings.cache_ttl}s", "RAG_CACHE_TTL")

            self.console.print(table)

        except Exception as e:
            self.console.print(f"[red]Error displaying configuration: {e}[/red]")

    def check_migration_needed(self) -> Tuple[bool, List[str]]:
        """Check if migration from old config is needed.

        Returns:
            Tuple of (migration_needed, list_of_recommendations)
        """
        recommendations = []
        migration_needed = False

        # Check for old config.py usage
        old_config_path = (
            Path(__file__).parent.parent.parent.parent / "config" / "config.py"
        )
        if old_config_path.exists():
            migration_needed = True
            recommendations.append(
                "Old config.py file detected - consider migrating to new settings system"
            )

        # Check for hardcoded values in code
        src_dir = Path(__file__).parent.parent
        hardcoded_patterns = [
            (
                "all-MiniLM-L6-v2",
                "Consider using RAG_EMBEDDING_MODEL environment variable",
            ),
            ("gpt2", "Consider using RAG_LANGUAGE_MODEL environment variable"),
            ("1000", "Consider using RAG_CHUNK_SIZE environment variable"),
            ("200", "Consider using RAG_CHUNK_OVERLAP environment variable"),
        ]

        for pattern, recommendation in hardcoded_patterns:
            # This is a simplified check - in practice, you'd want more sophisticated
            # analysis
            if any(
                pattern in file.read_text(encoding="utf-8", errors="ignore")
                for file in src_dir.rglob("*.py")
                if file.is_file()
            ):
                recommendations.append(recommendation)

        # Check environment variables
        env_vars_to_check = [
            ("RAG_ENVIRONMENT", "Set environment (development/testing/production)"),
            ("RAG_LOG_LEVEL", "Set logging level for better debugging"),
            ("RAG_ENABLE_CACHING", "Configure caching for better performance"),
        ]

        for env_var, recommendation in env_vars_to_check:
            if not os.getenv(env_var):
                recommendations.append(f"Consider setting {env_var}: {recommendation}")

        return migration_needed, recommendations

    def generate_env_template(self, output_path: Optional[Path] = None) -> Path:
        """Generate .env template file with all available settings.

        Args:
            output_path: Optional path for output file

        Returns:
            Path to generated template file
        """
        if output_path is None:
            output_path = Path.cwd() / ".env.template"

        template_content = """# RAG Startups Configuration Template
# Copy this file to .env and customize the values

# =============================================================================
# REQUIRED SETTINGS
# =============================================================================

# HuggingFace API Token (REQUIRED)
# Get your token from: https://huggingface.co/settings/tokens
HUGGINGFACE_TOKEN=your-token-here

# =============================================================================
# ENVIRONMENT SETTINGS
# =============================================================================

# Application environment: development, testing, production
RAG_ENVIRONMENT=development

# Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL
RAG_LOG_LEVEL=INFO

# Optional log file path
# RAG_LOG_FILE=/path/to/logfile.log

# =============================================================================
# MODEL CONFIGURATION
# =============================================================================

# Embedding model for vector search
RAG_EMBEDDING_MODEL=all-MiniLM-L6-v2

# Local language model for text generation
RAG_LANGUAGE_MODEL=gpt2

# =============================================================================
# TEXT PROCESSING
# =============================================================================

# Text chunk size for document splitting (100-4000)
RAG_CHUNK_SIZE=1000

# Overlap between text chunks (0-1000, must be < chunk_size)
RAG_CHUNK_OVERLAP=200

# Maximum lines to process from data files
RAG_MAX_LINES=500000

# =============================================================================
# RETRIEVAL CONFIGURATION
# =============================================================================

# Number of documents to retrieve (1-20)
RAG_RETRIEVER_TOP_K=4

# Search type: similarity, mmr, similarity_score_threshold
RAG_SEARCH_TYPE=similarity

# =============================================================================
# PERFORMANCE SETTINGS
# =============================================================================

# Rate limiting for API calls
RAG_RATE_LIMIT_REQUESTS=120
RAG_RATE_LIMIT_WINDOW=3600

# Caching configuration
RAG_ENABLE_CACHING=true
RAG_CACHE_TTL=3600

# Processing performance
RAG_MAX_WORKERS=4
RAG_BATCH_SIZE=32

# =============================================================================
# LANGCHAIN INTEGRATION (OPTIONAL)
# =============================================================================

# Enable LangChain tracing
LANGCHAIN_TRACING_V2=false

# LangChain API configuration
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=your-langchain-api-key
LANGCHAIN_PROJECT=rag_startups

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================

# Database connection URL
RAG_DATABASE_URL=sqlite:///./rag_startups.db

# =============================================================================
# API CONFIGURATION
# =============================================================================

# HuggingFace API base URL
HUGGINGFACE_API_URL=https://api-inference.huggingface.co/models
"""

        output_path.write_text(template_content)
        self.console.print(
            f"[green]✓[/green] Environment template generated: {output_path}"
        )
        return output_path

    def run_health_check(self) -> bool:
        """Run comprehensive health check of the configuration.

        Returns:
            True if all checks pass, False otherwise
        """
        self.console.print(Panel("RAG Configuration Health Check", style="bold blue"))

        # Validate environment
        is_valid, errors = self.validate_environment()

        if errors:
            self.console.print("\n[red]Configuration Errors:[/red]")
            for error in errors:
                self.console.print(f"  • {error}")

        # Check migration needs
        migration_needed, recommendations = self.check_migration_needed()

        if recommendations:
            self.console.print("\n[yellow]Recommendations:[/yellow]")
            for rec in recommendations:
                self.console.print(f"  • {rec}")

        # Display current config
        self.console.print("\n")
        self.display_current_config()

        # Summary
        if is_valid and not migration_needed:
            self.console.print("\n[green]✓ Configuration is healthy![/green]")
        elif is_valid:
            self.console.print(
                "\n[yellow]⚠ Configuration is valid but could be improved[/yellow]"
            )
        else:
            self.console.print(
                "\n[red]✗ Configuration has errors that need to be fixed[/red]"
            )

        return is_valid


def main():
    """CLI entry point for configuration validation."""
    import argparse

    parser = argparse.ArgumentParser(description="RAG Configuration Validator")
    parser.add_argument("--health-check", action="store_true", help="Run health check")
    parser.add_argument(
        "--generate-template", action="store_true", help="Generate .env template"
    )
    parser.add_argument("--output", type=Path, help="Output path for template")

    args = parser.parse_args()

    validator = ConfigurationValidator()

    if args.generate_template:
        validator.generate_env_template(args.output)
    elif args.health_check:
        success = validator.run_health_check()
        sys.exit(0 if success else 1)
    else:
        validator.run_health_check()


if __name__ == "__main__":
    main()
