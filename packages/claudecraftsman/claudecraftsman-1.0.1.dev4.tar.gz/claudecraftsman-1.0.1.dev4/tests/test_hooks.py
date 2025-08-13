"""
Tests for hook configuration and handlers.
"""

import json

import pytest

from claudecraftsman.hooks.config import HookEvent, generate_hooks_json, get_default_hooks
from claudecraftsman.hooks.handlers import HookContext, HookHandler


class TestHookConfig:
    """Test hook configuration."""

    def test_hook_event_validation(self):
        """Test HookEvent model validation."""
        # Valid event
        event = HookEvent(
            event="preToolUse", handler="claudecraftsman hook validate", description="Test hook"
        )
        assert event.enabled is True

        # Invalid event type should raise error
        with pytest.raises(ValueError):
            HookEvent(event="invalidEvent", handler="test")

    def test_default_hooks(self):
        """Test default hook configuration."""
        hooks = get_default_hooks()

        # Should have 4 default hooks
        assert len(hooks) == 4

        # Check event types
        event_types = {hook.event for hook in hooks}
        assert event_types == {"preToolUse", "postToolUse", "userPromptSubmit", "sessionStart"}

        # All should be enabled by default
        assert all(hook.enabled for hook in hooks)

    def test_generate_hooks_json(self, tmp_path):
        """Test hooks.json generation."""
        output_path = tmp_path / "test_hooks.json"

        # Generate hooks
        json_str = generate_hooks_json(output_path)

        # Verify file created
        assert output_path.exists()

        # Verify JSON structure
        data = json.loads(json_str)
        assert data["version"] == "1.0"
        assert "hooks" in data
        assert len(data["hooks"]) == 4
        assert "settings" in data

        # Verify settings
        assert data["settings"]["claudecraftsman"]["autoValidate"] is True


class TestHookHandlers:
    """Test hook event handlers."""

    @pytest.fixture
    def handler(self, tmp_path):
        """Create hook handler with temp directory."""
        # Create minimal .claude structure
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        (claude_dir / "context").mkdir()
        (claude_dir / "docs" / "current").mkdir(parents=True)

        # Change to temp directory
        import os

        original_cwd = os.getcwd()
        os.chdir(tmp_path)

        try:
            handler = HookHandler()
            yield handler
        finally:
            os.chdir(original_cwd)

    def test_pre_tool_use_safe_tools(self, handler):
        """Test pre-tool validation for safe tools."""
        context = HookContext(event="preToolUse", tool="Read")

        result = handler.handle_pre_tool_use(context)
        assert result["allowed"] is True
        assert "message" not in result  # Safe tools skip validation

    def test_pre_tool_use_validation(self, handler):
        """Test pre-tool validation for write operations."""
        context = HookContext(
            event="preToolUse",
            tool="Write",
            args={"file_path": "tests/test_example.py"},  # Use valid test directory
        )

        # Set time context to avoid time_context violation
        handler.framework_validator.time_context_established = True

        result = handler.handle_pre_tool_use(context)
        assert result["allowed"] is True
        assert "message" in result or "warning" in result

    def test_post_tool_use_document_creation(self, handler):
        """Test post-tool state update for document creation."""
        context = HookContext(
            event="postToolUse",
            tool="Write",
            args={"file_path": str(handler.config.paths.docs_dir / "PRD-test.md")},
            result={"success": True},
        )

        # Should not raise any errors
        handler.handle_post_tool_use(context)

    def test_user_prompt_command_routing(self, handler):
        """Test command routing for framework commands."""
        # Test explicit command
        context = HookContext(event="userPromptSubmit", prompt="/design new-feature")

        result = handler.handle_user_prompt_submit(context)
        assert result["enhanced"] is True
        assert "claudecraftsman workflow design" in result["command"]

        # Test implicit pattern
        context = HookContext(event="userPromptSubmit", prompt="create a new backend agent")

        result = handler.handle_user_prompt_submit(context)
        assert result["enhanced"] is True
        assert "claudecraftsman add agent" in result["suggestion"]

    def test_session_initialization(self, handler):
        """Test session start handler."""
        context = HookContext(event="sessionStart")

        result = handler.handle_session_start(context)
        assert result["initialized"] is True
        assert "project" in result
        assert "mode" in result
        assert "checks" in result

    def test_event_dispatcher(self, handler):
        """Test main event dispatcher."""
        # Test each event type
        events = [
            {"event": "preToolUse", "tool": "Read"},
            {"event": "postToolUse", "tool": "Write", "result": {}},
            {"event": "userPromptSubmit", "prompt": "test"},
            {"event": "sessionStart"},
        ]

        for event_data in events:
            result = handler.handle_event(event_data)
            assert "error" not in result

        # Test unknown event
        result = handler.handle_event({"event": "unknownEvent"})
        assert "error" in result
