"""Core components for the Thoth Vector Database Manager."""

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
