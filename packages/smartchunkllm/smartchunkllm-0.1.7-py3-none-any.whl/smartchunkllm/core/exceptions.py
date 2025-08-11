"""Custom exceptions for SmartChunkLLM."""

from typing import Optional, Dict, Any, List


class SmartChunkLLMError(Exception):
    """Base exception class for SmartChunkLLM."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, 
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def __str__(self) -> str:
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary."""
        return {
            'error_type': self.__class__.__name__,
            'message': self.message,
            'error_code': self.error_code,
            'details': self.details
        }


class ConfigurationError(SmartChunkLLMError):
    """Raised when there's a configuration error."""
    pass


class PDFProcessingError(SmartChunkLLMError):
    """Raised when PDF processing fails."""
    
    def __init__(self, message: str, file_path: Optional[str] = None, 
                 page_number: Optional[int] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.file_path = file_path
        self.page_number = page_number
        if file_path:
            self.details['file_path'] = file_path
        if page_number is not None:
            self.details['page_number'] = page_number


class OCRError(PDFProcessingError):
    """Raised when OCR processing fails."""
    pass


class LayoutDetectionError(PDFProcessingError):
    """Raised when layout detection fails."""
    pass


class FontAnalysisError(PDFProcessingError):
    """Raised when font analysis fails."""
    pass


class EmbeddingError(SmartChunkLLMError):
    """Raised when embedding generation fails."""
    
    def __init__(self, message: str, model_name: Optional[str] = None, 
                 text_length: Optional[int] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.model_name = model_name
        self.text_length = text_length
        if model_name:
            self.details['model_name'] = model_name
        if text_length is not None:
            self.details['text_length'] = text_length


class ClusteringError(SmartChunkLLMError):
    """Raised when clustering fails."""
    
    def __init__(self, message: str, algorithm: Optional[str] = None, 
                 data_points: Optional[int] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.algorithm = algorithm
        self.data_points = data_points
        if algorithm:
            self.details['algorithm'] = algorithm
        if data_points is not None:
            self.details['data_points'] = data_points


class LLMError(SmartChunkLLMError):
    """Raised when LLM operations fail."""
    
    def __init__(self, message: str, provider: Optional[str] = None, 
                 model: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.provider = provider
        self.model = model
        if provider:
            self.details['provider'] = provider
        if model:
            self.details['model'] = model


class LLMProviderError(LLMError):
    """Raised when LLM provider is not available or configured incorrectly."""
    pass


class LLMAPIError(LLMError):
    """Raised when LLM API calls fail."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, 
                 response_text: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.status_code = status_code
        self.response_text = response_text
        if status_code is not None:
            self.details['status_code'] = status_code
        if response_text:
            self.details['response_text'] = response_text


class LLMTimeoutError(LLMError):
    """Raised when LLM operations timeout."""
    
    def __init__(self, message: str, timeout_seconds: Optional[float] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.timeout_seconds = timeout_seconds
        if timeout_seconds is not None:
            self.details['timeout_seconds'] = timeout_seconds


class LLMRateLimitError(LLMError):
    """Raised when LLM rate limits are exceeded."""
    
    def __init__(self, message: str, retry_after: Optional[int] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after
        if retry_after is not None:
            self.details['retry_after'] = retry_after


class ChunkingError(SmartChunkLLMError):
    """Raised when chunking operations fail."""
    
    def __init__(self, message: str, strategy: Optional[str] = None, 
                 text_length: Optional[int] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.strategy = strategy
        self.text_length = text_length
        if strategy:
            self.details['strategy'] = strategy
        if text_length is not None:
            self.details['text_length'] = text_length


class QualityAssessmentError(SmartChunkLLMError):
    """Raised when quality assessment fails."""
    
    def __init__(self, message: str, chunk_id: Optional[str] = None, 
                 assessment_type: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.chunk_id = chunk_id
        self.assessment_type = assessment_type
        if chunk_id:
            self.details['chunk_id'] = chunk_id
        if assessment_type:
            self.details['assessment_type'] = assessment_type


class LegalAnalysisError(SmartChunkLLMError):
    """Raised when legal analysis fails."""
    
    def __init__(self, message: str, document_type: Optional[str] = None, 
                 analysis_stage: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.document_type = document_type
        self.analysis_stage = analysis_stage
        if document_type:
            self.details['document_type'] = document_type
        if analysis_stage:
            self.details['analysis_stage'] = analysis_stage


class ValidationError(SmartChunkLLMError):
    """Raised when validation fails."""
    
    def __init__(self, message: str, validation_type: Optional[str] = None, 
                 failed_rules: Optional[List[str]] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.validation_type = validation_type
        self.failed_rules = failed_rules or []
        if validation_type:
            self.details['validation_type'] = validation_type
        if failed_rules:
            self.details['failed_rules'] = failed_rules


class ProcessingError(SmartChunkLLMError):
    """Raised when general processing operations fail."""
    
    def __init__(self, message: str, operation: Optional[str] = None, 
                 stage: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.operation = operation
        self.stage = stage
        if operation:
            self.details['operation'] = operation
        if stage:
            self.details['stage'] = stage


class DataError(SmartChunkLLMError):
    """Raised when there are data-related errors."""
    pass


class FileNotFoundError(DataError):
    """Raised when a required file is not found."""
    
    def __init__(self, message: str, file_path: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.file_path = file_path
        if file_path:
            self.details['file_path'] = file_path


class InvalidFormatError(DataError):
    """Raised when data format is invalid."""
    
    def __init__(self, message: str, expected_format: Optional[str] = None, 
                 actual_format: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.expected_format = expected_format
        self.actual_format = actual_format
        if expected_format:
            self.details['expected_format'] = expected_format
        if actual_format:
            self.details['actual_format'] = actual_format


class MemoryError(SmartChunkLLMError):
    """Raised when memory-related errors occur."""
    
    def __init__(self, message: str, memory_usage: Optional[float] = None, 
                 memory_limit: Optional[float] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.memory_usage = memory_usage
        self.memory_limit = memory_limit
        if memory_usage is not None:
            self.details['memory_usage'] = memory_usage
        if memory_limit is not None:
            self.details['memory_limit'] = memory_limit


class TimeoutError(SmartChunkLLMError):
    """Raised when operations timeout."""
    
    def __init__(self, message: str, timeout_seconds: Optional[float] = None, 
                 operation: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.timeout_seconds = timeout_seconds
        self.operation = operation
        if timeout_seconds is not None:
            self.details['timeout_seconds'] = timeout_seconds
        if operation:
            self.details['operation'] = operation


class DependencyError(SmartChunkLLMError):
    """Raised when required dependencies are missing or incompatible."""
    
    def __init__(self, message: str, dependency: Optional[str] = None, 
                 required_version: Optional[str] = None, 
                 installed_version: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.dependency = dependency
        self.required_version = required_version
        self.installed_version = installed_version
        if dependency:
            self.details['dependency'] = dependency
        if required_version:
            self.details['required_version'] = required_version
        if installed_version:
            self.details['installed_version'] = installed_version


class ModelNotFoundError(SmartChunkLLMError):
    """Raised when a required model is not found."""
    
    def __init__(self, message: str, model_name: Optional[str] = None, 
                 model_type: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.model_name = model_name
        self.model_type = model_type
        if model_name:
            self.details['model_name'] = model_name
        if model_type:
            self.details['model_type'] = model_type


class AuthenticationError(SmartChunkLLMError):
    """Raised when authentication fails."""
    
    def __init__(self, message: str, provider: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.provider = provider
        if provider:
            self.details['provider'] = provider


class PermissionError(SmartChunkLLMError):
    """Raised when permission is denied."""
    
    def __init__(self, message: str, resource: Optional[str] = None, 
                 required_permission: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.resource = resource
        self.required_permission = required_permission
        if resource:
            self.details['resource'] = resource
        if required_permission:
            self.details['required_permission'] = required_permission


# Exception mapping for better error handling
EXCEPTION_MAPPING = {
    'pdf_processing': PDFProcessingError,
    'ocr': OCRError,
    'layout_detection': LayoutDetectionError,
    'font_analysis': FontAnalysisError,
    'embedding': EmbeddingError,
    'clustering': ClusteringError,
    'llm': LLMError,
    'llm_provider': LLMProviderError,
    'llm_api': LLMAPIError,
    'llm_timeout': LLMTimeoutError,
    'llm_rate_limit': LLMRateLimitError,
    'chunking': ChunkingError,
    'quality_assessment': QualityAssessmentError,
    'legal_analysis': LegalAnalysisError,
    'validation': ValidationError,
    'data': DataError,
    'file_not_found': FileNotFoundError,
    'invalid_format': InvalidFormatError,
    'memory': MemoryError,
    'timeout': TimeoutError,
    'dependency': DependencyError,
    'model_not_found': ModelNotFoundError,
    'authentication': AuthenticationError,
    'permission': PermissionError,
    'configuration': ConfigurationError
}


def get_exception_class(error_type: str) -> type:
    """Get exception class by error type."""
    return EXCEPTION_MAPPING.get(error_type, SmartChunkLLMError)


def create_exception(error_type: str, message: str, **kwargs) -> SmartChunkLLMError:
    """Create an exception instance by error type."""
    exception_class = get_exception_class(error_type)
    return exception_class(message, **kwargs)


# Alias for backward compatibility
SmartChunkError = SmartChunkLLMError