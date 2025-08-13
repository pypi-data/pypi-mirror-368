"""Tests for framework enforcement functionality."""

import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest

from claudecraftsman.core.config import Config
from claudecraftsman.core.enforcement import (
    ComplianceReport,
    FrameworkEnforcer,
    HealthMetric,
    Violation,
    ViolationType,
)
from claudecraftsman.core.registry import DocumentEntry


@pytest.fixture
def config(tmp_path):
    """Create test configuration."""
    # Create test directory structure
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()

    docs_dir = claude_dir / "docs" / "current"
    docs_dir.mkdir(parents=True)

    agents_dir = claude_dir / "agents"
    agents_dir.mkdir()

    commands_dir = claude_dir / "commands"
    commands_dir.mkdir()

    context_dir = claude_dir / "context"
    context_dir.mkdir()

    # Create workflow state file
    workflow_state = context_dir / "WORKFLOW-STATE.md"
    workflow_state.write_text("# Workflow State\nStatus: Active")

    return Config(project_root=tmp_path, claude_dir=claude_dir, dev_mode=False)


@pytest.fixture
def enforcer(config):
    """Create test enforcer."""
    return FrameworkEnforcer(config)


class TestFrameworkEnforcer:
    """Test framework enforcement functionality."""

    def test_initialization(self, enforcer):
        """Test enforcer initialization."""
        assert enforcer.auto_correct is True
        assert enforcer.validation_interval == 300
        assert enforcer.last_validation is None
        assert enforcer.violations == []
        assert enforcer.health_metrics == {}

    def test_continuous_validation_start_stop(self, enforcer):
        """Test starting and stopping continuous validation."""
        # Start validation
        enforcer.validation_interval = 0.1  # Fast for testing
        enforcer.start_continuous_validation()

        assert enforcer._validation_thread is not None
        assert enforcer._validation_thread.is_alive()

        # Let it run briefly
        time.sleep(0.2)

        # Stop validation
        enforcer.stop_continuous_validation()
        time.sleep(0.1)

        assert not enforcer._validation_thread.is_alive()

    def test_naming_convention_violations(self, config, enforcer):
        """Test detection of naming convention violations."""
        # Create files with bad names
        bad_file1 = config.paths.docs_dir / "current" / "bad-name.md"
        bad_file1.write_text("# Bad name")

        bad_file2 = config.paths.docs_dir / "current" / "PRD-test.md"  # Missing date
        bad_file2.write_text("# Missing date")

        violations = enforcer._check_naming_conventions()

        # Should find at least the 2 bad files we created
        bad_files = [
            v
            for v in violations
            if "bad-name.md" in v.description or "PRD-test.md" in v.description
        ]
        assert len(bad_files) == 2
        assert all(v.type == ViolationType.NAMING_CONVENTION for v in violations)
        assert all(v.severity == "medium" for v in violations)

    def test_file_location_violations(self, config, enforcer):
        """Test detection of file location violations."""
        # Create implementation file in wrong location
        impl_file = config.paths.docs_dir / "current" / "IMPL-test-2025-01-01.md"
        impl_file.write_text("# Implementation doc")

        violations = enforcer._check_file_locations()

        assert len(violations) == 1
        assert violations[0].type == ViolationType.FILE_LOCATION
        assert violations[0].auto_correctable is True
        assert violations[0].correction_action == "move_to_implementation"

    def test_document_metadata_violations(self, config, enforcer):
        """Test detection of missing metadata."""
        # Create document without required metadata
        doc = config.paths.docs_dir / "current" / "PRD-test-2025-01-01.md"
        doc.write_text("# Test Document\nMissing metadata")

        violations = enforcer._check_document_metadata()

        assert len(violations) >= 2  # Missing Status and Created
        assert all(v.type == ViolationType.MISSING_METADATA for v in violations)

    def test_outdated_document_detection(self, config, enforcer):
        """Test detection of outdated documents."""
        # Mock registry with old completed document
        old_date = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")

        mock_entry = DocumentEntry(
            document="OLD-doc-2025-01-01.md",
            type="Plan",
            location="docs/current",
            created=old_date,
            status="Complete",
            purpose="Old document",
        )

        # Create the actual file
        old_file = config.paths.docs_dir / "current" / "OLD-doc-2025-01-01.md"
        old_file.write_text("# Old Document")

        with patch.object(enforcer.registry_manager, "parse_registry") as mock_parse:
            mock_parse.return_value = ([mock_entry], [])

            violations = enforcer._check_outdated_documents()

        assert len(violations) == 1
        assert violations[0].type == ViolationType.OUTDATED_DOCUMENT
        assert violations[0].auto_correctable is True
        assert violations[0].correction_action == "archive_document"

    def test_orphaned_files_detection(self, config, enforcer):
        """Test detection of orphaned files."""
        # Create unregistered file
        orphan = config.paths.docs_dir / "current" / "orphan.md"
        orphan.write_text("# Orphaned file")

        with patch.object(enforcer.registry_manager, "parse_registry") as mock_parse:
            mock_parse.return_value = ([], [])  # Empty registry

            violations = enforcer._check_orphaned_files()

        # Should find at least our orphan file
        orphan_violations = [v for v in violations if "orphan.md" in v.description]
        assert len(orphan_violations) == 1
        assert orphan_violations[0].type == ViolationType.ORPHANED_FILE

    def test_state_consistency_violations(self, enforcer):
        """Test detection of state inconsistencies."""
        # Mock inconsistent state
        mock_report = Mock()
        mock_report.is_consistent = False
        mock_report.issues = [{"description": "Phase mismatch"}, {"description": "Missing handoff"}]

        with patch.object(enforcer.state_manager, "check_consistency", return_value=mock_report):
            violations = enforcer._check_state_consistency()

        assert len(violations) == 2
        assert all(v.type == ViolationType.STALE_STATE for v in violations)
        assert all(v.auto_correctable is True for v in violations)

    def test_auto_correction(self, config, enforcer):
        """Test auto-correction of violations."""
        # Create test violations
        violations = [
            Violation(
                type=ViolationType.UNREGISTERED_DOCUMENT,
                severity="medium",
                description="Test",
                auto_correctable=True,
                correction_action="sync_registry",
            ),
            Violation(
                type=ViolationType.STALE_STATE,
                severity="high",
                description="State issue",
                auto_correctable=True,
                correction_action="repair_state",
            ),
            Violation(
                type=ViolationType.MISSING_METADATA,
                severity="medium",
                description="Missing metadata",
                auto_correctable=False,  # Not correctable
            ),
        ]

        enforcer.violations = violations.copy()

        with patch.object(enforcer.registry_manager, "sync_registry"):
            with patch.object(enforcer.state_manager, "repair_state"):
                corrected = enforcer.auto_correct_violations()

        assert len(corrected) == 2  # Only correctable ones
        assert len(enforcer.violations) == 1  # Non-correctable remains
        assert enforcer.violations[0].auto_correctable is False

    def test_health_metrics_calculation(self, config, enforcer):
        """Test health metrics calculation."""
        # Set up test state
        enforcer.violations = [
            Violation(type=ViolationType.NAMING_CONVENTION, severity="medium", description="Test"),
            Violation(type=ViolationType.FILE_LOCATION, severity="low", description="Test"),
        ]

        # Create test directory structure
        current_dir = config.paths.docs_dir / "current"
        current_dir.mkdir(parents=True, exist_ok=True)

        # Create a subdirectory with no files (to avoid unregistered documents)
        plans_dir = current_dir / "plans"
        plans_dir.mkdir(exist_ok=True)

        with patch.object(enforcer.registry_manager, "parse_registry") as mock_parse:
            mock_docs = [Mock() for _ in range(10)]  # 10 documents
            mock_parse.return_value = (mock_docs, [])

            with patch.object(enforcer.state_manager, "check_consistency") as mock_check:
                mock_check.return_value = Mock(is_consistent=True)

                enforcer.update_health_metrics()

        assert "document_health" in enforcer.health_metrics
        assert "state_health" in enforcer.health_metrics
        assert "registry_health" in enforcer.health_metrics
        assert "compliance_score" in enforcer.health_metrics

        # Check document health calculation
        doc_health = enforcer.health_metrics["document_health"]
        assert doc_health.value == 80.0  # 2 violations out of 10 docs = 80%
        assert doc_health.status == "healthy"  # Above 80% threshold

    def test_compliance_report_generation(self, config, enforcer):
        """Test compliance report generation."""
        # Set up test data
        enforcer.violations = [
            Violation(
                type=ViolationType.NAMING_CONVENTION,
                severity="critical",
                description="Critical issue",
                auto_correctable=True,
            )
        ]

        enforcer.health_metrics = {
            "compliance_score": HealthMetric(
                name="Overall Compliance",
                value=75.0,
                unit="%",
                status="warning",
                threshold_warning=85,
                threshold_critical=70,
            )
        }

        report = enforcer.generate_compliance_report()

        assert isinstance(report, ComplianceReport)
        assert len(report.violations_found) == 1
        assert report.compliance_score == 75.0
        assert len(report.recommendations) >= 2  # Critical violations + auto-correct

    def test_move_to_implementation(self, config, enforcer):
        """Test moving implementation files."""
        # Create implementation file in wrong location
        impl_file = config.paths.docs_dir / "current" / "IMPL-test-2025-01-01.md"
        impl_file.write_text("# Implementation")

        violation = Violation(
            type=ViolationType.FILE_LOCATION,
            severity="low",
            file_path=impl_file,
            description="Wrong location",
            auto_correctable=True,
            correction_action="move_to_implementation",
        )

        enforcer._move_to_implementation(violation)

        # Check file was moved
        assert not impl_file.exists()
        new_path = config.paths.docs_dir / "current" / "implementation" / impl_file.name
        assert new_path.exists()
        assert new_path.read_text() == "# Implementation"

    def test_health_status_calculation(self, enforcer):
        """Test health status calculation based on thresholds."""
        assert enforcer._get_health_status(95, 80, 60) == "healthy"
        assert enforcer._get_health_status(75, 80, 60) == "warning"
        assert enforcer._get_health_status(55, 80, 60) == "critical"

    def test_validate_framework_complete(self, config, enforcer):
        """Test complete framework validation."""
        # Create some test files
        doc1 = config.paths.docs_dir / "current" / "PRD-test-2025-01-01.md"
        doc1.write_text("# Test\nStatus: Active\nCreated: 2025-01-01\n## Overview")

        violations = enforcer.validate_framework()

        assert isinstance(violations, list)
        assert enforcer.last_validation is not None
        assert enforcer.violations == violations

    def test_validation_error_handling(self, enforcer):
        """Test error handling in validation loop."""
        # Mock validation to raise error
        with patch.object(enforcer, "validate_framework", side_effect=Exception("Test error")):
            # Start validation with short interval
            enforcer.validation_interval = 0.1
            enforcer.start_continuous_validation()

            # Let it run and handle error
            time.sleep(0.2)

            # Should still be running despite error
            assert enforcer._validation_thread.is_alive()

            # Stop validation
            enforcer.stop_continuous_validation()
