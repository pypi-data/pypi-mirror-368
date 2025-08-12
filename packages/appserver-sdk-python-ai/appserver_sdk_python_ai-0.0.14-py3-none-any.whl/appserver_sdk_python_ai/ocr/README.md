# Módulo OCR - Extração de Texto de Imagens

Este módulo fornece funcionalidades avançadas de OCR (Optical Character Recognition) para extrair texto de imagens em diversos formatos.

## 🚀 Características

- **Múltiplos Engines**: Suporte para Tesseract, EasyOCR e PaddleOCR
- **Seleção Automática**: Escolha automática do melhor engine disponível
- **Formatos Suportados**: JPEG, PNG, GIF, TIFF, BMP, WEBP
- **Pré-processamento**: Melhoria automática da qualidade da imagem
- **Cache Inteligente**: Cache de resultados para melhor performance
- **Processamento em Lote**: Processamento paralelo de múltiplas imagens
- **Configuração Flexível**: Configurações detalhadas para cada engine

## 📦 Instalação

### Dependências Básicas
```bash
pip install pillow
```

### Engines de OCR

#### Tesseract (Recomendado)
```bash
# Instalar biblioteca Python
pip install pytesseract

# Instalar Tesseract
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

### OCR Simples
```python
from appserver_sdk_python_ai.ocr import quick_ocr

# OCR básico
texto = quick_ocr("imagem.png")
print(texto)

# OCR com idiomas específicos
texto = quick_ocr("imagem.png", languages=["pt", "en"])
print(texto)
```

### OCR em Lote
```python
from appserver_sdk_python_ai.ocr import batch_ocr

def progress_callback(current, total, image_path, success):
    print(f"[{current}/{total}] {'✓' if success else '✗'} {image_path}")

resultados = batch_ocr(
    image_paths=["img1.png", "img2.jpg", "img3.gif"],
    max_workers=3,
    progress_callback=progress_callback
)

for resultado in resultados:
    if resultado["success"]:
        print(f"{resultado['image_path']}: {resultado['text']}")
    else:
        print(f"Erro em {resultado['image_path']}: {resultado['error']}")
```

### OCR Customizado
```python
from appserver_sdk_python_ai.ocr import create_custom_ocr_processor

# Criar processador customizado
processor = create_custom_ocr_processor(
    engine="tesseract",
    languages=["pt", "en"],
    confidence_threshold=0.8,
    preprocessing={
        "resize_factor": 2.0,
        "denoise": True,
        "enhance_contrast": True
    },
    cache_enabled=True
)

# Processar imagem
resultado = processor.process_image("imagem.png")
print(f"Texto: {resultado['text']}")
print(f"Confiança: {resultado['confidence']}")
print(f"Engine: {resultado['engine']}")
```

## ⚙️ Configuração Avançada

### Classe OCRConfig
```python
from appserver_sdk_python_ai.ocr import OCRConfig, OCRProcessor

config = OCRConfig(
    engine="auto",  # tesseract, easyocr, paddleocr, auto
    languages=["pt", "en"],
    confidence_threshold=0.7,
    
    # Configurações específicas do Tesseract
    tesseract_config={
        "psm": 6,  # Page Segmentation Mode
        "oem": 3,  # OCR Engine Mode
        "custom_config": "--psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz "
    },
    
    # Configurações do EasyOCR
    easyocr_config={
        "gpu": False,
        "detail": 1,
        "paragraph": False
    },
    
    # Configurações do PaddleOCR
    paddleocr_config={
        "use_angle_cls": True,
        "use_gpu": False,
        "show_log": False
    },
    
    # Pré-processamento de imagem
    preprocessing={
        "resize_factor": 1.5,
        "denoise": True,
        "enhance_contrast": True,
        "convert_to_grayscale": True,
        "threshold_type": "adaptive"  # binary, adaptive, otsu
    },
    
    # Pós-processamento de texto
    postprocessing={
        "remove_extra_whitespace": True,
        "fix_line_breaks": True,
        "remove_special_chars": False,
        "min_word_length": 1
    },
    
    # Cache
    cache_enabled=True,
    cache_ttl=3600,  # 1 hora
    
    # Processamento em lote
    batch_size=10,
    max_workers=3
)

processor = OCRProcessor(config)
```

## 🎯 Engines de OCR

### Tesseract
- **Prós**: Maduro, preciso, muitos idiomas
- **Contras**: Requer instalação separada
- **Melhor para**: Documentos, texto limpo

### EasyOCR
- **Prós**: Fácil instalação, boa para texto em cena
- **Contras**: Modelos grandes, menos idiomas
- **Melhor para**: Imagens naturais, placas, sinais

### PaddleOCR
- **Prós**: Rápido, boa precisão, suporte a chinês
- **Contras**: Documentação em chinês
- **Melhor para**: Documentos asiáticos, texto misto

## 📊 Formatos Suportados

| Formato | Extensões | Suporte |
|---------|-----------|----------|
| JPEG | .jpg, .jpeg | ✅ |
| PNG | .png | ✅ |
| GIF | .gif | ✅ |
| TIFF | .tiff, .tif | ✅ |
| BMP | .bmp | ✅ |
| WEBP | .webp | ✅ |

## 🔍 Verificação de Status

```python
from appserver_sdk_python_ai.ocr import (
    get_available_ocr_engines,
    check_ocr_dependencies,
    OCR_AVAILABLE
)

# Verificar se OCR está disponível
if OCR_AVAILABLE:
    print("OCR está disponível!")
else:
    print("OCR não está disponível")

# Listar engines disponíveis
engines = get_available_ocr_engines()
print(f"Engines disponíveis: {engines}")

# Verificar dependências
deps = check_ocr_dependencies()
for dep, status in deps.items():
    print(f"{dep}: {'✓' if status else '✗'}")
```

## 🚨 Tratamento de Erros

```python
from appserver_sdk_python_ai.ocr import (
    OCRError,
    OCRNotAvailableError,
    OCREngineError,
    OCRImageError,
    OCRFormatNotSupportedError,
    OCRTimeoutError,
    OCRLowConfidenceError
)

try:
    texto = quick_ocr("imagem.png")
except OCRNotAvailableError:
    print("OCR não está disponível. Instale as dependências.")
except OCRImageError as e:
    print(f"Erro na imagem: {e}")
except OCREngineError as e:
    print(f"Erro no engine: {e}")
except OCRLowConfidenceError as e:
    print(f"Baixa confiança no resultado: {e}")
except OCRError as e:
    print(f"Erro geral de OCR: {e}")
```

## 🎨 Pré-processamento de Imagem

O módulo inclui várias técnicas de pré-processamento para melhorar a qualidade do OCR:

- **Redimensionamento**: Aumenta a resolução para melhor reconhecimento
- **Remoção de Ruído**: Remove artefatos que podem confundir o OCR
- **Melhoria de Contraste**: Aumenta a diferença entre texto e fundo
- **Conversão para Escala de Cinza**: Simplifica o processamento
- **Binarização**: Converte para preto e branco puro

## 📈 Performance

### Dicas para Melhor Performance

1. **Use cache**: Habilite o cache para imagens processadas frequentemente
2. **Processamento em lote**: Use `batch_ocr` para múltiplas imagens
3. **Pré-processamento**: Configure adequadamente para seu tipo de imagem
4. **Engine apropriado**: Escolha o engine mais adequado para seu caso
5. **Resolução**: Imagens com DPI 300+ têm melhor precisão

### Benchmarks Típicos

| Engine | Velocidade | Precisão | Uso de Memória |
|--------|------------|----------|----------------|
| Tesseract | Médio | Alto | Baixo |
| EasyOCR | Lento | Alto | Alto |
| PaddleOCR | Rápido | Médio | Médio |

## 🔗 Integração com PDFs

Para processamento de PDFs com OCR, use as funções específicas que utilizam o Docling:

```python
from appserver_sdk_python_ai.ocr import (
    process_pdf_with_ocr,
    batch_process_pdfs
)

# Processar PDF único
resultado = process_pdf_with_ocr(
    pdf_path="documento.pdf",
    extract_images=True,
    extract_tables=True
)

# Processar múltiplos PDFs
resultados = batch_process_pdfs(
    pdf_paths=["doc1.pdf", "doc2.pdf"],
    output_dir="resultados",
    extract_images=True,
    extract_tables=True
)
```

## 🤝 Contribuição

Para contribuir com melhorias:

1. Adicione novos engines de OCR
2. Melhore algoritmos de pré-processamento
3. Otimize performance
4. Adicione suporte a novos formatos
5. Melhore tratamento de erros

## 📄 Licença

Este módulo faz parte do AppServer SDK Python AI e segue a mesma licença do projeto principal.