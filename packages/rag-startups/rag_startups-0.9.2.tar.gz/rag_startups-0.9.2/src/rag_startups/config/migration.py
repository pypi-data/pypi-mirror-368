"""Configuration migration utilities for transitioning to new settings system."""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn


class ConfigurationMigrator:
    """Handle migration from old configuration system to new enhanced system."""

    def __init__(self, console: Optional[Console] = None):
        """Initialize migrator with optional console for output."""
        self.console = console or Console()
        self.project_root = Path(__file__).parent.parent.parent.parent

    def detect_old_config(self) -> Dict[str, any]:
        """Detect and extract values from old config.py file.

        Returns:
            Dictionary of detected configuration values
        """
        old_config = {}
        old_config_path = self.project_root / "config" / "config.py"

        if not old_config_path.exists():
            return old_config

        try:
            # Read old config file
            config_content = old_config_path.read_text()

            # Extract common configuration patterns
            patterns = {
                "DEFAULT_EMBEDDING_MODEL": r'DEFAULT_EMBEDDING_MODEL\s*=\s*["\']([^"\']+)["\']',
                "LOCAL_LANGUAGE_MODEL": r'LOCAL_LANGUAGE_MODEL\s*=\s*["\']([^"\']+)["\']',
                "CHUNK_SIZE": r"CHUNK_SIZE\s*=\s*(\d+)",
                "CHUNK_OVERLAP": r"CHUNK_OVERLAP\s*=\s*(\d+)",
                "DEFAULT_RETRIEVER_TOP_K": r"DEFAULT_RETRIEVER_TOP_K\s*=\s*(\d+)",
                "DEFAULT_SEARCH_TYPE": r'DEFAULT_SEARCH_TYPE\s*=\s*["\']([^"\']+)["\']',
                "MAX_LINES": r"MAX_LINES\s*=\s*(\d+)",
            }

            import re

            for key, pattern in patterns.items():
                match = re.search(pattern, config_content)
                if match:
                    value = match.group(1)
                    # Convert numeric values
                    if key in [
                        "CHUNK_SIZE",
                        "CHUNK_OVERLAP",
                        "DEFAULT_RETRIEVER_TOP_K",
                        "MAX_LINES",
                    ]:
                        value = int(value)
                    old_config[key] = value

            self.console.print(
                f"[green]✓[/green] Detected old configuration in {old_config_path}"
            )

        except Exception as e:
            self.console.print(
                f"[yellow]Warning:[/yellow] Could not read old config: {e}"
            )

        return old_config

    def generate_migration_env(self, old_config: Dict[str, any]) -> Path:
        """Generate .env file based on old configuration.

        Args:
            old_config: Dictionary of old configuration values

        Returns:
            Path to generated .env file
        """
        env_path = self.project_root / ".env.migration"

        # Map old config keys to new environment variables
        mapping = {
            "DEFAULT_EMBEDDING_MODEL": "RAG_EMBEDDING_MODEL",
            "LOCAL_LANGUAGE_MODEL": "RAG_LANGUAGE_MODEL",
            "CHUNK_SIZE": "RAG_CHUNK_SIZE",
            "CHUNK_OVERLAP": "RAG_CHUNK_OVERLAP",
            "DEFAULT_RETRIEVER_TOP_K": "RAG_RETRIEVER_TOP_K",
            "DEFAULT_SEARCH_TYPE": "RAG_SEARCH_TYPE",
            "MAX_LINES": "RAG_MAX_LINES",
        }

        env_content = ["# Migrated configuration from old config.py"]
        env_content.append("# Review and customize these values as needed")
        env_content.append("")

        # Add required token placeholder
        env_content.append("# REQUIRED: Set your HuggingFace token")
        current_token = os.getenv("HUGGINGFACE_TOKEN", "your-token-here")
        env_content.append(f"HUGGINGFACE_TOKEN={current_token}")
        env_content.append("")

        # Add migrated values
        env_content.append("# Migrated from old configuration")
        for old_key, new_key in mapping.items():
            if old_key in old_config:
                value = old_config[old_key]
                env_content.append(f"{new_key}={value}")

        # Add recommended new settings
        env_content.extend(
            [
                "",
                "# Recommended new settings",
                "RAG_ENVIRONMENT=development",
                "RAG_LOG_LEVEL=INFO",
                "RAG_ENABLE_CACHING=true",
                "RAG_CACHE_TTL=3600",
            ]
        )

        env_path.write_text("\n".join(env_content))
        return env_path

    def backup_old_config(self) -> Optional[Path]:
        """Create backup of old configuration files.

        Returns:
            Path to backup directory if created, None otherwise
        """
        old_config_path = self.project_root / "config" / "config.py"

        if not old_config_path.exists():
            return None

        backup_dir = self.project_root / ".config_backup"
        backup_dir.mkdir(exist_ok=True)

        # Copy old config file
        backup_file = (
            backup_dir / f"config_backup_{old_config_path.stat().st_mtime:.0f}.py"
        )
        shutil.copy2(old_config_path, backup_file)

        self.console.print(f"[green]✓[/green] Backed up old config to {backup_file}")
        return backup_dir

    def update_imports(self) -> List[Tuple[Path, int]]:
        """Update import statements in source files to use new config system.

        Returns:
            List of (file_path, changes_count) tuples
        """
        updated_files = []
        src_dir = self.project_root / "src" / "rag_startups"

        # Import patterns to replace
        old_patterns = [
            (
                r"from config\.config import",
                "from src.rag_startups.config.settings import get_settings",
            ),
            (
                r"from \.\.config\.config import",
                "from .config.settings import get_settings",
            ),
            (
                r"import config\.config",
                "from src.rag_startups.config.settings import get_settings",
            ),
        ]

        # Variable patterns to replace
        variable_patterns = [
            (r"DEFAULT_EMBEDDING_MODEL", "get_settings().embedding_model"),
            (r"LOCAL_LANGUAGE_MODEL", "get_settings().language_model"),
            (r"CHUNK_SIZE", "get_settings().chunk_size"),
            (r"CHUNK_OVERLAP", "get_settings().chunk_overlap"),
            (r"DEFAULT_RETRIEVER_TOP_K", "get_settings().retriever_top_k"),
            (r"DEFAULT_SEARCH_TYPE", "get_settings().search_type"),
            (r"MAX_LINES", "get_settings().max_lines"),
        ]

        import re

        for py_file in src_dir.rglob("*.py"):
            if py_file.name in ["settings.py", "migration.py", "validator.py"]:
                continue  # Skip our new config files

            try:
                content = py_file.read_text()
                changes = 0

                # Replace import patterns
                for old_pattern, new_import in old_patterns:
                    new_content, count = re.subn(old_pattern, new_import, content)
                    if count > 0:
                        content = new_content
                        changes += count

                # Replace variable patterns (only if imports were updated)
                if changes > 0:
                    for old_var, new_var in variable_patterns:
                        new_content, count = re.subn(
                            rf"\b{old_var}\b", new_var, content
                        )
                        if count > 0:
                            content = new_content
                            changes += count

                if changes > 0:
                    py_file.write_text(content)
                    updated_files.append((py_file, changes))
                    self.console.print(
                        f"[green]✓[/green] Updated {py_file.relative_to(self.project_root)} ({changes} changes)"
                    )

            except Exception as e:
                self.console.print(
                    f"[yellow]Warning:[/yellow] Could not update {py_file}: {e}"
                )

        return updated_files

    def run_migration(self, dry_run: bool = False) -> bool:
        """Run complete migration process.

        Args:
            dry_run: If True, show what would be done without making changes

        Returns:
            True if migration completed successfully
        """
        self.console.print(Panel("RAG Configuration Migration", style="bold blue"))

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
            ) as progress:

                # Step 1: Detect old configuration
                task1 = progress.add_task("Detecting old configuration...", total=None)
                old_config = self.detect_old_config()
                progress.update(task1, description="✓ Old configuration detected")

                if not old_config:
                    self.console.print(
                        "[yellow]No old configuration found to migrate[/yellow]"
                    )
                    return True

                # Step 2: Backup old files
                if not dry_run:
                    task2 = progress.add_task(
                        "Backing up old configuration...", total=None
                    )
                    self.backup_old_config()
                    progress.update(task2, description="✓ Old configuration backed up")

                # Step 3: Generate migration .env file
                task3 = progress.add_task(
                    "Generating migration .env file...", total=None
                )
                if not dry_run:
                    env_path = self.generate_migration_env(old_config)
                    progress.update(
                        task3,
                        description=f"✓ Migration .env generated: {env_path.name}",
                    )
                else:
                    progress.update(
                        task3, description="✓ Would generate migration .env file"
                    )

                # Step 4: Update imports (optional, can be risky)
                if not dry_run:
                    task4 = progress.add_task(
                        "Updating import statements...", total=None
                    )
                    updated_files = self.update_imports()
                    progress.update(
                        task4, description=f"✓ Updated {len(updated_files)} files"
                    )
                else:
                    progress.update(
                        task4, description="✓ Would update import statements"
                    )

            # Summary
            self.console.print("\n[green]Migration completed successfully![/green]")

            if not dry_run:
                self.console.print("\n[yellow]Next steps:[/yellow]")
                self.console.print("1. Review the generated .env.migration file")
                self.console.print("2. Copy it to .env and customize as needed")
                self.console.print("3. Test the application with new configuration")
                self.console.print("4. Run configuration health check")

            return True

        except Exception as e:
            self.console.print(f"[red]Migration failed: {e}[/red]")
            return False

    def rollback_migration(self) -> bool:
        """Rollback migration changes.

        Returns:
            True if rollback completed successfully
        """
        self.console.print(Panel("Rolling Back Migration", style="bold yellow"))

        try:
            backup_dir = self.project_root / ".config_backup"

            if not backup_dir.exists():
                self.console.print("[yellow]No backup found to rollback[/yellow]")
                return False

            # Find most recent backup
            backup_files = list(backup_dir.glob("config_backup_*.py"))
            if not backup_files:
                self.console.print("[yellow]No config backup files found[/yellow]")
                return False

            latest_backup = max(backup_files, key=lambda f: f.stat().st_mtime)

            # Restore old config
            old_config_path = self.project_root / "config" / "config.py"
            old_config_path.parent.mkdir(exist_ok=True)
            shutil.copy2(latest_backup, old_config_path)

            self.console.print(
                f"[green]✓[/green] Restored config from {latest_backup.name}"
            )

            # Remove migration files
            migration_env = self.project_root / ".env.migration"
            if migration_env.exists():
                migration_env.unlink()
                self.console.print("[green]✓[/green] Removed migration .env file")

            self.console.print("[green]Rollback completed successfully![/green]")
            return True

        except Exception as e:
            self.console.print(f"[red]Rollback failed: {e}[/red]")
            return False


def main():
    """CLI entry point for configuration migration."""
    import argparse

    parser = argparse.ArgumentParser(description="RAG Configuration Migrator")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument(
        "--rollback", action="store_true", help="Rollback migration changes"
    )

    args = parser.parse_args()

    migrator = ConfigurationMigrator()

    if args.rollback:
        success = migrator.rollback_migration()
    else:
        success = migrator.run_migration(dry_run=args.dry_run)

    import sys

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
