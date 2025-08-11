"""PDF structure analysis and extraction."""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple, Union
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class StructureType(Enum):
    """Types of document structures."""
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    LIST = "list"
    TABLE = "table"
    FIGURE = "figure"
    CAPTION = "caption"
    FOOTER = "footer"
    HEADER = "header"
    SIDEBAR = "sidebar"
    QUOTE = "quote"
    CODE = "code"
    FORMULA = "formula"
    UNKNOWN = "unknown"


@dataclass
class StructureElement:
    """A structural element in a document."""
    element_type: StructureType
    text: str
    bbox: Optional[Tuple[float, float, float, float]] = None
    page_number: int = 0
    confidence: float = 1.0
    level: int = 0  # For hierarchical elements like headings
    attributes: Dict[str, Any] = None
    children: List['StructureElement'] = None
    
    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {}
        if self.children is None:
            self.children = []


@dataclass
class DocumentStructure:
    """Complete document structure."""
    elements: List[StructureElement]
    metadata: Dict[str, Any] = None
    page_count: int = 0
    processing_time: float = 0.0
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def get_headings(self) -> List[StructureElement]:
        """Get all heading elements."""
        return [elem for elem in self.elements if elem.element_type == StructureType.HEADING]
    
    def get_paragraphs(self) -> List[StructureElement]:
        """Get all paragraph elements."""
        return [elem for elem in self.elements if elem.element_type == StructureType.PARAGRAPH]
    
    def get_tables(self) -> List[StructureElement]:
        """Get all table elements."""
        return [elem for elem in self.elements if elem.element_type == StructureType.TABLE]
    
    def get_by_page(self, page_number: int) -> List[StructureElement]:
        """Get elements from a specific page."""
        return [elem for elem in self.elements if elem.page_number == page_number]
    
    def get_text_content(self) -> str:
        """Get all text content as a single string."""
        return '\n'.join([elem.text for elem in self.elements if elem.text.strip()])


class StructureAnalyzer:
    """Analyzes document structure from extracted content."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize structure analyzer.
        
        Args:
            config: Configuration options
        """
        self.config = config or {}
        
        # Configuration options
        self.min_heading_font_size = self.config.get('min_heading_font_size', 12)
        self.heading_font_threshold = self.config.get('heading_font_threshold', 1.2)
        self.min_paragraph_length = self.config.get('min_paragraph_length', 10)
        self.table_detection_enabled = self.config.get('table_detection', True)
        self.list_detection_enabled = self.config.get('list_detection', True)
        
        logger.info("Structure analyzer initialized")
    
    def analyze_document(self, pages_data: List[Dict[str, Any]]) -> DocumentStructure:
        """Analyze document structure from pages data.
        
        Args:
            pages_data: List of page data dictionaries
            
        Returns:
            DocumentStructure with analyzed elements
        """
        elements = []
        
        for page_data in pages_data:
            page_elements = self.analyze_page(page_data)
            elements.extend(page_elements)
        
        # Post-process elements
        elements = self._post_process_elements(elements)
        
        return DocumentStructure(
            elements=elements,
            page_count=len(pages_data),
            metadata={
                'analyzer': 'structure_analyzer',
                'total_elements': len(elements),
                'element_types': self._count_element_types(elements)
            }
        )
    
    def analyze_page(self, page_data: Dict[str, Any]) -> List[StructureElement]:
        """Analyze structure of a single page.
        
        Args:
            page_data: Page data dictionary
            
        Returns:
            List of StructureElement for the page
        """
        elements = []
        page_number = page_data.get('page_number', 0)
        
        # Extract text blocks
        text_blocks = self._extract_text_blocks(page_data)
        
        for block in text_blocks:
            element = self._classify_text_block(block, page_number)
            if element:
                elements.append(element)
        
        # Extract tables if enabled
        if self.table_detection_enabled:
            tables = self._extract_tables(page_data, page_number)
            elements.extend(tables)
        
        # Extract figures
        figures = self._extract_figures(page_data, page_number)
        elements.extend(figures)
        
        return elements
    
    def _extract_text_blocks(self, page_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract text blocks from page data."""
        blocks = []
        
        # If we have structured text data
        if 'text_blocks' in page_data:
            return page_data['text_blocks']
        
        # If we have simple text, create a single block
        if 'text' in page_data and page_data['text'].strip():
            blocks.append({
                'text': page_data['text'],
                'bbox': page_data.get('bbox'),
                'font_size': page_data.get('font_size', 12),
                'font_name': page_data.get('font_name', 'default')
            })
        
        # If we have OCR results
        if 'ocr_results' in page_data:
            for result in page_data['ocr_results']:
                if result.get('text', '').strip():
                    blocks.append({
                        'text': result['text'],
                        'bbox': result.get('bbox'),
                        'confidence': result.get('confidence', 1.0)
                    })
        
        return blocks
    
    def _classify_text_block(self, block: Dict[str, Any], page_number: int) -> Optional[StructureElement]:
        """Classify a text block into a structure element."""
        text = block.get('text', '').strip()
        if not text:
            return None
        
        bbox = block.get('bbox')
        font_size = block.get('font_size', 12)
        font_name = block.get('font_name', 'default')
        confidence = block.get('confidence', 1.0)
        
        # Determine element type
        element_type = self._determine_element_type(text, font_size, font_name, bbox)
        
        # Determine heading level if it's a heading
        level = 0
        if element_type == StructureType.HEADING:
            level = self._determine_heading_level(font_size, font_name)
        
        return StructureElement(
            element_type=element_type,
            text=text,
            bbox=bbox,
            page_number=page_number,
            confidence=confidence,
            level=level,
            attributes={
                'font_size': font_size,
                'font_name': font_name
            }
        )
    
    def _determine_element_type(self, text: str, font_size: float, font_name: str, bbox: Optional[Tuple]) -> StructureType:
        """Determine the type of a text element."""
        # Check for heading patterns
        if self._is_heading(text, font_size, font_name):
            return StructureType.HEADING
        
        # Check for list items
        if self.list_detection_enabled and self._is_list_item(text):
            return StructureType.LIST
        
        # Check for quotes
        if self._is_quote(text):
            return StructureType.QUOTE
        
        # Check for code blocks
        if self._is_code(text, font_name):
            return StructureType.CODE
        
        # Check for formulas
        if self._is_formula(text):
            return StructureType.FORMULA
        
        # Check for captions
        if self._is_caption(text):
            return StructureType.CAPTION
        
        # Check for headers/footers based on position
        if bbox and self._is_header_footer(bbox):
            return StructureType.HEADER if bbox[1] > 700 else StructureType.FOOTER
        
        # Default to paragraph if long enough
        if len(text) >= self.min_paragraph_length:
            return StructureType.PARAGRAPH
        
        return StructureType.UNKNOWN
    
    def _is_heading(self, text: str, font_size: float, font_name: str) -> bool:
        """Check if text is a heading."""
        # Font size based detection
        if font_size >= self.min_heading_font_size * self.heading_font_threshold:
            return True
        
        # Font weight based detection
        if 'bold' in font_name.lower() or 'heavy' in font_name.lower():
            return True
        
        # Pattern based detection
        heading_patterns = [
            r'^\d+\.\s+[A-ZÜĞŞÇÖI]',  # "1. Başlık"
            r'^[A-ZÜĞŞÇÖI][A-ZÜĞŞÇÖIa-züğşçöı\s]{2,50}$',  # All caps or title case
            r'^(BÖLÜM|CHAPTER|SECTION)\s+\d+',  # Chapter/section markers
        ]
        
        import re
        for pattern in heading_patterns:
            if re.match(pattern, text.strip()):
                return True
        
        # Short text that's not a sentence
        if len(text) < 100 and not text.endswith('.') and not text.endswith('!'):
            if text.isupper() or text.istitle():
                return True
        
        return False
    
    def _is_list_item(self, text: str) -> bool:
        """Check if text is a list item."""
        import re
        list_patterns = [
            r'^[•·▪▫◦‣⁃]\s+',  # Bullet points
            r'^\d+[.):]\s+',   # Numbered lists
            r'^[a-zA-Z][.):]\s+',  # Lettered lists
            r'^[-*+]\s+',      # Dash/asterisk lists
        ]
        
        for pattern in list_patterns:
            if re.match(pattern, text.strip()):
                return True
        
        return False
    
    def _is_quote(self, text: str) -> bool:
        """Check if text is a quote."""
        stripped = text.strip()
        return (
            (stripped.startswith('"') and stripped.endswith('"')) or
            (stripped.startswith('"') and stripped.endswith('"')) or
            (stripped.startswith('„') and stripped.endswith('"'))
        )
    
    def _is_code(self, text: str, font_name: str) -> bool:
        """Check if text is code."""
        # Font-based detection
        mono_fonts = ['courier', 'consolas', 'monaco', 'menlo', 'monospace']
        if any(font in font_name.lower() for font in mono_fonts):
            return True
        
        # Pattern-based detection
        import re
        code_patterns = [
            r'^\s*def\s+\w+\(',  # Python function
            r'^\s*class\s+\w+',  # Python class
            r'^\s*import\s+\w+', # Python import
            r'^\s*#include\s*<', # C include
            r'^\s*function\s+\w+\(', # JavaScript function
        ]
        
        for pattern in code_patterns:
            if re.match(pattern, text):
                return True
        
        return False
    
    def _is_formula(self, text: str) -> bool:
        """Check if text is a mathematical formula."""
        import re
        formula_patterns = [
            r'\$.*\$',  # LaTeX inline math
            r'\\\[.*\\\]',  # LaTeX display math
            r'[∑∏∫∂∇±×÷≤≥≠≈∞]',  # Math symbols
            r'[α-ωΑ-Ω]',  # Greek letters
        ]
        
        for pattern in formula_patterns:
            if re.search(pattern, text):
                return True
        
        return False
    
    def _is_caption(self, text: str) -> bool:
        """Check if text is a caption."""
        import re
        caption_patterns = [
            r'^(Figure|Fig|Table|Tablo|Şekil)\s*\d+[:.:]',
            r'^(Resim|Grafik|Çizelge)\s*\d+[:.:]',
        ]
        
        for pattern in caption_patterns:
            if re.match(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def _is_header_footer(self, bbox: Tuple[float, float, float, float]) -> bool:
        """Check if element is in header or footer area."""
        _, y1, _, y2 = bbox
        
        # Assuming page height of ~800 points
        # Header: top 50 points, Footer: bottom 50 points
        return y1 > 750 or y2 < 50
    
    def _determine_heading_level(self, font_size: float, font_name: str) -> int:
        """Determine heading level (1-6)."""
        # Simple font size based leveling
        if font_size >= 20:
            return 1
        elif font_size >= 18:
            return 2
        elif font_size >= 16:
            return 3
        elif font_size >= 14:
            return 4
        elif font_size >= 12:
            return 5
        else:
            return 6
    
    def _extract_tables(self, page_data: Dict[str, Any], page_number: int) -> List[StructureElement]:
        """Extract table elements from page data."""
        tables = []
        
        # If we have table data
        if 'tables' in page_data:
            for i, table_data in enumerate(page_data['tables']):
                table_text = self._format_table_text(table_data)
                
                tables.append(StructureElement(
                    element_type=StructureType.TABLE,
                    text=table_text,
                    bbox=table_data.get('bbox'),
                    page_number=page_number,
                    confidence=table_data.get('confidence', 1.0),
                    attributes={
                        'table_id': i,
                        'rows': table_data.get('rows', 0),
                        'cols': table_data.get('cols', 0)
                    }
                ))
        
        return tables
    
    def _format_table_text(self, table_data: Dict[str, Any]) -> str:
        """Format table data as text."""
        if 'cells' in table_data:
            # Format as tab-separated values
            rows = []
            for row in table_data['cells']:
                row_text = '\t'.join([str(cell) for cell in row])
                rows.append(row_text)
            return '\n'.join(rows)
        
        return table_data.get('text', 'Table content')
    
    def _extract_figures(self, page_data: Dict[str, Any], page_number: int) -> List[StructureElement]:
        """Extract figure elements from page data."""
        figures = []
        
        # If we have figure data
        if 'figures' in page_data:
            for i, figure_data in enumerate(page_data['figures']):
                figures.append(StructureElement(
                    element_type=StructureType.FIGURE,
                    text=figure_data.get('caption', f'Figure {i+1}'),
                    bbox=figure_data.get('bbox'),
                    page_number=page_number,
                    confidence=figure_data.get('confidence', 1.0),
                    attributes={
                        'figure_id': i,
                        'image_path': figure_data.get('image_path'),
                        'width': figure_data.get('width'),
                        'height': figure_data.get('height')
                    }
                ))
        
        return figures
    
    def _post_process_elements(self, elements: List[StructureElement]) -> List[StructureElement]:
        """Post-process elements to improve structure."""
        # Sort by page and position
        elements.sort(key=lambda x: (x.page_number, x.bbox[1] if x.bbox else 0))
        
        # Merge consecutive similar elements
        merged_elements = self._merge_similar_elements(elements)
        
        # Build hierarchy for headings
        hierarchical_elements = self._build_heading_hierarchy(merged_elements)
        
        return hierarchical_elements
    
    def _merge_similar_elements(self, elements: List[StructureElement]) -> List[StructureElement]:
        """Merge consecutive similar elements."""
        if not elements:
            return elements
        
        merged = [elements[0]]
        
        for current in elements[1:]:
            previous = merged[-1]
            
            # Merge consecutive paragraphs on the same page
            if (current.element_type == StructureType.PARAGRAPH and
                previous.element_type == StructureType.PARAGRAPH and
                current.page_number == previous.page_number):
                
                previous.text += '\n' + current.text
                if current.bbox and previous.bbox:
                    # Expand bounding box
                    previous.bbox = (
                        min(previous.bbox[0], current.bbox[0]),
                        min(previous.bbox[1], current.bbox[1]),
                        max(previous.bbox[2], current.bbox[2]),
                        max(previous.bbox[3], current.bbox[3])
                    )
            else:
                merged.append(current)
        
        return merged
    
    def _build_heading_hierarchy(self, elements: List[StructureElement]) -> List[StructureElement]:
        """Build hierarchical structure for headings."""
        # For now, just return elements as-is
        # In a more sophisticated implementation, we would build a tree structure
        return elements
    
    def _count_element_types(self, elements: List[StructureElement]) -> Dict[str, int]:
        """Count elements by type."""
        counts = {}
        for element in elements:
            element_type = element.element_type.value
            counts[element_type] = counts.get(element_type, 0) + 1
        return counts
    
    def extract_outline(self, structure: DocumentStructure) -> List[Dict[str, Any]]:
        """Extract document outline from headings."""
        outline = []
        headings = structure.get_headings()
        
        for heading in headings:
            outline.append({
                'title': heading.text,
                'level': heading.level,
                'page': heading.page_number,
                'bbox': heading.bbox
            })
        
        return outline
    
    def get_reading_order(self, structure: DocumentStructure) -> List[StructureElement]:
        """Get elements in reading order."""
        # Sort by page, then by vertical position (top to bottom)
        reading_order = sorted(
            structure.elements,
            key=lambda x: (x.page_number, -(x.bbox[1] if x.bbox else 0))
        )
        
        return reading_order


class StructureDetector:
    """Detects and analyzes document structure."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize structure detector.
        
        Args:
            config: Configuration options
        """
        self.config = config or {}
        self.analyzer = StructureAnalyzer(config)
        
        logger.info("Structure detector initialized")
    
    def detect_structure(self, pages_data: List[Dict[str, Any]]) -> DocumentStructure:
        """Detect document structure from pages data.
        
        Args:
            pages_data: List of page data dictionaries
            
        Returns:
            DocumentStructure with detected elements
        """
        return self.analyzer.analyze_document(pages_data)
    
    def detect_page_structure(self, page_data: Dict[str, Any]) -> List[StructureElement]:
        """Detect structure of a single page.
        
        Args:
            page_data: Page data dictionary
            
        Returns:
            List of StructureElement for the page
        """
        return self.analyzer.analyze_page(page_data)
    
    def extract_headings(self, pages_data: List[Dict[str, Any]]) -> List[StructureElement]:
        """Extract headings from document.
        
        Args:
            pages_data: List of page data dictionaries
            
        Returns:
            List of heading elements
        """
        structure = self.detect_structure(pages_data)
        return structure.get_headings()
    
    def extract_paragraphs(self, pages_data: List[Dict[str, Any]]) -> List[StructureElement]:
        """Extract paragraphs from document.
        
        Args:
            pages_data: List of page data dictionaries
            
        Returns:
            List of paragraph elements
        """
        structure = self.detect_structure(pages_data)
        return structure.get_paragraphs()
    
    def extract_tables(self, pages_data: List[Dict[str, Any]]) -> List[StructureElement]:
        """Extract tables from document.
        
        Args:
            pages_data: List of page data dictionaries
            
        Returns:
            List of table elements
        """
        structure = self.detect_structure(pages_data)
        return structure.get_tables()
    
    def get_document_outline(self, pages_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get document outline from headings.
        
        Args:
            pages_data: List of page data dictionaries
            
        Returns:
            List of outline items
        """
        structure = self.detect_structure(pages_data)
        return self.analyzer.extract_outline(structure)
    
    def get_reading_order(self, pages_data: List[Dict[str, Any]]) -> List[StructureElement]:
        """Get elements in reading order.
        
        Args:
            pages_data: List of page data dictionaries
            
        Returns:
            List of elements in reading order
        """
        structure = self.detect_structure(pages_data)
        return self.analyzer.get_reading_order(structure)