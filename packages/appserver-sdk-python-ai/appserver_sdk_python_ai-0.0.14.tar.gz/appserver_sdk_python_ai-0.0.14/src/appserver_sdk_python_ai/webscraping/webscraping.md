# Módulo WebScraping - AppServer SDK Python AI

O módulo WebScraping fornece funcionalidades avançadas para extração de conteúdo de páginas web, processamento de documentos e OCR (Optical Character Recognition).

## 🚀 Características Principais

### Web Scraping
- **Conversão Docling**: Conversão inteligente de HTML para Markdown
- **Extração de Metadados**: Título, descrição, palavras-chave, Open Graph
- **Sistema de Cache**: Cache inteligente para melhor performance
- **Processamento em Lote**: Scraping paralelo de múltiplas URLs
- **Tratamento de Erros**: Retry automático e tratamento robusto de erros

### OCR (Optical Character Recognition)
- **Múltiplos Engines**: Tesseract, EasyOCR, PaddleOCR
- **Formatos Suportados**: JPEG, PNG, GIF, TIFF, BMP, WEBP
- **Pré-processamento**: Melhoria automática da qualidade da imagem
- **Processamento em Lote**: OCR paralelo de múltiplas imagens
- **Seleção Automática**: Escolha automática do melhor engine disponível

### Processamento de PDFs
- **OCR Avançado**: Processamento de PDFs com OCR usando Docling
- **Extração de Imagens**: Extração e catalogação de imagens em PDFs
- **Extração de Tabelas**: Reconhecimento e extração de tabelas
- **Processamento em Lote**: Processamento paralelo de múltiplos PDFs
- **Metadados Detalhados**: Informações completas sobre o processamento

## 📦 Instalação

### Dependências Básicas
```bash
pip install requests beautifulsoup4 lxml
```

### Docling (Para conversão avançada e PDFs)
```bash
pip install docling
```

### OCR - Dependências Opcionais

#### Tesseract (Recomendado)
```bash
pip install pytesseract pillow

# Instalar Tesseract:
# Windows: https://github.com/UB-Mannheim/tesseract/wiki
# Linux: sudo apt install tesseract-ocr tesseract-ocr-por
# macOS: brew install tesseract
```

#### EasyOCR (Opcional)
```bash
pip install easyocr
```

#### PaddleOCR (Opcional)
```bash
pip install paddleocr
```

## 🔧 Uso Básico

### Web Scraping Simples
```python
from appserver_sdk_python_ai.webscraping import quick_scrape

# Scraping básico
resultado = quick_scrape("https://example.com")
print(f"Título: {resultado.title}")
print(f"Conteúdo: {resultado.content}")
```

### Web Scraping em Lote
```python
from appserver_sdk_python_ai.webscraping import batch_scrape_simple

urls = [
    "https://example1.com",
    "https://example2.com",
    "https://example3.com"
]

resultados = batch_scrape_simple(urls, max_workers=3)
for resultado in resultados:
    if resultado.success:
        print(f"✓ {resultado.url}: {resultado.title}")
    else:
        print(f"✗ {resultado.url}: {resultado.error}")
```

### OCR de Imagens
```python
from appserver_sdk_python_ai.webscraping import quick_ocr, batch_ocr

# OCR simples
texto = quick_ocr("imagem.png")
print(texto)

# OCR em lote
resultados = batch_ocr(["img1.png", "img2.jpg", "img3.gif"])
for resultado in resultados:
    if resultado["success"]:
        print(f"{resultado['image_path']}: {resultado['text']}")
```

### Processamento de PDFs
```python
from appserver_sdk_python_ai.webscraping import process_pdf_with_ocr, batch_process_pdfs

# PDF único
resultado = process_pdf_with_ocr(
    pdf_path="documento.pdf",
    extract_images=True,
    extract_tables=True
)

print(f"Páginas: {resultado.metadata['pages_processed']}")
print(f"Imagens: {resultado.metadata['images_count']}")
print(f"Tabelas: {resultado.metadata['tables_count']}")

# Múltiplos PDFs
resultados = batch_process_pdfs(
    pdf_paths=["doc1.pdf", "doc2.pdf"],
    output_dir="resultados",
    extract_images=True,
    extract_tables=True
)
```

## ⚙️ Configuração Avançada

### DoclingWebScraper
```python
from appserver_sdk_python_ai.webscraping import DoclingWebScraper

scraper = DoclingWebScraper(
    cache_enabled=True,
    cache_ttl=3600,
    request_delay=1.0,
    max_retries=3,
    timeout=30
)

resultado = scraper.scrape("https://example.com")
```

### OCR Customizado
```python
from appserver_sdk_python_ai.webscraping import create_custom_ocr_processor

processor = create_custom_ocr_processor(
    engine="tesseract",
    languages=["pt", "en"],
    confidence_threshold=0.8,
    preprocessing={
        "resize_factor": 2.0,
        "denoise": True,
        "enhance_contrast": True
    }
)

resultado = processor.process_image("imagem.png")
```

## 📊 Status e Verificações

### Verificar Status do Módulo
```python
from appserver_sdk_python_ai.webscraping import print_status, health_check

# Status detalhado
print_status()

# Health check
status = health_check()
print(f"Docling disponível: {status['dependencies']['docling']}")
print(f"OCR disponível: {status['features']['ocr_processing']}")
```

### Verificar Engines de OCR
```python
from appserver_sdk_python_ai.webscraping import (
    get_available_ocr_engines,
    check_ocr_dependencies,
    OCR_AVAILABLE
)

if OCR_AVAILABLE:
    engines = get_available_ocr_engines()
    print(f"Engines disponíveis: {engines}")
    
    deps = check_ocr_dependencies()
    for dep, status in deps.items():
        print(f"{dep}: {'✓' if status else '✗'}")
```

## 🎯 Casos de Uso

### 1. Extração de Conteúdo de Notícias
```python
from appserver_sdk_python_ai.webscraping import DoclingWebScraper

scraper = DoclingWebScraper()
urls_noticias = [
    "https://site-noticias1.com/artigo1",
    "https://site-noticias2.com/artigo2"
]

resultados = scraper.batch_scrape(urls_noticias)
for resultado in resultados:
    if resultado.success:
        print(f"Título: {resultado.title}")
        print(f"Resumo: {resultado.content[:200]}...")
        print(f"Palavras-chave: {resultado.metadata.get('keywords', [])}")
```

### 2. Digitalização de Documentos
```python
from appserver_sdk_python_ai.webscraping import batch_ocr
import os

# Encontrar todas as imagens em um diretório
imagens = []
for arquivo in os.listdir("documentos_escaneados"):
    if arquivo.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
        imagens.append(os.path.join("documentos_escaneados", arquivo))

# Processar todas as imagens
resultados = batch_ocr(
    image_paths=imagens,
    languages=["pt", "en"],
    max_workers=3
)

# Salvar resultados
for resultado in resultados:
    if resultado["success"]:
        nome_arquivo = os.path.splitext(resultado["image_path"])[0] + ".txt"
        with open(nome_arquivo, "w", encoding="utf-8") as f:
            f.write(resultado["text"])
```

### 3. Processamento de Relatórios em PDF
```python
from appserver_sdk_python_ai.webscraping import batch_process_pdfs
import glob

# Encontrar todos os PDFs
pdfs = glob.glob("relatorios/*.pdf")

def callback_progresso(atual, total, arquivo, sucesso):
    print(f"[{atual}/{total}] {'✓' if sucesso else '✗'} {os.path.basename(arquivo)}")

# Processar todos os PDFs
resultados = batch_process_pdfs(
    pdf_paths=pdfs,
    output_dir="relatorios_processados",
    extract_images=True,
    extract_tables=True,
    progress_callback=callback_progresso
)

# Gerar relatório
print("\n=== RELATÓRIO DE PROCESSAMENTO ===")
sucessos = sum(1 for r in resultados if r.success)
print(f"Total processado: {len(resultados)}")
print(f"Sucessos: {sucessos}")
print(f"Falhas: {len(resultados) - sucessos}")

total_paginas = sum(r.metadata.get('pages_processed', 0) for r in resultados if r.success)
total_imagens = sum(r.metadata.get('images_count', 0) for r in resultados if r.success)
total_tabelas = sum(r.metadata.get('tables_count', 0) for r in resultados if r.success)

print(f"Total de páginas: {total_paginas}")
print(f"Total de imagens: {total_imagens}")
print(f"Total de tabelas: {total_tabelas}")
```

## 🚨 Tratamento de Erros

```python
from appserver_sdk_python_ai.webscraping import (
    WebScrapingError,
    ConversionError,
    ValidationError,
    CacheError,
    OCRError,
    OCRNotAvailableError
)

try:
    resultado = quick_scrape("https://example.com")
except ValidationError as e:
    print(f"URL inválida: {e}")
except ConversionError as e:
    print(f"Erro na conversão: {e}")
except WebScrapingError as e:
    print(f"Erro geral: {e}")

try:
    texto = quick_ocr("imagem.png")
except OCRNotAvailableError:
    print("OCR não disponível. Instale as dependências.")
except OCRError as e:
    print(f"Erro no OCR: {e}")
```

## 📈 Performance e Otimização

### Dicas de Performance

1. **Use Cache**: Habilite o cache para URLs e imagens processadas frequentemente
2. **Processamento em Lote**: Use funções batch para múltiplos itens
3. **Configuração de Workers**: Ajuste `max_workers` baseado no seu hardware
4. **Timeout Adequado**: Configure timeouts apropriados para seu caso
5. **Pré-processamento**: Configure OCR adequadamente para seu tipo de imagem

### Configurações Recomendadas

```python
# Para web scraping intensivo
scraper = DoclingWebScraper(
    cache_enabled=True,
    cache_ttl=7200,  # 2 horas
    request_delay=0.5,  # Respeitar servidores
    max_retries=3,
    timeout=30
)

# Para OCR de documentos
processor = create_custom_ocr_processor(
    engine="tesseract",
    languages=["pt", "en"],
    preprocessing={
        "resize_factor": 2.0,
        "denoise": True,
        "enhance_contrast": True
    },
    cache_enabled=True
)

# Para processamento de PDFs
resultados = batch_process_pdfs(
    pdf_paths=pdfs,
    max_workers=2,  # PDFs são intensivos
    extract_images=True,
    extract_tables=True
)
```

## 🔗 Integração com Outros Módulos

O módulo WebScraping pode ser integrado com outros componentes do AppServer SDK:

```python
# Exemplo de integração com processamento de IA
from appserver_sdk_python_ai.webscraping import quick_scrape
from appserver_sdk_python_ai.ai import process_text  # Exemplo

# Extrair conteúdo
resultado = quick_scrape("https://artigo-tecnico.com")

if resultado.success:
    # Processar com IA
    resumo = process_text(resultado.content, task="summarize")
    print(f"Resumo: {resumo}")
```

## 📚 Exemplos Completos

Veja o arquivo `examples/webscraping_ocr_example.py` para exemplos completos de uso de todas as funcionalidades.

## 🤝 Contribuição

Para contribuir com o módulo:

1. **Web Scraping**: Melhore a extração de metadados, adicione suporte a novos sites
2. **OCR**: Adicione novos engines, melhore pré-processamento
3. **PDFs**: Otimize processamento, adicione novos tipos de extração
4. **Performance**: Otimize algoritmos, melhore cache
5. **Documentação**: Adicione exemplos, melhore documentação

## 📄 Licença

Este módulo faz parte do AppServer SDK Python AI e segue a mesma licença do projeto principal.

---

**Versão**: 1.0.0  
**Última atualização**: 2024  
**Compatibilidade**: Python 3.8+