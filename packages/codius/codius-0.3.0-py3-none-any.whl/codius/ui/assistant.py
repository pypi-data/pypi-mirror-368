from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.key_binding import KeyBindings
from rich.console import Console
from rich.panel import Panel

from codius.di import container
from codius.domain.model.config.config import Config
from codius.domain.services.session_service import SessionService
from codius.infrastructure.repository.session_repository import SessionRepository
from codius.infrastructure.services.graph_service import GraphService

from codius.infrastructure.services.project_metadata_service import ProjectMetadataService
from codius.ui.commands.slash_commands import SLASH_COMMANDS, handle_slash_command
from codius.version import __version__

console = Console()
slash_completer = WordCompleter(SLASH_COMMANDS.keys(), sentence=True)
bindings = KeyBindings()


@bindings.add("c-j")
def _(event):
    event.current_buffer.insert_text("\n")


def render_header():
    version = __version__
    console.print(
        Panel.fit(
            f"● [bold cyan]Codius Coding Assistant[/bold cyan] [dim]({version})[/dim]",
            padding=(0, 2),
            border_style="cyan",
        )
    )


def render_session_info():
    session_service = container.resolve(SessionService)
    project_metadata_service = container.resolve(ProjectMetadataService)

    session = session_service.get_or_create_active_session()

    project_root = project_metadata_service.get_project_root().resolve()

    config = container.resolve(Config)
    provider = config.llm.provider.value
    model = getattr(config.llm, provider).model.value
    approval_mode = config.approval_mode
    log_level = config.log_level

    console.print(Panel.fit(
        f"[bold]Session:[/bold] {session.id}\n"
        f"[bold]Project Path:[/bold] {project_root}\n"
        f"[bold]Provider:[/bold] {provider}\n"
        f"[bold]Model:[/bold] {model}\n"
        f"[bold]Log level:[/bold] {log_level}\n"
        f"[bold]Approval:[/bold] {approval_mode.value}",
        border_style="green",
    ))


def render_assistant_message(message: str):
    console.print(Panel.fit(
        message,
        title="[cyan]Assistant",
        border_style="cyan",
        padding=(1, 2),
    ))


def run_assistant():
    session_service = container.resolve(SessionService)
    session_repository = container.resolve(SessionRepository)
    graph_service = container.resolve(GraphService)

    render_header()
    render_session_info()
    console.print(Panel.fit("[dim]Type your modeling request or use slash-commands like /diff[/dim]"))

    prompt_session = PromptSession(completer=slash_completer, key_bindings=bindings)

    console.print()
    while True:
        try:
            user_input = prompt_session.prompt("> ")

            if user_input.strip().lower() in {"exit", "quit"}:
                console.print("[dim]Goodbye![/dim] 👋")
                break

            if not user_input.strip():
                continue

            # Handle slash-commands
            if user_input.startswith("/"):
                command = user_input.strip().split()[0]
                if command in SLASH_COMMANDS:
                    console.print(
                        f"[bold yellow]Running command:[/bold yellow] {command}")
                    handle_slash_command(command)
                    render_session_info()
                else:
                    console.print(f"[red]Unknown command:[/red] {command}")
                continue

            # Get active session
            session = session_service.get_active_session()

            # Run REPL cycle
            session = graph_service.run_repl_cycle(session, user_input)

            # Save session
            session_repository.save(session)

            # Render final message
            render_assistant_message(session.history.latest().content)

        except KeyboardInterrupt:
            console.print("\n[dim]Exited with Ctrl+C[/dim]")
            break
