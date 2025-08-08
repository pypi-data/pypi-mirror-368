"""Módulo LLM do AppServer SDK."""

from __future__ import annotations

from src.appserver_sdk_python_ai.llm.core.enums import (
    HuggingFaceModelEnum,
    OpenAIModelEnum,
    TokenizerTypeEnum,
)
from src.appserver_sdk_python_ai.llm.service.token_service import (
    get_model_info,
    get_portuguese_models,
    get_token_count,
    get_token_count_with_model,
    is_model_registered,
    list_available_models,
    register_custom_model,
)

__all__ = [
    # Enums
    "HuggingFaceModelEnum",
    "OpenAIModelEnum",
    "TokenizerTypeEnum",
    # Funções principais
    "get_token_count",
    "get_token_count_with_model",
    "register_custom_model",
    "list_available_models",
    "get_model_info",
    "is_model_registered",
    "get_portuguese_models",
]
