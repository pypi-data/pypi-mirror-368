"""Advanced embedding generation with ensemble support."""

from typing import Dict, List, Optional, Any, Union, Tuple
from abc import ABC, abstractmethod
import logging
import numpy as np
from dataclasses import dataclass
from pathlib import Path
import pickle
import hashlib

# Sentence Transformers
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logging.warning("sentence-transformers not available")

# OpenAI
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("openai not available")

# Ollama
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    logging.warning("ollama not available")

# Scientific computing
try:
    from sklearn.preprocessing import normalize
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("scikit-learn not available")

from ..core.config import EmbeddingConfig, OllamaConfig, OpenAIConfig


@dataclass
class EmbeddingResult:
    """Result of embedding generation."""
    embeddings: np.ndarray
    model_name: str
    dimension: int
    processing_time: float
    metadata: Dict[str, Any]


class EmbeddingGeneratorBase(ABC):
    """Base class for embedding generators."""
    
    def __init__(self, config: EmbeddingConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model_name = ""
        self.dimension = 0
    
    @abstractmethod
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a list of texts."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the embedding generator is available."""
        pass
    
    def generate_single_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for a single text."""
        return self.generate_embeddings([text])[0]


class SentenceTransformerEmbedding(EmbeddingGeneratorBase):
    """Embedding generator using Sentence Transformers."""
    
    def __init__(self, config: EmbeddingConfig, model_name: str = None):
        super().__init__(config)
        self.model_name = model_name or config.models[0] if config.models else "paraphrase-multilingual-mpnet-base-v2"
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the sentence transformer model."""
        if not self.is_available():
            raise RuntimeError("sentence-transformers is not available")
        
        try:
            self.logger.info(f"Loading SentenceTransformer model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            self.dimension = self.model.get_sentence_embedding_dimension()
            self.logger.info(f"Model loaded successfully, dimension: {self.dimension}")
        except Exception as e:
            self.logger.error(f"Failed to load model {self.model_name}: {e}")
            raise
    
    def is_available(self) -> bool:
        return SENTENCE_TRANSFORMERS_AVAILABLE
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings using SentenceTransformer."""
        if not self.model:
            self._load_model()
        
        try:
            # Generate embeddings
            embeddings = self.model.encode(
                texts,
                convert_to_numpy=True,
                normalize_embeddings=self.config.normalize,
                show_progress_bar=len(texts) > 100
            )
            
            return embeddings
        
        except Exception as e:
            self.logger.error(f"Failed to generate embeddings: {e}")
            raise


class OpenAIEmbedding(EmbeddingGeneratorBase):
    """Embedding generator using OpenAI API."""
    
    def __init__(self, config: EmbeddingConfig, openai_config: OpenAIConfig):
        super().__init__(config)
        self.openai_config = openai_config
        self.model_name = openai_config.embedding_model
        self.dimension = 3072 if "large" in self.model_name else 1536  # OpenAI embedding dimensions
        
        if openai_config.api_key:
            openai.api_key = openai_config.api_key
    
    def is_available(self) -> bool:
        return OPENAI_AVAILABLE and self.openai_config.api_key is not None
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings using OpenAI API."""
        if not self.is_available():
            raise RuntimeError("OpenAI API is not available or API key not set")
        
        try:
            # OpenAI has a limit on batch size, so we process in chunks
            batch_size = 100
            all_embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                
                response = openai.embeddings.create(
                    model=self.model_name,
                    input=batch_texts
                )
                
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)
            
            embeddings = np.array(all_embeddings)
            
            if self.config.normalize:
                embeddings = normalize(embeddings, norm='l2')
            
            return embeddings
        
        except Exception as e:
            self.logger.error(f"Failed to generate OpenAI embeddings: {e}")
            raise


class OllamaEmbedding(EmbeddingGeneratorBase):
    """Embedding generator using Ollama."""
    
    def __init__(self, config: EmbeddingConfig, ollama_config: OllamaConfig):
        super().__init__(config)
        self.ollama_config = ollama_config
        self.model_name = ollama_config.embedding_model
        self.dimension = 768  # Default dimension, will be updated after first call
        
        # Configure Ollama client
        if self.is_available():
            self._setup_client()
    
    def _setup_client(self):
        """Setup Ollama client."""
        try:
            # Check if model is available
            models = ollama.list()
            available_models = [model['name'] for model in models['models']]
            
            if self.model_name not in available_models:
                if self.ollama_config.auto_pull:
                    self.logger.info(f"Pulling Ollama model: {self.model_name}")
                    ollama.pull(self.model_name)
                else:
                    raise RuntimeError(f"Ollama model {self.model_name} not available")
        
        except Exception as e:
            self.logger.error(f"Failed to setup Ollama client: {e}")
            raise
    
    def is_available(self) -> bool:
        return OLLAMA_AVAILABLE and self.ollama_config.enabled
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings using Ollama."""
        if not self.is_available():
            raise RuntimeError("Ollama is not available")
        
        try:
            embeddings = []
            
            for text in texts:
                response = ollama.embeddings(
                    model=self.model_name,
                    prompt=text
                )
                
                embedding = response['embedding']
                embeddings.append(embedding)
            
            embeddings = np.array(embeddings)
            
            # Update dimension if this is the first call
            if self.dimension != embeddings.shape[1]:
                self.dimension = embeddings.shape[1]
                self.logger.info(f"Updated Ollama embedding dimension to {self.dimension}")
            
            if self.config.normalize:
                embeddings = normalize(embeddings, norm='l2')
            
            return embeddings
        
        except Exception as e:
            self.logger.error(f"Failed to generate Ollama embeddings: {e}")
            raise


class EnsembleEmbedding:
    """Ensemble embedding generator combining multiple models."""
    
    def __init__(self, config: EmbeddingConfig, ollama_config: OllamaConfig = None, openai_config: OpenAIConfig = None):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize available generators
        self.generators = []
        self.weights = []
        
        # Add SentenceTransformer generators
        if SENTENCE_TRANSFORMERS_AVAILABLE and config.models:
            for i, model_name in enumerate(config.models):
                try:
                    generator = SentenceTransformerEmbedding(config, model_name)
                    self.generators.append(generator)
                    
                    # Use provided weights or equal weights
                    weight = config.ensemble_weights[i] if i < len(config.ensemble_weights) else 1.0
                    self.weights.append(weight)
                    
                    self.logger.info(f"Added SentenceTransformer: {model_name} (weight: {weight})")
                except Exception as e:
                    self.logger.warning(f"Failed to load SentenceTransformer {model_name}: {e}")
        
        # Add Ollama generator
        if ollama_config and ollama_config.enabled and ollama_config.use_for_embeddings:
            try:
                generator = OllamaEmbedding(config, ollama_config)
                if generator.is_available():
                    self.generators.append(generator)
                    self.weights.append(0.3)  # Default weight for Ollama
                    self.logger.info(f"Added Ollama embedding: {ollama_config.embedding_model}")
            except Exception as e:
                self.logger.warning(f"Failed to load Ollama embedding: {e}")
        
        # Add OpenAI generator
        if openai_config and openai_config.enabled:
            try:
                generator = OpenAIEmbedding(config, openai_config)
                if generator.is_available():
                    self.generators.append(generator)
                    self.weights.append(0.4)  # Default weight for OpenAI
                    self.logger.info(f"Added OpenAI embedding: {openai_config.embedding_model}")
            except Exception as e:
                self.logger.warning(f"Failed to load OpenAI embedding: {e}")
        
        if not self.generators:
            raise RuntimeError("No embedding generators are available")
        
        # Normalize weights
        total_weight = sum(self.weights)
        self.weights = [w / total_weight for w in self.weights]
        
        self.logger.info(f"Ensemble initialized with {len(self.generators)} generators")
    
    def generate_embeddings(self, texts: List[str]) -> EmbeddingResult:
        """Generate ensemble embeddings."""
        import time
        start_time = time.time()
        
        if not self.config.use_ensemble or len(self.generators) == 1:
            # Use single best generator
            generator = self.generators[0]
            embeddings = generator.generate_embeddings(texts)
            
            return EmbeddingResult(
                embeddings=embeddings,
                model_name=generator.model_name,
                dimension=generator.dimension,
                processing_time=time.time() - start_time,
                metadata={"ensemble": False, "generators": 1}
            )
        
        # Generate embeddings from all generators
        all_embeddings = []
        successful_generators = []
        successful_weights = []
        
        for i, generator in enumerate(self.generators):
            try:
                embeddings = generator.generate_embeddings(texts)
                all_embeddings.append(embeddings)
                successful_generators.append(generator)
                successful_weights.append(self.weights[i])
                
                self.logger.debug(f"Generated embeddings using {generator.model_name}")
            
            except Exception as e:
                self.logger.warning(f"Generator {generator.model_name} failed: {e}")
        
        if not all_embeddings:
            raise RuntimeError("All embedding generators failed")
        
        # Normalize weights for successful generators
        total_weight = sum(successful_weights)
        successful_weights = [w / total_weight for w in successful_weights]
        
        # Combine embeddings using weighted average
        ensemble_embeddings = self._combine_embeddings(all_embeddings, successful_weights)
        
        # Determine ensemble dimension
        ensemble_dimension = ensemble_embeddings.shape[1]
        
        return EmbeddingResult(
            embeddings=ensemble_embeddings,
            model_name="ensemble",
            dimension=ensemble_dimension,
            processing_time=time.time() - start_time,
            metadata={
                "ensemble": True,
                "generators": len(successful_generators),
                "generator_names": [g.model_name for g in successful_generators],
                "weights": successful_weights
            }
        )
    
    def _combine_embeddings(self, embeddings_list: List[np.ndarray], weights: List[float]) -> np.ndarray:
        """Combine multiple embeddings using weighted average."""
        if not embeddings_list:
            raise ValueError("No embeddings to combine")
        
        # Check if all embeddings have the same dimension
        dimensions = [emb.shape[1] for emb in embeddings_list]
        
        if len(set(dimensions)) == 1:
            # Same dimension - simple weighted average
            combined = np.zeros_like(embeddings_list[0])
            
            for embeddings, weight in zip(embeddings_list, weights):
                combined += weight * embeddings
        
        else:
            # Different dimensions - need to handle carefully
            self.logger.warning("Embeddings have different dimensions, using concatenation")
            combined = np.concatenate(embeddings_list, axis=1)
        
        # Normalize if required
        if self.config.normalize:
            combined = normalize(combined, norm='l2')
        
        return combined
    
    def get_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate cosine similarity between two embeddings."""
        if not SKLEARN_AVAILABLE:
            # Manual cosine similarity calculation
            dot_product = np.dot(embedding1, embedding2)
            norm1 = np.linalg.norm(embedding1)
            norm2 = np.linalg.norm(embedding2)
            return dot_product / (norm1 * norm2)
        
        return cosine_similarity([embedding1], [embedding2])[0][0]
    
    def get_available_generators(self) -> List[str]:
        """Get list of available generator names."""
        return [generator.model_name for generator in self.generators]


class EmbeddingGenerator:
    """Main embedding generator with caching support."""
    
    def __init__(self, config: EmbeddingConfig, ollama_config: OllamaConfig = None, openai_config: OpenAIConfig = None, cache_dir: str = ".cache"):
        self.config = config
        self.cache_dir = Path(cache_dir) / "embeddings"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize ensemble embedding generator
        self.ensemble = EnsembleEmbedding(config, ollama_config, openai_config)
    
    def generate_embeddings(self, texts: List[str], use_cache: bool = True) -> EmbeddingResult:
        """Generate embeddings with optional caching."""
        if use_cache:
            # Check cache first
            cache_key = self._get_cache_key(texts)
            cached_result = self._load_from_cache(cache_key)
            
            if cached_result:
                self.logger.debug(f"Loaded embeddings from cache: {cache_key}")
                return cached_result
        
        # Generate new embeddings
        result = self.ensemble.generate_embeddings(texts)
        
        if use_cache:
            # Save to cache
            self._save_to_cache(cache_key, result)
        
        return result
    
    def _get_cache_key(self, texts: List[str]) -> str:
        """Generate cache key for texts."""
        # Create hash of texts and configuration
        text_hash = hashlib.md5("\n".join(texts).encode()).hexdigest()
        config_hash = hashlib.md5(str(self.config.to_dict()).encode()).hexdigest()[:8]
        
        return f"{text_hash}_{config_hash}"
    
    def _save_to_cache(self, cache_key: str, result: EmbeddingResult) -> None:
        """Save embedding result to cache."""
        try:
            cache_file = self.cache_dir / f"{cache_key}.pkl"
            
            with open(cache_file, 'wb') as f:
                pickle.dump(result, f)
            
            self.logger.debug(f"Saved embeddings to cache: {cache_key}")
        
        except Exception as e:
            self.logger.warning(f"Failed to save to cache: {e}")
    
    def _load_from_cache(self, cache_key: str) -> Optional[EmbeddingResult]:
        """Load embedding result from cache."""
        try:
            cache_file = self.cache_dir / f"{cache_key}.pkl"
            
            if cache_file.exists():
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
        
        except Exception as e:
            self.logger.warning(f"Failed to load from cache: {e}")
        
        return None
    
    def clear_cache(self) -> None:
        """Clear embedding cache."""
        try:
            for cache_file in self.cache_dir.glob("*.pkl"):
                cache_file.unlink()
            
            self.logger.info("Embedding cache cleared")
        
        except Exception as e:
            self.logger.error(f"Failed to clear cache: {e}")
    
    def get_cache_size(self) -> int:
        """Get number of cached embeddings."""
        return len(list(self.cache_dir.glob("*.pkl")))