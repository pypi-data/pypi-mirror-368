from enum import Enum


class OpenAiModel(str, Enum):
    GPT_4O = "gpt-4o"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_3_5 = "gpt-3.5-turbo"
