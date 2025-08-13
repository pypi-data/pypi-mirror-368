"""
Global pytest configuration and fixtures.
"""

from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def cleanup_test_files():
    """
    Automatically clean up any test files that might be accidentally
    created in the real project directory.
    """
    # List of test file patterns that should never exist in the real project
    test_patterns = [
        "OLD-doc-*.md",
        "orphan.md",
        "bad-name.md",
        "PRD-test*.md",
        "IMPL-test*.md",
        "PLAN-test*.md",
        "test-*.md",
        "*-test-*.md",
        "PLAN-unregistered-*.md",
        "PLAN-new-*.md",
    ]

    # Directories to check
    project_root = Path.cwd()
    docs_current = project_root / ".claude" / "docs" / "current"

    # Let test run
    yield

    # Cleanup after test
    if docs_current.exists():
        for pattern in test_patterns:
            for file_path in docs_current.glob(pattern):
                try:
                    file_path.unlink()
                    print(f"Cleaned up test file: {file_path}")
                except Exception as e:
                    print(f"Failed to clean up {file_path}: {e}")

            # Also check subdirectories
            for subdir in docs_current.iterdir():
                if subdir.is_dir():
                    for file_path in subdir.glob(pattern):
                        try:
                            file_path.unlink()
                            print(f"Cleaned up test file: {file_path}")
                        except Exception as e:
                            print(f"Failed to clean up {file_path}: {e}")


@pytest.fixture
def isolated_project(tmp_path):
    """
    Create an isolated project structure for tests.
    This ensures tests don't accidentally use the real project directory.
    """
    # Create full project structure in temp directory
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()

    # Create all necessary subdirectories
    (claude_dir / "docs" / "current").mkdir(parents=True)
    (claude_dir / "docs" / "archive").mkdir(parents=True)
    (claude_dir / "context").mkdir(parents=True)
    (claude_dir / "agents").mkdir(parents=True)
    (claude_dir / "commands").mkdir(parents=True)
    (claude_dir / "templates").mkdir(parents=True)

    # Create essential files
    (claude_dir / "docs" / "current" / "registry.md").write_text(
        "# Document Registry\\n\\n## Current Active Documents\\n\\n| Document | Type | Location | Date | Status | Purpose |\\n|----------|------|----------|------|--------|---------|\\n"
    )

    (claude_dir / "context" / "WORKFLOW-STATE.md").write_text(
        "# Workflow State\\n\\nStatus: Active\\nPhase: Testing"
    )

    return tmp_path
