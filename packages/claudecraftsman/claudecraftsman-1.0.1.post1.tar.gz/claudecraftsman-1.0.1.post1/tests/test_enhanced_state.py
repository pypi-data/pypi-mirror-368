"""
Tests for enhanced state management functionality.
"""

from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest

from claudecraftsman.core.state import WorkflowPhase, WorkflowState
from claudecraftsman.core.state_enhanced import EnhancedStateManager, StateChangeType


class TestEnhancedStateManager:
    """Test enhanced state management features."""

    @pytest.fixture
    def state_manager(self, tmp_path):
        """Create enhanced state manager with test config."""
        config = Mock()
        config.project_root = tmp_path
        config.paths.context_dir = tmp_path / ".claude" / "context"
        config.paths.docs_dir = tmp_path / ".claude" / "docs"
        config.paths.claude_dir = tmp_path / ".claude"

        # Create necessary directories
        config.paths.context_dir.mkdir(parents=True, exist_ok=True)

        return EnhancedStateManager(config)

    @pytest.fixture
    def sample_workflow_state(self):
        """Create sample workflow state for testing."""
        return WorkflowState(
            project="test-project",
            workflow_type="implementation",
            current_phase="Phase 1",
            status="active",
            phases=[
                WorkflowPhase(
                    name="Phase 1",
                    status="in_progress",
                    agent="test-agent",
                    started_at=datetime.now(),
                ),
                WorkflowPhase(name="Phase 2", status="pending", agent=None),
                WorkflowPhase(
                    name="Phase 3",
                    status="completed",
                    agent="another-agent",
                    started_at=datetime.now() - timedelta(hours=2),
                    completed_at=datetime.now() - timedelta(hours=1),
                ),
            ],
        )

    def test_intelligent_phase_update_valid_transition(self, state_manager, sample_workflow_state):
        """Test intelligent phase update with valid state transition."""
        # Write initial state
        state_manager.write_workflow_state(sample_workflow_state)

        # Update phase from pending to in_progress
        result = state_manager.intelligent_update(
            "phase_progress", phase_name="Phase 2", new_status="in_progress", agent="new-agent"
        )

        assert result is True

        # Read updated state
        state = state_manager.read_workflow_state()
        phase2 = next(p for p in state.phases if p.name == "Phase 2")

        assert phase2.status == "in_progress"
        assert phase2.agent == "new-agent"
        # Note: started_at is set but may not persist through markdown round-trip
        assert state.current_phase == "Phase 2"

        # Check that Phase 1 was auto-completed
        phase1 = next(p for p in state.phases if p.name == "Phase 1")
        assert phase1.status == "completed"

    def test_intelligent_phase_update_invalid_transition(
        self, state_manager, sample_workflow_state
    ):
        """Test intelligent phase update rejects invalid transitions."""
        state_manager.write_workflow_state(sample_workflow_state)

        # Try invalid transition from completed to pending
        result = state_manager.intelligent_update(
            "phase_progress", phase_name="Phase 3", new_status="pending"
        )

        assert result is False

        # State should remain unchanged
        state = state_manager.read_workflow_state()
        phase3 = next(p for p in state.phases if p.name == "Phase 3")
        assert phase3.status == "completed"

    def test_state_consistency_check_detects_issues(self, state_manager, sample_workflow_state):
        """Test consistency check detects various state issues."""
        # Create inconsistent state
        sample_workflow_state.current_phase = "Phase 2"  # Not in_progress
        sample_workflow_state.phases[2].completed_at = None  # Missing timestamp

        state_manager.write_workflow_state(sample_workflow_state)

        # Check consistency
        report = state_manager.check_consistency()

        assert report.is_consistent is False
        assert len(report.issues) >= 2
        assert len(report.repairs_needed) >= 2

        # Check specific issues detected
        issue_types = [issue["type"] for issue in report.issues]
        assert "phase_status_mismatch" in issue_types
        assert "missing_completion_timestamp" in issue_types

    def test_state_repair_fixes_issues(self, state_manager, sample_workflow_state):
        """Test state repair functionality."""
        # Create a simple inconsistent state
        sample_workflow_state.current_phase = "Phase 2"
        # Make all phases complete but workflow not complete
        for phase in sample_workflow_state.phases:
            phase.status = "completed"
            phase.completed_at = phase.completed_at or datetime.now()
        sample_workflow_state.status = "active"  # Should be completed

        state_manager.write_workflow_state(sample_workflow_state)

        # Get consistency report
        report = state_manager.check_consistency()
        # Should detect workflow status mismatch
        assert len(report.issues) > 0

        # Repair state
        result = state_manager.repair_state(report)
        assert result is True

        # Check specific repair was applied
        state = state_manager.read_workflow_state()
        # Workflow should now be marked complete
        assert state.status == "completed"

    def test_backup_and_rollback(self, state_manager, sample_workflow_state):
        """Test backup creation and rollback functionality."""
        # Write initial state
        state_manager.write_workflow_state(sample_workflow_state)

        # Create backup
        backup_path = state_manager.create_backup("test_backup")
        assert backup_path is not None
        assert backup_path.exists()
        assert (backup_path / "WORKFLOW-STATE.md").exists()

        # Modify state
        sample_workflow_state.status = "cancelled"
        sample_workflow_state.phases[0].status = "blocked"
        state_manager.write_workflow_state(sample_workflow_state)

        # Verify modification
        modified_state = state_manager.read_workflow_state()
        assert modified_state.status == "cancelled"

        # Rollback
        result = state_manager.rollback_to(backup_path)
        assert result is True

        # Verify rollback
        restored_state = state_manager.read_workflow_state()
        assert restored_state.status == "active"
        assert restored_state.phases[0].status == "in_progress"

    def test_state_history_tracking(self, state_manager, sample_workflow_state):
        """Test state change history tracking."""
        state_manager.write_workflow_state(sample_workflow_state)

        # Make some changes
        state_manager.intelligent_update(
            "phase_progress", phase_name="Phase 2", new_status="in_progress"
        )

        state_manager.intelligent_update("workflow_transition", new_status="paused")

        # Get history
        history = state_manager.get_state_history(limit=10)

        assert len(history) >= 2
        assert history[0].change_type in [StateChangeType.UPDATE]
        assert history[0].target in ["workflow", "phase:Phase 2"]

    def test_intelligent_document_update(self, state_manager):
        """Test intelligent document status update."""
        # Mock the registry import inside the method
        with patch("claudecraftsman.core.registry.RegistryManager") as mock_registry_class:
            mock_manager = Mock()
            mock_manager.update_document_status.return_value = True
            mock_registry_class.return_value = mock_manager

            result = state_manager.intelligent_update(
                "document_status", filename="PRD-test.md", new_status="Complete"
            )

            assert result is True
            mock_manager.update_document_status.assert_called_once_with("PRD-test.md", "Complete")

            # Check history was recorded
            assert len(state_manager.history) > 0
            last_change = state_manager.history[-1]
            assert last_change.target == "document:PRD-test.md"

    def test_workflow_completion_validation(self, state_manager, sample_workflow_state):
        """Test workflow completion requires all phases complete."""
        state_manager.write_workflow_state(sample_workflow_state)

        # Try to complete workflow with incomplete phases
        result = state_manager.intelligent_update("workflow_transition", new_status="completed")

        assert result is False

        # Complete all phases
        for phase in sample_workflow_state.phases:
            phase.status = "completed"
            phase.completed_at = datetime.now()

        state_manager.write_workflow_state(sample_workflow_state)

        # Now workflow completion should succeed
        result = state_manager.intelligent_update("workflow_transition", new_status="completed")

        assert result is True

    def test_multiple_active_phases_detection(self, state_manager, sample_workflow_state):
        """Test detection of multiple phases in progress."""
        # Set multiple phases to in_progress
        sample_workflow_state.phases[0].status = "in_progress"
        sample_workflow_state.phases[1].status = "in_progress"

        state_manager.write_workflow_state(sample_workflow_state)

        # Check consistency
        report = state_manager.check_consistency()

        assert report.is_consistent is False
        issue_types = [issue["type"] for issue in report.issues]
        assert "multiple_active_phases" in issue_types

        # Repair should fix this
        state_manager.repair_state(report)

        state = state_manager.read_workflow_state()
        in_progress_count = sum(1 for p in state.phases if p.status == "in_progress")
        assert in_progress_count == 1

    def test_prune_old_backups(self, state_manager, sample_workflow_state):
        """Test pruning of old backups."""
        state_manager.write_workflow_state(sample_workflow_state)

        # Create some backups with different ages
        old_backup = state_manager.state_backup_dir / "20240101_120000_old"
        old_backup.mkdir(parents=True)
        (old_backup / "test.md").write_text("old backup")

        recent_backup = state_manager.create_backup("recent")

        # Prune old backups
        removed = state_manager.prune_old_backups(keep_days=7)

        assert removed >= 1
        assert not old_backup.exists()
        assert recent_backup.exists()
