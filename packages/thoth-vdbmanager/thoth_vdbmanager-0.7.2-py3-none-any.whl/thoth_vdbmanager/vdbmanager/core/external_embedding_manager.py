# Copyright (c) 2025 Marco Pancotti
# This file is part of Thoth and is released under the MIT License.
# See the LICENSE.md file in the project root for full license information.

"""External Embedding Manager for Thoth Vector Database v0.6.0."""

import hashlib
import logging
import os
from typing import Any, Dict, List, Optional

from haystack.dataclasses import Document as HaystackDocument

from .base import BaseThothDocument
from .embedding_provider import EmbeddingProvider, EmbeddingProviderFactory

logger = logging.getLogger(__name__)


class EmbeddingCache:
    """Simple in-memory embedding cache."""
    
    def __init__(self, max_size: int = 10000):
        self._cache: Dict[str, List[float]] = {}
        self.max_size = max_size
    
    def get_cache_key(self, text: str, model: str) -> str:
        """Generate cache key for text and model combination."""
        return hashlib.md5(f"{text}:{model}".encode()).hexdigest()
    
    def get(self, text: str, model: str) -> Optional[List[float]]:
        """Get embedding from cache."""
        key = self.get_cache_key(text, model)
        return self._cache.get(key)
    
    def set(self, text: str, model: str, embedding: List[float]):
        """Store embedding in cache."""
        if len(self._cache) >= self.max_size:
            # Simple LRU eviction - remove oldest entry
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
        
        key = self.get_cache_key(text, model)
        self._cache[key] = embedding


class ExternalEmbeddingManager:
    """External embedding manager for thoth-vdbmanager v0.6.0.
    
    Replaces sentence-transformers with external API providers.
    Provides compatibility layer for existing Haystack-based adapters.
    """
    
    def __init__(self, provider: EmbeddingProvider, enable_cache: bool = True, cache_size: int = 10000):
        """Initialize external embedding manager.
        
        Args:
            provider: External embedding provider instance
            enable_cache: Enable embedding caching
            cache_size: Maximum cache size
        """
        self.provider = provider
        self.enable_cache = enable_cache
        self.cache = EmbeddingCache(cache_size) if enable_cache else None
        
        # Validate provider connection
        if not self.provider.validate_connection():
            raise ConnectionError(f"Failed to connect to {self.provider.provider_name} embedding service")
        
        logger.info(f"ExternalEmbeddingManager initialized with {self.provider.provider_name} provider")
        logger.info(f"Model: {getattr(self.provider, 'model', 'unknown')}")
        logger.info(f"Dimensions: {self.provider.get_dimensions()}")
        logger.info(f"Max batch size: {self.provider.max_batch_size}")
        logger.info(f"Cache enabled: {self.enable_cache}")
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> 'ExternalEmbeddingManager':
        """Create manager from configuration.
        
        Args:
            config: Configuration dictionary with provider settings
            
        Returns:
            ExternalEmbeddingManager instance
            
        Example:
            config = {
                'provider': 'openai',
                'api_key': 'sk-...',
                'model': 'text-embedding-3-small',
                'enable_cache': True,
                'cache_size': 10000
            }
        """
        provider_config = config.copy()
        provider_type = provider_config.pop('provider')
        
        # Extract manager-specific settings
        enable_cache = provider_config.pop('enable_cache', True)
        cache_size = provider_config.pop('cache_size', 10000)
        
        # Create provider with remaining config
        provider = EmbeddingProviderFactory.create_provider(provider_type, **provider_config)
        
        return cls(provider=provider, enable_cache=enable_cache, cache_size=cache_size)
    
    @classmethod
    def from_env(cls) -> 'ExternalEmbeddingManager':
        """Create manager from environment variables.
        
        Expected environment variables:
        - EMBEDDING_PROVIDER: openai, cohere, mistral, huggingface
        - EMBEDDING_MODEL: model name
        - EMBEDDING_API_KEY: API key
        - EMBEDDING_CACHE_SIZE: cache size (optional, default 10000)
        
        Returns:
            ExternalEmbeddingManager instance
        """
        provider_type = os.environ.get('EMBEDDING_PROVIDER')
        if not provider_type:
            raise ValueError("EMBEDDING_PROVIDER environment variable is required")
        
        api_key = os.environ.get('EMBEDDING_API_KEY')
        if not api_key:
            raise ValueError("EMBEDDING_API_KEY environment variable is required")
        
        model = os.environ.get('EMBEDDING_MODEL', cls._get_default_model(provider_type))
        cache_size = int(os.environ.get('EMBEDDING_CACHE_SIZE', '10000'))
        
        config = {
            'provider': provider_type,
            'api_key': api_key,
            'model': model,
            'cache_size': cache_size
        }
        
        return cls.from_config(config)
    
    @staticmethod
    def _get_default_model(provider_type: str) -> str:
        """Get default model for provider."""
        defaults = {
            'openai': 'text-embedding-3-small',
            'cohere': 'embed-multilingual-v3.0',
            'mistral': 'mistral-embed',
            'huggingface': 'sentence-transformers/all-MiniLM-L6-v2'
        }
        return defaults.get(provider_type, 'default')
    
    def encode_documents(self, documents: List[HaystackDocument]) -> List[HaystackDocument]:
        """Encode Haystack documents with embeddings.
        
        Provides compatibility with existing Haystack-based adapters.
        
        Args:
            documents: List of Haystack documents
            
        Returns:
            List of documents with embeddings attached
        """
        if not documents:
            return []
        
        logger.debug(f"Encoding {len(documents)} documents with {self.provider.provider_name}")
        
        # Extract text content from documents
        texts = [doc.content or "" for doc in documents]
        
        # Get embeddings with caching
        embeddings = self._get_embeddings_with_cache(texts)
        
        # Attach embeddings to documents
        for doc, embedding in zip(documents, embeddings):
            doc.embedding = embedding
        
        logger.debug(f"Successfully encoded {len(documents)} documents")
        return documents
    
    def encode_query(self, query: str) -> List[float]:
        """Encode single query text.
        
        Args:
            query: Query text
            
        Returns:
            Query embedding vector
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        logger.debug(f"Encoding query: '{query[:50]}{'...' if len(query) > 50 else ''}'")
        
        # Use cache if enabled
        if self.enable_cache and self.cache:
            cached = self.cache.get(query.strip(), self._get_model_identifier())
            if cached:
                logger.debug("Using cached query embedding")
                return cached
        
        # Get embedding from provider
        embedding = self.provider.embed_query(query.strip())
        
        # Cache if enabled
        if self.enable_cache and self.cache:
            self.cache.set(query.strip(), self._get_model_identifier(), embedding)
        
        logger.debug(f"Query encoded to {len(embedding)}-dimensional vector")
        return embedding
    
    def _get_embeddings_with_cache(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings with caching support."""
        if not self.enable_cache or not self.cache:
            return self.provider.embed_texts(texts)
        
        model_id = self._get_model_identifier()
        cached_embeddings = []
        uncached_texts = []
        uncached_indices = []
        
        # Check cache for each text
        for i, text in enumerate(texts):
            cached = self.cache.get(text, model_id)
            if cached:
                cached_embeddings.append((i, cached))
            else:
                uncached_texts.append(text)
                uncached_indices.append(i)
        
        # Get embeddings for uncached texts
        if uncached_texts:
            new_embeddings = self.provider.embed_texts(uncached_texts)
            
            # Cache new embeddings
            for text, embedding in zip(uncached_texts, new_embeddings):
                self.cache.set(text, model_id, embedding)
        else:
            new_embeddings = []
        
        # Combine cached and new embeddings in correct order
        all_embeddings = [None] * len(texts)
        
        # Place cached embeddings
        for idx, embedding in cached_embeddings:
            all_embeddings[idx] = embedding
        
        # Place new embeddings
        for uncached_idx, embedding in zip(uncached_indices, new_embeddings):
            all_embeddings[uncached_idx] = embedding
        
        logger.debug(f"Used cache for {len(cached_embeddings)} embeddings, "
                    f"computed {len(new_embeddings)} new embeddings")
        
        return all_embeddings
    
    def _get_model_identifier(self) -> str:
        """Get model identifier for caching."""
        return f"{self.provider.provider_name}:{getattr(self.provider, 'model', 'default')}"
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        return {
            "provider_name": self.provider.provider_name,
            "model_name": getattr(self.provider, 'model', 'unknown'),
            "embedding_dimension": self.provider.get_dimensions(),
            "max_batch_size": self.provider.max_batch_size,
            "cache_enabled": self.enable_cache,
            "cache_size": len(self.cache._cache) if self.cache else 0,
            "supports_multilingual": True,  # Most external providers support multilingual
            "is_external": True
        }
    
    async def encode_texts_async(self, texts: List[str]) -> List[List[float]]:
        """Async version of text encoding."""
        return await self.provider.embed_texts_async(texts)
    
    def clear_cache(self):
        """Clear embedding cache."""
        if self.cache:
            self.cache._cache.clear()
            logger.info("Embedding cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if not self.cache:
            return {"cache_enabled": False}
        
        return {
            "cache_enabled": True,
            "cache_size": len(self.cache._cache),
            "max_cache_size": self.cache.max_size,
            "cache_usage_percent": (len(self.cache._cache) / self.cache.max_size) * 100
        }


# Compatibility function for existing code
def get_external_embedding_manager(config: Dict[str, Any]) -> ExternalEmbeddingManager:
    """Factory function for external embedding manager.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        ExternalEmbeddingManager instance
    """
    return ExternalEmbeddingManager.from_config(config)