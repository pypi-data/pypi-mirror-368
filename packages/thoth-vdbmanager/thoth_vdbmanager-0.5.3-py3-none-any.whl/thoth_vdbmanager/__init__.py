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
    
    # Plugin discovery functions
    "get_available_vectordbs",
    "validate_backend", 
    "get_vectordb_info",
    "list_available_backends",
    "list_all_backends",
    "initialize_vectordb_plugins",
]
