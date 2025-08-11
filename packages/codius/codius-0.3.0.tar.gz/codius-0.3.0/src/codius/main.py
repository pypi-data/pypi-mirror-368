import argparse

from pathlib import Path

from codius.di import register_services, container
from codius.ui.assistant import run_assistant

from codius.domain.services.session_service import SessionService
from codius.infrastructure.services.logging_service import LoggingService
from codius.infrastructure.services.project_initializer_service import ProjectInitializerService
from codius.version import __version__


def main():
    parser = argparse.ArgumentParser(prog="codius")

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show the version number and exit",
    )

    parser.add_argument(
        "path",
        nargs="?",
        type=Path,
        default=Path.cwd(),
        help="(Optional) Path to the target OpenDDD.NET project directory"
    )

    args = parser.parse_args()

    # Load config
    project_initializer = ProjectInitializerService(project_path=args.path)
    project_initializer.ensure_config_file_exists()
    config = project_initializer.load_config()

    # Register dependencies with container
    register_services(config=config, args=args)

    # Initialize logging
    logging_service = container.resolve(LoggingService)
    logging_service.configure()

    # Start new session, if current is old or don't exist
    session_service = container.resolve(SessionService)
    session = session_service.get_or_create_active_session()
    if session and session.should_be_replaced():
        session = session_service.create_and_activate_session()
        print(f"🆕 Started new session: {session.id}")

    # Run the assistant
    run_assistant()


if __name__ == "__main__":
    main()
