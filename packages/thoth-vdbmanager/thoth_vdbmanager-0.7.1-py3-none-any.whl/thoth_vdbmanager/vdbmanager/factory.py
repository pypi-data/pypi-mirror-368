"""Factory for creating vector store instances."""

import logging
from typing import Any

from .core.base import VectorStoreInterface

logger = logging.getLogger(__name__)


class VectorStoreFactory:
    """Factory for creating vector store instances."""

    _adapters: dict[str, Any] = {}
    _initialized = False

    @classmethod
    def _initialize_adapters(cls):
        """Initialize available adapters based on installed dependencies."""
        if cls._initialized:
            return

        # Try to import and register each adapter
        # Phase 2: All supported databases enabled
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
        logger.info(f"Initialized vector store factory with adapters: {list(cls._adapters.keys())}")

    @classmethod
    def create(
        cls,
        backend: str,
        collection: str,
        **kwargs
    ) -> VectorStoreInterface:
        """Create a vector store instance.

        Args:
            backend: Backend type (qdrant, chroma, pgvector, milvus)
            collection: Collection/table/index name
            **kwargs: Backend-specific parameters

        Returns:
            Vector store instance

        Raises:
            ValueError: If backend is not supported
        """
        cls._initialize_adapters()

        if backend not in cls._adapters:
            available_backends = list(cls._adapters.keys())
            raise ValueError(
                f"Unsupported backend: {backend}. "
                f"Available backends: {available_backends}"
            )

        adapter_class = cls._adapters[backend]
        return adapter_class(collection=collection, **kwargs)

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> VectorStoreInterface:
        """Create vector store from configuration.
        
        Args:
            config: Configuration dictionary with 'backend' and 'params'
            
        Returns:
            Vector store instance
        """
        backend = config.get("backend")
        if not backend:
            raise ValueError("Configuration must include 'backend' key")

        params = config.get("params", {})
        return cls.create(backend, **params)

    @classmethod
    def list_backends(cls) -> list[str]:
        """List available backends."""
        cls._initialize_adapters()
        return list(cls._adapters.keys())

    @classmethod
    def get_backend_info(cls, backend: str) -> dict[str, Any]:
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

        # Get basic info from adapter
        return {
            "name": backend,
            "class": adapter_class.__name__,
            "module": adapter_class.__module__,
        }
