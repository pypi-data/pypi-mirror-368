# Copyright (c) 2025 Marco Pancotti
# This file is part of Thoth and is released under the MIT License.
# See the LICENSE.md file in the project root for full license information.

"""External Haystack adapter for Thoth Vector Database v0.6.0."""

import logging
from typing import Any, Dict, List, Optional

from haystack import Pipeline
from haystack.dataclasses import Document as HaystackDocument
from haystack.document_stores.types import DocumentStore, DuplicatePolicy

from ..core.base import (
    BaseThothDocument,
    ColumnNameDocument,
    EvidenceDocument,
    SqlDocument,
    ThothType,
    VectorStoreInterface,
)
from ..core.external_embedding_manager import ExternalEmbeddingManager

logger = logging.getLogger(__name__)


class ExternalHaystackAdapter(VectorStoreInterface):
    """Haystack adapter using external embedding providers."""

    def __init__(
        self,
        document_store: DocumentStore,
        collection_name: str,
        embedding_manager: ExternalEmbeddingManager,
    ):
        """Initialize the External Haystack adapter.
        
        Args:
            document_store: Haystack DocumentStore instance
            collection_name: Name of the collection/index
            embedding_manager: External embedding manager instance
        """
        self.document_store = document_store
        self.collection_name = collection_name
        self.embedding_manager = embedding_manager
        
        # Create a minimal pipeline for compatibility
        self._search_pipeline: Optional[Pipeline] = None

        logger.info(
            f"Initialized External Haystack adapter for {collection_name} "
            f"with {self.embedding_manager.provider.provider_name} provider"
        )

    def ensure_collection_exists(self) -> None:
        """Ensure the collection exists, create it if it doesn't."""
        # Base implementation - subclasses should override if needed
        pass

    def _get_search_pipeline(self) -> Pipeline:
        """Get or create search pipeline for external embeddings."""
        if self._search_pipeline is None:
            try:
                # Create custom pipeline with external embedding manager
                self._search_pipeline = Pipeline()
                
                # Add custom embedding component that uses external manager
                self._search_pipeline.add_component(
                    "external_embedder", 
                    ExternalEmbeddingComponent(self.embedding_manager)
                )
                
                # Try to add appropriate retriever
                retriever = self._create_retriever()
                if retriever is not None:
                    self._search_pipeline.add_component("retriever", retriever)
                    self._search_pipeline.connect("external_embedder.embedding", "retriever.query_embedding")
                else:
                    logger.warning("No suitable retriever found, pipeline will only have embedder")
                    
            except Exception as e:
                logger.error(f"Failed to create search pipeline: {e}")
                # Create minimal pipeline
                self._search_pipeline = Pipeline()
                self._search_pipeline.add_component(
                    "external_embedder", 
                    ExternalEmbeddingComponent(self.embedding_manager)
                )
                
        return self._search_pipeline

    def _create_retriever(self):
        """Create the appropriate retriever for the document store type."""
        document_store_type = type(self.document_store).__name__

        try:
            # Handle Qdrant document store
            if "Qdrant" in document_store_type:
                try:
                    from haystack_integrations.components.retrievers.qdrant import (
                        QdrantEmbeddingRetriever,
                    )
                    return QdrantEmbeddingRetriever(document_store=self.document_store, top_k=10)
                except ImportError as e:
                    logger.error(f"Failed to import QdrantEmbeddingRetriever: {e}")
                    return None

            # Handle InMemory document store
            elif "InMemory" in document_store_type:
                try:
                    from haystack.components.retrievers import (
                        InMemoryEmbeddingRetriever as MemoryRetriever,
                    )
                except ImportError:
                    try:
                        from haystack.components.retrievers import MemoryRetriever
                    except ImportError as e:
                        logger.error(f"Failed to import InMemory retriever: {e}")
                        return None
                return MemoryRetriever(document_store=self.document_store, top_k=10)

            # Handle Chroma document store
            elif "Chroma" in document_store_type:
                try:
                    from haystack_integrations.components.retrievers.chroma import (
                        ChromaEmbeddingRetriever,
                    )
                    return ChromaEmbeddingRetriever(document_store=self.document_store, top_k=10)
                except ImportError as e:
                    logger.error(f"Failed to import ChromaEmbeddingRetriever: {e}")
                    return None

            # Handle PgVector document store
            elif "Pgvector" in document_store_type:
                try:
                    from haystack_integrations.components.retrievers.pgvector import (
                        PgvectorEmbeddingRetriever,
                    )
                    return PgvectorEmbeddingRetriever(document_store=self.document_store, top_k=10)
                except ImportError as e:
                    logger.error(f"Failed to import PgvectorEmbeddingRetriever: {e}")
                    return None

            # Handle Milvus document store
            elif "Milvus" in document_store_type:
                try:
                    from milvus_haystack import MilvusEmbeddingRetriever
                    return MilvusEmbeddingRetriever(document_store=self.document_store, top_k=10)
                except ImportError as e:
                    logger.error(f"Failed to import MilvusEmbeddingRetriever: {e}")
                    return None

            else:
                logger.warning(f"No specific retriever found for document store type: {document_store_type}")
                return None

        except Exception as e:
            logger.error(f"Error creating retriever for {document_store_type}: {e}")
            return None

    def _convert_to_haystack_document(self, doc: BaseThothDocument) -> HaystackDocument:
        """Convert Thoth document to Haystack document."""
        if not doc.text:
            doc.text = self._enrich_content(doc)

        metadata = {
            "thoth_type": doc.thoth_type.value,
            "thoth_id": doc.id,
        }

        if isinstance(doc, ColumnNameDocument):
            metadata.update({
                "table_name": doc.table_name,
                "column_name": doc.column_name,
                "original_column_name": doc.original_column_name,
                "column_description": doc.column_description,
                "value_description": doc.value_description,
            })
        elif isinstance(doc, SqlDocument):
            metadata.update({
                "question": doc.question,
                "sql": doc.sql,
                "evidence": doc.evidence,
            })
        elif isinstance(doc, EvidenceDocument):
            metadata.update({
                "evidence": doc.evidence,
            })

        return HaystackDocument(
            id=doc.id,
            content=doc.text,
            meta=metadata,
        )

    def _convert_from_haystack_document(self, haystack_doc: HaystackDocument) -> BaseThothDocument | None:
        """Convert Haystack document to Thoth document."""
        if not haystack_doc.meta or "thoth_type" not in haystack_doc.meta:
            return None

        thoth_type_str = haystack_doc.meta["thoth_type"]
        try:
            thoth_type = ThothType(thoth_type_str)
        except ValueError:
            logger.warning(f"Invalid ThothType: {thoth_type_str}")
            return None

        doc_id = str(haystack_doc.meta.get("thoth_id", haystack_doc.id))
        doc_text = haystack_doc.content

        try:
            if thoth_type == ThothType.COLUMN_NAME:
                return ColumnNameDocument(
                    id=doc_id,
                    text=doc_text,
                    table_name=haystack_doc.meta.get("table_name", ""),
                    column_name=haystack_doc.meta.get("column_name", ""),
                    original_column_name=haystack_doc.meta.get("original_column_name", ""),
                    column_description=haystack_doc.meta.get("column_description", ""),
                    value_description=haystack_doc.meta.get("value_description", ""),
                )
            elif thoth_type == ThothType.SQL:
                return SqlDocument(
                    id=doc_id,
                    text=doc_text,
                    question=haystack_doc.meta.get("question", ""),
                    sql=haystack_doc.meta.get("sql", ""),
                    evidence=haystack_doc.meta.get("evidence", ""),
                )
            elif thoth_type == ThothType.EVIDENCE:
                return EvidenceDocument(
                    id=doc_id,
                    text=doc_text,
                    evidence=haystack_doc.meta.get("evidence", haystack_doc.content),
                )
        except Exception as e:
            logger.error(f"Error converting document: {e}")
            return None

    def _enrich_content(self, doc: BaseThothDocument) -> str:
        """Enrich document content for embedding."""
        if isinstance(doc, ColumnNameDocument):
            return (
                f"Table: {doc.table_name}, Column: {doc.column_name} "
                f"(Original: {doc.original_column_name}). "
                f"Description: {doc.column_description}. "
                f"Value Info: {doc.value_description}"
            )
        elif isinstance(doc, SqlDocument):
            return f"{doc.question.lower()} {doc.evidence.lower()}"
        elif isinstance(doc, EvidenceDocument):
            return doc.evidence
        else:
            return doc.text

    def _add_document_with_embedding(self, doc: BaseThothDocument) -> str:
        """Add document with embedding using external manager."""
        haystack_doc = self._convert_to_haystack_document(doc)

        # Generate embedding using external manager
        embedded_docs = self.embedding_manager.encode_documents([haystack_doc])

        # Store document
        self.document_store.write_documents(
            embedded_docs,
            policy=DuplicatePolicy.OVERWRITE
        )

        return embedded_docs[0].id

    def add_column_description(self, doc: ColumnNameDocument) -> str:
        """Add a column description document."""
        return self._add_document_with_embedding(doc)

    def add_sql(self, doc: SqlDocument) -> str:
        """Add an SQL document."""
        return self._add_document_with_embedding(doc)

    def add_evidence(self, doc: EvidenceDocument) -> str:
        """Add an evidence document."""
        return self._add_document_with_embedding(doc)

    def search_similar(
        self,
        query: str,
        doc_type: ThothType,
        top_k: int = 5,
        score_threshold: float = 0.7,
    ) -> List[BaseThothDocument]:
        """Search for similar documents using external embeddings."""
        if not query:
            return []

        try:
            # Create filter for document type
            filters = {
                "field": "meta.thoth_type",
                "operator": "==",
                "value": doc_type.value
            }
            logger.debug(f"Search filter: {filters} (looking for doc_type={doc_type})")

            # Use search pipeline
            pipeline = self._get_search_pipeline()

            # Check if pipeline has retriever component
            if "retriever" in pipeline.graph.nodes:
                # Full pipeline with retriever
                result = pipeline.run({
                    "external_embedder": {"text": query},
                    "retriever": {"top_k": top_k, "filters": filters}
                })
                documents = result.get("retriever", {}).get("documents", [])
            else:
                # Fallback: pipeline only has embedder, no retriever available
                logger.warning("No retriever component available in pipeline, returning empty results")
                return []

            # Convert and filter by score and document type
            thoth_docs = []
            for doc in documents:
                if hasattr(doc, 'score') and doc.score is not None:
                    if doc.score >= score_threshold:
                        thoth_doc = self._convert_from_haystack_document(doc)
                        if thoth_doc and thoth_doc.thoth_type == doc_type:
                            thoth_docs.append(thoth_doc)

            return thoth_docs

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def get_document(self, doc_id: str) -> BaseThothDocument | None:
        """Get a document by ID."""
        try:
            filters = {
                "operator": "OR",
                "conditions": [
                    {"field": "meta.thoth_id", "operator": "==", "value": doc_id},
                    {"field": "id", "operator": "==", "value": doc_id}
                ]
            }

            documents = self.document_store.filter_documents(filters=filters)
            if documents:
                return self._convert_from_haystack_document(documents[0])

        except Exception as e:
            logger.error(f"Error getting document {doc_id}: {e}")

        return None

    def delete_document(self, doc_id: str) -> None:
        """Delete a document by ID."""
        try:
            self.document_store.delete_documents([doc_id])
        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {e}")

    def bulk_add_documents(self, documents: List[BaseThothDocument], policy: Optional[DuplicatePolicy] = None) -> List[str]:
        """Add multiple documents in batch using external manager."""
        if not documents:
            return []

        # Use default policy if none provided
        if policy is None:
            policy = DuplicatePolicy.OVERWRITE

        haystack_docs = [self._convert_to_haystack_document(doc) for doc in documents]

        # Generate embeddings in batch using external manager
        embedded_docs = self.embedding_manager.encode_documents(haystack_docs)

        # Store all documents
        self.document_store.write_documents(
            embedded_docs,
            policy=policy
        )

        return [doc.id for doc in embedded_docs]

    def _get_all_documents(self) -> List[BaseThothDocument]:
        """Get all documents."""
        try:
            haystack_docs = self.document_store.filter_documents()
            return [
                doc for doc in [
                    self._convert_from_haystack_document(h_doc)
                    for h_doc in haystack_docs
                ]
                if doc is not None
            ]
        except Exception as e:
            logger.error(f"Error getting all documents: {e}")
            return []

    def delete_collection(self, thoth_type: ThothType) -> None:
        """Delete all documents of a specific type."""
        try:
            if thoth_type:
                filters = {
                    "field": "meta.thoth_type",
                    "operator": "==",
                    "value": thoth_type.value
                }
                documents = self.document_store.filter_documents(filters=filters)
                if documents:
                    doc_ids = [doc.id for doc in documents]
                    self.document_store.delete_documents(doc_ids)
                    logger.info(f"Deleted {len(doc_ids)} documents of type {thoth_type}")
            else:
                # Delete all documents
                documents = self.document_store.filter_documents()
                if documents:
                    doc_ids = [doc.id for doc in documents]
                    self.document_store.delete_documents(doc_ids)
                    logger.info(f"Deleted all {len(doc_ids)} documents")
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")

    def get_collection_info(self) -> Dict[str, Any]:
        """Get collection information including external embedding details."""
        try:
            count = self.document_store.count_documents()
            model_info = self.embedding_manager.get_model_info()
            
            return {
                "collection_name": self.collection_name,
                "total_documents": count,
                "embedding_provider": model_info["provider_name"],
                "embedding_model": model_info["model_name"],
                "embedding_dim": model_info["embedding_dimension"],
                "max_batch_size": model_info["max_batch_size"],
                "cache_enabled": model_info["cache_enabled"],
                "cache_size": model_info["cache_size"],
                "supports_multilingual": model_info["supports_multilingual"],
                "is_external": model_info["is_external"],
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {
                "collection_name": self.collection_name,
                "total_documents": 0,
                "error": str(e),
            }


class ExternalEmbeddingComponent:
    """Custom Haystack component for external embeddings."""
    
    def __init__(self, embedding_manager: ExternalEmbeddingManager):
        self.embedding_manager = embedding_manager
    
    def run(self, text: str) -> Dict[str, Any]:
        """Run external embedding."""
        embedding = self.embedding_manager.encode_query(text)
        return {"embedding": embedding}