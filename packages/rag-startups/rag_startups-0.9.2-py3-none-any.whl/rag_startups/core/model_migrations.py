"""
Model Migration Intelligence System

This module tracks known model migrations, deprecations, and provides
intelligent fallback suggestions based on real-world model lifecycle patterns.
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class MigrationReason(Enum):
    """Reasons for model migration."""

    DEPRECATED = "deprecated"
    REPLACED = "replaced"
    LOW_USAGE = "low_usage"
    PERFORMANCE_UPGRADE = "performance_upgrade"
    SECURITY_UPDATE = "security_update"
    PROVIDER_CHANGE = "provider_change"


@dataclass
class ModelMigration:
    """Information about a model migration."""

    old_model: str
    new_model: str
    reason: MigrationReason
    migration_date: Optional[str] = None
    notes: Optional[str] = None
    automatic_redirect: bool = False
    compatibility_notes: Optional[str] = None


class ModelMigrationTracker:
    """
    Tracks known model migrations and provides intelligent suggestions.

    This system learns from real-world model lifecycle patterns to provide
    better fallback strategies and proactive migration recommendations.
    """

    def __init__(self):
        self.migrations: Dict[str, ModelMigration] = {}
        self._load_known_migrations()

    def _load_known_migrations(self):
        """Load known model migrations from real-world observations."""

        # Mistral model migrations (based on user's discovery)
        self.add_migration(
            ModelMigration(
                old_model="mistralai/Mistral-7B-Instruct-v0.2",
                new_model="mistralai/Mistral-7B-Instruct-v0.3",
                reason=MigrationReason.PERFORMANCE_UPGRADE,
                migration_date="2024-Q2",
                notes="v0.3 includes extended vocabulary (32,768 tokens), v3 tokenizer, and function-calling capabilities",
                automatic_redirect=True,
                compatibility_notes="Requests to v0.2 are automatically redirected to v0.3 by some providers",
            )
        )

        # GPT model evolution patterns
        self.add_migration(
            ModelMigration(
                old_model="gpt-3.5-turbo-0301",
                new_model="gpt-3.5-turbo",
                reason=MigrationReason.DEPRECATED,
                notes="Older snapshot versions are deprecated in favor of rolling updates",
            )
        )

        # Common HuggingFace model patterns
        self.add_migration(
            ModelMigration(
                old_model="bert-base-uncased-deprecated",
                new_model="bert-base-uncased",
                reason=MigrationReason.REPLACED,
                notes="Repository restructuring and model updates",
            )
        )

        # Sentence transformer migrations
        self.add_migration(
            ModelMigration(
                old_model="distilbert-base-nli-stsb-mean-tokens",
                new_model="all-MiniLM-L6-v2",
                reason=MigrationReason.PERFORMANCE_UPGRADE,
                notes="Newer model with better performance and smaller size",
            )
        )

        logger.info(f"Loaded {len(self.migrations)} known model migrations")

    def add_migration(self, migration: ModelMigration):
        """Add a model migration to the tracker."""
        self.migrations[migration.old_model] = migration
        logger.debug(f"Added migration: {migration.old_model} -> {migration.new_model}")

    def get_migration(self, old_model: str) -> Optional[ModelMigration]:
        """Get migration information for a model."""
        return self.migrations.get(old_model)

    def suggest_replacement(self, unavailable_model: str) -> Optional[str]:
        """
        Suggest a replacement for an unavailable model.

        Args:
            unavailable_model: Name of the unavailable model

        Returns:
            Suggested replacement model name, or None if no suggestion available
        """
        # Direct migration mapping
        migration = self.get_migration(unavailable_model)
        if migration:
            logger.info(
                f"Found direct migration: {unavailable_model} -> {migration.new_model}"
            )
            return migration.new_model

        # Pattern-based suggestions
        suggestion = self._suggest_by_pattern(unavailable_model)
        if suggestion:
            logger.info(
                f"Pattern-based suggestion: {unavailable_model} -> {suggestion}"
            )
            return suggestion

        return None

    def _suggest_by_pattern(self, model_name: str) -> Optional[str]:
        """Suggest replacement based on naming patterns."""

        # Mistral version pattern
        if "mistralai/Mistral-7B-Instruct-v0." in model_name:
            # Always suggest the latest known version
            return "mistralai/Mistral-7B-Instruct-v0.3"

        # GPT-2 variants
        if model_name.startswith("gpt2") and "distil" not in model_name:
            return "gpt2"  # Base model is most stable

        # BERT variants
        if "bert-base" in model_name.lower():
            return "bert-base-uncased"

        # Sentence transformer patterns
        if "sentence-transformers/" in model_name or "all-" in model_name:
            return "all-MiniLM-L6-v2"  # Most reliable sentence transformer

        return None

    def get_migration_history(self, model_name: str) -> List[ModelMigration]:
        """Get the full migration history for a model."""
        history = []
        current = model_name

        # Trace backwards through migrations
        for migration in self.migrations.values():
            if migration.new_model == current:
                history.insert(0, migration)
                current = migration.old_model

        return history

    def is_model_deprecated(self, model_name: str) -> bool:
        """Check if a model is known to be deprecated."""
        return model_name in self.migrations

    def get_deprecation_info(self, model_name: str) -> Optional[Dict[str, str]]:
        """Get deprecation information for a model."""
        migration = self.get_migration(model_name)
        if migration:
            return {
                "deprecated": True,
                "replacement": migration.new_model,
                "reason": migration.reason.value,
                "notes": migration.notes or "",
                "automatic_redirect": migration.automatic_redirect,
            }
        return None

    def suggest_proactive_migrations(
        self, current_models: List[str]
    ) -> List[Tuple[str, str, str]]:
        """
        Suggest proactive migrations for current models.

        Args:
            current_models: List of currently used model names

        Returns:
            List of (old_model, new_model, reason) tuples for suggested migrations
        """
        suggestions = []

        for model in current_models:
            migration = self.get_migration(model)
            if migration:
                suggestions.append(
                    (
                        model,
                        migration.new_model,
                        f"{migration.reason.value}: {migration.notes or 'No additional notes'}",
                    )
                )

        return suggestions

    def export_migrations(self) -> Dict[str, Dict]:
        """Export migration data for external use."""
        export_data = {}
        for old_model, migration in self.migrations.items():
            export_data[old_model] = {
                "new_model": migration.new_model,
                "reason": migration.reason.value,
                "migration_date": migration.migration_date,
                "notes": migration.notes,
                "automatic_redirect": migration.automatic_redirect,
                "compatibility_notes": migration.compatibility_notes,
            }
        return export_data

    def import_migrations(self, migration_data: Dict[str, Dict]):
        """Import migration data from external source."""
        for old_model, data in migration_data.items():
            migration = ModelMigration(
                old_model=old_model,
                new_model=data["new_model"],
                reason=MigrationReason(data["reason"]),
                migration_date=data.get("migration_date"),
                notes=data.get("notes"),
                automatic_redirect=data.get("automatic_redirect", False),
                compatibility_notes=data.get("compatibility_notes"),
            )
            self.add_migration(migration)

        logger.info(f"Imported {len(migration_data)} migrations")


# Global migration tracker instance
_migration_tracker = None


def get_migration_tracker() -> ModelMigrationTracker:
    """Get the global migration tracker instance."""
    global _migration_tracker
    if _migration_tracker is None:
        _migration_tracker = ModelMigrationTracker()
    return _migration_tracker
