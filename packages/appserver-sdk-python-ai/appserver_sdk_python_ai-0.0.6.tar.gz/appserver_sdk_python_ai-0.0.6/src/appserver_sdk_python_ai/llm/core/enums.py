"""Enumerações para modelos de tokenização."""

from __future__ import annotations

from enum import Enum


class TokenizerTypeEnum(Enum):
    """Tipos de tokenizadores disponíveis."""

    OPENAI = "openai"
    HUGGINGFACE = "huggingface"
    CUSTOM = "custom"
    DEFAULT = "default"


class OpenAIModelEnum(Enum):
    """Modelos OpenAI disponíveis."""

    GPT_4 = "gpt-4"
    GPT_4O = "gpt-4o"
    GPT_3_5_TURBO = "gpt-3.5-turbo"

    def get_max_tokens(self) -> int:
        """Retorna limite máximo de tokens."""
        limits = {
            "gpt-4": 8192,
            "gpt-4o": 128000,
            "gpt-3.5-turbo": 4096,
        }
        return limits.get(self.value, 4096)

    def get_encoding_name(self) -> str:
        """Retorna nome do encoding."""
        return "cl100k_base"


class HuggingFaceModelEnum(Enum):
    """Modelos HuggingFace disponíveis."""

    BERT_BASE = "bert-base-uncased"
    ROBERTA_BASE = "roberta-base"

    def get_max_sequence_length(self) -> int:
        """Retorna comprimento máximo da sequência."""
        return 512

    @classmethod
    def get_portuguese_models(cls) -> list[HuggingFaceModelEnum]:
        """Retorna modelos adequados para português."""
        return [cls.BERT_BASE]
