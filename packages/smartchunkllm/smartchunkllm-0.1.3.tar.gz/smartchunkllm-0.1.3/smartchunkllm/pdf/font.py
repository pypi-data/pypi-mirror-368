"""Font analysis for hierarchical structure detection in legal documents."""

from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from collections import defaultdict, Counter
import logging
import re
from enum import Enum

from .extractor import TextBlock, PDFPage


class HierarchyLevel(Enum):
    """Hierarchy levels in legal documents."""
    TITLE = "title"  # Ana başlık
    CHAPTER = "chapter"  # Bölüm
    SECTION = "section"  # Kısım
    ARTICLE = "article"  # Madde
    PARAGRAPH = "paragraph"  # Fıkra
    CLAUSE = "clause"  # Bent
    SUBCLAUSE = "subclause"  # Alt bent
    BODY_TEXT = "body_text"  # Gövde metni
    FOOTNOTE = "footnote"  # Dipnot
    HEADER = "header"  # Sayfa başlığı
    FOOTER = "footer"  # Sayfa altlığı


@dataclass
class FontCharacteristics:
    """Font characteristics for analysis."""
    name: str = ""
    size: float = 0.0
    is_bold: bool = False
    is_italic: bool = False
    is_underlined: bool = False
    color: int = 0
    
    def __hash__(self):
        return hash((self.name, self.size, self.is_bold, self.is_italic, self.is_underlined))
    
    def __eq__(self, other):
        if not isinstance(other, FontCharacteristics):
            return False
        return (self.name == other.name and 
                abs(self.size - other.size) < 0.1 and
                self.is_bold == other.is_bold and
                self.is_italic == other.is_italic and
                self.is_underlined == other.is_underlined)
    
    @property
    def style_key(self) -> str:
        """Get a unique style key for grouping."""
        style_parts = []
        if self.is_bold:
            style_parts.append("bold")
        if self.is_italic:
            style_parts.append("italic")
        if self.is_underlined:
            style_parts.append("underlined")
        
        style = "_".join(style_parts) if style_parts else "normal"
        return f"{self.name}_{self.size:.1f}_{style}"


@dataclass
class FontCluster:
    """Represents a cluster of similar fonts."""
    characteristics: FontCharacteristics
    text_blocks: List[TextBlock] = field(default_factory=list)
    frequency: int = 0
    hierarchy_level: Optional[HierarchyLevel] = None
    confidence: float = 0.0
    
    @property
    def total_text_length(self) -> int:
        return sum(len(block.text) for block in self.text_blocks)
    
    @property
    def average_text_length(self) -> float:
        return self.total_text_length / len(self.text_blocks) if self.text_blocks else 0


class FontAnalyzer:
    """Analyzes font characteristics to detect document hierarchy."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Turkish legal document patterns
        self.legal_patterns = {
            HierarchyLevel.TITLE: [
                r'^[A-ZÜĞŞÇÖI\s]+$',  # All caps titles
                r'^(KANUN|YÖNETMELIK|TÜZÜK|GENELGE)',  # Legal document types
            ],
            HierarchyLevel.CHAPTER: [
                r'^(BİRİNCİ|İKİNCİ|ÜÇÜNCÜ|DÖRDÜNCÜ|BEŞİNCİ|ALTINCI|YEDİNCİ|SEKİZİNCİ|DOKUZUNCU|ONUNCU)\s+(BÖLÜM|KISIM)',
                r'^BÖLÜM\s+[IVXLCDM]+',  # Roman numerals
                r'^\d+\.\s*BÖLÜM',
            ],
            HierarchyLevel.SECTION: [
                r'^\d+\.\s*(KISIM|BÖLÜM)',
                r'^[A-Z]\)\s*',  # A) B) C) sections
            ],
            HierarchyLevel.ARTICLE: [
                r'^MADDE\s+\d+',
                r'^Madde\s+\d+',
                r'^\d+\s*[-–—]',  # Article with dash
            ],
            HierarchyLevel.PARAGRAPH: [
                r'^\(\d+\)',  # (1) (2) (3)
                r'^\d+\)',   # 1) 2) 3)
            ],
            HierarchyLevel.CLAUSE: [
                r'^[a-z]\)',  # a) b) c)
                r'^[a-z]\.',  # a. b. c.
            ],
        }
    
    def analyze_fonts(self, pages: List[PDFPage]) -> Dict[str, Any]:
        """Analyze font characteristics across all pages."""
        self.logger.info("Starting font analysis")
        
        # Extract all text blocks
        all_blocks = []
        for page in pages:
            all_blocks.extend(page.text_blocks)
        
        if not all_blocks:
            return {"clusters": [], "hierarchy": {}, "statistics": {}}
        
        # Normalize font information
        normalized_blocks = self._normalize_font_info(all_blocks)
        
        # Cluster similar fonts
        font_clusters = self._cluster_fonts(normalized_blocks)
        
        # Detect hierarchy levels
        hierarchy_mapping = self._detect_hierarchy(font_clusters)
        
        # Generate statistics
        statistics = self._generate_font_statistics(font_clusters)
        
        self.logger.info(f"Found {len(font_clusters)} font clusters")
        
        return {
            "clusters": font_clusters,
            "hierarchy": hierarchy_mapping,
            "statistics": statistics
        }
    
    def _normalize_font_info(self, blocks: List[TextBlock]) -> List[Tuple[TextBlock, FontCharacteristics]]:
        """Normalize font information from different PDF extractors."""
        normalized = []
        
        for block in blocks:
            font_info = block.font_info
            
            # Extract font characteristics
            characteristics = FontCharacteristics()
            
            # Font name
            if "font" in font_info:
                characteristics.name = font_info["font"]
            elif "fontname" in font_info:
                characteristics.name = font_info["fontname"]
            
            # Font size
            if "size" in font_info:
                characteristics.size = float(font_info["size"])
            
            # Font style flags (PyMuPDF format)
            if "flags" in font_info:
                flags = font_info["flags"]
                characteristics.is_bold = bool(flags & 2**4)  # Bold flag
                characteristics.is_italic = bool(flags & 2**6)  # Italic flag
            
            # Font style from name (common patterns)
            font_name_lower = characteristics.name.lower()
            if "bold" in font_name_lower:
                characteristics.is_bold = True
            if "italic" in font_name_lower:
                characteristics.is_italic = True
            
            # Color
            if "color" in font_info:
                characteristics.color = font_info["color"]
            
            normalized.append((block, characteristics))
        
        return normalized
    
    def _cluster_fonts(self, normalized_blocks: List[Tuple[TextBlock, FontCharacteristics]]) -> List[FontCluster]:
        """Cluster similar fonts together."""
        font_groups = defaultdict(list)
        
        # Group by font characteristics
        for block, characteristics in normalized_blocks:
            style_key = characteristics.style_key
            font_groups[style_key].append((block, characteristics))
        
        # Create clusters
        clusters = []
        for style_key, group in font_groups.items():
            if not group:
                continue
            
            # Use the first characteristics as representative
            representative_chars = group[0][1]
            blocks = [item[0] for item in group]
            
            cluster = FontCluster(
                characteristics=representative_chars,
                text_blocks=blocks,
                frequency=len(blocks)
            )
            
            clusters.append(cluster)
        
        # Sort by frequency (most common first)
        clusters.sort(key=lambda c: c.frequency, reverse=True)
        
        return clusters
    
    def _detect_hierarchy(self, clusters: List[FontCluster]) -> Dict[HierarchyLevel, List[FontCluster]]:
        """Detect hierarchy levels based on font characteristics and content patterns."""
        hierarchy_mapping = defaultdict(list)
        
        for cluster in clusters:
            detected_level = self._classify_cluster_hierarchy(cluster)
            if detected_level:
                cluster.hierarchy_level = detected_level
                hierarchy_mapping[detected_level].append(cluster)
        
        return dict(hierarchy_mapping)
    
    def _classify_cluster_hierarchy(self, cluster: FontCluster) -> Optional[HierarchyLevel]:
        """Classify a font cluster into hierarchy level."""
        chars = cluster.characteristics
        sample_texts = [block.text for block in cluster.text_blocks[:10]]  # Sample first 10
        
        # Score different hierarchy levels
        level_scores = defaultdict(float)
        
        # Font size based scoring
        if chars.size >= 16:
            level_scores[HierarchyLevel.TITLE] += 0.3
        elif chars.size >= 14:
            level_scores[HierarchyLevel.CHAPTER] += 0.2
            level_scores[HierarchyLevel.SECTION] += 0.1
        elif chars.size >= 12:
            level_scores[HierarchyLevel.ARTICLE] += 0.2
            level_scores[HierarchyLevel.SECTION] += 0.1
        else:
            level_scores[HierarchyLevel.BODY_TEXT] += 0.2
            level_scores[HierarchyLevel.PARAGRAPH] += 0.1
        
        # Font style based scoring
        if chars.is_bold:
            level_scores[HierarchyLevel.TITLE] += 0.2
            level_scores[HierarchyLevel.CHAPTER] += 0.15
            level_scores[HierarchyLevel.ARTICLE] += 0.1
        
        if chars.is_italic:
            level_scores[HierarchyLevel.FOOTNOTE] += 0.2
        
        # Pattern based scoring
        for text in sample_texts:
            text_clean = text.strip()
            
            for level, patterns in self.legal_patterns.items():
                for pattern in patterns:
                    if re.match(pattern, text_clean, re.IGNORECASE):
                        level_scores[level] += 0.4
                        break
        
        # Position based scoring (headers/footers)
        for block in cluster.text_blocks[:5]:  # Check first few blocks
            if block.bbox[1] < 50:  # Top of page
                level_scores[HierarchyLevel.HEADER] += 0.1
            elif block.bbox[3] > 750:  # Bottom of page (assuming ~800pt page)
                level_scores[HierarchyLevel.FOOTER] += 0.1
        
        # Text length based scoring
        avg_length = cluster.average_text_length
        if avg_length < 50:
            level_scores[HierarchyLevel.TITLE] += 0.1
            level_scores[HierarchyLevel.CHAPTER] += 0.1
        elif avg_length > 200:
            level_scores[HierarchyLevel.BODY_TEXT] += 0.2
        
        # Find best match
        if level_scores:
            best_level = max(level_scores.items(), key=lambda x: x[1])
            if best_level[1] > 0.3:  # Minimum confidence threshold
                cluster.confidence = best_level[1]
                return best_level[0]
        
        # Default to body text if no clear classification
        cluster.confidence = 0.1
        return HierarchyLevel.BODY_TEXT
    
    def _generate_font_statistics(self, clusters: List[FontCluster]) -> Dict[str, Any]:
        """Generate font usage statistics."""
        total_blocks = sum(cluster.frequency for cluster in clusters)
        
        # Font family distribution
        font_families = Counter()
        for cluster in clusters:
            font_families[cluster.characteristics.name] += cluster.frequency
        
        # Font size distribution
        font_sizes = Counter()
        for cluster in clusters:
            size_range = f"{int(cluster.characteristics.size)}-{int(cluster.characteristics.size)+1}pt"
            font_sizes[size_range] += cluster.frequency
        
        # Hierarchy distribution
        hierarchy_dist = Counter()
        for cluster in clusters:
            if cluster.hierarchy_level:
                hierarchy_dist[cluster.hierarchy_level.value] += cluster.frequency
        
        # Style distribution
        style_dist = {
            "bold": sum(c.frequency for c in clusters if c.characteristics.is_bold),
            "italic": sum(c.frequency for c in clusters if c.characteristics.is_italic),
            "underlined": sum(c.frequency for c in clusters if c.characteristics.is_underlined),
            "normal": sum(c.frequency for c in clusters if not any([
                c.characteristics.is_bold, 
                c.characteristics.is_italic, 
                c.characteristics.is_underlined
            ]))
        }
        
        return {
            "total_text_blocks": total_blocks,
            "unique_font_styles": len(clusters),
            "font_families": dict(font_families.most_common()),
            "font_sizes": dict(font_sizes.most_common()),
            "hierarchy_distribution": dict(hierarchy_dist),
            "style_distribution": style_dist,
            "most_common_font": clusters[0].characteristics.style_key if clusters else None,
            "largest_font_size": max((c.characteristics.size for c in clusters), default=0),
            "smallest_font_size": min((c.characteristics.size for c in clusters), default=0)
        }
    
    def get_hierarchy_blocks(self, pages: List[PDFPage], level: HierarchyLevel) -> List[TextBlock]:
        """Get all text blocks of a specific hierarchy level."""
        analysis = self.analyze_fonts(pages)
        hierarchy = analysis["hierarchy"]
        
        blocks = []
        if level in hierarchy:
            for cluster in hierarchy[level]:
                blocks.extend(cluster.text_blocks)
        
        return blocks
    
    def get_document_structure(self, pages: List[PDFPage]) -> Dict[str, Any]:
        """Get a structured representation of the document."""
        analysis = self.analyze_fonts(pages)
        hierarchy = analysis["hierarchy"]
        
        structure = {
            "title": [],
            "chapters": [],
            "sections": [],
            "articles": [],
            "paragraphs": [],
            "body_text": []
        }
        
        # Map hierarchy levels to structure keys
        level_mapping = {
            HierarchyLevel.TITLE: "title",
            HierarchyLevel.CHAPTER: "chapters",
            HierarchyLevel.SECTION: "sections",
            HierarchyLevel.ARTICLE: "articles",
            HierarchyLevel.PARAGRAPH: "paragraphs",
            HierarchyLevel.BODY_TEXT: "body_text"
        }
        
        for level, clusters in hierarchy.items():
            if level in level_mapping:
                key = level_mapping[level]
                for cluster in clusters:
                    for block in cluster.text_blocks:
                        structure[key].append({
                            "text": block.text,
                            "page": block.page_number,
                            "bbox": block.bbox,
                            "confidence": cluster.confidence
                        })
        
        return structure