"""
Main CLI application for ClaudeCraftsman.

This module defines the main Typer application and command structure.
"""

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from claudecraftsman import __version__
from claudecraftsman.core.config import get_config

# Create the main Typer app
app = typer.Typer(
    name="claudecraftsman",
    help="🛠️ ClaudeCraftsman: Artisanal development framework for Claude Code\n\n"
    "Transform your development workflow with craftsman-quality standards,\n"
    "thoughtful automation, and seamless Claude Code integration.",
    add_completion=True,
    rich_markup_mode="rich",
    pretty_exceptions_enable=True,
    pretty_exceptions_show_locals=False,
)

console = Console()


def version_callback(value: bool) -> None:
    """Display version information."""
    if value:
        import platform

        console.print(f"[bold cyan]ClaudeCraftsman[/bold cyan] v{__version__}")
        console.print(f"[dim]Python {platform.python_version()} on {platform.system()}[/dim]")

        # Try to show git info if available
        try:
            import subprocess

            commit = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, check=False
            ).stdout.strip()
            branch = subprocess.run(
                ["git", "branch", "--show-current"], capture_output=True, text=True, check=False
            ).stdout.strip()
            if commit and branch:
                console.print(f"[dim]Git: {branch}@{commit}[/dim]")
        except:
            pass

        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version and exit",
        callback=version_callback,
        is_eager=True,
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Enable debug output",
        envvar="CLAUDECRAFTSMAN_DEBUG",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        help="Enable verbose output",
        envvar="CLAUDECRAFTSMAN_VERBOSE",
    ),
) -> None:
    """
    ClaudeCraftsman - Artisanal development framework for Claude Code.

    Transform your development workflow with craftsman-quality standards,
    thoughtful automation, and seamless Claude Code integration.
    """
    # Update config with CLI options
    config = get_config()
    if debug:
        config.debug = True
    if verbose:
        config.verbose = True


@app.command()
def status() -> None:
    """
    Show ClaudeCraftsman status and configuration.

    Displays current mode (development/production), paths, and framework status.
    """
    config = get_config()
    config.display_status()

    # Show additional status information
    console.print("\n[bold]Framework Components[/bold]")

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Component", style="white")
    table.add_column("Status", justify="center")
    table.add_column("Path", style="dim")

    # Check framework components
    components = [
        ("Framework Core", config.paths.framework_file),
        ("Agents", config.paths.agents_dir),
        ("Commands", config.paths.commands_dir),
        ("Documentation", config.paths.docs_dir),
        ("Context", config.paths.context_dir),
    ]

    for name, path in components:
        if path.exists():
            status = "[green]✓[/green]"
        else:
            status = "[red]✗[/red]"
        table.add_row(name, status, str(path))

    console.print(table)


# Remove the old init command - it will be imported from commands/init.py


@app.command()
def install(
    global_install: bool = typer.Option(
        True,
        "--global/--local",
        help="Install globally (default) or locally",
    ),
) -> None:
    """
    Install ClaudeCraftsman framework files.

    Copies framework files (agents, commands, templates) to the appropriate
    location for use in projects.
    """
    config = get_config()

    if config.dev_mode:
        console.print(
            "[yellow]Running in development mode. "
            "Framework files are already available locally.[/yellow]"
        )
        return

    console.print("[cyan]Installing ClaudeCraftsman framework files...[/cyan]")

    # TODO: Implement actual installation logic
    # This will copy framework files from the package to ~/.claude/claudecraftsman/

    console.print("[green]✓ Installation complete![/green]")


@app.command()
def quality(
    phase: str = typer.Option(
        "general",
        "--phase",
        "-p",
        help="Quality validation phase",
    ),
    output: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Save report to file",
    ),
) -> None:
    """
    Run quality gates validation.

    Executes the 8-step quality validation cycle and reports results.
    """
    from claudecraftsman.core.validation import QualityGates

    console.print(f"[cyan]Running quality validation for phase: {phase}[/cyan]")

    gates = QualityGates()
    report = gates.validate_all(phase)

    if output:
        # Save report to file
        output.write_text(gates.create_quality_checklist())
        console.print(f"[green]✓ Quality checklist saved to {output}[/green]")

    # Exit with appropriate code
    if not report.overall_passed:
        raise typer.Exit(1)


# Import and add sub-commands
from claudecraftsman.cli.commands import (
    archive,
    health,
    hook,
    init,
    migrate,
    registry,
    state,
    test,
    validate,
)

# Register the init command directly (not as a sub-command)
app.command(name="init")(init.init_project)

app.add_typer(state.app, name="state", help="State management commands")
app.add_typer(validate.app, name="validate", help="Quality validation commands")
app.add_typer(registry.app, name="registry", help="Document registry management")
app.add_typer(archive.app, name="archive", help="Document archival commands")
app.add_typer(hook.app, name="hook", help="Claude Code hook configuration")
app.add_typer(migrate.app, name="migrate", help="Migration utilities")
app.add_typer(health.app, name="health", help="Framework health monitoring")
app.add_typer(test.app, name="test", help="Framework testing utilities")


if __name__ == "__main__":
    app()
