"""Initialize ClaudeCraftsman in a project."""

import shutil
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm

from ... import __version__
from ...core.config import Config
from ...utils.logging import logger

console = Console()


def init_project(
    name: str | None = typer.Option(None, "--name", "-n", help="Project name"),
    type: str | None = typer.Option(
        "web", "--type", "-t", help="Project type (web, api, mobile, desktop)"
    ),
    framework: str | None = typer.Option(
        None, "--framework", "-f", help="Framework (react, vue, express, flask)"
    ),
    force: bool = typer.Option(False, "--force", help="Force overwrite existing files"),
    merge: bool = typer.Option(
        True, "--merge/--no-merge", help="Merge with existing .claude directory"
    ),
):
    """Initialize ClaudeCraftsman framework in the current project.

    This command:
    1. Creates/updates .claude/ directory structure
    2. Extracts framework files (agents, commands) from the package
    3. Merges with existing .claude/ content if present
    4. Updates CLAUDE.md to activate the framework
    """
    config = Config()
    project_root = Path.cwd()
    claude_dir = project_root / ".claude"

    # Use provided name or directory name
    project_name = name or project_root.name

    console.print(f"\n[bold blue]Initializing ClaudeCraftsman in {project_root}[/bold blue]\n")

    # Check for existing .claude directory
    if claude_dir.exists() and not force and not merge:
        console.print("[yellow]⚠️  .claude/ directory already exists![/yellow]")
        if not Confirm.ask("Do you want to merge with existing content?"):
            console.print("[red]Initialization cancelled.[/red]")
            raise typer.Exit(1)

    # Create directory structure
    directories = [
        ".claude",
        ".claude/docs/current",
        ".claude/docs/archive",
        ".claude/docs/templates",
        ".claude/specs/api-specifications",
        ".claude/specs/database-schemas",
        ".claude/specs/component-specifications",
        ".claude/context",
        ".claude/templates",
        ".claude/agents",
        ".claude/commands",
    ]

    for dir_path in directories:
        full_path = project_root / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Created directory: {full_path}")

    # Extract framework files from package
    package_root = Path(__file__).parent.parent.parent
    templates_dir = package_root / "templates" / "framework"

    if not templates_dir.exists():
        console.print("[red]❌ Framework templates not found in package![/red]")
        console.print(f"[dim]Expected at: {templates_dir}[/dim]")
        raise typer.Exit(1)

    # Copy framework files with merge handling
    copied_files = []

    # Copy framework.md
    framework_src = templates_dir / "framework.md"
    framework_dst = claude_dir / "framework.md"
    if framework_src.exists():
        if framework_dst.exists() and merge:
            # Backup existing
            backup_path = framework_dst.with_suffix(".md.backup")
            shutil.copy2(framework_dst, backup_path)
            console.print(f"[dim]Backed up existing framework.md to {backup_path.name}[/dim]")

        shutil.copy2(framework_src, framework_dst)
        copied_files.append("framework.md")

    # Copy agents
    agents_src = templates_dir / "agents"
    agents_dst = claude_dir / "agents"
    if agents_src.exists():
        for agent_file in agents_src.glob("*.md"):
            dst_file = agents_dst / agent_file.name
            if dst_file.exists() and merge:
                # Skip if exists in merge mode
                console.print(f"[dim]Skipping {agent_file.name} (already exists)[/dim]")
                continue
            shutil.copy2(agent_file, dst_file)
            copied_files.append(f"agents/{agent_file.name}")

    # Copy commands
    commands_src = templates_dir / "commands"
    commands_dst = claude_dir / "commands"
    if commands_src.exists():
        for cmd_file in commands_src.glob("*.md"):
            dst_file = commands_dst / cmd_file.name
            if dst_file.exists() and merge:
                # Skip if exists in merge mode
                console.print(f"[dim]Skipping {cmd_file.name} (already exists)[/dim]")
                continue
            shutil.copy2(cmd_file, dst_file)
            copied_files.append(f"commands/{cmd_file.name}")

    # Create initial context files
    context_files = {
        "WORKFLOW-STATE.md": f"""# Workflow State
**Project**: {project_name}
**Type**: {type}
**Framework**: {framework or "Not specified"}
**Initialized**: {{current_datetime}}
**Status**: Active

## Current Phase
- Phase: Initialization
- Status: Complete
""",
        "CONTEXT.md": f"""# Project Context: {project_name}

## Overview
**Type**: {type}
**Framework**: {framework or "Not specified"}
**ClaudeCraftsman Version**: {__version__}

## Project Goals
[To be defined]

## Key Stakeholders
[To be defined]

## Success Criteria
[To be defined]

## Quality Standards
- Craftsman-level quality throughout
- Research-driven development
- Time-aware documentation
- Comprehensive testing
""",
        "HANDOFF-LOG.md": """# Agent Handoff Log

## Initialization
**Date**: {current_datetime}
**Agent**: ClaudeCraftsman CLI
**Action**: Project initialization
**Status**: Complete
""",
    }

    for filename, content in context_files.items():
        file_path = claude_dir / "context" / filename
        if not file_path.exists() or force:
            # Note: {current_datetime} will be replaced by agents using MCP time tool
            file_path.write_text(content)
            copied_files.append(f"context/{filename}")

    # Create/Update CLAUDE.md
    claude_md = project_root / "CLAUDE.md"
    if claude_md.exists() and merge:
        # Append framework activation
        existing_content = claude_md.read_text()
        if "ClaudeCraftsman" not in existing_content:
            with claude_md.open("a") as f:
                f.write("\n\n# ClaudeCraftsman Framework\n")
                f.write("@.claude/framework.md\n")
                f.write("@.claude/agents/product-architect.md\n")
                f.write("@.claude/agents/design-architect.md\n")
                f.write("@.claude/commands/help.md\n")
                f.write("@.claude/commands/design.md\n")
            console.print("[green]✅ Updated CLAUDE.md with framework activation[/green]")
    else:
        # Create new CLAUDE.md
        claude_md_content = f"""# ClaudeCraftsman: {project_name}
*Artisanal development with intention and care*

## Framework Activation
@.claude/framework.md

## Core Agents
@.claude/agents/product-architect.md
@.claude/agents/design-architect.md
@.claude/agents/workflow-coordinator.md
@.claude/agents/system-architect.md

## Essential Commands
@.claude/commands/help.md
@.claude/commands/add.md
@.claude/commands/plan.md
@.claude/commands/design.md
@.claude/commands/workflow.md

## Project Configuration
- **Project**: {project_name}
- **Type**: {type}
- **Framework**: {framework or "Not specified"}
- **Standards**: Research-driven specifications, time-aware documentation
- **Quality Gates**: Phase-based completion with craftsman approval
"""
        claude_md.write_text(claude_md_content)
        console.print("[green]✅ Created CLAUDE.md with framework activation[/green]")

    # Copy hooks.json template
    hooks_template = package_root / "templates" / "hooks.json"
    hooks_dest = project_root / "hooks.json"
    if hooks_template.exists() and not hooks_dest.exists():
        shutil.copy2(hooks_template, hooks_dest)
        console.print("[green]✅ Created hooks.json for Claude Code integration[/green]")
    elif hooks_dest.exists():
        console.print("[dim]Skipping hooks.json (already exists)[/dim]")

    # Create registry.md
    registry_path = claude_dir / "docs" / "current" / "registry.md"
    if not registry_path.exists():
        registry_content = f"""# ClaudeCraftsman Document Registry: {project_name}

## Active Documents
| Document | Type | Location | Date | Status | Purpose |
|----------|------|----------|------|--------|---------|
| framework.md | Framework | .claude/ | {{current_date}} | Active | Core framework principles |
| CONTEXT.md | Context | .claude/context/ | {{current_date}} | Active | Project context |

## Document Lifecycle
- **Active**: Currently in use
- **Archived**: Superseded but retained for reference
- **Draft**: Work in progress

## Usage
This registry tracks all project documentation to prevent sprawl and maintain organization.
"""
        registry_path.write_text(registry_content)
        copied_files.append("docs/current/registry.md")

    # Summary
    console.print("\n[bold green]✨ ClaudeCraftsman initialization complete![/bold green]\n")

    console.print(
        Panel.fit(
            f"""[green]✓[/green] Created project structure in .claude/
[green]✓[/green] Extracted {len(copied_files)} framework files
[green]✓[/green] {"Merged with" if claude_dir.exists() and merge else "Created"} existing content
[green]✓[/green] {"Updated" if claude_md.exists() else "Created"} CLAUDE.md

[bold]Next steps:[/bold]
1. Open Claude Code in this directory
2. The framework will auto-activate via CLAUDE.md
3. Use [cyan]/help[/cyan] to see available commands
4. Start with [cyan]/design[/cyan] for comprehensive planning

[dim]Framework files are now in your project's .claude/ directory
and will be loaded by Claude Code on session start.[/dim]""",
            title="Initialization Complete",
            border_style="green",
        )
    )


# Add the command to be registered in app.py
init_command = typer.Typer()
init_command.command(name="init")(init_project)
