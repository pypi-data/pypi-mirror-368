from abc import ABC, abstractmethod


class LlmPort(ABC):
    @abstractmethod
    def call_prompt(self, prompt: str) -> str:
        """Send a prompt to the LLM and return natural language response."""
        pass

    @abstractmethod
    def call_chat(self, messages: list[dict]) -> str:
        """Send role-based messages to the LLM and return response."""
        pass
