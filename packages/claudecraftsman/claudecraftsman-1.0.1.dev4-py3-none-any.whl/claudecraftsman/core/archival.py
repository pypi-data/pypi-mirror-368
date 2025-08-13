"""
Automatic document archival system for ClaudeCraftsman.

Monitors documents for completion status and automatically archives them
when appropriate, maintaining document history and registry integrity.
"""

import re
from datetime import datetime
from pathlib import Path

from rich.console import Console

from claudecraftsman.core.completion_detector import CompletionDetector
from claudecraftsman.core.config import get_config
from claudecraftsman.core.registry import RegistryManager
from claudecraftsman.utils.git import GitOperations

console = Console()


class DocumentArchiver:
    """Manages automatic archival of completed documents."""

    def __init__(self, config=None) -> None:
        """Initialize archiver with configuration."""
        self.config = config or get_config()
        self.registry_manager = RegistryManager(config)
        self.git_operations = GitOperations()
        self.completion_detector = CompletionDetector()
        self.docs_dir = self.config.paths.docs_dir
        self.archive_dir = self.docs_dir / "archive"

        # Patterns for completion detection (legacy, kept for compatibility)
        self.completion_patterns = [
            r"STATUS:\s*COMPLETE",
            r"STATUS:\s*Complete",
            r"## STATUS:\s*Phase \d+ COMPLETE",
            r"✅\s*COMPLETE",
            r"### Status:\s*Complete",
            r"Implementation Status:\s*Complete",
            r"Phase Status:\s*Complete",
        ]

        # Document age threshold for auto-archival (days)
        # Note: Completed documents are archived immediately regardless of age
        self.archive_age_days = 7

    def detect_completion_status(self, filepath: Path) -> bool:
        """
        Detect if a document is marked as complete using intelligent analysis.

        Args:
            filepath: Path to document

        Returns:
            True if document is marked complete
        """
        try:
            if not filepath.exists():
                return False

            # First try intelligent completion detection
            analysis = self.completion_detector.analyze_document(filepath)

            # If high confidence in completion, use that
            if analysis["confidence"] >= 0.8:
                if analysis["is_complete"]:
                    console.print(
                        f"[green]Document '{filepath.name}' detected as complete (confidence: {analysis['confidence']:.0%})[/green]"
                    )
                    console.print(f"[dim]  Reason: {analysis['reason']}[/dim]")
                    if analysis["criteria_met"]:
                        console.print(
                            f"[dim]  Criteria met: {len(analysis['criteria_met'])} items[/dim]"
                        )
                return bool(analysis["is_complete"])

            # Fall back to legacy pattern matching for lower confidence
            content = filepath.read_text()

            # Check for any completion pattern
            for pattern in self.completion_patterns:
                if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                    return True

            # Check filename patterns
            filename = filepath.name
            if any(marker in filename for marker in ["COMPLETE", "FINAL", "DONE"]):
                return True

            # If analysis had medium confidence (0.5-0.8), report the pending criteria
            if 0.5 <= analysis["confidence"] < 0.8 and analysis["criteria_pending"]:
                console.print(f"[yellow]Document '{filepath.name}' not complete yet:[/yellow]")
                for criterion in analysis["criteria_pending"][:3]:  # Show first 3
                    console.print(f"[dim]  - {criterion}[/dim]")
                if len(analysis["criteria_pending"]) > 3:
                    console.print(
                        f"[dim]  - ...and {len(analysis['criteria_pending']) - 3} more[/dim]"
                    )

            return False

        except Exception as e:
            console.print(
                f"[yellow]Warning: Could not check completion status for {filepath}: {e}[/yellow]"
            )
            return False

    def get_document_age(self, filepath: Path) -> int | None:
        """
        Get the age of a document in days based on its filename date.

        Args:
            filepath: Path to document

        Returns:
            Age in days or None if date cannot be determined
        """
        try:
            # Extract date from filename (TYPE-name-YYYY-MM-DD.md)
            filename = filepath.name
            date_match = re.search(r"(\d{4}-\d{2}-\d{2})\.md$", filename)

            if date_match:
                date_str = date_match.group(1)
                doc_date = datetime.strptime(date_str, "%Y-%m-%d")
                age_days = (datetime.now() - doc_date).days
                return age_days

            # Fallback to file modification time
            mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
            age_days = (datetime.now() - mtime).days
            return age_days

        except Exception as e:
            console.print(f"[yellow]Warning: Could not determine age for {filepath}: {e}[/yellow]")
            return None

    def find_archival_candidates(self) -> list[tuple[Path, str]]:
        """
        Find documents that should be archived.

        Returns:
            List of (filepath, reason) tuples for documents to archive
        """
        candidates = []
        current_dir = self.docs_dir / "current"

        # Get all documents from registry
        active_docs, _ = self.registry_manager.parse_registry()

        for doc in active_docs:
            # Skip if already marked for archival or in draft status
            if doc.status in ["Archived", "Draft"]:
                continue

            # Build file path
            doc_path = self.docs_dir / doc.location / doc.document

            if not doc_path.exists():
                continue

            # Check if document is complete
            is_complete = self.detect_completion_status(doc_path)

            # Check document age
            age_days = self.get_document_age(doc_path)

            # Determine if should be archived
            # Archive immediately if complete, regardless of age
            if is_complete:
                if age_days is not None:
                    reason = f"Complete (archived after {age_days} days)"
                else:
                    reason = "Complete"
                candidates.append((doc_path, reason))
                # Update registry status if needed
                if doc.status != "Complete":
                    self.registry_manager.update_document_status(doc.document, "Complete")
            elif doc.status == "Complete":
                # Registry says complete but document doesn't match patterns
                if age_days is not None:
                    reason = f"Registry marked complete (archived after {age_days} days)"
                else:
                    reason = "Registry marked complete"
                candidates.append((doc_path, reason))

        return candidates

    def archive_document(self, filepath: Path, reason: str) -> bool:
        """
        # Handle both single Path and List[Path]
        if isinstance(file_paths, Path):
            file_paths = [file_paths]
        file_path = file_paths[0] if file_paths else None
        if not file_path:
            return False
        Archive a single document.

        Args:
            filepath: Path to document to archive
            reason: Reason for archiving

        Returns:
            True if successfully archived
        """
        try:
            filename = filepath.name

            # Use registry manager's archive functionality
            success = self.registry_manager.archive_document(filename, reason)

            if success:
                console.print(f"[green]✓ Archived {filename}: {reason}[/green]")

                # Stage the changes for git
                archive_date = datetime.now().strftime("%Y-%m-%d")
                archive_path = self.archive_dir / archive_date / filename
                if archive_path.exists():
                    self.git_operations.add_files([str(archive_path)])
                    # Also stage the removal of the original
                    self.git_operations.add_files([str(filepath)])

                return True
            else:
                console.print(f"[red]✗ Failed to archive {filename}[/red]")
                return False

        except Exception as e:
            console.print(f"[red]Error archiving {filepath}: {e}[/red]")
            return False

    def auto_archive(self, dry_run: bool = False) -> int:
        """
        Automatically archive all eligible documents.

        Args:
            dry_run: If True, only show what would be archived

        Returns:
            Number of documents archived
        """
        console.print("[cyan]Scanning for documents to archive...[/cyan]")

        candidates = self.find_archival_candidates()

        if not candidates:
            console.print("[green]No documents need archiving[/green]")
            return 0

        console.print(f"\n[yellow]Found {len(candidates)} documents to archive:[/yellow]")
        for filepath, reason in candidates:
            console.print(f"  • {filepath.name}: {reason}")

        if dry_run:
            console.print("\n[cyan]Dry run - no documents were archived[/cyan]")
            return 0

        archived_count = 0
        for filepath, reason in candidates:
            if self.archive_document(filepath, reason):
                archived_count += 1

        if archived_count > 0:
            # Update registry after all archival operations
            self.registry_manager.sync_registry()

            # Create a summary commit
            if archived_count == 1:
                commit_msg = "chore(archive): auto-archive 1 completed document"
            else:
                commit_msg = f"chore(archive): auto-archive {archived_count} completed documents"

            try:
                self.git_operations.commit(commit_msg)
            except Exception:
                # Git operations are optional
                pass

        console.print(f"\n[green]✓ Archived {archived_count} documents[/green]")
        return archived_count

    def monitor_document_changes(self, filepath: Path) -> None:
        """
        Monitor a document for completion status changes.

        This is called by the hook system when a document is updated.

        Args:
            filepath: Path to document that was changed
        """
        # Only monitor documents in current/
        if ".claude/docs/current/" not in str(filepath):
            return

        # Check if document is now complete
        if self.detect_completion_status(filepath):
            # Update registry status
            filename = filepath.name
            active_docs, _ = self.registry_manager.parse_registry()

            # Find document in registry
            for doc in active_docs:
                if doc.document == filename and doc.status != "Complete":
                    console.print(f"[yellow]Document '{filename}' marked as complete[/yellow]")
                    self.registry_manager.update_document_status(filename, "Complete")

                    # Check if old enough to archive immediately
                    age_days = self.get_document_age(filepath)
                    if age_days is not None and age_days >= self.archive_age_days:
                        console.print(
                            f"[cyan]Document is {age_days} days old - archiving now[/cyan]"
                        )
                        self.archive_document(
                            filepath, f"Auto-archived on completion ({age_days} days old)"
                        )
                    break

    def create_archive_manifest(self, archive_date: str) -> None:
        """
        Create or update the archive manifest for a specific date.

        Args:
            archive_date: Date string in YYYY-MM-DD format
        """
        archive_date_dir = self.archive_dir / archive_date
        if not archive_date_dir.exists():
            return

        manifest_path = archive_date_dir / "ARCHIVE-MANIFEST.md"

        # Get all documents in this archive directory
        archived_docs = list(archive_date_dir.glob("*.md"))
        archived_docs = [d for d in archived_docs if d.name != "ARCHIVE-MANIFEST.md"]

        if not archived_docs:
            return

        # Create manifest content
        content = f"""# Archive Manifest
**Archive Date**: {archive_date}
**Documents Archived**: {len(archived_docs)}

## Archived Documents

"""

        for doc_path in sorted(archived_docs):
            # Try to extract metadata from document
            try:
                doc_content = doc_path.read_text()
                lines = doc_content.split("\n")[:10]

                # Find title
                title = doc_path.name
                for line in lines:
                    if line.startswith("# "):
                        title = line[2:].strip()
                        break

                content += f"### {doc_path.name}\n"
                content += f"- **Title**: {title}\n"
                content += f"- **Size**: {doc_path.stat().st_size} bytes\n"
                content += "\n"

            except Exception:
                content += f"### {doc_path.name}\n"
                content += f"- **Size**: {doc_path.stat().st_size} bytes\n"
                content += "\n"

        manifest_path.write_text(content)
        console.print(f"[green]✓ Updated archive manifest for {archive_date}[/green]")
