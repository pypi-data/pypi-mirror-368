"""Validation utilities for SmartChunkLLM."""

import re
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable, Tuple
from datetime import datetime
import mimetypes

try:
    from pydantic import BaseModel, ValidationError as PydanticValidationError
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False

from ..core.types import (
    ChunkingStrategy, QualityLevel, ContentType, ProcessingStatus,
    LLMProvider, EmbeddingModel, ClusteringAlgorithm,
    ValidationResult
)
from ..core.exceptions import (
    ValidationError,
    ConfigurationError,
    DataError
)


class Validator:
    """Base validator class."""
    
    def __init__(self, strict: bool = False):
        self.strict = strict
        self.errors = []
        self.warnings = []
    
    def reset(self):
        """Reset validation state."""
        self.errors.clear()
        self.warnings.clear()
    
    def add_error(self, message: str, field: Optional[str] = None):
        """Add validation error.
        
        Args:
            message: Error message
            field: Field name (optional)
        """
        error = {'message': message, 'field': field, 'type': 'error'}
        self.errors.append(error)
    
    def add_warning(self, message: str, field: Optional[str] = None):
        """Add validation warning.
        
        Args:
            message: Warning message
            field: Field name (optional)
        """
        warning = {'message': message, 'field': field, 'type': 'warning'}
        self.warnings.append(warning)
    
    def is_valid(self) -> bool:
        """Check if validation passed.
        
        Returns:
            True if no errors
        """
        return len(self.errors) == 0
    
    def get_result(self) -> ValidationResult:
        """Get validation result.
        
        Returns:
            ValidationResult object
        """
        return ValidationResult(
            is_valid=self.is_valid(),
            errors=self.errors.copy(),
            warnings=self.warnings.copy(),
            details={}
        )
    
    def validate(self, data: Any) -> ValidationResult:
        """Validate data.
        
        Args:
            data: Data to validate
        
        Returns:
            Validation result
        """
        self.reset()
        self._validate_impl(data)
        return self.get_result()
    
    def _validate_impl(self, data: Any):
        """Implementation of validation logic.
        
        Args:
            data: Data to validate
        """
        raise NotImplementedError


class ConfigValidator(Validator):
    """Configuration validator."""
    
    def _validate_impl(self, config: Dict[str, Any]):
        """Validate configuration.
        
        Args:
            config: Configuration dictionary
        """
        # Validate required fields
        required_fields = ['chunking', 'processing', 'llm']
        for field in required_fields:
            if field not in config:
                self.add_error(f"Missing required field: {field}")
        
        # Validate chunking configuration
        if 'chunking' in config:
            self._validate_chunking_config(config['chunking'])
        
        # Validate processing configuration
        if 'processing' in config:
            self._validate_processing_config(config['processing'])
        
        # Validate LLM configuration
        if 'llm' in config:
            self._validate_llm_config(config['llm'])
        
        # Validate embedding configuration
        if 'embedding' in config:
            self._validate_embedding_config(config['embedding'])
        
        # Validate clustering configuration
        if 'clustering' in config:
            self._validate_clustering_config(config['clustering'])
    
    def _validate_chunking_config(self, config: Dict[str, Any]):
        """Validate chunking configuration."""
        # Strategy
        if 'strategy' in config:
            try:
                ChunkingStrategy(config['strategy'])
            except ValueError:
                self.add_error(f"Invalid chunking strategy: {config['strategy']}", 'chunking.strategy')
        
        # Chunk size
        if 'chunk_size' in config:
            chunk_size = config['chunk_size']
            if not isinstance(chunk_size, int) or chunk_size <= 0:
                self.add_error("Chunk size must be a positive integer", 'chunking.chunk_size')
            elif chunk_size < 100:
                self.add_warning("Chunk size is very small, may affect quality", 'chunking.chunk_size')
            elif chunk_size > 8192:
                self.add_warning("Chunk size is very large, may affect performance", 'chunking.chunk_size')
        
        # Overlap
        if 'overlap' in config:
            overlap = config['overlap']
            if not isinstance(overlap, int) or overlap < 0:
                self.add_error("Overlap must be a non-negative integer", 'chunking.overlap')
            elif 'chunk_size' in config and overlap >= config['chunk_size']:
                self.add_error("Overlap must be less than chunk size", 'chunking.overlap')
        
        # Quality level
        if 'quality_level' in config:
            try:
                QualityLevel(config['quality_level'])
            except ValueError:
                self.add_error(f"Invalid quality level: {config['quality_level']}", 'chunking.quality_level')
    
    def _validate_processing_config(self, config: Dict[str, Any]):
        """Validate processing configuration."""
        # Content type
        if 'content_type' in config:
            try:
                ContentType(config['content_type'])
            except ValueError:
                self.add_error(f"Invalid content type: {config['content_type']}", 'processing.content_type')
        
        # OCR settings
        if 'ocr' in config:
            ocr_config = config['ocr']
            if 'enabled' in ocr_config and not isinstance(ocr_config['enabled'], bool):
                self.add_error("OCR enabled must be boolean", 'processing.ocr.enabled')
            
            if 'language' in ocr_config:
                lang = ocr_config['language']
                if not isinstance(lang, str) or len(lang) < 2:
                    self.add_error("OCR language must be a valid language code", 'processing.ocr.language')
        
        # Layout detection
        if 'layout_detection' in config:
            layout_config = config['layout_detection']
            if 'enabled' in layout_config and not isinstance(layout_config['enabled'], bool):
                self.add_error("Layout detection enabled must be boolean", 'processing.layout_detection.enabled')
    
    def _validate_llm_config(self, config: Dict[str, Any]):
        """Validate LLM configuration."""
        # Provider
        if 'provider' in config:
            try:
                LLMProvider(config['provider'])
            except ValueError:
                self.add_error(f"Invalid LLM provider: {config['provider']}", 'llm.provider')
        
        # Model
        if 'model' in config:
            model = config['model']
            if not isinstance(model, str) or not model.strip():
                self.add_error("LLM model must be a non-empty string", 'llm.model')
        
        # API key
        if 'api_key' in config:
            api_key = config['api_key']
            if api_key and not isinstance(api_key, str):
                self.add_error("API key must be a string", 'llm.api_key')
        
        # Temperature
        if 'temperature' in config:
            temp = config['temperature']
            if not isinstance(temp, (int, float)) or temp < 0 or temp > 2:
                self.add_error("Temperature must be between 0 and 2", 'llm.temperature')
        
        # Max tokens
        if 'max_tokens' in config:
            max_tokens = config['max_tokens']
            if not isinstance(max_tokens, int) or max_tokens <= 0:
                self.add_error("Max tokens must be a positive integer", 'llm.max_tokens')
    
    def _validate_embedding_config(self, config: Dict[str, Any]):
        """Validate embedding configuration."""
        # Model
        if 'model' in config:
            try:
                EmbeddingModel(config['model'])
            except ValueError:
                self.add_error(f"Invalid embedding model: {config['model']}", 'embedding.model')
        
        # Dimensions
        if 'dimensions' in config:
            dims = config['dimensions']
            if not isinstance(dims, int) or dims <= 0:
                self.add_error("Embedding dimensions must be a positive integer", 'embedding.dimensions')
    
    def _validate_clustering_config(self, config: Dict[str, Any]):
        """Validate clustering configuration."""
        # Algorithm
        if 'algorithm' in config:
            try:
                ClusteringAlgorithm(config['algorithm'])
            except ValueError:
                self.add_error(f"Invalid clustering algorithm: {config['algorithm']}", 'clustering.algorithm')
        
        # Min cluster size
        if 'min_cluster_size' in config:
            min_size = config['min_cluster_size']
            if not isinstance(min_size, int) or min_size <= 0:
                self.add_error("Min cluster size must be a positive integer", 'clustering.min_cluster_size')


class FileValidator(Validator):
    """File validator."""
    
    def __init__(self, allowed_extensions: Optional[List[str]] = None,
                 max_size: Optional[int] = None,
                 strict: bool = False):
        super().__init__(strict)
        self.allowed_extensions = allowed_extensions or []
        self.max_size = max_size
    
    def _validate_impl(self, file_path: Union[str, Path]):
        """Validate file.
        
        Args:
            file_path: Path to file
        """
        path = Path(file_path)
        
        # Check if file exists
        if not path.exists():
            self.add_error(f"File does not exist: {path}")
            return
        
        # Check if it's a file
        if not path.is_file():
            self.add_error(f"Path is not a file: {path}")
            return
        
        # Check file extension
        if self.allowed_extensions:
            ext = path.suffix.lower().lstrip('.')
            if ext not in [e.lower().lstrip('.') for e in self.allowed_extensions]:
                self.add_error(f"File extension '{ext}' not allowed. Allowed: {self.allowed_extensions}")
        
        # Check file size
        if self.max_size:
            size = path.stat().st_size
            if size > self.max_size:
                self.add_error(f"File size ({size} bytes) exceeds maximum ({self.max_size} bytes)")
        
        # Check if file is readable
        try:
            with open(path, 'rb') as f:
                f.read(1)
        except (IOError, OSError) as e:
            self.add_error(f"Cannot read file: {e}")
        
        # Check MIME type for PDFs
        if self.allowed_extensions and 'pdf' in [e.lower() for e in self.allowed_extensions]:
            mime_type, _ = mimetypes.guess_type(str(path))
            if path.suffix.lower() == '.pdf' and mime_type != 'application/pdf':
                self.add_warning("File has .pdf extension but MIME type suggests it may not be a PDF")


class TextValidator(Validator):
    """Text content validator."""
    
    def __init__(self, min_length: int = 1,
                 max_length: Optional[int] = None,
                 required_patterns: Optional[List[str]] = None,
                 forbidden_patterns: Optional[List[str]] = None,
                 strict: bool = False):
        super().__init__(strict)
        self.min_length = min_length
        self.max_length = max_length
        self.required_patterns = required_patterns or []
        self.forbidden_patterns = forbidden_patterns or []
    
    def _validate_impl(self, text: str):
        """Validate text content.
        
        Args:
            text: Text to validate
        """
        if not isinstance(text, str):
            self.add_error("Input must be a string")
            return
        
        # Check length
        if len(text) < self.min_length:
            self.add_error(f"Text too short: {len(text)} < {self.min_length} characters")
        
        if self.max_length and len(text) > self.max_length:
            self.add_error(f"Text too long: {len(text)} > {self.max_length} characters")
        
        # Check required patterns
        for pattern in self.required_patterns:
            if not re.search(pattern, text, re.IGNORECASE):
                self.add_error(f"Required pattern not found: {pattern}")
        
        # Check forbidden patterns
        for pattern in self.forbidden_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                self.add_error(f"Forbidden pattern found: {pattern}")
        
        # Check for suspicious content
        if len(text.strip()) == 0:
            self.add_error("Text is empty or contains only whitespace")
        
        # Check encoding issues
        try:
            text.encode('utf-8')
        except UnicodeEncodeError:
            self.add_error("Text contains invalid Unicode characters")
        
        # Check for excessive repetition
        words = text.split()
        if len(words) > 10:
            word_counts = {}
            for word in words:
                word_counts[word.lower()] = word_counts.get(word.lower(), 0) + 1
            
            max_count = max(word_counts.values())
            if max_count > len(words) * 0.3:  # More than 30% repetition
                self.add_warning("Text contains excessive word repetition")


class ChunkValidator(Validator):
    """Chunk validator."""
    
    def __init__(self, min_tokens: int = 10,
                 max_tokens: int = 8192,
                 min_sentences: int = 1,
                 strict: bool = False):
        super().__init__(strict)
        self.min_tokens = min_tokens
        self.max_tokens = max_tokens
        self.min_sentences = min_sentences
    
    def _validate_impl(self, chunk: Dict[str, Any]):
        """Validate chunk.
        
        Args:
            chunk: Chunk dictionary
        """
        # Check required fields
        required_fields = ['text', 'metadata']
        for field in required_fields:
            if field not in chunk:
                self.add_error(f"Missing required field: {field}")
        
        if 'text' not in chunk:
            return
        
        text = chunk['text']
        
        # Validate text content
        text_validator = TextValidator(min_length=self.min_tokens)
        text_result = text_validator.validate(text)
        
        if not text_result.is_valid:
            for error in text_result.errors:
                self.add_error(f"Text validation: {error['message']}")
        
        # Check token count
        token_count = len(text.split())  # Simple approximation
        if token_count < self.min_tokens:
            self.add_error(f"Chunk too small: {token_count} < {self.min_tokens} tokens")
        
        if token_count > self.max_tokens:
            self.add_error(f"Chunk too large: {token_count} > {self.max_tokens} tokens")
        
        # Check sentence count
        sentence_count = len([s for s in text.split('.') if s.strip()])
        if sentence_count < self.min_sentences:
            self.add_warning(f"Chunk has few sentences: {sentence_count}")
        
        # Validate metadata
        if 'metadata' in chunk:
            metadata = chunk['metadata']
            if not isinstance(metadata, dict):
                self.add_error("Metadata must be a dictionary")
            else:
                # Check for required metadata fields
                if 'chunk_id' not in metadata:
                    self.add_error("Missing chunk_id in metadata")
                
                if 'source' not in metadata:
                    self.add_warning("Missing source in metadata")


class SchemaValidator(Validator):
    """Schema validator using Pydantic if available."""
    
    def __init__(self, schema: Union[type, Dict[str, Any]], strict: bool = False):
        super().__init__(strict)
        self.schema = schema
        
        if not PYDANTIC_AVAILABLE and isinstance(schema, type):
            raise ImportError("Pydantic is required for schema validation")
    
    def _validate_impl(self, data: Any):
        """Validate data against schema.
        
        Args:
            data: Data to validate
        """
        if PYDANTIC_AVAILABLE and isinstance(self.schema, type) and issubclass(self.schema, BaseModel):
            try:
                self.schema(**data if isinstance(data, dict) else data)
            except PydanticValidationError as e:
                for error in e.errors():
                    field = '.'.join(str(loc) for loc in error['loc'])
                    self.add_error(error['msg'], field)
        
        elif isinstance(self.schema, dict):
            self._validate_dict_schema(data, self.schema)
        
        else:
            self.add_error("Unsupported schema type")
    
    def _validate_dict_schema(self, data: Any, schema: Dict[str, Any], path: str = ''):
        """Validate data against dictionary schema.
        
        Args:
            data: Data to validate
            schema: Schema dictionary
            path: Current validation path
        """
        if not isinstance(data, dict):
            self.add_error(f"Expected dictionary at {path or 'root'}")
            return
        
        # Check required fields
        required = schema.get('required', [])
        for field in required:
            if field not in data:
                field_path = f"{path}.{field}" if path else field
                self.add_error(f"Missing required field: {field_path}")
        
        # Validate properties
        properties = schema.get('properties', {})
        for field, field_schema in properties.items():
            if field in data:
                field_path = f"{path}.{field}" if path else field
                self._validate_field(data[field], field_schema, field_path)
    
    def _validate_field(self, value: Any, field_schema: Dict[str, Any], path: str):
        """Validate individual field.
        
        Args:
            value: Field value
            field_schema: Field schema
            path: Field path
        """
        field_type = field_schema.get('type')
        
        if field_type == 'string' and not isinstance(value, str):
            self.add_error(f"Expected string at {path}, got {type(value).__name__}")
        
        elif field_type == 'integer' and not isinstance(value, int):
            self.add_error(f"Expected integer at {path}, got {type(value).__name__}")
        
        elif field_type == 'number' and not isinstance(value, (int, float)):
            self.add_error(f"Expected number at {path}, got {type(value).__name__}")
        
        elif field_type == 'boolean' and not isinstance(value, bool):
            self.add_error(f"Expected boolean at {path}, got {type(value).__name__}")
        
        elif field_type == 'array' and not isinstance(value, list):
            self.add_error(f"Expected array at {path}, got {type(value).__name__}")
        
        elif field_type == 'object' and not isinstance(value, dict):
            self.add_error(f"Expected object at {path}, got {type(value).__name__}")
        
        # Validate constraints
        if 'minimum' in field_schema and isinstance(value, (int, float)):
            if value < field_schema['minimum']:
                self.add_error(f"Value at {path} is below minimum: {value} < {field_schema['minimum']}")
        
        if 'maximum' in field_schema and isinstance(value, (int, float)):
            if value > field_schema['maximum']:
                self.add_error(f"Value at {path} is above maximum: {value} > {field_schema['maximum']}")
        
        if 'minLength' in field_schema and isinstance(value, str):
            if len(value) < field_schema['minLength']:
                self.add_error(f"String at {path} is too short: {len(value)} < {field_schema['minLength']}")
        
        if 'maxLength' in field_schema and isinstance(value, str):
            if len(value) > field_schema['maxLength']:
                self.add_error(f"String at {path} is too long: {len(value)} > {field_schema['maxLength']}")


def validate_file_path(path: Union[str, Path], 
                      must_exist: bool = True,
                      must_be_file: bool = True,
                      allowed_extensions: Optional[List[str]] = None) -> ValidationResult:
    """Validate file path.
    
    Args:
        path: File path to validate
        must_exist: File must exist
        must_be_file: Path must be a file (not directory)
        allowed_extensions: Allowed file extensions
    
    Returns:
        Validation result
    """
    validator = FileValidator(allowed_extensions=allowed_extensions)
    
    path = Path(path)
    errors = []
    warnings = []
    
    if must_exist and not path.exists():
        errors.append({'message': f"Path does not exist: {path}", 'field': 'path', 'type': 'error'})
    
    if path.exists() and must_be_file and not path.is_file():
        errors.append({'message': f"Path is not a file: {path}", 'field': 'path', 'type': 'error'})
    
    if path.exists() and path.is_file():
        result = validator.validate(path)
        errors.extend(result.errors)
        warnings.extend(result.warnings)
    
    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        details={'path': str(path)}
    )


def validate_url(url: str) -> ValidationResult:
    """Validate URL.
    
    Args:
        url: URL to validate
    
    Returns:
        Validation result
    """
    errors = []
    warnings = []
    
    if not isinstance(url, str):
        errors.append({'message': 'URL must be a string', 'field': 'url', 'type': 'error'})
        return ValidationResult(is_valid=False, errors=errors, warnings=warnings, details={})
    
    # Basic URL pattern
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'  # domain...
        r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # host...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    if not url_pattern.match(url):
        errors.append({'message': 'Invalid URL format', 'field': 'url', 'type': 'error'})
    
    # Check for common issues
    if url.startswith('http://') and 'password' in url.lower():
        warnings.append({'message': 'HTTP URL with credentials is insecure', 'field': 'url', 'type': 'warning'})
    
    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        details={'url': url}
    )


def validate_email(email: str) -> ValidationResult:
    """Validate email address.
    
    Args:
        email: Email to validate
    
    Returns:
        Validation result
    """
    errors = []
    warnings = []
    
    if not isinstance(email, str):
        errors.append({'message': 'Email must be a string', 'field': 'email', 'type': 'error'})
        return ValidationResult(is_valid=False, errors=errors, warnings=warnings, details={})
    
    # Basic email pattern
    email_pattern = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    if not email_pattern.match(email):
        errors.append({'message': 'Invalid email format', 'field': 'email', 'type': 'error'})
    
    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        details={'email': email}
    )


def validate_api_key(api_key: str, provider: str = 'openai') -> ValidationResult:
    """Validate API key format.
    
    Args:
        api_key: API key to validate
        provider: API provider
    
    Returns:
        Validation result
    """
    errors = []
    warnings = []
    
    if not isinstance(api_key, str):
        errors.append({'message': 'API key must be a string', 'field': 'api_key', 'type': 'error'})
        return ValidationResult(is_valid=False, errors=errors, warnings=warnings, details={})
    
    if not api_key.strip():
        errors.append({'message': 'API key cannot be empty', 'field': 'api_key', 'type': 'error'})
        return ValidationResult(is_valid=False, errors=errors, warnings=warnings, details={})
    
    # Provider-specific validation
    if provider.lower() == 'openai':
        if not api_key.startswith('sk-'):
            warnings.append({'message': 'OpenAI API keys typically start with "sk-"', 'field': 'api_key', 'type': 'warning'})
        
        if len(api_key) < 40:
            warnings.append({'message': 'API key seems too short', 'field': 'api_key', 'type': 'warning'})
    
    elif provider.lower() == 'anthropic':
        if not api_key.startswith('sk-ant-'):
            warnings.append({'message': 'Anthropic API keys typically start with "sk-ant-"', 'field': 'api_key', 'type': 'warning'})
    
    # General security checks
    if ' ' in api_key:
        errors.append({'message': 'API key should not contain spaces', 'field': 'api_key', 'type': 'error'})
    
    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        details={'provider': provider, 'key_length': len(api_key)}
    )


class ValidationPipeline:
    """Pipeline for running multiple validators."""
    
    def __init__(self, validators: List[Validator]):
        self.validators = validators
    
    def validate(self, data: Any) -> ValidationResult:
        """Run all validators.
        
        Args:
            data: Data to validate
        
        Returns:
            Combined validation result
        """
        all_errors = []
        all_warnings = []
        all_details = {}
        
        for i, validator in enumerate(self.validators):
            result = validator.validate(data)
            
            # Prefix errors and warnings with validator index
            for error in result.errors:
                error['validator'] = i
                all_errors.append(error)
            
            for warning in result.warnings:
                warning['validator'] = i
                all_warnings.append(warning)
            
            all_details[f'validator_{i}'] = result.details
        
        return ValidationResult(
            is_valid=len(all_errors) == 0,
            errors=all_errors,
            warnings=all_warnings,
            details=all_details
        )


def validate_pdf_file(path: Union[str, Path]) -> ValidationResult:
    """Validate PDF file.
    
    Args:
        path: PDF file path
    
    Returns:
        Validation result
    """
    errors = []
    warnings = []
    details = {}
    
    path = Path(path)
    
    # Check if file exists
    if not path.exists():
        errors.append({'message': f'PDF file not found: {path}', 'field': 'path', 'type': 'error'})
        return ValidationResult(is_valid=False, errors=errors, warnings=warnings, details=details)
    
    # Check if it's a file
    if not path.is_file():
        errors.append({'message': f'Path is not a file: {path}', 'field': 'path', 'type': 'error'})
        return ValidationResult(is_valid=False, errors=errors, warnings=warnings, details=details)
    
    # Check file extension
    if path.suffix.lower() != '.pdf':
        errors.append({'message': f'File is not a PDF: {path}', 'field': 'extension', 'type': 'error'})
    
    # Check file size
    try:
        file_size = path.stat().st_size
        details['file_size'] = file_size
        
        if file_size == 0:
            errors.append({'message': 'PDF file is empty', 'field': 'size', 'type': 'error'})
        elif file_size > 100 * 1024 * 1024:  # 100MB
            warnings.append({'message': 'PDF file is very large (>100MB)', 'field': 'size', 'type': 'warning'})
    except OSError as e:
        errors.append({'message': f'Cannot read file stats: {e}', 'field': 'access', 'type': 'error'})
    
    # Check PDF magic bytes
    try:
        with open(path, 'rb') as f:
            header = f.read(4)
            if header != b'%PDF':
                errors.append({'message': 'File does not have PDF magic bytes', 'field': 'format', 'type': 'error'})
            else:
                details['is_valid_pdf'] = True
    except (IOError, OSError) as e:
        errors.append({'message': f'Cannot read PDF file: {e}', 'field': 'access', 'type': 'error'})
    
    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        details=details
    )


class InputValidator:
    """General input validator class."""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate_text(self, text: str, min_length: int = 1, max_length: int = 1000000) -> ValidationResult:
        """Validate text input."""
        return validate_text_input(text, min_length, max_length)
    
    def validate_file(self, file_path: Union[str, Path], must_exist: bool = True) -> ValidationResult:
        """Validate file path."""
        return validate_file_path(file_path, must_exist)
    
    def validate_config(self, config: Dict[str, Any]) -> ValidationResult:
        """Validate configuration."""
        return validate_config(config)
    
    def validate_chunk_size(self, chunk_size: int) -> ValidationResult:
        """Validate chunk size."""
        return validate_chunk_size(chunk_size)
    
    def validate_quality_threshold(self, threshold: float) -> ValidationResult:
        """Validate quality threshold."""
        return validate_quality_threshold(threshold)
    
    def validate_pdf_file(self, file_path: Union[str, Path]) -> ValidationResult:
        """Validate PDF file."""
        return validate_pdf_file(file_path)


def validate_quality_threshold(threshold: float, min_threshold: float = 0.0, max_threshold: float = 1.0) -> ValidationResult:
    """Validate quality threshold.
    
    Args:
        threshold: Quality threshold to validate
        min_threshold: Minimum allowed threshold
        max_threshold: Maximum allowed threshold
    
    Returns:
        Validation result
    """
    errors = []
    warnings = []
    details = {'threshold': threshold, 'min_threshold': min_threshold, 'max_threshold': max_threshold}
    
    # Check if threshold is numeric
    if not isinstance(threshold, (int, float)):
        errors.append({'message': 'Quality threshold must be a number', 'field': 'threshold', 'type': 'error'})
        return ValidationResult(is_valid=False, errors=errors, warnings=warnings, details=details)
    
    # Check range
    if threshold < min_threshold:
        errors.append({'message': f'Quality threshold too low: {threshold} < {min_threshold}', 'field': 'threshold', 'type': 'error'})
    
    if threshold > max_threshold:
        errors.append({'message': f'Quality threshold too high: {threshold} > {max_threshold}', 'field': 'threshold', 'type': 'error'})
    
    # Warnings for extreme values
    if threshold < 0.1:
        warnings.append({'message': 'Very low quality threshold may accept poor chunks', 'field': 'threshold', 'type': 'warning'})
    
    if threshold > 0.9:
        warnings.append({'message': 'Very high quality threshold may reject good chunks', 'field': 'threshold', 'type': 'warning'})
    
    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        details=details
    )


def validate_config(config: Dict[str, Any]) -> ValidationResult:
    """Validate configuration dictionary.
    
    Args:
        config: Configuration to validate
    
    Returns:
        Validation result
    """
    validator = ConfigValidator()
    return validator.validate(config)


def validate_chunk_size(chunk_size: int, min_size: int = 50, max_size: int = 8192) -> ValidationResult:
    """Validate chunk size.
    
    Args:
        chunk_size: Chunk size to validate
        min_size: Minimum allowed size
        max_size: Maximum allowed size
    
    Returns:
        Validation result
    """
    errors = []
    warnings = []
    details = {'chunk_size': chunk_size, 'min_size': min_size, 'max_size': max_size}
    
    # Check if chunk_size is integer
    if not isinstance(chunk_size, int):
        errors.append({'message': 'Chunk size must be an integer', 'field': 'chunk_size', 'type': 'error'})
        return ValidationResult(is_valid=False, errors=errors, warnings=warnings, details=details)
    
    # Check range
    if chunk_size < min_size:
        errors.append({'message': f'Chunk size too small: {chunk_size} < {min_size}', 'field': 'chunk_size', 'type': 'error'})
    
    if chunk_size > max_size:
        errors.append({'message': f'Chunk size too large: {chunk_size} > {max_size}', 'field': 'chunk_size', 'type': 'error'})
    
    # Warnings for suboptimal sizes
    if chunk_size < 100:
        warnings.append({'message': 'Very small chunk size may affect quality', 'field': 'chunk_size', 'type': 'warning'})
    
    if chunk_size > 4096:
        warnings.append({'message': 'Large chunk size may affect performance', 'field': 'chunk_size', 'type': 'warning'})
    
    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        details=details
    )


def validate_text_input(text: str, min_length: int = 1, max_length: int = 1000000) -> ValidationResult:
    """Validate text input.
    
    Args:
        text: Text to validate
        min_length: Minimum text length
        max_length: Maximum text length
    
    Returns:
        Validation result
    """
    errors = []
    warnings = []
    details = {'length': len(text) if isinstance(text, str) else 0}
    
    # Check if text is string
    if not isinstance(text, str):
        errors.append({'message': 'Input must be a string', 'field': 'text', 'type': 'error'})
        return ValidationResult(is_valid=False, errors=errors, warnings=warnings, details=details)
    
    # Check length
    text_length = len(text)
    details['length'] = text_length
    
    if text_length < min_length:
        errors.append({'message': f'Text too short: {text_length} < {min_length}', 'field': 'length', 'type': 'error'})
    
    if text_length > max_length:
        errors.append({'message': f'Text too long: {text_length} > {max_length}', 'field': 'length', 'type': 'error'})
    
    # Check if text is empty or only whitespace
    if not text.strip():
        errors.append({'message': 'Text cannot be empty or only whitespace', 'field': 'content', 'type': 'error'})
    
    # Check for very long lines
    lines = text.split('\n')
    max_line_length = max(len(line) for line in lines) if lines else 0
    details['max_line_length'] = max_line_length
    details['line_count'] = len(lines)
    
    if max_line_length > 10000:
        warnings.append({'message': f'Very long line detected: {max_line_length} characters', 'field': 'format', 'type': 'warning'})
    
    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        details=details
    )