# appserver_sdk_python_ai/webscraping/__init__.py
"""
Módulo de Web Scraping para appserver_sdk_python_ai
============================================

Este módulo fornece funcionalidades avançadas de web scraping com conversão
para markdown usando Docling e outras ferramentas.

Componentes principais:
- DoclingWebScraper: Scraper principal com Docling
- Utilitários de limpeza e validação
- Sistema de cache robusto
- Processamento em lote
- Tratamento avançado de erros

Exemplo de uso básico:
    from appserver_sdk_python_ai.webscraping import DoclingWebScraper, ScrapingConfig

    config = ScrapingConfig(clean_html=True, enable_cache=True)
    scraper = DoclingWebScraper(config)
    result = scraper.scrape_to_markdown("https://example.com")

Exemplo de uso simplificado:
    from appserver_sdk_python_ai.webscraping import quick_scrape
    markdown = quick_scrape("https://example.com")
"""

__version__ = "1.0.0"
__author__ = "appserver_sdk_python_ai"

# Importações padrão
import logging

# Importações principais
from .core.config import (
    DoclingConfig,
    GlobalWebScrapingConfig,
    ScrapingConfig,
    global_config,
)
from .core.exceptions import (
    AuthenticationError,
    CacheError,
    ContentTooLargeError,
    ConversionError,
    NetworkError,
    RateLimitError,
    UnsupportedFormatError,
    ValidationError,
    WebScrapingError,
)
from .core.models import (
    BatchScrapingResult,
    CacheEntry,
    ScrapingResult,
    ScrapingStatus,
    WebPageMetadata,
)

# Importações condicionais para evitar erros quando dependências não estão instaladas
try:
    from .docling.scraper import DoclingWebScraper

    SCRAPER_AVAILABLE = True
except ImportError as e:
    DoclingWebScraper = None  # type: ignore
    SCRAPER_AVAILABLE = False
    import warnings

    warnings.warn(f"DoclingWebScraper não pôde ser importado: {e}", stacklevel=2)

try:
    from .utils.cache import CacheManager, MemoryCache
    from .utils.cleaner import ContentCleaner
    from .utils.validators import ContentValidator, RobotsTxtChecker, URLValidator

    UTILS_AVAILABLE = True
except ImportError as e:
    ContentCleaner = None  # type: ignore
    CacheManager = None  # type: ignore
    MemoryCache = None  # type: ignore
    URLValidator = None  # type: ignore
    ContentValidator = None  # type: ignore
    RobotsTxtChecker = None  # type: ignore
    UTILS_AVAILABLE = False
    import warnings

    warnings.warn(f"Utilitários não puderam ser importados: {e}", stacklevel=2)

# Verificar disponibilidade do Docling
try:
    import docling

    DOCLING_AVAILABLE = True
    DOCLING_VERSION = getattr(docling, "__version__", "unknown")
except ImportError:
    DOCLING_AVAILABLE = False
    DOCLING_VERSION = None


# Funções de conveniência
def quick_scrape(
    url: str,
    clean_html: bool = True,
    include_images: bool = True,
    enable_cache: bool = False,
) -> str:
    """
    Função de conveniência para scraping rápido.

    Args:
        url: URL para fazer scraping
        clean_html: Se deve limpar HTML
        include_images: Se deve incluir imagens
        enable_cache: Se deve habilitar cache

    Returns:
        str: Conteúdo em markdown

    Raises:
        WebScrapingError: Em caso de erro no scraping
    """
    if not SCRAPER_AVAILABLE or DoclingWebScraper is None:
        raise WebScrapingError(
            "DoclingWebScraper não está disponível. Verifique as dependências."
        )

    config = ScrapingConfig(
        clean_html=clean_html, include_images=include_images, enable_cache=enable_cache
    )

    scraper = DoclingWebScraper(config)
    result = scraper.scrape_to_markdown(url)

    if not result.success:
        raise WebScrapingError(f"Falha no scraping: {result.error}", url)

    return result.content


def batch_scrape_simple(
    urls: list, output_dir: str = "scraped_content", max_workers: int = 5
) -> dict:
    """
    Função de conveniência para scraping em lote.

    Args:
        urls: Lista de URLs
        output_dir: Diretório de saída
        max_workers: Número máximo de workers

    Returns:
        dict: Dicionário com status de sucesso para cada URL
    """
    if not SCRAPER_AVAILABLE or DoclingWebScraper is None:
        raise WebScrapingError(
            "DoclingWebScraper não está disponível. Verifique as dependências."
        )

    scraper = DoclingWebScraper()
    results = scraper.batch_scrape(urls, output_dir, max_workers)

    return {result.url: result.success for result in results}


def create_custom_scraper(
    timeout: int = 30,
    user_agent: str | None = None,
    clean_html: bool = True,
    include_images: bool = True,
    enable_cache: bool = False,
    **kwargs,
):
    """
    Cria um scraper customizado com configurações específicas.

    Args:
        timeout: Timeout para requisições
        user_agent: User agent customizado
        clean_html: Se deve limpar HTML
        include_images: Se deve incluir imagens
        enable_cache: Se deve habilitar cache
        **kwargs: Outros parâmetros de configuração

    Returns:
        DoclingWebScraper: Instância configurada
    """
    if not SCRAPER_AVAILABLE or DoclingWebScraper is None:
        raise WebScrapingError(
            "DoclingWebScraper não está disponível. Verifique as dependências."
        )

    config = ScrapingConfig(
        timeout=timeout,
        user_agent=user_agent or global_config.default_user_agent,
        clean_html=clean_html,
        include_images=include_images,
        enable_cache=enable_cache,
        **kwargs,
    )

    return DoclingWebScraper(config)


# Funções de informação
def get_version_info():
    """Retorna informações sobre a versão e dependências."""
    import sys

    return {
        "webscraping_version": __version__,
        "docling_available": DOCLING_AVAILABLE,
        "docling_version": DOCLING_VERSION,
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
    }


def check_dependencies():
    """Verifica se todas as dependências estão instaladas."""
    dependencies = {
        "requests": None,
        "beautifulsoup4": None,
        "lxml": None,
        "docling": None,
    }

    for dep in dependencies:
        try:
            if dep == "beautifulsoup4":
                import bs4

                dependencies[dep] = getattr(bs4, "__version__", "installed")
            elif dep == "docling":
                import docling

                dependencies[dep] = getattr(docling, "__version__", "installed")
            else:
                module = __import__(dep)
                dependencies[dep] = getattr(module, "__version__", "installed")
        except ImportError:
            dependencies[dep] = "NOT_INSTALLED"

    return dependencies


def health_check():
    """Verifica a saúde do módulo e suas dependências."""
    health = {
        "status": "OK",
        "version": __version__,
        "dependencies": check_dependencies(),
        "features": {
            "docling_conversion": DOCLING_AVAILABLE,
            "cache_system": True,
            "batch_processing": True,
        },
        "issues": [],
    }

    deps = health["dependencies"]

    # Verificar dependências críticas
    if deps["requests"] == "NOT_INSTALLED":
        health["status"] = "ERROR"
        health["issues"].append("requests não está instalado")

    if deps["beautifulsoup4"] == "NOT_INSTALLED":
        health["status"] = "ERROR"
        health["issues"].append("beautifulsoup4 não está instalado")

    # Verificar dependências opcionais
    if deps["lxml"] == "NOT_INSTALLED":
        if health["status"] != "ERROR":
            health["status"] = "WARNING"
        health["issues"].append(
            "lxml não está instalado (parser HTML pode ser mais lento)"
        )

    if deps["docling"] == "NOT_INSTALLED":
        if health["status"] != "ERROR":
            health["status"] = "WARNING"
        health["issues"].append(
            "docling não está instalado (conversão básica será usada)"
        )

    return health


def print_status():
    """Imprime status do módulo."""
    health = health_check()

    print("=" * 60)
    print("MÓDULO WEB SCRAPING - appserver_sdk_python_ai")
    print("=" * 60)
    print(f"Versão: {__version__}")
    print(f"Status: {health['status']}")
    print(f"Docling: {'✅ Disponível' if DOCLING_AVAILABLE else '❌ Não disponível'}")

    print("\n📦 Dependências:")
    for dep, version in health["dependencies"].items():
        status = "✅" if version != "NOT_INSTALLED" else "❌"
        version_str = version if version != "NOT_INSTALLED" else "NÃO INSTALADO"
        print(f"  {status} {dep}: {version_str}")

    if health["issues"]:
        print("\n⚠️ Problemas encontrados:")
        for issue in health["issues"]:
            print(f"  • {issue}")

    print("\n🚀 Recursos disponíveis:")
    for feature, available in health["features"].items():
        status = "✅" if available else "❌"
        print(f"  {status} {feature.replace('_', ' ').title()}")

    print("=" * 60)


# Configuração de logging


def setup_logging(level=logging.INFO, format_string=None):
    """
    Configura logging para o módulo.

    Args:
        level: Nível de logging
        format_string: Formato customizado para logs
    """
    if format_string is None:
        format_string = global_config.log_format

    logging.basicConfig(
        level=level, format=format_string, handlers=[logging.StreamHandler()]
    )


# Exportar tudo necessário
__all__ = [
    # Classes principais
    "DoclingWebScraper",
    "ScrapingConfig",
    "DoclingConfig",
    "GlobalWebScrapingConfig",
    "global_config",
    # Modelos
    "ScrapingResult",
    "BatchScrapingResult",
    "WebPageMetadata",
    "CacheEntry",
    "ScrapingStatus",
    # Exceções
    "WebScrapingError",
    "ConversionError",
    "NetworkError",
    "ValidationError",
    "CacheError",
    "RateLimitError",
    "AuthenticationError",
    "ContentTooLargeError",
    "UnsupportedFormatError",
    # Utilitários
    "ContentCleaner",
    "CacheManager",
    "MemoryCache",
    "URLValidator",
    "ContentValidator",
    "RobotsTxtChecker",
    # Funções de conveniência
    "quick_scrape",
    "batch_scrape_simple",
    "create_custom_scraper",
    # Informações e configuração
    "get_version_info",
    "check_dependencies",
    "health_check",
    "print_status",
    "setup_logging",
    # Constantes
    "__version__",
    "DOCLING_AVAILABLE",
    "DOCLING_VERSION",
]

# Inicialização automática
logger = logging.getLogger(__name__)
logger.info(f"Módulo webscraping v{__version__} carregado")

if not DOCLING_AVAILABLE:
    logger.warning("Docling não disponível - usando conversão básica")
