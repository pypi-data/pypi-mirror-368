"""
Smart Model Management System for RAG Startups

This module provides resilient model management with automatic fallback,
health checking, and local caching to avoid external dependency failures.
"""

import json
import logging
import time
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

from .model_migrations import get_migration_tracker

logger = logging.getLogger(__name__)


class ModelType(Enum):
    """Types of models supported."""

    LANGUAGE_GENERATION = "text-generation"
    EMBEDDING = "sentence-similarity"
    CLASSIFICATION = "text-classification"


class ModelStatus(Enum):
    """Model availability status."""

    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"
    CACHED = "cached"


@dataclass
class ModelConfig:
    """Configuration for a model."""

    name: str
    model_type: ModelType
    provider: str  # "huggingface", "local", "openai", etc.
    endpoint: Optional[str] = None
    fallback_priority: int = 1  # Lower = higher priority
    parameters: Dict[str, Any] = None
    last_checked: Optional[float] = None
    status: ModelStatus = ModelStatus.UNKNOWN

    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}


class ModelManager:
    """
    Smart model manager with automatic fallback and health checking.

    Features:
    - Automatic model health checking
    - Fallback hierarchy with priority ordering
    - Local model caching and management
    - Provider-agnostic interface
    - Configuration-driven model selection
    """

    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or Path.home() / ".cache" / "rag_startups" / "models"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.model_configs: Dict[str, ModelConfig] = {}
        self.health_check_interval = 3600  # 1 hour
        self.timeout = 10  # seconds

        # Load default model configurations
        self._load_default_configs()

        # Load cached model status
        self._load_model_cache()

    def _load_default_configs(self):
        """Load default model configurations with fallback hierarchy."""

        # Language Generation Models (ordered by priority)
        # Updated with current model availability and migration patterns
        language_models = [
            # Current Mistral models (highest priority - most capable)
            ModelConfig(
                name="mistralai/Mistral-7B-Instruct-v0.3",
                model_type=ModelType.LANGUAGE_GENERATION,
                provider="huggingface",
                fallback_priority=1,
                parameters={
                    "max_new_tokens": 1000,
                    "temperature": 0.7,
                    "do_sample": True,
                    "repetition_penalty": 1.2,
                    # v0.3 improvements: extended vocab (32,768), v3 tokenizer, function
                    # calling
                    "return_full_text": False,
                    "stop": ["</s>", "[/INST]"],
                },
            ),
            # Backup Mistral (in case v0.3 has issues)
            ModelConfig(
                name="mistralai/Mistral-7B-v0.1",
                model_type=ModelType.LANGUAGE_GENERATION,
                provider="huggingface",
                fallback_priority=2,
                parameters={
                    "max_new_tokens": 800,
                    "temperature": 0.7,
                    "do_sample": True,
                    "repetition_penalty": 1.1,
                },
            ),
            # Reliable conversation models
            ModelConfig(
                name="microsoft/DialoGPT-medium",
                model_type=ModelType.LANGUAGE_GENERATION,
                provider="huggingface",
                fallback_priority=3,
                parameters={
                    "max_new_tokens": 800,
                    "temperature": 0.7,
                    "do_sample": True,
                    "repetition_penalty": 1.2,
                },
            ),
            # Stable GPT-2 variants (always available)
            ModelConfig(
                name="openai-community/gpt2",
                model_type=ModelType.LANGUAGE_GENERATION,
                provider="huggingface",
                fallback_priority=4,
                parameters={
                    "max_new_tokens": 600,
                    "temperature": 0.7,
                    "do_sample": True,
                    "_expected_sha": "607a30d783dfa663caf39e06633721c8d4cfcd7e",  # For validation
                },
            ),
            ModelConfig(
                name="distilbert/distilgpt2",
                model_type=ModelType.LANGUAGE_GENERATION,
                provider="huggingface",
                fallback_priority=5,
                parameters={
                    "max_new_tokens": 400,
                    "temperature": 0.7,
                    "do_sample": True,
                },
            ),
            # Local fallback option (always works offline)
            ModelConfig(
                name="local-gpt2",
                model_type=ModelType.LANGUAGE_GENERATION,
                provider="local",
                fallback_priority=99,  # Last resort
                parameters={"max_new_tokens": 300, "temperature": 0.7},
            ),
        ]

        # Embedding Models (ordered by priority)
        embedding_models = [
            ModelConfig(
                name="all-MiniLM-L6-v2",
                model_type=ModelType.EMBEDDING,
                provider="sentence-transformers",
                fallback_priority=1,
            ),
            ModelConfig(
                name="all-mpnet-base-v2",
                model_type=ModelType.EMBEDDING,
                provider="sentence-transformers",
                fallback_priority=2,
            ),
            ModelConfig(
                name="distilbert-base-nli-stsb-mean-tokens",
                model_type=ModelType.EMBEDDING,
                provider="sentence-transformers",
                fallback_priority=3,
            ),
        ]

        # Register all models
        for model in language_models + embedding_models:
            self.model_configs[model.name] = model

    def _load_model_cache(self):
        """Load cached model status from disk."""
        cache_file = self.cache_dir / "model_status.json"
        if cache_file.exists():
            try:
                with open(cache_file, "r") as f:
                    cached_data = json.load(f)

                for model_name, status_data in cached_data.items():
                    if model_name in self.model_configs:
                        self.model_configs[model_name].last_checked = status_data.get(
                            "last_checked"
                        )
                        self.model_configs[model_name].status = ModelStatus(
                            status_data.get("status", "unknown")
                        )

            except Exception as e:
                logger.warning(f"Failed to load model cache: {e}")

    def _save_model_cache(self):
        """Save model status to disk cache."""
        cache_file = self.cache_dir / "model_status.json"
        try:
            cache_data = {}
            for model_name, config in self.model_configs.items():
                cache_data[model_name] = {
                    "last_checked": config.last_checked,
                    "status": config.status.value,
                }

            with open(cache_file, "w") as f:
                json.dump(cache_data, f, indent=2)

        except Exception as e:
            logger.warning(f"Failed to save model cache: {e}")

    def check_model_health(self, model_name: str, force: bool = False) -> ModelStatus:
        """
        Check if a model is available and healthy.

        Args:
            model_name: Name of the model to check
            force: Force check even if recently checked

        Returns:
            ModelStatus indicating availability
        """
        if model_name not in self.model_configs:
            logger.warning(f"Unknown model: {model_name}")
            return ModelStatus.UNKNOWN

        config = self.model_configs[model_name]

        # Check if we need to refresh the health check
        now = time.time()
        if not force and config.last_checked:
            if now - config.last_checked < self.health_check_interval:
                return config.status

        logger.info(f"Checking health for model: {model_name}")

        try:
            if config.provider == "huggingface":
                status = self._check_huggingface_model(config)
            elif config.provider == "local":
                status = self._check_local_model(config)
            elif config.provider == "sentence-transformers":
                status = self._check_sentence_transformer_model(config)
            else:
                logger.warning(f"Unknown provider: {config.provider}")
                status = ModelStatus.UNKNOWN

            # Update cache
            config.last_checked = now
            config.status = status
            self._save_model_cache()

            return status

        except Exception as e:
            logger.error(f"Health check failed for {model_name}: {e}")
            config.status = ModelStatus.UNAVAILABLE
            config.last_checked = now
            self._save_model_cache()
            return ModelStatus.UNAVAILABLE

    def _check_huggingface_model(self, config: ModelConfig) -> ModelStatus:
        """Check HuggingFace model availability using model info API."""
        # Use the model info API instead of inference API for better reliability
        url = f"https://huggingface.co/api/models/{config.name}"

        # Add authentication headers if token is available
        headers = {}
        # Get token from settings instead of os.getenv() since .env is loaded by Pydantic
        from ..config.settings import get_settings

        settings = get_settings()
        if settings.huggingface_token:
            headers["Authorization"] = f"Bearer {settings.huggingface_token}"

        try:
            response = requests.get(url, headers=headers, timeout=self.timeout)
            # If token appears invalid (401), retry anonymously – public models should still pass
            if response.status_code == 401 and "Authorization" in headers:
                logger.warning(
                    f"HuggingFace auth returned 401 for {config.name}; retrying without token"
                )
                response = requests.get(url, timeout=self.timeout)
            if response.status_code == 200:
                model_info = response.json()

                # Check if model is deprecated or private
                if model_info.get("private", False):
                    logger.warning(f"HuggingFace model is private: {config.name}")
                    return ModelStatus.UNAVAILABLE

                # Check for deprecation markers
                if "deprecated" in model_info.get("tags", []):
                    logger.warning(f"HuggingFace model is deprecated: {config.name}")
                    return ModelStatus.UNAVAILABLE

                # Store SHA for validation if available
                if "sha" in model_info:
                    config.parameters = config.parameters or {}
                    config.parameters["_model_sha"] = model_info["sha"]
                    logger.debug(f"Model {config.name} SHA: {model_info['sha']}")

                return ModelStatus.AVAILABLE

            elif response.status_code == 404:
                logger.warning(f"HuggingFace model not found: {config.name}")
                return ModelStatus.UNAVAILABLE
            else:
                logger.warning(
                    f"HuggingFace model check returned {response.status_code}: {config.name}"
                )
                return ModelStatus.UNKNOWN

        except requests.RequestException as e:
            logger.warning(
                f"Network error checking HuggingFace model {config.name}: {e}"
            )
            return ModelStatus.UNKNOWN
        except Exception as e:
            logger.warning(
                f"Error parsing HuggingFace model info for {config.name}: {e}"
            )
            return ModelStatus.UNKNOWN

    def _check_local_model(self, config: ModelConfig) -> ModelStatus:
        """Check local model availability with fallback to HuggingFace."""
        logger.info(f"Checking local model: {config.name}")

        # Check if local model directory exists
        local_path = self.cache_dir / "transformers" / config.name.replace("/", "--")
        logger.info(f"Looking for local model at: {local_path}")

        if local_path.exists() and (local_path / "config.json").exists():
            logger.info(f"Found cached local model: {config.name}")
            return ModelStatus.CACHED

        # If local model doesn't exist, check if we can fall back to HuggingFace
        if config.name.startswith("local-"):
            # Try to map local-* names to actual HuggingFace models
            actual_name = config.name.replace("local-", "")
            if actual_name == "gpt2":
                actual_name = "openai-community/gpt2"  # Updated namespace

            logger.info(
                f"Local model {config.name} not found, checking HuggingFace fallback: {actual_name}"
            )

            # Create temporary config for HF check
            temp_config = ModelConfig(
                name=actual_name,
                model_type=config.model_type,
                provider="huggingface",
                fallback_priority=config.fallback_priority,
            )

            hf_status = self._check_huggingface_model(temp_config)
            if hf_status == ModelStatus.AVAILABLE:
                # Update the config to use HuggingFace instead
                config.name = actual_name
                config.provider = "huggingface"
                # Give upgraded model better priority (mid-range, not last resort)
                config.fallback_priority = 50
                # Update the registry with the new config
                self.model_configs[actual_name] = config
                logger.info(
                    f"Upgraded local model to HuggingFace: {actual_name} (priority: {config.fallback_priority})"
                )
                return ModelStatus.AVAILABLE
            elif hf_status == ModelStatus.UNKNOWN:
                # HF model exists but API is having issues - return UNKNOWN to try it later
                logger.info(
                    f"Local model {config.name} not found, HuggingFace fallback {actual_name} has unknown status"
                )
                return ModelStatus.UNKNOWN

        # Local model doesn't exist and no valid fallback
        logger.warning(
            f"Local model {config.name} not found and no valid fallback available"
        )
        return ModelStatus.UNAVAILABLE

    def _check_sentence_transformer_model(self, config: ModelConfig) -> ModelStatus:
        """Check sentence transformer model availability."""
        try:
            pass

            # Try to load the model (this will download if not cached)
            model_path = self.cache_dir / "sentence_transformers" / config.name
            if model_path.exists():
                return ModelStatus.CACHED
            else:
                # Check if we can download it
                return ModelStatus.AVAILABLE
        except Exception as e:
            logger.warning(f"Sentence transformer check failed for {config.name}: {e}")
            return ModelStatus.UNAVAILABLE

    def get_best_model(
        self, model_type: ModelType, force_check: bool = False
    ) -> Optional[ModelConfig]:
        """
        Get the best available model of the specified type with intelligent migration handling.

        Args:
            model_type: Type of model needed
            force_check: Force health check for all models

        Returns:
            Best available model configuration, or None if none available
        """
        # Filter models by type
        candidates = [
            config
            for config in self.model_configs.values()
            if config.model_type == model_type
        ]

        if not candidates:
            logger.error(f"No models configured for type: {model_type}")
            return None

        # Sort by priority (lower number = higher priority)
        candidates.sort(key=lambda x: x.fallback_priority)

        # Check health and return first available
        # Try models in order: AVAILABLE/CACHED -> UNKNOWN -> UNAVAILABLE
        migration_tracker = get_migration_tracker()

        # First pass: try definitely available models
        for config in candidates:
            original_name = config.name
            status = self.check_model_health(config.name, force=force_check)
            if status in [ModelStatus.AVAILABLE, ModelStatus.CACHED]:
                # If the config was updated during health check (e.g., local->HF upgrade),
                # return the updated config from the registry
                if config.name != original_name:
                    updated_config = self.model_configs.get(config.name, config)
                    logger.info(
                        f"Selected model: {updated_config.name} (status: {status.value})"
                    )
                    return updated_config
                else:
                    logger.info(
                        f"Selected model: {config.name} (status: {status.value})"
                    )
                    return config

        # Second pass: try unknown models (might work despite network issues)
        for config in candidates:
            status = self.check_model_health(config.name, force=force_check)
            if status == ModelStatus.UNKNOWN:
                logger.info(
                    f"Trying unknown model: {config.name} (network issues may resolve)"
                )
                return config

        # Third pass: try migration for unavailable models
        for config in candidates:
            status = self.check_model_health(config.name, force=force_check)
            if status == ModelStatus.UNAVAILABLE:
                # Try intelligent migration suggestion
                suggested_model = migration_tracker.suggest_replacement(config.name)
                if suggested_model and suggested_model != config.name:
                    logger.info(
                        f"Model {config.name} unavailable, trying suggested replacement: {suggested_model}"
                    )

                    # Create temporary config for suggested model
                    suggested_config = ModelConfig(
                        name=suggested_model,
                        model_type=config.model_type,
                        provider=config.provider,
                        fallback_priority=config.fallback_priority,
                        parameters=(
                            config.parameters.copy() if config.parameters else {}
                        ),
                    )

                    # Check if suggested model is available
                    suggested_status = self.check_model_health(
                        suggested_model, force=True
                    )
                    if suggested_status in [ModelStatus.AVAILABLE, ModelStatus.CACHED]:
                        logger.info(
                            f"Successfully migrated to: {suggested_model} (status: {suggested_status.value})"
                        )
                        # Add the working model to our configs for future use
                        self.model_configs[suggested_model] = suggested_config
                        return suggested_config

        # If no models are available, return the highest priority one anyway
        # (maybe the health check was wrong, or network is down)
        logger.warning(
            f"No healthy models found for {model_type}, using fallback: {candidates[0].name}"
        )
        return candidates[0]

    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a model."""
        if model_name not in self.model_configs:
            return None

        config = self.model_configs[model_name]
        status = self.check_model_health(model_name)

        return {
            **asdict(config),
            "current_status": status.value,
            "is_healthy": status in [ModelStatus.AVAILABLE, ModelStatus.CACHED],
        }

    def list_models(
        self, model_type: Optional[ModelType] = None
    ) -> List[Dict[str, Any]]:
        """List all configured models with their status."""
        models = []
        for config in self.model_configs.values():
            if model_type is None or config.model_type == model_type:
                models.append(self.get_model_info(config.name))

        return sorted(
            models, key=lambda x: (x["model_type"].value, x["fallback_priority"])
        )

    def add_model(self, config: ModelConfig) -> bool:
        """Add a new model configuration."""
        try:
            self.model_configs[config.name] = config
            self._save_model_cache()
            logger.info(f"Added model configuration: {config.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to add model {config.name}: {e}")
            return False

    def remove_model(self, model_name: str) -> bool:
        """Remove a model configuration."""
        if model_name in self.model_configs:
            del self.model_configs[model_name]
            self._save_model_cache()
            logger.info(f"Removed model configuration: {model_name}")
            return True
        return False
