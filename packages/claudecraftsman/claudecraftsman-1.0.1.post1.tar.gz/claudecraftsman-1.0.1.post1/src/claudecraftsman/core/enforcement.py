"""
Framework self-enforcement module.

Provides continuous validation, auto-correction, and health monitoring
for the ClaudeCraftsman framework.
"""

import threading
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field
from rich.console import Console
from rich.table import Table

from claudecraftsman.core.config import get_config
from claudecraftsman.core.registry import RegistryManager
from claudecraftsman.core.state_enhanced import EnhancedStateManager
from claudecraftsman.core.validation import QualityGates
from claudecraftsman.utils.logging import logger

console = Console()


class ViolationType(str, Enum):
    """Types of framework violations."""

    NAMING_CONVENTION = "naming_convention"
    FILE_LOCATION = "file_location"
    MISSING_METADATA = "missing_metadata"
    OUTDATED_DOCUMENT = "outdated_document"
    ORPHANED_FILE = "orphaned_file"
    UNREGISTERED_DOCUMENT = "unregistered_document"
    INCOMPLETE_HANDOFF = "incomplete_handoff"
    STALE_STATE = "stale_state"
    MISSING_CITATION = "missing_citation"
    QUALITY_GATE_FAILURE = "quality_gate_failure"


class Violation(BaseModel):
    """Represents a framework violation."""

    model_config = ConfigDict(extra="forbid")

    type: ViolationType
    severity: str = Field(pattern="^(critical|high|medium|low)$")
    file_path: Path | None = None
    description: str
    auto_correctable: bool = False
    correction_action: str | None = None
    detected_at: datetime = Field(default_factory=datetime.now)


class HealthMetric(BaseModel):
    """Framework health metric."""

    model_config = ConfigDict(extra="forbid")

    name: str
    value: float
    unit: str
    status: str = Field(pattern="^(healthy|warning|critical)$")
    threshold_warning: float
    threshold_critical: float
    last_updated: datetime = Field(default_factory=datetime.now)


class ComplianceReport(BaseModel):
    """Framework compliance report."""

    model_config = ConfigDict(extra="forbid")

    timestamp: datetime = Field(default_factory=datetime.now)
    total_files_scanned: int
    violations_found: list[Violation]
    violations_corrected: list[Violation]
    health_metrics: list[HealthMetric]
    compliance_score: float  # 0-100
    recommendations: list[str]


class FrameworkEnforcer:
    """Enforces framework standards with continuous validation."""

    def __init__(self, config=None) -> None:
        """Initialize framework enforcer."""
        self.config = config or get_config()
        self.registry_manager = RegistryManager(self.config)
        self.state_manager = EnhancedStateManager(self.config)
        self.quality_gates = QualityGates()

        # Enforcement settings
        self.auto_correct = True
        self.validation_interval = 300  # 5 minutes
        self.last_validation: datetime | None = None
        self.violations: list[Violation] = []
        self.health_metrics: dict[str, HealthMetric] = {}

        # Background validation
        self._validation_thread: threading.Thread | None = None
        self._stop_validation = threading.Event()

    def start_continuous_validation(self) -> None:
        """Start background validation thread."""
        if self._validation_thread and self._validation_thread.is_alive():
            logger.info("Continuous validation already running")
            return

        self._stop_validation.clear()
        self._validation_thread = threading.Thread(target=self._validation_loop, daemon=True)
        self._validation_thread.start()
        logger.info("Started continuous framework validation")

    def stop_continuous_validation(self) -> None:
        """Stop background validation thread."""
        if self._validation_thread and self._validation_thread.is_alive():
            self._stop_validation.set()
            self._validation_thread.join(timeout=5)
            logger.info("Stopped continuous framework validation")

    def _validation_loop(self) -> None:
        """Background validation loop."""
        while not self._stop_validation.is_set():
            try:
                # Run validation
                self.validate_framework()

                # Auto-correct if enabled
                if self.auto_correct:
                    self.auto_correct_violations()

                # Update health metrics
                self.update_health_metrics()

                # Wait for next interval
                self._stop_validation.wait(self.validation_interval)

            except Exception as e:
                logger.error(f"Validation loop error: {e}")
                self._stop_validation.wait(60)  # Wait a minute before retry

    def validate_framework(self) -> list[Violation]:
        """Validate framework standards and detect violations."""
        violations: list[Violation] = []

        # Check naming conventions
        violations.extend(self._check_naming_conventions())

        # Check file locations
        violations.extend(self._check_file_locations())

        # Check document metadata
        violations.extend(self._check_document_metadata())

        # Check for outdated documents
        violations.extend(self._check_outdated_documents())

        # Check for orphaned files
        violations.extend(self._check_orphaned_files())

        # Check registry synchronization
        violations.extend(self._check_registry_sync())

        # Check state consistency
        violations.extend(self._check_state_consistency())

        # Check quality gates
        violations.extend(self._check_quality_gates())

        self.violations = violations
        self.last_validation = datetime.now()

        return violations

    def _check_naming_conventions(self) -> list[Violation]:
        """Check file naming conventions."""
        violations: list[Violation] = []

        # Expected patterns
        patterns = {
            "docs/current": r"^(PRD|SPEC|PLAN|IMPL|BDD)-[\w-]+-\d{4}-\d{2}-\d{2}\.md$",
            "agents": r"^[\w-]+\.md$",
            "commands": r"^[\w-]+\.md$",
        }

        for location, pattern in patterns.items():
            dir_path = self.config.paths.claude_dir / location
            if not dir_path.exists():
                continue

            import re

            regex = re.compile(pattern)

            for file_path in dir_path.rglob("*.md"):
                if not regex.match(file_path.name):
                    violations.append(
                        Violation(
                            type=ViolationType.NAMING_CONVENTION,
                            severity="medium",
                            file_path=file_path,
                            description=f"File '{file_path.name}' does not follow naming convention",
                            auto_correctable=False,
                        )
                    )

        return violations

    def _check_file_locations(self) -> list[Violation]:
        """Check files are in correct locations."""
        violations = []

        # Check for misplaced files
        docs_current = self.config.paths.docs_dir / "current"
        if docs_current.exists():
            for file_path in docs_current.glob("*.md"):
                # Check if implementation files are in wrong location
                if file_path.name.startswith("IMPL-") and "implementation" not in str(
                    file_path.parent
                ):
                    violations.append(
                        Violation(
                            type=ViolationType.FILE_LOCATION,
                            severity="low",
                            file_path=file_path,
                            description="Implementation document should be in 'implementation' subdirectory",
                            auto_correctable=True,
                            correction_action="move_to_implementation",
                        )
                    )

        return violations

    def _check_document_metadata(self) -> list[Violation]:
        """Check for missing document metadata."""
        violations = []

        # Required metadata patterns
        required_metadata = [
            "Status:",
            "Created:",
            "## Overview",
        ]

        docs_dir = self.config.paths.docs_dir / "current"
        if docs_dir.exists():
            for file_path in docs_dir.rglob("*.md"):
                try:
                    content = file_path.read_text()
                    for metadata in required_metadata:
                        if metadata not in content:
                            violations.append(
                                Violation(
                                    type=ViolationType.MISSING_METADATA,
                                    severity="medium",
                                    file_path=file_path,
                                    description=f"Missing required metadata: {metadata}",
                                    auto_correctable=False,
                                )
                            )
                except Exception as e:
                    logger.warning(f"Could not read {file_path}: {e}")

        return violations

    def _check_outdated_documents(self) -> list[Violation]:
        """Check for documents that should be archived."""
        violations = []

        # Check age of completed documents
        threshold_days = 7
        cutoff_date = datetime.now() - timedelta(days=threshold_days)

        active_docs, _ = self.registry_manager.parse_registry()
        for entry in active_docs:
            if entry.status == "Complete":
                try:
                    created_date = datetime.strptime(entry.created, "%Y-%m-%d")
                    if created_date < cutoff_date:
                        file_path = self.config.paths.claude_dir / entry.location / entry.document
                        if file_path.exists():
                            violations.append(
                                Violation(
                                    type=ViolationType.OUTDATED_DOCUMENT,
                                    severity="low",
                                    file_path=file_path,
                                    description=f"Completed document older than {threshold_days} days should be archived",
                                    auto_correctable=True,
                                    correction_action="archive_document",
                                )
                            )
                except Exception as e:
                    logger.warning(f"Could not check date for {entry.document}: {e}")

        return violations

    def _check_orphaned_files(self) -> list[Violation]:
        """Check for orphaned files not in registry."""
        violations = []

        # Get all markdown files in docs
        docs_dir = self.config.paths.docs_dir
        if docs_dir.exists():
            all_files = set()
            for file_path in docs_dir.rglob("*.md"):
                if "archive" not in str(file_path):
                    all_files.add(file_path.name)

            # Get files in registry
            active_docs, _ = self.registry_manager.parse_registry()
            registered_files = {entry.document for entry in active_docs}

            # Find orphaned files
            orphaned = all_files - registered_files - {"registry.md"}
            for filename in orphaned:
                violations.append(
                    Violation(
                        type=ViolationType.ORPHANED_FILE,
                        severity="high",
                        file_path=None,
                        description=f"File '{filename}' not found in registry",
                        auto_correctable=True,
                        correction_action="add_to_registry",
                    )
                )

        return violations

    def _check_registry_sync(self) -> list[Violation]:
        """Check if registry is synchronized."""
        violations = []

        try:
            # Get registered documents
            active_docs, _ = self.registry_manager.parse_registry()
            existing_docs = {doc.document for doc in active_docs}

            # Find unregistered documents
            current_dir = self.registry_manager.docs_dir / "current"
            if current_dir.exists():
                for subdir in current_dir.iterdir():
                    if subdir.is_dir() and subdir.name not in ["archive"]:
                        for filepath in subdir.glob("*.md"):
                            if (
                                filepath.name not in existing_docs
                                and filepath.name != "registry.md"
                            ):
                                violations.append(
                                    Violation(
                                        type=ViolationType.UNREGISTERED_DOCUMENT,
                                        severity="medium",
                                        file_path=filepath,
                                        description="Document not in registry",
                                        auto_correctable=True,
                                        correction_action="sync_registry",
                                    )
                                )
        except Exception as e:
            logger.warning(f"Could not check registry sync: {e}")

        return violations

    def _check_state_consistency(self) -> list[Violation]:
        """Check workflow state consistency."""
        violations = []

        # Check state consistency
        report = self.state_manager.check_consistency()
        if not report.is_consistent:
            for issue in report.issues:
                violations.append(
                    Violation(
                        type=ViolationType.STALE_STATE,
                        severity="high",
                        file_path=self.state_manager.workflow_state_file,
                        description=f"State inconsistency: {issue['description']}",
                        auto_correctable=True,
                        correction_action="repair_state",
                    )
                )

        return violations

    def _check_quality_gates(self) -> list[Violation]:
        """Check quality gate compliance."""
        violations = []

        # Run quality validation on recent files
        recent_files = []
        cutoff_date = datetime.now() - timedelta(hours=24)

        src_dir = self.config.project_root / "src"
        if src_dir.exists():
            for file_path in src_dir.rglob("*.py"):
                if file_path.stat().st_mtime > cutoff_date.timestamp():
                    recent_files.append(file_path)

        # Check each recent file
        for file_path in recent_files[:10]:  # Limit to 10 files
            try:
                results = self.quality_gates.validate_file(file_path)
                for result in results:
                    if not result.passed and result.severity == "error":
                        violations.append(
                            Violation(
                                type=ViolationType.QUALITY_GATE_FAILURE,
                                severity="medium",
                                file_path=file_path,
                                description=f"Quality issue: {result.message}",
                                auto_correctable=False,
                            )
                        )
            except Exception as e:
                logger.warning(f"Could not validate {file_path}: {e}")

        return violations

    def auto_correct_violations(self) -> list[Violation]:
        """Auto-correct violations where possible."""
        corrected = []

        for violation in self.violations:
            if not violation.auto_correctable:
                continue

            try:
                if violation.correction_action == "move_to_implementation":
                    self._move_to_implementation(violation)
                    corrected.append(violation)
                elif violation.correction_action == "archive_document":
                    self._archive_document(violation)
                    corrected.append(violation)
                elif violation.correction_action == "sync_registry":
                    self.registry_manager.sync_registry()
                    corrected.append(violation)
                elif violation.correction_action == "repair_state":
                    self.state_manager.repair_state()
                    corrected.append(violation)
                elif violation.correction_action == "add_to_registry":
                    self._add_to_registry(violation)
                    corrected.append(violation)

            except Exception as e:
                logger.error(f"Failed to correct violation: {e}")

        # Remove corrected violations
        self.violations = [v for v in self.violations if v not in corrected]

        return corrected

    def _move_to_implementation(self, violation: Violation) -> None:
        """Move implementation file to correct location."""
        if not violation.file_path:
            return

        impl_dir = violation.file_path.parent / "implementation"
        impl_dir.mkdir(exist_ok=True)

        new_path = impl_dir / violation.file_path.name
        violation.file_path.rename(new_path)

        logger.info(f"Moved {violation.file_path} to {new_path}")

    def _archive_document(self, violation: Violation) -> None:
        """Archive outdated document."""
        if not violation.file_path:
            return

        from claudecraftsman.core.archival import DocumentArchiver

        archiver = DocumentArchiver(self.config)

        archived = archiver.archive_document(violation.file_path, "Outdated document")
        if archived:
            logger.info(f"Archived {violation.file_path}")

    def _add_to_registry(self, violation: Violation) -> None:
        """Add orphaned file to registry."""
        # Extract filename from description
        import re

        match = re.search(r"File '(.+?)' not found", violation.description)
        if match:
            filename = match.group(1)
            # Use sync to add it
            self.registry_manager.sync_registry()

    def update_health_metrics(self) -> None:
        """Update framework health metrics."""
        # Document health
        active_docs, _ = self.registry_manager.parse_registry()
        total_docs = len(active_docs)
        violations_count = len(self.violations)

        self.health_metrics["document_health"] = HealthMetric(
            name="Document Health",
            value=100 - (violations_count / max(total_docs, 1) * 100),
            unit="%",
            status=self._get_health_status(
                100 - (violations_count / max(total_docs, 1) * 100), 80, 60
            ),
            threshold_warning=80,
            threshold_critical=60,
        )

        # State health
        state_consistent = self.state_manager.check_consistency().is_consistent
        self.health_metrics["state_health"] = HealthMetric(
            name="State Health",
            value=100 if state_consistent else 0,
            unit="%",
            status="healthy" if state_consistent else "critical",
            threshold_warning=100,
            threshold_critical=100,
        )

        # Registry health
        try:
            # Count unregistered documents using same logic as _check_registry_sync
            active_docs_set = {doc.document for doc in active_docs}
            unregistered = 0
            current_dir = self.registry_manager.docs_dir / "current"
            if current_dir.exists():
                for subdir in current_dir.iterdir():
                    if subdir.is_dir() and subdir.name not in ["archive"]:
                        for filepath in subdir.glob("*.md"):
                            if (
                                filepath.name not in active_docs_set
                                and filepath.name != "registry.md"
                            ):
                                unregistered += 1
            registry_health = 100 - (unregistered / max(total_docs, 1) * 100)
        except:
            registry_health = 100

        self.health_metrics["registry_health"] = HealthMetric(
            name="Registry Health",
            value=registry_health,
            unit="%",
            status=self._get_health_status(registry_health, 90, 70),
            threshold_warning=90,
            threshold_critical=70,
        )

        # Overall compliance
        compliance_score = sum(m.value for m in self.health_metrics.values()) / len(
            self.health_metrics
        )
        self.health_metrics["compliance_score"] = HealthMetric(
            name="Overall Compliance",
            value=compliance_score,
            unit="%",
            status=self._get_health_status(compliance_score, 85, 70),
            threshold_warning=85,
            threshold_critical=70,
        )

    def _get_health_status(self, value: float, warning: float, critical: float) -> str:
        """Get health status based on thresholds."""
        if value >= warning:
            return "healthy"
        elif value >= critical:
            return "warning"
        else:
            return "critical"

    def generate_compliance_report(self) -> ComplianceReport:
        """Generate comprehensive compliance report."""
        # Count files scanned
        total_files = 0
        for path in [
            self.config.paths.docs_dir,
            self.config.paths.claude_dir / "agents",
            self.config.paths.claude_dir / "commands",
            self.config.project_root / "src",
        ]:
            if path.exists():
                total_files += sum(1 for _ in path.rglob("*") if _.is_file())

        # Generate recommendations
        recommendations = []

        critical_violations = [v for v in self.violations if v.severity == "critical"]
        if critical_violations:
            recommendations.append(
                f"Address {len(critical_violations)} critical violations immediately"
            )

        auto_correctable = [v for v in self.violations if v.auto_correctable]
        if auto_correctable:
            recommendations.append(
                f"Enable auto-correction to fix {len(auto_correctable)} violations automatically"
            )

        if (
            self.health_metrics.get(
                "compliance_score",
                HealthMetric(
                    name="",
                    value=100,
                    unit="%",
                    status="healthy",
                    threshold_warning=85,
                    threshold_critical=70,
                ),
            ).value
            < 85
        ):
            recommendations.append("Schedule regular framework maintenance to improve compliance")

        return ComplianceReport(
            total_files_scanned=total_files,
            violations_found=self.violations,
            violations_corrected=[],
            health_metrics=list(self.health_metrics.values()),
            compliance_score=self.health_metrics.get(
                "compliance_score",
                HealthMetric(
                    name="",
                    value=0,
                    unit="%",
                    status="critical",
                    threshold_warning=85,
                    threshold_critical=70,
                ),
            ).value,
            recommendations=recommendations,
        )

    def display_health_dashboard(self) -> None:
        """Display framework health dashboard."""
        console.print("\n[bold cyan]ClaudeCraftsman Framework Health Dashboard[/bold cyan]\n")

        # Health metrics table
        table = Table(title="Health Metrics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", justify="right")
        table.add_column("Status", justify="center")

        for metric in self.health_metrics.values():
            status_color = {"healthy": "green", "warning": "yellow", "critical": "red"}[
                metric.status
            ]

            table.add_row(
                metric.name,
                f"{metric.value:.1f}{metric.unit}",
                f"[{status_color}]{metric.status.upper()}[/{status_color}]",
            )

        console.print(table)

        # Violations summary
        if self.violations:
            console.print(f"\n[yellow]Active Violations: {len(self.violations)}[/yellow]")

            by_severity: dict[str, list[Violation]] = {}
            for v in self.violations:
                by_severity.setdefault(v.severity, []).append(v)

            for severity in ["critical", "high", "medium", "low"]:
                if severity in by_severity:
                    color = {"critical": "red", "high": "yellow", "medium": "cyan", "low": "white"}[
                        severity
                    ]
                    console.print(
                        f"  [{color}]{severity.capitalize()}: {len(by_severity[severity])}[/{color}]"
                    )
        else:
            console.print("\n[green]✓ No active violations[/green]")

        # Last check time
        if self.last_validation:
            age = datetime.now() - self.last_validation
            console.print(f"\n[dim]Last checked: {age.seconds // 60} minutes ago[/dim]")
