"""LLM prompt templates for legal document processing."""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json


class PromptType(Enum):
    """Types of prompts for different tasks."""
    CHUNKING = "chunking"
    ANALYSIS = "analysis"
    CLASSIFICATION = "classification"
    QUALITY_ASSESSMENT = "quality_assessment"
    STRUCTURE_DETECTION = "structure_detection"
    REFERENCE_EXTRACTION = "reference_extraction"
    DEFINITION_EXTRACTION = "definition_extraction"
    SUMMARIZATION = "summarization"


@dataclass
class PromptTemplate:
    """A prompt template with variables."""
    name: str
    prompt_type: PromptType
    template: str
    variables: List[str]
    description: str = ""
    examples: List[Dict[str, str]] = None
    
    def __post_init__(self):
        if self.examples is None:
            self.examples = []
    
    def format(self, **kwargs) -> str:
        """Format the template with provided variables."""
        # Check if all required variables are provided
        missing_vars = [var for var in self.variables if var not in kwargs]
        if missing_vars:
            raise ValueError(f"Missing required variables: {missing_vars}")
        
        return self.template.format(**kwargs)
    
    def get_example_prompt(self, example_index: int = 0) -> str:
        """Get an example prompt with filled variables."""
        if not self.examples or example_index >= len(self.examples):
            return self.template
        
        example = self.examples[example_index]
        return self.format(**example)


class ChunkingPrompts:
    """Prompts for semantic chunking tasks."""
    
    SEMANTIC_CHUNKING = PromptTemplate(
        name="semantic_chunking",
        prompt_type=PromptType.CHUNKING,
        template="""Sen Türk hukuku konusunda uzman bir yapay zeka asistanısın. Verilen hukuki metni anlamsal olarak tutarlı parçalara böl.

Görevin:
1. Metni hukuki anlamı korunacak şekilde parçalara böl
2. Her parça kendi içinde tutarlı ve anlamlı olmalı
3. Madde, fıkra, bent yapısını dikkate al
4. Tanımlar, kurallar, istisnalar ve yaptırımları ayır

METİN:
{text}

ÇIKTI FORMATI:
Her parça için:
- Parça ID: [sayı]
- İçerik Türü: [tanım/kural/istisna/yaptırım/genel]
- Önem Düzeyi: [kritik/yüksek/orta/düşük]
- İçerik: [parça metni]
- Hukuki Kavramlar: [anahtar kavramlar listesi]

Parçalar:""",
        variables=["text"],
        description="Hukuki metni semantik parçalara böler",
        examples=[
            {
                "text": "MADDE 1 - Bu Kanunun amacı, kişisel verilerin işlenmesinde başta özel hayatın gizliliği olmak üzere kişilerin temel hak ve özgürlüklerini korumak ve kişisel verileri işleyen gerçek ve tüzel kişilerin yükümlülüklerini düzenlemektir."
            }
        ]
    )
    
    CHUNK_OPTIMIZATION = PromptTemplate(
        name="chunk_optimization",
        prompt_type=PromptType.CHUNKING,
        template="""Verilen hukuki metin parçasını kalite ve tutarlılık açısından optimize et.

MEVCUT PARÇA:
{chunk_content}

METADATA:
- İçerik Türü: {content_type}
- Önem Düzeyi: {importance_level}
- Kalite Skoru: {quality_score}

Optimizasyon kriterleri:
1. Hukuki bütünlük korunmalı
2. Gereksiz tekrarlar kaldırılmalı
3. Eksik bağlamlar tamamlanmalı
4. Referanslar netleştirilmeli

OPTİMİZE EDİLMİŞ PARÇA:""",
        variables=["chunk_content", "content_type", "importance_level", "quality_score"],
        description="Mevcut parçayı optimize eder"
    )
    
    CHUNK_MERGING = PromptTemplate(
        name="chunk_merging",
        prompt_type=PromptType.CHUNKING,
        template="""İki hukuki metin parçasının birleştirilip birleştirilemeyeceğini değerlendir.

PARÇA 1:
{chunk1_content}
İçerik Türü: {chunk1_type}

PARÇA 2:
{chunk2_content}
İçerik Türü: {chunk2_type}

Değerlendirme kriterleri:
1. Hukuki bağlam uyumu
2. İçerik türü uyumluluğu
3. Mantıksal akış
4. Boyut uygunluğu

Karar: [BİRLEŞTİR/AYRI_TUT]
Gerekçe: [açıklama]
Birleştirilmiş İçerik: [eğer birleştirme öneriliyorsa]""",
        variables=["chunk1_content", "chunk1_type", "chunk2_content", "chunk2_type"],
        description="İki parçanın birleştirilmesini değerlendirir"
    )


class AnalysisPrompts:
    """Prompts for legal document analysis."""
    
    STRUCTURE_ANALYSIS = PromptTemplate(
        name="structure_analysis",
        prompt_type=PromptType.STRUCTURE_DETECTION,
        template="""Verilen hukuki belgenin yapısını analiz et ve hiyerarşik organizasyonunu çıkar.

BELGE METNİ:
{document_text}

Analiz edilecek yapısal unsurlar:
1. Belge türü (kanun, yönetmelik, tebliğ, vb.)
2. Bölüm/kısım organizasyonu
3. Madde numaralandırması
4. Fıkra ve bent yapısı
5. Geçici ve son hükümler

ÇIKTI FORMATI (JSON):
{{
  "document_type": "[belge türü]",
  "title": "[belge başlığı]",
  "sections": [
    {{
      "type": "[bölüm/kısım]",
      "number": "[numara]",
      "title": "[başlık]",
      "articles": ["[madde numaraları]"]
    }}
  ],
  "articles": [
    {{
      "number": "[madde no]",
      "title": "[madde başlığı]",
      "paragraphs": ["[fıkra sayısı]"],
      "subparagraphs": ["[bent sayısı]"]
    }}
  ]
}}

Analiz:""",
        variables=["document_text"],
        description="Hukuki belge yapısını analiz eder"
    )
    
    LEGAL_CONCEPT_EXTRACTION = PromptTemplate(
        name="legal_concept_extraction",
        prompt_type=PromptType.ANALYSIS,
        template="""Verilen hukuki metinden önemli hukuki kavramları ve terimleri çıkar.

METİN:
{text}

Çıkarılacak kavram türleri:
1. Hukuki terimler ve tanımlar
2. Yükümlülükler ve haklar
3. Yaptırımlar ve cezalar
4. Prosedürler ve süreçler
5. Referans edilen diğer mevzuat

ÇIKTI FORMATI:
{{
  "legal_terms": [
    {{
      "term": "[terim]",
      "definition": "[tanım]",
      "category": "[kategori]",
      "importance": "[yüksek/orta/düşük]"
    }}
  ],
  "obligations": ["[yükümlülük listesi]"],
  "rights": ["[hak listesi]"],
  "sanctions": ["[yaptırım listesi]"],
  "procedures": ["[prosedür listesi]"],
  "references": ["[referans listesi]"]
}}

Kavramlar:""",
        variables=["text"],
        description="Hukuki kavramları ve terimleri çıkarır"
    )
    
    REFERENCE_ANALYSIS = PromptTemplate(
        name="reference_analysis",
        prompt_type=PromptType.REFERENCE_EXTRACTION,
        template="""Verilen hukuki metindeki tüm referansları (atıfları) tespit et ve kategorize et.

METİN:
{text}

Referans türleri:
1. İç referanslar (aynı belge içi madde/fıkra atıfları)
2. Dış referanslar (diğer kanun/yönetmelik atıfları)
3. Genel referanslar (yukarıdaki madde, aşağıdaki hüküm vb.)

ÇIKTI FORMATI:
{{
  "internal_references": [
    {{
      "type": "[madde/fıkra/bent]",
      "target": "[hedef numara]",
      "context": "[bağlam]",
      "position": "[metindeki konum]"
    }}
  ],
  "external_references": [
    {{
      "document_type": "[kanun/yönetmelik/vb.]",
      "document_number": "[sayı]",
      "specific_article": "[madde no]",
      "context": "[bağlam]"
    }}
  ],
  "general_references": [
    {{
      "type": "[yukarıdaki/aşağıdaki/bu]",
      "target_type": "[madde/hüküm/vb.]",
      "context": "[bağlam]"
    }}
  ]
}}

Referanslar:""",
        variables=["text"],
        description="Hukuki referansları tespit eder ve kategorize eder"
    )


class ClassificationPrompts:
    """Prompts for content classification."""
    
    CONTENT_TYPE_CLASSIFICATION = PromptTemplate(
        name="content_type_classification",
        prompt_type=PromptType.CLASSIFICATION,
        template="""Verilen hukuki metin parçasının içerik türünü sınıflandır.

METİN:
{text}

İçerik türleri:
1. TANIM - Bir kavram, terim veya durumun tanımlanması
2. KURAL - Genel kurallar, yükümlülükler, yasaklar
3. İSTİSNA - Genel kuralların istisnası, muafiyetler
4. YAPTIRIM - Cezalar, yaptırımlar, müeyyideler
5. PROSEDÜR - İşlemler, süreçler, usul kuralları
6. GENEL - Diğer genel hükümler

Değerlendirme kriterleri:
- Metnin ana amacı
- Kullanılan hukuki dil
- Yapısal özellikler
- Bağlam

SINIFLANDIRMA:
İçerik Türü: [TANIM/KURAL/İSTİSNA/YAPTIRIM/PROSEDÜR/GENEL]
Güven Skoru: [0.0-1.0]
Gerekçe: [açıklama]
Anahtar Göstergeler: [belirleyici kelime/ifadeler]""",
        variables=["text"],
        description="Hukuki içerik türünü sınıflandırır"
    )
    
    IMPORTANCE_CLASSIFICATION = PromptTemplate(
        name="importance_classification",
        prompt_type=PromptType.CLASSIFICATION,
        template="""Verilen hukuki metin parçasının önem düzeyini değerlendir.

METİN:
{text}
İÇERİK TÜRÜ: {content_type}

Önem düzeyi kriterleri:
1. KRİTİK - Temel haklar, ana yükümlülükler, ciddi yaptırımlar
2. YÜKSEK - Önemli kurallar, prosedürler, istisnalar
3. ORTA - Destekleyici hükümler, detay kurallar
4. DÜŞÜK - Teknik detaylar, tanımlar, geçici hükümler

Değerlendirme faktörleri:
- Hukuki sonuçların ciddiyeti
- Etkilenen kişi/kurum sayısı
- Uygulanma sıklığı
- Diğer hükümlerle bağlantı

ÖNEM DEĞERLENDİRMESİ:
Önem Düzeyi: [KRİTİK/YÜKSEK/ORTA/DÜŞÜK]
Güven Skoru: [0.0-1.0]
Gerekçe: [açıklama]
Etki Alanı: [etkilenen alan/kişiler]""",
        variables=["text", "content_type"],
        description="Hukuki içeriğin önem düzeyini değerlendirir"
    )


class QualityPrompts:
    """Prompts for quality assessment."""
    
    CHUNK_QUALITY_ASSESSMENT = PromptTemplate(
        name="chunk_quality_assessment",
        prompt_type=PromptType.QUALITY_ASSESSMENT,
        template="""Verilen hukuki metin parçasının kalitesini çok boyutlu olarak değerlendir.

METİN PARÇASI:
{chunk_content}

METADATA:
- İçerik Türü: {content_type}
- Önem Düzeyi: {importance_level}
- Uzunluk: {content_length} karakter

Kalite boyutları (0.0-1.0 skala):

1. TUTARLILIK (Coherence)
   - İç mantıksal bütünlük
   - Konu odaklılığı
   - Akış kalitesi

2. TAMLLIK (Completeness)
   - Hukuki bağlamın eksiksizliği
   - Gerekli bilgilerin varlığı
   - Referans bütünlüğü

3. OKUNABİLİRLİK (Readability)
   - Dil kalitesi
   - Anlaşılabilirlik
   - Yapısal netlik

4. TUTARLILIK (Consistency)
   - Terminoloji tutarlılığı
   - Format tutarlılığı
   - Stil tutarlılığı

5. ALAKA DÜZEYİ (Relevance)
   - Hukuki önem
   - Bağlam uygunluğu
   - Pratik değer

KALİTE DEĞERLENDİRMESİ:
{{
  "coherence": {{"score": 0.0, "explanation": ""}},
  "completeness": {{"score": 0.0, "explanation": ""}},
  "readability": {{"score": 0.0, "explanation": ""}},
  "consistency": {{"score": 0.0, "explanation": ""}},
  "relevance": {{"score": 0.0, "explanation": ""}},
  "overall_score": 0.0,
  "strengths": [""],
  "weaknesses": [""],
  "improvement_suggestions": [""]
}}

Değerlendirme:""",
        variables=["chunk_content", "content_type", "importance_level", "content_length"],
        description="Parça kalitesini çok boyutlu değerlendirir"
    )
    
    COMPARATIVE_QUALITY = PromptTemplate(
        name="comparative_quality",
        prompt_type=PromptType.QUALITY_ASSESSMENT,
        template="""İki hukuki metin parçasını kalite açısından karşılaştır.

PARÇA A:
{chunk_a_content}
İçerik Türü: {chunk_a_type}

PARÇA B:
{chunk_b_content}
İçerik Türü: {chunk_b_type}

Karşılaştırma kriterleri:
1. Hukuki bütünlük
2. İçerik zenginliği
3. Yapısal kalite
4. Pratik kullanılabilirlik

KARŞILAŞTIRMA SONUCU:
{{
  "better_chunk": "[A/B/EQUAL]",
  "quality_differences": {{
    "coherence": "[A/B/EQUAL] - [açıklama]",
    "completeness": "[A/B/EQUAL] - [açıklama]",
    "readability": "[A/B/EQUAL] - [açıklama]"
  }},
  "recommendation": "[hangi parçanın tercih edilmesi gerektiği]",
  "improvement_areas": ["[iyileştirme önerileri]"]
}}

Karşılaştırma:""",
        variables=["chunk_a_content", "chunk_a_type", "chunk_b_content", "chunk_b_type"],
        description="İki parçayı kalite açısından karşılaştırır"
    )


class SummarizationPrompts:
    """Prompts for summarization tasks."""
    
    CHUNK_SUMMARY = PromptTemplate(
        name="chunk_summary",
        prompt_type=PromptType.SUMMARIZATION,
        template="""Verilen hukuki metin parçasının özetini çıkar.

METİN PARÇASI:
{chunk_content}

Özet kriterleri:
1. Ana hukuki konuyu belirt
2. Temel kuralları/yükümlülükleri özetle
3. Önemli istisnaları dahil et
4. Pratik sonuçları vurgula
5. Maksimum {max_length} kelime

ÖZET:
Ana Konu: [konu başlığı]
Temel İçerik: [özet metin]
Anahtar Noktalar:
- [nokta 1]
- [nokta 2]
- [nokta 3]
Pratik Sonuç: [uygulamadaki anlamı]""",
        variables=["chunk_content", "max_length"],
        description="Hukuki parçanın özetini çıkarır"
    )
    
    DOCUMENT_SUMMARY = PromptTemplate(
        name="document_summary",
        prompt_type=PromptType.SUMMARIZATION,
        template="""Hukuki belgenin genel özetini oluştur.

BELGE BİLGİLERİ:
Başlık: {document_title}
Tür: {document_type}
Toplam Madde: {total_articles}
Ana Bölümler: {main_sections}

ÖNEMLİ PARÇALAR:
{important_chunks}

Özet gereksinimleri:
1. Belgenin amacını açıkla
2. Ana düzenlemeleri özetle
3. Önemli yükümlülükleri listele
4. Yaptırımları belirt
5. Uygulama alanını tanımla

BELGE ÖZETİ:
Amaç: [belgenin amacı]
Kapsam: [uygulama alanı]
Ana Düzenlemeler:
- [düzenleme 1]
- [düzenleme 2]
- [düzenleme 3]
Önemli Yükümlülükler:
- [yükümlülük 1]
- [yükümlülük 2]
Yaptırımlar: [yaptırım türleri]
Hedef Kitle: [kimler etkilenir]""",
        variables=["document_title", "document_type", "total_articles", "main_sections", "important_chunks"],
        description="Hukuki belgenin genel özetini oluşturur"
    )


class PromptManager:
    """Manages all prompt templates."""
    
    def __init__(self):
        """Initialize prompt manager with all templates."""
        self.templates = {}
        self._load_all_templates()
    
    def _load_all_templates(self):
        """Load all prompt templates."""
        # Chunking prompts
        self.templates.update({
            "semantic_chunking": ChunkingPrompts.SEMANTIC_CHUNKING,
            "chunk_optimization": ChunkingPrompts.CHUNK_OPTIMIZATION,
            "chunk_merging": ChunkingPrompts.CHUNK_MERGING,
        })
        
        # Analysis prompts
        self.templates.update({
            "structure_analysis": AnalysisPrompts.STRUCTURE_ANALYSIS,
            "legal_concept_extraction": AnalysisPrompts.LEGAL_CONCEPT_EXTRACTION,
            "reference_analysis": AnalysisPrompts.REFERENCE_ANALYSIS,
        })
        
        # Classification prompts
        self.templates.update({
            "content_type_classification": ClassificationPrompts.CONTENT_TYPE_CLASSIFICATION,
            "importance_classification": ClassificationPrompts.IMPORTANCE_CLASSIFICATION,
        })
        
        # Quality prompts
        self.templates.update({
            "chunk_quality_assessment": QualityPrompts.CHUNK_QUALITY_ASSESSMENT,
            "comparative_quality": QualityPrompts.COMPARATIVE_QUALITY,
        })
        
        # Summarization prompts
        self.templates.update({
            "chunk_summary": SummarizationPrompts.CHUNK_SUMMARY,
            "document_summary": SummarizationPrompts.DOCUMENT_SUMMARY,
        })
    
    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """Get a prompt template by name."""
        return self.templates.get(name)
    
    def get_templates_by_type(self, prompt_type: PromptType) -> List[PromptTemplate]:
        """Get all templates of a specific type."""
        return [template for template in self.templates.values() 
                if template.prompt_type == prompt_type]
    
    def list_templates(self) -> List[str]:
        """List all available template names."""
        return list(self.templates.keys())
    
    def format_prompt(self, template_name: str, **kwargs) -> str:
        """Format a prompt template with variables."""
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found")
        
        return template.format(**kwargs)
    
    def add_custom_template(self, template: PromptTemplate):
        """Add a custom prompt template."""
        self.templates[template.name] = template
    
    def export_templates(self) -> Dict[str, Dict[str, Any]]:
        """Export all templates as dictionary."""
        return {
            name: {
                "name": template.name,
                "type": template.prompt_type.value,
                "template": template.template,
                "variables": template.variables,
                "description": template.description,
                "examples": template.examples
            }
            for name, template in self.templates.items()
        }
    
    def import_templates(self, templates_dict: Dict[str, Dict[str, Any]]):
        """Import templates from dictionary."""
        for name, template_data in templates_dict.items():
            template = PromptTemplate(
                name=template_data["name"],
                prompt_type=PromptType(template_data["type"]),
                template=template_data["template"],
                variables=template_data["variables"],
                description=template_data.get("description", ""),
                examples=template_data.get("examples", [])
            )
            self.templates[name] = template