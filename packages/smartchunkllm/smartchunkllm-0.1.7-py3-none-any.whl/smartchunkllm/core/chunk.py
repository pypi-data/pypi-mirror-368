"""Semantic chunk data structure for legal documents."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import json
from datetime import datetime


class ContentType(Enum):
    """Legal content classification types."""
    DEFINITION = "definition"  # Tanım
    RULE = "rule"  # Kural
    EXCEPTION = "exception"  # İstisna
    SANCTION = "sanction"  # Yaptırım
    PROCEDURE = "procedure"  # Prosedür
    REFERENCE = "reference"  # Atıf
    ARTICLE = "article"  # Madde
    PARAGRAPH = "paragraph"  # Fıkra
    CLAUSE = "clause"  # Bent
    TITLE = "title"  # Başlık
    PREAMBLE = "preamble"  # Önsöz
    APPENDIX = "appendix"  # Ek
    OTHER = "other"  # Diğer


class ImportanceLevel(Enum):
    """Importance levels for legal content."""
    CRITICAL = "critical"  # 0.8-1.0
    HIGH = "high"  # 0.6-0.8
    MEDIUM = "medium"  # 0.4-0.6
    LOW = "low"  # 0.2-0.4
    MINIMAL = "minimal"  # 0.0-0.2


@dataclass
class LegalConcept:
    """Represents a legal concept extracted from text."""
    term: str
    definition: Optional[str] = None
    category: Optional[str] = None
    confidence: float = 0.0
    context: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "term": self.term,
            "definition": self.definition,
            "category": self.category,
            "confidence": self.confidence,
            "context": self.context
        }


@dataclass
class QualityMetrics:
    """Quality assessment metrics for semantic chunks."""
    coherence_score: float = 0.0  # İçsel tutarlılık
    completeness_score: float = 0.0  # Tamlık
    relevance_score: float = 0.0  # İlgililik
    readability_score: float = 0.0  # Okunabilirlik
    legal_accuracy_score: float = 0.0  # Hukuki doğruluk
    overall_score: float = 0.0  # Genel kalite
    
    def calculate_overall_score(self) -> float:
        """Calculate weighted overall quality score."""
        weights = {
            "coherence": 0.25,
            "completeness": 0.20,
            "relevance": 0.20,
            "readability": 0.15,
            "legal_accuracy": 0.20
        }
        
        self.overall_score = (
            self.coherence_score * weights["coherence"] +
            self.completeness_score * weights["completeness"] +
            self.relevance_score * weights["relevance"] +
            self.readability_score * weights["readability"] +
            self.legal_accuracy_score * weights["legal_accuracy"]
        )
        return self.overall_score

    def to_dict(self) -> Dict[str, float]:
        return {
            "coherence_score": self.coherence_score,
            "completeness_score": self.completeness_score,
            "relevance_score": self.relevance_score,
            "readability_score": self.readability_score,
            "legal_accuracy_score": self.legal_accuracy_score,
            "overall_score": self.overall_score
        }


@dataclass
class SemanticChunk:
    """Represents a semantically meaningful chunk of legal text."""
    
    # Core content
    text: str
    chunk_id: str
    
    # Metadata
    content_type: ContentType = ContentType.OTHER
    importance_score: float = 0.0
    legal_concepts: List[LegalConcept] = field(default_factory=list)
    
    # Document structure
    page_number: Optional[int] = None
    section_title: Optional[str] = None
    article_number: Optional[str] = None
    paragraph_number: Optional[str] = None
    
    # Processing metadata
    font_info: Dict[str, Any] = field(default_factory=dict)
    layout_info: Dict[str, Any] = field(default_factory=dict)
    embedding_vector: Optional[List[float]] = None
    
    # Quality assessment
    quality_metrics: QualityMetrics = field(default_factory=QualityMetrics)
    
    # References and relationships
    references: List[str] = field(default_factory=list)
    related_chunks: List[str] = field(default_factory=list)
    
    # Processing info
    created_at: datetime = field(default_factory=datetime.now)
    processing_method: str = "semantic_chunking"
    model_version: str = "1.0.0"
    
    # Additional metadata
    custom_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization processing."""
        if not self.chunk_id:
            self.chunk_id = self._generate_chunk_id()
        
        # Calculate overall quality score
        self.quality_metrics.calculate_overall_score()
    
    def _generate_chunk_id(self) -> str:
        """Generate a unique chunk ID."""
        import hashlib
        content_hash = hashlib.md5(self.text.encode()).hexdigest()[:8]
        timestamp = int(self.created_at.timestamp())
        return f"chunk_{timestamp}_{content_hash}"
    
    @property
    def importance_level(self) -> ImportanceLevel:
        """Get importance level based on score."""
        if self.importance_score >= 0.8:
            return ImportanceLevel.CRITICAL
        elif self.importance_score >= 0.6:
            return ImportanceLevel.HIGH
        elif self.importance_score >= 0.4:
            return ImportanceLevel.MEDIUM
        elif self.importance_score >= 0.2:
            return ImportanceLevel.LOW
        else:
            return ImportanceLevel.MINIMAL
    
    @property
    def word_count(self) -> int:
        """Get word count of the chunk."""
        return len(self.text.split())
    
    @property
    def character_count(self) -> int:
        """Get character count of the chunk."""
        return len(self.text)
    
    def add_legal_concept(self, concept: LegalConcept) -> None:
        """Add a legal concept to the chunk."""
        self.legal_concepts.append(concept)
    
    def add_reference(self, reference: str) -> None:
        """Add a reference to another legal document or section."""
        if reference not in self.references:
            self.references.append(reference)
    
    def add_related_chunk(self, chunk_id: str) -> None:
        """Add a related chunk ID."""
        if chunk_id not in self.related_chunks:
            self.related_chunks.append(chunk_id)
    
    def get_summary(self, max_length: int = 200) -> str:
        """Get a human-readable summary of the chunk."""
        summary_parts = []
        
        # Content type and importance
        summary_parts.append(f"Type: {self.content_type.value.title()}")
        summary_parts.append(f"Importance: {self.importance_level.value.title()}")
        
        # Structure info
        if self.article_number:
            summary_parts.append(f"Article: {self.article_number}")
        if self.section_title:
            summary_parts.append(f"Section: {self.section_title}")
        
        # Legal concepts
        if self.legal_concepts:
            concepts = [c.term for c in self.legal_concepts[:3]]
            summary_parts.append(f"Key concepts: {', '.join(concepts)}")
        
        # Text preview
        text_preview = self.text[:max_length] + "..." if len(self.text) > max_length else self.text
        summary_parts.append(f"Text: {text_preview}")
        
        return " | ".join(summary_parts)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert chunk to dictionary for JSON serialization."""
        return {
            "chunk_id": self.chunk_id,
            "text": self.text,
            "content_type": self.content_type.value,
            "importance_score": self.importance_score,
            "importance_level": self.importance_level.value,
            "legal_concepts": [concept.to_dict() for concept in self.legal_concepts],
            "page_number": self.page_number,
            "section_title": self.section_title,
            "article_number": self.article_number,
            "paragraph_number": self.paragraph_number,
            "font_info": self.font_info,
            "layout_info": self.layout_info,
            "quality_metrics": self.quality_metrics.to_dict(),
            "references": self.references,
            "related_chunks": self.related_chunks,
            "word_count": self.word_count,
            "character_count": self.character_count,
            "created_at": self.created_at.isoformat(),
            "processing_method": self.processing_method,
            "model_version": self.model_version,
            "custom_metadata": self.custom_metadata
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert chunk to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SemanticChunk':
        """Create chunk from dictionary."""
        # Convert legal concepts
        legal_concepts = []
        for concept_data in data.get("legal_concepts", []):
            legal_concepts.append(LegalConcept(**concept_data))
        
        # Convert quality metrics
        quality_data = data.get("quality_metrics", {})
        quality_metrics = QualityMetrics(**quality_data)
        
        # Convert datetime
        created_at = datetime.fromisoformat(data.get("created_at", datetime.now().isoformat()))
        
        return cls(
            chunk_id=data["chunk_id"],
            text=data["text"],
            content_type=ContentType(data.get("content_type", "other")),
            importance_score=data.get("importance_score", 0.0),
            legal_concepts=legal_concepts,
            page_number=data.get("page_number"),
            section_title=data.get("section_title"),
            article_number=data.get("article_number"),
            paragraph_number=data.get("paragraph_number"),
            font_info=data.get("font_info", {}),
            layout_info=data.get("layout_info", {}),
            quality_metrics=quality_metrics,
            references=data.get("references", []),
            related_chunks=data.get("related_chunks", []),
            created_at=created_at,
            processing_method=data.get("processing_method", "semantic_chunking"),
            model_version=data.get("model_version", "1.0.0"),
            custom_metadata=data.get("custom_metadata", {})
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'SemanticChunk':
        """Create chunk from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)