"""Main processor for legal document semantic chunking."""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from pathlib import Path
import logging
import time
import json

# Core imports
from .core.types import SemanticChunk, ChunkMetadata
from .core.config import SmartChunkConfig

# PDF processing
from .pdf.extractor import PDFExtractor
from .pdf.font import FontAnalyzer
from .pdf.layout import LayoutAnalyzer
from .pdf.ocr import OCRProcessor
from .pdf.structure import StructureDetector

# AI/ML components
from .ai.embeddings import EmbeddingGenerator
from .ai.clustering import SemanticClusterer
from .ai.transformers import ContentClassifier
from .ai.quality import QualityAssessor

# LLM components
from .llm.providers import LLMManager
from .llm.prompts import PromptManager
from .llm.processors import LLMProcessor

# Legal domain
from .legal.processor import LegalDocumentProcessor
from .legal.analyzer import LegalAnalyzer
from .legal.validator import LegalValidator


@dataclass
class ProcessingOptions:
    """Options for document processing."""
    # PDF processing options
    use_ocr: bool = True
    use_layout_analysis: bool = True
    use_font_analysis: bool = True
    use_structure_detection: bool = True
    
    # AI/ML options
    use_embeddings: bool = True
    use_clustering: bool = True
    use_classification: bool = True
    use_quality_assessment: bool = True
    
    # LLM options
    use_llm_chunking: bool = True
    use_llm_analysis: bool = True
    use_llm_validation: bool = True
    
    # Legal domain options
    use_legal_analysis: bool = True
    use_legal_validation: bool = True
    
    # Performance options
    max_workers: int = 4
    batch_size: int = 10
    enable_caching: bool = True
    
    # Quality options
    min_chunk_quality: float = 0.6
    enable_chunk_optimization: bool = True
    enable_chunk_merging: bool = True


@dataclass
class ProcessingStats:
    """Statistics from document processing."""
    # Timing
    total_processing_time: float = 0.0
    pdf_processing_time: float = 0.0
    ai_processing_time: float = 0.0
    llm_processing_time: float = 0.0
    legal_processing_time: float = 0.0
    
    # Content stats
    total_pages: int = 0
    total_text_length: int = 0
    total_chunks: int = 0
    
    # Quality stats
    average_chunk_quality: float = 0.0
    chunks_optimized: int = 0
    chunks_merged: int = 0
    
    # AI stats
    embeddings_generated: int = 0
    clusters_created: int = 0
    classifications_made: int = 0
    
    # LLM stats
    llm_requests_made: int = 0
    total_tokens_used: int = 0
    
    # Legal stats
    legal_elements_detected: int = 0
    validation_issues_found: int = 0
    
    # Error stats
    errors_encountered: int = 0
    warnings_generated: int = 0


@dataclass
class ProcessingResult:
    """Complete result of document processing."""
    success: bool
    chunks: List[SemanticChunk]
    stats: ProcessingStats
    metadata: Dict[str, Any]
    errors: List[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'success': self.success,
            'chunks': [chunk.to_dict() for chunk in self.chunks],
            'stats': self.stats.__dict__,
            'metadata': self.metadata,
            'errors': self.errors,
            'warnings': self.warnings
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    def save_to_file(self, file_path: Union[str, Path]):
        """Save result to JSON file."""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(self.to_json())


class SmartChunkLLM:
    """Main processor for legal document semantic chunking.
    
    This is the primary interface for the SmartChunkLLM system.
    It coordinates all components to provide high-quality semantic chunking
    of legal documents using modern AI techniques.
    """
    
    def __init__(self, 
                 config: Optional[SmartChunkConfig] = None,
                 **kwargs):
        """Initialize SmartChunkLLM processor.
        
        Args:
            config: Configuration object
            **kwargs: Additional configuration options
        """
        # Initialize configuration
        self.config = config or SmartChunkConfig(**kwargs)
        
        # Setup logging
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize components
        self._initialize_components()
        
        # Processing state
        self._current_stats = ProcessingStats()
        self._processing_errors = []
        self._processing_warnings = []
    
    def _initialize_components(self):
        """Initialize all processing components."""
        try:
            # PDF processing components
            self.pdf_extractor = PDFExtractor(
                preferred_extractors=self.config.pdf_extractors,
                enable_fallback=True
            )
            
            self.font_analyzer = FontAnalyzer(
                legal_patterns=self.config.legal_patterns
            )
            
            self.layout_analyzer = LayoutAnalyzer(
                detection_model=self.config.layout_model
            )
            
            self.ocr_processor = OCRProcessor(
                ocr_engine=self.config.ocr_engine,
                languages=['tur', 'eng']
            )
            
            self.structure_detector = StructureDetector(
                legal_patterns=self.config.legal_patterns
            )
            
            # AI/ML components
            self.embedding_generator = EmbeddingGenerator(
                models=self.config.embedding_models,
                enable_caching=self.config.enable_caching
            )
            
            self.semantic_clusterer = SemanticClusterer(
                clustering_methods=self.config.clustering_methods,
                enable_ensemble=self.config.enable_ensemble_clustering
            )
            
            self.content_classifier = ContentClassifier(
                model_name=self.config.classification_model,
                legal_patterns=self.config.legal_patterns
            )
            
            self.quality_assessor = QualityAssessor(
                quality_thresholds=self.config.quality_thresholds,
                legal_patterns=self.config.legal_patterns
            )
            
            # LLM components
            self.llm_manager = LLMManager(
                providers=self.config.llm_providers,
                default_provider=self.config.default_llm_provider,
                enable_fallback=True
            )
            
            self.prompt_manager = PromptManager()
            
            self.llm_processor = LLMProcessor(
                llm_manager=self.llm_manager,
                prompt_manager=self.prompt_manager,
                max_retries=self.config.max_retries,
                timeout=self.config.request_timeout
            )
            
            # Legal domain components
            self.legal_analyzer = LegalAnalyzer(
                legal_patterns=self.config.legal_patterns
            )
            
            self.legal_validator = LegalValidator(
                validation_rules=self.config.validation_rules,
                quality_thresholds=self.config.quality_thresholds
            )
            
            # Main legal processor
            self.legal_processor = LegalDocumentProcessor(
                pdf_extractor=self.pdf_extractor,
                font_analyzer=self.font_analyzer,
                embedding_generator=self.embedding_generator,
                clusterer=self.semantic_clusterer,
                classifier=self.content_classifier,
                quality_assessor=self.quality_assessor,
                llm_manager=self.llm_manager,
                legal_analyzer=self.legal_analyzer,
                legal_validator=self.legal_validator
            )
            
            self.logger.info("All components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            raise
    
    def process_pdf(self, 
                   pdf_path: Union[str, Path],
                   options: Optional[ProcessingOptions] = None) -> ProcessingResult:
        """Process a PDF document for semantic chunking.
        
        Args:
            pdf_path: Path to PDF file
            options: Processing options
        
        Returns:
            ProcessingResult with chunks and metadata
        """
        start_time = time.time()
        
        # Initialize processing state
        self._reset_processing_state()
        options = options or ProcessingOptions()
        
        try:
            self.logger.info(f"Starting processing of PDF: {pdf_path}")
            
            # Validate input
            pdf_path = Path(pdf_path)
            if not pdf_path.exists():
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
            # Process with legal processor
            legal_result = self.legal_processor.process_legal_pdf(
                str(pdf_path),
                enable_ocr=options.use_ocr,
                enable_layout_analysis=options.use_layout_analysis,
                enable_font_analysis=options.use_font_analysis,
                enable_structure_detection=options.use_structure_detection,
                enable_embeddings=options.use_embeddings,
                enable_clustering=options.use_clustering,
                enable_classification=options.use_classification,
                enable_quality_assessment=options.use_quality_assessment,
                enable_legal_analysis=options.use_legal_analysis,
                enable_legal_validation=options.use_legal_validation,
                min_chunk_quality=options.min_chunk_quality
            )
            
            if not legal_result.success:
                raise Exception(f"Legal processing failed: {legal_result.error}")
            
            chunks = legal_result.chunks
            
            # Apply LLM processing if enabled
            if options.use_llm_chunking or options.use_llm_analysis:
                chunks = self._apply_llm_processing(chunks, options)
            
            # Apply optimization if enabled
            if options.enable_chunk_optimization:
                chunks = self._optimize_chunks(chunks, options)
            
            # Apply merging if enabled
            if options.enable_chunk_merging:
                chunks = self._merge_chunks(chunks, options)
            
            # Final quality check
            if options.use_quality_assessment:
                chunks = self._final_quality_check(chunks, options)
            
            # Calculate final stats
            self._current_stats.total_processing_time = time.time() - start_time
            self._current_stats.total_chunks = len(chunks)
            self._current_stats.average_chunk_quality = self._calculate_average_quality(chunks)
            
            # Create result
            result = ProcessingResult(
                success=True,
                chunks=chunks,
                stats=self._current_stats,
                metadata={
                    'pdf_path': str(pdf_path),
                    'processing_options': options.__dict__,
                    'config': self.config.to_dict(),
                    'legal_result_metadata': legal_result.metadata
                },
                errors=self._processing_errors,
                warnings=self._processing_warnings
            )
            
            self.logger.info(f"Processing completed successfully. Generated {len(chunks)} chunks.")
            return result
            
        except Exception as e:
            self.logger.error(f"Processing failed: {e}")
            
            return ProcessingResult(
                success=False,
                chunks=[],
                stats=self._current_stats,
                metadata={
                    'pdf_path': str(pdf_path),
                    'processing_options': options.__dict__ if options else {},
                    'error': str(e)
                },
                errors=self._processing_errors + [str(e)],
                warnings=self._processing_warnings
            )
    
    def process_text(self, 
                    text: str,
                    document_type: str = "legal",
                    options: Optional[ProcessingOptions] = None) -> ProcessingResult:
        """Process raw text for semantic chunking.
        
        Args:
            text: Input text
            document_type: Type of document
            options: Processing options
        
        Returns:
            ProcessingResult with chunks and metadata
        """
        start_time = time.time()
        
        # Initialize processing state
        self._reset_processing_state()
        options = options or ProcessingOptions()
        
        try:
            self.logger.info(f"Starting text processing ({len(text)} characters)")
            
            # Process with legal processor
            legal_result = self.legal_processor.process_legal_text(
                text,
                document_type=document_type,
                enable_embeddings=options.use_embeddings,
                enable_clustering=options.use_clustering,
                enable_classification=options.use_classification,
                enable_quality_assessment=options.use_quality_assessment,
                enable_legal_analysis=options.use_legal_analysis,
                enable_legal_validation=options.use_legal_validation,
                min_chunk_quality=options.min_chunk_quality
            )
            
            if not legal_result.success:
                raise Exception(f"Legal processing failed: {legal_result.error}")
            
            chunks = legal_result.chunks
            
            # Apply LLM processing if enabled
            if options.use_llm_chunking or options.use_llm_analysis:
                chunks = self._apply_llm_processing(chunks, options)
            
            # Apply optimization if enabled
            if options.enable_chunk_optimization:
                chunks = self._optimize_chunks(chunks, options)
            
            # Apply merging if enabled
            if options.enable_chunk_merging:
                chunks = self._merge_chunks(chunks, options)
            
            # Final quality check
            if options.use_quality_assessment:
                chunks = self._final_quality_check(chunks, options)
            
            # Calculate final stats
            self._current_stats.total_processing_time = time.time() - start_time
            self._current_stats.total_text_length = len(text)
            self._current_stats.total_chunks = len(chunks)
            self._current_stats.average_chunk_quality = self._calculate_average_quality(chunks)
            
            # Create result
            result = ProcessingResult(
                success=True,
                chunks=chunks,
                stats=self._current_stats,
                metadata={
                    'text_length': len(text),
                    'document_type': document_type,
                    'processing_options': options.__dict__,
                    'config': self.config.to_dict(),
                    'legal_result_metadata': legal_result.metadata
                },
                errors=self._processing_errors,
                warnings=self._processing_warnings
            )
            
            self.logger.info(f"Text processing completed successfully. Generated {len(chunks)} chunks.")
            return result
            
        except Exception as e:
            self.logger.error(f"Text processing failed: {e}")
            
            return ProcessingResult(
                success=False,
                chunks=[],
                stats=self._current_stats,
                metadata={
                    'text_length': len(text),
                    'document_type': document_type,
                    'processing_options': options.__dict__ if options else {},
                    'error': str(e)
                },
                errors=self._processing_errors + [str(e)],
                warnings=self._processing_warnings
            )
    
    def _apply_llm_processing(self, 
                             chunks: List[SemanticChunk],
                             options: ProcessingOptions) -> List[SemanticChunk]:
        """Apply LLM-based processing to chunks."""
        try:
            self.logger.info("Applying LLM processing to chunks")
            
            processed_chunks = []
            
            for chunk in chunks:
                # LLM-based content analysis
                if options.use_llm_analysis:
                    # Classify content type
                    content_type_result = self.llm_processor.classification_processor.classify_content_type(
                        chunk.content
                    )
                    
                    if content_type_result.success:
                        chunk.metadata.update({
                            'llm_content_type': content_type_result.result.get('content_type'),
                            'llm_content_confidence': content_type_result.result.get('confidence_score')
                        })
                        self._current_stats.llm_requests_made += 1
                        self._current_stats.total_tokens_used += content_type_result.tokens_used
                    
                    # Classify importance
                    content_type = chunk.metadata.get('llm_content_type', 'GENEL')
                    importance_result = self.llm_processor.classification_processor.classify_importance(
                        chunk.content, content_type
                    )
                    
                    if importance_result.success:
                        chunk.metadata.update({
                            'llm_importance_level': importance_result.result.get('importance_level'),
                            'llm_importance_confidence': importance_result.result.get('confidence_score')
                        })
                        self._current_stats.llm_requests_made += 1
                        self._current_stats.total_tokens_used += importance_result.tokens_used
                
                # LLM-based quality assessment
                if options.use_quality_assessment:
                    content_type = chunk.metadata.get('llm_content_type', 'GENEL')
                    importance_level = chunk.metadata.get('llm_importance_level', 'ORTA')
                    
                    quality_result = self.llm_processor.quality_processor.assess_chunk_quality(
                        chunk.content, content_type, importance_level
                    )
                    
                    if quality_result.success:
                        chunk.metadata.update({
                            'llm_quality_assessment': quality_result.result
                        })
                        self._current_stats.llm_requests_made += 1
                        self._current_stats.total_tokens_used += quality_result.tokens_used
                
                processed_chunks.append(chunk)
            
            return processed_chunks
            
        except Exception as e:
            self.logger.warning(f"LLM processing failed: {e}")
            self._processing_warnings.append(f"LLM processing failed: {e}")
            return chunks
    
    def _optimize_chunks(self, 
                        chunks: List[SemanticChunk],
                        options: ProcessingOptions) -> List[SemanticChunk]:
        """Optimize chunks for better quality."""
        try:
            self.logger.info("Optimizing chunks")
            
            optimized_chunks = []
            
            for chunk in chunks:
                # Check if chunk needs optimization
                quality_score = chunk.metadata.get('quality_score', 0.5)
                
                if quality_score < options.min_chunk_quality:
                    # Try to optimize with LLM
                    content_type = chunk.metadata.get('content_type', 'unknown')
                    importance_level = chunk.metadata.get('importance_level', 'medium')
                    
                    optimization_result = self.llm_processor.chunk_processor.optimize_chunk(
                        chunk.content, content_type, importance_level, quality_score
                    )
                    
                    if optimization_result.success:
                        # Update chunk with optimized content
                        chunk.content = optimization_result.result
                        chunk.metadata['optimized'] = True
                        chunk.metadata['original_quality_score'] = quality_score
                        
                        self._current_stats.chunks_optimized += 1
                        self._current_stats.llm_requests_made += 1
                        self._current_stats.total_tokens_used += optimization_result.tokens_used
                
                optimized_chunks.append(chunk)
            
            return optimized_chunks
            
        except Exception as e:
            self.logger.warning(f"Chunk optimization failed: {e}")
            self._processing_warnings.append(f"Chunk optimization failed: {e}")
            return chunks
    
    def _merge_chunks(self, 
                     chunks: List[SemanticChunk],
                     options: ProcessingOptions) -> List[SemanticChunk]:
        """Merge similar or related chunks."""
        try:
            self.logger.info("Evaluating chunk merging")
            
            merged_chunks = []
            i = 0
            
            while i < len(chunks):
                current_chunk = chunks[i]
                
                # Check if we can merge with next chunk
                if i + 1 < len(chunks):
                    next_chunk = chunks[i + 1]
                    
                    # Evaluate merging with LLM
                    merging_result = self.llm_processor.chunk_processor.evaluate_chunk_merging(
                        current_chunk, next_chunk
                    )
                    
                    if (merging_result.success and 
                        merging_result.result.get('should_merge', False)):
                        
                        # Merge chunks
                        merged_content = merging_result.result.get('merged_content', 
                                                                 current_chunk.content + "\n\n" + next_chunk.content)
                        
                        merged_chunk = SemanticChunk(
                            id=current_chunk.id,
                            content=merged_content,
                            metadata=ChunkMetadata(
                                start_page=current_chunk.metadata.start_page,
                                end_page=next_chunk.metadata.end_page,
                                content_type=current_chunk.metadata.content_type,
                                importance_score=max(current_chunk.metadata.importance_score,
                                                   next_chunk.metadata.importance_score),
                                legal_concepts=list(set(current_chunk.metadata.legal_concepts + 
                                                       next_chunk.metadata.legal_concepts)),
                                **{
                                    'merged': True,
                                    'merged_from': [current_chunk.id, next_chunk.id],
                                    'merging_reasoning': merging_result.result.get('reasoning', '')
                                }
                            )
                        )
                        
                        merged_chunks.append(merged_chunk)
                        self._current_stats.chunks_merged += 1
                        self._current_stats.llm_requests_made += 1
                        self._current_stats.total_tokens_used += merging_result.tokens_used
                        
                        i += 2  # Skip next chunk as it's been merged
                    else:
                        merged_chunks.append(current_chunk)
                        i += 1
                else:
                    merged_chunks.append(current_chunk)
                    i += 1
            
            return merged_chunks
            
        except Exception as e:
            self.logger.warning(f"Chunk merging failed: {e}")
            self._processing_warnings.append(f"Chunk merging failed: {e}")
            return chunks
    
    def _final_quality_check(self, 
                           chunks: List[SemanticChunk],
                           options: ProcessingOptions) -> List[SemanticChunk]:
        """Perform final quality check on chunks."""
        try:
            self.logger.info("Performing final quality check")
            
            quality_chunks = []
            
            for chunk in chunks:
                # Re-assess quality after processing
                quality_result = self.quality_assessor.assess_chunk_quality(chunk)
                
                if quality_result.overall_score >= options.min_chunk_quality:
                    chunk.metadata.quality_score = quality_result.overall_score
                    chunk.metadata.quality_details = quality_result.to_dict()
                    quality_chunks.append(chunk)
                else:
                    self.logger.warning(f"Chunk {chunk.id} failed final quality check (score: {quality_result.overall_score})")
                    self._processing_warnings.append(
                        f"Chunk {chunk.id} failed final quality check (score: {quality_result.overall_score})"
                    )
            
            return quality_chunks
            
        except Exception as e:
            self.logger.warning(f"Final quality check failed: {e}")
            self._processing_warnings.append(f"Final quality check failed: {e}")
            return chunks
    
    def _calculate_average_quality(self, chunks: List[SemanticChunk]) -> float:
        """Calculate average quality score of chunks."""
        if not chunks:
            return 0.0
        
        total_quality = sum(chunk.metadata.get('quality_score', 0.5) for chunk in chunks)
        return total_quality / len(chunks)
    
    def _reset_processing_state(self):
        """Reset processing state for new operation."""
        self._current_stats = ProcessingStats()
        self._processing_errors = []
        self._processing_warnings = []
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats."""
        return ['pdf']
    
    def get_component_status(self) -> Dict[str, bool]:
        """Get status of all components."""
        status = {}
        
        try:
            # Test each component
            status['pdf_extractor'] = self.pdf_extractor is not None
            status['font_analyzer'] = self.font_analyzer is not None
            status['layout_analyzer'] = self.layout_analyzer is not None
            status['ocr_processor'] = self.ocr_processor is not None
            status['structure_detector'] = self.structure_detector is not None
            status['embedding_generator'] = self.embedding_generator is not None
            status['semantic_clusterer'] = self.semantic_clusterer is not None
            status['content_classifier'] = self.content_classifier is not None
            status['quality_assessor'] = self.quality_assessor is not None
            status['llm_manager'] = self.llm_manager.is_available()
            status['legal_analyzer'] = self.legal_analyzer is not None
            status['legal_validator'] = self.legal_validator is not None
            
        except Exception as e:
            self.logger.error(f"Error checking component status: {e}")
        
        return status
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate current configuration."""
        validation_result = {
            'valid': True,
            'issues': [],
            'warnings': []
        }
        
        try:
            # Check LLM providers
            if not self.llm_manager.is_available():
                validation_result['issues'].append("No LLM providers available")
                validation_result['valid'] = False
            
            # Check embedding models
            if not self.embedding_generator.models:
                validation_result['warnings'].append("No embedding models configured")
            
            # Check configuration completeness
            if not self.config.legal_patterns:
                validation_result['warnings'].append("No legal patterns configured")
            
            if not self.config.quality_thresholds:
                validation_result['warnings'].append("No quality thresholds configured")
            
        except Exception as e:
            validation_result['issues'].append(f"Configuration validation error: {e}")
            validation_result['valid'] = False
        
        return validation_result


# Convenience functions
def create_processor(config_path: Optional[str] = None, **kwargs) -> SmartChunkLLM:
    """Create a SmartChunkLLM processor with configuration.
    
    Args:
        config_path: Path to configuration file
        **kwargs: Additional configuration options
    
    Returns:
        Configured SmartChunkLLM processor
    """
    if config_path:
        config = SmartChunkConfig.from_file(config_path)
        # Override with kwargs
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
    else:
        config = SmartChunkConfig(**kwargs)
    
    return SmartChunkLLM(config)


def process_legal_pdf(pdf_path: Union[str, Path], 
                     **kwargs) -> ProcessingResult:
    """Quick function to process a legal PDF.
    
    Args:
        pdf_path: Path to PDF file
        **kwargs: Processing options
    
    Returns:
        ProcessingResult
    """
    processor = create_processor(**kwargs)
    return processor.process_pdf(pdf_path)


def process_legal_text(text: str, 
                      document_type: str = "legal",
                      **kwargs) -> ProcessingResult:
    """Quick function to process legal text.
    
    Args:
        text: Input text
        document_type: Type of document
        **kwargs: Processing options
    
    Returns:
        ProcessingResult
    """
    processor = create_processor(**kwargs)
    return processor.process_text(text, document_type)