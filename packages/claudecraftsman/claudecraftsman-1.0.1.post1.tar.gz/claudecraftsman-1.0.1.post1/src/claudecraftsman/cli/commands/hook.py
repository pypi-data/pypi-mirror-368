"""
Hook management commands for ClaudeCraftsman CLI.

Manages Claude Code hook configuration and testing.
"""

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.syntax import Syntax

from claudecraftsman.core.config import get_config
from claudecraftsman.hooks.config import generate_hooks_json, validate_hooks_json
from claudecraftsman.hooks.handlers import HookHandler

app = typer.Typer(name="hook", help="Claude Code hook configuration")
console = Console()


@app.command("generate")
def generate(
    output: Path = typer.Option(
        Path("hooks.json"),
        "--output",
        "-o",
        help="Output path for hooks.json",
    ),
    show: bool = typer.Option(
        False,
        "--show",
        "-s",
        help="Show generated configuration",
    ),
) -> None:
    """
    Generate hooks.json configuration for Claude Code.

    Creates a hooks.json file with ClaudeCraftsman integration hooks.
    """
    config = get_config()

    # Generate hooks configuration
    hooks_json = generate_hooks_json(output_path=output)

    if show:
        syntax = Syntax(hooks_json, "json", theme="monokai", line_numbers=True)
        console.print("\n[bold]Generated hooks.json:[/bold]")
        console.print(syntax)

    console.print(f"\n[green]✓ Hooks configuration saved to {output}[/green]")
    console.print("\n[yellow]To use these hooks:[/yellow]")
    console.print("1. Copy hooks.json to your Claude Code configuration directory")
    console.print("2. Restart Claude Code to load the hooks")
    console.print("3. The framework will automatically validate and update state")


@app.command("validate-config")
def validate_command(
    path: Path = typer.Argument(
        Path("hooks.json"),
        help="Path to hooks.json file",
    ),
) -> None:
    """
    Validate a hooks.json configuration file.

    Checks that the hooks configuration is valid and compatible.
    """
    if not path.exists():
        console.print(f"[red]File not found: {path}[/red]")
        raise typer.Exit(1)

    if validate_hooks_json(path):
        console.print("[green]✓ Hooks configuration is valid[/green]")
    else:
        console.print("[red]✗ Hooks configuration is invalid[/red]")
        raise typer.Exit(1)


@app.command("test")
def test_hook(
    event: str = typer.Argument(
        ...,
        help="Event type (preToolUse, postToolUse, userPromptSubmit, sessionStart)",
    ),
    data: str | None = typer.Option(
        None,
        "--data",
        "-d",
        help="JSON data for the event",
    ),
    tool: str | None = typer.Option(
        None,
        "--tool",
        "-t",
        help="Tool name (for tool use events)",
    ),
    prompt: str | None = typer.Option(
        None,
        "--prompt",
        "-p",
        help="User prompt (for prompt submit events)",
    ),
) -> None:
    """
    Test a hook handler with sample data.

    Useful for debugging hook behavior without Claude Code.
    """
    # Build event data
    event_data = {"event": event}

    if data:
        try:
            event_data.update(json.loads(data))
        except json.JSONDecodeError:
            console.print("[red]Invalid JSON data[/red]")
            raise typer.Exit(1)

    if tool:
        event_data["tool"] = tool

    if prompt:
        event_data["prompt"] = prompt

    # Create handler and process event
    handler = HookHandler()
    result = handler.handle_event(event_data)

    # Display result
    console.print(f"\n[bold]Hook Event:[/bold] {event}")
    console.print("[bold]Input Data:[/bold]")
    syntax = Syntax(json.dumps(event_data, indent=2), "json", theme="monokai")
    console.print(syntax)

    console.print("\n[bold]Result:[/bold]")
    syntax = Syntax(json.dumps(result, indent=2), "json", theme="monokai")
    console.print(syntax)


@app.command("install")
def install_hooks(
    target: Path = typer.Option(
        Path.home() / ".config" / "claude" / "hooks.json",
        "--target",
        "-t",
        help="Target location for hooks.json",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing hooks.json",
    ),
) -> None:
    """
    Install hooks.json to Claude Code configuration.

    Generates and installs the hooks configuration in the appropriate location.
    """
    # Check if target exists
    if target.exists() and not force:
        console.print(f"[yellow]File already exists: {target}[/yellow]")
        console.print("Use --force to overwrite")
        raise typer.Exit(1)

    # Ensure target directory exists
    target.parent.mkdir(parents=True, exist_ok=True)

    # Generate and save hooks
    generate_hooks_json(output_path=target)

    console.print(f"[green]✓ Hooks installed to {target}[/green]")
    console.print("\n[yellow]Next steps:[/yellow]")
    console.print("1. Restart Claude Code to load the new hooks")
    console.print("2. ClaudeCraftsman will now integrate with Claude Code")
    console.print("3. Use 'claudecraftsman hook test' to verify integration")


# These are the actual hook handler commands called by Claude Code
@app.command("validate", hidden=True)
def hook_validate() -> None:
    """Pre-tool validation hook handler."""
    import sys

    from claudecraftsman.hooks.handlers import main

    # Set up sys.argv for the main() function
    original_argv = sys.argv
    try:
        sys.argv = ["claudecraftsman", "validate"]
        main()
    finally:
        sys.argv = original_argv


@app.command("update-state", hidden=True)
def hook_update_state() -> None:
    """Post-tool state update hook handler."""
    import sys

    from claudecraftsman.hooks.handlers import main

    # Set up sys.argv for the main() function
    original_argv = sys.argv
    try:
        sys.argv = ["claudecraftsman", "update-state"]
        main()
    finally:
        sys.argv = original_argv


@app.command("route-command", hidden=True)
def hook_route_command() -> None:
    """User prompt command routing hook handler."""
    import sys

    from claudecraftsman.hooks.handlers import main

    # Set up sys.argv for the main() function
    original_argv = sys.argv
    try:
        sys.argv = ["claudecraftsman", "route-command"]
        main()
    finally:
        sys.argv = original_argv


@app.command("initialize", hidden=True)
def hook_initialize() -> None:
    """Session initialization hook handler."""
    import sys

    from claudecraftsman.hooks.handlers import main

    # Set up sys.argv for the main() function
    original_argv = sys.argv
    try:
        sys.argv = ["claudecraftsman", "initialize"]
        main()
    finally:
        sys.argv = original_argv
