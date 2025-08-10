"""Serviço para contagem de tokens com suporte a modelos customizados."""

from __future__ import annotations

from typing import Any

try:
    # Usar importações relativas
    from ..core.enums import (
        HuggingFaceModelEnum,
        OpenAIModelEnum,
        TokenizerTypeEnum,
    )
    from ..core.model_manager import TokenizerModelManager
except ImportError:
    # Fallback para importações absolutas se necessário
    from appserver_sdk_python_ai.llm.core.enums import (
        HuggingFaceModelEnum,
        OpenAIModelEnum,
        TokenizerTypeEnum,
    )
    from appserver_sdk_python_ai.llm.core.model_manager import TokenizerModelManager

# Instância global do gerenciador
_model_manager: TokenizerModelManager | None = None


def _get_model_manager() -> TokenizerModelManager:
    """Obtém instância do model manager (lazy loading)."""
    global _model_manager
    if _model_manager is None:
        _model_manager = TokenizerModelManager()
    return _model_manager


def get_token_count(text: str) -> int:
    """Conta tokens usando tokenizer padrão.

    Args:
        text: Texto para análise.

    Returns:
        Número de tokens.

    Raises:
        ValueError: Se texto for None.
    """
    if text is None:
        raise ValueError("Texto não pode ser None")

    if not text.strip():
        return 0

    # Usa GPT-4 como padrão (cl100k_base encoding)
    try:
        manager = _get_model_manager()
        result = manager.count_tokens(text, OpenAIModelEnum.GPT_4.value)
        return result["token_count"]
    except Exception:
        # Fallback simples se tiktoken não estiver disponível
        return max(1, len(text) // 4)


def get_token_count_with_model(
    text: str,
    model: str | OpenAIModelEnum | HuggingFaceModelEnum,
    max_tokens: int | None = None,
) -> dict[str, Any]:
    """Conta tokens com modelo específico.

    Args:
        text: Texto para análise.
        model: Modelo de tokenização.
        max_tokens: Limite máximo de tokens.

    Returns:
        Dicionário com resultado detalhado.

    Raises:
        ValueError: Se texto for None.
    """
    if text is None:
        raise ValueError("Texto não pode ser None")

    # Converte enum para string
    model_name = model.value if hasattr(model, "value") else str(model)

    try:
        manager = _get_model_manager()
        result = manager.count_tokens(text, model_name)
    except Exception as e:
        # Fallback em caso de erro
        token_count = max(1, len(text) // 4)
        result = {
            "token_count": token_count,
            "model": model_name,
            "type": "fallback",
            "max_tokens": None,
            "truncated": False,
            "text_preview": text[:100] + "..." if len(text) > 100 else text,
            "warning": f"Erro ao usar modelo '{model_name}': {e}. Usando fallback.",
        }

    # Aplica limite se especificado
    if max_tokens is not None:
        result["max_tokens"] = max_tokens
        result["truncated"] = result["token_count"] > max_tokens

    return result


def register_custom_model(
    name: str,
    tokenizer_type: TokenizerTypeEnum = TokenizerTypeEnum.CUSTOM,
    max_tokens: int | None = None,
    encoding: str | None = None,
    description: str | None = None,
) -> None:
    """Registra modelo customizado.

    Args:
        name: Nome único do modelo.
        tokenizer_type: Tipo de tokenizer.
        max_tokens: Limite de tokens.
        encoding: Encoding para modelos OpenAI.
        description: Descrição do modelo.

    Raises:
        ValueError: Se nome já estiver registrado.
    """
    manager = _get_model_manager()
    manager.register_custom_model(
        name=name,
        tokenizer_type=tokenizer_type,
        max_tokens=max_tokens,
        encoding=encoding,
        description=description,
    )


def list_available_models(tokenizer_type: TokenizerTypeEnum | None = None) -> list[str]:
    """Lista modelos disponíveis.

    Args:
        tokenizer_type: Filtro por tipo (opcional).

    Returns:
        Lista de nomes de modelos.
    """
    try:
        manager = _get_model_manager()
        return manager.list_models(tokenizer_type)
    except Exception:
        return []


def get_model_info(model_name: str) -> dict[str, Any] | None:
    """Obtém informações do modelo.

    Args:
        model_name: Nome do modelo.

    Returns:
        Informações do modelo ou None.
    """
    try:
        manager = _get_model_manager()
        model_info = manager.get_model_info(model_name)
        if model_info is None:
            return None

        return {
            "name": model_info.name,
            "type": model_info.type.value,
            "max_tokens": model_info.max_tokens,
            "encoding": model_info.encoding,
            "description": model_info.description,
        }
    except Exception:
        return None


def is_model_registered(model_name: str) -> bool:
    """Verifica se modelo está registrado.

    Args:
        model_name: Nome do modelo.

    Returns:
        True se registrado.
    """
    try:
        manager = _get_model_manager()
        return model_name in manager
    except Exception:
        return False


def get_portuguese_models() -> list[str]:
    """Lista modelos para português.

    Returns:
        Lista de modelos recomendados.
    """
    try:
        manager = _get_model_manager()
        return manager.get_portuguese_models()
    except Exception:
        return []


# Compatibilidade com versão anterior
try:
    TokenizerModel = OpenAIModelEnum  # Alias para compatibilidade
except NameError:
    pass  # Se OpenAIModelEnum não estiver disponível, ignora
