from pathlib import Path

from prompt_toolkit import PromptSession
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
from rich.text import Text

from codius.domain.model.config.approval_mode import ApprovalMode
from codius.domain.model.config.config import Config
from codius.domain.model.plan.steps.plan_step_type import PlanStepType
from codius.infrastructure.services.project_metadata_service import ProjectMetadataService

from codius.ui.apps.approval_app import show_approval_app


def preview(state: dict) -> dict:
    from codius.di import container

    config = container.resolve(Config)
    metadata_service = container.resolve(ProjectMetadataService)

    session_id = state.get('session_id')
    generated_dir = metadata_service.get_generated_path(session_id)
    project_root = Path(state["project_metadata"]["project_root"])

    console = Console()
    session = PromptSession()

    files_on_disk = list(generated_dir.rglob("*.cs"))
    deletions = [p for p in state.get("plan", []) if p["type"] == "delete_file"]

    console.print("[bold underline]The assistant proposes the following changes:[/bold underline]\n")

    # Show added/updated files
    for path in files_on_disk:
        content = path.read_text()
        rel_path = path.relative_to(generated_dir)
        syntax = Syntax(content, "csharp", theme="monokai", line_numbers=True)
        panel = Panel(syntax, title=f"[green]{rel_path}[/green]", border_style="green")
        console.print(panel)

    # Show deletions
    for item in deletions:
        file_path = project_root / item["path"]
        if file_path.exists():
            try:
                content = file_path.read_text()
                syntax = Syntax(content, "csharp", theme="monokai", line_numbers=True)
            except Exception:
                syntax = Text("(Unable to preview content)", style="dim")

            panel = Panel(
                syntax,
                title=f"[red]{item['path']}[/red]",
                border_style="red"
            )
            console.print(panel)
        else:
            console.print(Panel(
                Text("(File not found for preview)", style="dim"),
                title=f"[red]{file_path}[/red]",
                border_style="red"
            ))

    # Show warnings
    warnings = state.get("plan_warnings", [])
    if warnings:
        console.print()
        for warning in warnings:
            console.print(f"{warning}")

    # Abort only if there are no changes AND no warnings
    if not files_on_disk and not deletions:
        # No need to ask user to approve nothing
        state["approval"] = "abort"
        return state

    has_deletions = any(
        PlanStepType.is_destructive(item.get("type"))
        for item in state.get("plan", [])
    )

    if config.approval_mode == ApprovalMode.AUTO:
        if has_deletions:
            console.print("[yellow]⚠️ Destructive change detected. Approval is required.[/yellow]")
        else:
            state["approval"] = "apply"
            return state

    # Manual approval path
    console.print("\nWould you like to apply these changes?")
    console.print("\nUse ↑/↓ to select an action, then press Enter:\n")
    response = show_approval_app()

    if response in {"yes", "y", "apply"}:
        state["approval"] = "apply"
    elif response in {"no", "n", "abort"}:
        state["approval"] = "abort"
    elif response in {"change", "revise"}:
        console.print("Please describe what you'd like to change:")
        feedback = session.prompt("> ")
        state["approval"] = "revise"
        state["revision_feedback"] = feedback
    else:
        console.print("[red]Invalid choice. Please type yes, no, or change.[/red]")
        return preview(state)

    return state
