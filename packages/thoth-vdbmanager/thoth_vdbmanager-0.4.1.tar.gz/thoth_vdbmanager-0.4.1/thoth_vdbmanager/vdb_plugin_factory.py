# Copyright (c) 2025 Marco Pancotti
# This file is part of Thoth and is released under the MIT License.
# See the LICENSE.md file in the project root for full license information.

"""
Plugin-aware factory for creating vector store instances with dynamic discovery.
"""

import logging
from typing import Any, Dict, List, Optional

from .vdb_discovery import (
    get_available_vectordbs,
    validate_backend,
    import_adapter,
    get_vectordb_info,
    VectorDbImportError
)
from .vdbmanager.core.base import VectorStoreInterface

logger = logging.getLogger(__name__)


class ThothVectorStoreFactory:
    """
    Plugin-aware factory for creating vector store instances.
    Provides plugin-based instantiation with automatic discovery.
    """
    
    _initialized = False
    _available_backends = {}
    
    @classmethod
    def _initialize_plugins(cls):
        """Initialize plugin discovery and check available backends."""
        if cls._initialized:
            return
            
        try:
            cls._available_backends = get_available_vectordbs()
            available_list = [backend for backend, available in cls._available_backends.items() if available]
            unavailable_list = [backend for backend, available in cls._available_backends.items() if not available]
            
            if available_list:
                logger.info(f"Available vector database backends: {', '.join(available_list)}")
            if unavailable_list:
                logger.info(f"Unavailable vector database backends (missing dependencies): {', '.join(unavailable_list)}")
                
            cls._initialized = True
            
        except Exception as e:
            logger.error(f"Error initializing vector database plugins: {str(e)}")
            cls._available_backends = {}
    
    @staticmethod
    def create(
        backend: str,
        collection: str,
        **kwargs
    ) -> VectorStoreInterface:
        """
        Create a vector store instance using the plugin discovery system.
        
        Args:
            backend: Backend type (qdrant, chroma, pgvector, milvus)
            collection: Collection/table/index name
            **kwargs: Backend-specific connection parameters
            
        Returns:
            Vector store instance
            
        Raises:
            ValueError: If backend is not supported or available
            RuntimeError: If plugin initialization fails
        """
        try:
            # Initialize plugins if not already done
            ThothVectorStoreFactory._initialize_plugins()
            
            # Validate backend availability
            if not validate_backend(backend):
                available_backends = ThothVectorStoreFactory.list_available_backends()
                raise ValueError(
                    f"Backend '{backend}' is not supported or available. "
                    f"Available backends: {available_backends}"
                )
            
            # Import and create adapter
            adapter_class = import_adapter(backend)
            vector_store = adapter_class(collection=collection, **kwargs)
            
            logger.info(f"Successfully created {backend} vector store for collection: {collection}")
            return vector_store
            
        except VectorDbImportError as e:
            logger.error(f"Failed to import {backend} backend: {e}")
            raise ValueError(f"Backend '{backend}' dependencies not available: {e.missing_deps}")
        except Exception as e:
            logger.error(f"Failed to create {backend} vector store: {e}")
            raise RuntimeError(f"Failed to create {backend} vector store: {e}") from e
    
    @staticmethod
    def from_config(config: Dict[str, Any]) -> VectorStoreInterface:
        """
        Create vector store from configuration dictionary.
        
        Args:
            config: Configuration dictionary containing all parameters
            
        Returns:
            Vector store instance
            
        Example config:
            {
                "backend": "qdrant",
                "collection": "my_collection",
                "host": "localhost",
                "port": 6333,
                "api_key": None
            }
        """
        # Extract factory parameters
        config_copy = config.copy()  # Don't modify the original config
        backend = config_copy.pop("backend")
        collection = config_copy.pop("collection", None)
        
        if not collection:
            raise ValueError("Configuration must include 'collection' parameter")
        
        # Remaining parameters are connection parameters
        return ThothVectorStoreFactory.create(
            backend=backend,
            collection=collection,
            **config_copy
        )
    
    @staticmethod
    def list_backends() -> List[str]:
        """
        List all supported vector database backends.
        
        Returns:
            List of all supported backend identifiers
        """
        ThothVectorStoreFactory._initialize_plugins()
        return list(ThothVectorStoreFactory._available_backends.keys())
    
    @staticmethod
    def list_available_backends() -> List[str]:
        """
        List available vector database backends (with dependencies installed).
        
        Returns:
            List of available backend identifiers
        """
        ThothVectorStoreFactory._initialize_plugins()
        return [
            backend for backend, available 
            in ThothVectorStoreFactory._available_backends.items() 
            if available
        ]
    
    @staticmethod
    def get_backend_info(backend: Optional[str] = None) -> Dict[str, Any]:
        """
        Get information about vector database backends.
        
        Args:
            backend: Specific backend name, or None for all
            
        Returns:
            Backend information dictionary
        """
        ThothVectorStoreFactory._initialize_plugins()
        return get_vectordb_info(backend)
    
    @staticmethod
    def validate_backend(backend: str) -> bool:
        """
        Check if a vector database backend is supported and available.
        
        Args:
            backend: Backend identifier
            
        Returns:
            True if supported and available, False otherwise
        """
        ThothVectorStoreFactory._initialize_plugins()
        return validate_backend(backend)
    
    @staticmethod
    def get_required_parameters(backend: str) -> Dict[str, Any]:
        """
        Get required connection parameters for a backend.
        
        Args:
            backend: Backend identifier
            
        Returns:
            Dictionary describing required parameters
        """
        ThothVectorStoreFactory._initialize_plugins()
        
        if not validate_backend(backend):
            return {
                "error": f"Backend '{backend}' not supported or available",
                "available_backends": ThothVectorStoreFactory.list_available_backends()
            }
        
        # Define common parameters based on backend type
        common_params = {
            "qdrant": {
                "required": ["collection"],
                "optional": ["host", "port", "api_key", "url", "embedding_model", "embedding_dim"]
            },
            "chroma": {
                "required": ["collection"],
                "optional": ["path", "host", "port", "embedding_model", "embedding_dim"]
            },
            "pgvector": {
                "required": ["collection", "host", "database", "user", "password"],
                "optional": ["port", "schema", "embedding_model", "embedding_dim"]
            },
            "milvus": {
                "required": ["collection"],
                "optional": ["host", "port", "user", "password", "embedding_model", "embedding_dim"]
            }
        }
        
        return common_params.get(backend, {
            "required": ["collection"],
            "optional": [],
            "note": f"Parameters for {backend} not defined. Check adapter documentation."
        })
    
    @staticmethod
    def create_with_validation(backend: str, collection: str, **kwargs) -> VectorStoreInterface:
        """
        Create a vector store with parameter validation.
        
        Args:
            backend: Backend identifier
            collection: Collection name
            **kwargs: Connection parameters
            
        Returns:
            Vector store instance
            
        Raises:
            ValueError: If parameters are invalid
            RuntimeError: If creation fails
        """
        # Validate backend
        if not ThothVectorStoreFactory.validate_backend(backend):
            available = ThothVectorStoreFactory.list_available_backends()
            raise ValueError(f"Unsupported or unavailable backend '{backend}'. Available: {available}")
        
        # Get required parameters
        param_info = ThothVectorStoreFactory.get_required_parameters(backend)
        
        if "required" in param_info:
            # Check required parameters (collection is already provided)
            missing_params = []
            for param in param_info["required"]:
                if param != "collection" and param not in kwargs:
                    missing_params.append(param)
            
            if missing_params:
                raise ValueError(f"Missing required parameters for {backend}: {missing_params}")
        
        # Create the vector store
        return ThothVectorStoreFactory.create(backend, collection, **kwargs)
    
    @staticmethod
    def get_plugin_status() -> Dict[str, Any]:
        """
        Get status information about all vector database backends.
        
        Returns:
            Status information for all backends
        """
        ThothVectorStoreFactory._initialize_plugins()
        backends = ThothVectorStoreFactory.list_backends()
        available_backends = ThothVectorStoreFactory.list_available_backends()
        
        status = {
            "total_backends": len(backends),
            "available_backends": available_backends,
            "unavailable_backends": [b for b in backends if b not in available_backends],
            "backends": {}
        }
        
        for backend in backends:
            try:
                backend_info = ThothVectorStoreFactory.get_backend_info(backend)
                status["backends"][backend] = {
                    "status": "available" if backend_info["available"] else "unavailable",
                    "info": backend_info
                }
            except Exception as e:
                status["backends"][backend] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return status


# Backward compatibility - create an alias to the old factory
VectorStoreFactory = ThothVectorStoreFactory