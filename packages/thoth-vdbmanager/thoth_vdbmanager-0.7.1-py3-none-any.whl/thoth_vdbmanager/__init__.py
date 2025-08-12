from .vdbmanager import (
    BaseThothDocument,
    ColumnNameDocument,
    EvidenceDocument,
    SqlDocument,
    ThothType,
    VectorStoreInterface,
)

# Import the new plugin-aware factory
from .vdb_plugin_factory import ThothVectorStoreFactory, VectorStoreFactory

# Import plugin discovery functions
from .vdb_discovery import (
    get_available_vectordbs,
    validate_backend,
    get_vectordb_info,
    list_available_backends,
    list_all_backends,
)

# Import plugin initialization
from .initialize_vdb_plugins import initialize_vectordb_plugins

# Import external embedding classes (new in v0.6.0)
from .vdbmanager.core.embedding_provider import (
    EmbeddingProvider,
    OpenAIEmbeddingProvider,
    CohereEmbeddingProvider,
    MistralEmbeddingProvider,
    HuggingFaceEmbeddingProvider,
    EmbeddingProviderFactory,
)
from .vdbmanager.core.external_embedding_manager import (
    ExternalEmbeddingManager,
    EmbeddingCache,
    get_external_embedding_manager,
)
from .vdbmanager.external_factory import ExternalVectorStoreFactory

__all__ = [
    # Core interfaces and documents
    "BaseThothDocument",
    "ColumnNameDocument", 
    "EvidenceDocument",
    "SqlDocument",
    "ThothType",
    "VectorStoreInterface",
    
    # Factories
    "VectorStoreFactory",  # Backward compatibility
    "ThothVectorStoreFactory",  # New plugin-aware factory
    "ExternalVectorStoreFactory",  # External embedding factory (new in v0.6.0)
    
    # Plugin discovery functions
    "get_available_vectordbs",
    "validate_backend", 
    "get_vectordb_info",
    "list_available_backends",
    "list_all_backends",
    "initialize_vectordb_plugins",
    
    # External embedding providers (new in v0.6.0)
    "EmbeddingProvider",
    "OpenAIEmbeddingProvider",
    "CohereEmbeddingProvider",
    "MistralEmbeddingProvider",
    "HuggingFaceEmbeddingProvider",
    "EmbeddingProviderFactory",
    
    # External embedding manager (new in v0.6.0)
    "ExternalEmbeddingManager",
    "EmbeddingCache",
    "get_external_embedding_manager",
]
