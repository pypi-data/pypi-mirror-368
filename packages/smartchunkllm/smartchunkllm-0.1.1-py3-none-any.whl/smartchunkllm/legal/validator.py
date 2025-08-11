"""Legal document validation and quality control."""

from typing import Dict, List, Optional, Any, Tuple, Callable
import re
import logging
from dataclasses import dataclass, field
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

# Core imports
from ..core.config import LegalConfig
from ..core.chunk import SemanticChunk, ContentType, ImportanceLevel
from .analyzer import LegalStructure, LegalElement, LegalElementType


@dataclass
class ValidationRule:
    """A validation rule for legal documents."""
    name: str
    category: 'ValidationCategory'
    severity: 'ValidationSeverity'
    description: str
    check_function: Callable[[Any], bool]
    message_template: str
    suggestion: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ValidationSeverity(Enum):
    """Validation issue severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ValidationCategory(Enum):
    """Categories of validation issues."""
    STRUCTURE = "structure"
    CONTENT = "content"
    LEGAL_COMPLIANCE = "legal_compliance"
    FORMATTING = "formatting"
    COMPLETENESS = "completeness"
    CONSISTENCY = "consistency"
    REFERENCES = "references"


@dataclass
class ValidationIssue:
    """A validation issue found in the document."""
    category: ValidationCategory
    severity: ValidationSeverity
    message: str
    element_id: Optional[str] = None
    chunk_id: Optional[str] = None
    page_number: Optional[int] = None
    suggestion: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """Complete validation result."""
    is_valid: bool
    overall_score: float  # 0.0 to 1.0
    issues: List[ValidationIssue] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_issues_by_severity(self, severity: ValidationSeverity) -> List[ValidationIssue]:
        """Get issues by severity level."""
        return [issue for issue in self.issues if issue.severity == severity]
    
    def get_issues_by_category(self, category: ValidationCategory) -> List[ValidationIssue]:
        """Get issues by category."""
        return [issue for issue in self.issues if issue.category == category]
    
    def has_critical_issues(self) -> bool:
        """Check if there are critical issues."""
        return any(issue.severity == ValidationSeverity.CRITICAL for issue in self.issues)
    
    def get_summary(self) -> Dict[str, int]:
        """Get summary of issues by severity."""
        summary = {severity.value: 0 for severity in ValidationSeverity}
        for issue in self.issues:
            summary[issue.severity.value] += 1
        return summary


class LegalValidator:
    """Validates legal documents and semantic chunks for compliance and quality."""
    
    def __init__(self, config: LegalConfig):
        """Initialize the legal validator.
        
        Args:
            config: Legal validation configuration
        """
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Turkish legal validation rules
        self.validation_rules = self._initialize_validation_rules()
        
        # Legal terminology and patterns
        self.legal_patterns = self._initialize_legal_patterns()
        
        # Quality thresholds
        self.quality_thresholds = {
            "min_chunk_length": 50,
            "max_chunk_length": 5000,
            "min_coherence_score": 0.6,
            "min_completeness_score": 0.7,
            "max_reference_distance": 10  # Maximum distance for internal references
        }
    
    def _initialize_validation_rules(self) -> Dict[str, Any]:
        """Initialize validation rules for Turkish legal documents."""
        return {
            "required_elements": {
                "articles": True,
                "title": True,
                "document_type": False
            },
            "numbering_rules": {
                "articles_sequential": True,
                "paragraphs_sequential": True,
                "allow_gaps": False
            },
            "content_rules": {
                "min_article_length": 20,
                "max_article_length": 2000,
                "require_definitions": False,
                "check_references": True
            },
            "formatting_rules": {
                "consistent_numbering": True,
                "proper_hierarchy": True,
                "valid_characters": True
            }
        }
    
    def _initialize_legal_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Initialize legal patterns for validation."""
        return {
            "invalid_references": [
                re.compile(r"madde\s+\d+\s*(?![-–—])", re.IGNORECASE),  # Incomplete article references
                re.compile(r"\d+\s*sayılı\s*$", re.IGNORECASE),  # Incomplete law references
            ],
            "formatting_issues": [
                re.compile(r"\s{3,}"),  # Multiple spaces
                re.compile(r"[.]{2,}"),  # Multiple dots
                re.compile(r"[,]{2,}"),  # Multiple commas
            ],
            "content_issues": [
                re.compile(r"^\s*$"),  # Empty content
                re.compile(r"^.{1,10}$"),  # Too short content
            ],
            "legal_terminology": [
                re.compile(r"\b(?:hak|yükümlülük|sorumluluk|yetki|görev)\b", re.IGNORECASE),
                re.compile(r"\b(?:ceza|para\s*cezası|hapis|disiplin)\b", re.IGNORECASE),
                re.compile(r"\b(?:kanun|yönetmelik|tebliğ|genelge)\b", re.IGNORECASE),
            ]
        }
    
    def validate_chunks(self, chunks: List[SemanticChunk], legal_structure: LegalStructure) -> ValidationResult:
        """Validate semantic chunks against legal requirements.
        
        Args:
            chunks: List of semantic chunks to validate
            legal_structure: Legal document structure
        
        Returns:
            ValidationResult with issues and recommendations
        """
        try:
            self.logger.info(f"Starting validation of {len(chunks)} chunks")
            
            issues = []
            
            # Validate individual chunks
            for chunk in chunks:
                chunk_issues = self._validate_chunk(chunk, legal_structure)
                issues.extend(chunk_issues)
            
            # Validate chunk relationships
            relationship_issues = self._validate_chunk_relationships(chunks, legal_structure)
            issues.extend(relationship_issues)
            
            # Validate completeness
            completeness_issues = self._validate_completeness(chunks, legal_structure)
            issues.extend(completeness_issues)
            
            # Validate consistency
            consistency_issues = self._validate_consistency(chunks)
            issues.extend(consistency_issues)
            
            # Calculate overall score
            overall_score = self._calculate_validation_score(issues, chunks)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(issues, chunks, legal_structure)
            
            # Compile statistics
            statistics = self._compile_statistics(issues, chunks, legal_structure)
            
            result = ValidationResult(
                is_valid=not any(issue.severity == ValidationSeverity.CRITICAL for issue in issues),
                overall_score=overall_score,
                issues=issues,
                statistics=statistics,
                recommendations=recommendations,
                metadata={
                    "total_chunks": len(chunks),
                    "validation_timestamp": __import__('time').time()
                }
            )
            
            self.logger.info(f"Validation completed: {len(issues)} issues found, score: {overall_score:.3f}")
            
            return result
        
        except Exception as e:
            self.logger.error(f"Validation failed: {e}")
            return ValidationResult(
                is_valid=False,
                overall_score=0.0,
                issues=[ValidationIssue(
                    category=ValidationCategory.STRUCTURE,
                    severity=ValidationSeverity.CRITICAL,
                    message=f"Validation process failed: {e}"
                )]
            )
    
    def _validate_chunk(self, chunk: SemanticChunk, legal_structure: LegalStructure) -> List[ValidationIssue]:
        """Validate an individual chunk."""
        issues = []
        
        # Content length validation
        content_length = len(chunk.content.strip())
        if content_length < self.quality_thresholds["min_chunk_length"]:
            issues.append(ValidationIssue(
                category=ValidationCategory.CONTENT,
                severity=ValidationSeverity.WARNING,
                message=f"Chunk content too short: {content_length} characters",
                chunk_id=chunk.id,
                suggestion="Consider merging with adjacent chunks or expanding content"
            ))
        elif content_length > self.quality_thresholds["max_chunk_length"]:
            issues.append(ValidationIssue(
                category=ValidationCategory.CONTENT,
                severity=ValidationSeverity.WARNING,
                message=f"Chunk content too long: {content_length} characters",
                chunk_id=chunk.id,
                suggestion="Consider splitting into smaller, more focused chunks"
            ))
        
        # Content quality validation
        if not chunk.content.strip():
            issues.append(ValidationIssue(
                category=ValidationCategory.CONTENT,
                severity=ValidationSeverity.ERROR,
                message="Chunk has empty content",
                chunk_id=chunk.id,
                suggestion="Remove empty chunks or add meaningful content"
            ))
        
        # Formatting validation
        formatting_issues = self._check_formatting(chunk.content)
        for issue_msg in formatting_issues:
            issues.append(ValidationIssue(
                category=ValidationCategory.FORMATTING,
                severity=ValidationSeverity.INFO,
                message=issue_msg,
                chunk_id=chunk.id,
                suggestion="Clean up formatting inconsistencies"
            ))
        
        # Legal content validation
        legal_issues = self._validate_legal_content(chunk, legal_structure)
        issues.extend(legal_issues)
        
        # Quality metrics validation
        if chunk.quality_metrics:
            quality_issues = self._validate_quality_metrics(chunk)
            issues.extend(quality_issues)
        
        return issues
    
    def _check_formatting(self, content: str) -> List[str]:
        """Check for formatting issues in content."""
        issues = []
        
        for pattern_name, patterns in self.legal_patterns["formatting_issues"]:
            for pattern in patterns:
                if pattern.search(content):
                    issues.append(f"Formatting issue detected: {pattern_name}")
        
        # Check for inconsistent spacing
        if re.search(r"\s{3,}", content):
            issues.append("Multiple consecutive spaces found")
        
        # Check for inconsistent punctuation
        if re.search(r"[.]{2,}", content):
            issues.append("Multiple consecutive periods found")
        
        return issues
    
    def _validate_legal_content(self, chunk: SemanticChunk, legal_structure: LegalStructure) -> List[ValidationIssue]:
        """Validate legal-specific content."""
        issues = []
        
        # Check for incomplete references
        for pattern in self.legal_patterns["invalid_references"]:
            matches = pattern.findall(chunk.content)
            for match in matches:
                issues.append(ValidationIssue(
                    category=ValidationCategory.REFERENCES,
                    severity=ValidationSeverity.WARNING,
                    message=f"Potentially incomplete reference: {match}",
                    chunk_id=chunk.id,
                    suggestion="Verify and complete legal references"
                ))
        
        # Validate content type consistency
        if chunk.content_type == ContentType.DEFINITION:
            if not self._contains_definition_pattern(chunk.content):
                issues.append(ValidationIssue(
                    category=ValidationCategory.CONTENT,
                    severity=ValidationSeverity.WARNING,
                    message="Chunk marked as definition but doesn't contain definition patterns",
                    chunk_id=chunk.id,
                    suggestion="Review content type classification"
                ))
        
        # Check for legal terminology presence
        if chunk.content_type in [ContentType.RULE, ContentType.SANCTION]:
            has_legal_terms = any(
                pattern.search(chunk.content) 
                for pattern in self.legal_patterns["legal_terminology"]
            )
            if not has_legal_terms:
                issues.append(ValidationIssue(
                    category=ValidationCategory.LEGAL_COMPLIANCE,
                    severity=ValidationSeverity.INFO,
                    message="Legal content lacks typical legal terminology",
                    chunk_id=chunk.id,
                    suggestion="Verify legal content classification"
                ))
        
        return issues
    
    def _contains_definition_pattern(self, content: str) -> bool:
        """Check if content contains definition patterns."""
        definition_indicators = [
            r":\s*[A-ZÜĞŞÇÖI]",  # Colon followed by definition
            r"ifadesi\s*[,:]?",  # "ifadesi" (expression)
            r"deyimi\s*[,:]?",   # "deyimi" (phrase)
            r"kavramı\s*[,:]?",  # "kavramı" (concept)
            r"anlamına\s+gelir",  # "anlamına gelir" (means)
            r"\"[^\"]+\"\s*[,:]?"  # Quoted terms
        ]
        
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in definition_indicators)
    
    def _validate_quality_metrics(self, chunk: SemanticChunk) -> List[ValidationIssue]:
        """Validate quality metrics of a chunk."""
        issues = []
        
        if not chunk.quality_metrics:
            issues.append(ValidationIssue(
                category=ValidationCategory.COMPLETENESS,
                severity=ValidationSeverity.WARNING,
                message="Chunk missing quality metrics",
                chunk_id=chunk.id,
                suggestion="Run quality assessment on chunk"
            ))
            return issues
        
        # Check coherence score
        if hasattr(chunk.quality_metrics, 'coherence'):
            if chunk.quality_metrics.coherence < self.quality_thresholds["min_coherence_score"]:
                issues.append(ValidationIssue(
                    category=ValidationCategory.CONTENT,
                    severity=ValidationSeverity.WARNING,
                    message=f"Low coherence score: {chunk.quality_metrics.coherence:.3f}",
                    chunk_id=chunk.id,
                    suggestion="Review chunk boundaries and content cohesion"
                ))
        
        # Check completeness score
        if hasattr(chunk.quality_metrics, 'completeness'):
            if chunk.quality_metrics.completeness < self.quality_thresholds["min_completeness_score"]:
                issues.append(ValidationIssue(
                    category=ValidationCategory.COMPLETENESS,
                    severity=ValidationSeverity.WARNING,
                    message=f"Low completeness score: {chunk.quality_metrics.completeness:.3f}",
                    chunk_id=chunk.id,
                    suggestion="Ensure chunk contains complete legal concepts"
                ))
        
        return issues
    
    def _validate_chunk_relationships(self, chunks: List[SemanticChunk], legal_structure: LegalStructure) -> List[ValidationIssue]:
        """Validate relationships between chunks."""
        issues = []
        
        # Check for overlapping content
        for i, chunk1 in enumerate(chunks):
            for j, chunk2 in enumerate(chunks[i+1:], i+1):
                similarity = self._calculate_content_similarity(chunk1.content, chunk2.content)
                if similarity > 0.8:  # High similarity threshold
                    issues.append(ValidationIssue(
                        category=ValidationCategory.CONSISTENCY,
                        severity=ValidationSeverity.WARNING,
                        message=f"High content similarity between chunks: {similarity:.3f}",
                        chunk_id=f"{chunk1.id}, {chunk2.id}",
                        suggestion="Review chunk boundaries to avoid duplication"
                    ))
        
        # Check for logical sequence
        article_chunks = [c for c in chunks if c.content_type == ContentType.RULE]
        if len(article_chunks) > 1:
            sequence_issues = self._check_logical_sequence(article_chunks)
            issues.extend(sequence_issues)
        
        return issues
    
    def _calculate_content_similarity(self, content1: str, content2: str) -> float:
        """Calculate similarity between two content strings."""
        # Simple word-based similarity
        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _check_logical_sequence(self, chunks: List[SemanticChunk]) -> List[ValidationIssue]:
        """Check logical sequence of chunks."""
        issues = []
        
        # Extract article numbers if available
        numbered_chunks = []
        for chunk in chunks:
            article_match = re.search(r"madde\s+(\d+)", chunk.content, re.IGNORECASE)
            if article_match:
                numbered_chunks.append((int(article_match.group(1)), chunk))
        
        # Check for sequential numbering
        if len(numbered_chunks) > 1:
            numbered_chunks.sort(key=lambda x: x[0])
            for i in range(len(numbered_chunks) - 1):
                current_num = numbered_chunks[i][0]
                next_num = numbered_chunks[i+1][0]
                
                if next_num - current_num > 1:
                    issues.append(ValidationIssue(
                        category=ValidationCategory.STRUCTURE,
                        severity=ValidationSeverity.INFO,
                        message=f"Gap in article numbering: {current_num} to {next_num}",
                        suggestion="Verify if missing articles should be included"
                    ))
        
        return issues
    
    def _validate_completeness(self, chunks: List[SemanticChunk], legal_structure: LegalStructure) -> List[ValidationIssue]:
        """Validate completeness of the chunking."""
        issues = []
        
        # Check if all articles are represented
        chunk_articles = set()
        for chunk in chunks:
            article_matches = re.findall(r"madde\s+(\d+)", chunk.content, re.IGNORECASE)
            chunk_articles.update(article_matches)
        
        structure_articles = set()
        for article in legal_structure.articles:
            if article.number:
                structure_articles.add(article.number)
        
        missing_articles = structure_articles - chunk_articles
        if missing_articles:
            issues.append(ValidationIssue(
                category=ValidationCategory.COMPLETENESS,
                severity=ValidationSeverity.WARNING,
                message=f"Articles not represented in chunks: {', '.join(sorted(missing_articles))}",
                suggestion="Ensure all legal articles are properly chunked"
            ))
        
        # Check for orphaned content
        if len(chunks) == 0 and legal_structure.articles:
            issues.append(ValidationIssue(
                category=ValidationCategory.COMPLETENESS,
                severity=ValidationSeverity.CRITICAL,
                message="No chunks generated despite having legal content",
                suggestion="Review chunking process and parameters"
            ))
        
        return issues
    
    def _validate_consistency(self, chunks: List[SemanticChunk]) -> List[ValidationIssue]:
        """Validate consistency across chunks."""
        issues = []
        
        # Check content type distribution
        content_types = [chunk.content_type for chunk in chunks]
        type_counts = {}
        for content_type in content_types:
            type_counts[content_type] = type_counts.get(content_type, 0) + 1
        
        # Warn if too many general chunks
        general_ratio = type_counts.get(ContentType.GENERAL, 0) / len(chunks) if chunks else 0
        if general_ratio > 0.5:
            issues.append(ValidationIssue(
                category=ValidationCategory.CONSISTENCY,
                severity=ValidationSeverity.WARNING,
                message=f"High ratio of general content chunks: {general_ratio:.2%}",
                suggestion="Review content classification to improve specificity"
            ))
        
        # Check importance level distribution
        importance_levels = [chunk.importance_level for chunk in chunks]
        high_importance_ratio = importance_levels.count(ImportanceLevel.CRITICAL) / len(chunks) if chunks else 0
        if high_importance_ratio > 0.8:
            issues.append(ValidationIssue(
                category=ValidationCategory.CONSISTENCY,
                severity=ValidationSeverity.INFO,
                message=f"Very high ratio of critical importance chunks: {high_importance_ratio:.2%}",
                suggestion="Review importance level classification for balance"
            ))
        
        return issues
    
    def _calculate_validation_score(self, issues: List[ValidationIssue], chunks: List[SemanticChunk]) -> float:
        """Calculate overall validation score."""
        if not chunks:
            return 0.0
        
        # Weight issues by severity
        severity_weights = {
            ValidationSeverity.INFO: 0.1,
            ValidationSeverity.WARNING: 0.3,
            ValidationSeverity.ERROR: 0.7,
            ValidationSeverity.CRITICAL: 1.0
        }
        
        total_penalty = sum(severity_weights[issue.severity] for issue in issues)
        max_possible_penalty = len(chunks) * 2  # Assume max 2 critical issues per chunk
        
        # Calculate score (1.0 = perfect, 0.0 = worst)
        score = max(0.0, 1.0 - (total_penalty / max_possible_penalty))
        
        return score
    
    def _generate_recommendations(self, issues: List[ValidationIssue], chunks: List[SemanticChunk], legal_structure: LegalStructure) -> List[str]:
        """Generate recommendations based on validation issues."""
        recommendations = []
        
        # Count issues by category
        category_counts = {}
        for issue in issues:
            category_counts[issue.category] = category_counts.get(issue.category, 0) + 1
        
        # Generate category-specific recommendations
        if category_counts.get(ValidationCategory.CONTENT, 0) > 0:
            recommendations.append("Review content quality and ensure chunks contain meaningful legal information")
        
        if category_counts.get(ValidationCategory.STRUCTURE, 0) > 0:
            recommendations.append("Verify document structure analysis and chunk boundary detection")
        
        if category_counts.get(ValidationCategory.REFERENCES, 0) > 0:
            recommendations.append("Check and complete all legal references for accuracy")
        
        if category_counts.get(ValidationCategory.FORMATTING, 0) > 0:
            recommendations.append("Clean up formatting inconsistencies in the source document")
        
        if category_counts.get(ValidationCategory.COMPLETENESS, 0) > 0:
            recommendations.append("Ensure all important legal content is properly captured in chunks")
        
        # General recommendations
        if len(issues) > len(chunks) * 0.5:  # More than 0.5 issues per chunk
            recommendations.append("Consider adjusting chunking parameters to improve quality")
        
        if not recommendations:
            recommendations.append("Document validation passed with good quality")
        
        return recommendations
    
    def _compile_statistics(self, issues: List[ValidationIssue], chunks: List[SemanticChunk], legal_structure: LegalStructure) -> Dict[str, Any]:
        """Compile validation statistics."""
        return {
            "total_issues": len(issues),
            "issues_by_severity": {
                severity.value: len([i for i in issues if i.severity == severity])
                for severity in ValidationSeverity
            },
            "issues_by_category": {
                category.value: len([i for i in issues if i.category == category])
                for category in ValidationCategory
            },
            "chunk_statistics": {
                "total_chunks": len(chunks),
                "avg_chunk_length": sum(len(c.content) for c in chunks) / len(chunks) if chunks else 0,
                "content_type_distribution": {
                    content_type.value: len([c for c in chunks if c.content_type == content_type])
                    for content_type in ContentType
                },
                "importance_distribution": {
                    importance.value: len([c for c in chunks if c.importance_level == importance])
                    for importance in ImportanceLevel
                }
            },
            "structure_statistics": {
                "total_articles": len(legal_structure.articles),
                "total_sections": len(legal_structure.sections),
                "total_references": len(legal_structure.references),
                "document_type": legal_structure.document_type
            }
        }
    
    def validate_single_chunk(self, chunk: SemanticChunk) -> ValidationResult:
        """Validate a single chunk.
        
        Args:
            chunk: Chunk to validate
        
        Returns:
            ValidationResult for the chunk
        """
        issues = self._validate_chunk(chunk, LegalStructure())
        
        return ValidationResult(
            is_valid=not any(issue.severity == ValidationSeverity.CRITICAL for issue in issues),
            overall_score=self._calculate_validation_score(issues, [chunk]),
            issues=issues,
            statistics=self._compile_statistics(issues, [chunk], LegalStructure()),
            recommendations=self._generate_recommendations(issues, [chunk], LegalStructure())
        )