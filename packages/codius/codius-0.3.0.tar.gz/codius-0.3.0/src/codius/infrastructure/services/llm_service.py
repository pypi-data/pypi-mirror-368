import logging
import re
import json

from codius.domain.model.config.config import Config
from codius.domain.model.port.llm_port import LlmPort
from codius.utils import print_highlighted

logger = logging.getLogger(__name__)


class LlmService:
    def __init__(self, llm_port: LlmPort, config: Config):
        self.llm = llm_port
        self.config = config

    def call_prompt(self, prompt: str) -> str:
        logger.debug("Calling LLM services with prompt...")
        if self.config.debug_llm:
            print_highlighted(prompt, title="📨 Prompt Sent to LLM")

        try:
            response = self.llm.call_prompt(prompt)
        except Exception as e:
            # Attempt to extract OpenAI-style error message
            message = str(e)
            try:
                # Some adapters may wrap the response string in the error
                if hasattr(e, "response") and hasattr(e.response, "text"):
                    error_json = json.loads(e.response.text)
                else:
                    error_json = json.loads(message)

                openai_msg = error_json.get("error", {}).get("message")
                if "Incorrect API key" in openai_msg:
                    raise RuntimeError(
                        "❌ OpenAI API authentication failed: Incorrect API key provided. "
                        "Check your API key in config or environment variables."
                    ) from e

                # Generic OpenAI API error
                raise RuntimeError(f"❌ OpenAI API error: {openai_msg}") from e

            except (ValueError, KeyError, AttributeError):
                # Fall back to generic error if parsing fails
                logger.error("Error while calling LLM: %s", e)
                raise RuntimeError(
                    "❌ Failed to call LLM service. Please try again later."
                ) from e

        if self.config.debug_llm:
            print_highlighted(response, title="🧠 LLM Response")

        return response

    def call_chat(self, messages: list[dict]) -> str:
        logger.debug("Calling LLM services with chat messages...")
        if self.config.debug_llm:
            for msg in messages:
                print_highlighted(msg["content"],
                                  title=f"📨 {msg['role'].title()} Message")

        response = self.llm.call_chat(messages)

        if self.config.debug_llm:
            print_highlighted(response, title="🧠 LLM Response")

        return response

    def try_extract_json(self, response: str) -> dict:
        """Try to parse a JSON object from a markdown-wrapped LLM response."""
        match = re.search(r"```(?:json)?\s*(.*?)```", response, re.DOTALL)
        json_text = match.group(1).strip() if match else response.strip()

        try:
            return json.loads(json_text)
        except json.JSONDecodeError as e:
            logger.warning("Failed to parse JSON from LLM response: %s", e)
            return {"error": "invalid_json", "raw": response}
