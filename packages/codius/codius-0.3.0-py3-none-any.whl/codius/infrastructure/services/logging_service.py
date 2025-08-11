import logging
import os
from typing import Optional

from codius.domain.model.config.config import Config


class LoggingService:
    def __init__(self, config: Config):
        self.log_level = config.log_level
        self.debug = config.debug

    def configure(self, level_override: Optional[str] = None):
        # Priority: explicit arg > config file > DEBUG env
        level_str = (
            level_override
            or self.log_level
            or ("debug" if self.debug or os.getenv("DEBUG") == "1" else "info")
        ).lower()

        level = self._parse_log_level(level_str)

        logging.basicConfig(
            level=level,
            format="[%(levelname)s] %(message)s",
            handlers=[logging.StreamHandler()]
        )

        self._suppress_external_noise()

    def _parse_log_level(self, level: str) -> int:
        levels = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
            "critical": logging.CRITICAL
        }
        return levels.get(level.lower(), logging.INFO)

    def _suppress_external_noise(self):
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)
        logging.getLogger("openai").setLevel(logging.WARNING)
        logging.getLogger("asyncio").setLevel(logging.WARNING)
