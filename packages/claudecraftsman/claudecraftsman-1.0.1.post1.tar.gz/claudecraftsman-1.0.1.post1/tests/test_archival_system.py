"""
Tests for the document archival system.
"""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from claudecraftsman.core.archival import DocumentArchiver
from claudecraftsman.core.registry import DocumentEntry


@pytest.fixture
def mock_config(tmp_path):
    """Create a mock configuration with temporary directory."""
    config = Mock()
    # Use pytest's tmp_path fixture for temporary directories
    test_dir = tmp_path / "test_project"
    test_dir.mkdir(exist_ok=True)
    claude_dir = test_dir / ".claude"
    claude_dir.mkdir(exist_ok=True)
    docs_dir = claude_dir / "docs"
    docs_dir.mkdir(exist_ok=True)

    config.paths.docs_dir = docs_dir
    config.paths.claude_dir = claude_dir
    return config


@pytest.fixture
def archiver(mock_config):
    """Create a document archiver instance."""
    return DocumentArchiver(mock_config)


@pytest.fixture
def sample_docs():
    """Create sample documents for testing."""
    return [
        DocumentEntry(
            document="PLAN-test-feature-2025-01-01.md",
            type="Plan",
            location="current/plans",
            created="2025-01-01",
            status="Complete",
            purpose="Test plan",
        ),
        DocumentEntry(
            document="IMPL-test-implementation-2025-01-20.md",
            type="Implementation",
            location="current/implementation",
            created="2025-01-20",
            status="Active",
            purpose="Test implementation",
        ),
        DocumentEntry(
            document="ARCH-test-architecture-2024-12-15.md",
            type="Architecture",
            location="current/architecture",
            created="2024-12-15",
            status="Active",  # Not complete in registry
            purpose="Test architecture",
        ),
    ]


class TestDocumentArchiver:
    """Test document archival functionality."""

    def test_completion_detection_from_content(self, archiver, tmp_path):
        """Test detecting completion status from document content."""
        # Create test documents
        complete_doc = tmp_path / "complete.md"
        complete_doc.write_text("# Test Document\n\n## STATUS: COMPLETE\n\nContent here.")

        incomplete_doc = tmp_path / "incomplete.md"
        incomplete_doc.write_text("# Test Document\n\n## STATUS: In Progress\n\nContent here.")

        # Test detection
        assert archiver.detect_completion_status(complete_doc) is True
        assert archiver.detect_completion_status(incomplete_doc) is False

    def test_completion_detection_from_filename(self, archiver, tmp_path):
        """Test detecting completion status from filename."""
        # Create test documents
        complete_doc = tmp_path / "IMPL-COMPLETE-feature.md"
        complete_doc.write_text("# Test Document")

        final_doc = tmp_path / "PLAN-FINAL-design.md"
        final_doc.write_text("# Test Document")

        regular_doc = tmp_path / "PLAN-ongoing-work.md"
        regular_doc.write_text("# Test Document")

        # Test detection
        assert archiver.detect_completion_status(complete_doc) is True
        assert archiver.detect_completion_status(final_doc) is True
        assert archiver.detect_completion_status(regular_doc) is False

    def test_document_age_calculation(self, archiver, tmp_path):
        """Test calculating document age from filename."""
        # Create test document with date in filename
        doc = tmp_path / "PLAN-test-2025-01-01.md"
        doc.write_text("# Test Document")

        # Mock current date
        with patch("claudecraftsman.core.archival.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 1, 15)
            mock_datetime.strptime = datetime.strptime

            age = archiver.get_document_age(doc)
            assert age == 14  # 14 days old

    def test_find_archival_candidates(self, sample_docs, mock_config, tmp_path):
        """Test finding documents ready for archival."""
        # Setup test environment
        docs_dir = tmp_path / ".claude" / "docs"
        current_dir = docs_dir / "current"
        current_dir.mkdir(parents=True)

        # Create subdirectories
        (current_dir / "plans").mkdir()
        (current_dir / "implementation").mkdir()
        (current_dir / "architecture").mkdir()

        # Update mock config
        mock_config.paths.docs_dir = docs_dir

        # Create archiver after updating config
        archiver = DocumentArchiver(mock_config)

        # Create test documents
        old_complete = current_dir / "plans" / "PLAN-test-feature-2025-01-01.md"
        old_complete.write_text("# Plan\n\n## STATUS: COMPLETE")

        new_complete = current_dir / "implementation" / "IMPL-test-implementation-2025-01-20.md"
        new_complete.write_text("# Implementation\n\n## STATUS: COMPLETE")

        old_incomplete = current_dir / "architecture" / "ARCH-test-architecture-2024-12-15.md"
        old_incomplete.write_text("# Architecture\n\n## STATUS: In Progress")

        # Mock registry manager
        with patch.object(archiver.registry_manager, "parse_registry") as mock_parse:
            mock_parse.return_value = (sample_docs, [])

            # Mock current date
            with patch("claudecraftsman.core.archival.datetime") as mock_datetime:
                mock_datetime.now.return_value = datetime(2025, 1, 30)
                mock_datetime.strptime = datetime.strptime
                mock_datetime.fromtimestamp = datetime.fromtimestamp

                candidates = archiver.find_archival_candidates()

                # Should find:
                # - old_complete (29 days old and complete) ✓
                # - new_complete (10 days old and complete) ✓ (>= 7 days)
                # Should NOT find:
                # - old_incomplete (old but not complete in document content)
                assert len(candidates) == 2

                # Sort by document name for consistent testing
                candidates.sort(key=lambda x: x[0].name)

                # Check IMPL document (10 days old, complete)
                assert "IMPL-test-implementation" in str(candidates[0][0])
                assert "Complete (archived after 10 days)" in candidates[0][1]

                # Check PLAN document (29 days old, complete)
                assert "PLAN-test-feature" in str(candidates[1][0])
                assert "Complete (archived after 29 days)" in candidates[1][1]

    def test_archive_document(self, archiver, mock_config, tmp_path):
        """Test archiving a single document."""
        # Setup test environment
        docs_dir = tmp_path / ".claude" / "docs"
        current_dir = docs_dir / "current"
        archive_dir = docs_dir / "archive"

        current_dir.mkdir(parents=True)
        archive_dir.mkdir(parents=True)

        # Update mock config
        mock_config.paths.docs_dir = docs_dir
        archiver.archive_dir = archive_dir

        # Create test document
        doc_path = current_dir / "PLAN-test.md"
        doc_path.write_text("# Test Plan")

        # Mock registry manager archive
        with patch.object(archiver.registry_manager, "archive_document") as mock_archive:
            mock_archive.return_value = True

            # Mock git operations
            with patch.object(archiver.git_operations, "add_files"):
                success = archiver.archive_document(doc_path, "Test archival")

                assert success is True
                mock_archive.assert_called_once_with("PLAN-test.md", "Test archival")

    def test_monitor_document_changes(self, archiver, mock_config, tmp_path):
        """Test monitoring document changes for completion."""
        # Setup test environment
        docs_dir = tmp_path / ".claude" / "docs"
        current_dir = docs_dir / "current" / "plans"
        current_dir.mkdir(parents=True)

        # Update mock config
        mock_config.paths.docs_dir = docs_dir

        # Create test document marked as complete
        doc_path = current_dir / "PLAN-test-2025-01-01.md"
        doc_path.write_text("# Test Plan\n\n## STATUS: COMPLETE")

        # Mock registry data
        active_docs = [
            DocumentEntry(
                document="PLAN-test-2025-01-01.md",
                type="Plan",
                location="current/plans",
                created="2025-01-01",
                status="Active",  # Not yet marked complete in registry
                purpose="Test plan",
            )
        ]

        # Mock registry manager
        with patch.object(archiver.registry_manager, "parse_registry") as mock_parse:
            mock_parse.return_value = (active_docs, [])

            with patch.object(archiver.registry_manager, "update_document_status") as mock_update:
                # Mock current date (document is old enough)
                with patch("claudecraftsman.core.archival.datetime") as mock_datetime:
                    mock_datetime.now.return_value = datetime(2025, 1, 30)
                    mock_datetime.strptime = datetime.strptime

                    # Monitor the document
                    archiver.monitor_document_changes(doc_path)

                    # Should update status to Complete
                    mock_update.assert_called_once_with("PLAN-test-2025-01-01.md", "Complete")

    def test_create_archive_manifest(self, archiver, mock_config, tmp_path):
        """Test creating an archive manifest."""
        # Setup test environment
        archive_dir = tmp_path / ".claude" / "docs" / "archive" / "2025-01-30"
        archive_dir.mkdir(parents=True)

        # Update mock config
        archiver.archive_dir = tmp_path / ".claude" / "docs" / "archive"

        # Create archived documents
        doc1 = archive_dir / "PLAN-feature-2025-01-01.md"
        doc1.write_text("# Feature Plan\n\nThis is a test plan.")

        doc2 = archive_dir / "IMPL-feature-2025-01-05.md"
        doc2.write_text("# Feature Implementation\n\nThis is the implementation.")

        # Create manifest
        archiver.create_archive_manifest("2025-01-30")

        # Check manifest was created
        manifest_path = archive_dir / "ARCHIVE-MANIFEST.md"
        assert manifest_path.exists()

        # Check manifest content
        content = manifest_path.read_text()
        assert "**Archive Date**: 2025-01-30" in content
        assert "**Documents Archived**: 2" in content
        assert "PLAN-feature-2025-01-01.md" in content
        assert "IMPL-feature-2025-01-05.md" in content
        assert "Feature Plan" in content
        assert "Feature Implementation" in content

    def test_auto_archive_dry_run(self, archiver, sample_docs, mock_config, tmp_path):
        """Test auto-archive in dry run mode."""
        # Setup test environment
        docs_dir = tmp_path / ".claude" / "docs"
        current_dir = docs_dir / "current" / "plans"
        current_dir.mkdir(parents=True)

        # Update mock config
        mock_config.paths.docs_dir = docs_dir

        # Create old complete document
        doc_path = current_dir / "PLAN-test-2025-01-01.md"
        doc_path.write_text("# Test Plan\n\n## STATUS: COMPLETE")

        # Mock registry
        with patch.object(archiver.registry_manager, "parse_registry") as mock_parse:
            mock_parse.return_value = ([sample_docs[0]], [])

            # Mock current date
            with patch("claudecraftsman.core.archival.datetime") as mock_datetime:
                mock_datetime.now.return_value = datetime(2025, 1, 30)
                mock_datetime.strptime = datetime.strptime
                mock_datetime.fromtimestamp = datetime.fromtimestamp

                # Run auto-archive in dry run mode
                count = archiver.auto_archive(dry_run=True)

                # Should find 1 document but not archive it
                assert count == 0
                assert doc_path.exists()  # Document should still exist


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
