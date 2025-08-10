"""
AppServer SDK Python AI

SDK Python para serviços de IA da AppServer com suporte a contagem de tokens
para diversos modelos de linguagem.
"""

from __future__ import annotations

import warnings

# Informações do pacote
__version__ = "0.0.7"
__author__ = "AppServer Team"
__email__ = "suporte@appserver.com.br"
__description__ = (
    "SDK Python para serviços de IA da AppServer com suporte a contagem de tokens"
)


# User-Agent para identificação
def get_user_agent() -> str:
    """Retorna o User-Agent do SDK."""
    return f"AppServerSDKPythonAI/{__version__}"


# Variáveis para controle de importações
_import_success = False
_import_error = None
_available_functions = []

# Tentar importar funcionalidades completas
try:
    # Imports corretos baseados na estrutura real
    from appserver_sdk_python_ai.llm.core.enums import (
        ModelCapability,
        ModelProvider,
        ModelType,
        SupportedLanguage,
        TokenizationMethod,
    )
    from appserver_sdk_python_ai.llm.service.token_service import (
        get_model_info,
        get_portuguese_models,
        get_token_count,
        get_token_count_with_model,
        is_model_registered as is_model_available,
        list_available_models,
        register_custom_model,
    )
    
    # Implementar funções que não existem no token_service
    def get_default_model() -> str:
        """Retorna o modelo padrão."""
        return "gpt-4"
    
    def estimate_cost(token_count: int, model: str = "gpt-4") -> float:
        """Estima custo baseado no número de tokens."""
        # Custos aproximados por 1K tokens (valores de exemplo)
        costs = {
            "gpt-4": 0.03,
            "gpt-3.5-turbo": 0.002,
            "text-davinci-003": 0.02,
        }
        cost_per_1k = costs.get(model, 0.002)
        return (token_count / 1000) * cost_per_1k
    
    def get_multilingual_models() -> list[str]:
        """Lista modelos multilíngues."""
        return ["gpt-4", "gpt-3.5-turbo", "claude-3-sonnet", "claude-3-haiku"]
    
    # Classe TokenService para compatibilidade
    class TokenService:
        """Classe de serviço para tokens (compatibilidade)."""
        
        @staticmethod
        def count_tokens(text: str, model: str = "gpt-4") -> int:
            return get_token_count(text)
        
        @staticmethod
        def get_model_info(model: str) -> dict:
            return get_model_info(model) or {}

    # Se chegou até aqui, todas as importações foram bem-sucedidas
    _import_success = True
    _available_functions = [
        "get_token_count",
        "get_token_count_with_model",
        "list_available_models",
        "get_model_info",
        "get_portuguese_models",
        "get_multilingual_models",
        "is_model_available",
        "get_default_model",
        "estimate_cost",
        "register_custom_model",
        "get_user_agent",
        "get_sdk_info",
        "TokenService",
    ]

except ImportError as e:
    _import_success = False
    _import_error = str(e)

    # Implementações fallback (básicas)
    def get_token_count(text: str, model: str = "gpt-3.5-turbo") -> int:
        """
        Contagem básica de tokens (fallback).

        Args:
            text: Texto para contar tokens
            model: Modelo (ignorado no modo fallback)

        Returns:
            Número estimado de tokens
        """
        if not text:
            return 0

        # Estimativa básica: ~0.75 tokens por palavra em português
        words = len(text.split())
        return max(1, int(words * 0.75))

    def get_token_count_with_model(text: str, model: str = "gpt-3.5-turbo") -> dict:
        """Versão detalhada da contagem (fallback)."""
        token_count = get_token_count(text, model)
        return {
            "token_count": token_count,
            "model": model,
            "method": "fallback_estimation",
            "character_count": len(text),
            "word_count": len(text.split()),
            "warnings": ["Funcionalidade básica - instale dependências completas"],
        }

    def list_available_models() -> list:
        """Lista modelos (fallback)."""
        return ["gpt-3.5-turbo", "gpt-4", "text-davinci-003"]

    def get_model_info(model: str) -> dict:
        """Informações do modelo (fallback)."""
        return {
            "name": model,
            "provider": "unknown",
            "max_tokens": 4096,
            "cost_per_1k_tokens": 0.002,
            "mode": "fallback",
        }

    def get_portuguese_models() -> list:
        """Modelos em português (fallback)."""
        return ["gpt-3.5-turbo", "gpt-4"]

    def get_multilingual_models() -> list:
        """Modelos multilíngues (fallback)."""
        return ["gpt-3.5-turbo", "gpt-4"]

    def is_model_available(model: str) -> bool:
        """Verifica se modelo está disponível (fallback)."""
        return model in list_available_models()

    def get_default_model() -> str:
        """Modelo padrão (fallback)."""
        return "gpt-3.5-turbo"

    def estimate_cost(token_count: int, model: str = "gpt-3.5-turbo") -> float:
        """Estima custo (fallback)."""
        return (token_count / 1000) * 0.002

    def register_custom_model(*args, **kwargs):
        """Registro de modelo customizado (fallback)."""
        warnings.warn("Funcionalidade não disponível no modo fallback")
        return None

    # Classe TokenService para compatibilidade (fallback)
    class TokenService:
        """Classe de serviço para tokens (fallback)."""
        
        @staticmethod
        def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
            return get_token_count(text, model)
        
        @staticmethod
        def get_model_info(model: str) -> dict:
            return get_model_info(model)

    _available_functions = [
        "get_token_count (fallback)",
        "get_token_count_with_model (fallback)",
        "list_available_models (fallback)",
        "get_model_info (fallback)",
        "get_portuguese_models (fallback)",
        "get_multilingual_models (fallback)",
        "is_model_available (fallback)",
        "get_default_model (fallback)",
        "estimate_cost (fallback)",
        "register_custom_model (fallback)",
        "get_user_agent",
        "get_sdk_info",
        "TokenService (fallback)",
    ]


# Informações do SDK
def get_sdk_info() -> dict:
    """
    Retorna informações completas do SDK.

    Returns:
        Dicionário com informações do SDK
    """
    return {
        "name": "AppServer SDK Python AI",
        "version": __version__,
        "author": __author__,
        "email": __email__,
        "description": __description__,
        "user_agent": get_user_agent(),
        "imports_successful": _import_success,
        "import_error": _import_error,
        "available_functions": _available_functions,
        "mode": "full" if _import_success else "fallback",
    }


# Funções para compatibilidade com versões antigas
def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """Alias para get_token_count (compatibilidade)."""
    warnings.warn(
        "count_tokens está deprecated. Use get_token_count.",
        DeprecationWarning,
        stacklevel=2,
    )
    return get_token_count(text, model)


# Exports principais
__all__ = [
    # Informações
    "__version__",
    "__author__",
    "__email__",
    "__description__",
    # Funções principais
    "get_token_count",
    "get_token_count_with_model",
    "list_available_models",
    "get_model_info",
    "get_portuguese_models",
    "get_multilingual_models",
    "is_model_available",
    "get_default_model",
    "estimate_cost",
    "register_custom_model",
    "get_user_agent",
    "get_sdk_info",
    # Classes
    "TokenService",
    # Compatibilidade
    "count_tokens",
]

# Adicionar enums se importados com sucesso
if _import_success:
    __all__.extend(
        [
            "ModelType",
            "ModelProvider",
            "ModelCapability",
            "TokenizationMethod",
            "SupportedLanguage",
        ]
    )
