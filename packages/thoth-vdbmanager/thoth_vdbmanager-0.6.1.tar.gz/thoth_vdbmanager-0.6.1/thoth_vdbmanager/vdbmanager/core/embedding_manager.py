# Copyright (c) 2025 Marco Pancotti
# This file is part of Thoth and is released under the MIT License.
# See the LICENSE.md file in the project root for full license information.

"""Multilingual Embedding Manager for Thoth Vector Database."""

import logging
import os
import warnings
from typing import List, Dict, Any, Optional
from pathlib import Path

from haystack.components.embedders import (
    SentenceTransformersDocumentEmbedder,
    SentenceTransformersTextEmbedder,
)
from haystack.dataclasses import Document as HaystackDocument
from haystack.utils import ComponentDevice

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
        
        # Configura variabili ambiente per Hugging Face cache
        self._setup_cache_environment()
        
        # Docker-native initialization (NO WORKAROUNDS)
        self._document_embedder: Optional[SentenceTransformersDocumentEmbedder] = None
        self._text_embedder: Optional[SentenceTransformersTextEmbedder] = None
        self._initialized = False
        
        logger.info(f"MultilingualEmbeddingManager created: {self.model_name}")
        logger.info(f"Cache directory: {self.cache_dir}")
        logger.info(f"Docker environment: {self._is_docker_environment()}")
    
    def _get_default_cache_dir(self) -> str:
        """Configura cache directory standard di Hugging Face."""
        # Usa la cache standard di Hugging Face
        cache_dir = os.path.expanduser("~/.cache/huggingface")
        return cache_dir
    
    def _setup_cache_environment(self):
        """Configura variabili ambiente per ottimizzare l'uso della cache."""
        # Usa la cache standard di Hugging Face
        hf_home = os.environ.get('HF_HOME', os.path.expanduser("~/.cache/huggingface"))
        st_home = os.environ.get('SENTENCE_TRANSFORMERS_HOME', os.path.expanduser("~/.cache/sentence-transformers"))
        
        os.environ.setdefault('HF_HOME', hf_home)
        os.environ.setdefault('TRANSFORMERS_CACHE', os.path.join(hf_home, 'transformers'))
        os.environ.setdefault('SENTENCE_TRANSFORMERS_HOME', st_home)
        
        # Verifica se i modelli sono già cached
        if self._is_model_cached(self.model_name):
            logger.info(f"Model {self.model_name} found in cache at {st_home}")
        else:
            logger.info(f"Model {self.model_name} not in cache, will download on first use")
    
    def _is_model_cached(self, model_name: str) -> bool:
        """Verifica se un modello è già presente nella cache locale."""
        # Controlla nella cache di sentence-transformers
        st_cache = os.path.expanduser("~/.cache/sentence-transformers")
        model_path = os.path.join(st_cache, model_name.replace('/', '_'))
        
        if os.path.exists(model_path):
            # Verifica che ci siano effettivamente i file del modello
            has_model_files = any(
                fname.endswith(('.bin', '.safetensors', '.onnx')) 
                for fname in os.listdir(model_path) 
                if os.path.isfile(os.path.join(model_path, fname))
            ) if os.path.isdir(model_path) else False
            return has_model_files
        
        # Controlla anche nella cache di Hugging Face
        hf_cache = os.path.expanduser("~/.cache/huggingface/hub")
        if os.path.exists(hf_cache):
            # Il nome nella cache HF è diverso, include un hash
            for item in os.listdir(hf_cache):
                if model_name.replace('/', '--') in item:
                    return True
        
        return False
    
    def _is_docker_environment(self) -> bool:
        """Rileva se siamo in ambiente Docker (per retrocompatibilità)."""
        return os.environ.get('DOCKER_ENV') == '1' or os.path.exists('/.dockerenv')
    
    def _initialize_embedders(self):
        """Inizializzazione robusta per ambiente Docker e locale."""
        if self._initialized:
            return
            
        logger.info(f"Initializing embedders for model: {self.model_name}")
        
        try:
            # Configurazione ottimizzata per Docker e locale
            embedder_config = {
                'model': self.model_name,
                'trust_remote_code': False,  # Evita download di codice remoto
            }
            
            # Auto-detect device se non specificato
            if 'device' not in embedder_config:
                try:
                    import torch
                    if torch.cuda.is_available():
                        embedder_config['device'] = ComponentDevice.from_str('cuda')
                        logger.info("GPU available - using CUDA")
                    else:
                        embedder_config['device'] = ComponentDevice.from_str('cpu')
                        logger.info("Using CPU for embeddings")
                except ImportError:
                    embedder_config['device'] = ComponentDevice.from_str('cpu')
                    logger.info("Using CPU for embeddings (torch not available)")
            
            logger.debug(f"Embedder config: {embedder_config}")
            
            # Haystack embedders con configurazione Docker-ready
            self._document_embedder = SentenceTransformersDocumentEmbedder(**embedder_config)
            self._text_embedder = SentenceTransformersTextEmbedder(**embedder_config)
            
            # Warm-up con gestione errori
            logger.info(f"Warming up document embedder for model: {self.model_name}")
            try:
                self._document_embedder.warm_up()
                logger.info("Document embedder ready")
            except Exception as e:
                logger.error(f"Failed to warm up document embedder: {e}")
                raise
            
            logger.info(f"Warming up text embedder for model: {self.model_name}")
            try:
                self._text_embedder.warm_up()
                logger.info("Text embedder ready")
            except Exception as e:
                logger.error(f"Failed to warm up text embedder: {e}")
                raise
            
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
    def clear_cache(cls) -> None:
        """Pulisce la cache dei modelli singleton."""
        cls._initialized_models.clear()
        logger.info("Model cache cleared")
    
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