"""Tests for health command CLI."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from typer.testing import CliRunner

from claudecraftsman.cli.commands.health import app
from claudecraftsman.core.enforcement import ComplianceReport, Violation, ViolationType


@pytest.fixture
def runner():
    """Create CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_enforcer():
    """Create mock enforcer."""
    enforcer = Mock()
    enforcer.violations = []
    enforcer.health_metrics = {}
    enforcer.validation_interval = 300
    enforcer.auto_correct = True
    return enforcer


@pytest.fixture
def mock_config():
    """Create mock config."""
    config = Mock()
    config.paths = Mock()
    config.paths.claude_dir = Path("/test/.claude")
    config.paths.docs_dir = Path("/test/.claude/docs")
    return config


class TestHealthCommand:
    """Test health command functionality."""

    @patch("claudecraftsman.cli.commands.health.get_config")
    @patch("claudecraftsman.cli.commands.health.FrameworkEnforcer")
    def test_health_check_basic(
        self, mock_enforcer_class, mock_get_config, runner, mock_config, mock_enforcer
    ):
        """Test basic health check command."""
        mock_get_config.return_value = mock_config
        mock_enforcer_class.return_value = mock_enforcer

        # Mock clean validation
        mock_enforcer.validate_framework.return_value = []
        mock_enforcer.update_health_metrics.return_value = None
        mock_enforcer.display_health_dashboard.return_value = None

        result = runner.invoke(app, ["check"])

        assert result.exit_code == 0
        assert "Running framework health check" in result.output
        mock_enforcer.validate_framework.assert_called_once()
        mock_enforcer.update_health_metrics.assert_called_once()
        mock_enforcer.display_health_dashboard.assert_called_once()

    @patch("claudecraftsman.cli.commands.health.get_config")
    @patch("claudecraftsman.cli.commands.health.FrameworkEnforcer")
    def test_health_check_with_violations(
        self, mock_enforcer_class, mock_get_config, runner, mock_config, mock_enforcer
    ):
        """Test health check with violations."""
        mock_get_config.return_value = mock_config
        mock_enforcer_class.return_value = mock_enforcer

        # Mock violations
        violations = [
            Violation(
                type=ViolationType.NAMING_CONVENTION,
                severity="medium",
                file_path=Path("/test/bad-file.md"),
                description="Bad naming",
                auto_correctable=True,
            ),
            Violation(
                type=ViolationType.MISSING_METADATA,
                severity="high",
                description="Missing metadata",
                auto_correctable=False,
            ),
        ]
        mock_enforcer.validate_framework.return_value = violations

        result = runner.invoke(app, ["check", "--detailed"])

        assert result.exit_code == 0
        assert "Active Violations:" in result.output
        assert "naming_convention" in result.output
        assert "missing_metadata" in result.output
        assert "✓ Auto-correctable" in result.output

    @patch("claudecraftsman.cli.commands.health.get_config")
    @patch("claudecraftsman.cli.commands.health.FrameworkEnforcer")
    def test_health_check_auto_correct(
        self, mock_enforcer_class, mock_get_config, runner, mock_config, mock_enforcer
    ):
        """Test health check with auto-correction."""
        mock_get_config.return_value = mock_config
        mock_enforcer_class.return_value = mock_enforcer

        # Mock correctable violations
        violations = [
            Violation(
                type=ViolationType.UNREGISTERED_DOCUMENT,
                severity="medium",
                description="Unregistered",
                auto_correctable=True,
            )
        ]
        mock_enforcer.validate_framework.return_value = violations
        mock_enforcer.auto_correct_violations.return_value = violations

        result = runner.invoke(app, ["check", "--auto-correct"])

        assert result.exit_code == 0
        assert "Auto-correcting 1 violations" in result.output
        assert "✓ Corrected 1 violations" in result.output
        assert "Re-validating after corrections" in result.output

        # Should validate twice - before and after correction
        assert mock_enforcer.validate_framework.call_count == 2
        mock_enforcer.auto_correct_violations.assert_called_once()

    @patch("claudecraftsman.cli.commands.health.get_config")
    @patch("claudecraftsman.cli.commands.health.FrameworkEnforcer")
    def test_health_monitor(
        self, mock_enforcer_class, mock_get_config, runner, mock_config, mock_enforcer
    ):
        """Test health monitoring command."""
        mock_get_config.return_value = mock_config
        mock_enforcer_class.return_value = mock_enforcer

        result = runner.invoke(app, ["monitor", "--interval", "600", "--no-auto-correct"])

        assert result.exit_code == 0
        assert "Starting continuous health monitoring" in result.output
        assert "Interval: 600 seconds" in result.output
        assert "Auto-correction: disabled" in result.output
        assert "✓ Health monitoring started" in result.output

        mock_enforcer.start_continuous_validation.assert_called_once()
        assert mock_enforcer.validation_interval == 600
        assert mock_enforcer.auto_correct is False

    @patch("claudecraftsman.cli.commands.health.get_config")
    @patch("claudecraftsman.cli.commands.health.FrameworkEnforcer")
    def test_health_report(
        self, mock_enforcer_class, mock_get_config, runner, mock_config, mock_enforcer
    ):
        """Test compliance report generation."""
        mock_get_config.return_value = mock_config
        mock_enforcer_class.return_value = mock_enforcer

        # Mock report
        mock_report = ComplianceReport(
            total_files_scanned=50,
            violations_found=[],
            violations_corrected=[],
            health_metrics=[],
            compliance_score=95.0,
            recommendations=["Keep up the good work!"],
        )
        mock_enforcer.generate_compliance_report.return_value = mock_report

        result = runner.invoke(app, ["report"])

        assert result.exit_code == 0
        assert "Generating compliance report" in result.output
        assert "Files Scanned: 50" in result.output
        assert "Compliance Score: 95.0%" in result.output
        assert "Keep up the good work!" in result.output

    @patch("claudecraftsman.cli.commands.health.get_config")
    @patch("claudecraftsman.cli.commands.health.FrameworkEnforcer")
    def test_health_report_save_to_file(
        self, mock_enforcer_class, mock_get_config, runner, mock_config, mock_enforcer, tmp_path
    ):
        """Test saving compliance report to file."""
        mock_get_config.return_value = mock_config
        mock_enforcer_class.return_value = mock_enforcer

        # Mock report
        mock_report = ComplianceReport(
            total_files_scanned=50,
            violations_found=[],
            violations_corrected=[],
            health_metrics=[],
            compliance_score=95.0,
            recommendations=[],
        )
        mock_enforcer.generate_compliance_report.return_value = mock_report

        output_file = tmp_path / "report.json"
        result = runner.invoke(app, ["report", "--output", str(output_file)])

        assert result.exit_code == 0
        assert "Report saved to" in result.output
        assert str(output_file) in result.output
        assert output_file.exists()

        # Check file content
        import json

        report_data = json.loads(output_file.read_text())
        assert report_data["total_files_scanned"] == 50
        assert report_data["compliance_score"] == 95.0

    @patch("claudecraftsman.cli.commands.health.get_config")
    @patch("claudecraftsman.cli.commands.health.FrameworkEnforcer")
    def test_health_violations_list(
        self, mock_enforcer_class, mock_get_config, runner, mock_config, mock_enforcer
    ):
        """Test listing violations."""
        mock_get_config.return_value = mock_config
        mock_enforcer_class.return_value = mock_enforcer

        # Mock various violations
        violations = [
            Violation(
                type=ViolationType.NAMING_CONVENTION,
                severity="critical",
                description="Critical naming issue",
                auto_correctable=False,
            ),
            Violation(
                type=ViolationType.FILE_LOCATION,
                severity="medium",
                file_path=Path("/test/file.md"),
                description="Wrong location",
                auto_correctable=True,
            ),
            Violation(
                type=ViolationType.MISSING_METADATA,
                severity="low",
                description="Missing field",
                auto_correctable=False,
            ),
        ]
        mock_enforcer.validate_framework.return_value = violations

        result = runner.invoke(app, ["violations"])

        assert result.exit_code == 0
        assert "Found 3 violations:" in result.output
        assert "CRITICAL (1)" in result.output
        assert "MEDIUM (1)" in result.output
        assert "LOW (1)" in result.output
        assert "Auto-correctable" in result.output

    @patch("claudecraftsman.cli.commands.health.get_config")
    @patch("claudecraftsman.cli.commands.health.FrameworkEnforcer")
    def test_health_violations_filter_by_type(
        self, mock_enforcer_class, mock_get_config, runner, mock_config, mock_enforcer
    ):
        """Test filtering violations by type."""
        mock_get_config.return_value = mock_config
        mock_enforcer_class.return_value = mock_enforcer

        # Mock violations
        violations = [
            Violation(
                type=ViolationType.NAMING_CONVENTION,
                severity="medium",
                description="Naming issue 1",
                auto_correctable=False,
            ),
            Violation(
                type=ViolationType.NAMING_CONVENTION,
                severity="medium",
                description="Naming issue 2",
                auto_correctable=False,
            ),
            Violation(
                type=ViolationType.FILE_LOCATION,
                severity="low",
                description="Location issue",
                auto_correctable=True,
            ),
        ]
        mock_enforcer.validate_framework.return_value = violations

        result = runner.invoke(app, ["violations", "--type", "naming_convention"])

        assert result.exit_code == 0
        assert "Found 2 violations:" in result.output
        assert "Naming issue 1" in result.output
        assert "Naming issue 2" in result.output
        assert "Location issue" not in result.output

    @patch("claudecraftsman.cli.commands.health.get_config")
    @patch("claudecraftsman.cli.commands.health.FrameworkEnforcer")
    def test_health_violations_filter_by_severity(
        self, mock_enforcer_class, mock_get_config, runner, mock_config, mock_enforcer
    ):
        """Test filtering violations by severity."""
        mock_get_config.return_value = mock_config
        mock_enforcer_class.return_value = mock_enforcer

        # Mock violations
        violations = [
            Violation(
                type=ViolationType.NAMING_CONVENTION,
                severity="critical",
                description="Critical issue",
                auto_correctable=False,
            ),
            Violation(
                type=ViolationType.FILE_LOCATION,
                severity="medium",
                description="Medium issue",
                auto_correctable=True,
            ),
        ]
        mock_enforcer.validate_framework.return_value = violations

        result = runner.invoke(app, ["violations", "--severity", "critical"])

        assert result.exit_code == 0
        assert "Found 1 violations:" in result.output
        assert "Critical issue" in result.output
        assert "Medium issue" not in result.output

    @patch("claudecraftsman.cli.commands.health.get_config")
    @patch("claudecraftsman.cli.commands.health.FrameworkEnforcer")
    def test_health_no_violations(
        self, mock_enforcer_class, mock_get_config, runner, mock_config, mock_enforcer
    ):
        """Test when no violations are found."""
        mock_get_config.return_value = mock_config
        mock_enforcer_class.return_value = mock_enforcer

        mock_enforcer.validate_framework.return_value = []

        result = runner.invoke(app, ["violations"])

        assert result.exit_code == 0
        assert "✓ No violations found" in result.output
