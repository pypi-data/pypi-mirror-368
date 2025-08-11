from enum import Enum


class AnthropicModel(str, Enum):
    CLAUDE_OPUS = "claude-3-opus"
    CLAUDE_SONNET = "claude-3-sonnet"
    CLAUDE_HAIKU = "claude-3-haiku"
