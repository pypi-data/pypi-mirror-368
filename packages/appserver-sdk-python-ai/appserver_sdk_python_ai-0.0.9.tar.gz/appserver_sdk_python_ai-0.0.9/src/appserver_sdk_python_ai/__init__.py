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

__version__ = "0.0.9"
__author__ = "appserver_sdk_python_ai"

# Importar módulos principais
try:
    from . import webscraping
except ImportError as e:
    import warnings

    warnings.warn(f"Módulo webscraping não pôde ser importado: {e}", stacklevel=2)
    webscraping = None

# Exportar módulos disponíveis
__all__ = [
    "webscraping",
    "__version__",
    "__author__",
]


# Informações do SDK
def get_sdk_info():
    """Retorna informações sobre o SDK."""
    modules = []

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
