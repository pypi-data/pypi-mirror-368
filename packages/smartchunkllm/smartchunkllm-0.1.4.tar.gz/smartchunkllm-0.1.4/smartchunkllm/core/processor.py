"""Core processor module for SmartChunkLLM."""

from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import time
from dataclasses import dataclass

from .types import (
    ChunkingStrategy,
    QualityLevel,
    ProcessingStatus,
    ChunkMetadata,
    ProcessingMetrics,
    QualityMetrics,
    ValidationResult
)
from .exceptions import (
    SmartChunkLLMError,
    ProcessingError,
    ValidationError
)
from ..utils.text import TextProcessor
from ..utils.logging import get_logger
from ..utils.memory import get_memory_info
from ..utils.performance import Timer


@dataclass
class ProcessingResult:
    """Processing result container."""
    chunks: List[Dict[str, Any]]
    metrics: ProcessingMetrics
    quality_metrics: QualityMetrics
    validation_result: ValidationResult
    status: ProcessingStatus
    error: Optional[str] = None


class SmartChunkProcessor:
    """Core processor for SmartChunkLLM."""
    
    def __init__(
        self,
        strategy: ChunkingStrategy = ChunkingStrategy.FIXED_SIZE,
        quality_level: QualityLevel = QualityLevel.BALANCED,
        chunk_size: int = 800,
        overlap: int = 150,
        language: str = "tr",
        **kwargs
    ):
        """Initialize the processor.
        
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
        
        # Initialize components
        self.text_processor = TextProcessor()
        self.logger = get_logger(self.__class__.__name__)
        
        self.logger.info(
            f"SmartChunkProcessor initialized with strategy={strategy}, "
            f"quality_level={quality_level}, chunk_size={chunk_size}"
        )
    
    def process_text(self, text: str) -> ProcessingResult:
        """Process text and return chunks.
        
        Args:
            text: Input text to process
            
        Returns:
            ProcessingResult containing chunks and metrics
        """
        timer = Timer()
        timer.start()
        
        try:
            self.logger.info(f"Starting text processing, length: {len(text)} chars")
            
            # Validate input
            validation_result = self._validate_input(text)
            if not validation_result.is_valid:
                return ProcessingResult(
                    chunks=[],
                    metrics=ProcessingMetrics(),
                    quality_metrics=QualityMetrics(),
                    validation_result=validation_result,
                    status=ProcessingStatus.FAILED,
                    error=validation_result.error_message
                )
            
            # Clean and normalize text
            cleaned_text = self.text_processor.clean_text(text)
            normalized_text = self.text_processor.normalize_text(cleaned_text)
            
            # Detect language
            detected_language = self.text_processor.detect_language(normalized_text)
            self.logger.info(f"Detected language: {detected_language}")
            
            # Create chunks based on strategy
            chunks = self._create_chunks(normalized_text)
            
            # Calculate metrics
            processing_time = timer.stop()
            memory_info = get_memory_info()
            
            metrics = ProcessingMetrics(
                processing_time=processing_time,
                memory_usage=memory_info.used_mb,
                total_chunks=len(chunks),
                average_chunk_size=sum(len(c['text']) for c in chunks) / len(chunks) if chunks else 0,
                language_detected=detected_language
            )
            
            # Calculate quality metrics
            quality_metrics = self._calculate_quality_metrics(chunks)
            
            self.logger.info(
                f"Processing completed: {len(chunks)} chunks in {processing_time:.2f}s"
            )
            
            return ProcessingResult(
                chunks=chunks,
                metrics=metrics,
                quality_metrics=quality_metrics,
                validation_result=validation_result,
                status=ProcessingStatus.COMPLETED
            )
            
        except Exception as e:
            self.logger.error(f"Processing failed: {e}")
            return ProcessingResult(
                chunks=[],
                metrics=ProcessingMetrics(),
                quality_metrics=QualityMetrics(),
                validation_result=ValidationResult(is_valid=False, error_message=str(e)),
                status=ProcessingStatus.FAILED,
                error=str(e)
            )
    
    def _validate_input(self, text: str) -> ValidationResult:
        """Validate input text.
        
        Args:
            text: Input text to validate
            
        Returns:
            ValidationResult with validation status
        """
        if not text or not text.strip():
            return ValidationResult(
                is_valid=False,
                error_message="Input text is empty"
            )
        
        if len(text) < 10:
            return ValidationResult(
                is_valid=False,
                error_message="Input text is too short (minimum 10 characters)"
            )
        
        if len(text) > 10_000_000:  # 10MB limit
            return ValidationResult(
                is_valid=False,
                error_message="Input text is too large (maximum 10MB)"
            )
        
        return ValidationResult(is_valid=True)
    
    def _create_chunks(self, text: str) -> List[Dict[str, Any]]:
        """Create chunks based on the selected strategy.
        
        Args:
            text: Input text to chunk
            
        Returns:
            List of chunk dictionaries
        """
        if self.strategy == ChunkingStrategy.FIXED_SIZE:
            return self._create_fixed_size_chunks(text)
        elif self.strategy == ChunkingStrategy.SEMANTIC:
            return self._create_semantic_chunks(text)
        elif self.strategy == ChunkingStrategy.HYBRID:
            return self._create_hybrid_chunks(text)
        else:
            # Default to fixed size
            return self._create_fixed_size_chunks(text)
    
    def _create_fixed_size_chunks(self, text: str) -> List[Dict[str, Any]]:
        """Create fixed-size chunks.
        
        Args:
            text: Input text
            
        Returns:
            List of chunk dictionaries
        """
        chunks = []
        text_length = len(text)
        
        for i in range(0, text_length, self.chunk_size - self.overlap):
            chunk_text = text[i:i + self.chunk_size]
            
            if not chunk_text.strip():
                continue
            
            chunk_id = f"chunk_{len(chunks) + 1:03d}"
            
            metadata = ChunkMetadata(
                chunk_id=chunk_id,
                start_position=i,
                end_position=min(i + self.chunk_size, text_length),
                chunk_size=len(chunk_text),
                strategy=self.strategy,
                quality_score=self._calculate_chunk_quality(chunk_text),
                confidence=0.8,  # Default confidence for fixed-size chunks
                language=self.language
            )
            
            chunks.append({
                'id': chunk_id,
                'text': chunk_text,
                'metadata': metadata.__dict__
            })
        
        return chunks
    
    def _create_semantic_chunks(self, text: str) -> List[Dict[str, Any]]:
        """Create semantic chunks (simplified implementation).
        
        Args:
            text: Input text
            
        Returns:
            List of chunk dictionaries
        """
        # For now, use sentence-based chunking as a semantic approach
        sentences = self.text_processor.extract_sentences(text)
        chunks = []
        current_chunk = ""
        current_position = 0
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= self.chunk_size:
                current_chunk += sentence + " "
            else:
                if current_chunk.strip():
                    chunk_id = f"chunk_{len(chunks) + 1:03d}"
                    
                    metadata = ChunkMetadata(
                        chunk_id=chunk_id,
                        start_position=current_position,
                        end_position=current_position + len(current_chunk),
                        chunk_size=len(current_chunk),
                        strategy=self.strategy,
                        quality_score=self._calculate_chunk_quality(current_chunk),
                        confidence=0.9,  # Higher confidence for semantic chunks
                        language=self.language
                    )
                    
                    chunks.append({
                        'id': chunk_id,
                        'text': current_chunk.strip(),
                        'metadata': metadata.__dict__
                    })
                    
                    current_position += len(current_chunk)
                
                current_chunk = sentence + " "
        
        # Add the last chunk
        if current_chunk.strip():
            chunk_id = f"chunk_{len(chunks) + 1:03d}"
            
            metadata = ChunkMetadata(
                chunk_id=chunk_id,
                start_position=current_position,
                end_position=current_position + len(current_chunk),
                chunk_size=len(current_chunk),
                strategy=self.strategy,
                quality_score=self._calculate_chunk_quality(current_chunk),
                confidence=0.9,
                language=self.language
            )
            
            chunks.append({
                'id': chunk_id,
                'text': current_chunk.strip(),
                'metadata': metadata.__dict__
            })
        
        return chunks
    
    def _create_hybrid_chunks(self, text: str) -> List[Dict[str, Any]]:
        """Create hybrid chunks (combination of fixed-size and semantic).
        
        Args:
            text: Input text
            
        Returns:
            List of chunk dictionaries
        """
        # Start with semantic chunking, then adjust for size constraints
        semantic_chunks = self._create_semantic_chunks(text)
        
        # If semantic chunks are too large, split them further
        final_chunks = []
        for chunk in semantic_chunks:
            if len(chunk['text']) > self.chunk_size * 1.5:  # 50% tolerance
                # Split large semantic chunks using fixed-size approach
                sub_chunks = self._create_fixed_size_chunks(chunk['text'])
                for i, sub_chunk in enumerate(sub_chunks):
                    sub_chunk['id'] = f"{chunk['id']}_sub_{i+1}"
                    sub_chunk['metadata']['strategy'] = ChunkingStrategy.HYBRID
                    final_chunks.append(sub_chunk)
            else:
                chunk['metadata']['strategy'] = ChunkingStrategy.HYBRID
                final_chunks.append(chunk)
        
        return final_chunks
    
    def _calculate_chunk_quality(self, chunk_text: str) -> float:
        """Calculate quality score for a chunk.
        
        Args:
            chunk_text: Text content of the chunk
            
        Returns:
            Quality score between 0.0 and 1.0
        """
        if not chunk_text.strip():
            return 0.0
        
        # Simple quality metrics
        score = 0.0
        
        # Length score (optimal range: 200-1000 characters)
        length = len(chunk_text)
        if 200 <= length <= 1000:
            score += 0.3
        elif 100 <= length < 200 or 1000 < length <= 1500:
            score += 0.2
        elif length > 50:
            score += 0.1
        
        # Sentence completeness (ends with proper punctuation)
        if chunk_text.strip().endswith(('.', '!', '?', ':', ';')):
            score += 0.2
        
        # Word count (reasonable number of words)
        word_count = len(chunk_text.split())
        if 30 <= word_count <= 200:
            score += 0.2
        elif 15 <= word_count < 30 or 200 < word_count <= 300:
            score += 0.1
        
        # Language consistency (Turkish text)
        if self.text_processor.is_turkish_text(chunk_text):
            score += 0.2
        
        # Readability (no excessive whitespace or special characters)
        clean_ratio = len(chunk_text.strip()) / len(chunk_text) if chunk_text else 0
        if clean_ratio > 0.9:
            score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_quality_metrics(self, chunks: List[Dict[str, Any]]) -> QualityMetrics:
        """Calculate overall quality metrics for all chunks.
        
        Args:
            chunks: List of chunk dictionaries
            
        Returns:
            QualityMetrics object
        """
        if not chunks:
            return QualityMetrics()
        
        quality_scores = [chunk['metadata']['quality_score'] for chunk in chunks]
        confidence_scores = [chunk['metadata']['confidence'] for chunk in chunks]
        chunk_sizes = [chunk['metadata']['chunk_size'] for chunk in chunks]
        
        return QualityMetrics(
            average_quality=sum(quality_scores) / len(quality_scores),
            min_quality=min(quality_scores),
            max_quality=max(quality_scores),
            quality_variance=self._calculate_variance(quality_scores),
            average_confidence=sum(confidence_scores) / len(confidence_scores),
            chunk_size_consistency=1.0 - (max(chunk_sizes) - min(chunk_sizes)) / max(chunk_sizes),
            semantic_coherence=0.8,  # Placeholder for now
            completeness_score=0.9   # Placeholder for now
        )
    
    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of a list of values.
        
        Args:
            values: List of numeric values
            
        Returns:
            Variance value
        """
        if not values:
            return 0.0
        
        mean = sum(values) / len(values)
        return sum((x - mean) ** 2 for x in values) / len(values)