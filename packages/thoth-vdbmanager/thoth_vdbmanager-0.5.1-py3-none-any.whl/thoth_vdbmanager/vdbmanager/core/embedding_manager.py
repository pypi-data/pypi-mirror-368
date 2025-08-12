# Copyright (c) 2025 Marco Pancotti
# This file is part of Thoth and is released under the MIT License.
# See the LICENSE.md file in the project root for full license information.

"""Multilingual Embedding Manager for Thoth Vector Database."""

import logging
import os
from typing import List, Dict, Any, Optional
from pathlib import Path

from haystack.components.embedders import (
    SentenceTransformersDocumentEmbedder,
    SentenceTransformersTextEmbedder,
)
from haystack.dataclasses import Document as HaystackDocument

from .base import BaseThothDocument, ThothType

logger = logging.getLogger(__name__)


class EmbeddingInitializationError(Exception):
    """Exception raised when embedding initialization fails."""
    pass


class MultilingualEmbeddingManager:
    """Gestore centralizzato per embedding multilingua con supporto Docker nativo.
    
    Gestisce l'inizializzazione e l'uso di modelli di embedding multilingua
    con supporto nativo per ambienti Docker e locali, senza workaround.
    """
    
    # Configurazione modelli multilingua
    MULTILINGUAL_MODELS = {
        "default": "paraphrase-multilingual-MiniLM-L12-v2",  # 384d, 50+ lingue, bilanciato
        "large": "paraphrase-multilingual-mpnet-base-v2",     # 768d, performance superiore
        "fast": "distiluse-base-multilingual-cased",          # 512d, veloce
        "legacy": "sentence-transformers/all-MiniLM-L6-v2"    # 384d, principalmente inglese
    }
    
    # Singleton pattern per evitare reinizializzazioni multiple
    _instance = None
    _initialized_models = {}
    
    def __new__(cls, model_name: str = "default", cache_dir: Optional[str] = None):
        """Singleton pattern per evitare inizializzazioni multiple dello stesso modello."""
        cache_key = f"{model_name}_{cache_dir}"
        if cache_key not in cls._initialized_models:
            instance = super().__new__(cls)
            cls._initialized_models[cache_key] = instance
            return instance
        return cls._initialized_models[cache_key]
    
    def __init__(self, model_name: str = "default", cache_dir: Optional[str] = None):
        """Initialize the multilingual embedding manager.
        
        Args:
            model_name: Nome del modello o chiave da MULTILINGUAL_MODELS
            cache_dir: Directory per cache modelli (auto-detect se None)
        """
        # Evita reinizializzazione del singleton
        if hasattr(self, '_initialized'):
            return
            
        self.model_name = self.MULTILINGUAL_MODELS.get(model_name, model_name)
        self.model_key = model_name
        self.cache_dir = cache_dir or self._get_default_cache_dir()
        
        # Assicura che la cache directory esista
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Docker-native initialization (NO WORKAROUNDS)
        self._document_embedder: Optional[SentenceTransformersDocumentEmbedder] = None
        self._text_embedder: Optional[SentenceTransformersTextEmbedder] = None
        self._initialized = False
        
        logger.info(f"MultilingualEmbeddingManager created: {self.model_name}")
        logger.info(f"Cache directory: {self.cache_dir}")
        logger.info(f"Docker environment: {self._is_docker_environment()}")
    
    def _get_default_cache_dir(self) -> str:
        """Configura cache directory ottimizzata per Docker e locale."""
        if self._is_docker_environment():
            # Directory standard per containers Docker
            cache_dir = "/app/.embeddings_cache"
        else:
            # Directory utente per sviluppo locale
            cache_dir = os.path.expanduser("~/.thoth/embeddings_cache")
        
        return cache_dir
    
    def _is_docker_environment(self) -> bool:
        """Rileva ambiente Docker senza assumere configurazioni speciali."""
        # Metodo 1: File .dockerenv (standard Docker)
        if os.path.exists('/.dockerenv'):
            return True
            
        # Metodo 2: Controllo cgroup (backup)
        try:
            if os.path.exists('/proc/1/cgroup'):
                with open('/proc/1/cgroup', 'r') as f:
                    content = f.read()
                    if 'docker' in content or 'containerd' in content:
                        return True
        except (IOError, OSError):
            pass
            
        # Metodo 3: Variabile ambiente comune
        if os.environ.get('DOCKER_ENV') == '1':
            return True
            
        return False
    
    def _initialize_embedders(self):
        """Inizializzazione robusta per ambiente Docker e locale."""
        if self._initialized:
            return
            
        logger.info(f"Initializing embedders for model: {self.model_name}")
        
        try:
            # Configurazione unificata (Docker + locale)
            embedder_config = {
                'model': self.model_name,
                'model_kwargs': {
                    'cache_dir': self.cache_dir,
                }
            }
            
            logger.debug(f"Embedder config: {embedder_config}")
            
            # Haystack embedders con configurazione Docker-ready
            self._document_embedder = SentenceTransformersDocumentEmbedder(**embedder_config)
            self._text_embedder = SentenceTransformersTextEmbedder(**embedder_config)
            
            # Warm-up sincronizzato
            logger.info("Warming up document embedder...")
            self._document_embedder.warm_up()
            
            logger.info("Warming up text embedder...")
            self._text_embedder.warm_up()
            
            self._initialized = True
            logger.info(f"Embedding manager initialized successfully: {self.model_name} (multilingual)")
            
        except Exception as e:
            logger.error(f"Embedding initialization failed: {e}", exc_info=True)
            raise EmbeddingInitializationError(f"Failed to initialize multilingual embedder: {e}") from e
    
    def get_document_embedder(self) -> SentenceTransformersDocumentEmbedder:
        """Get or create document embedder."""
        self._initialize_embedders()
        return self._document_embedder
    
    def get_text_embedder(self) -> SentenceTransformersTextEmbedder:
        """Get or create text embedder."""
        self._initialize_embedders()
        return self._text_embedder
    
    def encode_documents(self, documents: List[HaystackDocument]) -> List[HaystackDocument]:
        """Encoding documenti con supporto multilingua automatico.
        
        Args:
            documents: Lista di documenti Haystack da embedare
            
        Returns:
            Lista di documenti con embeddings calcolati
        """
        if not documents:
            return []
            
        logger.debug(f"Encoding {len(documents)} documents with multilingual model")
        
        embedder = self.get_document_embedder()
        result = embedder.run(documents=documents)
        
        embedded_docs = result["documents"]
        logger.debug(f"Successfully encoded {len(embedded_docs)} documents")
        
        return embedded_docs
    
    def encode_query(self, query: str) -> List[float]:
        """Encoding query multilingua.
        
        Args:
            query: Testo della query in qualsiasi lingua supportata
            
        Returns:
            Vettore embedding della query
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
            
        logger.debug(f"Encoding query: '{query[:50]}{'...' if len(query) > 50 else ''}'")
        
        embedder = self.get_text_embedder()
        result = embedder.run(text=query.strip())
        
        embedding = result["embedding"]
        logger.debug(f"Query encoded to {len(embedding)}-dimensional vector")
        
        return embedding
    
    def get_model_info(self) -> Dict[str, Any]:
        """Informazioni sul modello corrente."""
        return {
            "model_name": self.model_name,
            "model_key": self.model_key,
            "cache_dir": self.cache_dir,
            "is_docker": self._is_docker_environment(),
            "initialized": self._initialized,
            "supports_multilingual": True,
            "embedding_dimension": self._get_embedding_dimension()
        }
    
    def _get_embedding_dimension(self) -> int:
        """Ottiene la dimensione degli embedding del modello."""
        dimension_map = {
            "paraphrase-multilingual-MiniLM-L12-v2": 384,
            "paraphrase-multilingual-mpnet-base-v2": 768,
            "distiluse-base-multilingual-cased": 512,
            "sentence-transformers/all-MiniLM-L6-v2": 384
        }
        return dimension_map.get(self.model_name, 384)  # Default 384
    
    @classmethod
    def get_available_models(cls) -> Dict[str, str]:
        """Lista dei modelli disponibili."""
        return cls.MULTILINGUAL_MODELS.copy()
    
    @classmethod
    def preload_model(cls, model_name: str = "default", cache_dir: Optional[str] = None) -> bool:
        """Pre-carica un modello (utile per Docker build).
        
        Args:
            model_name: Nome del modello da pre-caricare
            cache_dir: Directory cache (auto-detect se None)
            
        Returns:
            True se il pre-caricamento è riuscito
        """
        try:
            logger.info(f"Pre-loading model: {model_name}")
            manager = cls(model_name=model_name, cache_dir=cache_dir)
            manager._initialize_embedders()
            logger.info(f"Model {model_name} pre-loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to pre-load model {model_name}: {e}")
            return False


# Factory function per compatibility
def get_multilingual_embedding_manager(model_name: str = "default", cache_dir: Optional[str] = None) -> MultilingualEmbeddingManager:
    """Factory function per ottenere un embedding manager multilingua."""
    return MultilingualEmbeddingManager(model_name=model_name, cache_dir=cache_dir)