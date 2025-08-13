"""
Migration command for transitioning from shell scripts to Python package.
"""

import typer
from rich.console import Console
from rich.table import Table

from claudecraftsman.compatibility import (
    check_compatibility,
    install_compatibility,
    remove_compatibility,
)
from claudecraftsman.migration import ClaudeCraftsmanMigrator

app = typer.Typer(help="Migration utilities")
console = Console()


@app.command()
def from_shell(
    skip_backup: bool = typer.Option(
        False, "--skip-backup", help="Skip creating backup of existing installation"
    ),
    auto_confirm: bool = typer.Option(False, "--yes", "-y", help="Auto-confirm all prompts"),
) -> None:
    """
    Migrate from shell-based ClaudeCraftsman to Python package.

    This command helps users transition from the old shell script
    implementation to the new Python package, preserving their data
    and cleaning up old installations.
    """
    migrator = ClaudeCraftsmanMigrator()
    success = migrator.run_migration(skip_backup=skip_backup, auto_confirm=auto_confirm)

    if not success:
        raise typer.Exit(1)


@app.command()
def check() -> None:
    """
    Check if migration from shell scripts is needed.

    Shows the current installation status and whether migration
    is required.
    """
    migrator = ClaudeCraftsmanMigrator()

    console.print("[cyan]Checking for shell-based installation...[/cyan]\n")

    if migrator.old_scripts_dir.exists():
        console.print("[yellow]📦 Shell-based installation found at:[/yellow]")
        console.print(f"   {migrator.old_scripts_dir}")
        console.print("\n[yellow]Migration recommended![/yellow]")
        console.print("Run: [cyan]claudecraftsman migrate from-shell[/cyan]")
    else:
        console.print("[green]✅ No shell-based installation found[/green]")
        console.print("You're using the Python version!")

    # Check for any shell script references in configs
    console.print("\n[cyan]Checking shell configurations...[/cyan]")

    found_refs = False
    for config_path in migrator.shell_configs:
        if config_path.exists():
            try:
                content = config_path.read_text()
                if ".claude/claudecraftsman/scripts" in content:
                    console.print(f"[yellow]⚠️  Found old references in {config_path.name}[/yellow]")
                    found_refs = True
            except Exception:
                pass

    if found_refs:
        console.print("\n[yellow]Old script references found in shell configs[/yellow]")
        console.print("Run: [cyan]claudecraftsman migrate from-shell[/cyan] to clean them up")
    else:
        console.print("[green]✅ Shell configurations are clean[/green]")


@app.command()
def install_compat() -> None:
    """
    Install backward compatibility layer for old shell commands.

    Creates shell script shims that forward old commands to the new
    Python CLI, helping with gradual migration.
    """
    success = install_compatibility()
    if not success:
        raise typer.Exit(1)


@app.command()
def check_compat() -> None:
    """
    Check which compatibility shims are installed.

    Shows the current status of the backward compatibility layer.
    """
    installed = check_compatibility()

    if not installed:
        console.print("[yellow]No compatibility shims installed[/yellow]")
        console.print("\nRun: [cyan]claudecraftsman migrate install-compat[/cyan] to install")
        return

    console.print("[cyan]Installed compatibility shims:[/cyan]\n")

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Old Command", style="yellow")
    table.add_column("Status", justify="center")
    table.add_column("Type")

    for shim in installed:
        if shim == "cc":
            table.add_row(shim, "[green]✓[/green]", "Shorthand")
        elif shim == "cc-migrate":
            table.add_row(shim, "[green]✓[/green]", "Helper")
        else:
            table.add_row(shim, "[green]✓[/green]", "Compatibility")

    console.print(table)
    console.print(f"\n[green]Total: {len(installed)} shims installed[/green]")


@app.command()
def remove_compat() -> None:
    """
    Remove backward compatibility layer.

    Removes all compatibility shims after you've migrated to
    the new Python commands.
    """
    from rich.prompt import Confirm

    installed = check_compatibility()

    if not installed:
        console.print("[yellow]No compatibility shims to remove[/yellow]")
        return

    console.print(f"[yellow]Found {len(installed)} compatibility shims[/yellow]")

    if not Confirm.ask("\nRemove all compatibility shims?"):
        console.print("[yellow]Removal cancelled[/yellow]")
        return

    success = remove_compatibility()
    if not success:
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
