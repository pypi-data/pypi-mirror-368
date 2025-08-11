from dataclasses import dataclass


@dataclass
class GroqConfig:
    model: str
    api_key: str
