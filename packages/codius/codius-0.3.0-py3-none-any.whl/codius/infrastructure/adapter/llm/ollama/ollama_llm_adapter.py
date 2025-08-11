import logging, time, requests
from codius.domain.model.config.config import Config
from codius.domain.model.port.llm_port import LlmPort

logger = logging.getLogger(__name__)

class OllamaLlmAdapter(LlmPort):
    def __init__(self, config: Config):
        cfg = config.llm.ollama
        if not cfg:
            raise RuntimeError("Ollama config not found. Add `llm.ollama` in config.")
        self.base_url = cfg.server_url.rstrip("/")
        self.model = cfg.model
        self.options = {}
        self.session = requests.Session()
        self.timeout = 300

    def call_prompt(self, prompt: str) -> str:
        start = time.time()
        payload = {
            "model": self.model,
            "prompt": prompt,
            "options": self.options,
            "stream": False,
        }
        r = self.session.post(f"{self.base_url}/api/generate", json=payload, timeout=self.timeout)
        r.raise_for_status()
        data = r.json()
        content = data.get("response", "")
        logger.debug("Ollama /generate returned %d chars in %d ms", len(content), int((time.time()-start)*1000))
        return content

    def call_chat(self, messages: list[dict]) -> str:
        # messages format: [{"role": "system|user|assistant", "content": "..."}, ...]
        start = time.time()
        payload = {
            "model": self.model,
            "messages": messages,
            "options": self.options,
            "stream": False,
        }
        r = self.session.post(f"{self.base_url}/api/chat", json=payload, timeout=self.timeout)
        r.raise_for_status()
        data = r.json()
        # final message is in data["message"]["content"] per Ollama docs
        msg = (data.get("message") or {}).get("content", "")
        logger.debug("Ollama /chat returned %d chars in %d ms", len(msg), int((time.time()-start)*1000))
        return msg
