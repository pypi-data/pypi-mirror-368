import logging
import time

import openai

from codius.domain.model.config.config import Config
from codius.domain.model.port.llm_port import LlmPort

logger = logging.getLogger(__name__)


class OpenAiLlmAdapter(LlmPort):
    def __init__(self, config: Config):
        config = config.llm.openai
        self.model = config.model
        self.api_key = config.resolve_api_key()
        if not self.api_key or not self.api_key.startswith("sk-"):
            logger.error("Missing or invalid OpenAI API key")
            raise RuntimeError("Anthropic API key is not set. Set it via config or OPENAI_API_KEY.")
        else:
            self.client = openai.OpenAI(api_key=self.api_key)

    def call_prompt(self, prompt: str) -> str:
        if not self.client:
            raise Exception("Missing or invalid OpenAI API key in .codius/config.yaml")

        prompt_len = len(prompt)
        token_estimate = prompt_len // 4  # Roughly: 1 token ≈ 4 chars

        logger.debug("Using OpenAI model: %s", self.model)
        logger.debug("Prompt length: %d chars (~%d tokens)", prompt_len,
                     token_estimate)

        start = time.time()

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0
        )

        duration = int((time.time() - start) * 1000)  # ms
        content = response.choices[0].message.content
        logger.debug("LLM response length: %d chars | Duration: %d ms", len(content), duration)
        return content

    def call_chat(self, messages: list[dict]) -> str:
        if not self.client:
            raise Exception("Missing or invalid OpenAI API key in .codius/config.yaml")

        total_input_chars = sum(len(m["content"]) for m in messages)
        token_estimate = total_input_chars // 4

        logger.debug("Using OpenAI model: %s", self.model)
        logger.debug("Estimated input: %d chars (~%d tokens)", total_input_chars,
                     token_estimate)

        start = time.time()

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.0
        )

        duration = int((time.time() - start) * 1000)
        content = response.choices[0].message.content
        logger.debug("LLM response length: %d chars | Duration: %d ms", len(content), duration)
        return content
