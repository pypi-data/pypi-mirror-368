"""Core type definitions for SmartChunkLLM."""

from enum import Enum
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime


class ChunkingStrategy(Enum):
    """Available chunking strategies."""
    SEMANTIC = "semantic"
    HYBRID = "hybrid"
    HIERARCHICAL = "hierarchical"
    FIXED_SIZE = "fixed_size"
    SLIDING_WINDOW = "sliding_window"


class QualityLevel(Enum):
    """Quality levels for processing."""
    FAST = "fast"
    BALANCED = "balanced"
    HIGH = "high"
    MAXIMUM = "maximum"


class ContentType(Enum):
    """Types of content in legal documents."""
    TITLE = "title"
    ARTICLE = "article"
    PARAGRAPH = "paragraph"
    CLAUSE = "clause"
    DEFINITION = "definition"
    REFERENCE = "reference"
    EXCEPTION = "exception"
    SANCTION = "sanction"
    PROCEDURE = "procedure"
    GENERAL = "general"
    METADATA = "metadata"
    FOOTER = "footer"
    HEADER = "header"
    TABLE = "table"
    LIST = "list"


class ProcessingStatus(Enum):
    """Processing status indicators."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class LLMProvider(Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"


class EmbeddingModel(Enum):
    """Available embedding models."""
    SENTENCE_TRANSFORMERS = "sentence-transformers/all-MiniLM-L6-v2"
    OPENAI_ADA = "text-embedding-ada-002"
    OPENAI_3_SMALL = "text-embedding-3-small"
    OPENAI_3_LARGE = "text-embedding-3-large"
    MULTILINGUAL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    TURKISH = "sentence-transformers/distiluse-base-multilingual-cased"


class ClusteringAlgorithm(Enum):
    """Available clustering algorithms."""
    HDBSCAN = "hdbscan"
    KMEANS = "kmeans"
    AGGLOMERATIVE = "agglomerative"
    DBSCAN = "dbscan"
    GAUSSIAN_MIXTURE = "gaussian_mixture"


@dataclass
class BoundingBox:
    """Bounding box for layout elements."""
    x0: float
    y0: float
    x1: float
    y1: float
    
    @property
    def width(self) -> float:
        return self.x1 - self.x0
    
    @property
    def height(self) -> float:
        return self.y1 - self.y0
    
    @property
    def area(self) -> float:
        return self.width * self.height
    
    def overlaps_with(self, other: 'BoundingBox') -> bool:
        """Check if this bounding box overlaps with another."""
        return not (self.x1 < other.x0 or other.x1 < self.x0 or 
                   self.y1 < other.y0 or other.y1 < self.y0)
    
    def intersection_area(self, other: 'BoundingBox') -> float:
        """Calculate intersection area with another bounding box."""
        if not self.overlaps_with(other):
            return 0.0
        
        x_overlap = min(self.x1, other.x1) - max(self.x0, other.x0)
        y_overlap = min(self.y1, other.y1) - max(self.y0, other.y0)
        return x_overlap * y_overlap


@dataclass
class FontInfo:
    """Font information for text elements."""
    name: str
    size: float
    is_bold: bool = False
    is_italic: bool = False
    color: Optional[str] = None
    
    def __hash__(self) -> int:
        return hash((self.name, self.size, self.is_bold, self.is_italic))
    
    def is_similar(self, other: 'FontInfo', size_tolerance: float = 1.0) -> bool:
        """Check if this font is similar to another."""
        return (self.name == other.name and 
                abs(self.size - other.size) <= size_tolerance and
                self.is_bold == other.is_bold and
                self.is_italic == other.is_italic)


@dataclass
class TextElement:
    """Text element with position and formatting information."""
    text: str
    bbox: BoundingBox
    font: FontInfo
    page_number: int
    confidence: float = 1.0
    content_type: Optional[ContentType] = None
    
    @property
    def is_title(self) -> bool:
        """Check if this element is likely a title."""
        return (self.font.is_bold or 
                self.font.size > 12 or 
                self.content_type == ContentType.TITLE)
    
    @property
    def is_header(self) -> bool:
        """Check if this element is likely a header."""
        return (self.bbox.y1 > 0.9 * 842 or  # A4 page height
                self.content_type == ContentType.HEADER)
    
    @property
    def is_footer(self) -> bool:
        """Check if this element is likely a footer."""
        return (self.bbox.y0 < 0.1 * 842 or  # A4 page height
                self.content_type == ContentType.FOOTER)


@dataclass
class ProcessingMetrics:
    """Metrics for processing performance."""
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    total_pages: int = 0
    total_elements: int = 0
    total_chunks: int = 0
    total_tokens: int = 0
    processing_time: float = 0.0
    memory_usage: float = 0.0


@dataclass
class ProcessingMetadata:
    """Metadata for processing operations."""
    operation_id: str
    operation_type: str
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    status: ProcessingStatus = ProcessingStatus.PENDING
    input_size: int = 0
    output_size: int = 0
    error_message: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    metrics: Optional[ProcessingMetrics] = None
    
    @property
    def duration(self) -> float:
        """Calculate processing duration in seconds."""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0
    
    def finish(self):
        """Mark processing as finished."""
        self.end_time = datetime.now()
        self.processing_time = self.duration


@dataclass
class QualityMetrics:
    """Quality assessment metrics."""
    coherence_score: float = 0.0
    completeness_score: float = 0.0
    readability_score: float = 0.0
    consistency_score: float = 0.0
    relevance_score: float = 0.0
    structure_score: float = 0.0
    legal_compliance_score: float = 0.0
    information_density_score: float = 0.0
    
    @property
    def overall_score(self) -> float:
        """Calculate overall quality score."""
        scores = [
            self.coherence_score,
            self.completeness_score,
            self.readability_score,
            self.consistency_score,
            self.relevance_score,
            self.structure_score,
            self.legal_compliance_score,
            self.information_density_score
        ]
        return sum(scores) / len(scores) if scores else 0.0
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            'coherence': self.coherence_score,
            'completeness': self.completeness_score,
            'readability': self.readability_score,
            'consistency': self.consistency_score,
            'relevance': self.relevance_score,
            'structure': self.structure_score,
            'legal_compliance': self.legal_compliance_score,
            'information_density': self.information_density_score,
            'overall': self.overall_score
        }


@dataclass
class ChunkMetadata:
    """Metadata for semantic chunks."""
    chunk_id: str
    source_file: Optional[str] = None
    page_numbers: List[int] = field(default_factory=list)
    content_type: Optional[ContentType] = None
    legal_concepts: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    definitions: List[str] = field(default_factory=list)
    language: str = "tr"
    confidence: float = 1.0
    processing_timestamp: datetime = field(default_factory=datetime.now)
    parent_chunk_id: Optional[str] = None
    child_chunk_ids: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'chunk_id': self.chunk_id,
            'source_file': self.source_file,
            'page_numbers': self.page_numbers,
            'content_type': self.content_type.value if self.content_type else None,
            'legal_concepts': self.legal_concepts,
            'references': self.references,
            'definitions': self.definitions,
            'language': self.language,
            'confidence': self.confidence,
            'processing_timestamp': self.processing_timestamp.isoformat(),
            'parent_chunk_id': self.parent_chunk_id,
            'child_chunk_ids': self.child_chunk_ids
        }


@dataclass
class ValidationResult:
    """Result of validation process."""
    is_valid: bool
    score: float
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    
    def add_issue(self, issue: str, severity: str = "error"):
        """Add a validation issue."""
        if severity == "error":
            self.issues.append(issue)
            self.is_valid = False
        elif severity == "warning":
            self.warnings.append(issue)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'is_valid': self.is_valid,
            'score': self.score,
            'issues': self.issues,
            'warnings': self.warnings,
            'suggestions': self.suggestions
        }


# Type aliases for better readability
EmbeddingVector = List[float]
TokenList = List[str]
ChunkList = List['SemanticChunk']  # Forward reference
MetadataDict = Dict[str, Any]
ConfigDict = Dict[str, Any]


# Constants
DEFAULT_CHUNK_SIZE = 512
DEFAULT_OVERLAP_SIZE = 50
DEFAULT_MIN_CHUNK_SIZE = 100
DEFAULT_MAX_CHUNK_SIZE = 2048
DEFAULT_QUALITY_THRESHOLD = 0.7
DEFAULT_SIMILARITY_THRESHOLD = 0.8
DEFAULT_BATCH_SIZE = 32
DEFAULT_MAX_WORKERS = 4

# Language codes
SUPPORTED_LANGUAGES = {
    'tr': 'Turkish',
    'en': 'English',
    'de': 'German',
    'fr': 'French',
    'es': 'Spanish',
    'it': 'Italian',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'ar': 'Arabic'
}

# Legal document patterns (Turkish)
TURKISH_LEGAL_PATTERNS = {
    'article': r'(?:Madde|MADDE)\s+(\d+)',
    'paragraph': r'(?:Fıkra|FIKRA)\s+(\d+)',
    'clause': r'(?:Bent|BENT)\s+([a-z]|[A-Z])',
    'section': r'(?:Bölüm|BÖLÜM)\s+(\d+|[IVX]+)',
    'part': r'(?:Kısım|KISIM)\s+(\d+|[IVX]+)',
    'definition': r'(?:tanım|tanımı|anlamında|ifade eder)',
    'reference': r'(?:bu\s+(?:Kanun|Yönetmelik|Tüzük)|\d+\s*(?:inci|nci|üncü|ncü)\s+madde)',
    'exception': r'(?:ancak|fakat|lakin|şu\s+kadar\s+ki|istisnası)',
    'sanction': r'(?:ceza|para\s+cezası|hapis|disiplin|yaptırım)'
}


@dataclass
class SemanticChunk:
    """Semantic chunk with enhanced metadata and analysis."""
    id: str
    text: str
    metadata: ChunkMetadata
    embedding: Optional[EmbeddingVector] = None
    quality_score: float = 0.0
    similarity_scores: Dict[str, float] = field(default_factory=dict)
    tokens: Optional[TokenList] = None
    word_count: int = 0
    char_count: int = 0
    
    def __post_init__(self):
        """Post-initialization processing."""
        if not self.word_count:
            self.word_count = len(self.text.split())
        if not self.char_count:
            self.char_count = len(self.text)
    
    @property
    def is_valid(self) -> bool:
        """Check if chunk is valid."""
        return (
            bool(self.text.strip()) and
            self.char_count >= DEFAULT_MIN_CHUNK_SIZE and
            self.char_count <= DEFAULT_MAX_CHUNK_SIZE and
            self.quality_score >= DEFAULT_QUALITY_THRESHOLD
        )
    
    @property
    def density(self) -> float:
        """Calculate information density (words per character)."""
        return self.word_count / max(self.char_count, 1)
    
    def calculate_similarity(self, other: 'SemanticChunk') -> float:
        """Calculate similarity with another chunk."""
        if not self.embedding or not other.embedding:
            return 0.0
        
        # Simple cosine similarity
        import math
        
        dot_product = sum(a * b for a, b in zip(self.embedding, other.embedding))
        magnitude_a = math.sqrt(sum(a * a for a in self.embedding))
        magnitude_b = math.sqrt(sum(b * b for b in other.embedding))
        
        if magnitude_a == 0 or magnitude_b == 0:
            return 0.0
        
        return dot_product / (magnitude_a * magnitude_b)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'text': self.text,
            'metadata': self.metadata.to_dict(),
            'embedding': self.embedding,
            'quality_score': self.quality_score,
            'similarity_scores': self.similarity_scores,
            'tokens': self.tokens,
            'word_count': self.word_count,
            'char_count': self.char_count,
            'is_valid': self.is_valid,
            'density': self.density
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SemanticChunk':
        """Create from dictionary."""
        metadata = ChunkMetadata(**data['metadata']) if isinstance(data['metadata'], dict) else data['metadata']
        
        return cls(
            id=data['id'],
            text=data['text'],
            metadata=metadata,
            embedding=data.get('embedding'),
            quality_score=data.get('quality_score', 0.0),
            similarity_scores=data.get('similarity_scores', {}),
            tokens=data.get('tokens'),
            word_count=data.get('word_count', 0),
            char_count=data.get('char_count', 0)
         )


@dataclass
class DocumentMetadata:
    """Metadata for processed documents."""
    filename: str
    file_path: Optional[str] = None
    file_size: int = 0
    file_type: str = "text"
    encoding: str = "utf-8"
    language: str = "tr"
    page_count: int = 0
    word_count: int = 0
    char_count: int = 0
    processing_timestamp: datetime = field(default_factory=datetime.now)
    source_hash: Optional[str] = None
    author: Optional[str] = None
    title: Optional[str] = None
    subject: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    creation_date: Optional[datetime] = None
    modification_date: Optional[datetime] = None
    legal_document_type: Optional[str] = None
    jurisdiction: Optional[str] = None
    law_number: Optional[str] = None
    publication_date: Optional[datetime] = None
    effective_date: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'filename': self.filename,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'encoding': self.encoding,
            'language': self.language,
            'page_count': self.page_count,
            'word_count': self.word_count,
            'char_count': self.char_count,
            'processing_timestamp': self.processing_timestamp.isoformat(),
            'source_hash': self.source_hash,
            'author': self.author,
            'title': self.title,
            'subject': self.subject,
            'keywords': self.keywords,
            'creation_date': self.creation_date.isoformat() if self.creation_date else None,
            'modification_date': self.modification_date.isoformat() if self.modification_date else None,
            'legal_document_type': self.legal_document_type,
            'jurisdiction': self.jurisdiction,
            'law_number': self.law_number,
            'publication_date': self.publication_date.isoformat() if self.publication_date else None,
            'effective_date': self.effective_date.isoformat() if self.effective_date else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DocumentMetadata':
        """Create from dictionary."""
        # Convert ISO format strings back to datetime objects
        for date_field in ['processing_timestamp', 'creation_date', 'modification_date', 'publication_date', 'effective_date']:
            if data.get(date_field) and isinstance(data[date_field], str):
                try:
                    data[date_field] = datetime.fromisoformat(data[date_field])
                except ValueError:
                    data[date_field] = None
        
        return cls(**data)