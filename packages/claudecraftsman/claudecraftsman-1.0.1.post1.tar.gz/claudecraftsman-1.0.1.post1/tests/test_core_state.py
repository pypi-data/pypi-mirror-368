"""
Tests for state management module.
"""

from datetime import datetime

import pytest

from claudecraftsman.core.state import HandoffEntry, StateManager, WorkflowPhase, WorkflowState


class TestStateManager:
    """Test state management functionality."""

    @pytest.fixture
    def state_manager(self, tmp_path, monkeypatch):
        """Create state manager with temp directory."""
        # Create .claude structure in temp directory
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        (claude_dir / "context").mkdir()
        (claude_dir / "docs" / "current").mkdir(parents=True)
        (claude_dir / "project-mgt" / "06-project-tracking").mkdir(parents=True)

        # Change to temp directory for the test
        monkeypatch.chdir(tmp_path)

        # Create state manager with default config (will use cwd)
        return StateManager()

    def test_ensure_context_dir(self, state_manager):
        """Test context directory creation."""
        assert state_manager.ensure_context_dir()
        assert state_manager.context_dir.exists()

    def test_workflow_state_roundtrip(self, state_manager):
        """Test writing and reading workflow state."""
        # Create workflow state
        state = WorkflowState(
            project="TestProject",
            workflow_type="feature",
            current_phase="Design",
            status="active",
            phases=[
                WorkflowPhase(
                    name="Planning",
                    status="completed",
                    agent="product-architect",
                    started_at=datetime.now(),
                    completed_at=datetime.now(),
                    deliverables=["PRD.md"],
                    notes="Requirements gathered",
                ),
                WorkflowPhase(
                    name="Design",
                    status="in_progress",
                    agent="design-architect",
                    started_at=datetime.now(),
                ),
            ],
        )

        # Write state
        assert state_manager.write_workflow_state(state)
        assert state_manager.workflow_state_file.exists()

        # Read state back
        read_state = state_manager.read_workflow_state()
        assert read_state is not None
        assert read_state.project == "TestProject"
        assert read_state.workflow_type == "feature"
        assert read_state.current_phase == "Design"
        assert len(read_state.phases) == 2
        assert read_state.phases[0].name == "Planning"
        assert read_state.phases[0].status == "completed"

    def test_handoff_entry(self, state_manager):
        """Test adding handoff entries."""
        entry = HandoffEntry(
            from_agent="product-architect",
            to_agent="design-architect",
            workflow="TestWorkflow",
            context_summary="PRD completed, ready for technical design",
            deliverables=["PRD.md", "user-research.md"],
            next_phase_briefing="Create technical specification based on PRD",
            quality_status="passed",
        )

        assert state_manager.add_handoff_entry(entry)
        assert state_manager.handoff_log_file.exists()

        # Verify content
        content = state_manager.handoff_log_file.read_text()
        assert "product-architect → design-architect" in content
        assert "PRD completed" in content

    def test_progress_update(self, state_manager):
        """Test updating phase progress."""
        # Create initial state
        state = WorkflowState(
            project="TestProject",
            current_phase="Planning",
            phases=[
                WorkflowPhase(name="Planning", status="pending"),
                WorkflowPhase(name="Design", status="pending"),
            ],
        )
        state_manager.write_workflow_state(state)

        # Update progress
        assert state_manager.update_progress("Planning", "in_progress", "Starting requirements")

        # Verify update
        updated_state = state_manager.read_workflow_state()
        assert updated_state.phases[0].status == "in_progress"
        # Note: started_at timestamp is not preserved in markdown roundtrip
        assert updated_state.phases[0].notes == "Starting requirements"
        assert updated_state.current_phase == "Planning"

    def test_document_lifecycle(self, state_manager):
        """Test document creation and completion."""
        # Ensure registry is clean
        registry_file = state_manager.docs_dir / "current" / "registry.md"
        if registry_file.exists():
            registry_file.write_text(
                "# Document Registry\n\n| Document | Type | Location | Created | Status | Purpose |\n|----------|------|----------|---------|--------|---------|\n"
            )

        # Create document
        assert state_manager.document_created(
            filename="PRD-test-lifecycle.md",
            doc_type="PRD",
            location="docs/current",
            purpose="Test product requirements",
        )

        # Mark as completed
        assert state_manager.document_completed("PRD-test-lifecycle.md")

        # Check progress log
        assert state_manager.progress_log_file.exists()
        content = state_manager.progress_log_file.read_text()
        assert "Document Created: PRD-test-lifecycle.md" in content
        assert "Document Completed: PRD-test-lifecycle.md" in content

    def test_phase_lifecycle(self, state_manager):
        """Test phase start and completion."""
        # Ensure clean state
        if state_manager.workflow_state_file.exists():
            state_manager.workflow_state_file.unlink()

        # Start phase
        assert state_manager.phase_started(
            phase="Implementation", agent="backend-architect", description="Building API endpoints"
        )

        # Verify state
        state = state_manager.read_workflow_state()
        assert state is not None
        assert state.current_phase == "Implementation"
        assert any(p.name == "Implementation" for p in state.phases)
        impl_phase = next(p for p in state.phases if p.name == "Implementation")
        assert impl_phase.status == "in_progress"

        # Complete phase
        assert state_manager.phase_completed(
            phase="Implementation", agent="backend-architect", description="API endpoints completed"
        )

        # Verify completion
        state = state_manager.read_workflow_state()
        impl_phase = next(p for p in state.phases if p.name == "Implementation")
        assert impl_phase.status == "completed"
        # Note: completed_at won't be preserved through markdown roundtrip
