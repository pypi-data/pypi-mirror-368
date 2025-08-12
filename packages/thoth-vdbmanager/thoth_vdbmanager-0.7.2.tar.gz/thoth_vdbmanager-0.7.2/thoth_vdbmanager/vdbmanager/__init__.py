"""Thoth Vector Database Manager - Haystack-based implementation."""

from .core.base import (
    BaseThothDocument,
    ColumnNameDocument,
    EvidenceDocument,
    SqlDocument,
    ThothType,
    VectorStoreInterface,
)
from .factory import VectorStoreFactory

# Adapters are loaded dynamically by VectorStoreFactory to handle missing dependencies

__version__ = "2.0.0"
__all__ = [
    # Core classes
    "BaseThothDocument",
    "ColumnNameDocument",
    "EvidenceDocument",
    "SqlDocument",
    "ThothType",
    "VectorStoreInterface",

    # Factory
    "VectorStoreFactory",
]
