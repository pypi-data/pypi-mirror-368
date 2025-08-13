"""
Test enhanced hook functionality.
"""

from unittest.mock import Mock, patch

import pytest

from claudecraftsman.hooks.handlers import HookContext, HookHandler


class TestEnhancedHooks:
    """Test enhanced hook functionality including progress logging and chaining."""

    @pytest.fixture
    def handler(self, tmp_path):
        """Create handler with test config."""
        with patch("claudecraftsman.hooks.handlers.get_config") as mock_config:
            config = Mock()
            config.project_root = tmp_path
            config.paths.claude_dir = tmp_path / ".claude"
            config.paths.docs_dir = tmp_path / ".claude" / "docs"
            config.paths.context_dir = tmp_path / ".claude" / "context"
            config.dev_mode = False
            config.paths.is_valid = True

            # Create directories
            config.paths.claude_dir.mkdir(parents=True)
            config.paths.docs_dir.mkdir(parents=True)
            config.paths.context_dir.mkdir(parents=True)

            mock_config.return_value = config
            return HookHandler()

    def test_progress_log_update_on_document_creation(self, handler, tmp_path):
        """Test that creating a document updates the progress log."""
        # Create progress log directory
        progress_dir = tmp_path / ".claude" / "project-mgt" / "06-project-tracking"
        progress_dir.mkdir(parents=True)

        # Create document via PostToolUse hook
        context = HookContext(
            event="postToolUse",
            tool="Write",
            args={
                "file_path": str(tmp_path / ".claude" / "docs" / "current" / "PRD-test.md"),
                "content": "# Test PRD\n\nThis is a test PRD.",
            },
            result={"success": True},
        )

        handler.handle_post_tool_use(context)

        # Check that progress log was updated
        progress_log = progress_dir / "progress-log.md"
        assert progress_log.exists()
        content = progress_log.read_text()
        assert "Document Created: PRD-test.md" in content
        assert "Created new document in current" in content

    def test_hook_chaining_on_document_completion(self, handler, tmp_path, capfd):
        """Test that marking a document complete triggers archive check."""
        # Create a completed document first
        docs_current = tmp_path / ".claude" / "docs" / "current"
        docs_current.mkdir(parents=True)

        old_doc = docs_current / "IMPL-old-feature-2025-01-01.md"
        old_doc.write_text("# Old Implementation\n\nStatus: Complete\n\nThis is done.")

        # Update registry to know about the document
        registry_file = docs_current / "registry.md"
        registry_file.write_text("""# Document Registry

## Active Documents
| Document | Type | Location | Created | Status | Purpose |
|----------|------|----------|---------|---------|---------|
| IMPL-old-feature-2025-01-01.md | Implementation | docs/current/ | 2025-01-01 | Complete | Old feature |
""")

        # Now update another document to mark it complete
        context = HookContext(
            event="postToolUse",
            tool="Edit",
            args={
                "file_path": str(docs_current / "IMPL-new-feature.md"),
                "new_string": "# New Implementation\n\nStatus: Complete\n\nAll done!",
            },
            result={"success": True},
        )

        with patch.object(handler.document_archiver, "auto_archive") as mock_archive:
            mock_archive.return_value = 1  # Simulate archiving 1 document
            handler.handle_post_tool_use(context)

            # Verify archive was triggered by hook chaining
            assert mock_archive.called

            # Check console output
            captured = capfd.readouterr()
            assert "Auto-archived 1 completed documents" in captured.out

    def test_git_commit_triggers_registry_sync(self, handler, tmp_path):
        """Test that git commit triggers registry sync via hook chaining."""
        # Create registry
        registry_file = tmp_path / ".claude" / "docs" / "current" / "registry.md"
        registry_file.parent.mkdir(parents=True)
        registry_file.write_text("# Document Registry\n\n## Active Documents\n")

        context = HookContext(
            event="postToolUse",
            tool="Bash",
            args={"command": "git commit -m 'test: add new feature'"},
            result={"success": True},
        )

        # Patch where RegistryManager is imported inside the method
        with patch("claudecraftsman.core.registry.RegistryManager") as MockRegistry:
            mock_instance = Mock()
            mock_instance.sync_registry = Mock()
            MockRegistry.return_value = mock_instance

            handler.handle_post_tool_use(context)

            # Verify registry sync was triggered
            mock_instance.sync_registry.assert_called_once()

    def test_pre_tool_quality_gate_enforcement(self, handler, tmp_path):
        """Test enhanced quality gate enforcement in PreToolUse."""
        # Test 1: PRD creation should fail without time context
        context = HookContext(
            event="preToolUse",
            tool="Write",
            args={
                "file_path": str(tmp_path / ".claude" / "docs" / "current" / "PRD-test.md"),
                "content": "# Test PRD\n\nStatus: Complete",
            },
        )

        result = handler.handle_pre_tool_use(context)

        # Should be blocked due to framework violations
        assert not result["allowed"]
        assert "Framework validation failed" in result["error"]
        violations = [d["violation"] for d in result["details"] if d["type"] == "framework"]
        assert "time_context" in violations
        assert "research_evidence" in violations

        # Test 2: Safe tools should always pass
        context2 = HookContext(
            event="preToolUse", tool="Read", args={"file_path": str(tmp_path / "README.md")}
        )

        result2 = handler.handle_pre_tool_use(context2)
        assert result2["allowed"]

        # Test 3: Time context established should allow PRD creation
        with patch.object(handler.framework_validator, "time_context_established", True):
            # Mock that we have MCP tools available
            handler.framework_validator.session_mcp_tools.append("searxng")

            context3 = HookContext(
                event="preToolUse",
                tool="Write",
                args={
                    "file_path": str(tmp_path / ".claude" / "docs" / "current" / "PRD-test.md"),
                    "content": "# Test PRD\n\nCreated: 2025-08-07\n\nResearch conducted with MCP tools.",
                },
            )

            result3 = handler.handle_pre_tool_use(context3)
            # Should pass now with proper context
            assert result3["allowed"]

    def test_automatic_progress_tracking_for_code_changes(self, handler, tmp_path):
        """Test that code changes are tracked in progress log."""
        # Create progress log directory
        progress_dir = tmp_path / ".claude" / "project-mgt" / "06-project-tracking"
        progress_dir.mkdir(parents=True)

        # Create source file
        src_dir = tmp_path / "src" / "claudecraftsman"
        src_dir.mkdir(parents=True)

        context = HookContext(
            event="postToolUse",
            tool="Write",
            args={
                "file_path": str(src_dir / "new_module.py"),
                "content": "# New module\n\ndef hello():\n    return 'world'",
            },
            result={"success": True},
        )

        handler.handle_post_tool_use(context)

        # Check progress log
        progress_log = progress_dir / "progress-log.md"
        assert progress_log.exists()
        content = progress_log.read_text()
        assert "Code Created: new_module.py" in content
        assert "Created source file in claudecraftsman" in content
