"""Quality assessment for semantic chunks."""

from typing import Dict, List, Optional, Any, Union, Tuple
import logging
import numpy as np
from dataclasses import dataclass
from enum import Enum
import re
import warnings
warnings.filterwarnings('ignore')

# Text analysis
try:
    from textstat import flesch_reading_ease, flesch_kincaid_grade
    TEXTSTAT_AVAILABLE = True
except ImportError:
    TEXTSTAT_AVAILABLE = False
    logging.warning("textstat not available")

# Language detection
try:
    from langdetect import detect, detect_langs
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False
    logging.warning("langdetect not available")

# Similarity metrics
try:
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.feature_extraction.text import TfidfVectorizer
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("scikit-learn not available")

from ..core.chunk import SemanticChunk, QualityMetrics
from ..core.config import QualityConfig
from .embeddings import EmbeddingResult


class QualityDimension(Enum):
    """Quality assessment dimensions."""
    COHERENCE = "coherence"
    COMPLETENESS = "completeness"
    READABILITY = "readability"
    CONSISTENCY = "consistency"
    RELEVANCE = "relevance"
    STRUCTURE = "structure"
    LEGAL_COMPLIANCE = "legal_compliance"
    INFORMATION_DENSITY = "information_density"


@dataclass
class QualityAssessment:
    """Comprehensive quality assessment result."""
    overall_score: float
    dimension_scores: Dict[QualityDimension, float]
    detailed_metrics: Dict[str, float]
    issues: List[str]
    recommendations: List[str]
    metadata: Dict[str, Any]
    processing_time: float


class QualityAssessor:
    """Comprehensive quality assessor for semantic chunks."""
    
    def __init__(self, config: QualityConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize text analysis tools
        self.tfidf_vectorizer = None
        if SKLEARN_AVAILABLE:
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',  # Will be enhanced for Turkish
                ngram_range=(1, 2)
            )
        
        # Turkish stop words and patterns
        self.turkish_stop_words = self._get_turkish_stop_words()
        self.legal_patterns = self._get_legal_patterns()
        
        # Quality thresholds
        self.quality_thresholds = {
            QualityDimension.COHERENCE: 0.7,
            QualityDimension.COMPLETENESS: 0.6,
            QualityDimension.READABILITY: 0.5,
            QualityDimension.CONSISTENCY: 0.8,
            QualityDimension.RELEVANCE: 0.7,
            QualityDimension.STRUCTURE: 0.6,
            QualityDimension.LEGAL_COMPLIANCE: 0.8,
            QualityDimension.INFORMATION_DENSITY: 0.5
        }
    
    def _get_turkish_stop_words(self) -> set:
        """Get Turkish stop words."""
        return {
            "ve", "ile", "bir", "bu", "şu", "o", "da", "de", "ta", "te",
            "ki", "mi", "mı", "mu", "mü", "için", "gibi", "kadar", "daha",
            "en", "çok", "az", "var", "yok", "olan", "olarak", "ancak",
            "fakat", "lakin", "ama", "veya", "yahut", "ya", "hem", "ne",
            "nasıl", "neden", "niçin", "nerede", "ne zaman", "hangi", "kim"
        }
    
    def _get_legal_patterns(self) -> Dict[str, List[str]]:
        """Get Turkish legal document patterns."""
        return {
            "article_references": [
                r"\b(\d+)\s*\.?\s*madde",
                r"madde\s*(\d+)",
                r"(\d+)\s*nci\s*madde",
                r"(\d+)\s*inci\s*madde"
            ],
            "paragraph_references": [
                r"\b(\d+)\s*\.?\s*fıkra",
                r"fıkra\s*(\d+)",
                r"(\d+)\s*nci\s*fıkra",
                r"(\d+)\s*inci\s*fıkra"
            ],
            "subparagraph_references": [
                r"\b([a-z])\s*\)\s*bent",
                r"bent\s*([a-z])\s*\)",
                r"\b([a-z])\s*bendi"
            ],
            "law_references": [
                r"\b(\d+)\s*sayılı\s*kanun",
                r"kanun\s*no\s*:?\s*(\d+)",
                r"(\d{4})\s*tarihli.*kanun"
            ],
            "regulation_references": [
                r"yönetmelik",
                r"tebliğ",
                r"genelge",
                r"tüzük"
            ]
        }
    
    def assess_chunk_quality(self, chunk: SemanticChunk, context_chunks: List[SemanticChunk] = None) -> QualityAssessment:
        """Assess the quality of a semantic chunk."""
        import time
        start_time = time.time()
        
        # Calculate dimension scores
        dimension_scores = {}
        detailed_metrics = {}
        issues = []
        recommendations = []
        
        # Coherence assessment
        coherence_score, coherence_metrics, coherence_issues = self._assess_coherence(chunk)
        dimension_scores[QualityDimension.COHERENCE] = coherence_score
        detailed_metrics.update(coherence_metrics)
        issues.extend(coherence_issues)
        
        # Completeness assessment
        completeness_score, completeness_metrics, completeness_issues = self._assess_completeness(chunk)
        dimension_scores[QualityDimension.COMPLETENESS] = completeness_score
        detailed_metrics.update(completeness_metrics)
        issues.extend(completeness_issues)
        
        # Readability assessment
        readability_score, readability_metrics, readability_issues = self._assess_readability(chunk)
        dimension_scores[QualityDimension.READABILITY] = readability_score
        detailed_metrics.update(readability_metrics)
        issues.extend(readability_issues)
        
        # Consistency assessment
        consistency_score, consistency_metrics, consistency_issues = self._assess_consistency(chunk, context_chunks)
        dimension_scores[QualityDimension.CONSISTENCY] = consistency_score
        detailed_metrics.update(consistency_metrics)
        issues.extend(consistency_issues)
        
        # Relevance assessment
        relevance_score, relevance_metrics, relevance_issues = self._assess_relevance(chunk)
        dimension_scores[QualityDimension.RELEVANCE] = relevance_score
        detailed_metrics.update(relevance_metrics)
        issues.extend(relevance_issues)
        
        # Structure assessment
        structure_score, structure_metrics, structure_issues = self._assess_structure(chunk)
        dimension_scores[QualityDimension.STRUCTURE] = structure_score
        detailed_metrics.update(structure_metrics)
        issues.extend(structure_issues)
        
        # Legal compliance assessment
        legal_score, legal_metrics, legal_issues = self._assess_legal_compliance(chunk)
        dimension_scores[QualityDimension.LEGAL_COMPLIANCE] = legal_score
        detailed_metrics.update(legal_metrics)
        issues.extend(legal_issues)
        
        # Information density assessment
        density_score, density_metrics, density_issues = self._assess_information_density(chunk)
        dimension_scores[QualityDimension.INFORMATION_DENSITY] = density_score
        detailed_metrics.update(density_metrics)
        issues.extend(density_issues)
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(dimension_scores)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(dimension_scores, issues)
        
        return QualityAssessment(
            overall_score=overall_score,
            dimension_scores=dimension_scores,
            detailed_metrics=detailed_metrics,
            issues=issues,
            recommendations=recommendations,
            metadata={
                "chunk_id": chunk.id,
                "content_type": chunk.content_type.value,
                "importance_level": chunk.importance_level.value,
                "text_length": len(chunk.content),
                "word_count": len(chunk.content.split())
            },
            processing_time=time.time() - start_time
        )
    
    def _assess_coherence(self, chunk: SemanticChunk) -> Tuple[float, Dict[str, float], List[str]]:
        """Assess text coherence."""
        metrics = {}
        issues = []
        
        text = chunk.content
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        # Sentence count and length variation
        if sentences:
            sentence_lengths = [len(s.split()) for s in sentences]
            metrics['sentence_count'] = len(sentences)
            metrics['avg_sentence_length'] = np.mean(sentence_lengths)
            metrics['sentence_length_std'] = np.std(sentence_lengths)
            
            # Check for very short or very long sentences
            if any(length < 3 for length in sentence_lengths):
                issues.append("Contains very short sentences")
            
            if any(length > 50 for length in sentence_lengths):
                issues.append("Contains very long sentences")
        
        # Transition words and connectors
        transition_words = [
            "ancak", "fakat", "lakin", "ama", "bununla birlikte",
            "öte yandan", "diğer taraftan", "ayrıca", "bunun yanında",
            "sonuç olarak", "bu nedenle", "dolayısıyla", "çünkü"
        ]
        
        transition_count = sum(1 for word in transition_words if word in text.lower())
        metrics['transition_density'] = transition_count / len(text.split()) if text.split() else 0
        
        if metrics['transition_density'] < 0.01:
            issues.append("Low transition word density - may lack coherence")
        
        # Repetition analysis
        words = text.lower().split()
        if words:
            word_freq = {}
            for word in words:
                if word not in self.turkish_stop_words and len(word) > 3:
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            if word_freq:
                max_freq = max(word_freq.values())
                metrics['max_word_frequency'] = max_freq
                metrics['vocabulary_diversity'] = len(word_freq) / len(words)
                
                if max_freq > len(words) * 0.1:
                    issues.append("High word repetition detected")
        
        # Calculate coherence score
        score = 1.0
        
        # Penalize issues
        if metrics.get('sentence_length_std', 0) > 15:
            score -= 0.2
        
        if metrics.get('transition_density', 0) < 0.01:
            score -= 0.3
        
        if metrics.get('vocabulary_diversity', 1) < 0.3:
            score -= 0.2
        
        score = max(0.0, score)
        
        return score, metrics, issues
    
    def _assess_completeness(self, chunk: SemanticChunk) -> Tuple[float, Dict[str, float], List[str]]:
        """Assess content completeness."""
        metrics = {}
        issues = []
        
        text = chunk.content
        
        # Check for incomplete sentences
        incomplete_patterns = [
            r'\.\.\.',  # Ellipsis
            r'\[.*\]',   # Brackets indicating missing content
            r'\(.*\?.*\)',  # Question marks in parentheses
            r'\bvb\b',   # "ve benzeri" indicating incomplete list
            r'\betc\b',  # etc.
            r'\bgibi\b$'  # "gibi" at end of sentence
        ]
        
        incomplete_count = 0
        for pattern in incomplete_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            incomplete_count += len(matches)
        
        metrics['incomplete_indicators'] = incomplete_count
        
        if incomplete_count > 0:
            issues.append(f"Found {incomplete_count} indicators of incomplete content")
        
        # Check for proper sentence endings
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        if sentences:
            last_sentence = sentences[-1]
            if not last_sentence.endswith(('.', '!', '?', ':', ';')):
                issues.append("Text does not end with proper punctuation")
                metrics['proper_ending'] = 0.0
            else:
                metrics['proper_ending'] = 1.0
        
        # Check for balanced parentheses and quotes
        open_parens = text.count('(')
        close_parens = text.count(')')
        open_quotes = text.count('"')
        
        metrics['parentheses_balanced'] = 1.0 if open_parens == close_parens else 0.0
        metrics['quotes_balanced'] = 1.0 if open_quotes % 2 == 0 else 0.0
        
        if open_parens != close_parens:
            issues.append("Unbalanced parentheses")
        
        if open_quotes % 2 != 0:
            issues.append("Unbalanced quotes")
        
        # Content type specific completeness
        if chunk.content_type.value == "definition":
            if "tanım" not in text.lower() and "anlamı" not in text.lower():
                issues.append("Definition chunk lacks definition keywords")
        
        # Calculate completeness score
        score = 1.0
        
        if incomplete_count > 0:
            score -= 0.3 * min(1.0, incomplete_count / 3)
        
        if metrics.get('proper_ending', 1) == 0:
            score -= 0.2
        
        if metrics.get('parentheses_balanced', 1) == 0:
            score -= 0.2
        
        if metrics.get('quotes_balanced', 1) == 0:
            score -= 0.1
        
        score = max(0.0, score)
        
        return score, metrics, issues
    
    def _assess_readability(self, chunk: SemanticChunk) -> Tuple[float, Dict[str, float], List[str]]:
        """Assess text readability."""
        metrics = {}
        issues = []
        
        text = chunk.content
        
        # Basic readability metrics
        words = text.split()
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        if words and sentences:
            metrics['avg_words_per_sentence'] = len(words) / len(sentences)
            
            # Average word length
            word_lengths = [len(word.strip('.,!?;:()[]"')) for word in words]
            metrics['avg_word_length'] = np.mean(word_lengths)
            
            # Complex word ratio (words > 6 characters)
            complex_words = [word for word in words if len(word.strip('.,!?;:()[]"')) > 6]
            metrics['complex_word_ratio'] = len(complex_words) / len(words)
            
            # Check for readability issues
            if metrics['avg_words_per_sentence'] > 25:
                issues.append("Sentences are too long on average")
            
            if metrics['avg_word_length'] > 8:
                issues.append("Words are too long on average")
            
            if metrics['complex_word_ratio'] > 0.4:
                issues.append("High ratio of complex words")
        
        # Turkish-specific readability
        # Check for excessive use of passive voice
        passive_indicators = ["edilir", "olunur", "yapılır", "alınır", "verilir"]
        passive_count = sum(1 for indicator in passive_indicators if indicator in text.lower())
        metrics['passive_voice_ratio'] = passive_count / len(words) if words else 0
        
        if metrics['passive_voice_ratio'] > 0.1:
            issues.append("Excessive use of passive voice")
        
        # Check for legal jargon density
        legal_jargon = [
            "müteakip", "mezkur", "mezkûr", "merkum", "mahsus", "müteallik",
            "münhasır", "mütevelli", "müstahak", "müstahdem", "müteselsil"
        ]
        jargon_count = sum(1 for jargon in legal_jargon if jargon in text.lower())
        metrics['legal_jargon_ratio'] = jargon_count / len(words) if words else 0
        
        if metrics['legal_jargon_ratio'] > 0.05:
            issues.append("High density of archaic legal jargon")
        
        # Calculate readability score
        score = 1.0
        
        if metrics.get('avg_words_per_sentence', 0) > 25:
            score -= 0.3
        
        if metrics.get('complex_word_ratio', 0) > 0.4:
            score -= 0.2
        
        if metrics.get('passive_voice_ratio', 0) > 0.1:
            score -= 0.2
        
        if metrics.get('legal_jargon_ratio', 0) > 0.05:
            score -= 0.3
        
        score = max(0.0, score)
        
        return score, metrics, issues
    
    def _assess_consistency(self, chunk: SemanticChunk, context_chunks: List[SemanticChunk] = None) -> Tuple[float, Dict[str, float], List[str]]:
        """Assess consistency with context."""
        metrics = {}
        issues = []
        
        # Internal consistency
        text = chunk.content
        
        # Check for consistent terminology
        # Extract key terms and check for variations
        key_terms = self._extract_key_terms(text)
        metrics['unique_terms'] = len(key_terms)
        
        # Check for consistent formatting
        # Numbers formatting
        number_patterns = re.findall(r'\d+', text)
        if number_patterns:
            # Check if numbers are consistently formatted
            has_periods = any('.' in text[max(0, text.find(num)-5):text.find(num)+len(num)+5] for num in number_patterns)
            has_commas = any(',' in text[max(0, text.find(num)-5):text.find(num)+len(num)+5] for num in number_patterns)
            
            if has_periods and has_commas:
                issues.append("Inconsistent number formatting")
        
        # Context consistency
        if context_chunks:
            # Compare with similar chunks
            similar_chunks = [c for c in context_chunks if c.content_type == chunk.content_type]
            
            if similar_chunks:
                # Check terminology consistency
                context_terms = set()
                for ctx_chunk in similar_chunks:
                    context_terms.update(self._extract_key_terms(ctx_chunk.content))
                
                common_terms = key_terms.intersection(context_terms)
                metrics['terminology_overlap'] = len(common_terms) / len(key_terms) if key_terms else 0
                
                if metrics['terminology_overlap'] < 0.3:
                    issues.append("Low terminology overlap with similar chunks")
        
        # Calculate consistency score
        score = 1.0
        
        if len(issues) > 0:
            score -= 0.2 * len(issues)
        
        score = max(0.0, score)
        
        return score, metrics, issues
    
    def _assess_relevance(self, chunk: SemanticChunk) -> Tuple[float, Dict[str, float], List[str]]:
        """Assess content relevance."""
        metrics = {}
        issues = []
        
        text = chunk.content
        
        # Check for legal content indicators
        legal_indicators = [
            "madde", "fıkra", "bent", "kanun", "yönetmelik", "hüküm",
            "karar", "mahkeme", "hâkim", "dava", "hak", "yükümlülük"
        ]
        
        legal_count = sum(1 for indicator in legal_indicators if indicator in text.lower())
        metrics['legal_indicator_density'] = legal_count / len(text.split()) if text.split() else 0
        
        # Check content type alignment
        content_type = chunk.content_type.value
        type_keywords = {
            "definition": ["tanım", "anlamı", "ifade eder", "demektir"],
            "rule": ["zorunlu", "mecburi", "yapılır", "uygulanır"],
            "exception": ["hariç", "istisna", "ancak", "fakat"],
            "sanction": ["ceza", "yaptırım", "hapis", "para cezası"]
        }
        
        if content_type in type_keywords:
            keyword_count = sum(1 for keyword in type_keywords[content_type] if keyword in text.lower())
            metrics['content_type_alignment'] = keyword_count / len(type_keywords[content_type])
            
            if metrics['content_type_alignment'] < 0.2:
                issues.append(f"Low alignment with {content_type} content type")
        
        # Check for off-topic content
        off_topic_indicators = [
            "spor", "müzik", "sanat", "eğlence", "turizm", "yemek",
            "moda", "teknoloji" # unless in legal context
        ]
        
        off_topic_count = sum(1 for indicator in off_topic_indicators if indicator in text.lower())
        if off_topic_count > 0:
            issues.append("May contain off-topic content")
        
        # Calculate relevance score
        score = 1.0
        
        if metrics.get('legal_indicator_density', 0) < 0.01:
            score -= 0.3
        
        if metrics.get('content_type_alignment', 1) < 0.2:
            score -= 0.4
        
        if off_topic_count > 0:
            score -= 0.2
        
        score = max(0.0, score)
        
        return score, metrics, issues
    
    def _assess_structure(self, chunk: SemanticChunk) -> Tuple[float, Dict[str, float], List[str]]:
        """Assess structural quality."""
        metrics = {}
        issues = []
        
        text = chunk.content
        
        # Check for proper paragraph structure
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        metrics['paragraph_count'] = len(paragraphs)
        
        if len(paragraphs) == 0:
            issues.append("No clear paragraph structure")
        
        # Check for lists and enumerations
        list_patterns = [
            r'^\s*[a-z]\)',  # a) b) c)
            r'^\s*\d+\.',    # 1. 2. 3.
            r'^\s*-',        # bullet points
            r'^\s*•'         # bullet points
        ]
        
        list_items = 0
        for pattern in list_patterns:
            matches = re.findall(pattern, text, re.MULTILINE)
            list_items += len(matches)
        
        metrics['list_items'] = list_items
        
        # Check for proper legal structure
        legal_structure_patterns = {
            'articles': r'\b(\d+)\s*\.?\s*madde',
            'paragraphs': r'\b(\d+)\s*\.?\s*fıkra',
            'subparagraphs': r'\b([a-z])\s*\)'
        }
        
        for structure_type, pattern in legal_structure_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            metrics[f'{structure_type}_count'] = len(matches)
        
        # Check for proper headings
        heading_patterns = [
            r'^[A-ZÜĞŞÇÖI][A-ZÜĞŞÇÖIa-züğşçöı\s]+:',  # HEADING:
            r'^\d+\.[A-ZÜĞŞÇÖI]',  # 1.HEADING
            r'^[A-ZÜĞŞÇÖI]{3,}$'   # ALL CAPS HEADING
        ]
        
        heading_count = 0
        for pattern in heading_patterns:
            matches = re.findall(pattern, text, re.MULTILINE)
            heading_count += len(matches)
        
        metrics['heading_count'] = heading_count
        
        # Calculate structure score
        score = 1.0
        
        if metrics['paragraph_count'] == 0:
            score -= 0.3
        
        # Bonus for good structure
        if metrics.get('articles_count', 0) > 0:
            score += 0.1
        
        if metrics.get('heading_count', 0) > 0:
            score += 0.1
        
        score = min(1.0, max(0.0, score))
        
        return score, metrics, issues
    
    def _assess_legal_compliance(self, chunk: SemanticChunk) -> Tuple[float, Dict[str, float], List[str]]:
        """Assess legal document compliance."""
        metrics = {}
        issues = []
        
        text = chunk.content
        
        # Check for proper legal references
        reference_patterns = self.legal_patterns
        total_references = 0
        
        for ref_type, patterns in reference_patterns.items():
            ref_count = 0
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                ref_count += len(matches)
            
            metrics[f'{ref_type}_count'] = ref_count
            total_references += ref_count
        
        metrics['total_legal_references'] = total_references
        
        # Check for proper legal language
        formal_language_indicators = [
            "müteakip", "mahfuz", "saklı kalmak", "hükümsüz", "batıl",
            "meri", "yürürlük", "ilga", "tadil", "değişiklik"
        ]
        
        formal_count = sum(1 for indicator in formal_language_indicators if indicator in text.lower())
        metrics['formal_language_density'] = formal_count / len(text.split()) if text.split() else 0
        
        # Check for required legal elements based on content type
        content_type = chunk.content_type.value
        
        if content_type == "sanction":
            sanction_elements = ["ceza", "para cezası", "hapis", "yaptırım"]
            has_sanction_elements = any(element in text.lower() for element in sanction_elements)
            if not has_sanction_elements:
                issues.append("Sanction content lacks proper sanction elements")
        
        elif content_type == "procedure":
            procedure_elements = ["başvuru", "süre", "işlem", "adım", "aşama"]
            has_procedure_elements = any(element in text.lower() for element in procedure_elements)
            if not has_procedure_elements:
                issues.append("Procedure content lacks procedural elements")
        
        # Check for date and number formatting
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{4}',  # DD/MM/YYYY
            r'\d{1,2}\.\d{1,2}\.\d{4}',  # DD.MM.YYYY
            r'\d{4}-\d{1,2}-\d{1,2}'   # YYYY-MM-DD
        ]
        
        date_count = 0
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            date_count += len(matches)
        
        metrics['date_references'] = date_count
        
        # Calculate legal compliance score
        score = 1.0
        
        if total_references == 0 and len(text.split()) > 50:
            score -= 0.2  # Long text without legal references
        
        if metrics.get('formal_language_density', 0) < 0.01 and len(text.split()) > 20:
            score -= 0.1  # Lacks formal legal language
        
        if len(issues) > 0:
            score -= 0.3 * len(issues)
        
        score = max(0.0, score)
        
        return score, metrics, issues
    
    def _assess_information_density(self, chunk: SemanticChunk) -> Tuple[float, Dict[str, float], List[str]]:
        """Assess information density."""
        metrics = {}
        issues = []
        
        text = chunk.content
        words = text.split()
        
        if not words:
            return 0.0, metrics, ["Empty content"]
        
        # Calculate information-bearing word ratio
        info_words = [word for word in words if word.lower() not in self.turkish_stop_words and len(word) > 2]
        metrics['info_word_ratio'] = len(info_words) / len(words)
        
        # Calculate unique word ratio
        unique_words = set(word.lower() for word in words)
        metrics['unique_word_ratio'] = len(unique_words) / len(words)
        
        # Calculate concept density
        legal_concepts = chunk.legal_concepts if chunk.legal_concepts else []
        metrics['concept_density'] = len(legal_concepts) / len(words) * 100  # concepts per 100 words
        
        # Check for redundancy
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        if len(sentences) > 1:
            # Simple redundancy check - look for repeated phrases
            phrases = []
            for sentence in sentences:
                sentence_words = sentence.split()
                for i in range(len(sentence_words) - 2):
                    phrase = ' '.join(sentence_words[i:i+3])
                    phrases.append(phrase.lower())
            
            if phrases:
                phrase_freq = {}
                for phrase in phrases:
                    phrase_freq[phrase] = phrase_freq.get(phrase, 0) + 1
                
                repeated_phrases = [phrase for phrase, freq in phrase_freq.items() if freq > 1]
                metrics['repeated_phrases'] = len(repeated_phrases)
                
                if len(repeated_phrases) > len(phrases) * 0.1:
                    issues.append("High phrase repetition detected")
        
        # Check for filler words
        filler_words = [
            "aslında", "gerçekten", "tabii ki", "elbette", "muhakkak",
            "kesinlikle", "tamamen", "oldukça", "gayet", "son derece"
        ]
        
        filler_count = sum(1 for word in filler_words if word in text.lower())
        metrics['filler_word_ratio'] = filler_count / len(words)
        
        if metrics['filler_word_ratio'] > 0.05:
            issues.append("High filler word usage")
        
        # Calculate information density score
        score = 1.0
        
        if metrics['info_word_ratio'] < 0.4:
            score -= 0.3
        
        if metrics['unique_word_ratio'] < 0.3:
            score -= 0.2
        
        if metrics.get('repeated_phrases', 0) > 3:
            score -= 0.2
        
        if metrics['filler_word_ratio'] > 0.05:
            score -= 0.2
        
        score = max(0.0, score)
        
        return score, metrics, issues
    
    def _extract_key_terms(self, text: str) -> set:
        """Extract key terms from text."""
        words = text.lower().split()
        key_terms = set()
        
        for word in words:
            # Clean word
            clean_word = word.strip('.,!?;:()[]"')
            
            # Add if it's a meaningful term
            if (len(clean_word) > 3 and 
                clean_word not in self.turkish_stop_words and 
                not clean_word.isdigit()):
                key_terms.add(clean_word)
        
        return key_terms
    
    def _calculate_overall_score(self, dimension_scores: Dict[QualityDimension, float]) -> float:
        """Calculate overall quality score."""
        # Weighted average of dimension scores
        weights = {
            QualityDimension.COHERENCE: 0.15,
            QualityDimension.COMPLETENESS: 0.15,
            QualityDimension.READABILITY: 0.10,
            QualityDimension.CONSISTENCY: 0.15,
            QualityDimension.RELEVANCE: 0.15,
            QualityDimension.STRUCTURE: 0.10,
            QualityDimension.LEGAL_COMPLIANCE: 0.15,
            QualityDimension.INFORMATION_DENSITY: 0.05
        }
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for dimension, score in dimension_scores.items():
            weight = weights.get(dimension, 0.1)
            weighted_sum += score * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def _generate_recommendations(self, dimension_scores: Dict[QualityDimension, float], issues: List[str]) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []
        
        # Dimension-specific recommendations
        for dimension, score in dimension_scores.items():
            threshold = self.quality_thresholds.get(dimension, 0.7)
            
            if score < threshold:
                if dimension == QualityDimension.COHERENCE:
                    recommendations.append("Improve text coherence by adding transition words and ensuring logical flow")
                
                elif dimension == QualityDimension.COMPLETENESS:
                    recommendations.append("Ensure all content is complete and properly terminated")
                
                elif dimension == QualityDimension.READABILITY:
                    recommendations.append("Simplify language and reduce sentence complexity")
                
                elif dimension == QualityDimension.CONSISTENCY:
                    recommendations.append("Maintain consistent terminology and formatting")
                
                elif dimension == QualityDimension.RELEVANCE:
                    recommendations.append("Focus on legal content and remove off-topic material")
                
                elif dimension == QualityDimension.STRUCTURE:
                    recommendations.append("Improve document structure with proper headings and organization")
                
                elif dimension == QualityDimension.LEGAL_COMPLIANCE:
                    recommendations.append("Add proper legal references and use formal legal language")
                
                elif dimension == QualityDimension.INFORMATION_DENSITY:
                    recommendations.append("Increase information density by removing redundant content")
        
        # Issue-specific recommendations
        if "very long sentences" in ' '.join(issues):
            recommendations.append("Break down long sentences into shorter, clearer ones")
        
        if "repetition" in ' '.join(issues):
            recommendations.append("Reduce repetitive content and vary vocabulary")
        
        if "passive voice" in ' '.join(issues):
            recommendations.append("Use active voice where appropriate to improve clarity")
        
        return list(set(recommendations))  # Remove duplicates
    
    def batch_assess_quality(self, chunks: List[SemanticChunk]) -> List[QualityAssessment]:
        """Assess quality for multiple chunks."""
        assessments = []
        
        for i, chunk in enumerate(chunks):
            try:
                # Provide context chunks (previous and next)
                context_chunks = []
                if i > 0:
                    context_chunks.append(chunks[i-1])
                if i < len(chunks) - 1:
                    context_chunks.append(chunks[i+1])
                
                assessment = self.assess_chunk_quality(chunk, context_chunks)
                assessments.append(assessment)
            
            except Exception as e:
                self.logger.error(f"Failed to assess chunk {chunk.id}: {e}")
                # Create default assessment
                assessments.append(QualityAssessment(
                    overall_score=0.0,
                    dimension_scores={},
                    detailed_metrics={},
                    issues=[f"Assessment failed: {str(e)}"],
                    recommendations=["Manual review required"],
                    metadata={"error": str(e)},
                    processing_time=0.0
                ))
        
        return assessments