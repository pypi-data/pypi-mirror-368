"""
Tests for hooks and enhanced state integration.
"""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from claudecraftsman.core.state_enhanced import StateConsistencyReport
from claudecraftsman.hooks.handlers import HookContext, HookHandler


class TestHooksStateIntegration:
    """Test integration between hooks and enhanced state management."""

    @pytest.fixture
    def hook_handler(self, tmp_path):
        """Create hook handler with test config."""
        with patch("claudecraftsman.hooks.handlers.get_config") as mock_config:
            config = Mock()
            config.project_root = tmp_path
            config.paths.claude_dir = tmp_path / ".claude"
            config.paths.context_dir = tmp_path / ".claude" / "context"
            config.paths.docs_dir = tmp_path / ".claude" / "docs"
            config.paths.is_valid = True
            config.dev_mode = False

            # Create necessary directories
            config.paths.claude_dir.mkdir(parents=True, exist_ok=True)
            config.paths.context_dir.mkdir(parents=True, exist_ok=True)
            config.paths.docs_dir.mkdir(parents=True, exist_ok=True)
            (config.paths.docs_dir / "current").mkdir(parents=True, exist_ok=True)

            mock_config.return_value = config
            return HookHandler()

    def test_session_start_with_state_consistency_check(self, hook_handler):
        """Test session start runs state consistency check and repairs issues."""
        # Create inconsistent workflow state
        workflow_state_content = """# Workflow State

**Project**: test-project
**Workflow Type**: implementation
**Current Phase**: Phase 2
**Status**: active
**Created**: 2025-08-07 10:00 UTC
**Updated**: 2025-08-07 10:00 UTC

## Phases

### Phase 1 ✅
- **Status**: completed

### Phase 2 ⏳
- **Status**: pending
"""
        hook_handler.state_manager.workflow_state_file.write_text(workflow_state_content)

        # Create context for session start
        context = HookContext(event="SessionStart", correlation_id="test-session")

        # Handle session start
        result = hook_handler.handle_session_start(context)

        # Check that consistency check was run
        assert result["initialized"] is True
        assert "checks" in result

        # Verify state repair message appears in checks
        checks_str = "\n".join(result["checks"])
        assert (
            "State inconsistencies detected" in checks_str or "State files consistent" in checks_str
        )

        # If inconsistencies were found, verify repair
        if "State inconsistencies detected" in checks_str:
            assert "automatically repaired" in checks_str.lower()

    def test_document_completion_triggers_intelligent_update(self, hook_handler):
        """Test document completion detection triggers intelligent state update."""
        # Create a document with completion marker
        doc_path = hook_handler.config.paths.docs_dir / "current" / "PRD-test.md"
        doc_content = """# Test PRD

        ## Status
        Status: Complete ✅

        ## Content
        This is a completed document.
        """

        context = HookContext(
            event="postToolUse",
            tool="Write",
            args={"file_path": str(doc_path), "content": doc_content},
            result={"success": True},
        )

        # Mock the archive check
        with patch.object(hook_handler, "_check_and_archive_old_documents"):
            # Mock intelligent update to verify it's called
            with patch.object(hook_handler.state_manager, "intelligent_update") as mock_update:
                mock_update.return_value = True

                # Handle post tool use
                hook_handler.handle_post_tool_use(context)

                # Verify intelligent update was called
                mock_update.assert_called_with(
                    "document_status", filename="PRD-test.md", new_status="Complete"
                )

    def test_file_creation_triggers_progress_tracking(self, hook_handler):
        """Test file creation triggers intelligent progress tracking."""
        # Create a new document
        doc_path = hook_handler.config.paths.docs_dir / "current" / "PLAN-feature.md"

        context = HookContext(
            event="postToolUse",
            tool="Write",
            args={"file_path": str(doc_path), "content": "# Feature Plan"},
            result={"success": True},
        )

        # Mock intelligent update
        with patch.object(hook_handler.state_manager, "intelligent_update") as mock_update:
            mock_update.return_value = True

            # Mock update_progress_log
            with patch.object(hook_handler.state_manager, "update_progress_log") as mock_progress:
                # Handle post tool use
                hook_handler.handle_post_tool_use(context)

                # Verify intelligent update was called for new document
                mock_update.assert_called_with(
                    "document_status", filename="PLAN-feature.md", new_status="Active"
                )

                # Verify progress was logged
                mock_progress.assert_called()

    def test_git_commit_triggers_registry_sync(self, hook_handler):
        """Test git commit triggers registry sync through hook chaining."""
        context = HookContext(
            event="postToolUse",
            tool="Bash",
            args={"command": "git commit -m 'feat: add new feature'"},
            result={"success": True},
        )

        # Mock registry sync
        with patch("claudecraftsman.core.registry.RegistryManager") as mock_registry_class:
            mock_registry = Mock()
            mock_registry_class.return_value = mock_registry

            # Handle post tool use
            hook_handler.handle_post_tool_use(context)

            # Verify registry sync was called
            mock_registry.sync_registry.assert_called_once()

    def test_state_repair_during_session_start(self, hook_handler):
        """Test state repair is triggered during session start when issues found."""
        # Create a simple state consistency issue
        workflow_state = """# Workflow State
**Project**: test-project
**Current Phase**: NonExistentPhase
**Status**: active

## Phases
### Phase 1 ✅
- **Status**: completed
"""
        hook_handler.state_manager.workflow_state_file.write_text(workflow_state)

        # Mock check_consistency to return issues
        mock_report = StateConsistencyReport(
            is_consistent=False,
            issues=[{"type": "phase_not_found", "description": "Current phase not in phase list"}],
            repairs_needed=[{"action": "fix_current_phase"}],
        )

        with patch.object(hook_handler.state_manager, "check_consistency") as mock_check:
            mock_check.return_value = mock_report

            with patch.object(hook_handler.state_manager, "repair_state") as mock_repair:
                mock_repair.return_value = True

                context = HookContext(event="SessionStart")
                result = hook_handler.handle_session_start(context)

                # Verify consistency check was called
                mock_check.assert_called_once()

                # Verify repair was called with the report
                mock_repair.assert_called_once_with(mock_report)

                # Verify result contains repair message
                checks = result.get("checks", [])
                assert any("automatically repaired" in check for check in checks)

    def test_old_backup_pruning(self, hook_handler):
        """Test old backup pruning functionality."""
        # Create some old backup directories
        backup_dir = hook_handler.state_manager.state_backup_dir
        backup_dir.mkdir(parents=True, exist_ok=True)

        # Create old backup (10 days ago)
        old_backup = backup_dir / "20240728_120000_test"
        old_backup.mkdir()
        (old_backup / "test.md").write_text("old backup")

        # Create recent backup
        recent_backup = backup_dir / datetime.now().strftime("%Y%m%d_%H%M%S_test")
        recent_backup.mkdir()
        (recent_backup / "test.md").write_text("recent backup")

        # Prune old backups
        removed = hook_handler.state_manager.prune_old_backups(keep_days=7)

        # Verify old backup was removed
        assert removed >= 1
        assert not old_backup.exists()
        assert recent_backup.exists()
