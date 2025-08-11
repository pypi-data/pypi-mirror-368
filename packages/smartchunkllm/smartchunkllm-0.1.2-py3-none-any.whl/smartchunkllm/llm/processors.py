"""LLM processors for different legal document processing tasks."""

from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod
import json
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed

from .providers import LLMManager, LLMRequest, LLMResponse
from .prompts import PromptManager, PromptType
from ..core.types import SemanticChunk


@dataclass
class ProcessingResult:
    """Result of LLM processing."""
    success: bool
    result: Any
    error: Optional[str] = None
    processing_time: float = 0.0
    tokens_used: int = 0
    model_used: str = ""
    confidence_score: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class BatchProcessingResult:
    """Result of batch LLM processing."""
    total_items: int
    successful_items: int
    failed_items: int
    results: List[ProcessingResult]
    total_processing_time: float
    total_tokens_used: int
    error_summary: List[str] = None
    
    def __post_init__(self):
        if self.error_summary is None:
            self.error_summary = []
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        return self.successful_items / self.total_items if self.total_items > 0 else 0.0


class LLMProcessorBase(ABC):
    """Base class for LLM processors."""
    
    def __init__(self, 
                 llm_manager: LLMManager,
                 prompt_manager: PromptManager,
                 max_retries: int = 3,
                 timeout: float = 30.0):
        """Initialize LLM processor.
        
        Args:
            llm_manager: LLM manager instance
            prompt_manager: Prompt manager instance
            max_retries: Maximum number of retries for failed requests
            timeout: Request timeout in seconds
        """
        self.llm_manager = llm_manager
        self.prompt_manager = prompt_manager
        self.max_retries = max_retries
        self.timeout = timeout
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def process(self, *args, **kwargs) -> ProcessingResult:
        """Process input and return result."""
        pass
    
    def _create_request(self, 
                       prompt: str, 
                       temperature: float = 0.1,
                       max_tokens: Optional[int] = None,
                       **kwargs) -> LLMRequest:
        """Create LLM request."""
        return LLMRequest(
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
    
    def _process_with_retry(self, request: LLMRequest) -> ProcessingResult:
        """Process request with retry logic."""
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                response = self.llm_manager.generate(request)
                
                if response.success:
                    return ProcessingResult(
                        success=True,
                        result=response.content,
                        processing_time=response.processing_time,
                        tokens_used=response.tokens_used,
                        model_used=response.model_used,
                        confidence_score=response.confidence_score
                    )
                else:
                    last_error = response.error
                    
            except Exception as e:
                last_error = str(e)
                self.logger.warning(f"Attempt {attempt + 1} failed: {last_error}")
        
        return ProcessingResult(
            success=False,
            result=None,
            error=f"Failed after {self.max_retries + 1} attempts. Last error: {last_error}"
        )
    
    async def _process_with_retry_async(self, request: LLMRequest) -> ProcessingResult:
        """Process request with retry logic (async)."""
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                response = await self.llm_manager.generate_async(request)
                
                if response.success:
                    return ProcessingResult(
                        success=True,
                        result=response.content,
                        processing_time=response.processing_time,
                        tokens_used=response.tokens_used,
                        model_used=response.model_used,
                        confidence_score=response.confidence_score
                    )
                else:
                    last_error = response.error
                    
            except Exception as e:
                last_error = str(e)
                self.logger.warning(f"Async attempt {attempt + 1} failed: {last_error}")
        
        return ProcessingResult(
            success=False,
            result=None,
            error=f"Failed after {self.max_retries + 1} attempts. Last error: {last_error}"
        )
    
    def process_batch(self, 
                     items: List[Any], 
                     max_workers: int = 4,
                     use_async: bool = False) -> BatchProcessingResult:
        """Process multiple items in batch."""
        if use_async:
            return asyncio.run(self._process_batch_async(items, max_workers))
        else:
            return self._process_batch_sync(items, max_workers)
    
    def _process_batch_sync(self, items: List[Any], max_workers: int) -> BatchProcessingResult:
        """Process batch synchronously."""
        import time
        start_time = time.time()
        
        results = []
        total_tokens = 0
        errors = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_item = {executor.submit(self.process, item): item for item in items}
            
            # Collect results
            for future in as_completed(future_to_item):
                try:
                    result = future.result()
                    results.append(result)
                    total_tokens += result.tokens_used
                    
                    if not result.success:
                        errors.append(result.error)
                        
                except Exception as e:
                    error_msg = f"Processing failed: {str(e)}"
                    results.append(ProcessingResult(
                        success=False,
                        result=None,
                        error=error_msg
                    ))
                    errors.append(error_msg)
        
        successful_items = sum(1 for r in results if r.success)
        failed_items = len(results) - successful_items
        
        return BatchProcessingResult(
            total_items=len(items),
            successful_items=successful_items,
            failed_items=failed_items,
            results=results,
            total_processing_time=time.time() - start_time,
            total_tokens_used=total_tokens,
            error_summary=errors
        )
    
    async def _process_batch_async(self, items: List[Any], max_workers: int) -> BatchProcessingResult:
        """Process batch asynchronously."""
        import time
        start_time = time.time()
        
        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(max_workers)
        
        async def process_with_semaphore(item):
            async with semaphore:
                return await self.process_async(item)
        
        # Process all items
        tasks = [process_with_semaphore(item) for item in items]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        processed_results = []
        total_tokens = 0
        errors = []
        
        for result in results:
            if isinstance(result, Exception):
                error_msg = f"Processing failed: {str(result)}"
                processed_results.append(ProcessingResult(
                    success=False,
                    result=None,
                    error=error_msg
                ))
                errors.append(error_msg)
            else:
                processed_results.append(result)
                total_tokens += result.tokens_used
                
                if not result.success:
                    errors.append(result.error)
        
        successful_items = sum(1 for r in processed_results if r.success)
        failed_items = len(processed_results) - successful_items
        
        return BatchProcessingResult(
            total_items=len(items),
            successful_items=successful_items,
            failed_items=failed_items,
            results=processed_results,
            total_processing_time=time.time() - start_time,
            total_tokens_used=total_tokens,
            error_summary=errors
        )
    
    async def process_async(self, *args, **kwargs) -> ProcessingResult:
        """Async version of process method."""
        # Default implementation calls sync version
        # Subclasses should override for true async processing
        return self.process(*args, **kwargs)


class ChunkProcessor(LLMProcessorBase):
    """Processor for semantic chunking tasks."""
    
    def process(self, 
               text: str, 
               chunk_size_hint: Optional[int] = None,
               content_type: Optional[str] = None) -> ProcessingResult:
        """Process text for semantic chunking.
        
        Args:
            text: Input text to chunk
            chunk_size_hint: Suggested chunk size
            content_type: Expected content type
        """
        try:
            # Prepare prompt
            prompt = self.prompt_manager.format_prompt(
                "semantic_chunking",
                text=text
            )
            
            # Create request
            request = self._create_request(
                prompt=prompt,
                temperature=0.1,
                max_tokens=4000
            )
            
            # Process with retry
            result = self._process_with_retry(request)
            
            if result.success:
                # Parse the result to extract chunks
                chunks = self._parse_chunking_result(result.result)
                result.result = chunks
                result.metadata = {
                    "chunk_count": len(chunks),
                    "input_length": len(text),
                    "chunk_size_hint": chunk_size_hint,
                    "content_type": content_type
                }
            
            return result
            
        except Exception as e:
            return ProcessingResult(
                success=False,
                result=None,
                error=f"Chunking failed: {str(e)}"
            )
    
    def optimize_chunk(self, 
                      chunk_content: str,
                      content_type: str,
                      importance_level: str,
                      quality_score: float) -> ProcessingResult:
        """Optimize an existing chunk."""
        try:
            prompt = self.prompt_manager.format_prompt(
                "chunk_optimization",
                chunk_content=chunk_content,
                content_type=content_type,
                importance_level=importance_level,
                quality_score=quality_score
            )
            
            request = self._create_request(prompt=prompt, temperature=0.1)
            return self._process_with_retry(request)
            
        except Exception as e:
            return ProcessingResult(
                success=False,
                result=None,
                error=f"Chunk optimization failed: {str(e)}"
            )
    
    def evaluate_chunk_merging(self, 
                              chunk1: SemanticChunk,
                              chunk2: SemanticChunk) -> ProcessingResult:
        """Evaluate if two chunks should be merged."""
        try:
            prompt = self.prompt_manager.format_prompt(
                "chunk_merging",
                chunk1_content=chunk1.content,
                chunk1_type=chunk1.metadata.get("content_type", "unknown"),
                chunk2_content=chunk2.content,
                chunk2_type=chunk2.metadata.get("content_type", "unknown")
            )
            
            request = self._create_request(prompt=prompt, temperature=0.1)
            result = self._process_with_retry(request)
            
            if result.success:
                # Parse merging decision
                decision = self._parse_merging_decision(result.result)
                result.result = decision
            
            return result
            
        except Exception as e:
            return ProcessingResult(
                success=False,
                result=None,
                error=f"Chunk merging evaluation failed: {str(e)}"
            )
    
    def _parse_chunking_result(self, result_text: str) -> List[Dict[str, Any]]:
        """Parse chunking result from LLM response."""
        chunks = []
        
        try:
            # Simple parsing logic - can be enhanced
            lines = result_text.split('\n')
            current_chunk = {}
            
            for line in lines:
                line = line.strip()
                if line.startswith('- Parça ID:'):
                    if current_chunk:
                        chunks.append(current_chunk)
                    current_chunk = {'id': line.split(':')[1].strip()}
                elif line.startswith('- İçerik Türü:'):
                    current_chunk['content_type'] = line.split(':')[1].strip()
                elif line.startswith('- Önem Düzeyi:'):
                    current_chunk['importance_level'] = line.split(':')[1].strip()
                elif line.startswith('- İçerik:'):
                    current_chunk['content'] = line.split(':', 1)[1].strip()
                elif line.startswith('- Hukuki Kavramlar:'):
                    concepts = line.split(':', 1)[1].strip()
                    current_chunk['legal_concepts'] = [c.strip() for c in concepts.split(',')]
            
            if current_chunk:
                chunks.append(current_chunk)
                
        except Exception as e:
            self.logger.warning(f"Failed to parse chunking result: {e}")
            # Fallback: return raw text as single chunk
            chunks = [{
                'id': '1',
                'content': result_text,
                'content_type': 'unknown',
                'importance_level': 'medium',
                'legal_concepts': []
            }]
        
        return chunks
    
    def _parse_merging_decision(self, result_text: str) -> Dict[str, Any]:
        """Parse merging decision from LLM response."""
        try:
            # Extract decision and reasoning
            lines = result_text.split('\n')
            decision = "AYRI_TUT"  # default
            reasoning = ""
            merged_content = ""
            
            for line in lines:
                if line.startswith('Karar:'):
                    decision = line.split(':')[1].strip()
                elif line.startswith('Gerekçe:'):
                    reasoning = line.split(':', 1)[1].strip()
                elif line.startswith('Birleştirilmiş İçerik:'):
                    merged_content = line.split(':', 1)[1].strip()
            
            return {
                'should_merge': decision == 'BİRLEŞTİR',
                'reasoning': reasoning,
                'merged_content': merged_content if decision == 'BİRLEŞTİR' else None
            }
            
        except Exception as e:
            self.logger.warning(f"Failed to parse merging decision: {e}")
            return {
                'should_merge': False,
                'reasoning': 'Parsing failed',
                'merged_content': None
            }


class AnalysisProcessor(LLMProcessorBase):
    """Processor for legal document analysis tasks."""
    
    def analyze_structure(self, document_text: str) -> ProcessingResult:
        """Analyze document structure."""
        try:
            prompt = self.prompt_manager.format_prompt(
                "structure_analysis",
                document_text=document_text
            )
            
            request = self._create_request(
                prompt=prompt,
                temperature=0.1,
                max_tokens=3000
            )
            
            result = self._process_with_retry(request)
            
            if result.success:
                # Parse JSON structure
                try:
                    structure = json.loads(result.result)
                    result.result = structure
                except json.JSONDecodeError:
                    # Fallback parsing
                    result.result = self._parse_structure_fallback(result.result)
            
            return result
            
        except Exception as e:
            return ProcessingResult(
                success=False,
                result=None,
                error=f"Structure analysis failed: {str(e)}"
            )
    
    def extract_legal_concepts(self, text: str) -> ProcessingResult:
        """Extract legal concepts from text."""
        try:
            prompt = self.prompt_manager.format_prompt(
                "legal_concept_extraction",
                text=text
            )
            
            request = self._create_request(prompt=prompt, temperature=0.1)
            result = self._process_with_retry(request)
            
            if result.success:
                try:
                    concepts = json.loads(result.result)
                    result.result = concepts
                except json.JSONDecodeError:
                    result.result = self._parse_concepts_fallback(result.result)
            
            return result
            
        except Exception as e:
            return ProcessingResult(
                success=False,
                result=None,
                error=f"Legal concept extraction failed: {str(e)}"
            )
    
    def analyze_references(self, text: str) -> ProcessingResult:
        """Analyze legal references in text."""
        try:
            prompt = self.prompt_manager.format_prompt(
                "reference_analysis",
                text=text
            )
            
            request = self._create_request(prompt=prompt, temperature=0.1)
            result = self._process_with_retry(request)
            
            if result.success:
                try:
                    references = json.loads(result.result)
                    result.result = references
                except json.JSONDecodeError:
                    result.result = self._parse_references_fallback(result.result)
            
            return result
            
        except Exception as e:
            return ProcessingResult(
                success=False,
                result=None,
                error=f"Reference analysis failed: {str(e)}"
            )
    
    def _parse_structure_fallback(self, text: str) -> Dict[str, Any]:
        """Fallback structure parsing."""
        return {
            "document_type": "unknown",
            "title": "Unknown Document",
            "sections": [],
            "articles": [],
            "parsing_method": "fallback"
        }
    
    def _parse_concepts_fallback(self, text: str) -> Dict[str, Any]:
        """Fallback concept parsing."""
        return {
            "legal_terms": [],
            "obligations": [],
            "rights": [],
            "sanctions": [],
            "procedures": [],
            "references": [],
            "parsing_method": "fallback"
        }
    
    def _parse_references_fallback(self, text: str) -> Dict[str, Any]:
        """Fallback reference parsing."""
        return {
            "internal_references": [],
            "external_references": [],
            "general_references": [],
            "parsing_method": "fallback"
        }


class ClassificationProcessor(LLMProcessorBase):
    """Processor for content classification tasks."""
    
    def classify_content_type(self, text: str) -> ProcessingResult:
        """Classify content type of text."""
        try:
            prompt = self.prompt_manager.format_prompt(
                "content_type_classification",
                text=text
            )
            
            request = self._create_request(prompt=prompt, temperature=0.1)
            result = self._process_with_retry(request)
            
            if result.success:
                classification = self._parse_classification_result(result.result)
                result.result = classification
            
            return result
            
        except Exception as e:
            return ProcessingResult(
                success=False,
                result=None,
                error=f"Content type classification failed: {str(e)}"
            )
    
    def classify_importance(self, text: str, content_type: str) -> ProcessingResult:
        """Classify importance level of text."""
        try:
            prompt = self.prompt_manager.format_prompt(
                "importance_classification",
                text=text,
                content_type=content_type
            )
            
            request = self._create_request(prompt=prompt, temperature=0.1)
            result = self._process_with_retry(request)
            
            if result.success:
                classification = self._parse_importance_result(result.result)
                result.result = classification
            
            return result
            
        except Exception as e:
            return ProcessingResult(
                success=False,
                result=None,
                error=f"Importance classification failed: {str(e)}"
            )
    
    def _parse_classification_result(self, text: str) -> Dict[str, Any]:
        """Parse content type classification result."""
        try:
            lines = text.split('\n')
            result = {
                'content_type': 'GENEL',
                'confidence_score': 0.5,
                'reasoning': '',
                'key_indicators': []
            }
            
            for line in lines:
                if line.startswith('İçerik Türü:'):
                    result['content_type'] = line.split(':')[1].strip()
                elif line.startswith('Güven Skoru:'):
                    try:
                        result['confidence_score'] = float(line.split(':')[1].strip())
                    except ValueError:
                        pass
                elif line.startswith('Gerekçe:'):
                    result['reasoning'] = line.split(':', 1)[1].strip()
                elif line.startswith('Anahtar Göstergeler:'):
                    indicators = line.split(':', 1)[1].strip()
                    result['key_indicators'] = [i.strip() for i in indicators.split(',')]
            
            return result
            
        except Exception as e:
            self.logger.warning(f"Failed to parse classification result: {e}")
            return {
                'content_type': 'GENEL',
                'confidence_score': 0.5,
                'reasoning': 'Parsing failed',
                'key_indicators': []
            }
    
    def _parse_importance_result(self, text: str) -> Dict[str, Any]:
        """Parse importance classification result."""
        try:
            lines = text.split('\n')
            result = {
                'importance_level': 'ORTA',
                'confidence_score': 0.5,
                'reasoning': '',
                'impact_area': ''
            }
            
            for line in lines:
                if line.startswith('Önem Düzeyi:'):
                    result['importance_level'] = line.split(':')[1].strip()
                elif line.startswith('Güven Skoru:'):
                    try:
                        result['confidence_score'] = float(line.split(':')[1].strip())
                    except ValueError:
                        pass
                elif line.startswith('Gerekçe:'):
                    result['reasoning'] = line.split(':', 1)[1].strip()
                elif line.startswith('Etki Alanı:'):
                    result['impact_area'] = line.split(':', 1)[1].strip()
            
            return result
            
        except Exception as e:
            self.logger.warning(f"Failed to parse importance result: {e}")
            return {
                'importance_level': 'ORTA',
                'confidence_score': 0.5,
                'reasoning': 'Parsing failed',
                'impact_area': ''
            }


class QualityProcessor(LLMProcessorBase):
    """Processor for quality assessment tasks."""
    
    def assess_chunk_quality(self, 
                           chunk_content: str,
                           content_type: str,
                           importance_level: str) -> ProcessingResult:
        """Assess quality of a semantic chunk."""
        try:
            prompt = self.prompt_manager.format_prompt(
                "chunk_quality_assessment",
                chunk_content=chunk_content,
                content_type=content_type,
                importance_level=importance_level,
                content_length=len(chunk_content)
            )
            
            request = self._create_request(
                prompt=prompt,
                temperature=0.1,
                max_tokens=2000
            )
            
            result = self._process_with_retry(request)
            
            if result.success:
                try:
                    quality_assessment = json.loads(result.result)
                    result.result = quality_assessment
                except json.JSONDecodeError:
                    result.result = self._parse_quality_fallback(result.result)
            
            return result
            
        except Exception as e:
            return ProcessingResult(
                success=False,
                result=None,
                error=f"Quality assessment failed: {str(e)}"
            )
    
    def compare_chunk_quality(self, 
                            chunk_a: SemanticChunk,
                            chunk_b: SemanticChunk) -> ProcessingResult:
        """Compare quality of two chunks."""
        try:
            prompt = self.prompt_manager.format_prompt(
                "comparative_quality",
                chunk_a_content=chunk_a.content,
                chunk_a_type=chunk_a.metadata.get("content_type", "unknown"),
                chunk_b_content=chunk_b.content,
                chunk_b_type=chunk_b.metadata.get("content_type", "unknown")
            )
            
            request = self._create_request(prompt=prompt, temperature=0.1)
            result = self._process_with_retry(request)
            
            if result.success:
                try:
                    comparison = json.loads(result.result)
                    result.result = comparison
                except json.JSONDecodeError:
                    result.result = self._parse_comparison_fallback(result.result)
            
            return result
            
        except Exception as e:
            return ProcessingResult(
                success=False,
                result=None,
                error=f"Quality comparison failed: {str(e)}"
            )
    
    def _parse_quality_fallback(self, text: str) -> Dict[str, Any]:
        """Fallback quality assessment parsing."""
        return {
            "coherence": {"score": 0.5, "explanation": "Parsing failed"},
            "completeness": {"score": 0.5, "explanation": "Parsing failed"},
            "readability": {"score": 0.5, "explanation": "Parsing failed"},
            "consistency": {"score": 0.5, "explanation": "Parsing failed"},
            "relevance": {"score": 0.5, "explanation": "Parsing failed"},
            "overall_score": 0.5,
            "strengths": [],
            "weaknesses": ["Quality assessment parsing failed"],
            "improvement_suggestions": ["Retry quality assessment"]
        }
    
    def _parse_comparison_fallback(self, text: str) -> Dict[str, Any]:
        """Fallback comparison parsing."""
        return {
            "better_chunk": "EQUAL",
            "quality_differences": {
                "coherence": "EQUAL - Parsing failed",
                "completeness": "EQUAL - Parsing failed",
                "readability": "EQUAL - Parsing failed"
            },
            "recommendation": "Unable to determine due to parsing failure",
            "improvement_areas": ["Retry comparison analysis"]
        }


class LLMProcessor:
    """Main LLM processor that coordinates all specialized processors."""
    
    def __init__(self, 
                 llm_manager: LLMManager,
                 prompt_manager: Optional[PromptManager] = None,
                 max_retries: int = 3,
                 timeout: float = 30.0):
        """Initialize main LLM processor.
        
        Args:
            llm_manager: LLM manager instance
            prompt_manager: Prompt manager instance (creates new if None)
            max_retries: Maximum retries for failed requests
            timeout: Request timeout in seconds
        """
        self.llm_manager = llm_manager
        self.prompt_manager = prompt_manager or PromptManager()
        
        # Initialize specialized processors
        self.chunk_processor = ChunkProcessor(
            llm_manager, self.prompt_manager, max_retries, timeout
        )
        self.analysis_processor = AnalysisProcessor(
            llm_manager, self.prompt_manager, max_retries, timeout
        )
        self.classification_processor = ClassificationProcessor(
            llm_manager, self.prompt_manager, max_retries, timeout
        )
        self.quality_processor = QualityProcessor(
            llm_manager, self.prompt_manager, max_retries, timeout
        )
        
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def process_document_complete(self, 
                                document_text: str,
                                include_structure: bool = True,
                                include_concepts: bool = True,
                                include_references: bool = True,
                                chunk_size_hint: Optional[int] = None) -> Dict[str, ProcessingResult]:
        """Complete document processing pipeline.
        
        Args:
            document_text: Input document text
            include_structure: Whether to analyze structure
            include_concepts: Whether to extract concepts
            include_references: Whether to analyze references
            chunk_size_hint: Suggested chunk size
        
        Returns:
            Dictionary of processing results
        """
        results = {}
        
        # 1. Semantic chunking
        self.logger.info("Starting semantic chunking...")
        results['chunking'] = self.chunk_processor.process(
            document_text, chunk_size_hint
        )
        
        # 2. Structure analysis
        if include_structure:
            self.logger.info("Analyzing document structure...")
            results['structure'] = self.analysis_processor.analyze_structure(
                document_text
            )
        
        # 3. Legal concept extraction
        if include_concepts:
            self.logger.info("Extracting legal concepts...")
            results['concepts'] = self.analysis_processor.extract_legal_concepts(
                document_text
            )
        
        # 4. Reference analysis
        if include_references:
            self.logger.info("Analyzing references...")
            results['references'] = self.analysis_processor.analyze_references(
                document_text
            )
        
        # 5. Process chunks if chunking was successful
        if results['chunking'].success and results['chunking'].result:
            chunks = results['chunking'].result
            
            # Classify each chunk
            self.logger.info(f"Classifying {len(chunks)} chunks...")
            chunk_classifications = []
            
            for i, chunk in enumerate(chunks):
                content = chunk.get('content', '')
                
                # Content type classification
                content_type_result = self.classification_processor.classify_content_type(content)
                
                # Importance classification
                content_type = 'GENEL'
                if content_type_result.success:
                    content_type = content_type_result.result.get('content_type', 'GENEL')
                
                importance_result = self.classification_processor.classify_importance(
                    content, content_type
                )
                
                # Quality assessment
                importance_level = 'ORTA'
                if importance_result.success:
                    importance_level = importance_result.result.get('importance_level', 'ORTA')
                
                quality_result = self.quality_processor.assess_chunk_quality(
                    content, content_type, importance_level
                )
                
                chunk_classifications.append({
                    'chunk_index': i,
                    'content_type': content_type_result,
                    'importance': importance_result,
                    'quality': quality_result
                })
            
            results['chunk_classifications'] = chunk_classifications
        
        return results
    
    def get_processing_summary(self, results: Dict[str, ProcessingResult]) -> Dict[str, Any]:
        """Generate summary of processing results.
        
        Args:
            results: Processing results from process_document_complete
        
        Returns:
            Summary dictionary
        """
        summary = {
            'total_operations': len(results),
            'successful_operations': 0,
            'failed_operations': 0,
            'total_tokens_used': 0,
            'total_processing_time': 0.0,
            'operation_details': {}
        }
        
        for operation, result in results.items():
            if operation == 'chunk_classifications':
                # Handle chunk classifications separately
                chunk_summary = {
                    'total_chunks': len(result),
                    'successful_classifications': 0,
                    'failed_classifications': 0,
                    'tokens_used': 0,
                    'processing_time': 0.0
                }
                
                for chunk_result in result:
                    for classification_type, classification_result in chunk_result.items():
                        if classification_type == 'chunk_index':
                            continue
                        
                        if isinstance(classification_result, ProcessingResult):
                            if classification_result.success:
                                chunk_summary['successful_classifications'] += 1
                            else:
                                chunk_summary['failed_classifications'] += 1
                            
                            chunk_summary['tokens_used'] += classification_result.tokens_used
                            chunk_summary['processing_time'] += classification_result.processing_time
                
                summary['operation_details'][operation] = chunk_summary
                summary['total_tokens_used'] += chunk_summary['tokens_used']
                summary['total_processing_time'] += chunk_summary['processing_time']
                
            else:
                # Handle regular processing results
                if isinstance(result, ProcessingResult):
                    if result.success:
                        summary['successful_operations'] += 1
                    else:
                        summary['failed_operations'] += 1
                    
                    summary['total_tokens_used'] += result.tokens_used
                    summary['total_processing_time'] += result.processing_time
                    
                    summary['operation_details'][operation] = {
                        'success': result.success,
                        'tokens_used': result.tokens_used,
                        'processing_time': result.processing_time,
                        'model_used': result.model_used,
                        'error': result.error
                    }
        
        return summary