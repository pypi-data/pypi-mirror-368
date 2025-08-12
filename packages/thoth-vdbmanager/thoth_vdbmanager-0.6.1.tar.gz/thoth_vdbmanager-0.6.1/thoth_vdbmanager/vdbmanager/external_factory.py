# Copyright (c) 2025 Marco Pancotti
# This file is part of Thoth and is released under the MIT License.
# See the LICENSE.md file in the project root for full license information.

"""External embedding factory for thoth-vdbmanager v0.6.0."""

import logging
import os
from typing import Any, Dict, Optional

from .core.base import VectorStoreInterface
from .core.external_embedding_manager import ExternalEmbeddingManager
from .core.embedding_provider import EmbeddingProviderFactory

logger = logging.getLogger(__name__)


class ExternalVectorStoreFactory:
    """Factory for creating vector store instances with external embedding providers."""

    _adapters: Dict[str, Any] = {}
    _initialized = False

    @classmethod
    def _initialize_adapters(cls):
        """Initialize available adapters based on installed dependencies."""
        if cls._initialized:
            return

        # Try to import and register each adapter with external embedding support
        adapters_to_try = [
            ("qdrant", "qdrant_adapter", "QdrantAdapter"),
            ("chroma", "chroma_adapter", "ChromaAdapter"),
            ("pgvector", "pgvector_adapter", "PgvectorAdapter"),
            ("milvus", "milvus_adapter", "MilvusAdapter"),
        ]

        for backend_name, module_name, class_name in adapters_to_try:
            try:
                # Use importlib for cleaner dynamic imports
                import importlib
                module = importlib.import_module(f".adapters.{module_name}", package=__package__)
                adapter_class = getattr(module, class_name)
                cls._adapters[backend_name] = adapter_class
                logger.info(f"Registered {backend_name} adapter")
            except ImportError as e:
                logger.warning(f"Could not import {backend_name} adapter: {e}")
            except Exception as e:
                logger.error(f"Error registering {backend_name} adapter: {e}")

        cls._initialized = True
        logger.info(f"Initialized external vector store factory with adapters: {list(cls._adapters.keys())}")

    @classmethod
    def create(
        cls,
        backend: str,
        embedding_config: Dict[str, Any],
        collection: str,
        **kwargs
    ) -> VectorStoreInterface:
        """Create a vector store instance with external embeddings.

        Args:
            backend: Backend type (qdrant, chroma, pgvector, milvus)
            embedding_config: External embedding configuration:
                {
                    'provider': 'openai',  # openai, cohere, mistral, huggingface
                    'api_key': 'your-api-key',
                    'model': 'text-embedding-3-small',
                    'enable_cache': True,
                    'cache_size': 10000
                }
            collection: Collection/table/index name
            **kwargs: Backend-specific parameters

        Returns:
            Vector store instance with external embeddings

        Raises:
            ValueError: If backend is not supported
            ConnectionError: If embedding provider connection fails
        """
        cls._initialize_adapters()

        if backend not in cls._adapters:
            available_backends = list(cls._adapters.keys())
            raise ValueError(
                f"Unsupported backend: {backend}. "
                f"Available backends: {available_backends}"
            )

        if not embedding_config:
            raise ValueError("Embedding configuration is required")

        # Create external embedding manager
        try:
            embedding_manager = ExternalEmbeddingManager.from_config(embedding_config)
        except Exception as e:
            raise ConnectionError(f"Failed to create embedding manager: {e}")

        # Get adapter class and create instance
        adapter_class = cls._adapters[backend]
        
        # Check if adapter supports external embeddings
        if hasattr(adapter_class, '_supports_external_embeddings'):
            # Use external embedding adapter
            return adapter_class(
                collection=collection,
                embedding_manager=embedding_manager,
                **kwargs
            )
        else:
            # Use legacy adapter with external embedding manager
            # This is a compatibility layer for existing adapters
            instance = adapter_class(collection=collection, **kwargs)
            
            # Replace the embedding manager if possible
            if hasattr(instance, 'embedding_manager'):
                instance.embedding_manager = embedding_manager
                logger.info(f"Replaced embedding manager in {backend} adapter with external provider")
            else:
                logger.warning(f"Adapter {backend} does not support external embedding manager replacement")
            
            return instance

    @classmethod
    def create_from_env(
        cls,
        backend: str,
        collection: str,
        **kwargs
    ) -> VectorStoreInterface:
        """Create vector store from environment variables.

        Expected environment variables:
        - EMBEDDING_PROVIDER: openai, cohere, mistral, huggingface
        - EMBEDDING_MODEL: model name
        - EMBEDDING_API_KEY: API key
        - EMBEDDING_CACHE_SIZE: cache size (optional)

        Args:
            backend: Backend type
            collection: Collection name
            **kwargs: Backend-specific parameters

        Returns:
            Vector store instance
        """
        # Create embedding config from environment
        embedding_config = cls._get_embedding_config_from_env()
        
        return cls.create(
            backend=backend,
            embedding_config=embedding_config,
            collection=collection,
            **kwargs
        )

    @classmethod
    def _get_embedding_config_from_env(cls) -> Dict[str, Any]:
        """Get embedding configuration from environment variables."""
        provider = os.environ.get('EMBEDDING_PROVIDER')
        if not provider:
            raise ValueError("EMBEDDING_PROVIDER environment variable is required")

        api_key = os.environ.get('EMBEDDING_API_KEY')
        if not api_key:
            raise ValueError("EMBEDDING_API_KEY environment variable is required")

        model = os.environ.get('EMBEDDING_MODEL', cls._get_default_model(provider))
        cache_size = int(os.environ.get('EMBEDDING_CACHE_SIZE', '10000'))
        enable_cache = os.environ.get('EMBEDDING_ENABLE_CACHE', 'true').lower() == 'true'

        return {
            'provider': provider,
            'api_key': api_key,
            'model': model,
            'enable_cache': enable_cache,
            'cache_size': cache_size
        }

    @staticmethod
    def _get_default_model(provider: str) -> str:
        """Get default model for provider."""
        defaults = {
            'openai': 'text-embedding-3-small',
            'cohere': 'embed-multilingual-v3.0',
            'mistral': 'mistral-embed',
            'huggingface': 'sentence-transformers/all-MiniLM-L6-v2'
        }
        return defaults.get(provider, 'default')

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> VectorStoreInterface:
        """Create vector store from configuration dictionary.
        
        Args:
            config: Configuration dictionary:
                {
                    'backend': 'qdrant',
                    'collection': 'my_collection',
                    'embedding': {
                        'provider': 'openai',
                        'api_key': 'sk-...',
                        'model': 'text-embedding-3-small'
                    },
                    'params': {
                        # backend-specific parameters
                    }
                }
            
        Returns:
            Vector store instance
        """
        backend = config.get("backend")
        if not backend:
            raise ValueError("Configuration must include 'backend' key")

        collection = config.get("collection")
        if not collection:
            raise ValueError("Configuration must include 'collection' key")

        embedding_config = config.get("embedding")
        if not embedding_config:
            raise ValueError("Configuration must include 'embedding' key")

        params = config.get("params", {})
        
        return cls.create(
            backend=backend,
            embedding_config=embedding_config,
            collection=collection,
            **params
        )

    @classmethod
    def list_backends(cls) -> list[str]:
        """List available backends."""
        cls._initialize_adapters()
        return list(cls._adapters.keys())

    @classmethod
    def get_supported_providers(cls) -> list[str]:
        """Get list of supported embedding providers."""
        return EmbeddingProviderFactory.get_supported_providers()

    @classmethod
    def validate_provider_config(cls, provider: str, api_key: str, model: str = None) -> bool:
        """Validate embedding provider configuration.
        
        Args:
            provider: Provider name
            api_key: API key
            model: Model name (optional, uses default if None)
            
        Returns:
            True if configuration is valid
        """
        try:
            if not model:
                model = cls._get_default_model(provider)
            
            # Create temporary provider to test connection
            embedding_provider = EmbeddingProviderFactory.create_provider(
                provider, api_key=api_key, model=model
            )
            return embedding_provider.validate_connection()
        except Exception as e:
            logger.error(f"Provider validation failed: {e}")
            return False

    @classmethod
    def get_backend_info(cls, backend: str) -> Dict[str, Any]:
        """Get information about a backend.
        
        Args:
            backend: Backend name
            
        Returns:
            Backend information
        """
        cls._initialize_adapters()

        if backend not in cls._adapters:
            raise ValueError(f"Unsupported backend: {backend}")

        adapter_class = cls._adapters[backend]

        return {
            "name": backend,
            "class": adapter_class.__name__,
            "module": adapter_class.__module__,
            "supports_external_embeddings": hasattr(adapter_class, '_supports_external_embeddings'),
        }