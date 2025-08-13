"""
State management commands for ClaudeCraftsman CLI.

Replaces framework-state-update.sh functionality.
"""

import typer
from rich.console import Console

from claudecraftsman.core.registry import RegistryManager
from claudecraftsman.core.state import StateManager

app = typer.Typer(name="state", help="State management commands")
console = Console()


@app.command("document-created")
def document_created(
    filename: str = typer.Argument(..., help="Document filename"),
    doc_type: str = typer.Argument(..., help="Document type (e.g., PRD, SPEC)"),
    location: str = typer.Argument(..., help="Location relative to .claude/"),
    purpose: str = typer.Argument(..., help="Purpose of the document"),
) -> None:
    """
    Record creation of a new document.

    Updates the document registry and logs progress.
    """
    state_manager = StateManager()

    if state_manager.document_created(filename, doc_type, location, purpose):
        console.print(f"[green]✓ Document '{filename}' recorded successfully[/green]")
        console.print("[yellow]💡 Remember to commit these state changes to git[/yellow]")
    else:
        console.print(f"[red]✗ Failed to record document '{filename}'[/red]")
        raise typer.Exit(1)


@app.command("document-completed")
def document_completed(
    filename: str = typer.Argument(..., help="Document filename to mark complete"),
) -> None:
    """
    Mark a document as completed.

    Updates the registry status and may trigger archiving.
    """
    state_manager = StateManager()

    if state_manager.document_completed(filename):
        console.print(f"[green]✓ Document '{filename}' marked as complete[/green]")
        console.print("[yellow]💡 Remember to commit these state changes to git[/yellow]")
    else:
        console.print(f"[red]✗ Failed to update document '{filename}'[/red]")
        raise typer.Exit(1)


@app.command("phase-started")
def phase_started(
    phase: str = typer.Argument(..., help="Phase name"),
    agent: str = typer.Argument(..., help="Agent starting the phase"),
    description: str | None = typer.Argument(None, help="Phase description"),
) -> None:
    """
    Record the start of a new workflow phase.

    Updates workflow state and progress log.
    """
    state_manager = StateManager()

    if state_manager.phase_started(phase, agent, description):
        console.print(f"[green]✓ Phase '{phase}' started by {agent}[/green]")
        console.print("[yellow]💡 Remember to commit these state changes to git[/yellow]")
    else:
        console.print("[red]✗ Failed to record phase start[/red]")
        raise typer.Exit(1)


@app.command("phase-completed")
def phase_completed(
    phase: str = typer.Argument(..., help="Phase name"),
    agent: str = typer.Argument(..., help="Agent completing the phase"),
    description: str | None = typer.Argument(None, help="Completion description"),
) -> None:
    """
    Record the completion of a workflow phase.

    Updates workflow state and progress log.
    """
    state_manager = StateManager()

    if state_manager.phase_completed(phase, agent, description):
        console.print(f"[green]✓ Phase '{phase}' completed by {agent}[/green]")
        console.print("[yellow]💡 Remember to commit these state changes to git[/yellow]")
    else:
        console.print("[red]✗ Failed to record phase completion[/red]")
        raise typer.Exit(1)


@app.command("handoff")
def handoff(
    from_agent: str = typer.Argument(..., help="Agent handing off work"),
    to_agent: str = typer.Argument(..., help="Agent receiving work"),
    context: str = typer.Argument(..., help="Handoff context description"),
) -> None:
    """
    Record a handoff between agents.

    Updates handoff log and workflow state.
    """
    state_manager = StateManager()

    if state_manager.handoff(from_agent, to_agent, context):
        console.print(f"[green]✓ Handoff from {from_agent} to {to_agent} recorded[/green]")
        console.print("[yellow]💡 Remember to commit these state changes to git[/yellow]")
    else:
        console.print("[red]✗ Failed to record handoff[/red]")
        raise typer.Exit(1)


@app.command("show")
def show_state(
    workflow: bool = typer.Option(
        False,
        "--workflow",
        "-w",
        help="Show workflow state",
    ),
    handoffs: bool = typer.Option(
        False,
        "--handoffs",
        "-h",
        help="Show handoff log",
    ),
    context: bool = typer.Option(
        False,
        "--context",
        "-c",
        help="Show project context",
    ),
) -> None:
    """
    Display current state information.

    Shows workflow state, handoff log, or project context.
    """
    state_manager = StateManager()

    if not any([workflow, handoffs, context]):
        # Default to showing workflow state
        workflow = True

    if workflow:
        console.print("\n[bold]Workflow State[/bold]")
        state = state_manager.read_workflow_state()
        if state:
            console.print(f"Project: {state.project}")
            console.print(f"Current Phase: {state.current_phase}")
            console.print(f"Status: {state.status}")
            console.print("\nPhases:")
            for phase in state.phases:
                status_icon = {
                    "pending": "⏳",
                    "in_progress": "🔄",
                    "completed": "✅",
                    "blocked": "🚧",
                }.get(phase.status, "❓")
                console.print(f"  {status_icon} {phase.name} - {phase.status}")
                if phase.agent:
                    console.print(f"     Agent: {phase.agent}")
        else:
            console.print("[yellow]No active workflow state[/yellow]")

    if handoffs and state_manager.handoff_log_file.exists():
        console.print("\n[bold]Recent Handoffs[/bold]")
        content = state_manager.handoff_log_file.read_text()
        # Show last 5 handoffs
        handoff_sections = content.split("## Handoff:")
        for handoff in handoff_sections[-5:]:
            if handoff.strip():
                console.print(f"\n## Handoff:{handoff[:200]}...")

    if context and state_manager.context_file.exists():
        console.print("\n[bold]Project Context[/bold]")
        content = state_manager.context_file.read_text()
        console.print(content[:500] + "..." if len(content) > 500 else content)


@app.command("archive")
def archive_document(
    filename: str = typer.Argument(..., help="Document filename to archive"),
    reason: str = typer.Argument("Superseded", help="Reason for archiving"),
) -> None:
    """
    Archive a document with reason.

    Moves the document to the archive directory and updates the registry.
    """
    registry_manager = RegistryManager()

    if registry_manager.archive_document(filename, reason):
        console.print(f"[green]✓ Document '{filename}' archived successfully[/green]")
        console.print(f"[yellow]💡 Reason: {reason}[/yellow]")
        console.print("[yellow]💡 Remember to commit these changes to git[/yellow]")
    else:
        console.print(f"[red]✗ Failed to archive document '{filename}'[/red]")
        raise typer.Exit(1)
