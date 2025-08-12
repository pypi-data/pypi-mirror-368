# Copyright (c) 2025 Marco Pancotti
# This file is part of Thoth and is released under the MIT License.
# See the LICENSE.md file in the project root for full license information.

"""External embedding providers for thoth-vdbmanager v0.6.0."""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class EmbeddingProvider(ABC):
    """Abstract interface for external embedding providers."""
    
    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for list of texts."""
        pass
    
    @abstractmethod
    def embed_query(self, query: str) -> List[float]:
        """Generate embedding for single query."""
        pass
    
    @abstractmethod
    async def embed_texts_async(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings async for list of texts."""
        pass
    
    @abstractmethod
    def validate_connection(self) -> bool:
        """Test connection and API key validity."""
        pass
    
    @abstractmethod
    def get_dimensions(self) -> int:
        """Return embedding dimensions for the model."""
        pass
    
    @property
    @abstractmethod
    def max_batch_size(self) -> int:
        """Maximum batch size for provider."""
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Provider name for logging/metrics."""
        pass


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """OpenAI embedding provider implementation."""
    
    def __init__(self, api_key: str, model: str = "text-embedding-3-small", 
                 base_url: Optional[str] = None, timeout: int = 30):
        """Initialize OpenAI provider."""
        if not api_key:
            raise ValueError("OpenAI API key is required")
        
        try:
            from openai import OpenAI
        except ImportError as e:
            raise ImportError("OpenAI library not installed. Install with: pip install openai>=1.0.0") from e
        
        self.client = OpenAI(api_key=api_key, base_url=base_url, timeout=timeout)
        self.model = model
        self.timeout = timeout
        self._dimensions: Optional[int] = None
        self._validate_model()
    
    def _validate_model(self):
        """Validate that the model exists."""
        valid_models = [
            "text-embedding-3-small", 
            "text-embedding-3-large", 
            "text-embedding-ada-002"
        ]
        if self.model not in valid_models:
            raise ValueError(f"Model {self.model} not supported. Valid models: {valid_models}")
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Implement batch embedding with retry logic."""
        if not texts:
            return []
        
        # Batch processing to respect rate limits
        batches = [texts[i:i + self.max_batch_size] 
                  for i in range(0, len(texts), self.max_batch_size)]
        
        all_embeddings = []
        for batch in batches:
            try:
                response = self.client.embeddings.create(
                    input=batch,
                    model=self.model
                )
                batch_embeddings = [embedding.embedding for embedding in response.data]
                all_embeddings.extend(batch_embeddings)
                
                # Rate limiting - respect OpenAI limits
                time.sleep(0.1)
                
            except Exception as e:
                raise RuntimeError(f"OpenAI embedding failed: {e}")
        
        return all_embeddings
    
    def embed_query(self, query: str) -> List[float]:
        """Embed single query."""
        return self.embed_texts([query])[0]
    
    async def embed_texts_async(self, texts: List[str]) -> List[List[float]]:
        """Async implementation for better performance."""
        return await asyncio.to_thread(self.embed_texts, texts)
    
    def validate_connection(self) -> bool:
        """Validate connection to OpenAI."""
        try:
            test_embedding = self.embed_texts(["test"])
            return len(test_embedding) > 0 and len(test_embedding[0]) > 0
        except Exception as e:
            logger.warning(f"OpenAI connection validation failed: {e}")
            return False
    
    def get_dimensions(self) -> int:
        """Get embedding dimensions."""
        if self._dimensions is None:
            test_embedding = self.embed_texts(["dimension test"])
            self._dimensions = len(test_embedding[0])
        return self._dimensions
    
    @property
    def max_batch_size(self) -> int:
        return 2048  # OpenAI limit
    
    @property
    def provider_name(self) -> str:
        return "openai"


class CohereEmbeddingProvider(EmbeddingProvider):
    """Cohere embedding provider implementation."""
    
    def __init__(self, api_key: str, model: str = "embed-multilingual-v3.0"):
        """Initialize Cohere provider."""
        if not api_key:
            raise ValueError("Cohere API key is required")
        
        try:
            import cohere
        except ImportError as e:
            raise ImportError("Cohere library not installed. Install with: pip install cohere>=4.0.0") from e
        
        self.client = cohere.Client(api_key=api_key)
        self.model = model
        self._dimensions: Optional[int] = None
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed texts with Cohere."""
        try:
            response = self.client.embed(
                texts=texts,
                model=self.model,
                input_type="search_document"
            )
            return response.embeddings
        except Exception as e:
            raise RuntimeError(f"Cohere embedding failed: {e}")
    
    def embed_query(self, query: str) -> List[float]:
        """Embed query with Cohere."""
        try:
            response = self.client.embed(
                texts=[query],
                model=self.model,
                input_type="search_query"
            )
            return response.embeddings[0]
        except Exception as e:
            raise RuntimeError(f"Cohere query embedding failed: {e}")
    
    async def embed_texts_async(self, texts: List[str]) -> List[List[float]]:
        """Async implementation."""
        return await asyncio.to_thread(self.embed_texts, texts)
    
    def validate_connection(self) -> bool:
        """Validate connection to Cohere."""
        try:
            test_embedding = self.embed_texts(["test"])
            return len(test_embedding) > 0 and len(test_embedding[0]) > 0
        except Exception as e:
            logger.warning(f"Cohere connection validation failed: {e}")
            return False
    
    def get_dimensions(self) -> int:
        """Get embedding dimensions."""
        if self._dimensions is None:
            test_embedding = self.embed_texts(["dimension test"])
            self._dimensions = len(test_embedding[0])
        return self._dimensions
    
    @property
    def max_batch_size(self) -> int:
        return 96  # Cohere limit
    
    @property
    def provider_name(self) -> str:
        return "cohere"


class MistralEmbeddingProvider(EmbeddingProvider):
    """Mistral AI embedding provider implementation."""
    
    def __init__(self, api_key: str, model: str = "mistral-embed"):
        """Initialize Mistral provider."""
        if not api_key:
            raise ValueError("Mistral API key is required")
        
        try:
            from mistralai.client import MistralClient
        except ImportError as e:
            raise ImportError("Mistral library not installed. Install with: pip install mistralai>=0.1.0") from e
        
        self.client = MistralClient(api_key=api_key)
        self.model = model
        self._dimensions: Optional[int] = None
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed texts with Mistral."""
        try:
            response = self.client.embeddings(
                model=self.model,
                input=texts
            )
            return [embedding.embedding for embedding in response.data]
        except Exception as e:
            raise RuntimeError(f"Mistral embedding failed: {e}")
    
    def embed_query(self, query: str) -> List[float]:
        """Embed query with Mistral."""
        return self.embed_texts([query])[0]
    
    async def embed_texts_async(self, texts: List[str]) -> List[List[float]]:
        """Async implementation."""
        return await asyncio.to_thread(self.embed_texts, texts)
    
    def validate_connection(self) -> bool:
        """Validate connection to Mistral."""
        try:
            test_embedding = self.embed_texts(["test"])
            return len(test_embedding) > 0 and len(test_embedding[0]) > 0
        except Exception as e:
            logger.warning(f"Mistral connection validation failed: {e}")
            return False
    
    def get_dimensions(self) -> int:
        """Get embedding dimensions."""
        if self._dimensions is None:
            test_embedding = self.embed_texts(["dimension test"])
            self._dimensions = len(test_embedding[0])
        return self._dimensions
    
    @property
    def max_batch_size(self) -> int:
        return 1000  # Mistral estimate
    
    @property
    def provider_name(self) -> str:
        return "mistral"


class HuggingFaceEmbeddingProvider(EmbeddingProvider):
    """HuggingFace Inference API embedding provider implementation."""
    
    def __init__(self, api_token: str, model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """Initialize HuggingFace provider."""
        if not api_token:
            raise ValueError("HuggingFace API token is required")
        
        try:
            import requests
        except ImportError as e:
            raise ImportError("Requests library not installed. Install with: pip install requests>=2.25.0") from e
        
        self.api_token = api_token
        self.model = model
        self.api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{model}"
        self.headers = {"Authorization": f"Bearer {api_token}"}
        self._dimensions: Optional[int] = None
        
        # Import requests for use in methods
        self.requests = requests
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed texts with HuggingFace."""
        try:
            response = self.requests.post(
                self.api_url,
                headers=self.headers,
                json={"inputs": texts, "options": {"wait_for_model": True}}
            )
            response.raise_for_status()
            embeddings = response.json()
            
            # HuggingFace can return different formats
            if isinstance(embeddings[0], list):
                return embeddings
            else:
                return [embeddings]
                
        except Exception as e:
            raise RuntimeError(f"HuggingFace embedding failed: {e}")
    
    def embed_query(self, query: str) -> List[float]:
        """Embed query with HuggingFace."""
        return self.embed_texts([query])[0]
    
    async def embed_texts_async(self, texts: List[str]) -> List[List[float]]:
        """Async implementation."""
        return await asyncio.to_thread(self.embed_texts, texts)
    
    def validate_connection(self) -> bool:
        """Validate connection to HuggingFace."""
        try:
            test_embedding = self.embed_texts(["test"])
            return len(test_embedding) > 0 and len(test_embedding[0]) > 0
        except Exception as e:
            logger.warning(f"HuggingFace connection validation failed: {e}")
            return False
    
    def get_dimensions(self) -> int:
        """Get embedding dimensions."""
        if self._dimensions is None:
            test_embedding = self.embed_texts(["dimension test"])
            self._dimensions = len(test_embedding[0])
        return self._dimensions
    
    @property
    def max_batch_size(self) -> int:
        return 100  # Conservative for HF
    
    @property
    def provider_name(self) -> str:
        return "huggingface"


class EmbeddingProviderFactory:
    """Factory for creating embedding providers."""
    
    @staticmethod
    def create_provider(provider_type: str, **kwargs) -> EmbeddingProvider:
        """Create embedding provider instance."""
        provider_map = {
            'openai': OpenAIEmbeddingProvider,
            'cohere': CohereEmbeddingProvider,
            'mistral': MistralEmbeddingProvider,
            'huggingface': HuggingFaceEmbeddingProvider,
        }
        
        if provider_type not in provider_map:
            raise ValueError(f"Provider {provider_type} not supported. "
                           f"Available: {list(provider_map.keys())}")
        
        provider_class = provider_map[provider_type]
        return provider_class(**kwargs)
    
    @staticmethod
    def get_supported_providers() -> List[str]:
        """Get list of supported providers."""
        return ['openai', 'cohere', 'mistral', 'huggingface']