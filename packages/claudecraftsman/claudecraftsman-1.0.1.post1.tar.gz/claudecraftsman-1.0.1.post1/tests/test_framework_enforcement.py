"""
Test framework enforcement through lifecycle hooks.

Validates that our deterministic enforcement system works correctly.
"""

from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from claudecraftsman.core.config import Config
from claudecraftsman.hooks.enforcers import FrameworkEnforcer
from claudecraftsman.hooks.handlers import HookContext, HookHandler
from claudecraftsman.hooks.validators import FrameworkValidator


@pytest.fixture
def mock_config(tmp_path):
    """Create mock config for tests."""
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()
    docs_dir = claude_dir / "docs" / "current"
    docs_dir.mkdir(parents=True)

    return Config(project_root=tmp_path, claude_dir=claude_dir, dev_mode=False)


class TestFrameworkValidation:
    """Test framework validation rules."""

    def test_naming_convention_validation(self):
        """Test file naming convention enforcement."""
        validator = FrameworkValidator()

        # Valid names
        valid_names = [
            ".claude/docs/current/PRD-project-2025-08-06.md",
            ".claude/docs/current/TECH-SPEC-feature-2025-08-06.md",
            ".claude/docs/current/PLAN-enhancement-2025-08-06.md",
        ]

        for name in valid_names:
            valid, error = validator.validate_naming_convention(name)
            assert valid, f"Should accept {name}: {error}"

        # Invalid names
        invalid_names = [
            ".claude/docs/current/project.md",  # Missing type and date
            ".claude/docs/current/PRD-project.md",  # Missing date
            ".claude/docs/current/prd-project-2025-08-06.md",  # Lowercase type
            ".claude/docs/current/PRD-project-08-06-2025.md",  # Wrong date format
        ]

        for name in invalid_names:
            valid, error = validator.validate_naming_convention(name)
            assert not valid, f"Should reject {name}"
            assert "TYPE-name-YYYY-MM-DD.md" in error

    def test_file_location_validation(self):
        """Test file location enforcement."""
        validator = FrameworkValidator()

        # Valid locations
        valid_paths = [
            ".claude/docs/current/plans/PRD-test-2025-08-06.md",
            ".claude/docs/current/registry.md",  # Registry is allowed in root
            ".claude/context/WORKFLOW-STATE.md",
            ".claude/agents/test-agent.md",
            "src/claudecraftsman/hooks/validators.py",
            "tests/test_enforcement.py",
            "README.md",
            "CLAUDE.md",
        ]

        for path in valid_paths:
            valid, error = validator.validate_file_location(path)
            assert valid, f"Should accept {path}: {error}"

        # Invalid locations
        invalid_paths = [
            ".claude/docs/current/PRD-test-2025-08-06.md",  # Document in root of current/
            "random/location/file.md",
            "../outside/project.md",
            "temp/scratch.md",
        ]

        for path in invalid_paths:
            valid, error = validator.validate_file_location(path)
            assert not valid, f"Should reject {path}"

    def test_time_context_validation(self):
        """Test time context enforcement."""
        validator = FrameworkValidator()

        # No time context established
        valid, error = validator.validate_time_context()
        assert not valid
        assert "Time context not established" in error

        # Establish time context
        validator.record_mcp_tool_usage("time")
        valid, error = validator.validate_time_context()
        assert valid

    def test_research_evidence_validation(self):
        """Test research document validation."""
        validator = FrameworkValidator()

        # Research document without MCP tools
        valid, error = validator.validate_research_evidence("PRD-project-2025-08-06.md")
        assert not valid
        assert "requires MCP research tools" in error

        # Record research tool usage
        validator.record_mcp_tool_usage("searxng")
        valid, error = validator.validate_research_evidence("PRD-project-2025-08-06.md")
        assert valid

        # Non-research document doesn't require tools
        valid, error = validator.validate_research_evidence("README.md")
        assert valid

    def test_citation_validation(self):
        """Test citation format validation."""
        validator = FrameworkValidator()

        # Document with proper citations
        content_with_citations = """
        # Research Report

        According to recent studies, the market is growing[1]^[1].
        Another report shows similar trends[2]^[2].

        ## Sources
        [1] Market Research Report - https://example.com - 2025-08-06
        [2] Industry Analysis - https://example.org - 2025-08-06
        """

        valid, error = validator.validate_citations(content_with_citations)
        assert valid

        # Document with citations but no sources - make it long enough (>500 chars)
        content_no_sources = """
        # Research Report

        The market is growing[1]^[1]. This is based on extensive research that shows
        significant growth patterns across multiple sectors and regions. The data indicates
        that this trend will continue for the foreseeable future, with particularly strong
        growth in emerging markets and technology sectors. Additional analysis suggests
        that regulatory changes and consumer behavior shifts are key drivers of this growth.
        Further investigation reveals opportunities in untapped markets and segments.
        """

        valid, error = validator.validate_citations(content_no_sources)
        assert not valid
        assert "no Sources section" in error

        # Research content without any citations
        content_research_no_citations = """
        # Market Analysis Report

        According to recent research, the market is experiencing unprecedented growth.
        Multiple studies have shown that this trend is accelerating. Survey data indicates
        strong consumer demand. Industry statistics show year-over-year improvements.
        Market analysis reveals significant opportunities in emerging sectors.
        The report concludes that investment opportunities are abundant.
        This extensive research demonstrates clear market trends.
        """

        valid, error = validator.validate_citations(content_research_no_citations)
        assert not valid
        assert "lacks citations" in error

    def test_hardcoded_dates_validation(self):
        """Test hardcoded date detection."""
        validator = FrameworkValidator()

        # Content with hardcoded dates
        content_with_dates = """
        # Project Plan

        We will launch on 2025-09-15.
        The deadline is October 31, 2025.
        """

        valid, error = validator.validate_hardcoded_dates(content_with_dates)
        assert not valid
        assert "Hardcoded date" in error

        # Content with acceptable date headers
        content_ok_dates = """
        # Document
        *Date: 2025-08-06*
        Created: 2025-08-06

        This document uses dynamic dates for content.
        """

        valid, error = validator.validate_hardcoded_dates(content_ok_dates)
        assert valid


class TestFrameworkEnforcement:
    """Test framework enforcement and auto-correction."""

    def test_auto_correction_eligibility(self, mock_config):
        """Test which violations can be auto-corrected."""
        with patch("pathlib.Path.cwd", return_value=mock_config.project_root):
            enforcer = FrameworkEnforcer()

        # Can auto-correct naming and dates
        correctable = [
            ("naming_convention", "Wrong format"),
            ("hardcoded_dates", "Date found"),
        ]
        assert enforcer.can_auto_correct(correctable)

        # Cannot auto-correct other violations
        not_correctable = [
            ("naming_convention", "Wrong format"),
            ("time_context", "Not established"),
        ]
        assert not enforcer.can_auto_correct(not_correctable)

    def test_naming_auto_correction(self, mock_config):
        """Test automatic naming correction."""
        with patch("pathlib.Path.cwd", return_value=mock_config.project_root):
            enforcer = FrameworkEnforcer()

        # Test various incorrect names
        test_cases = [
            ("project.md", f"DOC-project-{datetime.now().strftime('%Y-%m-%d')}.md"),
            ("PRD-project.md", f"PRD-project-{datetime.now().strftime('%Y-%m-%d')}.md"),
            ("spec-feature-old-date.md", f"SPEC-feature-{datetime.now().strftime('%Y-%m-%d')}.md"),
        ]

        for original, expected in test_cases:
            corrected = enforcer.auto_correct_naming(original)
            assert Path(corrected).name == expected

    def test_date_auto_correction(self, mock_config):
        """Test automatic date replacement."""
        with patch("pathlib.Path.cwd", return_value=mock_config.project_root):
            enforcer = FrameworkEnforcer()
        current_date = datetime.now().strftime("%Y-%m-%d")

        content = """
        # Plan

        Launch date: 2025-09-15
        Review by October 31, 2025
        """

        corrected = enforcer.auto_correct_dates(content, current_date)
        assert "2025-09-15" not in corrected
        assert "October 31, 2025" not in corrected
        assert current_date in corrected


class TestHookIntegration:
    """Test complete hook handler integration."""

    @patch("claudecraftsman.hooks.handlers.get_config")
    def test_pre_tool_validation(self, mock_config):
        """Test pre-tool use validation flow."""
        # Setup
        mock_config.return_value.paths.claude_dir.exists.return_value = True
        handler = HookHandler()

        # Create context for Write operation
        context = HookContext(
            event="preToolUse",
            tool="Write",
            args={
                "file_path": ".claude/docs/current/test.md",  # Invalid name
                "content": "Test content",
            },
        )

        # Should detect naming violation and time context missing
        result = handler.handle_pre_tool_use(context)
        # In non-strict mode, it should allow with warnings
        if "allowed" in result:
            if not result["allowed"]:
                # Should be because of missing time context
                assert "Time context not established" in str(result)
            else:
                # Allowed with warnings or corrections
                assert "warning" in result or "corrections" in result

    @patch("claudecraftsman.hooks.handlers.get_config")
    def test_post_tool_state_update(self, mock_config):
        """Test post-tool use state updates."""
        # Setup
        mock_config.return_value.paths.claude_dir.exists.return_value = True
        handler = HookHandler()

        # Mock the enforcer to track calls
        with patch.object(handler.framework_enforcer, "enforce_post_operation") as mock_enforce:
            context = HookContext(
                event="postToolUse",
                tool="Write",
                args={"file_path": ".claude/docs/current/PRD-test-2025-08-06.md"},
                result={"success": True},
            )

            handler.handle_post_tool_use(context)

            # Verify enforcement was called
            mock_enforce.assert_called_once_with(
                operation="create",
                filepath=".claude/docs/current/PRD-test-2025-08-06.md",
                success=True,
            )

    @patch("claudecraftsman.hooks.handlers.get_config")
    def test_session_initialization(self, mock_config):
        """Test session start initialization."""
        # Setup
        mock_config.return_value.paths.claude_dir.exists.return_value = True
        mock_config.return_value.paths.is_valid = True
        mock_config.return_value.project_root.name = "test-project"
        mock_config.return_value.dev_mode = True
        mock_config.return_value.get.return_value = {}

        handler = HookHandler()
        context = HookContext(event="sessionStart")

        result = handler.handle_session_start(context)

        assert result["initialized"]
        assert result["project"] == "test-project"
        assert "checks" in result
        assert "reminders" in result
        assert len(result["reminders"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
