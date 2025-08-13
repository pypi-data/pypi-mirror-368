"""
Tests for registry management functionality.
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from claudecraftsman.core.registry import RegistryManager


@pytest.fixture
def temp_docs_dir():
    """Create a temporary documents directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        docs_dir = Path(tmpdir) / ".claude" / "docs"
        (docs_dir / "current" / "plans").mkdir(parents=True, exist_ok=True)
        (docs_dir / "current" / "implementation").mkdir(parents=True, exist_ok=True)
        (docs_dir / "archive").mkdir(parents=True, exist_ok=True)
        yield docs_dir


@pytest.fixture
def mock_config(temp_docs_dir):
    """Create a mock config with temporary paths."""
    config = MagicMock()
    config.paths.docs_dir = temp_docs_dir
    return config


@pytest.fixture
def registry_manager(mock_config):
    """Create a registry manager with mock config."""
    return RegistryManager(config=mock_config)


def test_parse_document_metadata_from_filename(registry_manager, temp_docs_dir):
    """Test parsing metadata from document filename."""
    # Create a test document
    doc_path = temp_docs_dir / "current" / "plans" / "PLAN-test-feature-2025-08-06.md"
    doc_path.write_text("# Test Feature Plan\n\n## Overview\n- This is a test feature plan")

    metadata = registry_manager.parse_document_metadata(doc_path)

    assert metadata["document"] == "PLAN-test-feature-2025-08-06.md"
    assert metadata["type"] == "Plan"
    assert metadata["location"] == "current/plans"
    assert metadata["created"] == "2025-08-06"
    assert metadata["status"] == "Active"
    assert (
        metadata["purpose"] == "This is a test feature plan"
    )  # Purpose is extracted from Overview section


def test_parse_document_metadata_with_status(registry_manager, temp_docs_dir):
    """Test parsing document with STATUS marker."""
    doc_path = temp_docs_dir / "current" / "implementation" / "IMPL-feature-2025-08-06.md"
    doc_path.write_text("""# Feature Implementation

STATUS: Complete

## Overview
- Implementation of the feature is complete
""")

    metadata = registry_manager.parse_document_metadata(doc_path)

    assert metadata["status"] == "Complete"
    assert metadata["type"] == "Implementation"


def test_parse_document_metadata_compound_type(registry_manager, temp_docs_dir):
    """Test parsing compound document types like TECH-SPEC."""
    # Create the technical directory first
    (temp_docs_dir / "current" / "technical").mkdir(parents=True, exist_ok=True)

    doc_path = temp_docs_dir / "current" / "technical" / "TECH-SPEC-api-2025-08-06.md"
    doc_path.write_text("# API Technical Specification")

    metadata = registry_manager.parse_document_metadata(doc_path)

    assert metadata["type"] == "Technical Specification"


def test_auto_register_document(registry_manager, temp_docs_dir):
    """Test automatic document registration."""
    # Create registry file
    registry_path = temp_docs_dir / "current" / "registry.md"
    registry_path.write_text("""# ClaudeCraftsman Document Registry
*Master index of all project documentation*

**Project**: ClaudeCraftsman Framework
**Last Updated**: 2025-08-06

## Current Active Documents
| Document | Type | Location | Created | Status | Purpose |
|----------|------|----------|---------|--------|---------|

## Recently Archived
| Document | Type | Archive Date | Location | Reason |
|----------|------|--------------|----------|--------|
""")

    # Create a test document
    doc_path = temp_docs_dir / "current" / "plans" / "PLAN-new-feature-2025-08-06.md"
    doc_path.write_text("# New Feature Plan\n\n## Overview\n- Planning for new feature")

    # Auto-register the document
    result = registry_manager.auto_register_document(doc_path)

    assert result is True

    # Verify registry was updated
    registry_content = registry_path.read_text()
    assert "PLAN-new-feature-2025-08-06.md" in registry_content
    assert "Plan" in registry_content
    assert "current/plans" in registry_content


def test_sync_registry(registry_manager, temp_docs_dir):
    """Test syncing registry with file system."""
    # Create empty registry
    registry_path = temp_docs_dir / "current" / "registry.md"
    registry_path.write_text("""# ClaudeCraftsman Document Registry
*Master index of all project documentation*

**Project**: ClaudeCraftsman Framework
**Last Updated**: 2025-08-06

## Current Active Documents
| Document | Type | Location | Created | Status | Purpose |
|----------|------|----------|---------|--------|---------|

## Recently Archived
| Document | Type | Archive Date | Location | Reason |
|----------|------|--------------|----------|--------|
""")

    # Create unregistered documents
    (temp_docs_dir / "current" / "plans" / "PLAN-unregistered-1-2025-08-06.md").write_text(
        "# Unregistered 1"
    )
    (temp_docs_dir / "current" / "implementation" / "IMPL-unregistered-2-2025-08-06.md").write_text(
        "# Unregistered 2"
    )

    # Sync registry
    added_count = registry_manager.sync_registry()

    assert added_count == 2

    # Verify both documents were added
    registry_content = registry_path.read_text()
    assert "PLAN-unregistered-1-2025-08-06.md" in registry_content
    assert "IMPL-unregistered-2-2025-08-06.md" in registry_content


def test_validate_registry_missing_files(registry_manager, temp_docs_dir):
    """Test registry validation detects missing files."""
    # Create registry with orphaned entry
    registry_path = temp_docs_dir / "current" / "registry.md"
    registry_path.write_text("""# ClaudeCraftsman Document Registry
*Master index of all project documentation*

**Project**: ClaudeCraftsman Framework
**Last Updated**: 2025-08-06

## Current Active Documents
| Document | Type | Location | Created | Status | Purpose |
|----------|------|----------|---------|--------|---------|
| MISSING-doc-2025-08-06.md | Plan | current/plans | 2025-08-06 | Active | Missing document |

## Recently Archived
| Document | Type | Archive Date | Location | Reason |
|----------|------|--------------|----------|--------|
""")

    # Validate registry
    is_valid, issues = registry_manager.validate_registry()

    assert is_valid is False
    assert len(issues) == 1
    assert "Missing file" in issues[0]
    assert "MISSING-doc-2025-08-06.md" in issues[0]


def test_validate_registry_old_complete_docs(registry_manager, temp_docs_dir):
    """Test registry validation suggests archiving old complete documents."""
    # Create registry with old complete document
    registry_path = temp_docs_dir / "current" / "registry.md"
    registry_path.write_text("""# ClaudeCraftsman Document Registry
*Master index of all project documentation*

**Project**: ClaudeCraftsman Framework
**Last Updated**: 2025-08-06

## Current Active Documents
| Document | Type | Location | Created | Status | Purpose |
|----------|------|----------|---------|--------|---------|
| OLD-complete-doc.md | Plan | current/plans | 2025-07-01 | Complete | Old complete document |

## Recently Archived
| Document | Type | Archive Date | Location | Reason |
|----------|------|--------------|----------|--------|
""")

    # Create the actual file
    (temp_docs_dir / "current" / "plans" / "OLD-complete-doc.md").write_text("# Old Complete")

    # Validate registry
    is_valid, issues = registry_manager.validate_registry()

    assert is_valid is False
    assert len(issues) == 1
    assert "consider archiving" in issues[0]
    assert "OLD-complete-doc.md" in issues[0]


def test_archive_document(registry_manager, temp_docs_dir):
    """Test archiving a document."""
    # Create registry with active document
    registry_path = temp_docs_dir / "current" / "registry.md"
    # Use same format as the _write_registry method creates
    registry_content = """# ClaudeCraftsman Document Registry
*Master index of all project documentation*

**Project**: ClaudeCraftsman Framework
**Last Updated**: 2025-08-06

## Current Active Documents
| Document | Type | Location | Created | Status | Purpose |
|----------|------|----------|---------|--------|---------|
| PLAN-to-archive-2025-08-06.md | Plan | current/plans | 2025-08-06 | Complete | Document to archive |

## Recently Archived
| Document | Type | Archive Date | Location | Reason |
|----------|------|--------------|----------|--------|
"""
    registry_path.write_text(registry_content)

    # Create the actual file
    doc_path = temp_docs_dir / "current" / "plans" / "PLAN-to-archive-2025-08-06.md"
    doc_path.write_text("# Document to Archive")

    # Archive the document

    with patch("claudecraftsman.core.registry.datetime") as mock_datetime:
        mock_datetime.now.return_value.strftime.return_value = "2025-08-06"
        result = registry_manager.archive_document("PLAN-to-archive-2025-08-06.md", "Completed")

    assert result is True

    # Verify document was moved
    assert not doc_path.exists()
    archive_path = temp_docs_dir / "archive" / "2025-08-06" / "PLAN-to-archive-2025-08-06.md"
    assert archive_path.exists()

    # Verify registry was updated
    registry_content = registry_path.read_text()
    assert "PLAN-to-archive-2025-08-06.md" not in registry_content.split("## Recently Archived")[0]
    assert "PLAN-to-archive-2025-08-06.md" in registry_content.split("## Recently Archived")[1]
