from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout, HSplit, Window
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.layout.controls import FormattedTextControl
from datetime import datetime
from rich.console import Console

from codius.di import container
from codius.domain.services.session_service import SessionService
from codius.infrastructure.repository.session_repository import SessionRepository

console = Console()


def show_sessions_app():
    session_service = container.resolve(SessionService)
    session_repository = container.resolve(SessionRepository)

    sessions = sorted(session_repository.get_all(), key=lambda s: s.created_at, reverse=True)
    if not sessions:
        console.print("[bold yellow]⚠️ No saved sessions found.[/bold yellow]")
        return

    active_id = session_service.get_active_session_id()
    index = [0]

    def get_text():
        lines = []

        for i, s in enumerate(sessions):
            is_selected = i == index[0]
            is_active = s.id == active_id
            prefix = "❯" if is_selected else " "

            ts_source = (
                s.history.messages[0].timestamp
                if s.history.messages else s.created_at
            )
            ts = format_timestamp(ts_source)

            msg_count = len(s.history.messages)

            if s.state.summary:
                summary = s.state.summary.strip()
            elif s.history.messages:
                summary = "No summary"
            else:
                summary = "Empty session"

            summary = summary[:40] + "…" if len(summary) > 40 else summary

            # Add (active) tag if this is the current active session
            active_label = " (active)" if is_active else ""
            line = f"{prefix} {ts} · {msg_count} msgs · {summary}{active_label}"

            if is_selected:
                style = "fg:green bold"
            elif is_active:
                style = "fg:#888888"
            else:
                style = ""

            lines.append((style, line + "\n"))

        return FormattedText(lines)

    kb = KeyBindings()

    @kb.add("up")
    def _(event):
        index[0] = (index[0] - 1) % len(sessions)

    @kb.add("down")
    def _(event):
        index[0] = (index[0] + 1) % len(sessions)

    @kb.add("enter")
    def _(event):
        selected = sessions[index[0]]
        session_repository.save(selected)
        event.app.exit()
        # console.print(f"[bold green]✅ Resumed session:[/bold green] {selected.id}")

    @kb.add("escape", eager=True)
    @kb.add("q")
    def _(event):
        event.app.exit()

    console.print("[bold]Resume session[/bold]")
    console.print("press enter to resume · esc to cancel\n")

    app = Application(
        layout=Layout(
            HSplit([
                Window(FormattedTextControl(get_text), always_hide_cursor=True),
            ])
        ),
        key_bindings=kb,
        full_screen=False
    )

    app.run()


def format_timestamp(timestamp: str) -> str:
    try:
        dt = datetime.fromisoformat(timestamp)
        return dt.strftime("%-m/%-d/%y, %-I:%M %p")
    except Exception:
        return "–"
