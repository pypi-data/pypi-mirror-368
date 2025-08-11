"""Main legal document processor."""

from typing import Dict, List, Optional, Any, Union, Tuple
import logging
import time
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

# Core imports
from ..core.config import Config
from ..core.chunk import SemanticChunk, ContentType, ImportanceLevel, LegalConcept, QualityMetrics

# PDF processing
from ..pdf.extractor import PDFExtractor, PDFPage
from ..pdf.font import FontAnalyzer, HierarchyLevel

# AI components
from ..ai.embeddings import EmbeddingGenerator, EmbeddingResult
from ..ai.clustering import SemanticClusterer, ClusteringResult
from ..ai.transformers import ContentClassifier, ClassificationResult
from ..ai.quality import QualityAssessor, QualityAssessment

# LLM integration
from ..llm.providers import LLMManager, LLMRequest, LLMResponse

# Legal analysis
from .analyzer import LegalAnalyzer, LegalStructure
from .validator import LegalValidator, ValidationResult


class ProcessingStage(Enum):
    """Processing stages."""
    INITIALIZATION = "initialization"
    PDF_EXTRACTION = "pdf_extraction"
    FONT_ANALYSIS = "font_analysis"
    STRUCTURE_DETECTION = "structure_detection"
    CONTENT_CLASSIFICATION = "content_classification"
    SEMANTIC_EMBEDDING = "semantic_embedding"
    CLUSTERING = "clustering"
    CHUNK_GENERATION = "chunk_generation"
    QUALITY_ASSESSMENT = "quality_assessment"
    VALIDATION = "validation"
    FINALIZATION = "finalization"


@dataclass
class ProcessingStats:
    """Processing statistics."""
    total_pages: int = 0
    total_text_blocks: int = 0
    total_chunks: int = 0
    processing_time: float = 0.0
    stage_times: Dict[str, float] = None
    quality_scores: Dict[str, float] = None
    validation_results: Dict[str, Any] = None
    errors: List[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.stage_times is None:
            self.stage_times = {}
        if self.quality_scores is None:
            self.quality_scores = {}
        if self.validation_results is None:
            self.validation_results = {}
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


@dataclass
class ProcessingResult:
    """Complete processing result."""
    chunks: List[SemanticChunk]
    stats: ProcessingStats
    legal_structure: Optional[LegalStructure] = None
    quality_assessments: List[QualityAssessment] = None
    validation_result: Optional[ValidationResult] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.quality_assessments is None:
            self.quality_assessments = []
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "chunks": [asdict(chunk) for chunk in self.chunks],
            "stats": asdict(self.stats),
            "legal_structure": asdict(self.legal_structure) if self.legal_structure else None,
            "quality_assessments": [asdict(qa) for qa in self.quality_assessments],
            "validation_result": asdict(self.validation_result) if self.validation_result else None,
            "metadata": self.metadata
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False, default=str)
    
    def save_to_file(self, file_path: Union[str, Path]) -> None:
        """Save result to JSON file."""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(self.to_json())


class LegalDocumentProcessor:
    """Main legal document processor with enterprise-grade semantic chunking."""
    
    def __init__(self, config: Optional[Config] = None, **kwargs):
        """Initialize the processor.
        
        Args:
            config: Configuration object
            **kwargs: Override configuration parameters
        """
        # Initialize configuration
        if config is None:
            config = Config.create_default()
        
        # Apply kwargs overrides
        if kwargs:
            config = self._apply_config_overrides(config, kwargs)
        
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize components
        self._initialize_components()
        
        # Processing state
        self.current_stage = None
        self.stage_start_time = None
    
    def _apply_config_overrides(self, config: Config, overrides: Dict[str, Any]) -> Config:
        """Apply configuration overrides."""
        # Handle common overrides
        if 'use_ollama' in overrides and overrides['use_ollama']:
            config.llm.primary_provider = 'ollama'
            if 'ollama_model' in overrides:
                config.ollama.model = overrides['ollama_model']
        
        if 'use_ollama_embeddings' in overrides and overrides['use_ollama_embeddings']:
            config.embedding.primary_provider = 'ollama'
        
        if 'openai_api_key' in overrides:
            config.openai.api_key = overrides['openai_api_key']
        
        if 'anthropic_api_key' in overrides:
            config.anthropic.api_key = overrides['anthropic_api_key']
        
        if 'quality_threshold' in overrides:
            config.quality.min_quality_score = overrides['quality_threshold']
        
        return config
    
    def _initialize_components(self):
        """Initialize all processing components."""
        try:
            # PDF processing
            self.pdf_extractor = PDFExtractor()
            self.font_analyzer = FontAnalyzer()
            
            # AI components
            self.embedding_generator = EmbeddingGenerator(self.config.embedding)
            self.clusterer = SemanticClusterer(self.config.clustering)
            self.classifier = ContentClassifier(self.config.ai)
            self.quality_assessor = QualityAssessor(self.config.quality)
            
            # LLM manager
            self.llm_manager = LLMManager(self.config)
            
            # Legal components
            self.legal_analyzer = LegalAnalyzer(self.config.legal)
            self.legal_validator = LegalValidator(self.config.legal)
            
            self.logger.info("All components initialized successfully")
        
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            raise
    
    def process_legal_pdf(self, pdf_path: Union[str, Path], **kwargs) -> ProcessingResult:
        """Process a legal PDF document.
        
        Args:
            pdf_path: Path to PDF file
            **kwargs: Processing options
        
        Returns:
            ProcessingResult with chunks and metadata
        """
        start_time = time.time()
        stats = ProcessingStats()
        
        try:
            self.logger.info(f"Starting processing of {pdf_path}")
            
            # Stage 1: PDF Extraction
            self._start_stage(ProcessingStage.PDF_EXTRACTION, stats)
            pages = self._extract_pdf_content(pdf_path)
            stats.total_pages = len(pages)
            stats.total_text_blocks = sum(len(page.text_blocks) for page in pages)
            self._end_stage(stats)
            
            # Stage 2: Font Analysis
            self._start_stage(ProcessingStage.FONT_ANALYSIS, stats)
            font_hierarchy = self._analyze_font_hierarchy(pages)
            self._end_stage(stats)
            
            # Stage 3: Structure Detection
            self._start_stage(ProcessingStage.STRUCTURE_DETECTION, stats)
            legal_structure = self._detect_legal_structure(pages, font_hierarchy)
            self._end_stage(stats)
            
            # Stage 4: Content Classification
            self._start_stage(ProcessingStage.CONTENT_CLASSIFICATION, stats)
            classified_blocks = self._classify_content(pages)
            self._end_stage(stats)
            
            # Stage 5: Semantic Embedding
            self._start_stage(ProcessingStage.SEMANTIC_EMBEDDING, stats)
            embeddings = self._generate_embeddings(classified_blocks)
            self._end_stage(stats)
            
            # Stage 6: Clustering
            self._start_stage(ProcessingStage.CLUSTERING, stats)
            clustering_result = self._perform_clustering(embeddings, classified_blocks)
            self._end_stage(stats)
            
            # Stage 7: Chunk Generation
            self._start_stage(ProcessingStage.CHUNK_GENERATION, stats)
            chunks = self._generate_semantic_chunks(
                clustering_result, classified_blocks, legal_structure, font_hierarchy
            )
            stats.total_chunks = len(chunks)
            self._end_stage(stats)
            
            # Stage 8: Quality Assessment
            self._start_stage(ProcessingStage.QUALITY_ASSESSMENT, stats)
            quality_assessments = self._assess_quality(chunks)
            stats.quality_scores = self._calculate_quality_stats(quality_assessments)
            self._end_stage(stats)
            
            # Stage 9: Validation
            self._start_stage(ProcessingStage.VALIDATION, stats)
            validation_result = self._validate_chunks(chunks, legal_structure)
            stats.validation_results = asdict(validation_result)
            self._end_stage(stats)
            
            # Stage 10: Finalization
            self._start_stage(ProcessingStage.FINALIZATION, stats)
            final_chunks = self._finalize_chunks(chunks, quality_assessments, validation_result)
            self._end_stage(stats)
            
            # Complete processing
            stats.processing_time = time.time() - start_time
            
            result = ProcessingResult(
                chunks=final_chunks,
                stats=stats,
                legal_structure=legal_structure,
                quality_assessments=quality_assessments,
                validation_result=validation_result,
                metadata={
                    "pdf_path": str(pdf_path),
                    "processing_timestamp": time.time(),
                    "config_summary": self._get_config_summary()
                }
            )
            
            self.logger.info(f"Processing completed successfully in {stats.processing_time:.2f}s")
            self.logger.info(f"Generated {len(final_chunks)} semantic chunks")
            
            return result
        
        except Exception as e:
            stats.errors.append(str(e))
            stats.processing_time = time.time() - start_time
            self.logger.error(f"Processing failed: {e}")
            raise
    
    def _start_stage(self, stage: ProcessingStage, stats: ProcessingStats):
        """Start a processing stage."""
        self.current_stage = stage
        self.stage_start_time = time.time()
        self.logger.debug(f"Starting stage: {stage.value}")
    
    def _end_stage(self, stats: ProcessingStats):
        """End a processing stage."""
        if self.current_stage and self.stage_start_time:
            stage_time = time.time() - self.stage_start_time
            stats.stage_times[self.current_stage.value] = stage_time
            self.logger.debug(f"Completed stage: {self.current_stage.value} in {stage_time:.2f}s")
        
        self.current_stage = None
        self.stage_start_time = None
    
    def _extract_pdf_content(self, pdf_path: Union[str, Path]) -> List[PDFPage]:
        """Extract content from PDF."""
        try:
            return self.pdf_extractor.extract_pages(pdf_path)
        except Exception as e:
            self.logger.error(f"PDF extraction failed: {e}")
            raise
    
    def _analyze_font_hierarchy(self, pages: List[PDFPage]) -> Dict[str, Any]:
        """Analyze font hierarchy."""
        try:
            return self.font_analyzer.analyze_hierarchy(pages)
        except Exception as e:
            self.logger.error(f"Font analysis failed: {e}")
            return {}
    
    def _detect_legal_structure(self, pages: List[PDFPage], font_hierarchy: Dict[str, Any]) -> LegalStructure:
        """Detect legal document structure."""
        try:
            return self.legal_analyzer.analyze_structure(pages, font_hierarchy)
        except Exception as e:
            self.logger.error(f"Structure detection failed: {e}")
            return LegalStructure(sections=[], articles=[], references=[])
    
    def _classify_content(self, pages: List[PDFPage]) -> List[Tuple[Any, ClassificationResult]]:
        """Classify content blocks."""
        classified_blocks = []
        
        for page in pages:
            for block in page.text_blocks:
                try:
                    classification = self.classifier.classify_content(block.text)
                    classified_blocks.append((block, classification))
                except Exception as e:
                    self.logger.warning(f"Classification failed for block: {e}")
                    # Create default classification
                    default_classification = ClassificationResult(
                        content_type=ContentType.GENERAL,
                        importance_level=ImportanceLevel.MEDIUM,
                        legal_concepts=[],
                        confidence_scores={},
                        processing_time=0.0
                    )
                    classified_blocks.append((block, default_classification))
        
        return classified_blocks
    
    def _generate_embeddings(self, classified_blocks: List[Tuple[Any, ClassificationResult]]) -> List[EmbeddingResult]:
        """Generate embeddings for content blocks."""
        embeddings = []
        
        for block, classification in classified_blocks:
            try:
                embedding = self.embedding_generator.generate_embedding(block.text)
                embeddings.append(embedding)
            except Exception as e:
                self.logger.warning(f"Embedding generation failed: {e}")
                # Create dummy embedding
                import numpy as np
                dummy_embedding = EmbeddingResult(
                    vector=np.zeros(384),  # Default dimension
                    model="dummy",
                    processing_time=0.0,
                    metadata={"error": str(e)}
                )
                embeddings.append(dummy_embedding)
        
        return embeddings
    
    def _perform_clustering(self, embeddings: List[EmbeddingResult], classified_blocks: List[Tuple[Any, ClassificationResult]]) -> ClusteringResult:
        """Perform semantic clustering."""
        try:
            # Extract vectors
            vectors = [emb.vector for emb in embeddings]
            texts = [block.text for block, _ in classified_blocks]
            
            return self.clusterer.cluster_semantic_content(vectors, texts)
        except Exception as e:
            self.logger.error(f"Clustering failed: {e}")
            # Return default clustering
            import numpy as np
            return ClusteringResult(
                cluster_labels=np.zeros(len(embeddings), dtype=int),
                cluster_centers=np.array([]),
                cluster_summaries=[],
                quality_metrics={},
                processing_time=0.0,
                metadata={"error": str(e)}
            )
    
    def _generate_semantic_chunks(
        self, 
        clustering_result: ClusteringResult,
        classified_blocks: List[Tuple[Any, ClassificationResult]],
        legal_structure: LegalStructure,
        font_hierarchy: Dict[str, Any]
    ) -> List[SemanticChunk]:
        """Generate semantic chunks from clustered content."""
        chunks = []
        
        # Group blocks by cluster
        cluster_groups = {}
        for i, (block, classification) in enumerate(classified_blocks):
            cluster_id = clustering_result.cluster_labels[i]
            if cluster_id not in cluster_groups:
                cluster_groups[cluster_id] = []
            cluster_groups[cluster_id].append((block, classification))
        
        # Create chunks from clusters
        for cluster_id, group in cluster_groups.items():
            try:
                chunk = self._create_chunk_from_group(
                    cluster_id, group, legal_structure, font_hierarchy
                )
                chunks.append(chunk)
            except Exception as e:
                self.logger.warning(f"Failed to create chunk for cluster {cluster_id}: {e}")
        
        return chunks
    
    def _create_chunk_from_group(
        self,
        cluster_id: int,
        group: List[Tuple[Any, ClassificationResult]],
        legal_structure: LegalStructure,
        font_hierarchy: Dict[str, Any]
    ) -> SemanticChunk:
        """Create a semantic chunk from a group of blocks."""
        # Combine text content
        content_parts = []
        classifications = []
        
        for block, classification in group:
            content_parts.append(block.text)
            classifications.append(classification)
        
        content = "\n\n".join(content_parts)
        
        # Determine dominant content type and importance
        content_types = [c.content_type for c in classifications]
        importance_levels = [c.importance_level for c in classifications]
        
        # Use most common content type
        dominant_content_type = max(set(content_types), key=content_types.count)
        dominant_importance = max(set(importance_levels), key=importance_levels.count)
        
        # Collect legal concepts
        all_concepts = []
        for classification in classifications:
            all_concepts.extend(classification.legal_concepts)
        
        # Remove duplicates while preserving order
        unique_concepts = []
        seen = set()
        for concept in all_concepts:
            if concept.term not in seen:
                unique_concepts.append(concept)
                seen.add(concept.term)
        
        # Create chunk
        chunk = SemanticChunk(
            id=f"chunk_{cluster_id}",
            content=content,
            content_type=dominant_content_type,
            importance_level=dominant_importance,
            legal_concepts=unique_concepts,
            metadata={
                "cluster_id": cluster_id,
                "block_count": len(group),
                "font_hierarchy": font_hierarchy,
                "legal_structure_refs": self._extract_structure_references(content, legal_structure)
            },
            quality_metrics=QualityMetrics()  # Will be filled later
        )
        
        return chunk
    
    def _extract_structure_references(self, content: str, legal_structure: LegalStructure) -> List[str]:
        """Extract references to legal structure elements."""
        references = []
        
        # Check for article references
        for article in legal_structure.articles:
            if article.number and f"madde {article.number}" in content.lower():
                references.append(f"article_{article.number}")
        
        # Check for section references
        for section in legal_structure.sections:
            if section.title and section.title.lower() in content.lower():
                references.append(f"section_{section.title}")
        
        return references
    
    def _assess_quality(self, chunks: List[SemanticChunk]) -> List[QualityAssessment]:
        """Assess quality of chunks."""
        return self.quality_assessor.batch_assess_quality(chunks)
    
    def _calculate_quality_stats(self, assessments: List[QualityAssessment]) -> Dict[str, float]:
        """Calculate quality statistics."""
        if not assessments:
            return {}
        
        scores = [a.overall_score for a in assessments]
        
        return {
            "mean_quality": sum(scores) / len(scores),
            "min_quality": min(scores),
            "max_quality": max(scores),
            "quality_std": np.std(scores) if len(scores) > 1 else 0.0
        }
    
    def _validate_chunks(self, chunks: List[SemanticChunk], legal_structure: LegalStructure) -> ValidationResult:
        """Validate chunks against legal requirements."""
        return self.legal_validator.validate_chunks(chunks, legal_structure)
    
    def _finalize_chunks(self, chunks: List[SemanticChunk], quality_assessments: List[QualityAssessment], validation_result: ValidationResult) -> List[SemanticChunk]:
        """Finalize chunks with quality metrics."""
        final_chunks = []
        
        for i, chunk in enumerate(chunks):
            # Update quality metrics
            if i < len(quality_assessments):
                assessment = quality_assessments[i]
                chunk.quality_metrics = QualityMetrics(
                    coherence=assessment.dimension_scores.get('coherence', 0.0),
                    completeness=assessment.dimension_scores.get('completeness', 0.0),
                    readability=assessment.dimension_scores.get('readability', 0.0),
                    consistency=assessment.dimension_scores.get('consistency', 0.0)
                )
            
            # Filter low-quality chunks if configured
            if (chunk.quality_metrics and 
                hasattr(chunk.quality_metrics, 'coherence') and
                chunk.quality_metrics.coherence >= self.config.quality.min_quality_score):
                final_chunks.append(chunk)
            elif not self.config.quality.filter_low_quality:
                final_chunks.append(chunk)
        
        return final_chunks
    
    def _get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary."""
        return {
            "llm_provider": self.config.llm.primary_provider,
            "embedding_provider": self.config.embedding.primary_provider,
            "clustering_method": self.config.clustering.primary_method.value,
            "quality_threshold": self.config.quality.min_quality_score
        }
    
    def process_batch(self, pdf_paths: List[Union[str, Path]], **kwargs) -> List[ProcessingResult]:
        """Process multiple PDF files."""
        results = []
        
        for pdf_path in pdf_paths:
            try:
                result = self.process_legal_pdf(pdf_path, **kwargs)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Failed to process {pdf_path}: {e}")
                # Create error result
                error_result = ProcessingResult(
                    chunks=[],
                    stats=ProcessingStats(errors=[str(e)]),
                    metadata={"pdf_path": str(pdf_path), "error": str(e)}
                )
                results.append(error_result)
        
        return results
    
    def get_processing_summary(self, result: ProcessingResult) -> str:
        """Get human-readable processing summary."""
        summary_parts = [
            f"📄 Legal Document Processing Summary",
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"📊 Statistics:",
            f"  • Total Pages: {result.stats.total_pages}",
            f"  • Text Blocks: {result.stats.total_text_blocks}",
            f"  • Semantic Chunks: {result.stats.total_chunks}",
            f"  • Processing Time: {result.stats.processing_time:.2f}s",
            f"",
            f"🎯 Quality Metrics:"
        ]
        
        if result.stats.quality_scores:
            for metric, score in result.stats.quality_scores.items():
                summary_parts.append(f"  • {metric.replace('_', ' ').title()}: {score:.3f}")
        
        if result.stats.stage_times:
            summary_parts.extend([
                f"",
                f"⏱️ Stage Timings:"
            ])
            for stage, time_taken in result.stats.stage_times.items():
                summary_parts.append(f"  • {stage.replace('_', ' ').title()}: {time_taken:.2f}s")
        
        if result.stats.errors:
            summary_parts.extend([
                f"",
                f"❌ Errors:"
            ])
            for error in result.stats.errors:
                summary_parts.append(f"  • {error}")
        
        if result.stats.warnings:
            summary_parts.extend([
                f"",
                f"⚠️ Warnings:"
            ])
            for warning in result.stats.warnings:
                summary_parts.append(f"  • {warning}")
        
        return "\n".join(summary_parts)