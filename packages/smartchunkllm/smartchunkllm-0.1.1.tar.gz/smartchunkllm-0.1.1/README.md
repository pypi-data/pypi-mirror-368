# SmartChunkLLM

Türkçe hukuki belgeler için gelişmiş semantik metin parçalama ve analiz sistemi.

## 🚀 Kurulum

### Gereksinimler
- Python 3.8+
- pip veya conda

### Temel Kurulum

```bash
# Projeyi klonlayın
git clone <repository-url>
cd smartchunkllm

# Sanal ortam oluşturun (önerilen)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# veya
venv\Scripts\activate     # Windows

# Bağımlılıkları yükleyin
pip install -r requirements.txt

# Paketi geliştirme modunda yükleyin
pip install -e .
```

### İsteğe Bağlı Bağımlılıklar

```bash
# OCR desteği için
pip install "smartchunkllm[ocr]"

# Web arayüzü için
pip install "smartchunkllm[web]"

# Türkçe NLP desteği için
pip install "smartchunkllm[turkish]"

# Tüm özellikler için
pip install "smartchunkllm[all]"
```

## 📖 Kullanım

### Komut Satırı Arayüzü (CLI)

#### PDF Belgelerini İşleme

```bash
# Temel PDF işleme
smartchunk process document.pdf

# OCR ile taranmış PDF işleme
smartchunk process document.pdf --ocr

# Düzen algılama ile
smartchunk process document.pdf --layout-detection

# Çıktıyı JSON formatında kaydetme
smartchunk process document.pdf --output results.json --format json

# Özel parça boyutu ile
smartchunk process document.pdf --chunk-size 1000 --overlap 200
```

#### Ham Metin İşleme

```bash
# Metin dosyasını parçalama
smartchunk chunk-text input.txt --output chunks.json

# Farklı strateji ile
smartchunk chunk-text input.txt --strategy semantic --quality high
```

#### Sistem Bilgileri

```bash
# Sistem durumunu kontrol etme
smartchunk info

# Kullanım örneklerini görme
smartchunk examples
```

### Python API

#### Temel Kullanım

```python
from smartchunkllm import SmartChunkLLM, ChunkingStrategy, QualityLevel

# SmartChunkLLM örneği oluşturma
chunker = SmartChunkLLM(
    strategy=ChunkingStrategy.SEMANTIC,
    quality_level=QualityLevel.HIGH,
    chunk_size=800,
    overlap=150
)

# PDF belgesi işleme
result = chunker.process_pdf("document.pdf")

# Sonuçları görüntüleme
for chunk in result.chunks:
    print(f"Chunk {chunk.id}: {chunk.text[:100]}...")
    print(f"Kalite Skoru: {chunk.quality_score}")
    print(f"Güven Düzeyi: {chunk.confidence}")
    print("---")
```

#### Gelişmiş Kullanım

```python
from smartchunkllm import (
    SmartChunkLLM, 
    LLMProvider, 
    EmbeddingModel,
    ClusteringAlgorithm
)

# Gelişmiş yapılandırma
chunker = SmartChunkLLM(
    strategy=ChunkingStrategy.HYBRID,
    quality_level=QualityLevel.PREMIUM,
    llm_provider=LLMProvider.OPENAI,
    embedding_model=EmbeddingModel.OPENAI_ADA_002,
    clustering_algorithm=ClusteringAlgorithm.HIERARCHICAL,
    enable_ocr=True,
    enable_layout_detection=True,
    language="tr"
)

# Metin işleme
text = "Uzun hukuki metin..."
result = chunker.process_text(text)

# Kalite metrikleri
print(f"Ortalama Kalite: {result.metrics.average_quality}")
print(f"İşlem Süresi: {result.metrics.processing_time}s")
print(f"Bellek Kullanımı: {result.metrics.memory_usage}MB")
```

#### Hukuki Belge Analizi

```python
from smartchunkllm.legal import LegalAnalyzer

# Hukuki analiz
analyzer = LegalAnalyzer()
analysis = analyzer.analyze_document("contract.pdf")

# Sonuçları görüntüleme
print(f"Belge Türü: {analysis.document_type}")
print(f"Tespit Edilen Maddeler: {len(analysis.articles)}")
print(f"Anahtar Terimler: {analysis.key_terms}")
```

### Yapılandırma

#### Ortam Değişkenleri

```bash
# API anahtarları
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
export COHERE_API_KEY="your-cohere-key"

# Ollama yapılandırması
export OLLAMA_HOST="http://localhost:11434"

# Loglama seviyesi
export SMARTCHUNK_LOG_LEVEL="INFO"

# Bellek limiti (MB)
export SMARTCHUNK_MEMORY_LIMIT="2048"
```

#### Yapılandırma Dosyası

```yaml
# config.yaml
chunking:
  strategy: "semantic"
  chunk_size: 800
  overlap: 150
  quality_level: "high"

llm:
  provider: "openai"
  model: "gpt-4"
  temperature: 0.1
  max_tokens: 2000

embedding:
  model: "openai-ada-002"
  batch_size: 100

processing:
  enable_ocr: true
  enable_layout_detection: true
  language: "tr"
  max_workers: 4

logging:
  level: "INFO"
  format: "structured"
  file: "smartchunk.log"
```

## 🔧 Özellikler

### ✨ Temel Özellikler
- **Semantik Parçalama**: İçerik anlamına göre akıllı metin bölme
- **Çoklu Strateji**: Sabit boyut, semantik, hibrit parçalama
- **Kalite Değerlendirme**: Otomatik parça kalitesi analizi
- **Türkçe Desteği**: Özelleşmiş Türkçe NLP işlemleri

### 📄 PDF İşleme
- **OCR Desteği**: Taranmış belgeleri metin çıkarma
- **Düzen Algılama**: Sayfa düzenini koruyarak işleme
- **Font Analizi**: Metin biçimlendirme bilgilerini koruma
- **Tablo Çıkarma**: Yapılandırılmış veri tespiti

### 🤖 AI/ML Entegrasyonu
- **Çoklu LLM Desteği**: OpenAI, Anthropic, Cohere, Ollama
- **Embedding Modelleri**: Çeşitli gömme modeli seçenekleri
- **Kümeleme**: Benzer içerikleri gruplandırma
- **Kalite Analizi**: AI destekli kalite değerlendirme

### ⚖️ Hukuki Belge Desteği
- **Belge Türü Tespiti**: Sözleşme, kanun, yönetmelik analizi
- **Madde Çıkarma**: Hukuki maddeleri otomatik tespit
- **Anahtar Terim Analizi**: Hukuki terim vurgulama
- **Referans Takibi**: Çapraz referans analizi

### 🔍 Monitoring ve Profiling
- **Performans İzleme**: Gerçek zamanlı performans metrikleri
- **Bellek Yönetimi**: Otomatik bellek optimizasyonu
- **Loglama**: Yapılandırılmış günlük kayıtları
- **Hata Yönetimi**: Kapsamlı hata yakalama ve raporlama

## 📊 Çıktı Formatları

### JSON Çıktısı
```json
{
  "chunks": [
    {
      "id": "chunk_001",
      "text": "Metin içeriği...",
      "metadata": {
        "page_number": 1,
        "position": {"x": 100, "y": 200},
        "font_info": {"family": "Arial", "size": 12},
        "quality_score": 0.95,
        "confidence": 0.88
      }
    }
  ],
  "metrics": {
    "total_chunks": 25,
    "average_quality": 0.92,
    "processing_time": 15.3,
    "memory_usage": 256
  }
}
```

### Markdown Çıktısı
```markdown
# Belge Analiz Sonuçları

## Chunk 1
**Kalite Skoru**: 0.95  
**Sayfa**: 1  
**Pozisyon**: (100, 200)

Metin içeriği...

---

## Chunk 2
...
```

## 🛠️ Geliştirme

### Test Çalıştırma
```bash
# Tüm testleri çalıştırma
python -m pytest tests/

# Belirli bir test dosyası
python -m pytest tests/test_chunking.py

# Kapsam raporu ile
python -m pytest --cov=smartchunkllm tests/
```

### Kod Kalitesi
```bash
# Kod formatı kontrolü
black smartchunkllm/
flake8 smartchunkllm/

# Tip kontrolü
mypy smartchunkllm/
```

## 📝 Lisans

MIT License - Detaylar için `LICENSE` dosyasına bakınız.

## 🤝 Katkıda Bulunma

1. Projeyi fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## 📞 Destek

Sorularınız için:
- GitHub Issues
- Dokümantasyon: [Link]
- E-posta: [E-posta adresi]

---

**SmartChunkLLM** - Türkçe hukuki belgeler için akıllı metin analizi 🚀