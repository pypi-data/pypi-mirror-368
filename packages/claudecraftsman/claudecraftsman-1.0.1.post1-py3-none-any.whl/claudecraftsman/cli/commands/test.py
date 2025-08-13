"""Test command for ClaudeCraftsman framework development."""

import json
import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


app = typer.Typer(
    name="test", help="Framework testing utilities for development", rich_markup_mode="rich"
)


@app.command()
def quick(
    source: Path = typer.Option(
        Path.cwd(), "--source", help="Source directory of framework to test"
    ),
) -> None:
    """Quick smoke test of framework functionality."""
    # Safety check (bypass for CI testing)
    import os

    if Path.cwd().is_relative_to(source) and not os.environ.get("CC_TEST_BYPASS"):
        console.print(
            Panel(
                "[red]Cannot test from within framework source![/red]\n"
                "Please run from a different directory.",
                style="red",
            )
        )
        return

    console.print("[bold cyan]Running quick framework tests...[/bold cyan]\n")

    # Create minimal test environment
    with tempfile.TemporaryDirectory(prefix="cc-quick-test-") as tmpdir:
        test_dir = Path(tmpdir)
        project_dir = test_dir / "test-project"

        # Step 1: Install framework
        console.print("1. Installing framework from local source...")
        try:
            subprocess.run(["uv", "init", str(project_dir)], check=True, capture_output=True)
            subprocess.run(
                ["uv", "add", "--editable", str(source)],
                check=True,
                cwd=project_dir,
                capture_output=True,
            )
            console.print("   [green]✅ Installation successful[/green]")
        except subprocess.CalledProcessError as e:
            console.print(f"   [red]❌ Installation failed: {e}[/red]")
            raise typer.Exit(1)

        # Step 2: Test CLI availability
        console.print("2. Testing CLI availability...")
        result = subprocess.run(
            ["uv", "run", "cc", "--version"],
            check=False,
            capture_output=True,
            text=True,
            cwd=project_dir,
        )
        if result.returncode == 0:
            console.print(f"   [green]✅ CLI available: {result.stdout.strip()}[/green]")
        else:
            console.print("   [red]❌ CLI not available[/red]")
            raise typer.Exit(1)

        # Step 3: Test init command
        console.print("3. Testing project initialization...")
        # Create subdirectory for init
        init_dir = project_dir / "quick-test"
        init_dir.mkdir()
        result = subprocess.run(
            ["uv", "run", "cc", "init", "--name", "quick-test"],
            check=False,
            capture_output=True,
            text=True,
            cwd=init_dir,
        )
        if result.returncode == 0:
            console.print("   [green]✅ Project initialization works[/green]")
        else:
            console.print(f"   [red]❌ Init failed: {result.stderr}[/red]")
            raise typer.Exit(1)

        # Step 4: Verify structure
        console.print("4. Verifying created structure...")
        test_project = init_dir  # Already points to project_dir / "quick-test"
        checks = [
            (test_project / ".claude", "Framework directory"),
            (test_project / "CLAUDE.md", "Configuration file"),
        ]

        all_good = True
        for path, desc in checks:
            if path.exists():
                console.print(f"   [green]✅ {desc} created[/green]")
            else:
                console.print(f"   [red]❌ {desc} missing[/red]")
                all_good = False

        if not all_good:
            raise typer.Exit(1)

        # Step 5: Test basic commands
        console.print("5. Testing basic commands...")

        # Create a test file for validation
        test_file = test_project / "example.py"
        test_file.write_text(
            '"""Example module."""\n\ndef greet(name: str) -> str:\n    """Greet someone."""\n    return f"Hello, {name}!"\n'
        )

        test_cmds = [
            (["validate", "pre-operation"], "Pre-operation checks"),
            (["validate", "checklist"], "Checklist generation"),
            (["hook", "--help"], "Hook system"),
            (["--help"], "Help system"),
        ]

        for cmd_parts, desc in test_cmds:
            result = subprocess.run(  # type: ignore[assignment]
                ["uv", "run", "cc", *cmd_parts], check=False, capture_output=True, cwd=test_project
            )
            if result.returncode == 0:
                console.print(f"   [green]✅ {desc} works[/green]")
            else:
                console.print(f"   [red]❌ {desc} failed[/red]")
                all_good = False

        if all_good:
            console.print("\n[bold green]✅ All quick tests passed![/bold green]")
        else:
            console.print("\n[bold red]❌ Some tests failed[/bold red]")
            raise typer.Exit(1)


@app.command()
def install(
    source: Path = typer.Option(
        Path.cwd(), "--source", help="Source directory of framework to test", exists=True
    ),
    isolated: bool = typer.Option(
        True, "--isolated/--no-isolated", help="Run tests in isolated environment"
    ),
) -> None:
    """Test framework installation from local source."""
    if not isolated:
        console.print("[yellow]⚠️ Non-isolated testing not recommended[/yellow]")
        return

    # Safety check - prevent self-pollution (bypass for CI)
    import os

    if Path.cwd().is_relative_to(source) and not os.environ.get("CC_TEST_BYPASS"):
        console.print(
            Panel(
                "[red]Cannot test from within framework source![/red]\n"
                "Please run from a different directory to avoid circular dependencies.",
                style="red",
            )
        )
        return

    # Create isolated test environment
    test_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    test_root = Path("/tmp/claudecraftsman-tests")
    test_dir = test_root / f"test-{test_id}"

    try:
        console.print(f"Creating test environment at {test_dir}")
        test_dir.mkdir(parents=True, exist_ok=True)

        # Save test metadata
        metadata = {
            "test_id": test_id,
            "source": str(source),
            "created": datetime.now().isoformat(),
            "status": "in_progress",
        }
        (test_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))

        # Create test project
        project_dir = test_dir / "test-project"
        console.print("Initializing test project with uv...")
        subprocess.run(["uv", "init", str(project_dir)], check=True, cwd=test_dir)

        # Install framework from local source (editable)
        console.print(f"Installing framework from {source}...")
        subprocess.run(["uv", "add", "--editable", str(source)], check=True, cwd=project_dir)

        # Test installation
        console.print("Verifying installation...")
        result = subprocess.run(
            ["uv", "run", "cc", "--version"],
            check=False,
            capture_output=True,
            text=True,
            cwd=project_dir,
        )

        if result.returncode == 0:
            console.print(
                Panel(
                    f"[green]✅ Installation successful![/green]\nTest environment: {test_dir}",
                    style="green",
                )
            )

            # Update metadata
            metadata["status"] = "success"
            (test_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))
        else:
            console.print(f"[red]Installation failed: {result.stderr}[/red]")
            metadata["status"] = "failed"
            (test_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))

    except Exception as e:
        console.print(f"[red]Test failed: {e}[/red]")


@app.command(name="list")
def list_tests() -> None:
    """List all test environments."""
    test_root = Path("/tmp/claudecraftsman-tests")

    if not test_root.exists():
        console.print("No test environments found")
        return

    table = Table(title="Test Environments")
    table.add_column("Test ID", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Created", style="yellow")
    table.add_column("Size", style="blue")

    for test_dir in sorted(test_root.glob("test-*")):
        if test_dir.is_dir():
            test_id = test_dir.name.replace("test-", "")

            # Read metadata if available
            metadata_file = test_dir / "metadata.json"
            if metadata_file.exists():
                metadata = json.loads(metadata_file.read_text())
                status = metadata.get("status", "unknown")
                created = metadata.get("created", "unknown")
            else:
                status = "unknown"
                created = "unknown"

            # Calculate size
            size = sum(f.stat().st_size for f in test_dir.rglob("*") if f.is_file())
            size_str = f"{size / 1024 / 1024:.1f} MB"

            table.add_row(test_id, status, created, size_str)

    console.print(table)


@app.command()
def cleanup(
    test_id: str | None = typer.Argument(None, help="Test ID to remove"),
    clean_all: bool = typer.Option(False, "--all", help="Remove all test environments"),
    old: int | None = typer.Option(None, "--old", help="Remove tests older than N days"),
) -> None:
    """Clean up test environments."""
    test_root = Path("/tmp/claudecraftsman-tests")

    if not test_root.exists():
        console.print("No test environments to clean")
        return

    if clean_all:
        if typer.confirm("Remove ALL test environments?"):
            shutil.rmtree(test_root)
            console.print("[green]All test environments removed[/green]")
    elif old is not None:
        # Remove old tests
        from datetime import timedelta

        cutoff = datetime.now() - timedelta(days=old)
        removed = 0

        for test_dir in test_root.glob("test-*"):
            if test_dir.stat().st_mtime < cutoff.timestamp():
                shutil.rmtree(test_dir)
                removed += 1

        console.print(f"[green]Removed {removed} old test environment(s)[/green]")
    elif test_id:
        # Remove specific test
        test_dir = test_root / f"test-{test_id}"
        if test_dir.exists():
            shutil.rmtree(test_dir)
            console.print(f"[green]Removed test environment: {test_id}[/green]")
        else:
            console.print(f"[red]Test environment not found: {test_id}[/red]")
    else:
        console.print("Please specify --all, --old=N, or a test ID")


@app.command()
def run(
    test_type: str = typer.Argument(
        "all", help="Type of tests to run: all, unit, integration, e2e, or specific test file"
    ),
    source: Path = typer.Option(
        Path.cwd(), "--source", help="Source directory of framework to test"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
    test_id: str | None = typer.Option(
        None, "--test-id", help="Run tests in existing test environment"
    ),
    preserve: bool = typer.Option(
        False, "--preserve", help="Preserve test environment for debugging (default: auto-cleanup)"
    ),
) -> None:
    """Run framework tests.

    By default, test environments are automatically cleaned up (idempotent).
    Use --preserve to keep them for debugging purposes.
    """
    # If test_id provided, run in existing environment
    if test_id:
        test_root = Path("/tmp/claudecraftsman-tests")
        test_dir = test_root / f"test-{test_id}"
        if not test_dir.exists():
            console.print(f"[red]Test environment not found: {test_id}[/red]")
            return
        project_dir = test_dir / "test-project"
    else:
        # Create temporary test environment
        test_id = datetime.now().strftime("%Y%m%d-%H%M%S")
        test_root = Path("/tmp/claudecraftsman-tests")
        test_dir = test_root / f"test-{test_id}"
        project_dir = test_dir / "test-project"

        # Install framework first
        console.print("[yellow]Creating test environment...[/yellow]")
        test_dir.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["uv", "init", str(project_dir)], check=True, cwd=test_dir, capture_output=not verbose
        )
        subprocess.run(
            ["uv", "add", "--editable", str(source)],
            check=True,
            cwd=project_dir,
            capture_output=not verbose,
        )

    console.print(f"[cyan]Running {test_type} tests in {project_dir}[/cyan]")

    # Determine test command based on type
    if test_type == "all":
        # Run all tests
        # First set of tests run in test project dir
        test_commands_base = [
            ("Framework installation", ["uv", "run", "cc", "--version"]),
            ("Help system", ["uv", "run", "cc", "--help"]),
        ]

        results = []
        for test_name, cmd in test_commands_base:
            console.print(f"\n[bold]Testing: {test_name}[/bold]")
            result = subprocess.run(
                cmd, check=False, capture_output=True, text=True, cwd=project_dir
            )
            if result.returncode == 0:
                console.print(f"  [green]✅ {test_name} passed[/green]")
                results.append((test_name, True))
            else:
                console.print(f"  [red]❌ {test_name} failed[/red]")
                if verbose:
                    console.print(f"  [dim]{result.stderr}[/dim]")
                results.append((test_name, False))

        # Initialize a test project
        console.print("\n[bold]Testing: Framework initialization[/bold]")
        test_project_dir = project_dir / "test-project"
        test_project_dir.mkdir()
        result = subprocess.run(
            ["uv", "run", "cc", "init", "--name", "test-project"],
            check=False,
            capture_output=True,
            text=True,
            cwd=test_project_dir,
        )
        if result.returncode == 0:
            console.print("  [green]✅ Framework initialization passed[/green]")
            results.append(("Framework initialization", True))

            # Create a simple Python file for quality validation
            test_file = test_project_dir / "test.py"
            test_file.write_text(
                '"""Test module."""\n\ndef hello():\n    """Say hello."""\n    return "Hello, World!"\n'
            )

            # Now run commands that need framework context
            test_commands_in_project = [
                ("Pre-operation validation", ["uv", "run", "cc", "validate", "pre-operation"]),
                ("Checklist generation", ["uv", "run", "cc", "validate", "checklist"]),
                ("Hook configuration check", ["uv", "run", "cc", "hook", "--help"]),
                ("Health check", ["uv", "run", "cc", "health", "--help"]),
            ]

            for test_name, cmd in test_commands_in_project:
                console.print(f"\n[bold]Testing: {test_name}[/bold]")
                result = subprocess.run(
                    cmd, check=False, capture_output=True, text=True, cwd=test_project_dir
                )
                if result.returncode == 0:
                    console.print(f"  [green]✅ {test_name} passed[/green]")
                    results.append((test_name, True))
                else:
                    console.print(f"  [red]❌ {test_name} failed[/red]")
                    if verbose:
                        console.print(f"  [dim]{result.stderr}[/dim]")
                    results.append((test_name, False))
        else:
            console.print("  [red]❌ Framework initialization failed[/red]")
            if verbose:
                console.print(f"  [dim]{result.stderr}[/dim]")
            results.append(("Framework initialization", False))

        # Summary
        passed = sum(1 for _, p in results if p)
        total = len(results)
        console.print(f"\n[bold]Test Summary:[/bold] {passed}/{total} passed")

        if passed == total:
            console.print("[green]✅ All tests passed![/green]")
        else:
            console.print("[red]❌ Some tests failed[/red]")
            raise typer.Exit(1)

    elif test_type == "unit":
        # Run unit tests (if we had pytest configured)
        console.print(
            "[yellow]Unit tests not yet configured. Use pytest to add unit tests.[/yellow]"
        )

    elif test_type == "integration":
        # Run integration tests
        console.print("[yellow]Integration tests not yet configured.[/yellow]")

    elif test_type == "e2e":
        # Run end-to-end tests
        console.print("[cyan]Running end-to-end test...[/cyan]")

        # E2E test: Full workflow
        e2e_dir = project_dir / "e2e-test"
        e2e_dir.mkdir()

        # Initialize project
        result = subprocess.run(  # type: ignore[assignment]
            ["uv", "run", "cc", "init", "--name", "e2e-test"],
            check=False,
            capture_output=not verbose,
            cwd=e2e_dir,
        )
        if result.returncode != 0:
            console.print("[red]E2E test failed at: project initialization[/red]")
            raise typer.Exit(1)

        # Create some test files
        (e2e_dir / "main.py").write_text(
            '"""Main module."""\n\nif __name__ == "__main__":\n    print("E2E Test")\n'
        )
        (e2e_dir / "utils.py").write_text(
            '"""Utilities."""\n\ndef helper():\n    """Helper function."""\n    pass\n'
        )

        # Run comprehensive tests
        cmds = [
            ["validate", "pre-operation"],
            ["validate", "checklist"],
            ["hook", "--help"],
            ["health", "check"],
        ]

        for cmd in cmds:
            result = subprocess.run(  # type: ignore[assignment]
                ["uv", "run", "cc", *cmd], check=False, cwd=e2e_dir, capture_output=not verbose
            )
            if result.returncode != 0:
                console.print(f"[red]E2E test failed at: cc {' '.join(cmd)}[/red]")
                raise typer.Exit(1)

        console.print("[green]✅ E2E test passed![/green]")

    else:
        # Assume it's a specific test file
        console.print(f"[yellow]Running specific test: {test_type}[/yellow]")
        result = subprocess.run(  # type: ignore[assignment]
            ["uv", "run", "python", "-m", "pytest", test_type],
            check=False,
            cwd=project_dir,
            capture_output=False,
        )
        raise typer.Exit(result.returncode)

    # Clean up by default (idempotent), preserve only if requested
    if not test_id:  # Don't cleanup if using existing test environment
        if preserve:
            console.print(f"\n[yellow]Test environment preserved at: {test_dir}[/yellow]")
            console.print(f"[dim]Use --test-id={test_id} to rerun in this environment[/dim]")
            console.print(f"[dim]Use 'cc test cleanup {test_id}' to remove it[/dim]")
        else:
            console.print("\n[green]Cleaning up test environment...[/green]")
            shutil.rmtree(test_dir)
            console.print("[green]✅ Test environment cleaned up (idempotent)[/green]")


@app.command()
def validate(test_id: str = typer.Argument(..., help="Test ID to validate")) -> None:
    """Validate a test environment has all components."""
    test_root = Path("/tmp/claudecraftsman-tests")
    test_dir = test_root / f"test-{test_id}"

    if not test_dir.exists():
        console.print(f"[red]Test environment not found: {test_id}[/red]")
        return

    project_dir = test_dir / "test-project"

    # Run cc init in test environment
    console.print("Testing framework initialization...")
    validation_dir = project_dir / "validation-test"
    validation_dir.mkdir()
    result = subprocess.run(
        ["uv", "run", "cc", "init", "--name", "validation-test"],
        check=False,
        capture_output=True,
        text=True,
        cwd=validation_dir,
    )

    if result.returncode != 0:
        console.print(f"[red]Initialization failed: {result.stderr}[/red]")
        return

    # Check created structure (validation_dir already defined above)
    checks = [
        (validation_dir / ".claude", "Framework directory"),
        (validation_dir / ".claude" / "agents", "Agents directory"),
        (validation_dir / ".claude" / "commands", "Commands directory"),
        (validation_dir / ".claude" / "docs" / "current", "Documentation structure"),
        (validation_dir / "CLAUDE.md", "Main configuration"),
    ]

    all_passed = True
    for path, description in checks:
        if path.exists():
            console.print(f"✅ {description}")
        else:
            console.print(f"❌ {description} missing")
            all_passed = False

    if all_passed:
        console.print("[green]All validation checks passed![/green]")
    else:
        console.print("[red]Some validation checks failed[/red]")
