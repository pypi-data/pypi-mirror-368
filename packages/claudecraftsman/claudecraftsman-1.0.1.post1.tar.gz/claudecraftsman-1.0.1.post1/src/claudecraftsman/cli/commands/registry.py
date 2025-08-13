"""
Registry management commands for ClaudeCraftsman CLI.
"""

import typer
from rich.console import Console
from rich.prompt import Confirm

from claudecraftsman.core.config import get_config
from claudecraftsman.core.registry import RegistryManager

app = typer.Typer(help="Document registry management commands")
console = Console()


@app.command()
def sync() -> None:
    """Sync the document registry with the file system."""
    config = get_config()
    registry_manager = RegistryManager(config)

    console.print("[cyan]Syncing document registry...[/cyan]")

    # First validate existing registry
    is_valid, issues = registry_manager.validate_registry()
    if not is_valid:
        console.print("\n[yellow]Registry validation issues found:[/yellow]")
        for issue in issues:
            console.print(f"  • {issue}")

    # Then sync with file system
    added_count = registry_manager.sync_registry()

    if added_count > 0:
        console.print(f"\n[green]✓ Registry sync complete: {added_count} documents added[/green]")
    else:
        console.print("\n[green]✓ Registry is already up to date[/green]")


@app.command()
def validate() -> None:
    """Validate the document registry integrity."""
    config = get_config()
    registry_manager = RegistryManager(config)

    console.print("[cyan]Validating document registry...[/cyan]")

    is_valid, issues = registry_manager.validate_registry()

    if is_valid:
        console.print("\n[green]✓ Registry validation passed[/green]")
    else:
        console.print(f"\n[red]✗ Registry validation failed with {len(issues)} issues:[/red]")
        for issue in issues:
            console.print(f"  • {issue}")


@app.command()
def show():
    """Display the current registry in a formatted table."""
    config = get_config()
    registry_manager = RegistryManager(config)

    registry_manager.display_registry()


@app.command()
def archive(
    document_name: str = typer.Argument(..., help="Name of document to archive"),
    reason: str = typer.Option("Completed", help="Reason for archiving"),
):
    """Archive a completed document."""
    config = get_config()
    registry_manager = RegistryManager(config)

    # Confirm action
    if not Confirm.ask(f"Archive '{document_name}' with reason '{reason}'?"):
        console.print("[yellow]Archive cancelled[/yellow]")
        return

    if registry_manager.archive_document(document_name, reason):
        console.print(f"[green]✓ Document '{document_name}' archived successfully[/green]")
    else:
        console.print(f"[red]✗ Failed to archive '{document_name}'[/red]")


@app.command()
def fix_paths():
    """Fix incorrect paths in the registry (one-time migration)."""
    config = get_config()
    registry_manager = RegistryManager(config)

    console.print("[cyan]Fixing registry paths...[/cyan]")

    # Parse current registry
    active_docs, archived_docs = registry_manager.parse_registry()

    fixed_count = 0
    for doc in active_docs:
        # Fix paths that don't start with "current/"
        if (
            doc.location
            and not doc.location.startswith("current/")
            and not doc.location.startswith("archive/")
        ):
            old_location = doc.location
            doc.location = f"current/{doc.location}" if doc.location else "current"
            console.print(f"[yellow]Fixed path: {old_location} → {doc.location}[/yellow]")
            fixed_count += 1

    # Write updated registry
    if fixed_count > 0:
        registry_manager._write_registry(active_docs, archived_docs)
        console.print(f"\n[green]✓ Fixed {fixed_count} document paths[/green]")
    else:
        console.print("\n[green]✓ All paths are already correct[/green]")


@app.command()
def cleanup():
    """Archive all completed documents older than 7 days."""
    config = get_config()
    registry_manager = RegistryManager(config)

    console.print("[cyan]Checking for documents to archive...[/cyan]")

    # Get validation issues to find old complete documents
    _, issues = registry_manager.validate_registry()

    docs_to_archive = []
    for issue in issues:
        if "consider archiving" in issue:
            # Extract document name from issue message
            import re

            match = re.search(r"Document (\S+) is Complete", issue)
            if match:
                docs_to_archive.append(match.group(1))

    if not docs_to_archive:
        console.print("\n[green]No documents need archiving[/green]")
        return

    console.print(f"\n[yellow]Found {len(docs_to_archive)} documents to archive:[/yellow]")
    for doc in docs_to_archive:
        console.print(f"  • {doc}")

    if Confirm.ask("\nArchive these documents?"):
        archived_count = 0
        for doc in docs_to_archive:
            if registry_manager.archive_document(doc, "Auto-archived (>7 days old)"):
                console.print(f"[green]✓ Archived {doc}[/green]")
                archived_count += 1
            else:
                console.print(f"[red]✗ Failed to archive {doc}[/red]")

        console.print(f"\n[green]Archived {archived_count} documents[/green]")
    else:
        console.print("[yellow]Archive cancelled[/yellow]")


if __name__ == "__main__":
    app()
