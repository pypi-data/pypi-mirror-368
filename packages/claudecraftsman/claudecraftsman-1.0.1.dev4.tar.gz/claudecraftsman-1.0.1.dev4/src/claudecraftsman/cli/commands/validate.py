"""
Validation commands for ClaudeCraftsman CLI.

Replaces enforce-quality-gates.sh functionality.
"""

import subprocess
from datetime import datetime, timedelta
from pathlib import Path

import typer
from rich.console import Console

from claudecraftsman.core.config import get_config
from claudecraftsman.core.validation import QualityGates

app = typer.Typer(name="validate", help="Quality validation commands")
console = Console()


class PreOperationValidator:
    """Pre-operation quality gate validator."""

    def __init__(self) -> None:
        """Initialize validator."""
        self.config = get_config()
        self.claude_dir = self.config.paths.claude_dir
        self.passed = 0
        self.failed = 0
        self.results: list[tuple[str, bool, str]] = []

    def check_framework_structure(self) -> tuple[bool, str]:
        """Check if framework structure is valid."""
        required = [
            self.claude_dir / "framework.md",
            self.claude_dir / "agents",
            self.claude_dir / "commands",
            self.claude_dir / "docs" / "current",
            self.claude_dir / "context",
        ]

        missing = []
        for path in required:
            if not path.exists():
                missing.append(str(path.relative_to(self.claude_dir)))

        if missing:
            return False, f"Missing: {', '.join(missing)}"
        return True, "All required directories present"

    def check_state_currency(self) -> tuple[bool, str]:
        """Check if state files are current (modified within 24 hours)."""
        registry = self.claude_dir / "docs" / "current" / "registry.md"
        workflow = self.claude_dir / "context" / "WORKFLOW-STATE.md"

        if not registry.exists() or not workflow.exists():
            return False, "State files missing"

        now = datetime.now()
        reg_mod = datetime.fromtimestamp(registry.stat().st_mtime)
        work_mod = datetime.fromtimestamp(workflow.stat().st_mtime)

        reg_age = now - reg_mod
        work_age = now - work_mod

        if reg_age > timedelta(hours=24) or work_age > timedelta(hours=24):
            return (
                False,
                f"State files are stale (registry: {reg_age.days}d, workflow: {work_age.days}d old)",
            )

        return True, "State files are current"

    def check_git_clean(self) -> tuple[bool, str]:
        """Check if git repository is reasonably clean."""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                check=False,
                capture_output=True,
                text=True,
                cwd=self.config.project_root,
            )

            if result.returncode != 0:
                return True, "Git not available (skipping)"

            modified_files = len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0

            if modified_files > 20:
                return False, f"Too many uncommitted changes ({modified_files} files)"

            return True, f"{modified_files} uncommitted files (acceptable)"

        except Exception:
            return True, "Git not available (skipping)"

    def check_no_conflicts(self) -> tuple[bool, str]:
        """Check for git conflict markers."""
        try:
            # Search for conflict markers in .claude directory
            result = subprocess.run(
                ["grep", "-r", "^<<<<<<< ", str(self.claude_dir)],
                check=False,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                # Found conflict markers
                conflicts = len(result.stdout.strip().split("\n"))
                return False, f"Found {conflicts} conflict markers"

            return True, "No conflict markers found"

        except Exception:
            return True, "Conflict check skipped"

    def check_documentation_standards(self) -> tuple[bool, str]:
        """Check if documents follow naming conventions."""
        docs_dir = self.claude_dir / "docs" / "current"
        if not docs_dir.exists():
            return True, "No documents directory"

        bad_names = []
        for doc in docs_dir.glob("*.md"):
            if doc.name == "registry.md":
                continue
            # Check for YYYY-MM-DD pattern in filename
            if not any(char.isdigit() for char in doc.name):
                bad_names.append(doc.name)

        if bad_names:
            return False, f"Non-standard names: {', '.join(bad_names[:3])}"

        return True, "All documents follow naming conventions"

    def check_required_components(self) -> tuple[bool, str]:
        """Check if required components exist."""
        if self.config.dev_mode:
            # In dev mode, check Python modules
            required = [
                Path("src/claudecraftsman/core/state.py"),
                Path("src/claudecraftsman/core/registry.py"),
                Path("src/claudecraftsman/core/validation.py"),
            ]
            missing = [p.name for p in required if not p.exists()]
        else:
            # In production, check for installed framework
            if not self.config.paths.framework_file.exists():
                missing = ["framework.md"]
            else:
                missing = []

        if missing:
            return False, f"Missing components: {', '.join(missing)}"

        return True, "All required components present"

    def run_all_checks(self) -> bool:
        """Run all pre-operation quality gates."""
        console.print(
            "\n[bold blue]🛡️  ClaudeCraftsman Quality Gates - Pre-Operation Validation[/bold blue]"
        )
        console.print("[blue]" + "━" * 70 + "[/blue]\n")

        checks = [
            ("Framework Structure", self.check_framework_structure),
            ("State Files Current", self.check_state_currency),
            ("Git Repository", self.check_git_clean),
            ("No Conflicts", self.check_no_conflicts),
            ("Documentation Standards", self.check_documentation_standards),
            ("Required Components", self.check_required_components),
        ]

        for name, check_func in checks:
            console.print(f"🔍 Checking {name}... ", end="")
            passed, message = check_func()

            if passed:
                console.print("[green]✅ PASSED[/green]")
                self.passed += 1
            else:
                console.print("[red]❌ FAILED[/red]")
                console.print(f"   [red]{message}[/red]")
                self.failed += 1

            self.results.append((name, passed, message))

        return self.failed == 0

    def show_summary(self) -> None:
        """Show validation summary."""
        console.print("\n[blue]" + "━" * 70 + "[/blue]")
        console.print("[bold blue]📊 Quality Gate Summary[/bold blue]")
        console.print("[blue]" + "━" * 70 + "[/blue]\n")

        if self.failed == 0:
            console.print(
                f"[green]✅ All quality gates passed! ({self.passed}/{self.passed})[/green]"
            )
            console.print("[green]   Ready to proceed with operation.[/green]")
        else:
            console.print(
                f"[red]❌ Quality gates failed! ({self.passed} passed, {self.failed} failed)[/red]"
            )
            console.print("\n[yellow]⚠️  Recommendations:[/yellow]")

            for name, passed, _message in self.results:
                if not passed:
                    if "Framework Structure" in name:
                        console.print(
                            "[yellow]   - Run 'claudecraftsman init' or check directory structure[/yellow]"
                        )
                    elif "State Files" in name:
                        console.print(
                            "[yellow]   - Update state files using 'claudecraftsman state' commands[/yellow]"
                        )
                    elif "Git Repository" in name:
                        console.print(
                            "[yellow]   - Commit your changes to keep repository manageable[/yellow]"
                        )
                    elif "Conflicts" in name:
                        console.print(
                            "[yellow]   - Resolve git conflicts before proceeding[/yellow]"
                        )
                    elif "Documentation" in name:
                        console.print(
                            "[yellow]   - Rename documents to follow YYYY-MM-DD format[/yellow]"
                        )
                    elif "Components" in name:
                        console.print(
                            "[yellow]   - Ensure all required components are installed[/yellow]"
                        )

            console.print("\n[red]⛔ Operation blocked until quality gates pass.[/red]")


@app.command("pre-operation")
def pre_operation(
    strict: bool = typer.Option(
        False,
        "--strict",
        "-s",
        help="Strict mode - fail on any warning",
    ),
) -> None:
    """
    Run pre-operation quality gates validation.

    Checks framework structure, state currency, and other quality standards
    before allowing operations to proceed.
    """
    validator = PreOperationValidator()

    if validator.run_all_checks():
        validator.show_summary()
        raise typer.Exit(0)
    else:
        validator.show_summary()
        raise typer.Exit(1)


@app.command("quality")
def quality_validation(
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
    Run comprehensive quality gates validation.

    Executes the 8-step quality validation cycle (syntax, types, lint, security,
    tests, performance, documentation, integration).
    """
    gates = QualityGates()
    report = gates.validate_all(phase)

    if output:
        output.write_text(gates.create_quality_checklist())
        console.print(f"[green]✓ Quality checklist saved to {output}[/green]")

    if not report.overall_passed:
        raise typer.Exit(1)


@app.command("checklist")
def generate_checklist(
    output: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Save checklist to file",
    ),
) -> None:
    """
    Generate a quality gates checklist.

    Creates a markdown checklist of all quality standards for manual review.
    """
    gates = QualityGates()
    checklist = gates.create_quality_checklist()

    if output:
        output.write_text(checklist)
        console.print(f"[green]✓ Quality checklist saved to {output}[/green]")
    else:
        console.print(checklist)
