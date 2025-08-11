"""Transformer model management and content classification."""

from typing import Dict, List, Optional, Any, Union, Tuple
from abc import ABC, abstractmethod
import logging
import numpy as np
from dataclasses import dataclass
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

# Transformers
try:
    from transformers import (
        AutoTokenizer, AutoModel, AutoModelForSequenceClassification,
        pipeline, BertTokenizer, BertModel, DistilBertTokenizer, DistilBertModel
    )
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.warning("transformers not available")

# Turkish NLP
try:
    import zeyrek
    ZEYREK_AVAILABLE = True
except ImportError:
    ZEYREK_AVAILABLE = False
    logging.warning("zeyrek not available")

try:
    from TurkishStemmer import TurkishStemmer
    TURKISH_STEMMER_AVAILABLE = True
except ImportError:
    TURKISH_STEMMER_AVAILABLE = False
    logging.warning("turkish-stemmer not available")

# Text processing
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    logging.warning("spacy not available")

try:
    import nltk
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    logging.warning("nltk not available")

from ..core.config import Config
from ..core.chunk import ContentType, ImportanceLevel, LegalConcept


class ModelType(Enum):
    """Available transformer model types."""
    BERT = "bert"
    DISTILBERT = "distilbert"
    ROBERTA = "roberta"
    TURKISH_BERT = "turkish_bert"
    MULTILINGUAL = "multilingual"
    CUSTOM = "custom"


@dataclass
class ClassificationResult:
    """Result of content classification."""
    content_type: ContentType
    importance_level: ImportanceLevel
    legal_concepts: List[LegalConcept]
    confidence_scores: Dict[str, float]
    features: Dict[str, Any]
    processing_time: float
    metadata: Dict[str, Any]


class TransformerManager:
    """Manager for transformer models with Turkish legal domain support."""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Model cache
        self.models = {}
        self.tokenizers = {}
        
        # Turkish NLP tools
        self.turkish_analyzer = None
        self.turkish_stemmer = None
        
        # Initialize Turkish tools
        self._initialize_turkish_tools()
        
        # Load default models
        self._load_default_models()
    
    def _initialize_turkish_tools(self):
        """Initialize Turkish NLP tools."""
        if ZEYREK_AVAILABLE:
            try:
                self.turkish_analyzer = zeyrek.MorphAnalyzer()
                self.logger.info("Zeyrek Turkish analyzer loaded")
            except Exception as e:
                self.logger.warning(f"Failed to load Zeyrek: {e}")
        
        if TURKISH_STEMMER_AVAILABLE:
            try:
                self.turkish_stemmer = TurkishStemmer()
                self.logger.info("Turkish stemmer loaded")
            except Exception as e:
                self.logger.warning(f"Failed to load Turkish stemmer: {e}")
    
    def _load_default_models(self):
        """Load default transformer models."""
        if not TRANSFORMERS_AVAILABLE:
            self.logger.warning("Transformers not available, skipping model loading")
            return
        
        # Default models for Turkish legal text
        default_models = {
            "turkish_bert": "dbmdz/bert-base-turkish-cased",
            "multilingual_bert": "bert-base-multilingual-cased",
            "distilbert": "distilbert-base-multilingual-cased"
        }
        
        for model_name, model_path in default_models.items():
            try:
                self.load_model(model_name, model_path)
            except Exception as e:
                self.logger.warning(f"Failed to load {model_name}: {e}")
    
    def load_model(self, model_name: str, model_path: str, model_type: ModelType = ModelType.BERT) -> bool:
        """Load a transformer model."""
        if not TRANSFORMERS_AVAILABLE:
            self.logger.error("Transformers library not available")
            return False
        
        try:
            self.logger.info(f"Loading model: {model_name} from {model_path}")
            
            # Load tokenizer
            if model_type == ModelType.DISTILBERT:
                tokenizer = DistilBertTokenizer.from_pretrained(model_path)
                model = DistilBertModel.from_pretrained(model_path)
            else:
                tokenizer = AutoTokenizer.from_pretrained(model_path)
                model = AutoModel.from_pretrained(model_path)
            
            # Store in cache
            self.tokenizers[model_name] = tokenizer
            self.models[model_name] = model
            
            self.logger.info(f"Successfully loaded {model_name}")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to load model {model_name}: {e}")
            return False
    
    def get_model_embeddings(self, texts: List[str], model_name: str = "turkish_bert") -> np.ndarray:
        """Get embeddings from a specific transformer model."""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not loaded")
        
        model = self.models[model_name]
        tokenizer = self.tokenizers[model_name]
        
        embeddings = []
        
        for text in texts:
            # Tokenize
            inputs = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=512
            )
            
            # Get embeddings
            with torch.no_grad():
                outputs = model(**inputs)
                # Use [CLS] token embedding or mean pooling
                if hasattr(outputs, 'last_hidden_state'):
                    # Mean pooling
                    embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
                else:
                    # [CLS] token
                    embedding = outputs.pooler_output.squeeze().numpy()
            
            embeddings.append(embedding)
        
        return np.array(embeddings)
    
    def analyze_turkish_text(self, text: str) -> Dict[str, Any]:
        """Analyze Turkish text using morphological analysis."""
        analysis = {
            "stems": [],
            "morphemes": [],
            "pos_tags": [],
            "features": {}
        }
        
        if self.turkish_analyzer:
            try:
                # Morphological analysis
                morphs = self.turkish_analyzer.analyze(text)
                
                for word_analysis in morphs:
                    if word_analysis:
                        for morph in word_analysis:
                            analysis["stems"].append(morph.lemma)
                            analysis["pos_tags"].append(morph.pos)
                            analysis["morphemes"].extend(morph.morphemes)
            
            except Exception as e:
                self.logger.warning(f"Turkish analysis failed: {e}")
        
        if self.turkish_stemmer:
            try:
                # Stemming
                words = text.split()
                stems = [self.turkish_stemmer.stem(word) for word in words]
                analysis["stemmed_words"] = stems
            
            except Exception as e:
                self.logger.warning(f"Turkish stemming failed: {e}")
        
        return analysis
    
    def get_available_models(self) -> List[str]:
        """Get list of available models."""
        return list(self.models.keys())
    
    def unload_model(self, model_name: str) -> bool:
        """Unload a model to free memory."""
        if model_name in self.models:
            del self.models[model_name]
            del self.tokenizers[model_name]
            self.logger.info(f"Unloaded model: {model_name}")
            return True
        return False


class ContentClassifier:
    """Legal content classifier using transformer models."""
    
    def __init__(self, config: Config, transformer_manager: TransformerManager):
        self.config = config
        self.transformer_manager = transformer_manager
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Legal patterns and keywords
        self.legal_patterns = self._initialize_legal_patterns()
        
        # Classification pipelines
        self.pipelines = {}
        self._initialize_pipelines()
    
    def _initialize_legal_patterns(self) -> Dict[str, Dict[str, List[str]]]:
        """Initialize Turkish legal patterns and keywords."""
        return {
            "content_types": {
                "definition": [
                    "tanım", "tanımı", "anlamı", "ifade eder", "demektir", 
                    "kastedilen", "kapsar", "dahildir", "şunlardır"
                ],
                "rule": [
                    "zorunlu", "mecburi", "gerekli", "şarttır", "lazımdır",
                    "yapılır", "uygulanır", "gerçekleştirilir", "sağlanır"
                ],
                "exception": [
                    "hariç", "istisna", "müstesna", "dışında", "saklı kalmak",
                    "ancak", "fakat", "lakin", "şu kadar ki", "bu kadarla"
                ],
                "sanction": [
                    "ceza", "para cezası", "hapis", "yaptırım", "müeyyide",
                    "disiplin", "ihtar", "uyarı", "kınama", "men"
                ],
                "procedure": [
                    "usul", "prosedür", "işlem", "süreç", "aşama",
                    "başvuru", "dilekçe", "form", "belge", "evrak"
                ],
                "reference": [
                    "madde", "fıkra", "bent", "kanun", "yönetmelik",
                    "tebliğ", "genelge", "karar", "hüküm", "atıf"
                ]
            },
            "importance_indicators": {
                "critical": [
                    "kesinlikle", "mutlaka", "zorunlu", "mecburi", "şart",
                    "yasak", "memnuniyet", "ceza", "yaptırım", "müeyyide"
                ],
                "high": [
                    "önemli", "gerekli", "lazım", "uygun", "münasip",
                    "dikkat", "özen", "titizlik", "hassasiyet"
                ],
                "medium": [
                    "tavsiye", "önerilir", "tercih", "uygun görülür",
                    "mümkün", "olabilir", "durumunda"
                ],
                "low": [
                    "isteğe bağlı", "seçmeli", "tercihen", "mümkün olduğunca",
                    "gerekirse", "lüzum halinde"
                ]
            },
            "legal_concepts": {
                "administrative": [
                    "idari", "bürokrasi", "memur", "kamu", "devlet",
                    "belediye", "valilik", "kaymakamlık", "müdürlük"
                ],
                "civil": [
                    "medeni", "özel", "şahıs", "kişi", "aile",
                    "miras", "mülkiyet", "sözleşme", "borç"
                ],
                "criminal": [
                    "ceza", "suç", "kabahat", "hapis", "para cezası",
                    "soruşturma", "kovuşturma", "mahkeme", "hâkim"
                ],
                "commercial": [
                    "ticari", "ticaret", "şirket", "ortaklık", "sermaye",
                    "kâr", "zarar", "bilanço", "vergi", "gümrük"
                ],
                "constitutional": [
                    "anayasa", "temel hak", "özgürlük", "eşitlik",
                    "cumhuriyet", "demokrasi", "hukuk devleti"
                ]
            }
        }
    
    def _initialize_pipelines(self):
        """Initialize classification pipelines."""
        if not TRANSFORMERS_AVAILABLE:
            return
        
        try:
            # Sentiment analysis pipeline for importance detection
            self.pipelines['sentiment'] = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-xlm-roberta-base-sentiment",
                return_all_scores=True
            )
        except Exception as e:
            self.logger.warning(f"Failed to initialize sentiment pipeline: {e}")
    
    def classify_content(self, text: str) -> ClassificationResult:
        """Classify legal content."""
        import time
        start_time = time.time()
        
        # Extract features
        features = self._extract_features(text)
        
        # Classify content type
        content_type = self._classify_content_type(text, features)
        
        # Determine importance level
        importance_level = self._classify_importance(text, features)
        
        # Extract legal concepts
        legal_concepts = self._extract_legal_concepts(text, features)
        
        # Calculate confidence scores
        confidence_scores = self._calculate_confidence_scores(text, features)
        
        return ClassificationResult(
            content_type=content_type,
            importance_level=importance_level,
            legal_concepts=legal_concepts,
            confidence_scores=confidence_scores,
            features=features,
            processing_time=time.time() - start_time,
            metadata={
                "text_length": len(text),
                "word_count": len(text.split()),
                "sentence_count": len([s for s in text.split('.') if s.strip()])
            }
        )
    
    def _extract_features(self, text: str) -> Dict[str, Any]:
        """Extract features from text."""
        features = {
            "length": len(text),
            "word_count": len(text.split()),
            "sentence_count": len([s for s in text.split('.') if s.strip()]),
            "has_numbers": any(char.isdigit() for char in text),
            "has_parentheses": '(' in text and ')' in text,
            "has_quotes": '"' in text or "'" in text,
            "uppercase_ratio": sum(1 for c in text if c.isupper()) / len(text) if text else 0
        }
        
        # Turkish morphological features
        if self.transformer_manager:
            turkish_analysis = self.transformer_manager.analyze_turkish_text(text)
            features.update(turkish_analysis)
        
        # Pattern matching features
        for category, patterns in self.legal_patterns.items():
            features[f"{category}_matches"] = {}
            for subcategory, keywords in patterns.items():
                matches = sum(1 for keyword in keywords if keyword.lower() in text.lower())
                features[f"{category}_matches"][subcategory] = matches
        
        return features
    
    def _classify_content_type(self, text: str, features: Dict[str, Any]) -> ContentType:
        """Classify content type based on patterns and features."""
        content_matches = features.get("content_types_matches", {})
        
        # Score each content type
        scores = {
            ContentType.DEFINITION: content_matches.get("definition", 0),
            ContentType.RULE: content_matches.get("rule", 0),
            ContentType.EXCEPTION: content_matches.get("exception", 0),
            ContentType.SANCTION: content_matches.get("sanction", 0),
            ContentType.PROCEDURE: content_matches.get("procedure", 0),
            ContentType.REFERENCE: content_matches.get("reference", 0)
        }
        
        # Additional heuristics
        text_lower = text.lower()
        
        # Definition indicators
        if any(indicator in text_lower for indicator in ["tanım", "anlamı", "ifade eder", "demektir"]):
            scores[ContentType.DEFINITION] += 2
        
        # Rule indicators
        if any(indicator in text_lower for indicator in ["zorunlu", "mecburi", "yapılır", "uygulanır"]):
            scores[ContentType.RULE] += 2
        
        # Exception indicators
        if any(indicator in text_lower for indicator in ["hariç", "istisna", "ancak", "fakat"]):
            scores[ContentType.EXCEPTION] += 2
        
        # Sanction indicators
        if any(indicator in text_lower for indicator in ["ceza", "yaptırım", "hapis", "para cezası"]):
            scores[ContentType.SANCTION] += 2
        
        # Find highest scoring type
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        
        return ContentType.OTHER
    
    def _classify_importance(self, text: str, features: Dict[str, Any]) -> ImportanceLevel:
        """Classify importance level."""
        importance_matches = features.get("importance_indicators_matches", {})
        
        # Score each importance level
        scores = {
            ImportanceLevel.CRITICAL: importance_matches.get("critical", 0),
            ImportanceLevel.HIGH: importance_matches.get("high", 0),
            ImportanceLevel.MEDIUM: importance_matches.get("medium", 0),
            ImportanceLevel.LOW: importance_matches.get("low", 0)
        }
        
        # Additional heuristics
        text_lower = text.lower()
        
        # Critical indicators
        if any(indicator in text_lower for indicator in ["yasak", "ceza", "zorunlu", "kesinlikle"]):
            scores[ImportanceLevel.CRITICAL] += 3
        
        # High importance indicators
        if any(indicator in text_lower for indicator in ["önemli", "gerekli", "dikkat", "özen"]):
            scores[ImportanceLevel.HIGH] += 2
        
        # Structural indicators
        if features.get("has_numbers", False):
            scores[ImportanceLevel.HIGH] += 1
        
        if features.get("uppercase_ratio", 0) > 0.1:
            scores[ImportanceLevel.HIGH] += 1
        
        # Find highest scoring level
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        
        return ImportanceLevel.MEDIUM
    
    def _extract_legal_concepts(self, text: str, features: Dict[str, Any]) -> List[LegalConcept]:
        """Extract legal concepts from text."""
        concepts = []
        concept_matches = features.get("legal_concepts_matches", {})
        
        # Check each concept category
        for category, count in concept_matches.items():
            if count > 0:
                # Create legal concept
                concept = LegalConcept(
                    term=category,
                    definition=f"Legal concept related to {category}",
                    category=category,
                    confidence=min(1.0, count / 5.0)  # Normalize confidence
                )
                concepts.append(concept)
        
        # Extract specific legal terms
        legal_terms = self._extract_legal_terms(text)
        for term, confidence in legal_terms.items():
            concept = LegalConcept(
                term=term,
                definition=f"Legal term: {term}",
                category="term",
                confidence=confidence
            )
            concepts.append(concept)
        
        return concepts
    
    def _extract_legal_terms(self, text: str) -> Dict[str, float]:
        """Extract specific legal terms with confidence scores."""
        terms = {}
        text_lower = text.lower()
        
        # Common Turkish legal terms
        legal_terms = [
            "madde", "fıkra", "bent", "kanun", "yönetmelik", "tebliğ",
            "mahkeme", "hâkim", "savcı", "avukat", "dava", "karar",
            "hüküm", "temyiz", "istinaf", "icra", "ihtiyati tedbir",
            "delil", "tanık", "bilirkişi", "keşif", "duruşma"
        ]
        
        for term in legal_terms:
            if term in text_lower:
                # Calculate confidence based on frequency and context
                frequency = text_lower.count(term)
                confidence = min(1.0, frequency / 3.0)
                terms[term] = confidence
        
        return terms
    
    def _calculate_confidence_scores(self, text: str, features: Dict[str, Any]) -> Dict[str, float]:
        """Calculate confidence scores for classifications."""
        scores = {
            "content_type": 0.0,
            "importance": 0.0,
            "legal_concepts": 0.0,
            "overall": 0.0
        }
        
        # Content type confidence
        content_matches = features.get("content_types_matches", {})
        if content_matches:
            max_matches = max(content_matches.values())
            scores["content_type"] = min(1.0, max_matches / 3.0)
        
        # Importance confidence
        importance_matches = features.get("importance_indicators_matches", {})
        if importance_matches:
            max_matches = max(importance_matches.values())
            scores["importance"] = min(1.0, max_matches / 2.0)
        
        # Legal concepts confidence
        concept_matches = features.get("legal_concepts_matches", {})
        if concept_matches:
            total_matches = sum(concept_matches.values())
            scores["legal_concepts"] = min(1.0, total_matches / 5.0)
        
        # Overall confidence
        scores["overall"] = np.mean(list(scores.values()))
        
        return scores
    
    def batch_classify(self, texts: List[str]) -> List[ClassificationResult]:
        """Classify multiple texts in batch."""
        results = []
        
        for text in texts:
            try:
                result = self.classify_content(text)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Failed to classify text: {e}")
                # Create default result
                results.append(ClassificationResult(
                    content_type=ContentType.OTHER,
                    importance_level=ImportanceLevel.MEDIUM,
                    legal_concepts=[],
                    confidence_scores={"overall": 0.0},
                    features={},
                    processing_time=0.0,
                    metadata={"error": str(e)}
                ))
        
        return results