from enum import Enum


class OllamaModel(str, Enum):
    GPT_OSS_20B = "gpt-oss:20b"
    GPT_OSS_120B = "gpt-oss:120b"
    LLAMA_31_8B = "llama3.1:8b-instruct-q4_K_M"
    MISTRAL_7B = "mistral:7b"
