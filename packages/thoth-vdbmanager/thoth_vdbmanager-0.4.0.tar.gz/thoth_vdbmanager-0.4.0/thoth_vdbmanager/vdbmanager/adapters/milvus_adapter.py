"""Milvus adapter for Thoth Vector Database."""

import logging
import time
from typing import Any

from haystack.document_stores.types import DuplicatePolicy
from milvus_haystack import MilvusDocumentStore

from ..core.base import BaseThothDocument
from .haystack_adapter import HaystackVectorStoreAdapter

logger = logging.getLogger(__name__)


class MilvusAdapter(HaystackVectorStoreAdapter):
    """Milvus implementation using Haystack integration."""

    _instances: dict[str, "MilvusAdapter"] = {}

    def __new__(
        cls,
        collection: str,
        connection_uri: str = "http://localhost:19530",
        **kwargs
    ):
        """Singleton pattern for Milvus adapter."""
        instance_key = f"{collection}:{connection_uri}"
        if instance_key in cls._instances:
            return cls._instances[instance_key]

        instance = super().__new__(cls)
        cls._instances[instance_key] = instance
        return instance

    def __init__(
        self,
        collection: str,
        connection_uri: str = "http://localhost:19530",
        mode: str = "lite",
        host: str | None = None,
        port: int | None = None,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        embedding_dim: int = 384,
        **kwargs
    ):
        """Initialize Milvus adapter.

        Args:
            collection: Collection name
            connection_uri: Milvus connection URI (for lite mode)
            mode: Mode of operation ('lite' or 'server')
            host: Host for server mode
            port: Port for server mode
            embedding_model: Embedding model name
            embedding_dim: Embedding dimension
            **kwargs: Additional Milvus parameters
        """
        if hasattr(self, '_initialized'):
            return

        # Create Milvus document store based on mode
        if mode == "server":
            # Server mode - connect to remote Milvus server
            if host and port:
                server_uri = f"http://{host}:{port}"
                logger.info(f"Milvus adapter configured for server mode: {server_uri}")
            else:
                server_uri = connection_uri
                logger.info(f"Milvus adapter configured for server mode: {server_uri}")

            document_store = MilvusDocumentStore(
                collection_name=collection,
                connection_args={"uri": server_uri},
                index_params={
                    "metric_type": "COSINE",
                    "index_type": "IVF_FLAT",
                    "params": {"nlist": 128},
                    **kwargs.get("index_params", {})
                },
                search_params={
                    "metric_type": "COSINE",
                    "params": {"nprobe": 10},
                    **kwargs.get("search_params", {})
                },
                **{k: v for k, v in kwargs.items() if k not in ["index_params", "search_params", "connection_uri", "mode", "host", "port"]}
            )
        elif mode == "lite":
            # Lite mode - file-based storage
            logger.info(f"Milvus adapter configured for lite mode: {connection_uri}")
            document_store = MilvusDocumentStore(
                collection_name=collection,
                connection_args={"uri": connection_uri},
                index_params={
                    "metric_type": "COSINE",
                    "index_type": "IVF_FLAT",
                    "params": {"nlist": 128},
                    **kwargs.get("index_params", {})
                },
                search_params={
                    "metric_type": "COSINE",
                    "params": {"nprobe": 10},
                    **kwargs.get("search_params", {})
                },
                **{k: v for k, v in kwargs.items() if k not in ["index_params", "search_params", "connection_uri", "mode", "host", "port"]}
            )
        else:
            raise ValueError(f"Invalid mode: {mode}. Must be 'lite' or 'server'")

        super().__init__(
            document_store=document_store,
            collection_name=collection,
            embedding_model=embedding_model,
            embedding_dim=embedding_dim
        )

        self._initialized = True
        self.connection_uri = connection_uri
        self.mode = mode
        self.host = host
        self.port = port
        logger.info(f"Milvus adapter initialized for collection: {collection} (mode: {mode})")

    def _add_document_with_embedding(self, doc: BaseThothDocument) -> str:
        """Add a single document with embedding (Milvus-specific implementation)."""
        haystack_doc = self._convert_to_haystack_document(doc)

        # Generate embedding
        embedder = self._get_document_embedder()
        result = embedder.run(documents=[haystack_doc])
        embedded_docs = result["documents"]

        # For Milvus, we need to handle duplicates manually since it only supports NONE policy
        try:
            # First, try to delete existing document if it exists
            existing_doc = self.get_document(doc.id)
            if existing_doc:
                self.delete_document(doc.id)
        except Exception as e:
            logger.debug(f"No existing document to delete: {e}")

        # Store document with NONE policy (Milvus requirement)
        self.document_store.write_documents(
            embedded_docs,
            policy=DuplicatePolicy.NONE
        )

        # Wait for Milvus to index the document (especially important for Milvus Lite)
        time.sleep(0.1)

        # Debug: Verify document was stored
        logger.debug(f"Stored document with ID: {embedded_docs[0].id}")

        return embedded_docs[0].id

    def bulk_add_documents(self, documents: list[BaseThothDocument], policy: DuplicatePolicy | None = None) -> list[str]:
        """Add multiple documents in batch (Milvus-specific implementation)."""
        if not documents:
            return []

        # Use default policy if none provided
        if policy is None:
            policy = DuplicatePolicy.OVERWRITE

        haystack_docs = [self._convert_to_haystack_document(doc) for doc in documents]

        # Generate embeddings in batch
        embedder = self._get_document_embedder()
        result = embedder.run(documents=haystack_docs)
        embedded_docs = result["documents"]

        # For Milvus, handle duplicates manually based on policy
        if policy == DuplicatePolicy.OVERWRITE:
            for doc in documents:
                try:
                    existing_doc = self.get_document(doc.id)
                    if existing_doc:
                        self.delete_document(doc.id)
                except Exception as e:
                    logger.debug(f"No existing document to delete: {e}")
        # For other policies like SKIP or FAIL, we could add additional logic here

        # Store all documents with NONE policy
        self.document_store.write_documents(
            embedded_docs,
            policy=DuplicatePolicy.NONE
        )

        # Wait for Milvus to index the documents
        time.sleep(0.1)

        return [doc.id for doc in embedded_docs]

    def get_document(self, doc_id: str) -> BaseThothDocument | None:
        """Get a document by ID (Milvus-specific implementation with enhanced filtering and retry)."""
        # Retry mechanism for Milvus indexing delays
        max_retries = 3
        retry_delay = 0.1

        for attempt in range(max_retries):
            try:
                # Try multiple filter approaches for Milvus
                filters_to_try = [
                    # Standard approach
                    {
                        "operator": "OR",
                        "conditions": [
                            {"field": "meta.thoth_id", "operator": "==", "value": doc_id},
                            {"field": "id", "operator": "==", "value": doc_id}
                        ]
                    },
                    # Simple thoth_id filter
                    {"field": "meta.thoth_id", "operator": "==", "value": doc_id},
                    # Simple id filter
                    {"field": "id", "operator": "==", "value": doc_id},
                ]

                for i, filters in enumerate(filters_to_try):
                    try:
                        logger.debug(f"Attempt {attempt+1}, filter approach {i+1}: {filters}")
                        documents = self.document_store.filter_documents(filters=filters)
                        if documents:
                            logger.debug(f"Found document with filter approach {i+1} on attempt {attempt+1}")
                            return self._convert_from_haystack_document(documents[0])
                    except Exception as e:
                        logger.debug(f"Filter approach {i+1} failed on attempt {attempt+1}: {e}")
                        continue

                # If filtering fails, try getting all documents and search manually
                logger.debug(f"All filter approaches failed on attempt {attempt+1}, trying manual search")
                try:
                    all_docs = self.document_store.filter_documents(filters={})
                    logger.debug(f"Found {len(all_docs)} total documents on attempt {attempt+1}")
                    for doc in all_docs:
                        if (doc.id == doc_id or
                            (doc.meta and doc.meta.get("thoth_id") == doc_id)):
                            logger.debug(f"Found document via manual search on attempt {attempt+1}")
                            return self._convert_from_haystack_document(doc)
                except Exception as e:
                    logger.debug(f"Manual search failed on attempt {attempt+1}: {e}")

            except Exception as e:
                logger.error(f"Error getting document {doc_id} on attempt {attempt+1}: {e}")

            # Wait before retry (except on last attempt)
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff

        logger.debug(f"Document {doc_id} not found after {max_retries} attempts")
        return None

    def _get_search_pipeline(self):
        """Get or create Milvus-specific search pipeline."""
        if self._search_pipeline is None:
            from haystack import Pipeline
            from milvus_haystack import MilvusEmbeddingRetriever

            self._search_pipeline = Pipeline()
            self._search_pipeline.add_component("embedder", self._get_text_embedder())
            self._search_pipeline.add_component(
                "retriever",
                MilvusEmbeddingRetriever(document_store=self.document_store, top_k=10)
            )
            self._search_pipeline.connect("embedder.embedding", "retriever.query_embedding")
        return self._search_pipeline

    def search_similar(
        self,
        query: str,
        doc_type,
        top_k: int = 5,
        score_threshold: float = 0.7,
    ):
        """Search for similar documents (Milvus-specific implementation)."""
        if not query:
            return []

        try:
            # Use Milvus search pipeline (simplified approach)
            pipeline = self._get_search_pipeline()

            # Run the pipeline with just the query
            result = pipeline.run({
                "embedder": {"text": query}
            })

            documents = result.get("retriever", {}).get("documents", [])

            # Convert and filter by document type and score
            thoth_docs = []
            for doc in documents:
                # Convert to thoth document first
                thoth_doc = self._convert_from_haystack_document(doc)
                if thoth_doc:
                    # Filter by document type
                    if thoth_doc.thoth_type == doc_type:
                        # Check score if available
                        if hasattr(doc, 'score') and doc.score is not None:
                            if doc.score >= score_threshold:
                                thoth_docs.append(thoth_doc)
                        else:
                            # If no score, include the document
                            thoth_docs.append(thoth_doc)

            return thoth_docs[:top_k]  # Ensure we don't exceed top_k

        except Exception as e:
            logger.error(f"Milvus search failed: {e}")
            return []

    def get_collection_info(self) -> dict[str, Any]:
        """Get detailed Milvus collection information."""
        info = super().get_collection_info()
        info["backend"] = "milvus"

        try:
            # Get Milvus-specific info
            from pymilvus import Collection, connections

            # Connect to Milvus
            connections.connect(uri=self.connection_uri)

            # Get collection info
            collection = Collection(self.collection_name)
            collection.load()

            # Get collection statistics (use num_entities instead of get_stats)
            try:
                row_count = collection.num_entities
            except Exception:
                # Fallback for older versions
                row_count = 0

            info.update({
                "connection_uri": self.connection_uri,
                "collection_name": self.collection_name,
                "row_count": row_count,
                "partitions": [p.name for p in collection.partitions],
                "schema": {
                    "fields": [field.name for field in collection.schema.fields],
                    "description": collection.schema.description
                }
            })

            # Try to get index info safely
            try:
                info["indexes"] = [idx.params for idx in collection.indexes]
            except Exception:
                info["indexes"] = []

            collection.release()

        except Exception as e:
            logger.error(f"Error getting Milvus collection info: {e}")

        return info

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "MilvusAdapter":
        """Create Milvus adapter from configuration."""
        return cls(**config)

    @classmethod
    def clear_all_instances(cls):
        """Clear all singleton instances (useful for testing)."""
        cls._instances.clear()
        logger.debug("Cleared all Milvus adapter instances")
