"""Legal document processing module."""

from .processor import (
    LegalDocumentProcessor,
    ProcessingResult,
    ProcessingStats
)

from .analyzer import (
    LegalAnalyzer,
    LegalStructure,
    LegalReference,
    ConceptExtractor
)

from .validator import (
    LegalValidator,
    ValidationResult,
    ValidationRule
)

__all__ = [
    # Main processor
    'LegalDocumentProcessor',
    'ProcessingResult',
    'ProcessingStats',
    
    # Analysis
    'LegalAnalyzer',
    'LegalStructure',
    'LegalReference',
    'ConceptExtractor',
    
    # Validation
    'LegalValidator',
    'ValidationResult',
    'ValidationRule'
]