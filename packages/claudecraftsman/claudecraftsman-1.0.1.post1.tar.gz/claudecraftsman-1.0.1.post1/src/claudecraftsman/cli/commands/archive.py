"""
Document archival commands for ClaudeCraftsman CLI.
"""

from datetime import datetime

import typer
from rich.console import Console
from rich.prompt import Confirm

from claudecraftsman.core.archival import DocumentArchiver
from claudecraftsman.core.config import get_config

app = typer.Typer(help="Document archival commands")
console = Console()


@app.command()
def scan(
    dry_run: bool = typer.Option(
        True, "--dry-run/--execute", help="Show what would be archived without actually archiving"
    ),
    age_override: int = typer.Option(
        None, "--age", help="Override the default age threshold (days)"
    ),
):
    """Scan for documents ready to be archived."""
    config = get_config()
    archiver = DocumentArchiver(config)

    # Override age threshold if specified
    if age_override is not None:
        original_age = archiver.archive_age_days
        archiver.archive_age_days = age_override
        console.print(
            f"[yellow]Using age threshold: {age_override} days (default: {original_age} days)[/yellow]\n"
        )

    console.print("[cyan]Scanning for documents to archive...[/cyan]")

    candidates = archiver.find_archival_candidates()

    if not candidates:
        console.print("[green]No documents need archiving[/green]")
        return

    console.print(f"\n[yellow]Found {len(candidates)} documents to archive:[/yellow]")
    for filepath, reason in candidates:
        console.print(f"  • {filepath.name}: {reason}")

    if not dry_run:
        if Confirm.ask("\nProceed with archival?"):
            archived_count = 0
            for filepath, reason in candidates:
                if archiver.archive_document(filepath, reason):
                    archived_count += 1

            console.print(f"\n[green]✓ Archived {archived_count} documents[/green]")
        else:
            console.print("[yellow]Archival cancelled[/yellow]")
    else:
        console.print("\n[cyan]Dry run - no documents were archived[/cyan]")


@app.command()
def auto(
    age_override: int = typer.Option(
        None, "--age", help="Override the default age threshold (days)"
    ),
):
    """Automatically archive all eligible documents."""
    config = get_config()
    archiver = DocumentArchiver(config)

    # Override age threshold if specified
    if age_override is not None:
        original_age = archiver.archive_age_days
        archiver.archive_age_days = age_override
        console.print(
            f"[yellow]Using age threshold: {age_override} days (default: {original_age} days)[/yellow]"
        )

    archived_count = archiver.auto_archive(dry_run=False)

    if archived_count == 0:
        console.print("[green]No documents needed archiving[/green]")


@app.command()
def manifest(date: str = typer.Argument(..., help="Archive date in YYYY-MM-DD format")):
    """Create or update archive manifest for a specific date."""
    config = get_config()
    archiver = DocumentArchiver(config)

    # Validate date format
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        console.print("[red]Error: Invalid date format. Use YYYY-MM-DD[/red]")
        raise typer.Exit(1)

    archiver.create_archive_manifest(date)


@app.command()
def status(filepath: str = typer.Argument(..., help="Document filename to check")):
    """Check the archival status of a specific document."""
    config = get_config()
    archiver = DocumentArchiver(config)

    # Find the document
    docs_dir = config.paths.docs_dir
    doc_path = None

    # Search in current directory and subdirectories
    for path in docs_dir.rglob(filepath):
        if path.is_file():
            doc_path = path
            break

    if not doc_path:
        console.print(f"[red]Document '{filepath}' not found[/red]")
        return

    # Check completion status
    is_complete = archiver.detect_completion_status(doc_path)
    age_days = archiver.get_document_age(doc_path)

    console.print(f"\n[cyan]Document Status: {doc_path.name}[/cyan]")
    console.print(f"  • Location: {doc_path.parent}")
    console.print(f"  • Complete: {'Yes' if is_complete else 'No'}")

    if age_days is not None:
        console.print(f"  • Age: {age_days} days")

        if is_complete:
            if age_days >= archiver.archive_age_days:
                console.print("  • [yellow]Ready for archival[/yellow]")
            else:
                days_until = archiver.archive_age_days - age_days
                console.print(f"  • [green]Will be archived in {days_until} days[/green]")
        else:
            console.print("  • [dim]Not eligible for archival (not complete)[/dim]")
    else:
        console.print("  • Age: Unknown")


@app.command()
def config():
    """Show archival configuration settings."""
    config = get_config()
    archiver = DocumentArchiver(config)

    console.print("[cyan]Archival Configuration[/cyan]")
    console.print(f"  • Archive age threshold: {archiver.archive_age_days} days")
    console.print(f"  • Archive directory: {archiver.archive_dir}")
    console.print(f"  • Docs directory: {archiver.docs_dir}")

    console.print("\n[cyan]Completion Detection Patterns[/cyan]")
    for pattern in archiver.completion_patterns[:5]:
        console.print(f"  • {pattern}")
    if len(archiver.completion_patterns) > 5:
        console.print(f"  • ... and {len(archiver.completion_patterns) - 5} more")


if __name__ == "__main__":
    app()
