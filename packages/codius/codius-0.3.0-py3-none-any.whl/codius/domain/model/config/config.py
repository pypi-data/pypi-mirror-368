from dataclasses import dataclass

from codius.domain.model.config.approval_mode import ApprovalMode
from codius.infrastructure.adapter.llm.llm_config import LlmConfig

DEFAULT_CONFIG = {
    "llm": {
        "provider": "openai",
        "openai": {
            "model": "gpt-4o",
            "api_key": "sk-... # Replace with your OpenAI API key"
        },
        "anthropic": {
            "model": "claude-3-opus",
            "api_key": "xyz-... # Replace with your Anthropic API key"
        },
        "ollama": {
            "base_url": "http://localhost:11434",
            "model": "gpt-oss:20b"
        }
    },
    "approval_mode": ApprovalMode.SUGGEST.value,
    "debug": False,
    "debug_llm": False,
    "log_level": "warning"
}


@dataclass
class Config:
    llm: LlmConfig
    approval_mode: ApprovalMode = ApprovalMode.SUGGEST
    debug: bool = False
    debug_llm: bool = False
    log_level: str = "info"
