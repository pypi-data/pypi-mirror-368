import logging

from codius.infrastructure.services.project_scanner_service import ProjectScannerService

logger = logging.getLogger(__name__)


def extract_project_metadata(state: dict) -> dict:
    from codius.di import container

    logger.debug("Running extract_project_metadata...")

    scanner = container.resolve(ProjectScannerService)

    metadata = scanner.extract_project_metadata()
    state["project_metadata"] = metadata

    logger.info("Extracted project metadata: %s", metadata)
    return state
