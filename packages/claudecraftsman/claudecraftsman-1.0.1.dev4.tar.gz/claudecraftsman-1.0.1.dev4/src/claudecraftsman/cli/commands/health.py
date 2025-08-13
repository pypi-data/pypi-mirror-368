"""Health command for framework compliance monitoring."""

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from claudecraftsman.core.config import get_config
from claudecraftsman.core.enforcement import FrameworkEnforcer
from claudecraftsman.utils.logging import logger

app = typer.Typer(
    name="health", help="Framework health monitoring and compliance reporting", no_args_is_help=True
)

console = Console()


@app.command()
def check(
    auto_correct: bool = typer.Option(
        False, "--auto-correct", help="Automatically correct violations where possible"
    ),
    detailed: bool = typer.Option(False, "--detailed", help="Show detailed violation information"),
) -> None:
    """Run framework health check and display results."""
    try:
        config = get_config()
        enforcer = FrameworkEnforcer(config)

        # Run validation
        console.print("\n[cyan]Running framework health check...[/cyan]\n")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Validating framework...", total=None)
            violations = enforcer.validate_framework()
            progress.update(task, completed=True)

        # Update health metrics
        enforcer.update_health_metrics()

        # Display dashboard
        enforcer.display_health_dashboard()

        # Show violations if detailed
        if detailed and violations:
            console.print("\n[yellow]Active Violations:[/yellow]\n")
            for v in violations:
                severity_color = {
                    "critical": "red",
                    "high": "yellow",
                    "medium": "cyan",
                    "low": "white",
                }[v.severity]

                console.print(f"[{severity_color}]● {v.type.value}[/{severity_color}]")
                console.print(f"  {v.description}")
                if v.file_path:
                    console.print(f"  File: {v.file_path}")
                if v.auto_correctable:
                    console.print("  [green]✓ Auto-correctable[/green]")
                console.print()

        # Auto-correct if requested
        if auto_correct and violations:
            correctable = [v for v in violations if v.auto_correctable]
            if correctable:
                console.print(f"\n[cyan]Auto-correcting {len(correctable)} violations...[/cyan]")
                corrected = enforcer.auto_correct_violations()
                console.print(f"[green]✓ Corrected {len(corrected)} violations[/green]")

                # Re-run validation
                console.print("\n[cyan]Re-validating after corrections...[/cyan]")
                enforcer.validate_framework()
                enforcer.update_health_metrics()
                enforcer.display_health_dashboard()

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        console.print(f"[red]Error: Health check failed - {e}[/red]")
        raise typer.Exit(1)


@app.command()
def monitor(
    interval: int = typer.Option(
        300, "--interval", help="Validation interval in seconds (default: 5 minutes)"
    ),
    auto_correct: bool = typer.Option(
        True, "--auto-correct/--no-auto-correct", help="Enable automatic correction of violations"
    ),
) -> None:
    """Start continuous health monitoring in the background."""
    try:
        config = get_config()
        enforcer = FrameworkEnforcer(config)

        # Configure settings
        enforcer.validation_interval = interval
        enforcer.auto_correct = auto_correct

        # Start monitoring
        console.print("\n[cyan]Starting continuous health monitoring...[/cyan]")
        console.print(f"Interval: {interval} seconds")
        console.print(f"Auto-correction: {'enabled' if auto_correct else 'disabled'}")

        enforcer.start_continuous_validation()

        console.print("\n[green]✓ Health monitoring started[/green]")
        console.print("[dim]Running in background - use 'health check' to see current status[/dim]")

    except Exception as e:
        logger.error(f"Failed to start monitoring: {e}")
        console.print(f"[red]Error: Failed to start monitoring - {e}[/red]")
        raise typer.Exit(1)


@app.command()
def report(
    output: str = typer.Option(None, "--output", "-o", help="Save report to file (JSON format)"),
) -> None:
    """Generate comprehensive compliance report."""
    try:
        config = get_config()
        enforcer = FrameworkEnforcer(config)

        # Run fresh validation
        console.print("\n[cyan]Generating compliance report...[/cyan]\n")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Analyzing framework...", total=None)
            enforcer.validate_framework()
            enforcer.update_health_metrics()
            report = enforcer.generate_compliance_report()
            progress.update(task, completed=True)

        # Display report summary
        console.print("[bold cyan]Compliance Report Summary[/bold cyan]\n")
        console.print(f"Timestamp: {report.timestamp}")
        console.print(f"Files Scanned: {report.total_files_scanned}")
        console.print(f"Violations Found: {len(report.violations_found)}")
        console.print(f"Compliance Score: {report.compliance_score:.1f}%")

        # Show recommendations
        if report.recommendations:
            console.print("\n[yellow]Recommendations:[/yellow]")
            for rec in report.recommendations:
                console.print(f"  • {rec}")

        # Save to file if requested
        if output:
            from pathlib import Path

            output_path = Path(output)
            output_path.write_text(report.model_dump_json(indent=2))
            console.print(f"\n[green]✓ Report saved to {output_path}[/green]")

    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        console.print(f"[red]Error: Report generation failed - {e}[/red]")
        raise typer.Exit(1)


@app.command()
def violations(
    type: str = typer.Option(None, "--type", help="Filter by violation type"),
    severity: str = typer.Option(
        None, "--severity", help="Filter by severity (critical/high/medium/low)"
    ),
) -> None:
    """List all active framework violations."""
    try:
        config = get_config()
        enforcer = FrameworkEnforcer(config)

        # Run validation
        violations = enforcer.validate_framework()

        # Filter if requested
        if type:
            violations = [v for v in violations if v.type.value == type]
        if severity:
            violations = [v for v in violations if v.severity == severity]

        if not violations:
            console.print("\n[green]✓ No violations found[/green]")
            return

        # Display violations
        console.print(f"\n[yellow]Found {len(violations)} violations:[/yellow]\n")

        # Group by severity
        by_severity: dict[str, list] = {}
        for v in violations:
            by_severity.setdefault(v.severity, []).append(v)

        for sev in ["critical", "high", "medium", "low"]:
            if sev not in by_severity:
                continue

            severity_color = {
                "critical": "red",
                "high": "yellow",
                "medium": "cyan",
                "low": "white",
            }[sev]

            console.print(
                f"[{severity_color}]{sev.upper()} ({len(by_severity[sev])})[/{severity_color}]"
            )

            for v in by_severity[sev]:
                console.print(f"  • {v.type.value}: {v.description}")
                if v.file_path:
                    console.print(f"    File: {v.file_path}")
                if v.auto_correctable:
                    console.print("    [green]Auto-correctable[/green]")
            console.print()

    except Exception as e:
        logger.error(f"Failed to list violations: {e}")
        console.print(f"[red]Error: Failed to list violations - {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
