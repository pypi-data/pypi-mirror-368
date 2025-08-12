# appserver_sdk_python_ai/ocr/exceptions.py
"""
Exceções específicas para o módulo de OCR
========================================

Este módulo define exceções customizadas para operações de OCR.
"""


class OCRError(Exception):
    """Exceção base para erros de OCR."""

    def __init__(
        self,
        message: str,
        engine: str | None = None,
        file_path: str | None = None,
    ):
        self.message = message
        self.engine = engine
        self.file_path = file_path
        super().__init__(self.message)

    def __str__(self) -> str:
        parts = [self.message]
        if self.engine:
            parts.append(f"Engine: {self.engine}")
        if self.file_path:
            parts.append(f"Arquivo: {self.file_path}")
        return " | ".join(parts)


class OCRNotAvailableError(OCRError):
    """Exceção lançada quando nenhuma biblioteca de OCR está disponível."""

    def __init__(self, message: str = "Nenhuma biblioteca de OCR está disponível"):
        super().__init__(message)


class OCREngineError(OCRError):
    """Exceção lançada quando há erro específico do engine de OCR."""

    def __init__(
        self, message: str, engine: str, original_error: Exception | None = None
    ):
        self.original_error = original_error
        super().__init__(message, engine)


class OCRImageError(OCRError):
    """Exceção lançada quando há erro no processamento da imagem."""

    def __init__(
        self, message: str, file_path: str, original_error: Exception | None = None
    ):
        self.original_error = original_error
        super().__init__(message, file_path=file_path)


class OCRFormatNotSupportedError(OCRError):
    """Exceção lançada quando o formato de arquivo não é suportado."""

    def __init__(self, file_path: str, format_detected: str):
        message = f"Formato '{format_detected}' não é suportado para OCR"
        super().__init__(message, file_path=file_path)
        self.format_detected = format_detected


class OCRTimeoutError(OCRError):
    """Exceção lançada quando o processamento de OCR excede o timeout."""

    def __init__(self, file_path: str, timeout: int, engine: str | None = None):
        message = f"Timeout de {timeout}s excedido durante processamento de OCR"
        super().__init__(message, engine, file_path)
        self.timeout = timeout


class OCRLowConfidenceError(OCRError):
    """Exceção lançada quando a confiança do OCR está abaixo do mínimo."""

    def __init__(
        self,
        file_path: str,
        confidence: float,
        min_confidence: float,
        engine: str | None = None,
    ):
        message = f"Confiança do OCR ({confidence:.2f}) abaixo do mínimo ({min_confidence:.2f})"
        super().__init__(message, engine, file_path)
        self.confidence = confidence
        self.min_confidence = min_confidence
