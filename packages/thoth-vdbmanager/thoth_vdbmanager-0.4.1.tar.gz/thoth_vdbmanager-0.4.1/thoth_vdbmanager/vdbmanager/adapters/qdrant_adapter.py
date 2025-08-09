"""Qdrant adapter for Thoth Vector Database."""

import logging
from typing import Any
from urllib.parse import urlparse

from haystack_integrations.document_stores.qdrant import QdrantDocumentStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from .haystack_adapter import HaystackVectorStoreAdapter

logger = logging.getLogger(__name__)


class QdrantAdapter(HaystackVectorStoreAdapter):
    """Qdrant implementation using Haystack integration."""

    _instances: dict[str, "QdrantAdapter"] = {}

    def __new__(
        cls,
        collection: str,
        host: str = "localhost",
        port: int = 6333,
        api_key: str | None = None,
        url: str | None = None,
        **kwargs
    ):
        """Singleton pattern for Qdrant adapter."""
        instance_key = f"{collection}:{host}:{port}:{api_key}"
        if instance_key in cls._instances:
            return cls._instances[instance_key]

        instance = super().__new__(cls)
        cls._instances[instance_key] = instance
        return instance

    def __init__(
        self,
        collection: str,
        host: str = "localhost",
        port: int = 6333,
        api_key: str | None = None,
        url: str | None = None,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        embedding_dim: int = 384,
        **kwargs
    ):
        """Initialize Qdrant adapter.
        
        Args:
            collection: Collection name
            host: Qdrant host
            port: Qdrant port
            api_key: API key for authentication
            url: Full URL (overrides host/port)
            embedding_model: Embedding model name
            embedding_dim: Embedding dimension
            **kwargs: Additional Qdrant parameters
        """
        # Prevent reinitialization
        if hasattr(self, '_initialized'):
            return

        # Parse URL if provided
        if url:
            parsed = urlparse(url)
            host = parsed.hostname or host
            port = parsed.port or port

        # Store connection details for later use
        self._host = host
        self._port = port
        self._api_key = api_key

        # Create Qdrant document store
        document_store = QdrantDocumentStore(
            index=collection,
            host=host,
            port=port,
            api_key=api_key,
            embedding_dim=embedding_dim,
            hnsw_config={
                "m": 16,
                "ef_construct": 100,
                **kwargs.get("hnsw_config", {})
            },
            **{k: v for k, v in kwargs.items() if k != "hnsw_config"}
        )

        super().__init__(
            document_store=document_store,
            collection_name=collection,
            embedding_model=embedding_model,
            embedding_dim=embedding_dim
        )

        self._initialized = True
        logger.info(f"Qdrant adapter initialized for collection: {collection}")

    def ensure_collection_exists(self) -> None:
        """Ensure the collection exists, create it if it doesn't."""
        logger.info(f"ensure_collection_exists called for collection: {self.collection_name}")
        try:
            # Create a direct Qdrant client connection using stored connection details
            logger.info(f"Creating Qdrant client with host={self._host}, port={self._port}, api_key={self._api_key}")
            try:
                client = QdrantClient(host=self._host, port=self._port, api_key=self._api_key)
                logger.info(f"QdrantClient constructor returned: {client}")
            except Exception as client_error:
                logger.error(f"Exception during QdrantClient creation: {client_error}")
                raise RuntimeError(f"Failed to create Qdrant client: {client_error}")

            if client is None:
                raise RuntimeError("Failed to create Qdrant client - client is None")

            logger.info(f"Successfully created Qdrant client: {client}")

            # Check if collection exists
            try:
                collection_info = client.get_collection(self.collection_name)
                logger.info(f"Collection '{self.collection_name}' already exists with {collection_info.points_count} points")
                return
            except Exception as e:
                # Collection doesn't exist, create it
                logger.info(f"Collection '{self.collection_name}' doesn't exist (error: {e}), creating it...")

                try:
                    # Create collection with proper configuration
                    result = client.create_collection(
                        collection_name=self.collection_name,
                        vectors_config=VectorParams(
                            size=self.embedding_dim,
                            distance=Distance.COSINE
                        )
                    )
                    logger.info(f"Successfully created collection '{self.collection_name}' with {self.embedding_dim}-dimensional vectors and Cosine distance. Result: {result}")
                except Exception as create_error:
                    logger.error(f"Failed to create collection '{self.collection_name}': {create_error}")
                    raise

        except Exception as e:
            logger.error(f"Error ensuring collection exists: {e}")
            raise

    def get_collection_info(self) -> dict[str, Any]:
        """Get detailed Qdrant collection information."""
        info = super().get_collection_info()

        try:
            # Get additional Qdrant-specific info using direct client connection
            try:
                client = QdrantClient(host=self._host, port=self._port, api_key=self._api_key)
                if client is None:
                    raise RuntimeError("QdrantClient constructor returned None")
            except Exception as client_error:
                logger.error(f"Exception during QdrantClient creation in get_collection_info: {client_error}")
                raise RuntimeError(f"Failed to create Qdrant client: {client_error}")

            collection_info = client.get_collection(self.collection_name)

            info.update({
                "backend": "qdrant",
                "points_count": collection_info.points_count,
                "vectors_config": {
                    "size": collection_info.config.params.vectors.size,
                    "distance": str(collection_info.config.params.vectors.distance),
                },
                "hnsw_config": {
                    "m": collection_info.config.params.hnsw_config.m,
                    "ef_construct": collection_info.config.params.hnsw_config.ef_construct,
                }
            })
        except Exception as e:
            logger.error(f"Error getting Qdrant collection info: {e}")
            info["backend"] = "qdrant"

        return info

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "QdrantAdapter":
        """Create Qdrant adapter from configuration."""
        return cls(**config)
