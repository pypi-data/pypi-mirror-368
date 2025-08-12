"""Core components for the Thoth Vector Database Manager."""

from .embedding_manager import (
    MultilingualEmbeddingManager,
    get_multilingual_embedding_manager,
    EmbeddingInitializationError,
)

__all__ = [
    'MultilingualEmbeddingManager',
    'get_multilingual_embedding_manager', 
    'EmbeddingInitializationError',
]
