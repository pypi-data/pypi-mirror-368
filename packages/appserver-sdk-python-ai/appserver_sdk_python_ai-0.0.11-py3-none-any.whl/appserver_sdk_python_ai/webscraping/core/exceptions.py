# appserver_sdk_python_ai/webscraping/core/exceptions.py
"""
Exceções customizadas para o módulo de webscraping.
"""


class WebScrapingError(Exception):
    """Exceção base para erros de scraping."""

    def __init__(self, message: str, url: str | None = None, status_code: int | None = None):
        self.message = message
        self.url = url
        self.status_code = status_code
        super().__init__(message)

    def __str__(self):
        parts = [self.message]
        if self.url:
            parts.append(f"URL: {self.url}")
        if self.status_code:
            parts.append(f"Status: {self.status_code}")
        return " | ".join(parts)


class ConversionError(WebScrapingError):
    """Exceção para erros de conversão de conteúdo."""

    pass


class NetworkError(WebScrapingError):
    """Exceção para erros de rede."""

    pass


class ValidationError(WebScrapingError):
    """Exceção para erros de validação."""

    pass


class CacheError(WebScrapingError):
    """Exceção para erros de cache."""

    pass


class RateLimitError(WebScrapingError):
    """Exceção para erros de rate limit."""

    pass


class AuthenticationError(WebScrapingError):
    """Exceção para erros de autenticação."""

    pass


class ContentTooLargeError(WebScrapingError):
    """Exceção quando o conteúdo é muito grande."""

    pass


class UnsupportedFormatError(WebScrapingError):
    """Exceção para formatos não suportados."""

    pass


class TimeoutError(WebScrapingError):
    """Exceção para timeouts."""

    pass


class ProxyError(WebScrapingError):
    """Exceção para erros de proxy."""

    pass


class SSLVerificationError(WebScrapingError):
    """Exceção para erros de verificação SSL."""

    pass
