"""Text processing utilities for SmartChunkLLM."""

import re
import string
import unicodedata
from typing import List, Optional, Dict, Set, Tuple
from collections import Counter
import math

try:
    import nltk
    from nltk.tokenize import sent_tokenize, word_tokenize
    from nltk.corpus import stopwords
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

try:
    from langdetect import detect, LangDetectError
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False

try:
    from zeyrek import MorphAnalyzer
    ZEYREK_AVAILABLE = True
except ImportError:
    ZEYREK_AVAILABLE = False

try:
    from turkish_stemmer import TurkishStemmer
    TURKISH_STEMMER_AVAILABLE = True
except ImportError:
    TURKISH_STEMMER_AVAILABLE = False


# Turkish stopwords
TURKISH_STOPWORDS = {
    'acaba', 'altı', 'altmış', 'ama', 'ancak', 'arada', 'artık', 'asla', 'aslında',
    'ayrıca', 'bana', 'bazen', 'bazı', 'bazıları', 'belki', 'ben', 'benden', 'beni',
    'benim', 'ber', 'beş', 'bile', 'bin', 'bir', 'birçok', 'biri', 'birkaç', 'birkez',
    'birşey', 'birşeyi', 'biz', 'bizden', 'bizi', 'bizim', 'böyle', 'böylece', 'bu',
    'buna', 'bunda', 'bundan', 'bunlar', 'bunları', 'bunların', 'bunu', 'bunun',
    'burada', 'çok', 'çünkü', 'da', 'daha', 'dahi', 'dan', 'de', 'defa', 'değil',
    'diğer', 'diye', 'dokuz', 'dolayı', 'dört', 'elbette', 'en', 'fakat', 'falan',
    'felan', 'gibi', 'göre', 'hala', 'halde', 'halen', 'hangi', 'hani', 'hatta',
    'hem', 'henüz', 'hep', 'hepsi', 'her', 'herhangi', 'hiç', 'hiçbir', 'için',
    'iki', 'ile', 'ise', 'işte', 'itibaren', 'kaç', 'kadar', 'karşı', 'kendi',
    'kendine', 'kendini', 'kendisi', 'kendisine', 'kendisini', 'kez', 'ki', 'kim',
    'kime', 'kimi', 'kimin', 'kimse', 'madem', 'nasıl', 'ne', 'neden', 'nedenle',
    'nerde', 'nerede', 'nereye', 'niye', 'niçin', 'o', 'olan', 'olarak', 'oldu',
    'olduğu', 'olduğunu', 'olduklarını', 'olmadı', 'olmadığı', 'olmak', 'olması',
    'olmayan', 'olmaz', 'olsa', 'olsun', 'olup', 'olur', 'olursa', 'oluyor', 'on',
    'ona', 'ondan', 'onlar', 'onları', 'onların', 'onu', 'onun', 'orada', 'oysa',
    'öyle', 'pek', 'rağmen', 'sana', 'sekiz', 'sen', 'senden', 'seni', 'senin',
    'siz', 'sizden', 'sizi', 'sizin', 'şey', 'şeyden', 'şeyi', 'şeyler', 'şu',
    'şuna', 'şunda', 'şundan', 'şunlar', 'şunları', 'şunların', 'şunu', 'şunun',
    'şurada', 'tarafından', 'tüm', 'tümü', 'üç', 'üzere', 've', 'veya', 'ya',
    'yani', 'yapacak', 'yapılan', 'yapılır', 'yapıyor', 'yapmak', 'yaptı',
    'yaptığı', 'yaptığını', 'yaptıkları', 'yedi', 'yerine', 'yine', 'yirmi',
    'yoksa', 'yüz', 'zaten', 'zira'
}

# Common Turkish legal terms
TURKISH_LEGAL_TERMS = {
    'kanun', 'madde', 'fıkra', 'bent', 'yönetmelik', 'tüzük', 'genelge', 'tebliğ',
    'karar', 'hüküm', 'ceza', 'yaptırım', 'sorumluluk', 'yükümlülük', 'hak',
    'yetki', 'görev', 'usul', 'esas', 'ilke', 'kural', 'norm', 'düzenleme',
    'mevzuat', 'hukuk', 'adalet', 'mahkeme', 'yargı', 'dava', 'davacı', 'davalı',
    'tanık', 'bilirkişi', 'avukat', 'savcı', 'hakim', 'icra', 'infaz', 'temyiz',
    'istinaf', 'karar', 'hüküm', 'itiraz', 'şikayet', 'suç', 'suçlu', 'mağdur',
    'zarar', 'tazminat', 'para', 'ceza', 'hapis', 'adli', 'para', 'cezası'
}


def clean_text(text: str, remove_extra_whitespace: bool = True, 
               remove_special_chars: bool = False, 
               preserve_legal_formatting: bool = True) -> str:
    """Clean and normalize text.
    
    Args:
        text: Input text to clean
        remove_extra_whitespace: Remove extra whitespace
        remove_special_chars: Remove special characters
        preserve_legal_formatting: Preserve legal document formatting
    
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove control characters but preserve newlines and tabs
    text = ''.join(char for char in text if unicodedata.category(char)[0] != 'C' or char in '\n\t')
    
    # Preserve legal formatting patterns
    if preserve_legal_formatting:
        # Preserve article numbers, paragraph markers, etc.
        legal_patterns = [
            r'(?:Madde|MADDE)\s+\d+',
            r'(?:Fıkra|FIKRA)\s+\d+',
            r'(?:Bent|BENT)\s+[a-zA-Z]',
            r'(?:Bölüm|BÖLÜM)\s+(?:\d+|[IVX]+)',
            r'(?:Kısım|KISIM)\s+(?:\d+|[IVX]+)'
        ]
        
        # Mark legal patterns for preservation
        preserved_patterns = {}
        for i, pattern in enumerate(legal_patterns):
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                placeholder = f"__LEGAL_PATTERN_{i}_{len(preserved_patterns)}__"
                preserved_patterns[placeholder] = match.group()
                text = text.replace(match.group(), placeholder)
    
    # Remove extra whitespace
    if remove_extra_whitespace:
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Preserve paragraph breaks
    
    # Remove special characters (but preserve Turkish characters)
    if remove_special_chars:
        # Keep Turkish characters and basic punctuation
        allowed_chars = string.ascii_letters + string.digits + 'çğıöşüÇĞIİÖŞÜ.,;:!?()[]{}"\'-\n\t '
        text = ''.join(char for char in text if char in allowed_chars)
    
    # Restore preserved legal patterns
    if preserve_legal_formatting and 'preserved_patterns' in locals():
        for placeholder, original in preserved_patterns.items():
            text = text.replace(placeholder, original)
    
    return text.strip()


def normalize_text(text: str, lowercase: bool = False, 
                  remove_diacritics: bool = False) -> str:
    """Normalize text for processing.
    
    Args:
        text: Input text
        lowercase: Convert to lowercase
        remove_diacritics: Remove diacritical marks
    
    Returns:
        Normalized text
    """
    if not text:
        return ""
    
    # Unicode normalization
    text = unicodedata.normalize('NFKC', text)
    
    if remove_diacritics:
        # Remove diacritics but preserve Turkish characters
        text = ''.join(
            char for char in unicodedata.normalize('NFD', text)
            if unicodedata.category(char) != 'Mn' or char in 'çğıöşüÇĞIİÖŞÜ'
        )
    
    if lowercase:
        # Turkish-aware lowercase conversion
        text = text.replace('I', 'ı').replace('İ', 'i')
        text = text.lower()
    
    return text


def extract_sentences(text: str, language: str = 'turkish') -> List[str]:
    """Extract sentences from text.
    
    Args:
        text: Input text
        language: Language for sentence tokenization
    
    Returns:
        List of sentences
    """
    if not text:
        return []
    
    if NLTK_AVAILABLE:
        try:
            # Download required NLTK data if not present
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                nltk.download('punkt', quiet=True)
            
            sentences = sent_tokenize(text, language=language)
            return [s.strip() for s in sentences if s.strip()]
        except Exception:
            pass
    
    # Fallback: simple sentence splitting
    sentences = re.split(r'[.!?]+\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def count_tokens(text: str, method: str = 'whitespace') -> int:
    """Count tokens in text.
    
    Args:
        text: Input text
        method: Tokenization method ('whitespace', 'nltk', 'approximate')
    
    Returns:
        Number of tokens
    """
    if not text:
        return 0
    
    if method == 'nltk' and NLTK_AVAILABLE:
        try:
            tokens = word_tokenize(text)
            return len(tokens)
        except Exception:
            pass
    
    if method == 'approximate':
        # Approximate token count (useful for LLM token estimation)
        # Roughly 1 token per 4 characters for Turkish
        return max(1, len(text) // 4)
    
    # Default: whitespace tokenization
    return len(text.split())


def split_into_tokens(text: str, method: str = 'whitespace') -> List[str]:
    """Split text into tokens.
    
    Args:
        text: Input text
        method: Tokenization method
    
    Returns:
        List of tokens
    """
    if not text:
        return []
    
    if method == 'nltk' and NLTK_AVAILABLE:
        try:
            return word_tokenize(text)
        except Exception:
            pass
    
    # Default: whitespace tokenization with punctuation handling
    tokens = re.findall(r'\b\w+\b|[.,;:!?]', text)
    return [token for token in tokens if token.strip()]


def detect_language(text: str) -> Optional[str]:
    """Detect language of text.
    
    Args:
        text: Input text
    
    Returns:
        Language code or None
    """
    if not text or len(text.strip()) < 10:
        return None
    
    if LANGDETECT_AVAILABLE:
        try:
            return detect(text)
        except LangDetectError:
            pass
    
    # Fallback: simple Turkish detection
    if is_turkish_text(text):
        return 'tr'
    
    return None


def is_turkish_text(text: str, threshold: float = 0.1) -> bool:
    """Check if text is likely Turkish.
    
    Args:
        text: Input text
        threshold: Minimum ratio of Turkish characters
    
    Returns:
        True if text is likely Turkish
    """
    if not text:
        return False
    
    # Count Turkish-specific characters
    turkish_chars = 'çğıöşüÇĞIİÖŞÜ'
    turkish_char_count = sum(1 for char in text if char in turkish_chars)
    
    # Count Turkish words
    words = text.lower().split()
    turkish_word_count = sum(1 for word in words if word in TURKISH_LEGAL_TERMS or word in TURKISH_STOPWORDS)
    
    # Calculate ratios
    char_ratio = turkish_char_count / len(text) if text else 0
    word_ratio = turkish_word_count / len(words) if words else 0
    
    return char_ratio >= threshold or word_ratio >= threshold


def remove_stopwords(text: str, language: str = 'turkish', 
                    custom_stopwords: Optional[Set[str]] = None) -> str:
    """Remove stopwords from text.
    
    Args:
        text: Input text
        language: Language for stopwords
        custom_stopwords: Additional stopwords to remove
    
    Returns:
        Text with stopwords removed
    """
    if not text:
        return ""
    
    # Get stopwords
    stop_words = set()
    
    if language == 'turkish':
        stop_words.update(TURKISH_STOPWORDS)
    elif NLTK_AVAILABLE:
        try:
            try:
                nltk.data.find('corpora/stopwords')
            except LookupError:
                nltk.download('stopwords', quiet=True)
            
            stop_words.update(stopwords.words(language))
        except Exception:
            pass
    
    if custom_stopwords:
        stop_words.update(custom_stopwords)
    
    # Remove stopwords
    words = text.split()
    filtered_words = [word for word in words if word.lower() not in stop_words]
    
    return ' '.join(filtered_words)


def stem_text(text: str, language: str = 'turkish') -> str:
    """Stem words in text.
    
    Args:
        text: Input text
        language: Language for stemming
    
    Returns:
        Text with stemmed words
    """
    if not text:
        return ""
    
    if language == 'turkish' and TURKISH_STEMMER_AVAILABLE:
        try:
            stemmer = TurkishStemmer()
            words = text.split()
            stemmed_words = [stemmer.stem(word) for word in words]
            return ' '.join(stemmed_words)
        except Exception:
            pass
    
    # Fallback: return original text
    return text


def calculate_text_similarity(text1: str, text2: str, method: str = 'jaccard') -> float:
    """Calculate similarity between two texts.
    
    Args:
        text1: First text
        text2: Second text
        method: Similarity method ('jaccard', 'cosine', 'overlap')
    
    Returns:
        Similarity score (0-1)
    """
    if not text1 or not text2:
        return 0.0
    
    # Tokenize and normalize
    tokens1 = set(normalize_text(text1, lowercase=True).split())
    tokens2 = set(normalize_text(text2, lowercase=True).split())
    
    if method == 'jaccard':
        intersection = len(tokens1.intersection(tokens2))
        union = len(tokens1.union(tokens2))
        return intersection / union if union > 0 else 0.0
    
    elif method == 'overlap':
        intersection = len(tokens1.intersection(tokens2))
        min_size = min(len(tokens1), len(tokens2))
        return intersection / min_size if min_size > 0 else 0.0
    
    elif method == 'cosine':
        # Simple cosine similarity based on word counts
        all_tokens = tokens1.union(tokens2)
        vector1 = [1 if token in tokens1 else 0 for token in all_tokens]
        vector2 = [1 if token in tokens2 else 0 for token in all_tokens]
        
        dot_product = sum(a * b for a, b in zip(vector1, vector2))
        magnitude1 = math.sqrt(sum(a * a for a in vector1))
        magnitude2 = math.sqrt(sum(b * b for b in vector2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    return 0.0


def extract_keywords(text: str, max_keywords: int = 10, 
                    min_word_length: int = 3) -> List[Tuple[str, float]]:
    """Extract keywords from text.
    
    Args:
        text: Input text
        max_keywords: Maximum number of keywords
        min_word_length: Minimum word length
    
    Returns:
        List of (keyword, score) tuples
    """
    if not text:
        return []
    
    # Clean and tokenize
    cleaned_text = normalize_text(text, lowercase=True)
    words = re.findall(r'\b\w+\b', cleaned_text)
    
    # Filter words
    filtered_words = [
        word for word in words 
        if len(word) >= min_word_length and 
        word not in TURKISH_STOPWORDS and
        not word.isdigit()
    ]
    
    if not filtered_words:
        return []
    
    # Calculate word frequencies
    word_counts = Counter(filtered_words)
    total_words = len(filtered_words)
    
    # Calculate TF scores
    tf_scores = {word: count / total_words for word, count in word_counts.items()}
    
    # Boost legal terms
    for word in tf_scores:
        if word in TURKISH_LEGAL_TERMS:
            tf_scores[word] *= 1.5
    
    # Sort by score and return top keywords
    sorted_keywords = sorted(tf_scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_keywords[:max_keywords]


class TextProcessor:
    """Text processing utility class."""
    
    def __init__(self, language: str = 'turkish', 
                 preserve_legal_formatting: bool = True):
        self.language = language
        self.preserve_legal_formatting = preserve_legal_formatting
        self._setup_language_tools()
    
    def _setup_language_tools(self):
        """Setup language-specific tools."""
        self.stemmer = None
        self.analyzer = None
        
        if self.language == 'turkish':
            if TURKISH_STEMMER_AVAILABLE:
                try:
                    self.stemmer = TurkishStemmer()
                except Exception:
                    pass
            
            if ZEYREK_AVAILABLE:
                try:
                    self.analyzer = MorphAnalyzer()
                except Exception:
                    pass
    
    def process(self, text: str, 
                clean: bool = True,
                normalize: bool = True,
                remove_stopwords: bool = False,
                stem: bool = False) -> str:
        """Process text with specified operations.
        
        Args:
            text: Input text
            clean: Clean text
            normalize: Normalize text
            remove_stopwords: Remove stopwords
            stem: Stem words
        
        Returns:
            Processed text
        """
        if not text:
            return ""
        
        result = text
        
        if clean:
            result = clean_text(result, preserve_legal_formatting=self.preserve_legal_formatting)
        
        if normalize:
            result = normalize_text(result)
        
        if remove_stopwords:
            result = remove_stopwords(result, language=self.language)
        
        if stem and self.stemmer:
            result = stem_text(result, language=self.language)
        
        return result
    
    def detect_language(self, text: str) -> str:
        """Detect language of text.
        
        Args:
            text: Input text
            
        Returns:
            Detected language code
        """
        return detect_language(text)
    
    def is_turkish_text(self, text: str) -> bool:
        """Check if text is Turkish.
        
        Args:
            text: Input text
            
        Returns:
            True if text is Turkish
        """
        return is_turkish_text(text)
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text.
        
        Args:
            text: Input text
            
        Returns:
            Number of tokens
        """
        return count_tokens(text)
    
    def extract_sentences(self, text: str) -> List[str]:
        """Extract sentences from text.
        
        Args:
            text: Input text
            
        Returns:
            List of sentences
        """
        return extract_sentences(text, self.language)
    
    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[Tuple[str, float]]:
        """Extract keywords from text.
        
        Args:
            text: Input text
            max_keywords: Maximum number of keywords
            
        Returns:
            List of (keyword, score) tuples
        """
        return extract_keywords(text, max_keywords)
    
    def extract_features(self, text: str) -> Dict[str, any]:
        """Extract text features.
        
        Args:
            text: Input text
        
        Returns:
            Dictionary of text features
        """
        if not text:
            return {}
        
        features = {
            'length': len(text),
            'word_count': len(text.split()),
            'sentence_count': len(extract_sentences(text, self.language)),
            'token_count': count_tokens(text),
            'avg_word_length': sum(len(word) for word in text.split()) / len(text.split()) if text.split() else 0,
            'language': detect_language(text),
            'is_turkish': is_turkish_text(text),
            'keywords': extract_keywords(text, max_keywords=5)
        }
        
        # Legal document features
        if self.preserve_legal_formatting:
            features.update({
                'has_articles': bool(re.search(r'(?:Madde|MADDE)\s+\d+', text)),
                'has_paragraphs': bool(re.search(r'(?:Fıkra|FIKRA)\s+\d+', text)),
                'has_clauses': bool(re.search(r'(?:Bent|BENT)\s+[a-zA-Z]', text)),
                'legal_term_count': sum(1 for word in text.lower().split() if word in TURKISH_LEGAL_TERMS)
            })
        
        return features
    
    def split_into_chunks(self, text: str, chunk_size: int = 512, 
                         overlap: int = 50, method: str = 'sentence') -> List[str]:
        """Split text into chunks.
        
        Args:
            text: Input text
            chunk_size: Target chunk size in tokens
            overlap: Overlap between chunks in tokens
            method: Chunking method ('sentence', 'word', 'character')
        
        Returns:
            List of text chunks
        """
        if not text:
            return []
        
        if method == 'sentence':
            sentences = extract_sentences(text, self.language)
            chunks = []
            current_chunk = []
            current_size = 0
            
            for sentence in sentences:
                sentence_size = count_tokens(sentence)
                
                if current_size + sentence_size > chunk_size and current_chunk:
                    chunks.append(' '.join(current_chunk))
                    
                    # Handle overlap
                    if overlap > 0 and len(current_chunk) > 1:
                        overlap_sentences = []
                        overlap_size = 0
                        for sent in reversed(current_chunk):
                            sent_size = count_tokens(sent)
                            if overlap_size + sent_size <= overlap:
                                overlap_sentences.insert(0, sent)
                                overlap_size += sent_size
                            else:
                                break
                        current_chunk = overlap_sentences
                        current_size = overlap_size
                    else:
                        current_chunk = []
                        current_size = 0
                
                current_chunk.append(sentence)
                current_size += sentence_size
            
            if current_chunk:
                chunks.append(' '.join(current_chunk))
            
            return chunks
        
        elif method == 'word':
            words = text.split()
            chunks = []
            
            for i in range(0, len(words), chunk_size - overlap):
                chunk_words = words[i:i + chunk_size]
                if chunk_words:
                    chunks.append(' '.join(chunk_words))
            
            return chunks
        
        else:  # character method
            chunks = []
            
            for i in range(0, len(text), chunk_size - overlap):
                chunk = text[i:i + chunk_size]
                if chunk.strip():
                    chunks.append(chunk)
            
            return chunks