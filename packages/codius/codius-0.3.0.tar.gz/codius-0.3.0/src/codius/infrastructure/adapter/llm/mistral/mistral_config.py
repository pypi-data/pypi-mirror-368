from dataclasses import dataclass


@dataclass
class MistralConfig:
    model: str
    api_key: str
