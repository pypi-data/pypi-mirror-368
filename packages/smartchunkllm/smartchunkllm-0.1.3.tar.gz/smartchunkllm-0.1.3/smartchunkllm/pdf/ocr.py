"""OCR processing for PDF documents."""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class OCREngine(Enum):
    """Supported OCR engines."""
    TESSERACT = "tesseract"
    EASYOCR = "easyocr"
    PADDLEOCR = "paddleocr"
    AZURE = "azure"
    GOOGLE = "google"


@dataclass
class OCRResult:
    """Result of OCR processing."""
    text: str
    confidence: float
    bbox: Optional[Tuple[float, float, float, float]] = None
    page_number: int = 0
    language: str = "tr"
    processing_time: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class OCRWord:
    """Individual word from OCR."""
    text: str
    confidence: float
    bbox: Tuple[float, float, float, float]
    

@dataclass
class OCRLine:
    """Line of text from OCR."""
    text: str
    words: List[OCRWord]
    confidence: float
    bbox: Tuple[float, float, float, float]


@dataclass
class OCRBlock:
    """Block of text from OCR."""
    text: str
    lines: List[OCRLine]
    confidence: float
    bbox: Tuple[float, float, float, float]


class OCRProcessor:
    """Processes images and PDFs using OCR."""
    
    def __init__(self, 
                 engine: OCREngine = OCREngine.TESSERACT,
                 languages: List[str] = None,
                 config: Optional[Dict[str, Any]] = None):
        """Initialize OCR processor.
        
        Args:
            engine: OCR engine to use
            languages: List of languages to detect (default: ['tr', 'en'])
            config: Additional configuration
        """
        self.engine = engine
        self.languages = languages or ['tr', 'en']
        self.config = config or {}
        
        # Default configuration
        self.min_confidence = self.config.get('min_confidence', 0.5)
        self.preprocess_image = self.config.get('preprocess_image', True)
        
        # Initialize engine
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize the OCR engine."""
        try:
            if self.engine == OCREngine.TESSERACT:
                self._init_tesseract()
            elif self.engine == OCREngine.EASYOCR:
                self._init_easyocr()
            elif self.engine == OCREngine.PADDLEOCR:
                self._init_paddleocr()
            else:
                logger.warning(f"OCR engine {self.engine} not implemented, using mock")
                self._init_mock()
        except Exception as e:
            logger.warning(f"Failed to initialize {self.engine}: {e}. Using mock OCR.")
            self._init_mock()
    
    def _init_tesseract(self):
        """Initialize Tesseract OCR."""
        try:
            import pytesseract
            from PIL import Image
            self.tesseract = pytesseract
            self.pil_image = Image
            logger.info("Tesseract OCR initialized")
        except ImportError:
            logger.warning("pytesseract not available, using mock OCR")
            self._init_mock()
    
    def _init_easyocr(self):
        """Initialize EasyOCR."""
        try:
            import easyocr
            self.reader = easyocr.Reader(self.languages)
            logger.info("EasyOCR initialized")
        except ImportError:
            logger.warning("easyocr not available, using mock OCR")
            self._init_mock()
    
    def _init_paddleocr(self):
        """Initialize PaddleOCR."""
        try:
            from paddleocr import PaddleOCR
            self.paddle_ocr = PaddleOCR(use_angle_cls=True, lang='tr')
            logger.info("PaddleOCR initialized")
        except ImportError:
            logger.warning("paddleocr not available, using mock OCR")
            self._init_mock()
    
    def _init_mock(self):
        """Initialize mock OCR for testing."""
        self.engine = "mock"
        logger.info("Mock OCR initialized")
    
    def process_image(self, image_data: Any, page_number: int = 0) -> OCRResult:
        """Process image with OCR.
        
        Args:
            image_data: Image data (PIL Image, numpy array, or file path)
            page_number: Page number for reference
            
        Returns:
            OCRResult with extracted text
        """
        try:
            if self.engine == OCREngine.TESSERACT:
                return self._process_with_tesseract(image_data, page_number)
            elif self.engine == OCREngine.EASYOCR:
                return self._process_with_easyocr(image_data, page_number)
            elif self.engine == OCREngine.PADDLEOCR:
                return self._process_with_paddleocr(image_data, page_number)
            else:
                return self._process_with_mock(image_data, page_number)
        except Exception as e:
            logger.error(f"OCR processing failed: {e}")
            return OCRResult(
                text="",
                confidence=0.0,
                page_number=page_number,
                metadata={'error': str(e)}
            )
    
    def _process_with_tesseract(self, image_data: Any, page_number: int) -> OCRResult:
        """Process with Tesseract OCR."""
        try:
            # Configure Tesseract
            lang_string = '+'.join(self.languages)
            config = '--oem 3 --psm 6'
            
            # Extract text
            text = self.tesseract.image_to_string(
                image_data, 
                lang=lang_string, 
                config=config
            )
            
            # Get confidence (approximate)
            data = self.tesseract.image_to_data(
                image_data, 
                lang=lang_string, 
                config=config,
                output_type=self.tesseract.Output.DICT
            )
            
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return OCRResult(
                text=text.strip(),
                confidence=avg_confidence / 100.0,
                page_number=page_number,
                language=self.languages[0],
                metadata={'engine': 'tesseract'}
            )
            
        except Exception as e:
            logger.error(f"Tesseract OCR failed: {e}")
            return self._process_with_mock(image_data, page_number)
    
    def _process_with_easyocr(self, image_data: Any, page_number: int) -> OCRResult:
        """Process with EasyOCR."""
        try:
            results = self.reader.readtext(image_data)
            
            text_parts = []
            confidences = []
            
            for (bbox, text, confidence) in results:
                if confidence >= self.min_confidence:
                    text_parts.append(text)
                    confidences.append(confidence)
            
            full_text = ' '.join(text_parts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return OCRResult(
                text=full_text,
                confidence=avg_confidence,
                page_number=page_number,
                language=self.languages[0],
                metadata={'engine': 'easyocr', 'detections': len(results)}
            )
            
        except Exception as e:
            logger.error(f"EasyOCR failed: {e}")
            return self._process_with_mock(image_data, page_number)
    
    def _process_with_paddleocr(self, image_data: Any, page_number: int) -> OCRResult:
        """Process with PaddleOCR."""
        try:
            results = self.paddle_ocr.ocr(image_data, cls=True)
            
            text_parts = []
            confidences = []
            
            for line in results:
                for word_info in line:
                    text = word_info[1][0]
                    confidence = word_info[1][1]
                    
                    if confidence >= self.min_confidence:
                        text_parts.append(text)
                        confidences.append(confidence)
            
            full_text = ' '.join(text_parts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return OCRResult(
                text=full_text,
                confidence=avg_confidence,
                page_number=page_number,
                language=self.languages[0],
                metadata={'engine': 'paddleocr'}
            )
            
        except Exception as e:
            logger.error(f"PaddleOCR failed: {e}")
            return self._process_with_mock(image_data, page_number)
    
    def _process_with_mock(self, image_data: Any, page_number: int) -> OCRResult:
        """Mock OCR processing for testing."""
        return OCRResult(
            text=f"Mock OCR text for page {page_number}",
            confidence=0.8,
            page_number=page_number,
            language="tr",
            metadata={'engine': 'mock'}
        )
    
    def process_pdf_page(self, page_data: Dict[str, Any]) -> OCRResult:
        """Process a PDF page with OCR.
        
        Args:
            page_data: Page data containing image or text information
            
        Returns:
            OCRResult with extracted text
        """
        page_number = page_data.get('page_number', 0)
        
        # If page already has text, return it
        if 'text' in page_data and page_data['text'].strip():
            return OCRResult(
                text=page_data['text'],
                confidence=1.0,
                page_number=page_number,
                language="tr",
                metadata={'source': 'existing_text'}
            )
        
        # If page has image data, process with OCR
        if 'image' in page_data:
            return self.process_image(page_data['image'], page_number)
        
        # No processable data
        return OCRResult(
            text="",
            confidence=0.0,
            page_number=page_number,
            metadata={'error': 'No processable data'}
        )
    
    def process_document(self, pages_data: List[Dict[str, Any]]) -> List[OCRResult]:
        """Process entire document with OCR.
        
        Args:
            pages_data: List of page data dictionaries
            
        Returns:
            List of OCRResult for each page
        """
        results = []
        
        for page_data in pages_data:
            result = self.process_pdf_page(page_data)
            results.append(result)
        
        return results
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages."""
        if self.engine == OCREngine.TESSERACT:
            try:
                return self.tesseract.get_languages()
            except:
                return ['tr', 'en']
        elif self.engine == OCREngine.EASYOCR:
            # EasyOCR supported languages
            return ['tr', 'en', 'de', 'fr', 'es', 'it', 'pt', 'ru', 'ar', 'zh']
        elif self.engine == OCREngine.PADDLEOCR:
            return ['tr', 'en', 'ch', 'de', 'fr', 'ja', 'ko']
        else:
            return ['tr', 'en']
    
    def set_languages(self, languages: List[str]):
        """Set OCR languages.
        
        Args:
            languages: List of language codes
        """
        self.languages = languages
        
        # Reinitialize if needed
        if self.engine == OCREngine.EASYOCR:
            try:
                import easyocr
                self.reader = easyocr.Reader(self.languages)
            except ImportError:
                pass