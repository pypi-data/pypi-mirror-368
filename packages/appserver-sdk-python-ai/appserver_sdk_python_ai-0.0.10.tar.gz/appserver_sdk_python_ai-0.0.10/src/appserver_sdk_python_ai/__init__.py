# appserver_sdk_python_ai/__init__.py
"""
SDK Python AI para AppServer
============================

SDK principal que integra diversos módulos de IA e automação.

Módulos disponíveis:
- webscraping: Módulo avançado de web scraping com conversão para markdown

Exemplo de uso:
    from appserver_sdk_python_ai.webscraping import DoclingWebScraper, ScrapingConfig

    config = ScrapingConfig(clean_html=True, enable_cache=True)
    scraper = DoclingWebScraper(config)
    result = scraper.scrape_to_markdown("https://example.com")
"""

import warnings
from collections.abc import Callable
from typing import Any, Optional

__version__ = "0.0.10"
__author__ = "appserver_sdk_python_ai"

# Declarar variáveis com tipos apropriados
webscraping: Any | None = None
llm: Any | None = None
get_token_count: Callable[[str], int] | None = None
get_token_count_with_model: Callable[..., Any] | None = None
list_available_models: Callable[..., Any] | None = None
get_portuguese_models: Callable[..., Any] | None = None
get_model_info: Callable[[str], Any] | None = None

# Importar módulos principais
try:
    from . import webscraping
except ImportError as e:
    warnings.warn(f"Módulo webscraping não pôde ser importado: {e}", stacklevel=2)

try:
    from . import llm

    # Importar funções principais do LLM
    from .llm.service.token_service import (
        get_model_info,
        get_portuguese_models,
        get_token_count,
        get_token_count_with_model,
        list_available_models,
    )
except ImportError as e:
    warnings.warn(f"Módulo LLM não pôde ser importado: {e}", stacklevel=2)

try:
    from .webscraping.core.config import DEFAULT_USER_AGENT
except ImportError:
    DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"


def get_user_agent():
    """Retorna o user agent padrão do SDK."""
    return DEFAULT_USER_AGENT


# Exportar módulos disponíveis
__all__ = [
    "webscraping",
    "llm",
    "get_token_count",
    "get_token_count_with_model",
    "list_available_models",
    "get_portuguese_models",
    "get_model_info",
    "get_user_agent",
    "__version__",
    "__author__",
]


# Informações do SDK
def get_sdk_info():
    """Retorna informações sobre o SDK."""
    modules = []

    # Módulo WebScraping
    if webscraping is not None:
        modules.append(
            {
                "name": "webscraping",
                "version": getattr(webscraping, "__version__", "unknown"),
                "available": True,
            }
        )
    else:
        modules.append({"name": "webscraping", "version": None, "available": False})

    # Módulo LLM
    if llm is not None:
        modules.append(
            {
                "name": "llm",
                "version": getattr(llm, "__version__", "unknown"),
                "available": True,
            }
        )
    else:
        modules.append({"name": "llm", "version": None, "available": False})

    return {"sdk_version": __version__, "author": __author__, "modules": modules}


def print_sdk_status():
    """Imprime status do SDK."""
    info = get_sdk_info()

    print("=" * 60)
    print("APPSERVER SDK PYTHON AI")
    print("=" * 60)
    print(f"Versão: {info['sdk_version']}")
    print(f"Autor: {info['author']}")

    print("\n📦 Módulos:")
    for module in info["modules"]:
        status = "✅" if module["available"] else "❌"
        version = module["version"] if module["version"] else "NÃO DISPONÍVEL"
        print(f"  {status} {module['name']}: {version}")

    print("=" * 60)
