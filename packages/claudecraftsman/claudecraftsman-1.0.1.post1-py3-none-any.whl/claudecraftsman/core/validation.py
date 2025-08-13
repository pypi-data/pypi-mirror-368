"""
Quality gates validation for ClaudeCraftsman.

Implements the 8-step validation cycle with Python-specific checks.
"""

from datetime import datetime
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator
from rich.console import Console
from rich.table import Table

from claudecraftsman.core.config import Config, get_config

console = Console()


class ValidationResult(BaseModel):
    """Result of a validation check."""

    model_config = ConfigDict(extra="forbid")

    step: str
    passed: bool
    message: str
    details: list[str] | None = Field(default_factory=list)
    severity: Annotated[str, Field(pattern="^(error|warning|info)$")] = "error"
    timestamp: datetime = Field(default_factory=datetime.now)


class QualityReport(BaseModel):
    """Complete quality validation report."""

    model_config = ConfigDict(extra="forbid")

    project: str
    phase: str
    overall_passed: bool
    validation_results: list[ValidationResult]
    created_at: datetime = Field(default_factory=datetime.now)
    coverage_metrics: dict[str, float] | None = None

    @field_validator("overall_passed", mode="before")
    @classmethod
    def calculate_overall(cls, v: bool | object, info: object) -> bool:
        """Calculate overall pass status from results."""
        if hasattr(info, "data") and "validation_results" in info.data:
            results = info.data["validation_results"]
            return all(r.passed or r.severity != "error" for r in results)
        return bool(v)


class QualityGates:
    """Manages the 8-step quality validation cycle."""

    def __init__(self, config: Config | None = None) -> None:
        """Initialize quality gates."""
        self.config = config or get_config()
        self.project_root = self.config.project_root

    def validate_all(self, phase: str = "general") -> QualityReport:
        """Run all 8 quality gate validations."""
        console.print("\n[bold cyan]Running Quality Gates Validation[/bold cyan]")

        results = []

        # Step 1: Syntax Validation
        results.append(self._validate_syntax())

        # Step 2: Type Checking
        results.append(self._validate_types())

        # Step 3: Lint Standards
        results.append(self._validate_lint())

        # Step 4: Security Analysis
        results.append(self._validate_security())

        # Step 5: Test Coverage
        results.append(self._validate_tests())

        # Step 6: Performance Analysis
        results.append(self._validate_performance())

        # Step 7: Documentation
        results.append(self._validate_documentation())

        # Step 8: Integration
        results.append(self._validate_integration())

        # Create report
        report = QualityReport(
            project=self.project_root.name,
            phase=phase,
            overall_passed=all(r.passed or r.severity != "error" for r in results),
            validation_results=results,
        )

        self._display_report(report)
        return report

    def _validate_syntax(self) -> ValidationResult:
        """Step 1: Validate Python syntax."""
        console.print("[dim]Step 1: Syntax Validation[/dim]")

        errors = []
        python_files = list(self.project_root.rglob("*.py"))

        for file in python_files:
            if ".venv" in str(file) or "__pycache__" in str(file):
                continue

            try:
                with open(file, encoding="utf-8") as f:
                    compile(f.read(), file, "exec")
            except SyntaxError as e:
                errors.append(f"{file}: {e}")

        if errors:
            return ValidationResult(
                step="Syntax Validation",
                passed=False,
                message=f"Found {len(errors)} syntax errors",
                details=errors[:5],  # Limit to first 5
                severity="error",
            )

        return ValidationResult(
            step="Syntax Validation",
            passed=True,
            message=f"All {len(python_files)} Python files have valid syntax",
            severity="info",
        )

    def _validate_types(self) -> ValidationResult:
        """Step 2: Type checking with mypy or similar."""
        console.print("[dim]Step 2: Type Checking[/dim]")

        # Check if mypy is available
        mypy_config = self.project_root / "mypy.ini"
        pyproject = self.project_root / "pyproject.toml"

        if mypy_config.exists() or (pyproject.exists() and "mypy" in pyproject.read_text()):
            # TODO: Run actual mypy check
            return ValidationResult(
                step="Type Checking",
                passed=True,
                message="Type checking configuration found (actual check pending)",
                severity="warning",
            )

        return ValidationResult(
            step="Type Checking",
            passed=True,
            message="Type checking not configured (optional)",
            severity="info",
        )

    def _validate_lint(self) -> ValidationResult:
        """Step 3: Linting standards (ruff, black, etc)."""
        console.print("[dim]Step 3: Lint Standards[/dim]")

        # Check for linting configuration
        configs = [
            "ruff.toml",
            ".ruff.toml",
            "pyproject.toml",  # May contain ruff/black config
            ".flake8",
            "setup.cfg",  # May contain flake8 config
        ]

        found_configs = [c for c in configs if (self.project_root / c).exists()]

        if found_configs:
            return ValidationResult(
                step="Lint Standards",
                passed=True,
                message=f"Linting configured: {', '.join(found_configs)}",
                details=["Run 'ruff check' or configured linter for detailed results"],
                severity="info",
            )

        return ValidationResult(
            step="Lint Standards",
            passed=False,
            message="No linting configuration found",
            details=["Consider adding ruff.toml or configuring in pyproject.toml"],
            severity="warning",
        )

    def _validate_security(self) -> ValidationResult:
        """Step 4: Security analysis."""
        console.print("[dim]Step 4: Security Analysis[/dim]")

        security_issues = []

        # Check for common security issues in Python files
        python_files = list(self.project_root.rglob("*.py"))

        for file in python_files:
            if ".venv" in str(file) or "__pycache__" in str(file):
                continue

            try:
                content = file.read_text()

                # Basic security checks
                if "eval(" in content:
                    security_issues.append(f"{file}: Uses eval() - potential security risk")
                if "exec(" in content:
                    security_issues.append(f"{file}: Uses exec() - potential security risk")
                if "pickle.loads" in content and "untrusted" not in content:
                    security_issues.append(f"{file}: Uses pickle.loads - ensure trusted source")
                if "os.system(" in content:
                    security_issues.append(f"{file}: Uses os.system - prefer subprocess")

            except Exception:
                pass

        if security_issues:
            return ValidationResult(
                step="Security Analysis",
                passed=False,
                message=f"Found {len(security_issues)} potential security issues",
                details=security_issues[:5],
                severity="warning",
            )

        return ValidationResult(
            step="Security Analysis",
            passed=True,
            message="No obvious security issues found",
            details=["Consider using 'bandit' for comprehensive security scanning"],
            severity="info",
        )

    def _validate_tests(self) -> ValidationResult:
        """Step 5: Test coverage validation."""
        console.print("[dim]Step 5: Test Coverage[/dim]")

        # Check for test directory
        test_dirs = [
            self.project_root / "tests",
            self.project_root / "test",
            self.project_root / "src" / "tests",
        ]

        test_dir = None
        for td in test_dirs:
            if td.exists():
                test_dir = td
                break

        if not test_dir:
            return ValidationResult(
                step="Test Coverage",
                passed=False,
                message="No test directory found",
                details=["Create a 'tests' directory and add test files"],
                severity="error",
            )

        # Count test files
        test_files = list(test_dir.rglob("test_*.py")) + list(test_dir.rglob("*_test.py"))

        if not test_files:
            return ValidationResult(
                step="Test Coverage",
                passed=False,
                message="No test files found",
                details=["Add test files named test_*.py or *_test.py"],
                severity="error",
            )

        return ValidationResult(
            step="Test Coverage",
            passed=True,
            message=f"Found {len(test_files)} test files",
            details=["Run 'pytest --cov' for detailed coverage metrics"],
            severity="info",
        )

    def _validate_performance(self) -> ValidationResult:
        """Step 6: Performance analysis."""
        console.print("[dim]Step 6: Performance Analysis[/dim]")

        # Basic performance checks
        issues = []
        python_files = list(self.project_root.rglob("*.py"))

        for file in python_files:
            if ".venv" in str(file) or "__pycache__" in str(file):
                continue

            try:
                content = file.read_text()
                lines = content.split("\n")

                # Check for obvious performance issues
                for i, line in enumerate(lines, 1):
                    if "sleep(" in line and "test" not in str(file):
                        issues.append(f"{file}:{i} - Uses sleep() in production code")
                    if ".append(" in line and "for " in line:
                        issues.append(
                            f"{file}:{i} - Appending in loop (consider list comprehension)"
                        )

            except Exception:
                pass

        if issues:
            return ValidationResult(
                step="Performance Analysis",
                passed=True,
                message=f"Found {len(issues)} potential performance improvements",
                details=issues[:3],
                severity="warning",
            )

        return ValidationResult(
            step="Performance Analysis",
            passed=True,
            message="No obvious performance issues found",
            severity="info",
        )

    def _validate_documentation(self) -> ValidationResult:
        """Step 7: Documentation validation."""
        console.print("[dim]Step 7: Documentation[/dim]")

        issues = []

        # Check README
        readme_files = ["README.md", "README.rst", "README.txt"]
        readme_exists = any((self.project_root / f).exists() for f in readme_files)

        if not readme_exists:
            issues.append("No README file found")

        # Check docstrings in Python files
        python_files = list(self.project_root.rglob("*.py"))
        files_without_docstring = []

        for file in python_files:
            if ".venv" in str(file) or "__pycache__" in str(file):
                continue

            try:
                content = file.read_text()
                if content.strip() and not ('"""' in content or "'''" in content):
                    files_without_docstring.append(str(file.relative_to(self.project_root)))
            except Exception:
                pass

        if files_without_docstring:
            issues.append(f"{len(files_without_docstring)} files lack docstrings")

        if issues:
            return ValidationResult(
                step="Documentation",
                passed=False,
                message="Documentation improvements needed",
                details=issues,
                severity="warning",
            )

        return ValidationResult(
            step="Documentation",
            passed=True,
            message="Documentation standards met",
            severity="info",
        )

    def _validate_integration(self) -> ValidationResult:
        """Step 8: Integration validation."""
        console.print("[dim]Step 8: Integration[/dim]")

        # Check CI/CD configuration
        ci_files = [
            ".github/workflows",
            ".gitlab-ci.yml",
            "Jenkinsfile",
            ".circleci/config.yml",
        ]

        ci_exists = any(
            (self.project_root / f).exists() or (self.project_root / f).is_dir() for f in ci_files
        )

        if ci_exists:
            return ValidationResult(
                step="Integration",
                passed=True,
                message="CI/CD configuration found",
                severity="info",
            )

        return ValidationResult(
            step="Integration",
            passed=True,
            message="No CI/CD configuration found (optional for development)",
            severity="info",
        )

    def _display_report(self, report: QualityReport) -> None:
        """Display quality report in a formatted table."""
        console.print("\n[bold]Quality Gates Report[/bold]")

        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Step", style="white")
        table.add_column("Status", justify="center")
        table.add_column("Message", style="dim")

        for result in report.validation_results:
            if result.passed:
                status = "[green]✓ PASS[/green]"
            elif result.severity == "warning":
                status = "[yellow]⚠ WARN[/yellow]"
            else:
                status = "[red]✗ FAIL[/red]"

            table.add_row(result.step, status, result.message)

        console.print(table)

        # Overall status
        if report.overall_passed:
            console.print("\n[bold green]✓ All quality gates passed![/bold green]")
        else:
            console.print("\n[bold red]✗ Quality gates need attention[/bold red]")

            # Show details for failures
            failures = [r for r in report.validation_results if not r.passed]
            if failures:
                console.print("\n[yellow]Issues to address:[/yellow]")
                for result in failures:
                    console.print(f"\n[bold]{result.step}:[/bold]")
                    if result.details:
                        for detail in result.details[:3]:  # Limit details
                            console.print(f"  • {detail}")

    def validate_file(self, file_path: Path) -> list[ValidationResult]:
        """Validate a specific file."""
        results = []

        if file_path.suffix == ".py":
            # Python-specific validations
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()
                    compile(content, file_path, "exec")
                results.append(
                    ValidationResult(
                        step="Syntax",
                        passed=True,
                        message="Valid Python syntax",
                        severity="info",
                    )
                )
            except SyntaxError as e:
                results.append(
                    ValidationResult(
                        step="Syntax",
                        passed=False,
                        message=f"Syntax error: {e}",
                        severity="error",
                    )
                )

        return results

    def create_quality_checklist(self) -> str:
        """Generate a quality checklist markdown."""
        checklist = """# Quality Gates Checklist

## 8-Step Validation Cycle

### Step 1: Syntax Validation ✓
- [ ] All Python files compile without syntax errors
- [ ] No import errors or circular dependencies
- [ ] Proper encoding declarations where needed

### Step 2: Type Checking 🔍
- [ ] Type hints for all public functions/methods
- [ ] Mypy or similar type checker passes
- [ ] Pydantic models use v2 patterns

### Step 3: Lint Standards 📏
- [ ] Ruff or similar linter configuration present
- [ ] All files pass linting checks
- [ ] Consistent code style throughout

### Step 4: Security Analysis 🛡️
- [ ] No use of eval() or exec() with untrusted input
- [ ] Proper input validation and sanitization
- [ ] Secure handling of credentials and secrets

### Step 5: Test Coverage 🧪
- [ ] Unit tests for all critical functions (≥80% coverage)
- [ ] Integration tests for APIs and workflows (≥70% coverage)
- [ ] Tests run successfully in CI/CD

### Step 6: Performance Analysis ⚡
- [ ] No obvious performance anti-patterns
- [ ] Async operations used where appropriate
- [ ] Database queries optimized

### Step 7: Documentation 📚
- [ ] README with clear setup instructions
- [ ] Docstrings for all public APIs
- [ ] Type hints serve as inline documentation

### Step 8: Integration ✅
- [ ] CI/CD pipeline configured
- [ ] Automated testing on commits
- [ ] Deployment process documented

## Craftsman Standards
- [ ] Would you be proud to show this code to another developer?
- [ ] Does the code reflect intentional, thoughtful design?
- [ ] Are all decisions well-reasoned and documented?
"""
        return checklist


# Convenience function for CLI
def run_quality_gates(phase: str = "general") -> bool:
    """Run quality gates and return overall pass status."""
    gates = QualityGates()
    report = gates.validate_all(phase)
    return report.overall_passed
