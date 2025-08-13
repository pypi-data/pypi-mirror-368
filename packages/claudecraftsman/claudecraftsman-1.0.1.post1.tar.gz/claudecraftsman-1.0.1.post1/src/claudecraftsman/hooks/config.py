"""
Hook configuration for Claude Code integration.

Generates and manages hook configurations for ClaudeCraftsman.
"""

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from rich.console import Console

console = Console()


class HookEvent(BaseModel):
    """Represents a single hook event configuration."""

    model_config = ConfigDict(extra="forbid")

    event: str = Field(pattern="^(preToolUse|postToolUse|userPromptSubmit|sessionStart)$")
    handler: str
    enabled: bool = True
    description: str | None = None
    filter: dict[str, Any] | None = None


class HookConfig(BaseModel):
    """Complete hook configuration for ClaudeCraftsman."""

    model_config = ConfigDict(extra="forbid")

    version: str = "1.0"
    description: str = "ClaudeCraftsman Framework Hooks"
    hooks: list[HookEvent] = Field(default_factory=list)
    settings: dict[str, Any] = Field(default_factory=dict)


def get_default_hooks() -> list[HookEvent]:
    """Get default hook configurations for ClaudeCraftsman."""
    return [
        # Pre-tool use validation
        HookEvent(
            event="preToolUse",
            handler="claudecraftsman hook validate",
            description="Validate operations before tool execution",
            filter={
                "tools": ["Edit", "Write", "MultiEdit"],
                "condition": "hasFramework",
            },
        ),
        # Post-tool use state updates
        HookEvent(
            event="postToolUse",
            handler="claudecraftsman hook update-state",
            description="Update framework state after tool execution",
            filter={
                "tools": ["Edit", "Write", "MultiEdit", "Read"],
                "condition": "hasFramework",
            },
        ),
        # User prompt command routing
        HookEvent(
            event="userPromptSubmit",
            handler="claudecraftsman hook route-command",
            description="Route framework commands and enhance prompts",
            filter={
                "pattern": "^/(design|plan|implement|workflow|add)",
            },
        ),
        # Session initialization
        HookEvent(
            event="sessionStart",
            handler="claudecraftsman hook initialize",
            description="Initialize framework for new session",
            enabled=True,
        ),
    ]


def generate_hooks_json(
    output_path: Path | None = None,
    custom_hooks: list[HookEvent] | None = None,
) -> str:
    """Generate hooks.json configuration for Claude Code."""
    # Use custom hooks or defaults
    hooks = custom_hooks or get_default_hooks()

    # Create configuration
    config = HookConfig(
        version="1.0",
        description="ClaudeCraftsman Framework Hooks - Artisanal development automation",
        hooks=hooks,
        settings={
            "claudecraftsman": {
                "autoValidate": True,
                "autoUpdateState": True,
                "enhanceCommands": True,
                "preserveContext": True,
            }
        },
    )

    # Convert to JSON
    hooks_json = {
        "version": config.version,
        "description": config.description,
        "hooks": [
            {
                "event": hook.event,
                "handler": hook.handler,
                "enabled": hook.enabled,
                "description": hook.description,
                "filter": hook.filter,
            }
            for hook in config.hooks
        ],
        "settings": config.settings,
    }

    json_str = json.dumps(hooks_json, indent=2)

    # Save if path provided
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json_str)
        console.print(f"[green]✓ Hooks configuration saved to {output_path}[/green]")

    return json_str


def validate_hooks_json(hooks_path: Path) -> bool:
    """Validate a hooks.json file."""
    try:
        content = json.loads(hooks_path.read_text())

        # Check required fields
        required = ["version", "hooks"]
        for field in required:
            if field not in content:
                console.print(f"[red]Missing required field: {field}[/red]")
                return False

        # Validate each hook
        for hook in content.get("hooks", []):
            if "event" not in hook or "handler" not in hook:
                console.print("[red]Hook missing required event or handler[/red]")
                return False

            # Validate event type
            valid_events = ["preToolUse", "postToolUse", "userPromptSubmit", "sessionStart"]
            if hook["event"] not in valid_events:
                console.print(f"[red]Invalid event type: {hook['event']}[/red]")
                return False

        console.print("[green]✓ Hooks configuration is valid[/green]")
        return True

    except json.JSONDecodeError as e:
        console.print(f"[red]Invalid JSON: {e}[/red]")
        return False
    except Exception as e:
        console.print(f"[red]Error validating hooks: {e}[/red]")
        return False
