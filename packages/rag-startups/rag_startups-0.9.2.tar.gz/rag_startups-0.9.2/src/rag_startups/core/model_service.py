"""
Model Service Integration for RAG Startups

This module integrates the smart model manager with the RAG pipeline,
providing seamless model selection and fallback handling.
"""

import logging
from typing import Any, Dict, List, Optional

from ..config.settings import RAGSettings
from .model_manager import ModelConfig, ModelManager, ModelStatus, ModelType

logger = logging.getLogger(__name__)


class ModelService:
    """
    Service layer for model management in RAG pipeline.

    Provides high-level interface for model selection, health monitoring,
    and integration with the RAG system configuration.
    """

    def __init__(self, settings: RAGSettings):
        self.settings = settings
        self.model_manager = ModelManager(
            cache_dir=settings.project_root / ".cache" / "models"
        )

        # Configure model manager with settings
        self.model_manager.health_check_interval = settings.model_health_check_interval
        self.model_manager.timeout = settings.model_timeout

        self._current_language_model: Optional[ModelConfig] = None
        self._current_embedding_model: Optional[ModelConfig] = None

    def get_language_model(self, force_check: bool = False) -> ModelConfig:
        """
        Get the best available language model for text generation.

        Args:
            force_check: Force health check for all models

        Returns:
            ModelConfig for the best available language model
        """
        if not self.settings.enable_smart_model_selection:
            # Use configured default model
            return ModelConfig(
                name=self.settings.language_model,
                model_type=ModelType.LANGUAGE_GENERATION,
                provider="huggingface",
                fallback_priority=1,
                parameters={
                    "max_new_tokens": 1000,
                    "temperature": 0.7,
                    "do_sample": True,
                    "repetition_penalty": 1.2,
                },
            )

        # Use smart selection
        if self._current_language_model is None or force_check:
            self._current_language_model = self.model_manager.get_best_model(
                ModelType.LANGUAGE_GENERATION, force_check=force_check
            )

            if self._current_language_model is None:
                # Fallback to configured default
                logger.warning("No language models available, using configured default")
                self._current_language_model = ModelConfig(
                    name=self.settings.language_model,
                    model_type=ModelType.LANGUAGE_GENERATION,
                    provider="huggingface",
                    fallback_priority=999,
                    parameters={
                        "max_new_tokens": 800,
                        "temperature": 0.7,
                        "do_sample": True,
                    },
                )

        return self._current_language_model

    def get_embedding_model(self, force_check: bool = False) -> ModelConfig:
        """
        Get the best available embedding model.

        Args:
            force_check: Force health check for all models

        Returns:
            ModelConfig for the best available embedding model
        """
        if not self.settings.enable_smart_model_selection:
            # Use configured default model
            return ModelConfig(
                name=self.settings.embedding_model,
                model_type=ModelType.EMBEDDING,
                provider="sentence-transformers",
                fallback_priority=1,
            )

        # Use smart selection
        if self._current_embedding_model is None or force_check:
            self._current_embedding_model = self.model_manager.get_best_model(
                ModelType.EMBEDDING, force_check=force_check
            )

            if self._current_embedding_model is None:
                # Fallback to configured default
                logger.warning(
                    "No embedding models available, using configured default"
                )
                self._current_embedding_model = ModelConfig(
                    name=self.settings.embedding_model,
                    model_type=ModelType.EMBEDDING,
                    provider="sentence-transformers",
                    fallback_priority=999,
                )

        return self._current_embedding_model

    def check_model_health(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Check health of current models or a specific model.

        Args:
            model_name: Specific model to check, or None for current models

        Returns:
            Dictionary with health status information
        """
        if model_name:
            status = self.model_manager.check_model_health(model_name, force=True)
            return {
                "model": model_name,
                "status": status.value,
                "healthy": status in [ModelStatus.AVAILABLE, ModelStatus.CACHED],
            }

        # Check current models
        language_model = self.get_language_model()
        embedding_model = self.get_embedding_model()

        language_status = self.model_manager.check_model_health(
            language_model.name, force=True
        )
        embedding_status = self.model_manager.check_model_health(
            embedding_model.name, force=True
        )

        return {
            "language_model": {
                "name": language_model.name,
                "status": language_status.value,
                "healthy": language_status
                in [ModelStatus.AVAILABLE, ModelStatus.CACHED],
            },
            "embedding_model": {
                "name": embedding_model.name,
                "status": embedding_status.value,
                "healthy": embedding_status
                in [ModelStatus.AVAILABLE, ModelStatus.CACHED],
            },
            "overall_healthy": all(
                [
                    language_status in [ModelStatus.AVAILABLE, ModelStatus.CACHED],
                    embedding_status in [ModelStatus.AVAILABLE, ModelStatus.CACHED],
                ]
            ),
        }

    def list_available_models(
        self, model_type: Optional[ModelType] = None
    ) -> List[Dict[str, Any]]:
        """
        List all available models with their status.

        Args:
            model_type: Filter by model type, or None for all models

        Returns:
            List of model information dictionaries
        """
        return self.model_manager.list_models(model_type)

    def refresh_model_health(self) -> Dict[str, Any]:
        """
        Force refresh health status for all models.

        Returns:
            Summary of health check results
        """
        logger.info("Refreshing model health status...")

        # Force check current models
        self._current_language_model = None
        self._current_embedding_model = None

        # Get fresh models (this will trigger health checks)
        self.get_language_model(force_check=True)
        self.get_embedding_model(force_check=True)

        return self.check_model_health()

    def get_model_parameters(self, model_config: ModelConfig) -> Dict[str, Any]:
        """
        Get parameters for a model, merging defaults with model-specific settings.

        Args:
            model_config: Model configuration

        Returns:
            Dictionary of parameters for the model
        """
        base_params = model_config.parameters.copy() if model_config.parameters else {}

        # Add any global settings that should override model defaults
        if model_config.model_type == ModelType.LANGUAGE_GENERATION:
            # You can add global overrides here if needed
            pass

        return base_params

    def create_huggingface_client(self, model_config: ModelConfig):
        """
        Create a HuggingFace client for the given model.

        Args:
            model_config: Model configuration

        Returns:
            Configured HuggingFace client
        """
        try:
            from huggingface_hub import InferenceClient

            client = InferenceClient(
                model=model_config.name, token=self.settings.huggingface_token
            )

            logger.info(f"Created HuggingFace client for model: {model_config.name}")
            return client

        except Exception as e:
            logger.error(
                f"Failed to create HuggingFace client for {model_config.name}: {e}"
            )
            raise

    def create_sentence_transformer(self, model_config: ModelConfig):
        """
        Create a sentence transformer for the given model.

        Args:
            model_config: Model configuration

        Returns:
            Configured sentence transformer
        """
        try:
            from sentence_transformers import SentenceTransformer

            # Use cache directory for model storage
            cache_folder = str(self.model_manager.cache_dir / "sentence_transformers")

            model = SentenceTransformer(model_config.name, cache_folder=cache_folder)

            logger.info(f"Created SentenceTransformer for model: {model_config.name}")
            return model

        except Exception as e:
            logger.error(
                f"Failed to create SentenceTransformer for {model_config.name}: {e}"
            )
            raise

    def add_custom_model(
        self,
        name: str,
        model_type: ModelType,
        provider: str,
        priority: int = 50,
        **kwargs,
    ) -> bool:
        """
        Add a custom model configuration.

        Args:
            name: Model name
            model_type: Type of model
            provider: Model provider
            priority: Fallback priority (lower = higher priority)
            **kwargs: Additional model parameters

        Returns:
            True if successfully added
        """
        config = ModelConfig(
            name=name,
            model_type=model_type,
            provider=provider,
            fallback_priority=priority,
            parameters=kwargs,
        )

        return self.model_manager.add_model(config)
