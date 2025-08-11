from dataclasses import dataclass


@dataclass
class OllamaConfig:
    server_url: str
    model: str
