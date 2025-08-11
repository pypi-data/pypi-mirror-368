import json
from pathlib import Path
import logging

from codius.infrastructure.services.project_metadata_service import ProjectMetadataService

logger = logging.getLogger(__name__)


class ProjectScannerService:
    def __init__(self, project_metadata_service: ProjectMetadataService):
        self.project_root = project_metadata_service.get_project_root().resolve()
        self.source_path = self.project_root / "src"

    def extract_project_metadata(self) -> dict:
        solution_path = self._find_solution_file()
        project_name = solution_path.stem
        root_namespace = project_name

        metadata = {
            "project_name": project_name,
            "root_namespace": root_namespace,
            "project_root": str(self.project_root),
            "source_path": str(self.source_path),
            "domain_path": self._detect_layer_path("Domain"),
            "application_path": self._detect_layer_path("Application"),
            "infrastructure_path": self._detect_layer_path("Infrastructure"),
            "interchange_path": self._detect_layer_path("Interchange"),
            "tests_path": self._detect_tests_path(project_name),
        }

        provider_settings = self._detect_provider_settings()
        metadata.update(provider_settings)

        return metadata

    def _find_solution_file(self) -> Path:
        slns = list(self.source_path.glob("*.sln"))
        if not slns:
            raise FileNotFoundError("No .sln file found in src/")
        return slns[0]

    def _detect_tests_path(self, project_name: str) -> str:
        test_folder = self.source_path / f"{project_name}.Tests"
        if test_folder.exists():
            return str(test_folder)

        # Fallback: look for *.csproj with "test" in name
        for csproj in self.source_path.rglob("*.csproj"):
            if "test" in csproj.stem.lower():
                return str(csproj.parent)

        return "src/Tests"

    def _detect_layer_path(self, layer: str) -> str:
        project_name = self._find_solution_file().stem
        candidate = self.source_path / project_name / layer

        if candidate.is_dir() and not self._is_under_tests(candidate):
            return str(candidate)

        raise FileNotFoundError(
            f"No valid `{layer}` folder found under src/{project_name}/")

    def _is_under_tests(self, path: Path) -> bool:
        return any(part.lower() in ["tests", "test"] for part in path.parts)

    def _load_appsettings(self) -> dict:
        """
        Searches all project folders under /src that start with the solution name
        (e.g., Orientera, Orientera.API) for appsettings files.
        Excludes test folders.
        """
        project_name = self._find_solution_file().stem.lower()
        priority_names = [
            "appsettings.Development.json",
            "appsettings.Production.json",
            "appsettings.json"
        ]

        for name in priority_names:
            for candidate_dir in self.source_path.iterdir():
                dir_name = candidate_dir.name.lower()
                if not candidate_dir.is_dir():
                    continue
                if not dir_name.startswith(project_name):
                    continue
                if "test" in dir_name:
                    continue

                config_file = candidate_dir / name
                if config_file.exists():
                    try:
                        with open(config_file) as f:
                            return json.load(f)
                    except Exception as e:
                        logger.warning(f"Failed to parse {config_file}: {e}")

        return {}

    def _detect_provider_settings(self) -> dict:
        config = self._load_appsettings()

        open_ddd_config = config.get("OpenDDD", {})
        persistence = open_ddd_config.get("PersistenceProvider", "OpenDdd")
        database = open_ddd_config.get("DatabaseProvider", "Postgres")

        return {
            "persistence_provider": persistence,
            "database_provider": database
        }
