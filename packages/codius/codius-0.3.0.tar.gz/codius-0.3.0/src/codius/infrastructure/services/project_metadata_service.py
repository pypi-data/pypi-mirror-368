from pathlib import Path
import shutil
import logging

logger = logging.getLogger(__name__)


class ProjectMetadataService:
    def __init__(self, project_path: Path):
        self.project_path = project_path.resolve()
        self.metadata_root = self.project_path / ".codius"

    def get_project_root(self) -> Path:
        """Returns the root path of the current project."""
        return self.project_path

    def get_config_path(self) -> Path:
        """Returns the full path to the global config.yaml."""
        return self.metadata_root / "config.yaml"

    def get_sessions_path(self) -> Path:
        """Returns the path to the sessions directory (.codius/sessions)."""
        return self.metadata_root / "sessions"

    def get_session_path(self, session_id: str) -> Path:
        return self.get_sessions_path() / session_id

    def get_generated_path(self, session_id: str) -> Path:
        """Returns the path to the generated/ directory for the given session."""
        return self.get_session_path(session_id) / "generated"

    def clear_generated_files(self, session_id: str):
        """Deletes and recreates the generated/ directory for the given session."""
        generated_dir = self.get_generated_path(session_id)

        if generated_dir.exists():
            try:
                shutil.rmtree(generated_dir)
                logger.info("Deleted generated directory: %s", generated_dir)
            except Exception as e:
                logger.warning("Failed to delete generated directory: %s", e)

        try:
            generated_dir.mkdir(parents=True, exist_ok=True)
            logger.info("Recreated generated directory: %s", generated_dir)
        except Exception as e:
            logger.error("Failed to recreate generated directory: %s", e)
