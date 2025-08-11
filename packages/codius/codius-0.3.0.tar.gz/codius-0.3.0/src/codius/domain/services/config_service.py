import yaml

from enum import Enum
from typing import Any

from codius.domain.model.config.anthropic.anthropic_llm_model import AnthropicModel
from codius.domain.model.config.approval_mode import ApprovalMode
from codius.domain.model.config.config import Config
from codius.domain.model.config.llm_provider import LlmProvider
from codius.domain.model.config.ollama.ollama_llm_model import OllamaModel
from codius.domain.model.config.openai.openai_llm_model import OpenAiModel

from codius.infrastructure.adapter.llm.anthropic.anthropic_config import AnthropicConfig
from codius.infrastructure.adapter.llm.llm_config import LlmConfig
from codius.infrastructure.adapter.llm.ollama.ollama_config import OllamaConfig
from codius.infrastructure.adapter.llm.openai.openai_config import OpenAiConfig
from codius.infrastructure.services.project_metadata_service import ProjectMetadataService


class ConfigService:
    def __init__(self, config: Config, metadata_service: ProjectMetadataService):
        self.config = config
        self.config_file = metadata_service.get_config_path()

    def set_config_value(self, key: str, value: Any):
        # Load raw YAML as dict
        with open(self.config_file, "r") as f:
            raw_config = yaml.safe_load(f) or {}

        # Traverse and set nested key
        keys = key.split(".")
        d = raw_config
        for part in keys[:-1]:
            d = d.setdefault(part, {})
        d[keys[-1]] = value.value if isinstance(value, Enum) else value

        # Write updated YAML back
        with open(self.config_file, "w") as f:
            yaml.dump(raw_config, f, sort_keys=False)

        # Update in-memory config object in-place
        updated_config = ConfigService.parse_structured(raw_config)
        self.config.llm = updated_config.llm
        self.config.approval_mode = updated_config.approval_mode
        self.config.debug = updated_config.debug
        self.config.debug_llm = updated_config.debug_llm
        self.config.log_level = updated_config.log_level

    @classmethod
    def parse_structured(cls, raw: dict) -> Config:
        llm_section = raw.get("llm", {})
        provider_str = llm_section.get("provider")
        try:
            provider = LlmProvider(provider_str)
        except ValueError:
            raise ValueError(f"Unsupported LLM provider: {provider_str}")

        llm_config = LlmConfig(provider=provider)

        anthropic = llm_section.get("anthropic", {})
        raw_model = anthropic.get("model") or "claude-3-opus"
        llm_config.anthropic = AnthropicConfig(
            model=AnthropicModel(raw_model),
            api_key=anthropic.get("api_key", "")
        )

        ollama = llm_section.get("ollama", {})
        raw_model = ollama.get("model") or OllamaModel.GPT_OSS_20B.value
        llm_config.ollama = OllamaConfig(
            model=OllamaModel(raw_model),
            server_url=ollama.get("server_url", "")
        )

        openai = llm_section.get("openai", {})
        raw_model = openai.get("model") or "gpt-4o"
        llm_config.openai = OpenAiConfig(
            model=OpenAiModel(raw_model),
            api_key=openai.get("api_key", "")
        )

        log_level = raw.get("log_level", "warning").lower()
        allowed_levels = {"debug", "info", "warning", "error", "critical"}
        if log_level not in allowed_levels:
            print(f"⚠️ Unknown log_level '{log_level}', falling back to 'warning'")
            log_level = "warning"

        approval_mode = ApprovalMode(raw.get("approval_mode", "suggest"))

        return Config(
            llm=llm_config,
            approval_mode=approval_mode,
            debug=raw.get("debug", False),
            debug_llm=raw.get("debug_llm", False),
            log_level=log_level,
        )
