"""Core components for the Thoth Vector Database Manager."""

from .embedding_manager import (
    MultilingualEmbeddingManager,
    get_multilingual_embedding_manager,
    EmbeddingInitializationError,
)
from .embedding_provider import (
    EmbeddingProvider,
    OpenAIEmbeddingProvider,
    CohereEmbeddingProvider,
    MistralEmbeddingProvider,
    HuggingFaceEmbeddingProvider,
    EmbeddingProviderFactory,
)
from .external_embedding_manager import (
    ExternalEmbeddingManager,
    EmbeddingCache,
    get_external_embedding_manager,
)

__all__ = [
    # Legacy embedding manager (sentence-transformers based)
    'MultilingualEmbeddingManager',
    'get_multilingual_embedding_manager', 
    'EmbeddingInitializationError',
    # External embedding providers
    'EmbeddingProvider',
    'OpenAIEmbeddingProvider',
    'CohereEmbeddingProvider',
    'MistralEmbeddingProvider',
    'HuggingFaceEmbeddingProvider',
    'EmbeddingProviderFactory',
    # External embedding manager
    'ExternalEmbeddingManager',
    'EmbeddingCache',
    'get_external_embedding_manager',
]
