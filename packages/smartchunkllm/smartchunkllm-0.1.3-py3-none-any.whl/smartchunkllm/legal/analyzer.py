"""Legal document structure analyzer."""

from typing import Dict, List, Optional, Any, Tuple, Pattern
import re
import logging
from dataclasses import dataclass, field
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

# Core imports
from ..core.config import LegalConfig
from ..pdf.extractor import PDFPage, TextBlock
from ..pdf.font import HierarchyLevel


class LegalElementType(Enum):
    """Types of legal document elements."""
    TITLE = "title"
    CHAPTER = "chapter"  # Bölüm
    SECTION = "section"  # Kısım
    ARTICLE = "article"  # Madde
    PARAGRAPH = "paragraph"  # Fıkra
    SUBPARAGRAPH = "subparagraph"  # Bent
    ITEM = "item"  # Alt bent
    DEFINITION = "definition"  # Tanım
    EXCEPTION = "exception"  # İstisna
    SANCTION = "sanction"  # Yaptırım
    REFERENCE = "reference"  # Atıf
    GENERAL_PROVISION = "general_provision"  # Genel hüküm
    TRANSITIONAL_PROVISION = "transitional_provision"  # Geçici hüküm
    FINAL_PROVISION = "final_provision"  # Son hüküm


@dataclass
class LegalElement:
    """A legal document element."""
    element_type: LegalElementType
    number: Optional[str] = None
    title: Optional[str] = None
    content: str = ""
    level: int = 0
    parent_id: Optional[str] = None
    children_ids: List[str] = field(default_factory=list)
    page_number: int = 0
    position: Tuple[float, float, float, float] = (0, 0, 0, 0)  # x, y, width, height
    font_info: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def id(self) -> str:
        """Generate unique ID for the element."""
        if self.number:
            return f"{self.element_type.value}_{self.number}"
        else:
            return f"{self.element_type.value}_{hash(self.content[:50])}_{self.page_number}"


@dataclass
class LegalReference:
    """A reference to another legal document or element."""
    reference_type: str  # "internal", "external", "law", "regulation", etc.
    target: str  # What is being referenced
    source_element_id: str  # Where the reference appears
    context: str  # Surrounding text
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LegalStructure:
    """Complete legal document structure."""
    title: str = ""
    document_type: str = ""  # "kanun", "yönetmelik", "tebliğ", etc.
    document_number: Optional[str] = None
    date: Optional[str] = None
    sections: List[LegalElement] = field(default_factory=list)
    articles: List[LegalElement] = field(default_factory=list)
    definitions: List[LegalElement] = field(default_factory=list)
    references: List[LegalReference] = field(default_factory=list)
    hierarchy: Dict[str, List[str]] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_element_by_id(self, element_id: str) -> Optional[LegalElement]:
        """Get element by ID."""
        all_elements = self.sections + self.articles + self.definitions
        for element in all_elements:
            if element.id == element_id:
                return element
        return None
    
    def get_children(self, element_id: str) -> List[LegalElement]:
        """Get children of an element."""
        children = []
        all_elements = self.sections + self.articles + self.definitions
        for element in all_elements:
            if element.parent_id == element_id:
                children.append(element)
        return children
    
    def get_article_by_number(self, number: str) -> Optional[LegalElement]:
        """Get article by number."""
        for article in self.articles:
            if article.number == number:
                return article
        return None


class LegalAnalyzer:
    """Analyzes legal document structure and extracts legal elements."""
    
    def __init__(self, config: LegalConfig):
        """Initialize the legal analyzer.
        
        Args:
            config: Legal analysis configuration
        """
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Turkish legal patterns
        self.patterns = self._initialize_patterns()
        
        # Document type patterns
        self.document_type_patterns = {
            "kanun": [r"kanun\s*(?:no|sayı)?", r"\d+\s*sayılı\s*kanun"],
            "yönetmelik": [r"yönetmelik", r"yönetmeliği"],
            "tebliğ": [r"tebliğ", r"tebliği"],
            "genelge": [r"genelge", r"genelgesi"],
            "karar": [r"karar", r"kararı"],
            "yönerge": [r"yönerge", r"yönergesi"]
        }
    
    def _initialize_patterns(self) -> Dict[str, List[Pattern]]:
        """Initialize regex patterns for legal elements."""
        patterns = {
            "article": [
                re.compile(r"^\s*(?:MADDE|Madde)\s+(\d+)\s*[-–—]?\s*(.*?)$", re.MULTILINE | re.IGNORECASE),
                re.compile(r"^\s*(\d+)\s*\.\s*madde\s*[-–—]?\s*(.*?)$", re.MULTILINE | re.IGNORECASE),
                re.compile(r"^\s*m\.?\s*(\d+)\s*[-–—]?\s*(.*?)$", re.MULTILINE | re.IGNORECASE)
            ],
            "paragraph": [
                re.compile(r"^\s*\((\d+)\)\s*(.*?)$", re.MULTILINE),
                re.compile(r"^\s*(\d+)\s*-\s*(.*?)$", re.MULTILINE)
            ],
            "subparagraph": [
                re.compile(r"^\s*([a-z])\)\s*(.*?)$", re.MULTILINE),
                re.compile(r"^\s*([a-z])\s*-\s*(.*?)$", re.MULTILINE)
            ],
            "item": [
                re.compile(r"^\s*(\d+)\)\s*(.*?)$", re.MULTILINE),
                re.compile(r"^\s*([ivx]+)\)\s*(.*?)$", re.MULTILINE | re.IGNORECASE)
            ],
            "section": [
                re.compile(r"^\s*(?:BÖLÜM|Bölüm|KISIM|Kısım)\s+(\w+)\s*[-–—]?\s*(.*?)$", re.MULTILINE | re.IGNORECASE),
                re.compile(r"^\s*(\w+)\s*\.\s*(?:BÖLÜM|Bölüm|KISIM|Kısım)\s*[-–—]?\s*(.*?)$", re.MULTILINE | re.IGNORECASE)
            ],
            "chapter": [
                re.compile(r"^\s*(?:BÖLÜM|Bölüm)\s+(\w+)\s*[-–—]?\s*(.*?)$", re.MULTILINE | re.IGNORECASE)
            ],
            "definition": [
                re.compile(r"(\w+)\s*:\s*([^.]+\.)?", re.MULTILINE),
                re.compile(r"\"([^\"]+)\"\s*(?:ifadesi|deyimi|kavramı)\s*[,:]?\s*([^.]+\.)", re.MULTILINE)
            ],
            "reference": [
                re.compile(r"(\d+)\s*sayılı\s*(\w+)", re.IGNORECASE),
                re.compile(r"(?:bu\s+)?(?:kanun|yönetmelik|tebliğ)(?:un|ün)?\s*(\d+)\s*(?:inci|nci|üncü|ncü)?\s*madde(?:si|sinde|sine)?", re.IGNORECASE),
                re.compile(r"yukarıdaki\s*(?:madde|fıkra|bent)", re.IGNORECASE),
                re.compile(r"aşağıdaki\s*(?:madde|fıkra|bent)", re.IGNORECASE)
            ],
            "exception": [
                re.compile(r"(?:ancak|fakat|lakin|bununla\s+birlikte|bu\s+hüküm)", re.IGNORECASE),
                re.compile(r"(?:istisna|muafiyet|hariç)", re.IGNORECASE)
            ],
            "sanction": [
                re.compile(r"(?:ceza|para\s*cezası|hapis|disiplin)", re.IGNORECASE),
                re.compile(r"(?:yaptırım|müeyyide)", re.IGNORECASE)
            ]
        }
        
        return patterns
    
    def analyze_structure(self, pages: List[PDFPage], font_hierarchy: Dict[str, Any]) -> LegalStructure:
        """Analyze the structure of a legal document.
        
        Args:
            pages: Extracted PDF pages
            font_hierarchy: Font hierarchy analysis results
        
        Returns:
            LegalStructure object
        """
        try:
            self.logger.info("Starting legal structure analysis")
            
            # Initialize structure
            structure = LegalStructure()
            
            # Extract document metadata
            self._extract_document_metadata(pages, structure)
            
            # Extract legal elements
            all_elements = self._extract_legal_elements(pages, font_hierarchy)
            
            # Categorize elements
            self._categorize_elements(all_elements, structure)
            
            # Build hierarchy
            self._build_hierarchy(structure)
            
            # Extract references
            structure.references = self._extract_references(pages, structure)
            
            # Extract definitions
            structure.definitions = self._extract_definitions(pages)
            
            self.logger.info(f"Structure analysis completed: {len(structure.articles)} articles, {len(structure.sections)} sections")
            
            return structure
        
        except Exception as e:
            self.logger.error(f"Structure analysis failed: {e}")
            return LegalStructure()
    
    def _extract_document_metadata(self, pages: List[PDFPage], structure: LegalStructure):
        """Extract document title, type, and metadata."""
        if not pages:
            return
        
        # Look for title in first few pages
        first_page_text = ""
        for i, page in enumerate(pages[:3]):
            for block in page.text_blocks:
                first_page_text += block.text + "\n"
        
        # Extract document type
        for doc_type, patterns in self.document_type_patterns.items():
            for pattern in patterns:
                if re.search(pattern, first_page_text, re.IGNORECASE):
                    structure.document_type = doc_type
                    break
            if structure.document_type:
                break
        
        # Extract document number
        number_match = re.search(r"(\d+)\s*sayılı", first_page_text, re.IGNORECASE)
        if number_match:
            structure.document_number = number_match.group(1)
        
        # Extract date
        date_patterns = [
            r"(\d{1,2})[./](\d{1,2})[./](\d{4})",
            r"(\d{4})[./](\d{1,2})[./](\d{1,2})"
        ]
        for pattern in date_patterns:
            date_match = re.search(pattern, first_page_text)
            if date_match:
                structure.date = date_match.group(0)
                break
        
        # Extract title (usually the largest/bold text in first page)
        title_candidates = []
        if pages:
            for block in pages[0].text_blocks:
                # Look for title characteristics
                text = block.text.strip()
                if (len(text) > 10 and len(text) < 200 and 
                    not re.search(r"^\s*(?:madde|bölüm|kısım)\s+\d+", text, re.IGNORECASE)):
                    title_candidates.append(text)
        
        if title_candidates:
            # Use the first substantial text as title
            structure.title = title_candidates[0]
    
    def _extract_legal_elements(self, pages: List[PDFPage], font_hierarchy: Dict[str, Any]) -> List[LegalElement]:
        """Extract all legal elements from pages."""
        elements = []
        
        for page_num, page in enumerate(pages):
            for block in page.text_blocks:
                # Try to identify element type
                element_type, number, title = self._identify_element_type(block.text)
                
                if element_type:
                    element = LegalElement(
                        element_type=element_type,
                        number=number,
                        title=title,
                        content=block.text,
                        page_number=page_num + 1,
                        position=getattr(block, 'bbox', (0, 0, 0, 0)),
                        font_info=getattr(block, 'font_info', {})
                    )
                    elements.append(element)
        
        return elements
    
    def _identify_element_type(self, text: str) -> Tuple[Optional[LegalElementType], Optional[str], Optional[str]]:
        """Identify the type of legal element from text."""
        text = text.strip()
        
        # Check each pattern type
        for element_type_name, patterns in self.patterns.items():
            if element_type_name in ['definition', 'reference', 'exception', 'sanction']:
                continue  # These are handled separately
            
            for pattern in patterns:
                match = pattern.match(text)
                if match:
                    try:
                        element_type = LegalElementType(element_type_name)
                        number = match.group(1) if match.groups() else None
                        title = match.group(2) if len(match.groups()) > 1 else None
                        return element_type, number, title
                    except ValueError:
                        continue
        
        return None, None, None
    
    def _categorize_elements(self, elements: List[LegalElement], structure: LegalStructure):
        """Categorize elements into structure."""
        for element in elements:
            if element.element_type == LegalElementType.ARTICLE:
                structure.articles.append(element)
            elif element.element_type in [LegalElementType.SECTION, LegalElementType.CHAPTER]:
                structure.sections.append(element)
            elif element.element_type == LegalElementType.DEFINITION:
                structure.definitions.append(element)
    
    def _build_hierarchy(self, structure: LegalStructure):
        """Build hierarchical relationships between elements."""
        all_elements = structure.sections + structure.articles + structure.definitions
        
        # Sort by page number and position
        all_elements.sort(key=lambda x: (x.page_number, x.position[1] if x.position else 0))
        
        # Build parent-child relationships
        current_section = None
        current_article = None
        
        for element in all_elements:
            if element.element_type in [LegalElementType.SECTION, LegalElementType.CHAPTER]:
                current_section = element
                current_article = None
            elif element.element_type == LegalElementType.ARTICLE:
                if current_section:
                    element.parent_id = current_section.id
                    current_section.children_ids.append(element.id)
                current_article = element
            elif element.element_type in [LegalElementType.PARAGRAPH, LegalElementType.SUBPARAGRAPH, LegalElementType.ITEM]:
                if current_article:
                    element.parent_id = current_article.id
                    current_article.children_ids.append(element.id)
        
        # Update hierarchy dictionary
        for element in all_elements:
            if element.parent_id:
                if element.parent_id not in structure.hierarchy:
                    structure.hierarchy[element.parent_id] = []
                structure.hierarchy[element.parent_id].append(element.id)
    
    def _extract_references(self, pages: List[PDFPage], structure: LegalStructure) -> List[LegalReference]:
        """Extract legal references from the document."""
        references = []
        
        for page in pages:
            for block in page.text_blocks:
                text = block.text
                
                # Find references using patterns
                for pattern in self.patterns['reference']:
                    for match in pattern.finditer(text):
                        reference = LegalReference(
                            reference_type="internal" if "bu" in match.group(0).lower() else "external",
                            target=match.group(0),
                            source_element_id="",  # Will be filled later
                            context=text[max(0, match.start()-50):match.end()+50],
                            confidence=0.8
                        )
                        references.append(reference)
        
        return references
    
    def _extract_definitions(self, pages: List[PDFPage]) -> List[LegalElement]:
        """Extract definitions from the document."""
        definitions = []
        
        for page_num, page in enumerate(pages):
            for block in page.text_blocks:
                text = block.text
                
                # Look for definition patterns
                for pattern in self.patterns['definition']:
                    for match in pattern.finditer(text):
                        if len(match.groups()) >= 1:
                            term = match.group(1)
                            definition_text = match.group(2) if len(match.groups()) > 1 else ""
                            
                            definition = LegalElement(
                                element_type=LegalElementType.DEFINITION,
                                title=term,
                                content=definition_text or text,
                                page_number=page_num + 1,
                                metadata={"term": term}
                            )
                            definitions.append(definition)
        
        return definitions
    
    def analyze_content_type(self, text: str) -> Tuple[LegalElementType, float]:
        """Analyze content to determine its legal element type.
        
        Args:
            text: Text content to analyze
        
        Returns:
            Tuple of (element_type, confidence)
        """
        text_lower = text.lower()
        
        # Check for exceptions
        for pattern in self.patterns['exception']:
            if pattern.search(text):
                return LegalElementType.EXCEPTION, 0.8
        
        # Check for sanctions
        for pattern in self.patterns['sanction']:
            if pattern.search(text):
                return LegalElementType.SANCTION, 0.8
        
        # Check for definitions
        for pattern in self.patterns['definition']:
            if pattern.search(text):
                return LegalElementType.DEFINITION, 0.7
        
        # Default classification based on structure
        if any(word in text_lower for word in ['madde', 'article']):
            return LegalElementType.ARTICLE, 0.6
        elif any(word in text_lower for word in ['bölüm', 'kısım', 'chapter', 'section']):
            return LegalElementType.SECTION, 0.6
        elif re.search(r'^\s*\(\d+\)', text):
            return LegalElementType.PARAGRAPH, 0.7
        elif re.search(r'^\s*[a-z]\)', text):
            return LegalElementType.SUBPARAGRAPH, 0.7
        
        return LegalElementType.GENERAL_PROVISION, 0.3
    
    def extract_legal_concepts(self, text: str) -> List[str]:
        """Extract legal concepts and terminology from text.
        
        Args:
            text: Text to analyze
        
        Returns:
            List of legal concepts found
        """
        concepts = []
        
        # Turkish legal terminology
        legal_terms = [
            "hak", "yükümlülük", "sorumluluk", "yetki", "görev",
            "ceza", "para cezası", "hapis", "disiplin",
            "başvuru", "itiraz", "temyiz", "karar", "hüküm",
            "kanun", "yönetmelik", "tebliğ", "genelge",
            "madde", "fıkra", "bent", "kısım", "bölüm",
            "istisna", "muafiyet", "yasak", "izin",
            "süre", "tarih", "usul", "prosedür"
        ]
        
        text_lower = text.lower()
        for term in legal_terms:
            if term in text_lower:
                concepts.append(term)
        
        # Extract quoted terms (often definitions)
        quoted_terms = re.findall(r'"([^"]+)"', text)
        concepts.extend(quoted_terms)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_concepts = []
        for concept in concepts:
            if concept not in seen:
                unique_concepts.append(concept)
                seen.add(concept)
        
        return unique_concepts
    
    def validate_structure(self, structure: LegalStructure) -> Dict[str, Any]:
        """Validate the extracted legal structure.
        
        Args:
            structure: Legal structure to validate
        
        Returns:
            Validation results
        """
        validation_results = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "statistics": {}
        }
        
        # Check for required elements
        if not structure.articles:
            validation_results["warnings"].append("No articles found in document")
        
        # Check article numbering
        article_numbers = []
        for article in structure.articles:
            if article.number:
                try:
                    num = int(article.number)
                    article_numbers.append(num)
                except ValueError:
                    validation_results["warnings"].append(f"Invalid article number: {article.number}")
        
        # Check for gaps in numbering
        if article_numbers:
            article_numbers.sort()
            for i in range(len(article_numbers) - 1):
                if article_numbers[i+1] - article_numbers[i] > 1:
                    validation_results["warnings"].append(
                        f"Gap in article numbering between {article_numbers[i]} and {article_numbers[i+1]}"
                    )
        
        # Statistics
        validation_results["statistics"] = {
            "total_articles": len(structure.articles),
            "total_sections": len(structure.sections),
            "total_definitions": len(structure.definitions),
            "total_references": len(structure.references),
            "document_type": structure.document_type,
            "has_hierarchy": bool(structure.hierarchy)
        }
        
        return validation_results


class ConceptExtractor:
    """Extracts legal concepts and terminology from legal documents."""
    
    def __init__(self, config: Optional[LegalConfig] = None):
        """Initialize the concept extractor.
        
        Args:
            config: Legal analysis configuration
        """
        self.config = config or LegalConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Legal concept patterns
        self.concept_patterns = self._initialize_concept_patterns()
        
        # Legal terminology database
        self.legal_terms = self._initialize_legal_terms()
        
        self.logger.info("Concept extractor initialized")
    
    def _initialize_concept_patterns(self) -> Dict[str, List[Pattern]]:
        """Initialize regex patterns for concept extraction."""
        patterns = {
            "rights": [
                re.compile(r"\b(hak|hakk?ı|yetkisi?)\b", re.IGNORECASE),
                re.compile(r"\b(right|authority|power)\b", re.IGNORECASE)
            ],
            "obligations": [
                re.compile(r"\b(yükümlülük|sorumluluk|görev|vazife)\b", re.IGNORECASE),
                re.compile(r"\b(obligation|responsibility|duty)\b", re.IGNORECASE)
            ],
            "sanctions": [
                re.compile(r"\b(ceza|para\s*cezası|hapis|disiplin|yaptırım)\b", re.IGNORECASE),
                re.compile(r"\b(penalty|fine|imprisonment|sanction)\b", re.IGNORECASE)
            ],
            "procedures": [
                re.compile(r"\b(usul|prosedür|işlem|süreç)\b", re.IGNORECASE),
                re.compile(r"\b(procedure|process|method)\b", re.IGNORECASE)
            ],
            "timeframes": [
                re.compile(r"\b(\d+)\s*(gün|ay|yıl|hafta)\b", re.IGNORECASE),
                re.compile(r"\b(\d+)\s*(day|month|year|week)s?\b", re.IGNORECASE)
            ],
            "definitions": [
                re.compile(r'"([^"]+)"\s*(?:ifadesi|deyimi|kavramı|anlamına)', re.IGNORECASE),
                re.compile(r'([A-ZÜĞŞÇÖI][a-züğşçöı\s]+)\s*:\s*([^.]+\.)', re.MULTILINE)
            ]
        }
        
        return patterns
    
    def _initialize_legal_terms(self) -> Dict[str, List[str]]:
        """Initialize legal terminology database."""
        return {
            "turkish": [
                "kanun", "yönetmelik", "tebliğ", "genelge", "karar", "hüküm",
                "madde", "fıkra", "bent", "kısım", "bölüm",
                "hak", "yükümlülük", "sorumluluk", "yetki", "görev",
                "ceza", "para cezası", "hapis", "disiplin", "yaptırım",
                "başvuru", "itiraz", "temyiz", "dava", "mahkeme",
                "istisna", "muafiyet", "yasak", "izin", "ruhsat",
                "süre", "tarih", "usul", "prosedür", "işlem",
                "taraf", "sözleşme", "anlaşma", "protokol",
                "mülkiyet", "zilyetlik", "rehin", "ipotek",
                "miras", "vasiyet", "veraset", "mirasçı"
            ],
            "english": [
                "law", "regulation", "statute", "ordinance", "decree",
                "article", "section", "paragraph", "clause", "provision",
                "right", "obligation", "responsibility", "authority", "duty",
                "penalty", "fine", "imprisonment", "sanction",
                "application", "appeal", "lawsuit", "court",
                "exception", "exemption", "prohibition", "permit",
                "period", "deadline", "procedure", "process",
                "party", "contract", "agreement", "protocol",
                "property", "ownership", "possession", "mortgage",
                "inheritance", "will", "heir", "estate"
            ]
        }
    
    def extract_concepts(self, text: str, concept_types: Optional[List[str]] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Extract legal concepts from text.
        
        Args:
            text: Text to analyze
            concept_types: Specific concept types to extract (optional)
            
        Returns:
            Dictionary of concept types and their extracted instances
        """
        if concept_types is None:
            concept_types = list(self.concept_patterns.keys())
        
        extracted_concepts = {}
        
        for concept_type in concept_types:
            if concept_type in self.concept_patterns:
                concepts = self._extract_concept_type(text, concept_type)
                extracted_concepts[concept_type] = concepts
        
        return extracted_concepts
    
    def _extract_concept_type(self, text: str, concept_type: str) -> List[Dict[str, Any]]:
        """Extract specific type of concepts from text."""
        concepts = []
        patterns = self.concept_patterns.get(concept_type, [])
        
        for pattern in patterns:
            for match in pattern.finditer(text):
                concept = {
                    "text": match.group(0),
                    "start": match.start(),
                    "end": match.end(),
                    "context": text[max(0, match.start()-50):match.end()+50],
                    "confidence": self._calculate_confidence(match.group(0), concept_type)
                }
                
                # Add specific information based on concept type
                if concept_type == "timeframes" and len(match.groups()) >= 2:
                    concept["duration"] = match.group(1)
                    concept["unit"] = match.group(2)
                elif concept_type == "definitions" and len(match.groups()) >= 2:
                    concept["term"] = match.group(1)
                    concept["definition"] = match.group(2) if len(match.groups()) > 1 else ""
                
                concepts.append(concept)
        
        return concepts
    
    def _calculate_confidence(self, text: str, concept_type: str) -> float:
        """Calculate confidence score for extracted concept."""
        base_confidence = 0.7
        
        # Adjust confidence based on context and pattern strength
        text_lower = text.lower()
        
        # Higher confidence for exact legal terms
        for lang_terms in self.legal_terms.values():
            if any(term in text_lower for term in lang_terms):
                base_confidence += 0.2
                break
        
        # Adjust for concept type specificity
        type_adjustments = {
            "definitions": 0.1,
            "timeframes": 0.15,
            "sanctions": 0.1,
            "rights": 0.05,
            "obligations": 0.05,
            "procedures": 0.0
        }
        
        base_confidence += type_adjustments.get(concept_type, 0.0)
        
        return min(base_confidence, 1.0)
    
    def extract_legal_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract legal entities (persons, organizations, etc.) from text."""
        entities = []
        
        # Patterns for legal entities
        entity_patterns = [
            re.compile(r"\b([A-ZÜĞŞÇÖI][a-züğşçöı]+\s+(?:A\.Ş\.|Ltd\.|Şti\.|Koop\.))", re.MULTILINE),
            re.compile(r"\b([A-ZÜĞŞÇÖI][a-züğşçöı]+\s+(?:Inc\.|Corp\.|LLC|Ltd\.))", re.MULTILINE),
            re.compile(r"\b([A-ZÜĞŞÇÖI][a-züğşçöı]+\s+(?:Bakanlığı|Müdürlüğü|Başkanlığı))", re.MULTILINE),
            re.compile(r"\b([A-ZÜĞŞÇÖI][a-züğşçöı]+\s+(?:Ministry|Department|Agency))", re.MULTILINE)
        ]
        
        for pattern in entity_patterns:
            for match in pattern.finditer(text):
                entity = {
                    "name": match.group(1),
                    "start": match.start(),
                    "end": match.end(),
                    "context": text[max(0, match.start()-30):match.end()+30],
                    "type": self._classify_entity_type(match.group(1))
                }
                entities.append(entity)
        
        return entities
    
    def _classify_entity_type(self, entity_name: str) -> str:
        """Classify the type of legal entity."""
        name_lower = entity_name.lower()
        
        if any(suffix in name_lower for suffix in ["a.ş.", "ltd.", "şti.", "inc.", "corp.", "llc"]):
            return "company"
        elif any(suffix in name_lower for suffix in ["bakanlığı", "müdürlüğü", "başkanlığı", "ministry", "department"]):
            return "government_agency"
        elif "koop." in name_lower:
            return "cooperative"
        else:
            return "organization"
    
    def extract_legal_references(self, text: str) -> List[Dict[str, Any]]:
        """Extract references to other legal documents."""
        references = []
        
        # Patterns for legal references
        reference_patterns = [
            re.compile(r"(\d+)\s*sayılı\s*(\w+)", re.IGNORECASE),
            re.compile(r"(\d{1,2}/\d{1,2}/\d{4})\s*tarihli\s*(\w+)", re.IGNORECASE),
            re.compile(r"(?:bu\s+)?(kanun|yönetmelik|tebliğ)(?:un|ün)?\s*(\d+)\s*(?:inci|nci|üncü|ncü)?\s*madde(?:si)?", re.IGNORECASE),
            re.compile(r"(\d+)\s*(?:inci|nci|üncü|ncü)\s*madde", re.IGNORECASE)
        ]
        
        for pattern in reference_patterns:
            for match in pattern.finditer(text):
                reference = {
                    "text": match.group(0),
                    "start": match.start(),
                    "end": match.end(),
                    "context": text[max(0, match.start()-50):match.end()+50],
                    "type": self._classify_reference_type(match.group(0))
                }
                
                # Extract specific reference information
                if len(match.groups()) >= 2:
                    reference["number"] = match.group(1)
                    reference["document_type"] = match.group(2)
                
                references.append(reference)
        
        return references
    
    def _classify_reference_type(self, reference_text: str) -> str:
        """Classify the type of legal reference."""
        text_lower = reference_text.lower()
        
        if "madde" in text_lower:
            return "article_reference"
        elif "sayılı" in text_lower:
            return "numbered_document"
        elif "tarihli" in text_lower:
            return "dated_document"
        elif any(doc_type in text_lower for doc_type in ["kanun", "yönetmelik", "tebliğ"]):
            return "document_reference"
        else:
            return "general_reference"
    
    def analyze_concept_relationships(self, concepts: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Analyze relationships between extracted concepts."""
        relationships = {
            "concept_counts": {},
            "co_occurrences": {},
            "concept_density": {},
            "dominant_themes": []
        }
        
        # Count concepts by type
        for concept_type, concept_list in concepts.items():
            relationships["concept_counts"][concept_type] = len(concept_list)
        
        # Calculate concept density (concepts per 100 words)
        total_concepts = sum(relationships["concept_counts"].values())
        # Assuming average of 5 words per concept for rough estimation
        estimated_word_count = total_concepts * 5
        
        for concept_type, count in relationships["concept_counts"].items():
            if estimated_word_count > 0:
                relationships["concept_density"][concept_type] = (count / estimated_word_count) * 100
        
        # Identify dominant themes
        sorted_concepts = sorted(
            relationships["concept_counts"].items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        relationships["dominant_themes"] = [concept_type for concept_type, count in sorted_concepts[:3] if count > 0]
        
        return relationships
    
    def generate_concept_summary(self, concepts: Dict[str, List[Dict[str, Any]]]) -> str:
        """Generate a summary of extracted concepts."""
        summary_parts = []
        
        total_concepts = sum(len(concept_list) for concept_list in concepts.values())
        summary_parts.append(f"Toplam {total_concepts} hukuki kavram tespit edildi.")
        
        for concept_type, concept_list in concepts.items():
            if concept_list:
                count = len(concept_list)
                summary_parts.append(f"- {concept_type.title()}: {count} kavram")
        
        # Add most frequent concepts
        all_concepts = []
        for concept_list in concepts.values():
            all_concepts.extend([c["text"] for c in concept_list])
        
        if all_concepts:
            from collections import Counter
            most_common = Counter(all_concepts).most_common(3)
            if most_common:
                summary_parts.append("\nEn sık geçen kavramlar:")
                for concept, count in most_common:
                    summary_parts.append(f"- {concept} ({count} kez)")
        
        return "\n".join(summary_parts)