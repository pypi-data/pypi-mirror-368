import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class AnthropicConfig:
    model: str
    api_key: Optional[str] = None

    def resolve_api_key(self):
        return self.api_key or os.getenv("ANTHROPIC_API_KEY")
