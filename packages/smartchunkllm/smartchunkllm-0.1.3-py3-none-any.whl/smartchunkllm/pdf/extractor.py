"""PDF text extraction with multiple backends."""

from typing import Dict, List, Optional, Any, Tuple, Union
from pathlib import Path
import logging
from dataclasses import dataclass
from abc import ABC, abstractmethod

# PDF processing libraries
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    logging.warning("PyMuPDF not available")

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    logging.warning("pdfplumber not available")

try:
    from pdfminer.high_level import extract_text, extract_pages
    from pdfminer.layout import LTTextContainer, LTTextBox, LTTextLine, LTChar
    PDFMINER_AVAILABLE = True
except ImportError:
    PDFMINER_AVAILABLE = False
    logging.warning("pdfminer not available")

try:
    import layoutparser as lp
    LAYOUTPARSER_AVAILABLE = True
except ImportError:
    LAYOUTPARSER_AVAILABLE = False
    logging.warning("layoutparser not available")

from ..core.config import PDFProcessingConfig


@dataclass
class TextBlock:
    """Represents a block of text with metadata."""
    text: str
    page_number: int
    bbox: Tuple[float, float, float, float]  # x0, y0, x1, y1
    font_info: Dict[str, Any]
    block_type: str = "text"
    confidence: float = 1.0
    
    @property
    def width(self) -> float:
        return self.bbox[2] - self.bbox[0]
    
    @property
    def height(self) -> float:
        return self.bbox[3] - self.bbox[1]
    
    @property
    def area(self) -> float:
        return self.width * self.height


@dataclass
class PDFPage:
    """Represents a PDF page with extracted content."""
    page_number: int
    text_blocks: List[TextBlock]
    images: List[Dict[str, Any]]
    tables: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    
    @property
    def full_text(self) -> str:
        """Get all text from the page."""
        return "\n".join([block.text for block in self.text_blocks])


class PDFExtractorBase(ABC):
    """Base class for PDF extractors."""
    
    def __init__(self, config: PDFProcessingConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def extract_pages(self, pdf_path: Union[str, Path]) -> List[PDFPage]:
        """Extract pages from PDF."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the extractor is available."""
        pass


class PyMuPDFExtractor(PDFExtractorBase):
    """PDF extractor using PyMuPDF (fitz)."""
    
    def is_available(self) -> bool:
        return PYMUPDF_AVAILABLE
    
    def extract_pages(self, pdf_path: Union[str, Path]) -> List[PDFPage]:
        """Extract pages using PyMuPDF."""
        if not self.is_available():
            raise RuntimeError("PyMuPDF is not available")
        
        pages = []
        doc = fitz.open(str(pdf_path))
        
        try:
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Extract text blocks
                text_blocks = self._extract_text_blocks(page, page_num)
                
                # Extract images
                images = self._extract_images(page) if self.config.extract_images else []
                
                # Extract tables (basic detection)
                tables = self._extract_tables(page)
                
                # Page metadata
                metadata = {
                    "width": page.rect.width,
                    "height": page.rect.height,
                    "rotation": page.rotation
                }
                
                pages.append(PDFPage(
                    page_number=page_num + 1,
                    text_blocks=text_blocks,
                    images=images,
                    tables=tables,
                    metadata=metadata
                ))
        
        finally:
            doc.close()
        
        return pages
    
    def _extract_text_blocks(self, page, page_num: int) -> List[TextBlock]:
        """Extract text blocks with font information."""
        blocks = []
        
        # Get text with detailed information
        text_dict = page.get_text("dict")
        
        for block in text_dict["blocks"]:
            if "lines" not in block:  # Skip image blocks
                continue
            
            for line in block["lines"]:
                line_text = ""
                font_info = {}
                bbox = line["bbox"]
                
                for span in line["spans"]:
                    line_text += span["text"]
                    
                    # Collect font information
                    if not font_info:  # Use first span's font info
                        font_info = {
                            "font": span.get("font", ""),
                            "size": span.get("size", 0),
                            "flags": span.get("flags", 0),
                            "color": span.get("color", 0)
                        }
                
                if line_text.strip() and len(line_text.strip()) >= self.config.min_text_length:
                    blocks.append(TextBlock(
                        text=line_text.strip(),
                        page_number=page_num + 1,
                        bbox=bbox,
                        font_info=font_info,
                        block_type="text"
                    ))
        
        return blocks
    
    def _extract_images(self, page) -> List[Dict[str, Any]]:
        """Extract image information."""
        images = []
        image_list = page.get_images()
        
        for img_index, img in enumerate(image_list):
            try:
                # Get image bbox
                img_rect = page.get_image_bbox(img)
                
                images.append({
                    "index": img_index,
                    "bbox": tuple(img_rect),
                    "width": img_rect.width,
                    "height": img_rect.height,
                    "ext": img[8] if len(img) > 8 else "unknown"
                })
            except Exception as e:
                self.logger.warning(f"Failed to extract image {img_index}: {e}")
        
        return images
    
    def _extract_tables(self, page) -> List[Dict[str, Any]]:
        """Basic table detection using PyMuPDF."""
        tables = []
        
        try:
            # Find tables using PyMuPDF's table detection
            tabs = page.find_tables()
            
            for tab_index, tab in enumerate(tabs):
                table_data = {
                    "index": tab_index,
                    "bbox": tuple(tab.bbox),
                    "rows": tab.row_count,
                    "cols": tab.col_count
                }
                
                # Extract table content if possible
                try:
                    table_content = tab.extract()
                    table_data["content"] = table_content
                except Exception as e:
                    self.logger.warning(f"Failed to extract table content: {e}")
                
                tables.append(table_data)
        
        except Exception as e:
            self.logger.warning(f"Table detection failed: {e}")
        
        return tables


class PDFPlumberExtractor(PDFExtractorBase):
    """PDF extractor using pdfplumber."""
    
    def is_available(self) -> bool:
        return PDFPLUMBER_AVAILABLE
    
    def extract_pages(self, pdf_path: Union[str, Path]) -> List[PDFPage]:
        """Extract pages using pdfplumber."""
        if not self.is_available():
            raise RuntimeError("pdfplumber is not available")
        
        pages = []
        
        with pdfplumber.open(str(pdf_path)) as pdf:
            for page_num, page in enumerate(pdf.pages):
                # Extract text with character-level information
                text_blocks = self._extract_text_blocks(page, page_num)
                
                # Extract images
                images = self._extract_images(page) if self.config.extract_images else []
                
                # Extract tables
                tables = self._extract_tables(page)
                
                # Page metadata
                metadata = {
                    "width": page.width,
                    "height": page.height,
                    "rotation": getattr(page, 'rotation', 0)
                }
                
                pages.append(PDFPage(
                    page_number=page_num + 1,
                    text_blocks=text_blocks,
                    images=images,
                    tables=tables,
                    metadata=metadata
                ))
        
        return pages
    
    def _extract_text_blocks(self, page, page_num: int) -> List[TextBlock]:
        """Extract text blocks using pdfplumber."""
        blocks = []
        
        # Get characters with detailed information
        chars = page.chars
        
        if not chars:
            return blocks
        
        # Group characters into lines
        lines = self._group_chars_into_lines(chars)
        
        for line_chars in lines:
            if not line_chars:
                continue
            
            # Combine text
            text = "".join([char["text"] for char in line_chars])
            
            if len(text.strip()) < self.config.min_text_length:
                continue
            
            # Calculate bounding box
            x0 = min([char["x0"] for char in line_chars])
            y0 = min([char["top"] for char in line_chars])
            x1 = max([char["x1"] for char in line_chars])
            y1 = max([char["bottom"] for char in line_chars])
            
            # Get font information from first character
            first_char = line_chars[0]
            font_info = {
                "fontname": first_char.get("fontname", ""),
                "size": first_char.get("size", 0),
                "adv": first_char.get("adv", 0)
            }
            
            blocks.append(TextBlock(
                text=text.strip(),
                page_number=page_num + 1,
                bbox=(x0, y0, x1, y1),
                font_info=font_info,
                block_type="text"
            ))
        
        return blocks
    
    def _group_chars_into_lines(self, chars: List[Dict]) -> List[List[Dict]]:
        """Group characters into lines based on vertical position."""
        if not chars:
            return []
        
        # Sort characters by vertical position, then horizontal
        sorted_chars = sorted(chars, key=lambda c: (c["top"], c["x0"]))
        
        lines = []
        current_line = [sorted_chars[0]]
        current_top = sorted_chars[0]["top"]
        
        for char in sorted_chars[1:]:
            # If character is on roughly the same line (within tolerance)
            if abs(char["top"] - current_top) < 3:
                current_line.append(char)
            else:
                # Start new line
                if current_line:
                    lines.append(current_line)
                current_line = [char]
                current_top = char["top"]
        
        # Add last line
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def _extract_images(self, page) -> List[Dict[str, Any]]:
        """Extract image information using pdfplumber."""
        images = []
        
        try:
            page_images = page.images
            
            for img_index, img in enumerate(page_images):
                images.append({
                    "index": img_index,
                    "bbox": (img["x0"], img["top"], img["x1"], img["bottom"]),
                    "width": img["width"],
                    "height": img["height"],
                    "object_type": img.get("object_type", "image")
                })
        
        except Exception as e:
            self.logger.warning(f"Failed to extract images: {e}")
        
        return images
    
    def _extract_tables(self, page) -> List[Dict[str, Any]]:
        """Extract tables using pdfplumber."""
        tables = []
        
        try:
            detected_tables = page.find_tables()
            
            for tab_index, table in enumerate(detected_tables):
                table_data = {
                    "index": tab_index,
                    "bbox": table.bbox,
                    "rows": len(table.rows) if table.rows else 0,
                    "cols": len(table.rows[0]) if table.rows and table.rows[0] else 0
                }
                
                # Extract table content
                try:
                    content = table.extract()
                    table_data["content"] = content
                except Exception as e:
                    self.logger.warning(f"Failed to extract table content: {e}")
                
                tables.append(table_data)
        
        except Exception as e:
            self.logger.warning(f"Table detection failed: {e}")
        
        return tables


class PDFMinerExtractor(PDFExtractorBase):
    """PDF extractor using pdfminer."""
    
    def is_available(self) -> bool:
        return PDFMINER_AVAILABLE
    
    def extract_pages(self, pdf_path: Union[str, Path]) -> List[PDFPage]:
        """Extract pages using pdfminer."""
        if not self.is_available():
            raise RuntimeError("pdfminer is not available")
        
        pages = []
        
        for page_num, page_layout in enumerate(extract_pages(str(pdf_path))):
            text_blocks = self._extract_text_blocks(page_layout, page_num)
            
            # Basic metadata
            metadata = {
                "width": page_layout.width,
                "height": page_layout.height,
                "rotation": getattr(page_layout, 'rotate', 0)
            }
            
            pages.append(PDFPage(
                page_number=page_num + 1,
                text_blocks=text_blocks,
                images=[],  # pdfminer doesn't easily extract images
                tables=[],  # Basic version doesn't detect tables
                metadata=metadata
            ))
        
        return pages
    
    def _extract_text_blocks(self, page_layout, page_num: int) -> List[TextBlock]:
        """Extract text blocks using pdfminer."""
        blocks = []
        
        def extract_text_from_element(element):
            if isinstance(element, LTTextContainer):
                for child in element:
                    yield from extract_text_from_element(child)
            elif isinstance(element, LTTextLine):
                text = element.get_text().strip()
                if len(text) >= self.config.min_text_length:
                    
                    # Get font information from first character
                    font_info = {}
                    for char in element:
                        if isinstance(char, LTChar):
                            font_info = {
                                "fontname": char.fontname,
                                "size": char.height,
                                "width": char.width
                            }
                            break
                    
                    blocks.append(TextBlock(
                        text=text,
                        page_number=page_num + 1,
                        bbox=(element.x0, element.y0, element.x1, element.y1),
                        font_info=font_info,
                        block_type="text"
                    ))
        
        # Extract text from all elements
        list(extract_text_from_element(page_layout))
        
        return blocks


class PDFExtractor:
    """Main PDF extractor with multiple backend support."""
    
    def __init__(self, config: PDFProcessingConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize available extractors
        self.extractors = {
            "pymupdf": PyMuPDFExtractor(config),
            "pdfplumber": PDFPlumberExtractor(config),
            "pdfminer": PDFMinerExtractor(config)
        }
        
        # Determine best available extractor
        self.primary_extractor = self._get_best_extractor()
        
        if not self.primary_extractor:
            raise RuntimeError("No PDF extraction libraries are available")
        
        self.logger.info(f"Using {self.primary_extractor} as primary PDF extractor")
    
    def _get_best_extractor(self) -> Optional[str]:
        """Get the best available extractor."""
        # Priority order: PyMuPDF > pdfplumber > pdfminer
        priority = ["pymupdf", "pdfplumber", "pdfminer"]
        
        for extractor_name in priority:
            if self.extractors[extractor_name].is_available():
                return extractor_name
        
        return None
    
    def extract_pdf(self, pdf_path: Union[str, Path]) -> List[PDFPage]:
        """Extract content from PDF using the best available method."""
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        self.logger.info(f"Extracting PDF: {pdf_path}")
        
        try:
            # Try primary extractor
            extractor = self.extractors[self.primary_extractor]
            pages = extractor.extract_pages(pdf_path)
            
            self.logger.info(f"Successfully extracted {len(pages)} pages using {self.primary_extractor}")
            return pages
        
        except Exception as e:
            self.logger.error(f"Primary extractor {self.primary_extractor} failed: {e}")
            
            # Try fallback extractors
            for extractor_name, extractor in self.extractors.items():
                if extractor_name == self.primary_extractor:
                    continue
                
                if not extractor.is_available():
                    continue
                
                try:
                    self.logger.info(f"Trying fallback extractor: {extractor_name}")
                    pages = extractor.extract_pages(pdf_path)
                    
                    self.logger.info(f"Successfully extracted {len(pages)} pages using {extractor_name}")
                    return pages
                
                except Exception as fallback_error:
                    self.logger.error(f"Fallback extractor {extractor_name} failed: {fallback_error}")
            
            raise RuntimeError(f"All PDF extractors failed for {pdf_path}")
    
    def get_available_extractors(self) -> List[str]:
        """Get list of available extractors."""
        return [name for name, extractor in self.extractors.items() if extractor.is_available()]
    
    def extract_text_only(self, pdf_path: Union[str, Path]) -> str:
        """Extract only text content from PDF."""
        pages = self.extract_pdf(pdf_path)
        return "\n\n".join([page.full_text for page in pages])