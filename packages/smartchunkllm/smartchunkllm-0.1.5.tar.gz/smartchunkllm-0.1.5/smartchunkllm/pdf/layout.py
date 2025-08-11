"""Layout analysis for PDF documents."""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class LayoutElementType(Enum):
    """Types of layout elements."""
    TEXT = "text"
    TITLE = "title"
    HEADER = "header"
    FOOTER = "footer"
    TABLE = "table"
    IMAGE = "image"
    LIST = "list"
    PARAGRAPH = "paragraph"
    COLUMN = "column"
    SECTION = "section"


@dataclass
class BoundingBox:
    """Bounding box coordinates."""
    x0: float
    y0: float
    x1: float
    y1: float
    
    @property
    def width(self) -> float:
        return self.x1 - self.x0
    
    @property
    def height(self) -> float:
        return self.y1 - self.y0
    
    @property
    def area(self) -> float:
        return self.width * self.height
    
    @property
    def center(self) -> Tuple[float, float]:
        return ((self.x0 + self.x1) / 2, (self.y0 + self.y1) / 2)


@dataclass
class LayoutElement:
    """A layout element in a PDF page."""
    element_type: LayoutElementType
    bbox: BoundingBox
    text: str = ""
    confidence: float = 1.0
    page_number: int = 0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class LayoutAnalysisResult:
    """Result of layout analysis."""
    elements: List[LayoutElement]
    page_number: int
    page_width: float
    page_height: float
    confidence: float = 1.0
    processing_time: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def get_elements_by_type(self, element_type: LayoutElementType) -> List[LayoutElement]:
        """Get elements by type."""
        return [elem for elem in self.elements if elem.element_type == element_type]
    
    def get_text_elements(self) -> List[LayoutElement]:
        """Get all text elements."""
        text_types = {LayoutElementType.TEXT, LayoutElementType.TITLE, 
                     LayoutElementType.HEADER, LayoutElementType.FOOTER, 
                     LayoutElementType.PARAGRAPH}
        return [elem for elem in self.elements if elem.element_type in text_types]


class LayoutAnalyzer:
    """Analyzes PDF layout to detect structure."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize layout analyzer.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.min_text_height = self.config.get('min_text_height', 8)
        self.min_element_area = self.config.get('min_element_area', 100)
        
    def analyze_page(self, page_data: Dict[str, Any]) -> LayoutAnalysisResult:
        """Analyze layout of a single page.
        
        Args:
            page_data: Page data containing text and layout information
            
        Returns:
            LayoutAnalysisResult with detected elements
        """
        try:
            elements = []
            page_number = page_data.get('page_number', 0)
            page_width = page_data.get('width', 612)
            page_height = page_data.get('height', 792)
            
            # Extract text elements
            if 'chars' in page_data:
                text_elements = self._extract_text_elements(page_data['chars'])
                elements.extend(text_elements)
            
            # Extract other elements (tables, images, etc.)
            if 'objects' in page_data:
                other_elements = self._extract_other_elements(page_data['objects'])
                elements.extend(other_elements)
            
            return LayoutAnalysisResult(
                elements=elements,
                page_number=page_number,
                page_width=page_width,
                page_height=page_height,
                confidence=0.8
            )
            
        except Exception as e:
            logger.error(f"Layout analysis failed for page {page_number}: {e}")
            return LayoutAnalysisResult(
                elements=[],
                page_number=page_number,
                page_width=612,
                page_height=792,
                confidence=0.0
            )
    
    def _extract_text_elements(self, chars: List[Dict[str, Any]]) -> List[LayoutElement]:
        """Extract text elements from character data."""
        elements = []
        
        # Group characters into text blocks
        text_blocks = self._group_chars_into_blocks(chars)
        
        for block in text_blocks:
            if len(block['text'].strip()) < 2:
                continue
                
            bbox = BoundingBox(
                x0=block['x0'],
                y0=block['y0'],
                x1=block['x1'],
                y1=block['y1']
            )
            
            # Determine element type based on characteristics
            element_type = self._classify_text_element(block)
            
            element = LayoutElement(
                element_type=element_type,
                bbox=bbox,
                text=block['text'],
                confidence=0.9,
                metadata={
                    'font_size': block.get('size', 12),
                    'font_name': block.get('fontname', 'unknown')
                }
            )
            
            elements.append(element)
        
        return elements
    
    def _extract_other_elements(self, objects: List[Dict[str, Any]]) -> List[LayoutElement]:
        """Extract non-text elements."""
        elements = []
        
        for obj in objects:
            obj_type = obj.get('object_type', 'unknown')
            
            if obj_type in ['image', 'figure']:
                element_type = LayoutElementType.IMAGE
            elif obj_type == 'table':
                element_type = LayoutElementType.TABLE
            else:
                continue
            
            bbox = BoundingBox(
                x0=obj.get('x0', 0),
                y0=obj.get('y0', 0),
                x1=obj.get('x1', 0),
                y1=obj.get('y1', 0)
            )
            
            element = LayoutElement(
                element_type=element_type,
                bbox=bbox,
                text="",
                confidence=0.8,
                metadata={'object_type': obj_type}
            )
            
            elements.append(element)
        
        return elements
    
    def _group_chars_into_blocks(self, chars: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Group characters into text blocks."""
        if not chars:
            return []
        
        # Sort characters by position
        sorted_chars = sorted(chars, key=lambda c: (c.get('y0', 0), c.get('x0', 0)))
        
        blocks = []
        current_block = {
            'text': '',
            'x0': float('inf'),
            'y0': float('inf'),
            'x1': float('-inf'),
            'y1': float('-inf'),
            'size': 0,
            'fontname': ''
        }
        
        for char in sorted_chars:
            text = char.get('text', '')
            if not text.strip():
                continue
            
            # Update block bounds
            current_block['x0'] = min(current_block['x0'], char.get('x0', 0))
            current_block['y0'] = min(current_block['y0'], char.get('y0', 0))
            current_block['x1'] = max(current_block['x1'], char.get('x1', 0))
            current_block['y1'] = max(current_block['y1'], char.get('y1', 0))
            
            current_block['text'] += text
            current_block['size'] = char.get('size', 12)
            current_block['fontname'] = char.get('fontname', 'unknown')
        
        if current_block['text'].strip():
            blocks.append(current_block)
        
        return blocks
    
    def _classify_text_element(self, block: Dict[str, Any]) -> LayoutElementType:
        """Classify text element type based on characteristics."""
        text = block['text'].strip()
        font_size = block.get('size', 12)
        
        # Simple heuristics for classification
        if font_size > 16:
            return LayoutElementType.TITLE
        elif len(text) < 50 and text.isupper():
            return LayoutElementType.HEADER
        elif text.startswith(('•', '-', '*', '1.', '2.', '3.')):
            return LayoutElementType.LIST
        else:
            return LayoutElementType.PARAGRAPH
    
    def analyze_document(self, pages_data: List[Dict[str, Any]]) -> List[LayoutAnalysisResult]:
        """Analyze layout of entire document.
        
        Args:
            pages_data: List of page data dictionaries
            
        Returns:
            List of LayoutAnalysisResult for each page
        """
        results = []
        
        for page_data in pages_data:
            result = self.analyze_page(page_data)
            results.append(result)
        
        return results