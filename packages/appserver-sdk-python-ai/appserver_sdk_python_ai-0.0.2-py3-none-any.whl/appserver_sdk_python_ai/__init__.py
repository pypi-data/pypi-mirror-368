"""AppServer SDK Python AI - SDK para serviços de IA."""

from __future__ import annotations

# Version
__version__ = "0.0.2"  # Incrementada para nova publicação

# Metadata
__author__ = "AppServer Team"
__email__ = "suporte@appserver.com.br"
__description__ = "SDK Python para serviços de IA da AppServer"
__url__ = "https://appserver.com.br"

# Importações principais com tratamento de erro
try:
    # Core enums
    from .llm.core.enums import (
        HuggingFaceModelEnum,
        OpenAIModelEnum,
        TokenizerTypeEnum,
    )

    # Core services
    from .llm.service.token_service import (
        get_model_info,
        get_portuguese_models,
        get_token_count,
        get_token_count_with_model,
        is_model_registered,
        list_available_models,
        register_custom_model,
    )

    # Todos os exports disponíveis
    __all__ = [
        # Version info
        "__version__",
        "__author__",
        "__email__",
        "__description__",
        "__url__",
        # Enums
        "HuggingFaceModelEnum",
        "OpenAIModelEnum",
        "TokenizerTypeEnum",
        # Core functions
        "get_token_count",
        "get_token_count_with_model",
        "register_custom_model",
        "list_available_models",
        "get_model_info",
        "is_model_registered",
        "get_portuguese_models",
        # Utility
        "get_user_agent",
    ]

except ImportError as e:
    # Fallback se houver problemas de importação
    import warnings

    warnings.warn(
        f"Algumas funcionalidades não estão disponíveis: {e}. "
        "Instale as dependências opcionais com: pip install 'appserver-sdk-python-ai[full]'",
        ImportWarning,
        stacklevel=2,
    )

    # Exports mínimos
    __all__ = [
        "__version__",
        "__author__",
        "__email__",
        "__description__",
        "__url__",
        "get_user_agent",
    ]


def get_user_agent() -> str:
    """Retorna User-Agent para requisições."""
    return f"appserver-sdk-python-ai/{__version__}"
