# appserver_sdk_python_ai/ocr/__init__.py
"""Módulo OCR para extração de texto de imagens.

Este módulo fornece funcionalidades avançadas de OCR (Optical Character Recognition)
para extrair texto de imagens em diversos formatos.

Características:
- Múltiplos engines: Tesseract, EasyOCR, PaddleOCR
- Formatos suportados: JPEG, PNG, GIF, TIFF, BMP, WEBP
- Pré-processamento automático de imagens
- Cache inteligente de resultados
- Processamento em lote
- Seleção automática do melhor engine

Exemplo de uso:
    from appserver_sdk_python_ai.ocr import OCRProcessor, OCRConfig

    # OCR customizado
    config = OCRConfig(engine="tesseract", languages=["pt", "en"])
    processor = OCRProcessor(config)
    resultado = processor.process_image("imagem.png")
"""

import warnings
from typing import Any

__version__ = "1.0.0"
__author__ = "appserver_sdk_python_ai"

from .config import OCRConfig
from .exceptions import OCRError, OCRNotAvailableError
from .processor import OCRProcessor

__all__ = [
    # Classes principais
    "OCRProcessor",
    "OCRConfig",
    # Exceções
    "OCRError",
    "OCRNotAvailableError",
    "OCREngineError",
    "OCRImageError",
    "OCRFormatNotSupportedError",
    "OCRTimeoutError",
    "OCRLowConfidenceError",
    # Funções utilitárias
    "get_available_ocr_engines",
    "check_ocr_dependencies",
    # Constantes
    "OCR_AVAILABLE",
    # Informações do módulo
    "__version__",
    "__author__",
]

# Verificar disponibilidade de bibliotecas de OCR
OCR_LIBRARIES = {
    "tesseract": False,
    "easyocr": False,
    "paddleocr": False,
}

try:
    import PIL
    import pytesseract

    OCR_LIBRARIES["tesseract"] = True
except ImportError:
    pass

try:
    import easyocr

    OCR_LIBRARIES["easyocr"] = True
except ImportError:
    pass

try:
    import paddleocr

    OCR_LIBRARIES["paddleocr"] = True
except ImportError:
    pass

# Verificar se pelo menos uma biblioteca está disponível
OCR_AVAILABLE = any(OCR_LIBRARIES.values())


def get_available_ocr_engines():
    """Retorna lista de engines de OCR disponíveis."""
    return [engine for engine, available in OCR_LIBRARIES.items() if available]


def check_ocr_dependencies():
    """Verifica dependências de OCR e retorna status."""
    return {
        "ocr_available": OCR_AVAILABLE,
        "libraries": OCR_LIBRARIES.copy(),
        "recommended_install": "pip install pytesseract pillow easyocr"
        if not OCR_AVAILABLE
        else None,
    }
