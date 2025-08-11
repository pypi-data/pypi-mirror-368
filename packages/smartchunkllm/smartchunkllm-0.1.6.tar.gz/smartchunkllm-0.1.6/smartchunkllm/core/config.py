"""Configuration management for SmartChunkLLM."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import os
import json
from enum import Enum


class LLMProvider(Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    HYBRID = "hybrid"


class EmbeddingProvider(Enum):
    """Supported embedding providers."""
    OPENAI = "openai"
    SENTENCE_TRANSFORMERS = "sentence_transformers"
    OLLAMA = "ollama"
    ENSEMBLE = "ensemble"


class ClusteringMethod(Enum):
    """Supported clustering methods."""
    AGGLOMERATIVE = "agglomerative"
    DBSCAN = "dbscan"
    HDBSCAN = "hdbscan"
    CUSTOM = "custom"
    ENSEMBLE = "ensemble"


@dataclass
class OllamaConfig:
    """Ollama configuration."""
    enabled: bool = True
    host: str = "localhost"
    port: int = 11434
    model: str = "llama3.1"
    embedding_model: str = "nomic-embed-text"
    timeout: int = 300
    auto_pull: bool = True
    use_for_embeddings: bool = True
    use_for_generation: bool = True
    
    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"


@dataclass
class OpenAIConfig:
    """OpenAI configuration."""
    enabled: bool = False
    api_key: Optional[str] = None
    model: str = "gpt-4-turbo-preview"
    embedding_model: str = "text-embedding-3-large"
    max_tokens: int = 4000
    temperature: float = 0.1
    
    def __post_init__(self):
        if not self.api_key:
            self.api_key = os.getenv("OPENAI_API_KEY")


@dataclass
class AnthropicConfig:
    """Anthropic configuration."""
    enabled: bool = False
    api_key: Optional[str] = None
    model: str = "claude-3-sonnet-20240229"
    max_tokens: int = 4000
    temperature: float = 0.1
    
    def __post_init__(self):
        if not self.api_key:
            self.api_key = os.getenv("ANTHROPIC_API_KEY")


@dataclass
class PDFProcessingConfig:
    """PDF processing configuration."""
    use_layout_detection: bool = True
    use_font_analysis: bool = True
    use_ocr: bool = True
    ocr_language: str = "tur+eng"
    extract_images: bool = True
    preserve_formatting: bool = True
    min_text_length: int = 10
    max_text_length: int = 10000


@dataclass
class ChunkingConfig:
    """Chunking configuration."""
    min_chunk_size: int = 100
    max_chunk_size: int = 2000
    overlap_size: int = 200
    use_semantic_splitting: bool = True
    use_sentence_boundaries: bool = True
    preserve_legal_structure: bool = True
    min_importance_score: float = 0.1


@dataclass
class EmbeddingConfig:
    """Embedding configuration."""
    provider: EmbeddingProvider = EmbeddingProvider.ENSEMBLE
    models: List[str] = field(default_factory=lambda: [
        "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
        "sentence-transformers/distiluse-base-multilingual-cased"
    ])
    dimension: int = 768
    normalize: bool = True
    use_ensemble: bool = True
    ensemble_weights: List[float] = field(default_factory=lambda: [0.6, 0.4])


@dataclass
class ClusteringConfig:
    """Clustering configuration."""
    method: ClusteringMethod = ClusteringMethod.ENSEMBLE
    min_cluster_size: int = 3
    max_cluster_size: int = 50
    eps: float = 0.3
    min_samples: int = 2
    linkage: str = "ward"
    distance_threshold: float = 0.5
    use_ensemble: bool = True


@dataclass
class LegalConfig:
    """Legal domain specific configuration."""
    language: str = "turkish"
    legal_system: str = "turkish_law"
    use_legal_nlp: bool = True
    extract_legal_concepts: bool = True
    detect_references: bool = True
    classify_content_types: bool = True
    legal_dictionaries: List[str] = field(default_factory=lambda: [
        "turkish_legal_terms.json",
        "eu_legal_terms.json"
    ])


@dataclass
class QualityConfig:
    """Quality assessment configuration."""
    enable_quality_scoring: bool = True
    min_quality_threshold: float = 0.5
    coherence_weight: float = 0.25
    completeness_weight: float = 0.20
    relevance_weight: float = 0.20
    readability_weight: float = 0.15
    legal_accuracy_weight: float = 0.20


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    format: str = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
    file_path: Optional[str] = None
    max_file_size: str = "10 MB"
    backup_count: int = 3
    enable_console: bool = True


@dataclass
class Config:
    """Main configuration class for SmartChunkLLM."""
    
    # Provider configurations
    ollama: OllamaConfig = field(default_factory=OllamaConfig)
    openai: OpenAIConfig = field(default_factory=OpenAIConfig)
    anthropic: AnthropicConfig = field(default_factory=AnthropicConfig)
    
    # Processing configurations
    pdf_processing: PDFProcessingConfig = field(default_factory=PDFProcessingConfig)
    chunking: ChunkingConfig = field(default_factory=ChunkingConfig)
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    clustering: ClusteringConfig = field(default_factory=ClusteringConfig)
    legal: LegalConfig = field(default_factory=LegalConfig)
    quality: QualityConfig = field(default_factory=QualityConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    # General settings
    primary_provider: LLMProvider = LLMProvider.OLLAMA
    fallback_provider: Optional[LLMProvider] = LLMProvider.OPENAI
    enable_caching: bool = True
    cache_dir: str = ".cache"
    temp_dir: str = ".temp"
    output_dir: str = "output"
    
    # Performance settings
    max_workers: int = 4
    batch_size: int = 10
    enable_gpu: bool = False
    memory_limit_gb: float = 8.0
    
    def __post_init__(self):
        """Post-initialization setup."""
        # Create directories
        for dir_path in [self.cache_dir, self.temp_dir, self.output_dir]:
            Path(dir_path).mkdir(exist_ok=True)
        
        # Validate provider availability
        self._validate_providers()
    
    def _validate_providers(self) -> None:
        """Validate that at least one provider is available."""
        available_providers = []
        
        if self.ollama.enabled:
            available_providers.append(LLMProvider.OLLAMA)
        
        if self.openai.enabled and self.openai.api_key:
            available_providers.append(LLMProvider.OPENAI)
        
        if self.anthropic.enabled and self.anthropic.api_key:
            available_providers.append(LLMProvider.ANTHROPIC)
        
        if not available_providers:
            raise ValueError("No LLM providers are available. Please configure at least one provider.")
        
        # Set primary provider if not available
        if self.primary_provider not in available_providers:
            self.primary_provider = available_providers[0]
    
    @property
    def available_providers(self) -> List[LLMProvider]:
        """Get list of available providers."""
        providers = []
        
        if self.ollama.enabled:
            providers.append(LLMProvider.OLLAMA)
        
        if self.openai.enabled and self.openai.api_key:
            providers.append(LLMProvider.OPENAI)
        
        if self.anthropic.enabled and self.anthropic.api_key:
            providers.append(LLMProvider.ANTHROPIC)
        
        return providers
    
    def get_provider_config(self, provider: LLMProvider) -> Union[OllamaConfig, OpenAIConfig, AnthropicConfig]:
        """Get configuration for specific provider."""
        if provider == LLMProvider.OLLAMA:
            return self.ollama
        elif provider == LLMProvider.OPENAI:
            return self.openai
        elif provider == LLMProvider.ANTHROPIC:
            return self.anthropic
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        def _convert_value(value):
            if hasattr(value, '__dict__'):
                return {k: _convert_value(v) for k, v in value.__dict__.items()}
            elif isinstance(value, Enum):
                return value.value
            elif isinstance(value, list):
                return [_convert_value(item) for item in value]
            else:
                return value
        
        return _convert_value(self)
    
    def to_json(self, indent: int = 2) -> str:
        """Convert config to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    def save(self, file_path: Union[str, Path]) -> None:
        """Save configuration to file."""
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(self.to_json())
    
    @classmethod
    def load(cls, file_path: Union[str, Path]) -> 'Config':
        """Load configuration from file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return cls.from_dict(data)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Config':
        """Create config from dictionary."""
        # Convert nested dictionaries to dataclass instances
        config_data = {}
        
        for key, value in data.items():
            if key == 'ollama' and isinstance(value, dict):
                config_data[key] = OllamaConfig(**value)
            elif key == 'openai' and isinstance(value, dict):
                config_data[key] = OpenAIConfig(**value)
            elif key == 'anthropic' and isinstance(value, dict):
                config_data[key] = AnthropicConfig(**value)
            elif key == 'pdf_processing' and isinstance(value, dict):
                config_data[key] = PDFProcessingConfig(**value)
            elif key == 'chunking' and isinstance(value, dict):
                config_data[key] = ChunkingConfig(**value)
            elif key == 'embedding' and isinstance(value, dict):
                # Handle enum conversion
                if 'provider' in value:
                    value['provider'] = EmbeddingProvider(value['provider'])
                config_data[key] = EmbeddingConfig(**value)
            elif key == 'clustering' and isinstance(value, dict):
                if 'method' in value:
                    value['method'] = ClusteringMethod(value['method'])
                config_data[key] = ClusteringConfig(**value)
            elif key == 'legal' and isinstance(value, dict):
                config_data[key] = LegalConfig(**value)
            elif key == 'quality' and isinstance(value, dict):
                config_data[key] = QualityConfig(**value)
            elif key == 'logging' and isinstance(value, dict):
                config_data[key] = LoggingConfig(**value)
            elif key in ['primary_provider', 'fallback_provider'] and isinstance(value, str):
                config_data[key] = LLMProvider(value) if value else None
            else:
                config_data[key] = value
        
        return cls(**config_data)
    
    @classmethod
    def create_default(cls) -> 'Config':
        """Create default configuration optimized for Turkish legal documents."""
        return cls(
            # Ollama as primary (free, offline)
            primary_provider=LLMProvider.OLLAMA,
            fallback_provider=LLMProvider.OPENAI,
            
            # Optimized for Turkish legal documents
            legal=LegalConfig(
                language="turkish",
                legal_system="turkish_law",
                use_legal_nlp=True,
                extract_legal_concepts=True,
                detect_references=True,
                classify_content_types=True
            ),
            
            # High-quality PDF processing
            pdf_processing=PDFProcessingConfig(
                use_layout_detection=True,
                use_font_analysis=True,
                use_ocr=True,
                ocr_language="tur+eng"
            ),
            
            # Ensemble embeddings for better quality
            embedding=EmbeddingConfig(
                provider=EmbeddingProvider.ENSEMBLE,
                use_ensemble=True
            ),
            
            # Ensemble clustering for robustness
            clustering=ClusteringConfig(
                method=ClusteringMethod.ENSEMBLE,
                use_ensemble=True
            )
        )


# Global default configuration instance
default_config = Config.create_default()

# Alias for backward compatibility
SmartChunkConfig = Config