from dataclasses import dataclass
from typing import Optional

from codius.domain.model.config.llm_provider import LlmProvider
from codius.infrastructure.adapter.llm.anthropic.anthropic_config import AnthropicConfig
from codius.infrastructure.adapter.llm.google.google_config import GoogleConfig
from codius.infrastructure.adapter.llm.groq.groq_config import GroqConfig
from codius.infrastructure.adapter.llm.mistral.mistral_config import MistralConfig
from codius.infrastructure.adapter.llm.ollama.ollama_config import OllamaConfig
from codius.infrastructure.adapter.llm.openai.openai_config import OpenAiConfig


@dataclass
class LlmConfig:
    provider: LlmProvider
    openai: Optional[OpenAiConfig] = None
    anthropic: Optional[AnthropicConfig] = None
    google: Optional[GoogleConfig] = None
    mistral: Optional[MistralConfig] = None
    groq: Optional[GroqConfig] = None
    ollama: Optional[OllamaConfig] = None
