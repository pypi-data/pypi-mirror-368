"""Text classification and categorization for SmartChunkLLM."""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple, Union
from enum import Enum
import logging
import re

logger = logging.getLogger(__name__)


class DocumentType(Enum):
    """Types of documents that can be classified."""
    LEGAL = "legal"
    ACADEMIC = "academic"
    TECHNICAL = "technical"
    BUSINESS = "business"
    NEWS = "news"
    LITERATURE = "literature"
    MANUAL = "manual"
    REPORT = "report"
    CONTRACT = "contract"
    POLICY = "policy"
    UNKNOWN = "unknown"


class ContentCategory(Enum):
    """Categories of content within documents."""
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    LIST = "list"
    TABLE = "table"
    FIGURE = "figure"
    CAPTION = "caption"
    QUOTE = "quote"
    CODE = "code"
    FORMULA = "formula"
    REFERENCE = "reference"
    FOOTNOTE = "footnote"
    HEADER = "header"
    FOOTER = "footer"
    UNKNOWN = "unknown"


class Language(Enum):
    """Supported languages for classification."""
    TURKISH = "tr"
    ENGLISH = "en"
    GERMAN = "de"
    FRENCH = "fr"
    SPANISH = "es"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    RUSSIAN = "ru"
    ARABIC = "ar"
    CHINESE = "zh"
    UNKNOWN = "unknown"


@dataclass
class ClassificationResult:
    """Result of text classification."""
    category: Union[DocumentType, ContentCategory, Language]
    confidence: float
    features: Dict[str, Any] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.features is None:
            self.features = {}
        if self.metadata is None:
            self.metadata = {}


@dataclass
class MultiClassificationResult:
    """Result of multi-label classification."""
    predictions: List[ClassificationResult]
    primary_category: Union[DocumentType, ContentCategory, Language]
    confidence_scores: Dict[str, float]
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class DocumentClassifier:
    """Classifies documents by type and content."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize document classifier.
        
        Args:
            config: Configuration options
        """
        self.config = config or {}
        
        # Classification thresholds
        self.min_confidence = self.config.get('min_confidence', 0.6)
        self.use_ml_models = self.config.get('use_ml_models', False)
        
        # Language patterns
        self.language_patterns = self._init_language_patterns()
        
        # Document type patterns
        self.document_patterns = self._init_document_patterns()
        
        # Content category patterns
        self.content_patterns = self._init_content_patterns()
        
        logger.info("Document classifier initialized")
    
    def _init_language_patterns(self) -> Dict[Language, List[str]]:
        """Initialize language detection patterns."""
        return {
            Language.TURKISH: [
                r'\b(ve|veya|ile|için|olan|olarak|bu|şu|o|bir|iki|üç|dört|beş)\b',
                r'[çğıöşüÇĞIÖŞÜ]',
                r'\b(madde|fıkra|bent|paragraf|bölüm|kısım)\b',
                r'\b(tarih|sayı|kanun|yönetmelik|tebliğ)\b'
            ],
            Language.ENGLISH: [
                r'\b(the|and|or|with|for|that|this|one|two|three|four|five)\b',
                r'\b(article|section|paragraph|chapter|clause)\b',
                r'\b(date|number|law|regulation|notice)\b'
            ],
            Language.GERMAN: [
                r'\b(der|die|das|und|oder|mit|für|dass|dieser|ein|zwei|drei)\b',
                r'[äöüßÄÖÜ]',
                r'\b(artikel|abschnitt|absatz|kapitel|klausel)\b'
            ],
            Language.FRENCH: [
                r'\b(le|la|les|et|ou|avec|pour|que|ce|un|deux|trois)\b',
                r'[àâäéèêëïîôöùûüÿçÀÂÄÉÈÊËÏÎÔÖÙÛÜŸÇ]',
                r'\b(article|section|paragraphe|chapitre|clause)\b'
            ]
        }
    
    def _init_document_patterns(self) -> Dict[DocumentType, List[str]]:
        """Initialize document type detection patterns."""
        return {
            DocumentType.LEGAL: [
                r'\b(kanun|yönetmelik|tebliğ|genelge|karar|hüküm|madde|fıkra)\b',
                r'\b(law|regulation|statute|ordinance|decree|article|clause)\b',
                r'\b(contract|agreement|terms|conditions|liability)\b',
                r'\b(sözleşme|anlaşma|şart|koşul|sorumluluk|yükümlülük)\b'
            ],
            DocumentType.ACADEMIC: [
                r'\b(abstract|introduction|methodology|results|conclusion|references)\b',
                r'\b(özet|giriş|metodoloji|sonuç|kaynakça|bibliyografya)\b',
                r'\b(research|study|analysis|experiment|hypothesis)\b',
                r'\b(araştırma|çalışma|analiz|deney|hipotez)\b'
            ],
            DocumentType.TECHNICAL: [
                r'\b(specification|manual|guide|documentation|API|SDK)\b',
                r'\b(şartname|kılavuz|dokümantasyon|teknik|özellik)\b',
                r'\b(function|method|class|variable|parameter)\b',
                r'\b(fonksiyon|metod|sınıf|değişken|parametre)\b'
            ],
            DocumentType.BUSINESS: [
                r'\b(report|proposal|plan|strategy|budget|revenue)\b',
                r'\b(rapor|teklif|plan|strateji|bütçe|gelir)\b',
                r'\b(company|corporation|business|market|sales)\b',
                r'\b(şirket|işletme|pazar|satış|müşteri)\b'
            ],
            DocumentType.CONTRACT: [
                r'\b(party|parties|whereas|therefore|hereby|agreement)\b',
                r'\b(taraf|taraflar|oysa|bu nedenle|işbu|anlaşma)\b',
                r'\b(obligation|right|duty|breach|termination)\b',
                r'\b(yükümlülük|hak|görev|ihlal|fesih)\b'
            ]
        }
    
    def _init_content_patterns(self) -> Dict[ContentCategory, List[str]]:
        """Initialize content category detection patterns."""
        return {
            ContentCategory.HEADING: [
                r'^\d+\.\s+[A-ZÜĞŞÇÖI]',  # "1. Başlık"
                r'^[A-ZÜĞŞÇÖI][A-ZÜĞŞÇÖIa-züğşçöı\s]{2,50}$',
                r'^(BÖLÜM|CHAPTER|SECTION)\s+\d+',
                r'^(MADDE|ARTICLE)\s+\d+'
            ],
            ContentCategory.LIST: [
                r'^[•·▪▫◦‣⁃]\s+',  # Bullet points
                r'^\d+[.):)]\s+',   # Numbered lists
                r'^[a-zA-Z][.):)]\s+',  # Lettered lists
                r'^[-*+]\s+'       # Dash/asterisk lists
            ],
            ContentCategory.REFERENCE: [
                r'\[\d+\]',  # [1], [2], etc.
                r'\(\d{4}\)',  # (2023)
                r'\bet\s+al\.',  # et al.
                r'\bvd\.',  # vd. (Turkish)
                r'\bpp\.',  # pp.
                r'\bvol\.',  # vol.
            ],
            ContentCategory.FORMULA: [
                r'\$.*\$',  # LaTeX inline math
                r'\\\[.*\\\]',  # LaTeX display math
                r'[∑∏∫∂∇±×÷≤≥≠≈∞]',  # Math symbols
                r'[α-ωΑ-Ω]'  # Greek letters
            ],
            ContentCategory.CODE: [
                r'^\s*def\s+\w+\(',  # Python function
                r'^\s*class\s+\w+',  # Python class
                r'^\s*import\s+\w+',  # Python import
                r'^\s*#include\s*<',  # C include
                r'^\s*function\s+\w+\('  # JavaScript function
            ]
        }
    
    def classify_document_type(self, text: str) -> ClassificationResult:
        """Classify document type.
        
        Args:
            text: Document text to classify
            
        Returns:
            ClassificationResult with document type
        """
        scores = {}
        
        for doc_type, patterns in self.document_patterns.items():
            score = self._calculate_pattern_score(text, patterns)
            scores[doc_type] = score
        
        # Find best match
        best_type = max(scores, key=scores.get)
        best_score = scores[best_type]
        
        # Check if confidence is above threshold
        if best_score < self.min_confidence:
            best_type = DocumentType.UNKNOWN
            best_score = 0.0
        
        return ClassificationResult(
            category=best_type,
            confidence=best_score,
            features={'pattern_scores': scores},
            metadata={'method': 'pattern_matching'}
        )
    
    def classify_content_category(self, text: str) -> ClassificationResult:
        """Classify content category.
        
        Args:
            text: Text content to classify
            
        Returns:
            ClassificationResult with content category
        """
        scores = {}
        
        for category, patterns in self.content_patterns.items():
            score = self._calculate_pattern_score(text, patterns)
            scores[category] = score
        
        # Additional heuristics
        scores.update(self._apply_content_heuristics(text))
        
        # Find best match
        best_category = max(scores, key=scores.get)
        best_score = scores[best_category]
        
        # Default to paragraph if no strong match
        if best_score < self.min_confidence:
            if len(text.strip()) > 50:  # Long text is likely a paragraph
                best_category = ContentCategory.PARAGRAPH
                best_score = 0.7
            else:
                best_category = ContentCategory.UNKNOWN
                best_score = 0.0
        
        return ClassificationResult(
            category=best_category,
            confidence=best_score,
            features={'pattern_scores': scores},
            metadata={'method': 'pattern_matching_with_heuristics'}
        )
    
    def detect_language(self, text: str) -> ClassificationResult:
        """Detect text language.
        
        Args:
            text: Text to analyze
            
        Returns:
            ClassificationResult with detected language
        """
        scores = {}
        
        for language, patterns in self.language_patterns.items():
            score = self._calculate_pattern_score(text, patterns)
            scores[language] = score
        
        # Additional character-based scoring
        char_scores = self._calculate_character_scores(text)
        
        # Combine pattern and character scores
        for language in scores:
            if language in char_scores:
                scores[language] = (scores[language] + char_scores[language]) / 2
        
        # Find best match
        best_language = max(scores, key=scores.get)
        best_score = scores[best_language]
        
        # Check if confidence is above threshold
        if best_score < self.min_confidence:
            best_language = Language.UNKNOWN
            best_score = 0.0
        
        return ClassificationResult(
            category=best_language,
            confidence=best_score,
            features={'pattern_scores': scores, 'char_scores': char_scores},
            metadata={'method': 'pattern_and_character_analysis'}
        )
    
    def classify_multi_label(self, text: str) -> MultiClassificationResult:
        """Perform multi-label classification.
        
        Args:
            text: Text to classify
            
        Returns:
            MultiClassificationResult with multiple classifications
        """
        predictions = []
        
        # Classify document type
        doc_type_result = self.classify_document_type(text)
        predictions.append(doc_type_result)
        
        # Classify content category
        content_result = self.classify_content_category(text)
        predictions.append(content_result)
        
        # Detect language
        language_result = self.detect_language(text)
        predictions.append(language_result)
        
        # Determine primary category (highest confidence)
        primary_category = max(predictions, key=lambda x: x.confidence).category
        
        # Collect confidence scores
        confidence_scores = {
            'document_type': doc_type_result.confidence,
            'content_category': content_result.confidence,
            'language': language_result.confidence
        }
        
        return MultiClassificationResult(
            predictions=predictions,
            primary_category=primary_category,
            confidence_scores=confidence_scores,
            metadata={'method': 'multi_label_classification'}
        )
    
    def _calculate_pattern_score(self, text: str, patterns: List[str]) -> float:
        """Calculate pattern matching score."""
        if not patterns:
            return 0.0
        
        matches = 0
        total_patterns = len(patterns)
        
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
                matches += 1
        
        return matches / total_patterns
    
    def _calculate_character_scores(self, text: str) -> Dict[Language, float]:
        """Calculate language scores based on character frequency."""
        scores = {}
        
        # Turkish specific characters
        turkish_chars = 'çğıöşüÇĞIÖŞÜ'
        turkish_count = sum(1 for char in text if char in turkish_chars)
        scores[Language.TURKISH] = min(turkish_count / max(len(text), 1), 1.0)
        
        # German specific characters
        german_chars = 'äöüßÄÖÜ'
        german_count = sum(1 for char in text if char in german_chars)
        scores[Language.GERMAN] = min(german_count / max(len(text), 1), 1.0)
        
        # French specific characters
        french_chars = 'àâäéèêëïîôöùûüÿçÀÂÄÉÈÊËÏÎÔÖÙÛÜŸÇ'
        french_count = sum(1 for char in text if char in french_chars)
        scores[Language.FRENCH] = min(french_count / max(len(text), 1), 1.0)
        
        # English (default for ASCII)
        ascii_count = sum(1 for char in text if ord(char) < 128)
        scores[Language.ENGLISH] = ascii_count / max(len(text), 1)
        
        return scores
    
    def _apply_content_heuristics(self, text: str) -> Dict[ContentCategory, float]:
        """Apply additional heuristics for content classification."""
        scores = {}
        
        # Length-based heuristics
        text_length = len(text.strip())
        
        # Short text is likely a heading
        if text_length < 100 and not text.endswith('.'):
            scores[ContentCategory.HEADING] = 0.6
        
        # Very long text is likely a paragraph
        elif text_length > 200:
            scores[ContentCategory.PARAGRAPH] = 0.7
        
        # Check for table-like structure
        if '\t' in text or text.count('|') > 2:
            scores[ContentCategory.TABLE] = 0.8
        
        # Check for figure references
        if re.search(r'(Figure|Fig|Şekil|Resim)\s*\d+', text, re.IGNORECASE):
            scores[ContentCategory.CAPTION] = 0.8
        
        # Check for quotes
        if (text.strip().startswith('"') and text.strip().endswith('"')) or \
           (text.strip().startswith('"') and text.strip().endswith('"')):
            scores[ContentCategory.QUOTE] = 0.9
        
        return scores
    
    def batch_classify(self, texts: List[str]) -> List[MultiClassificationResult]:
        """Classify multiple texts.
        
        Args:
            texts: List of texts to classify
            
        Returns:
            List of MultiClassificationResult
        """
        results = []
        
        for text in texts:
            result = self.classify_multi_label(text)
            results.append(result)
        
        return results
    
    def get_classification_stats(self, results: List[MultiClassificationResult]) -> Dict[str, Any]:
        """Get statistics from classification results.
        
        Args:
            results: List of classification results
            
        Returns:
            Dictionary with statistics
        """
        stats = {
            'total_texts': len(results),
            'document_types': {},
            'content_categories': {},
            'languages': {},
            'avg_confidence': {
                'document_type': 0.0,
                'content_category': 0.0,
                'language': 0.0
            }
        }
        
        if not results:
            return stats
        
        # Count categories
        for result in results:
            for prediction in result.predictions:
                category = prediction.category
                
                if isinstance(category, DocumentType):
                    doc_type = category.value
                    stats['document_types'][doc_type] = stats['document_types'].get(doc_type, 0) + 1
                elif isinstance(category, ContentCategory):
                    content_cat = category.value
                    stats['content_categories'][content_cat] = stats['content_categories'].get(content_cat, 0) + 1
                elif isinstance(category, Language):
                    lang = category.value
                    stats['languages'][lang] = stats['languages'].get(lang, 0) + 1
        
        # Calculate average confidences
        total_doc_conf = sum(r.confidence_scores.get('document_type', 0) for r in results)
        total_content_conf = sum(r.confidence_scores.get('content_category', 0) for r in results)
        total_lang_conf = sum(r.confidence_scores.get('language', 0) for r in results)
        
        stats['avg_confidence']['document_type'] = total_doc_conf / len(results)
        stats['avg_confidence']['content_category'] = total_content_conf / len(results)
        stats['avg_confidence']['language'] = total_lang_conf / len(results)
        
        return stats


class ContentClassifier:
    """Specialized classifier for content categorization."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize content classifier.
        
        Args:
            config: Configuration options
        """
        self.config = config or {}
        self.document_classifier = DocumentClassifier(config)
        
        logger.info("Content classifier initialized")
    
    def classify_chunk(self, chunk_text: str, context: Optional[Dict[str, Any]] = None) -> ClassificationResult:
        """Classify a text chunk.
        
        Args:
            chunk_text: Text chunk to classify
            context: Additional context information
            
        Returns:
            ClassificationResult with content category
        """
        return self.document_classifier.classify_content_category(chunk_text)
    
    def classify_chunks(self, chunks: List[str], contexts: Optional[List[Dict[str, Any]]] = None) -> List[ClassificationResult]:
        """Classify multiple text chunks.
        
        Args:
            chunks: List of text chunks
            contexts: Optional list of context information
            
        Returns:
            List of ClassificationResult
        """
        results = []
        
        for i, chunk in enumerate(chunks):
            context = contexts[i] if contexts and i < len(contexts) else None
            result = self.classify_chunk(chunk, context)
            results.append(result)
        
        return results
    
    def filter_by_category(self, chunks: List[str], target_category: ContentCategory) -> List[Tuple[str, int]]:
        """Filter chunks by content category.
        
        Args:
            chunks: List of text chunks
            target_category: Target content category
            
        Returns:
            List of (chunk_text, original_index) tuples
        """
        filtered = []
        
        for i, chunk in enumerate(chunks):
            result = self.classify_chunk(chunk)
            if result.category == target_category:
                filtered.append((chunk, i))
        
        return filtered
    
    def get_category_distribution(self, chunks: List[str]) -> Dict[str, int]:
        """Get distribution of content categories in chunks.
        
        Args:
            chunks: List of text chunks
            
        Returns:
            Dictionary with category counts
        """
        distribution = {}
        
        for chunk in chunks:
            result = self.classify_chunk(chunk)
            category = result.category.value if hasattr(result.category, 'value') else str(result.category)
            distribution[category] = distribution.get(category, 0) + 1
        
        return distribution