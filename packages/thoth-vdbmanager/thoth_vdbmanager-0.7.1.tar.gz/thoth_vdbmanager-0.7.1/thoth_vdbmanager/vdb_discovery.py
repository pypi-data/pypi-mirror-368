# Copyright (c) 2025 Marco Pancotti
# This file is part of Thoth and is released under the MIT License.
# See the LICENSE.md file in the project root for full license information.

"""
Plugin discovery system for vector databases.
This module provides dynamic loading and availability checking for vector database backends.
"""

import importlib
from typing import Dict, Any, Optional, List
import warnings
import logging

logger = logging.getLogger(__name__)

# Mapping of vector database backends to their required packages
VECTORDB_DEPENDENCIES = {
    'qdrant': ['qdrant-client', 'haystack-integrations'],
    'chroma': ['chromadb'],
    'pgvector': ['psycopg2', 'pgvector'],
    'milvus': ['pymilvus'],
}

# Mapping of backend names to their adapter classes (from existing structure)
VECTORDB_ADAPTERS = {
    'qdrant': 'thoth_vdbmanager.vdbmanager.adapters.qdrant_adapter.QdrantAdapter',
    'chroma': 'thoth_vdbmanager.vdbmanager.adapters.chroma_adapter.ChromaAdapter',
    'pgvector': 'thoth_vdbmanager.vdbmanager.adapters.pgvector_adapter.PgvectorAdapter',
    'milvus': 'thoth_vdbmanager.vdbmanager.adapters.milvus_adapter.MilvusAdapter',
}


class VectorDbImportError(ImportError):
    """Custom exception for vector database import errors."""
    
    def __init__(self, backend: str, missing_deps: List[str]):
        self.backend = backend
        self.missing_deps = missing_deps
        super().__init__(
            f"Missing dependencies for {backend}: {', '.join(missing_deps)}. "
            f"Install with: pip install thoth-vdbmanager[{backend}]"
        )


def check_dependencies(backend: str) -> List[str]:
    """
    Check if required dependencies for a vector database backend are available.
    
    Args:
        backend: Name of the vector database backend
        
    Returns:
        List of missing dependency names
    """
    if backend not in VECTORDB_DEPENDENCIES:
        raise ValueError(f"Unknown vector database backend: {backend}")
    
    missing_deps = []
    for dep in VECTORDB_DEPENDENCIES[backend]:
        try:
            # Handle package names with hyphens by converting to underscores for import
            import_name = dep.replace('-', '_')
            importlib.import_module(import_name)
        except ImportError:
            missing_deps.append(dep)
    
    # Additional check: try to import the adapter to make sure it actually works
    if not missing_deps and backend in VECTORDB_ADAPTERS:
        try:
            module_path, class_name = VECTORDB_ADAPTERS[backend].rsplit('.', 1)
            module = importlib.import_module(module_path)
            getattr(module, class_name)
        except (ImportError, AttributeError) as e:
            logger.debug(f"Adapter import failed for {backend}: {e}")
            missing_deps.append(f"Functional adapter for {backend}")
    
    return missing_deps


def import_adapter(backend: str) -> Any:
    """
    Dynamically import a vector database adapter class.
    
    Args:
        backend: Name of the vector database backend
        
    Returns:
        The vector database adapter class
        
    Raises:
        VectorDbImportError: If dependencies are missing
        ImportError: If the adapter class cannot be imported
    """
    if backend not in VECTORDB_ADAPTERS:
        raise ValueError(f"Unknown vector database backend: {backend}")
    
    # Check dependencies
    missing_deps = check_dependencies(backend)
    if missing_deps:
        raise VectorDbImportError(backend, missing_deps)
    
    # Import the adapter class
    module_path, class_name = VECTORDB_ADAPTERS[backend].rsplit('.', 1)
    try:
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    except ImportError as e:
        logger.error(f"Failed to import {backend} adapter: {e}")
        raise VectorDbImportError(backend, [f"Module {module_path}"])


def get_available_vectordbs() -> Dict[str, bool]:
    """
    Get a dictionary of available vector database backends and their dependency status.
    
    Returns:
        Dictionary mapping backend names to availability (True if all dependencies are available)
    """
    availability = {}
    for backend in VECTORDB_DEPENDENCIES:
        missing_deps = check_dependencies(backend)
        availability[backend] = len(missing_deps) == 0
        
        if missing_deps:
            logger.debug(f"Vector database backend '{backend}' unavailable - missing dependencies: {missing_deps}")
        else:
            logger.debug(f"Vector database backend '{backend}' available")
    
    return availability


def get_vectordb_info(backend: Optional[str] = None) -> Dict[str, Any]:
    """
    Get information about vector database backends.
    
    Args:
        backend: Specific backend name, or None for all backends
        
    Returns:
        Backend information dictionary
    """
    if backend:
        if backend not in VECTORDB_DEPENDENCIES:
            raise ValueError(f"Unknown vector database backend: {backend}")
        
        missing_deps = check_dependencies(backend)
        return {
            "backend": backend,
            "available": len(missing_deps) == 0,
            "required_dependencies": VECTORDB_DEPENDENCIES[backend],
            "missing_dependencies": missing_deps,
            "adapter_class": VECTORDB_ADAPTERS.get(backend, "Unknown")
        }
    else:
        # Return info for all backends
        availability = get_available_vectordbs()
        return {
            backend: {
                "available": availability[backend],
                "required_dependencies": VECTORDB_DEPENDENCIES[backend],
                "missing_dependencies": check_dependencies(backend),
                "adapter_class": VECTORDB_ADAPTERS.get(backend, "Unknown")
            }
            for backend in VECTORDB_DEPENDENCIES
        }


def validate_backend(backend: str) -> bool:
    """
    Check if a vector database backend is supported and available.
    
    Args:
        backend: Backend name to validate
        
    Returns:
        True if backend is supported and available, False otherwise
    """
    if backend not in VECTORDB_DEPENDENCIES:
        return False
    
    missing_deps = check_dependencies(backend)
    return len(missing_deps) == 0


def import_vectordb_components(backends: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    Import components for specified vector database backends.
    
    Args:
        backends: List of backend names to import
        
    Returns:
        Dictionary mapping backend names to their components
    """
    components = {}
    
    for backend in backends:
        try:
            components[backend] = {
                'adapter': import_adapter(backend),
                'available': True
            }
        except VectorDbImportError as e:
            warnings.warn(str(e))
            components[backend] = {
                'adapter': None,
                'available': False,
                'error': str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error importing {backend}: {e}")
            components[backend] = {
                'adapter': None,
                'available': False,
                'error': str(e)
            }
    
    return components


# Convenience functions for common use cases
def import_qdrant():
    """Import Qdrant components."""
    result = import_vectordb_components(['qdrant'])
    return result['qdrant'] if result['qdrant']['available'] else None

def import_chroma():
    """Import Chroma components."""
    result = import_vectordb_components(['chroma'])
    return result['chroma'] if result['chroma']['available'] else None

def import_pgvector():
    """Import PgVector components."""
    result = import_vectordb_components(['pgvector'])
    return result['pgvector'] if result['pgvector']['available'] else None

def import_milvus():
    """Import Milvus components."""
    result = import_vectordb_components(['milvus'])
    return result['milvus'] if result['milvus']['available'] else None


def list_available_backends() -> List[str]:
    """
    List all available vector database backends.
    
    Returns:
        List of available backend names
    """
    availability = get_available_vectordbs()
    return [backend for backend, available in availability.items() if available]


def list_all_backends() -> List[str]:
    """
    List all supported vector database backends.
    
    Returns:
        List of all backend names
    """
    return list(VECTORDB_DEPENDENCIES.keys())