"""PostgreSQL pgvector adapter for Thoth Vector Database."""

import logging
from typing import Any

from haystack.utils import Secret
from haystack_integrations.document_stores.pgvector import PgvectorDocumentStore

from .haystack_adapter import HaystackVectorStoreAdapter

logger = logging.getLogger(__name__)


class PgvectorAdapter(HaystackVectorStoreAdapter):
    """PostgreSQL pgvector implementation using Haystack integration."""

    _instances: dict[str, "PgvectorAdapter"] = {}

    def __new__(
        cls,
        collection: str,
        connection_string: str = "postgresql://postgres:postgres@localhost:5432/postgres",
        **kwargs
    ):
        """Singleton pattern for pgvector adapter."""
        instance_key = f"{collection}:{connection_string}"
        if instance_key in cls._instances:
            return cls._instances[instance_key]

        instance = super().__new__(cls)
        cls._instances[instance_key] = instance
        return instance

    def __init__(
        self,
        collection: str,
        connection_string: str = "postgresql://postgres:postgres@localhost:5432/postgres",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        embedding_dim: int = 384,
        **kwargs
    ):
        """Initialize pgvector adapter.
        
        Args:
            collection: Table name
            connection_string: PostgreSQL connection string
            embedding_model: Embedding model name
            embedding_dim: Embedding dimension
            **kwargs: Additional pgvector parameters
        """
        if hasattr(self, '_initialized'):
            return

        # Create pgvector document store
        # Wrap connection string in Secret object for newer Haystack versions
        connection_secret = Secret.from_token(connection_string) if isinstance(connection_string, str) else connection_string

        document_store = PgvectorDocumentStore(
            connection_string=connection_secret,
            table_name=collection,
            embedding_dimension=embedding_dim,
            vector_function="cosine_similarity",
            recreate_table=kwargs.pop("recreate_table", False),
            search_strategy="exact_nearest_neighbor",  # or "hnsw"
            **{k: v for k, v in kwargs.items() if k not in ["table_name", "embedding_dimension"]}
        )

        super().__init__(
            document_store=document_store,
            collection_name=collection,
            embedding_model=embedding_model,
            embedding_dim=embedding_dim
        )

        self._initialized = True
        self.connection_string = connection_string
        logger.info(f"Pgvector adapter initialized for table: {collection}")

    def get_collection_info(self) -> dict[str, Any]:
        """Get detailed pgvector collection information."""
        info = super().get_collection_info()
        info["backend"] = "pgvector"

        try:
            # Get PostgreSQL-specific info
            import psycopg2
            from psycopg2.extras import RealDictCursor

            # Parse connection string
            conn = psycopg2.connect(self.connection_string)
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # Get table info
            cursor.execute("""
                SELECT 
                    schemaname,
                    tablename,
                    attname,
                    format_type(atttypid, atttypmod) as data_type
                FROM pg_attribute
                JOIN pg_class ON pg_attribute.attrelid = pg_class.oid
                JOIN pg_namespace ON pg_class.relnamespace = pg_namespace.oid
                WHERE tablename = %s
                AND attnum > 0
                ORDER BY attnum;
            """, (self.collection_name,))

            columns = cursor.fetchall()

            # Get row count
            # Note: Table names cannot be parameterized, but collection_name is controlled by the adapter
            cursor.execute(f"SELECT COUNT(*) as count FROM {self.collection_name}")
            row_count = cursor.fetchone()["count"]

            conn.close()

            info.update({
                "connection_string": self.connection_string,
                "table_name": self.collection_name,
                "row_count": row_count,
                "columns": [dict(col) for col in columns],
            })

        except Exception as e:
            logger.error(f"Error getting pgvector collection info: {e}")

        return info

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "PgvectorAdapter":
        """Create pgvector adapter from configuration."""
        return cls(**config)
