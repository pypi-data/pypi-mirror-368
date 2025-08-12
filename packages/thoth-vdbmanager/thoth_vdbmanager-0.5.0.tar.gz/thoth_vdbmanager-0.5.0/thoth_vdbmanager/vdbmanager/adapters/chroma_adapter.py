"""Chroma adapter for Thoth Vector Database."""

import logging
from typing import Any

from haystack_integrations.document_stores.chroma import ChromaDocumentStore

from .haystack_adapter import HaystackVectorStoreAdapter

logger = logging.getLogger(__name__)


class ChromaAdapter(HaystackVectorStoreAdapter):
    """Chroma implementation using Haystack integration."""

    _instances: dict[str, "ChromaAdapter"] = {}

    def __new__(
        cls,
        collection: str,
        persist_path: str | None = None,
        **kwargs
    ):
        """Create new instance for each call to avoid readonly database issues."""
        # For testing purposes, always create new instances to avoid readonly database issues
        # In production, you might want to enable singleton pattern for performance
        instance = super().__new__(cls)

        # Still track instances for cleanup purposes
        instance_key = f"{collection}:{persist_path}:{id(instance)}"
        cls._instances[instance_key] = instance

        return instance

    def __init__(
        self,
        collection: str,
        persist_path: str | None = None,
        host: str | None = None,
        port: int | None = None,
        mode: str = "memory",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        embedding_dim: int = 384,
        **kwargs
    ):
        """Initialize Chroma adapter.

        Args:
            collection: Collection name
            persist_path: Path for persistent storage (filesystem mode)
            host: Host for server mode
            port: Port for server mode
            mode: Mode of operation ('memory', 'filesystem', 'server')
            embedding_model: Embedding model name
            embedding_dim: Embedding dimension
            **kwargs: Additional Chroma parameters
        """
        if hasattr(self, '_initialized'):
            return

        # Create Chroma document store based on mode
        store_params = {
            "collection_name": collection,
            "embedding_function": "default",  # Use default embedding function
        }

        # Configure based on mode
        if mode == "server":
            # Server mode - connect to remote Chroma server
            if host and port:
                store_params.update({
                    "host": host,
                    "port": port
                })
                logger.info(f"Chroma adapter configured for server mode: {host}:{port}")
            else:
                raise ValueError("Host and port must be provided for server mode")

        elif mode == "filesystem":
            # Filesystem mode - persistent storage
            if persist_path is not None:
                store_params["persist_path"] = persist_path
                logger.info(f"Chroma adapter configured for filesystem mode: {persist_path}")
            else:
                raise ValueError("persist_path must be provided for filesystem mode")

        elif mode == "memory":
            # Memory mode - no additional parameters needed
            logger.info("Chroma adapter configured for in-memory mode")
        else:
            raise ValueError(f"Invalid mode: {mode}. Must be 'memory', 'filesystem', or 'server'")

        # Add other parameters
        store_params.update({k: v for k, v in kwargs.items()
                           if k not in ["collection_name", "embedding_function", "host", "port", "persist_path", "mode"]})

        document_store = ChromaDocumentStore(**store_params)

        super().__init__(
            document_store=document_store,
            collection_name=collection,
            embedding_model=embedding_model,
            embedding_dim=embedding_dim
        )

        self._initialized = True
        self.persist_path = persist_path
        self.host = host
        self.port = port
        self.mode = mode
        logger.info(f"Chroma adapter initialized for collection: {collection} (mode: {mode})")

    def cleanup(self):
        """Clean up the Chroma adapter and its resources."""
        try:
            if hasattr(self, 'document_store') and self.document_store:
                # Close any connections
                if hasattr(self.document_store, '_client'):
                    # Reset the client to force cleanup
                    self.document_store._client = None
                if hasattr(self.document_store, '_collection'):
                    self.document_store._collection = None

            # Remove from singleton instances
            instance_key = f"{self.collection_name}:{self.persist_path}"
            if instance_key in self._instances:
                del self._instances[instance_key]

            logger.info(f"Chroma adapter cleaned up for collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error during Chroma cleanup: {e}")

    def get_collection_info(self) -> dict[str, Any]:
        """Get detailed Chroma collection information."""
        info = super().get_collection_info()
        info["backend"] = "chroma"

        try:
            # Get Chroma-specific info
            collection = self.document_store._collection

            info.update({
                "persist_path": self.persist_path,
                "collection_name": collection.name,
                "metadata": collection.metadata or {},
            })
        except Exception as e:
            logger.error(f"Error getting Chroma collection info: {e}")

        return info

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "ChromaAdapter":
        """Create Chroma adapter from configuration."""
        return cls(**config)

    @classmethod
    def clear_all_instances(cls):
        """Clear all singleton instances and clean up resources."""
        for instance in cls._instances.values():
            try:
                instance.cleanup()
            except Exception as e:
                logger.error(f"Error cleaning up Chroma instance: {e}")
        cls._instances.clear()
        logger.info("All Chroma adapter instances cleared")
