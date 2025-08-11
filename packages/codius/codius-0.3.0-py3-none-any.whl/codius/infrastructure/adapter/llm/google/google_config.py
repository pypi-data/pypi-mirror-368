from dataclasses import dataclass


@dataclass
class GoogleConfig:
    model: str
    api_key: str
