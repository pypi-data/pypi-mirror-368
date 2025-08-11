import logging
import yaml

from pathlib import Path
from codius.domain.model.config.config import Config, DEFAULT_CONFIG
from codius.domain.services.config_service import ConfigService

logger = logging.getLogger(__name__)


class ProjectInitializerService:
    def __init__(self, project_path: Path):
        self.project_path = project_path.resolve()
        self.metadata_dir = self.project_path / ".codius"
        self.config_file = self.metadata_dir / "config.yaml"

    def ensure_config_file_exists(self) -> None:
        if not self.config_file.exists():
            print("🛠 Project configuration not found. Creating .codius/config.yaml...")
            self.metadata_dir.mkdir(parents=True, exist_ok=True)
            with self.config_file.open("w") as f:
                yaml.dump(DEFAULT_CONFIG, f)
            print(f"✅ Created {self.config_file}. Please update your config before using the CLI.\n")
        else:
            print(f"📦 Using project config: {self.config_file}")

    def load_config(self) -> Config:
        with self.config_file.open("r") as f:
            raw_dict = yaml.safe_load(f) or {}
        config = ConfigService.parse_structured(raw_dict)
        return config
