"""SmartChunkLLM - Intelligent document chunking for LLM applications.

A comprehensive system for processing documents, extracting semantic chunks,
and optimizing content for Large Language Model applications with support
for Turkish legal documents and advanced AI-powered analysis.
"""

__version__ = "0.1.6"
__author__ = "SmartChunkLLM Team"
__email__ = "contact@smartchunkllm.com"
__description__ = "Advanced document processing and intelligent chunking system for LLM applications"
__license__ = "MIT"
__url__ = "https://github.com/smartchunkllm/smartchunkllm"

# Core imports
from .core.types import (
    SemanticChunk,
    ChunkMetadata,
    DocumentMetadata,
    ProcessingMetadata,
    ChunkingStrategy,
    QualityLevel
)
from .core.config import SmartChunkConfig
from .core.exceptions import (
    SmartChunkError,
    PDFProcessingError,
    EmbeddingError,
    ClusteringError,
    LLMError,
    ValidationError
)
from .core.processor import SmartChunkProcessor

# Main processor
from .processor import (
    SmartChunkLLM,
    ProcessingOptions,
    ProcessingStats,
    ProcessingResult,
    create_processor,
    process_legal_pdf,
    process_legal_text
)

# Main processor class definition
class SmartChunkLLM:
    """Main SmartChunkLLM processor class."""
    
    def __init__(
        self,
        strategy: str = "fixed_size",
        quality_level: str = "medium",
        chunk_size: int = 800,
        overlap: int = 150,
        language: str = "tr",
        **kwargs
    ):
        """Initialize SmartChunkLLM.
        
        Args:
            strategy: Chunking strategy to use
            quality_level: Quality level for processing
            chunk_size: Target chunk size in characters
            overlap: Overlap between chunks in characters
            language: Language code (default: "tr" for Turkish)
            **kwargs: Additional configuration options
        """
        self.strategy = strategy
        self.quality_level = quality_level
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.language = language
        self.config = kwargs
        
        # Initialize the core processor
        self.processor = SmartChunkProcessor(
            strategy=strategy,
            quality_level=quality_level,
            chunk_size=chunk_size,
            overlap=overlap,
            language=language,
            **kwargs
        )
        
    def process_pdf(self, file_path: str):
        """Process PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            ProcessingResult containing chunks and metrics
        """
        # TODO: Implement PDF processing
        return self.processor.process_pdf(file_path)
        
    def process_text(self, text: str):
        """Process text.
        
        Args:
            text: Input text to process
            
        Returns:
            ProcessingResult containing chunks and metrics
        """
        return self.processor.process_text(text)

# PDF processing
from .pdf.extractor import PDFExtractor
from .pdf.font import FontAnalyzer, HierarchyLevel, FontCharacteristics
from .pdf.layout import LayoutAnalyzer
from .pdf.ocr import OCRProcessor
from .pdf.structure import StructureDetector

# AI/ML components
from .ai.embeddings import (
    EmbeddingGenerator,
    EmbeddingResult,
    SentenceTransformerEmbedding,
    OpenAIEmbedding,
    OllamaEmbedding,
    EnsembleEmbedding
)
from .ai.clustering import (
    SemanticClusterer,
    ClusteringResult,
    ClusteringMethod,
    AgglomerativeClusterer,
    DBSCANClusterer,
    HDBSCANClusterer,
    AdaptiveClusterer,
    EnsembleClusterer
)
from .ai.transformers import (
    TransformerManager,
    ContentClassifier,
    ClassificationResult
)
from .ai.quality import QualityAssessor

# LLM components
from .llm.providers import (
    LLMManager,
    LLMProvider,
    OpenAIProvider,
    AnthropicProvider,
    OllamaProvider,
    LLMResponse,
    LLMRequest
)
from .llm.prompts import (
    PromptManager,
    PromptTemplate,
    PromptType
)
from .llm.processors import (
    LLMProcessor,
    ChunkProcessor,
    AnalysisProcessor,
    ClassificationProcessor,
    QualityProcessor
)

# Legal domain
from .legal.processor import LegalDocumentProcessor
from .legal.analyzer import (
    LegalAnalyzer,
    LegalElementType,
    LegalElement,
    LegalReference,
    LegalStructure
)
from .legal.validator import (
    LegalValidator,
    ValidationSeverity,
    ValidationCategory,
    ValidationIssue,
    ValidationResult
)

# Convenience imports for common use cases
from .processor import SmartChunkLLM as Processor
from .processor import process_legal_pdf as process_pdf
from .processor import process_legal_text as process_text

# All exports
__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__description__",
    
    # Main class
    "SmartChunkLLM",
    
    # Core types
    "SemanticChunk",
    "ChunkMetadata",
    "DocumentMetadata",
    "ProcessingMetadata",
    "SmartChunkConfig",
    "ChunkingStrategy",
    "QualityLevel",
    
    # Utility functions
    "get_system_info",
    "check_dependencies",
    
    # Core processors
    "SmartChunkProcessor",
    
    # Exceptions
    "SmartChunkError",
    "PDFProcessingError",
    "EmbeddingError",
    "ClusteringError",
    "LLMError",
    "ValidationError",
    
    # Main processor
    "Processor",
    "ProcessingOptions",
    "ProcessingStats",
    "ProcessingResult",
    "create_processor",
    "process_legal_pdf",
    "process_legal_text",
    "process_pdf",
    "process_text",
    
    # PDF processing
    "PDFExtractor",
    "FontAnalyzer",
    "HierarchyLevel",
    "FontCharacteristics",
    "LayoutAnalyzer",
    "OCRProcessor",
    "StructureDetector",
    
    # AI/ML components
    "EmbeddingGenerator",
    "EmbeddingResult",
    "SentenceTransformerEmbedding",
    "OpenAIEmbedding",
    "OllamaEmbedding",
    "EnsembleEmbedding",
    "SemanticClusterer",
    "ClusteringResult",
    "ClusteringMethod",
    "AgglomerativeClusterer",
    "DBSCANClusterer",
    "HDBSCANClusterer",
    "AdaptiveClusterer",
    "EnsembleClusterer",
    "TransformerManager",
    "ContentClassifier",
    "ClassificationResult",
    "QualityAssessor",
    
    # LLM components
    "LLMManager",
    "LLMProvider",
    "OpenAIProvider",
    "AnthropicProvider",
    "OllamaProvider",
    "LLMResponse",
    "LLMRequest",
    "PromptManager",
    "PromptTemplate",
    "PromptType",
    "LLMProcessor",
    "ChunkProcessor",
    "AnalysisProcessor",
    "ClassificationProcessor",
    "QualityProcessor",
    
    # Legal domain
    "LegalDocumentProcessor",
    "LegalAnalyzer",
    "LegalElementType",
    "LegalElement",
    "LegalReference",
    "LegalStructure",
    "LegalValidator",
    "ValidationSeverity",
    "ValidationCategory",
    "ValidationIssue",
    "ValidationResult",
]


# Package metadata
PACKAGE_INFO = {
    "name": "smartchunkllm",
    "version": __version__,
    "description": __description__,
    "author": __author__,
    "python_requires": ">=3.8",
    "keywords": [
        "legal", "documents", "semantic", "chunking", "nlp", 
        "ai", "llm", "pdf", "turkish", "law", "embedding", 
        "clustering", "transformers", "ollama", "openai"
    ],
    "classifiers": [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Legal Industry",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Office/Business :: Legal",
    ]
}


def get_version() -> str:
    """Get package version."""
    return __version__


def get_package_info() -> dict:
    """Get package information."""
    return PACKAGE_INFO.copy()


def get_system_info() -> dict:
    """Get system information and dependencies status."""
    return {
        "version": __version__,
        "python_version": ">=3.8",
        "dependencies": {
            "required": ["torch", "transformers", "sentence-transformers", "scikit-learn"],
            "optional": ["openai", "anthropic", "ollama"]
        }
    }


def check_dependencies() -> dict:
    """Check if dependencies are installed."""
    import importlib
    
    dependencies = {
        "torch": False,
        "transformers": False,
        "sentence_transformers": False,
        "sklearn": False,
        "openai": False,
        "anthropic": False,
        "ollama": False
    }
    
    for dep in dependencies:
        try:
            importlib.import_module(dep)
            dependencies[dep] = True
        except ImportError:
            pass
    
    return dependencies


def print_info():
    """Print package information."""
    print(f"SmartChunkLLM v{__version__}")
    print(f"Author: {__author__}")
    print(f"Description: {__description__}")
    print("\nFeatures:")
    print("  • Advanced PDF processing with layout detection")
    print("  • Font-based hierarchy analysis")
    print("  • Multi-modal AI embeddings")
    print("  • Ensemble clustering algorithms")
    print("  • LLM integration (OpenAI, Anthropic, Ollama)")
    print("  • Turkish legal document support")
    print("  • Quality assessment and validation")
    print("  • Semantic chunking optimization")
    print("\nQuick Start:")
    print("  from smartchunkllm import process_legal_pdf")
    print("  result = process_legal_pdf('document.pdf')")
    print("  chunks = result.chunks")


# Quick start examples
QUICK_START_EXAMPLES = {
    "basic_pdf_processing": """
# Basic PDF processing
from smartchunkllm import process_legal_pdf

result = process_legal_pdf('legal_document.pdf')
if result.success:
    chunks = result.chunks
    print(f"Generated {len(chunks)} semantic chunks")
    for chunk in chunks:
        print(f"Chunk {chunk.id}: {chunk.content[:100]}...")
else:
    print(f"Processing failed: {result.errors}")
""",
    
    "advanced_configuration": """
# Advanced configuration with Ollama
from smartchunkllm import SmartChunkLLM, ProcessingOptions

processor = SmartChunkLLM(
    use_ollama=True,
    ollama_model="llama3.1",
    use_ollama_embeddings=True,
    enable_ensemble_clustering=True,
    min_chunk_quality=0.7
)

options = ProcessingOptions(
    use_llm_chunking=True,
    use_llm_analysis=True,
    enable_chunk_optimization=True,
    enable_chunk_merging=True
)

result = processor.process_pdf('complex_legal_doc.pdf', options)
""",
    
    "text_processing": """
# Text processing
from smartchunkllm import process_legal_text

legal_text = '''Madde 1 - Bu Kanunun amacı...
Madde 2 - Bu Kanun kapsamında...'''

result = process_legal_text(legal_text, document_type="kanun")
chunks = result.chunks
""",
    
    "quality_assessment": """
# Quality assessment and validation
from smartchunkllm import SmartChunkLLM

processor = SmartChunkLLM()
result = processor.process_pdf('document.pdf')

for chunk in result.chunks:
    quality_score = chunk.metadata.get('quality_score', 0)
    content_type = chunk.metadata.get('content_type', 'unknown')
    legal_concepts = chunk.metadata.get('legal_concepts', [])
    
    print(f"Chunk {chunk.id}:")
    print(f"  Quality: {quality_score:.2f}")
    print(f"  Type: {content_type}")
    print(f"  Legal concepts: {legal_concepts}")
""",
    
    "batch_processing": """
# Batch processing multiple documents
from smartchunkllm import SmartChunkLLM
from pathlib import Path

processor = SmartChunkLLM()
pdf_files = Path('legal_docs').glob('*.pdf')

all_chunks = []
for pdf_file in pdf_files:
    result = processor.process_pdf(pdf_file)
    if result.success:
        all_chunks.extend(result.chunks)
        print(f"Processed {pdf_file.name}: {len(result.chunks)} chunks")
    else:
        print(f"Failed to process {pdf_file.name}: {result.errors}")

print(f"Total chunks generated: {len(all_chunks)}")
"""
}


def show_examples():
    """Show quick start examples."""
    print("SmartChunkLLM Quick Start Examples\n")
    
    for title, code in QUICK_START_EXAMPLES.items():
        print(f"=== {title.replace('_', ' ').title()} ===")
        print(code)
        print()


# Module initialization
def _initialize_logging():
    """Initialize logging configuration."""
    import logging
    
    # Create logger
    logger = logging.getLogger('smartchunkllm')
    
    # Only add handler if none exists
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)


# Initialize on import
_initialize_logging()