import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class OpenAiConfig:
    model: str = "gpt-4o"
    api_key: Optional[str] = None

    def resolve_api_key(self):
        return self.api_key or os.getenv("OPENAI_API_KEY")
