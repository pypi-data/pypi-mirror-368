"""Gerenciador centralizado para modelos de tokenização."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.appserver_sdk_python_ai.llm.core.enums import (
    HuggingFaceModelEnum,
    OpenAIModelEnum,
    TokenizerTypeEnum,
)


@dataclass
class ModelInfo:
    """Informações sobre um modelo de tokenização."""

    name: str
    type: TokenizerTypeEnum
    max_tokens: int | None = None
    encoding: str | None = None
    description: str | None = None


class TokenizerModelManager:
    """Gerenciador centralizado para modelos de tokenização."""

    def __init__(self) -> None:
        """Inicializa o gerenciador com modelos pré-definidos e cache."""
        self._models: dict[str, ModelInfo] = {}
        self._tokenizer_cache: dict[str, Any] = {}
        self._load_predefined_models()

    def _load_predefined_models(self) -> None:
        """Carrega modelos pré-definidos."""
        # Modelos OpenAI
        for model in OpenAIModelEnum:
            self._models[model.value] = ModelInfo(
                name=model.value,
                type=TokenizerTypeEnum.OPENAI,
                max_tokens=model.get_max_tokens(),
                encoding=model.get_encoding_name(),
                description=f"Modelo OpenAI: {model.value}",
            )

        # Modelos HuggingFace
        for model in HuggingFaceModelEnum:
            self._models[model.value] = ModelInfo(
                name=model.value,
                type=TokenizerTypeEnum.HUGGINGFACE,
                max_tokens=model.get_max_sequence_length(),
                description=f"Modelo HuggingFace: {model.value}",
            )

    def _get_openai_tokenizer(self, encoding_name: str) -> Any:
        """Carrega e cacheia tokenizer OpenAI."""
        if encoding_name in self._tokenizer_cache:
            return self._tokenizer_cache[encoding_name]

        try:
            import tiktoken  # type: ignore

            encoding = tiktoken.get_encoding(encoding_name)
            self._tokenizer_cache[encoding_name] = encoding
            return encoding
        except ImportError as e:
            raise ImportError(
                "tiktoken não está instalado. Use: pip install tiktoken"
            ) from e

    def _get_huggingface_tokenizer(self, model_name: str) -> Any:
        """Carrega e cacheia tokenizer HuggingFace."""
        if model_name in self._tokenizer_cache:
            return self._tokenizer_cache[model_name]

        try:
            from transformers import AutoTokenizer  # type: ignore

            tokenizer = AutoTokenizer.from_pretrained(model_name)
            self._tokenizer_cache[model_name] = tokenizer
            return tokenizer
        except ImportError as e:
            raise ImportError(
                "transformers não está instalado. Use: pip install transformers"
            ) from e

    def register_custom_model(
        self,
        name: str,
        tokenizer_type: TokenizerTypeEnum = TokenizerTypeEnum.CUSTOM,
        max_tokens: int | None = None,
        encoding: str | None = None,
        description: str | None = None,
    ) -> None:
        """Registra um modelo customizado."""
        if name in self._models:
            raise ValueError(f"Modelo '{name}' já registrado")

        self._models[name] = ModelInfo(
            name=name,
            type=tokenizer_type,
            max_tokens=max_tokens,
            encoding=encoding,
            description=description or f"Modelo customizado: {name}",
        )

    def get_model_info(self, model_name: str) -> ModelInfo | None:
        """Retorna informações do modelo."""
        return self._models.get(model_name)

    def is_model_registered(self, model_name: str) -> bool:
        """Verifica se modelo está registrado."""
        return model_name in self._models

    def list_models(self, tokenizer_type: TokenizerTypeEnum | None = None) -> list[str]:
        """Lista modelos registrados."""
        if tokenizer_type is None:
            return list(self._models.keys())

        return [
            name for name, info in self._models.items() if info.type == tokenizer_type
        ]

    def count_tokens(self, text: str, model_name: str) -> dict[str, Any]:
        """Conta tokens usando o modelo especificado."""
        if text is None:
            raise ValueError("Texto não pode ser None")

        if not text.strip():
            return self._create_empty_result(model_name)

        model_info = self.get_model_info(model_name)
        if model_info is None:
            return self._count_tokens_custom(text, model_name)

        try:
            token_count = self._count_tokens_by_type(text, model_info)
            return self._create_result(text, token_count, model_info)
        except (ImportError, AttributeError, ValueError) as e:
            return self._count_tokens_fallback(text, model_name, str(e))

    def _count_tokens_by_type(self, text: str, model_info: ModelInfo) -> int:
        """Conta tokens baseado no tipo."""
        if model_info.type == TokenizerTypeEnum.OPENAI:
            return self._count_tokens_openai(text, model_info)
        elif model_info.type == TokenizerTypeEnum.HUGGINGFACE:
            return self._count_tokens_huggingface(text, model_info)
        else:
            return self._count_tokens_default(text)

    def _count_tokens_openai(self, text: str, model_info: ModelInfo) -> int:
        """Conta tokens OpenAI."""
        encoding = self._get_openai_tokenizer(model_info.encoding or "cl100k_base")
        return len(encoding.encode(text))

    def _count_tokens_huggingface(self, text: str, model_info: ModelInfo) -> int:
        """Conta tokens HuggingFace."""
        tokenizer = self._get_huggingface_tokenizer(model_info.name)
        return len(tokenizer.encode(text, add_special_tokens=True))

    def _count_tokens_default(self, text: str) -> int:
        """Conta tokens usando método padrão."""
        try:
            encoding = self._get_openai_tokenizer("cl100k_base")
            return len(encoding.encode(text))
        except ImportError:
            # Fallback: ~4 caracteres por token
            return max(1, len(text) // 4)

    def _count_tokens_custom(self, text: str, model_name: str) -> dict[str, Any]:
        """Conta tokens para modelo não registrado."""
        token_count = self._count_tokens_default(text)
        return {
            "token_count": token_count,
            "model": model_name,
            "type": TokenizerTypeEnum.CUSTOM.value,
            "max_tokens": None,
            "truncated": False,
            "text_preview": self._get_text_preview(text),
            "warning": f"Modelo '{model_name}' não registrado. Usando padrão.",
        }

    def _count_tokens_fallback(
        self, text: str, model_name: str, error: str
    ) -> dict[str, Any]:
        """Conta tokens com fallback."""
        token_count = self._count_tokens_default(text)
        return {
            "token_count": token_count,
            "model": f"{model_name} (fallback)",
            "type": TokenizerTypeEnum.DEFAULT.value,
            "max_tokens": None,
            "truncated": False,
            "text_preview": self._get_text_preview(text),
            "warning": f"Erro com '{model_name}': {error}. Usando padrão.",
        }

    def _create_result(
        self,
        text: str,
        token_count: int,
        model_info: ModelInfo,
        max_tokens: int | None = None,
    ) -> dict[str, Any]:
        """Cria resultado padronizado."""
        effective_max_tokens = max_tokens or model_info.max_tokens
        truncated = bool(effective_max_tokens and token_count > effective_max_tokens)

        return {
            "token_count": token_count,
            "model": model_info.name,
            "type": model_info.type.value,
            "max_tokens": effective_max_tokens,
            "truncated": truncated,
            "text_preview": self._get_text_preview(text),
            "description": model_info.description,
        }

    def _create_empty_result(self, model_name: str) -> dict[str, Any]:
        """Cria resultado para texto vazio."""
        model_info = self.get_model_info(model_name)
        return {
            "token_count": 0,
            "model": model_name,
            "type": model_info.type.value
            if model_info
            else TokenizerTypeEnum.CUSTOM.value,
            "max_tokens": model_info.max_tokens if model_info else None,
            "truncated": False,
            "text_preview": "",
        }

    def _get_text_preview(self, text: str) -> str:
        """Retorna prévia do texto."""
        return text[:100] + "..." if len(text) > 100 else text

    def get_openai_models(self) -> list[str]:
        """Lista modelos OpenAI."""
        return self.list_models(TokenizerTypeEnum.OPENAI)

    def get_huggingface_models(self) -> list[str]:
        """Lista modelos HuggingFace."""
        return self.list_models(TokenizerTypeEnum.HUGGINGFACE)

    def get_portuguese_models(self) -> list[str]:
        """Lista modelos para português."""
        return [model.value for model in HuggingFaceModelEnum.get_portuguese_models()]

    def __len__(self) -> int:
        """Número de modelos registrados."""
        return len(self._models)

    def __contains__(self, model_name: str) -> bool:
        """Verifica se modelo está registrado."""
        return self.is_model_registered(model_name)
