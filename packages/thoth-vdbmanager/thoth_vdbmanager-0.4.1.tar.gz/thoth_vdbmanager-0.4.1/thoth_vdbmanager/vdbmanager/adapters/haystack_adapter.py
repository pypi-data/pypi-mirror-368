"""Base Haystack adapter for Thoth Vector Database."""

import logging
from typing import Any

from haystack import Pipeline
from haystack.components.embedders import (
    SentenceTransformersDocumentEmbedder,
    SentenceTransformersTextEmbedder,
)
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

logger = logging.getLogger(__name__)


class HaystackVectorStoreAdapter(VectorStoreInterface):
    """Base adapter that uses Haystack DocumentStore as backend."""

    def __init__(
        self,
        document_store: DocumentStore,
        collection_name: str,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        embedding_dim: int = 384,
    ):
        """Initialize the Haystack adapter.
        
        Args:
            document_store: Haystack DocumentStore instance
            collection_name: Name of the collection/index
            embedding_model: Name of the sentence transformer model
            embedding_dim: Dimension of the embeddings
        """
        self.document_store = document_store
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        self.embedding_dim = embedding_dim

        # Lazy initialization of embedders
        self._document_embedder: SentenceTransformersDocumentEmbedder | None = None
        self._text_embedder: SentenceTransformersTextEmbedder | None = None
        self._search_pipeline: Pipeline | None = None

        logger.info(
            f"Initialized Haystack adapter for {collection_name} "
            f"with model {embedding_model}"
        )

    def ensure_collection_exists(self) -> None:
        """Ensure the collection exists, create it if it doesn't.

        This is a base implementation that does nothing.
        Subclasses should override this method to implement collection creation logic.
        """
        pass

    def _get_document_embedder(self) -> SentenceTransformersDocumentEmbedder:
        """Get or create document embedder."""
        if self._document_embedder is None:
            self._document_embedder = SentenceTransformersDocumentEmbedder(
                model=self.embedding_model
            )
            self._document_embedder.warm_up()
        return self._document_embedder

    def _get_text_embedder(self) -> SentenceTransformersTextEmbedder:
        """Get or create text embedder."""
        if self._text_embedder is None:
            self._text_embedder = SentenceTransformersTextEmbedder(
                model=self.embedding_model
            )
            self._text_embedder.warm_up()
        return self._text_embedder

    def _get_search_pipeline(self) -> Pipeline:
        """Get or create search pipeline."""
        if self._search_pipeline is None:
            try:
                # Determine the appropriate retriever based on document store type
                retriever = self._create_retriever()

                if retriever is not None:
                    self._search_pipeline = Pipeline()
                    self._search_pipeline.add_component("embedder", self._get_text_embedder())
                    self._search_pipeline.add_component("retriever", retriever)
                    self._search_pipeline.connect("embedder.embedding", "retriever.query_embedding")
                else:
                    # Create a minimal pipeline without retriever for compatibility
                    logger.warning("No suitable retriever found, creating pipeline without retriever")
                    self._search_pipeline = Pipeline()
                    self._search_pipeline.add_component("embedder", self._get_text_embedder())
            except Exception as e:
                logger.error(f"Failed to create search pipeline: {e}")
                # Create a minimal pipeline without retriever for compatibility
                self._search_pipeline = Pipeline()
                self._search_pipeline.add_component("embedder", self._get_text_embedder())
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

            # Handle Milvus document store
            elif "Milvus" in document_store_type:
                try:
                    from milvus_haystack import MilvusEmbeddingRetriever
                    return MilvusEmbeddingRetriever(document_store=self.document_store, top_k=10)
                except ImportError as e:
                    logger.error(f"Failed to import MilvusEmbeddingRetriever: {e}")
                    return None

            # Handle Weaviate document store
            elif "Weaviate" in document_store_type:
                try:
                    from haystack_integrations.components.retrievers.weaviate import (
                        WeaviateEmbeddingRetriever,
                    )
                    return WeaviateEmbeddingRetriever(document_store=self.document_store, top_k=10)
                except ImportError as e:
                    logger.error(f"Failed to import WeaviateEmbeddingRetriever: {e}")
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

            # Handle Pinecone document store
            elif "Pinecone" in document_store_type:
                try:
                    from haystack_integrations.components.retrievers.pinecone import (
                        PineconeEmbeddingRetriever,
                    )
                    return PineconeEmbeddingRetriever(document_store=self.document_store, top_k=10)
                except ImportError as e:
                    logger.error(f"Failed to import PineconeEmbeddingRetriever: {e}")
                    return None

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

            # Handle other document store types - fallback to generic retriever
            else:
                logger.warning(f"No specific retriever found for document store type: {document_store_type}")
                # Try to use a generic retriever if available
                try:
                    from haystack.components.retrievers import (
                        InMemoryEmbeddingRetriever as MemoryRetriever,
                    )
                    return MemoryRetriever(document_store=self.document_store, top_k=10)
                except (ImportError, TypeError) as e:
                    logger.error(f"Generic retriever failed for {document_store_type}: {e}")
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
        """Add document with embedding."""
        haystack_doc = self._convert_to_haystack_document(doc)

        # Generate embedding
        embedder = self._get_document_embedder()
        result = embedder.run(documents=[haystack_doc])
        embedded_docs = result["documents"]

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
    ) -> list[BaseThothDocument]:
        """Search for similar documents."""
        if not query:
            return []

        try:
            # Create filter for document type
            filters = {
                "field": "meta.thoth_type",
                "operator": "==",
                "value": doc_type.value  # Use the enum value, not the string representation
            }
            logger.debug(f"Search filter: {filters} (looking for doc_type={doc_type})")

            # Use search pipeline
            pipeline = self._get_search_pipeline()

            # Check if pipeline has retriever component
            if "retriever" in pipeline.graph.nodes:
                # Full pipeline with retriever
                result = pipeline.run({
                    "embedder": {"text": query},
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
                        elif thoth_doc:
                            logger.debug(f"Filtered out document with wrong type: expected {doc_type}, got {thoth_doc.thoth_type}")

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

    def bulk_add_documents(self, documents: list[BaseThothDocument], policy: DuplicatePolicy | None = None) -> list[str]:
        """Add multiple documents in batch."""
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

        # Store all documents
        self.document_store.write_documents(
            embedded_docs,
            policy=policy
        )

        return [doc.id for doc in embedded_docs]

    def _get_all_documents(self) -> list[BaseThothDocument]:
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

    def delete_documents(self, document_ids: list[str]) -> None:
        """Deletes documents by their IDs."""
        return self.document_store.delete_documents(document_ids=document_ids)

    def delete_collection(self, thoth_type: ThothType | None = None) -> None:
        """Deletes documents from the store, optionally filtered by ThothType."""
        if thoth_type:
            logger.info(f"Deleting all documents of type: {str(thoth_type)}")
            docs_to_delete = self.get_documents_by_type(thoth_type, BaseThothDocument)
            if not docs_to_delete:
                logger.info(f"No documents of type {str(thoth_type)} found to delete.")
                return
            doc_ids = [doc.id for doc in docs_to_delete]
            logger.debug(f"Found {len(doc_ids)} documents of type {str(thoth_type)} to delete.")
        else:
            logger.warning("Deleting ALL documents in the collection.") # Message change was correct
            try:
                # Fetch all document IDs first, then delete by ID
                # This avoids potentially problematic filters like '!= None'
                all_docs_haystack = self.filter_documents(filters=None) # Get all docs - This line was correct
                if not all_docs_haystack:
                    logger.info("No documents found in the collection to delete.") # This line was correct
                    return # This line was correct
                # Ensure using the correct variable name from the line above
                doc_ids = [h_doc.id for h_doc in all_docs_haystack] # Corrected variable name
                logger.debug(f"Found {len(doc_ids)} documents to delete.") # Corrected log message

            except Exception as e:
                logger.error(f"Failed to retrieve all Thoth document IDs for deletion: {e}. Aborting delete_collection(None).", exc_info=True)
                return

        if not doc_ids:
            logger.info("No document IDs identified for deletion.")
            return

        try:
            logger.info(f"Deleting {len(doc_ids)} documents...")
            self.delete_documents(document_ids=doc_ids)
            logger.info(f"Successfully deleted {len(doc_ids)} documents.")
        except Exception as e:
            logger.error(f"Failed during bulk deletion of {len(doc_ids)} documents: {e}", exc_info=True)

    def get_collection_info(self) -> dict[str, Any]:
        """Get collection information."""
        try:
            count = self.document_store.count_documents()
            return {
                "collection_name": self.collection_name,
                "total_documents": count,
                "embedding_model": self.embedding_model,
                "embedding_dim": self.embedding_dim,
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {
                "collection_name": self.collection_name,
                "total_documents": 0,
                "embedding_model": self.embedding_model,
                "embedding_dim": self.embedding_dim,
            }

    def get_documents_by_type(self, thoth_type: ThothType, doc_class: type[BaseThothDocument]) -> list[BaseThothDocument]:
        """Get all documents of a specific ThothType."""
        try:
            if thoth_type == ThothType.COLUMN_NAME:
                return self.get_all_column_documents()
            elif thoth_type == ThothType.SQL:
                return self.get_all_sql_documents()
            elif thoth_type == ThothType.EVIDENCE:
                return self.get_all_evidence_documents()
            else:
                logger.warning(f"Unknown ThothType: {thoth_type}")
                return []
        except Exception as e:
            logger.error(f"Failed to get documents of type {str(thoth_type)}: {e}", exc_info=True)
            return []
