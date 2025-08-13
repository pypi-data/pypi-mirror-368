"""
Document registry management for ClaudeCraftsman.

Handles document tracking, registry updates, and archive operations.
"""

import re
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field
from rich.console import Console
from rich.table import Table

from claudecraftsman.core.config import Config, get_config

console = Console()


class DocumentEntry(BaseModel):
    """Represents a document in the registry."""

    model_config = ConfigDict(extra="forbid")

    document: str
    type: str
    location: str
    created: str
    status: str = Field(default="Active", pattern="^(Active|Archived|Draft|Complete)$")
    purpose: str


class ArchiveEntry(BaseModel):
    """Represents an archived document."""

    model_config = ConfigDict(extra="forbid")

    document: str
    type: str
    archive_date: str
    location: str
    reason: str


class RegistryManager:
    """Manages the ClaudeCraftsman document registry."""

    def __init__(self, config: Config | None = None) -> None:
        """Initialize registry manager."""
        self.config = config or get_config()
        self.docs_dir = self.config.paths.docs_dir
        self.registry_file = self.docs_dir / "current" / "registry.md"
        self.archive_dir = self.docs_dir / "archive"

        # Document type patterns for metadata extraction
        self.doc_type_patterns = {
            "PLAN": "Plan",
            "IMPL": "Implementation",
            "ARCH": "Architecture",
            "MAINT": "Maintenance",
            "MIGRATION": "Migration",
            "TECH": "Technical",
            "TECH-SPEC": "Technical Specification",
            "PRD": "Product Requirements",
            "SPEC": "Specification",
            "TEST": "Test",
            "USER-GUIDE": "User Guide",
            "INSTALL-GUIDE": "Installation Guide",
            "ANALYSIS": "Analysis",
            "RECOMMENDATIONS": "Recommendations",
            "SUMMARY": "Summary",
            "VALIDATION": "Validation",
        }

    def ensure_docs_structure(self) -> bool:
        """Ensure documentation directory structure exists."""
        try:
            (self.docs_dir / "current").mkdir(parents=True, exist_ok=True)
            self.archive_dir.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            console.print(f"[red]Error creating docs structure: {e}[/red]")
            return False

    def parse_registry(self) -> tuple[list[DocumentEntry], list[ArchiveEntry]]:
        """Parse registry markdown file into document entries."""
        active_docs: list[DocumentEntry] = []
        archived_docs: list[ArchiveEntry] = []

        if not self.registry_file.exists():
            return active_docs, archived_docs

        try:
            content = self.registry_file.read_text()
            lines = content.split("\n")

            in_active_section = False
            in_archive_section = False

            for _i, line in enumerate(lines):
                line = line.strip()

                # Section detection
                if "## Current Active Documents" in line or "Current Active Documents" in line:
                    in_active_section = True
                    in_archive_section = False
                    continue
                elif "## Recently Archived" in line or "Recently Archived" in line:
                    in_active_section = False
                    in_archive_section = True
                    continue

                # Skip non-table rows but not header detection line
                if not line.startswith("|"):
                    continue

                # Skip separator lines and header lines
                if "---" in line:
                    continue

                # Skip the header row itself
                if line.startswith("| Document"):
                    continue

                # Parse table rows
                parts = [p.strip() for p in line.split("|")[1:-1]]  # Skip empty first/last

                if in_active_section and len(parts) >= 6:
                    # Skip empty rows
                    if parts[0]:
                        active_docs.append(
                            DocumentEntry(
                                document=parts[0],
                                type=parts[1],
                                location=parts[2],
                                created=parts[3],
                                status=parts[4],
                                purpose=parts[5],
                            )
                        )
                elif in_archive_section and len(parts) >= 5:
                    archived_docs.append(
                        ArchiveEntry(
                            document=parts[0],
                            type=parts[1],
                            archive_date=parts[2],
                            location=parts[3],
                            reason=parts[4],
                        )
                    )

            return active_docs, archived_docs

        except Exception as e:
            console.print(f"[red]Error parsing registry: {e}[/red]")
            return [], []

    def add_document(self, entry: DocumentEntry) -> bool:
        """Add a new document to the registry."""
        if not self.ensure_docs_structure():
            return False

        active_docs, archived_docs = self.parse_registry()

        # Check if document already exists
        for doc in active_docs:
            if doc.document == entry.document:
                console.print(f"[yellow]Document '{entry.document}' already exists[/yellow]")
                return False

        # Add new entry
        active_docs.append(entry)

        # Write updated registry
        return self._write_registry(active_docs, archived_docs)

    def parse_document_metadata(self, filepath: Path) -> dict[str, str]:
        """Parse metadata from document content and filename."""
        metadata = {
            "document": filepath.name,
            "type": "Document",
            "location": str(filepath.parent.relative_to(self.docs_dir)),
            "created": datetime.now().strftime("%Y-%m-%d"),
            "status": "Active",
            "purpose": "Document",
        }

        # Extract type from filename
        filename = filepath.name
        # First try compound types (longer prefixes first)
        compound_types = sorted(
            self.doc_type_patterns.items(), key=lambda x: len(x[0]), reverse=True
        )
        for prefix, doc_type in compound_types:
            if filename.startswith(prefix + "-"):
                metadata["type"] = doc_type
                break

        # Extract date from filename (TYPE-name-YYYY-MM-DD.md)
        date_match = re.search(r"(\d{4}-\d{2}-\d{2})\.md$", filename)
        if date_match:
            metadata["created"] = date_match.group(1)

        # Try to parse content for additional metadata
        try:
            if filepath.exists():
                content = filepath.read_text()
                lines = content.split("\n")[:20]  # Check first 20 lines

                for line in lines:
                    line = line.strip()

                    # Check for title (# Title)
                    if line.startswith("# ") and metadata["purpose"] == "Document":
                        metadata["purpose"] = line[2:].strip()

                    # Check for status markers
                    if "STATUS:" in line.upper():
                        status_match = re.search(r"STATUS:\s*(\w+)", line, re.IGNORECASE)
                        if status_match:
                            status = status_match.group(1).capitalize()
                            if status in ["Active", "Complete", "Draft", "Archived"]:
                                metadata["status"] = status

                    # Check for purpose/overview sections
                    if line.startswith("## Overview") or line.startswith("## Purpose"):
                        # Look for next non-empty line
                        idx = lines.index(line)
                        for next_line in lines[idx + 1 :]:
                            if next_line.strip() and not next_line.startswith("#"):
                                # Clean up the purpose text
                                purpose = next_line.strip()
                                if purpose.startswith("- "):
                                    purpose = purpose[2:]
                                metadata["purpose"] = purpose[:100]  # Limit length
                                break

        except Exception as e:
            console.print(f"[yellow]Warning: Could not parse content of {filepath}: {e}[/yellow]")

        return metadata

    def auto_register_document(self, filepath: Path) -> bool:
        """Automatically register a document by parsing its metadata."""
        metadata = self.parse_document_metadata(filepath)

        entry = DocumentEntry(
            document=metadata["document"],
            type=metadata["type"],
            location=metadata["location"],
            created=metadata["created"],
            status=metadata["status"],
            purpose=metadata["purpose"],
        )

        return self.add_document(entry)

    def sync_registry(self) -> int:
        """Sync registry with actual files in docs/current/."""
        console.print("[cyan]Syncing registry with file system...[/cyan]")

        active_docs, archived_docs = self.parse_registry()
        existing_docs = {doc.document for doc in active_docs}

        added_count = 0
        current_dir = self.docs_dir / "current"

        # Scan all subdirectories in current/
        for subdir in current_dir.iterdir():
            if subdir.is_dir() and subdir.name not in ["archive"]:
                for filepath in subdir.glob("*.md"):
                    if filepath.name not in existing_docs:
                        console.print(
                            f"[yellow]Found unregistered document: {filepath.name}[/yellow]"
                        )
                        if self.auto_register_document(filepath):
                            console.print(f"[green]✓ Added {filepath.name} to registry[/green]")
                            added_count += 1

        # Check for orphaned entries (documents in registry but not on disk)
        orphaned = []
        for doc in active_docs:
            doc_path = self.docs_dir / doc.location / doc.document
            if not doc_path.exists():
                orphaned.append(doc.document)
                console.print(f"[red]Orphaned entry: {doc.document} (file not found)[/red]")

        if orphaned:
            console.print(f"\n[yellow]Found {len(orphaned)} orphaned entries in registry[/yellow]")

        console.print(f"\n[green]Sync complete: {added_count} documents added[/green]")
        return added_count

    def validate_registry(self) -> tuple[bool, list[str]]:
        """Validate registry integrity."""
        issues = []
        active_docs, archived_docs = self.parse_registry()

        # Check for duplicate entries
        seen_docs = set()
        for doc in active_docs:
            if doc.document in seen_docs:
                issues.append(f"Duplicate entry: {doc.document}")
            seen_docs.add(doc.document)

        # Check for missing files
        for doc in active_docs:
            doc_path = self.docs_dir / doc.location / doc.document
            if not doc_path.exists():
                issues.append(f"Missing file: {doc.document} at {doc.location}")

        # Check for invalid status values
        valid_statuses = {"Active", "Complete", "Draft", "Archived"}
        for doc in active_docs:
            if doc.status not in valid_statuses:
                issues.append(f"Invalid status '{doc.status}' for {doc.document}")

        # Check for documents that should be archived
        for doc in active_docs:
            if doc.status == "Complete":
                # Check if document is old (>7 days)
                try:
                    created_date = datetime.strptime(doc.created, "%Y-%m-%d")
                    days_old = (datetime.now() - created_date).days
                    if days_old > 7:
                        issues.append(
                            f"Document {doc.document} is Complete and {days_old} days old - consider archiving"
                        )
                except:
                    pass

        return len(issues) == 0, issues

    def update_document_status(self, document_name: str, new_status: str) -> bool:
        """Update the status of a document."""
        active_docs, archived_docs = self.parse_registry()

        found = False
        for doc in active_docs:
            if doc.document == document_name:
                doc.status = new_status
                found = True
                break

        if not found:
            console.print(f"[yellow]Document '{document_name}' not found[/yellow]")
            return False

        return self._write_registry(active_docs, archived_docs)

    def archive_document(self, document_name: str, reason: str) -> bool:
        """Archive a document."""
        active_docs, archived_docs = self.parse_registry()

        # Find document to archive
        doc_to_archive = None
        for i, doc in enumerate(active_docs):
            if doc.document == document_name:
                doc_to_archive = doc
                active_docs.pop(i)
                break

        if not doc_to_archive:
            console.print(f"[yellow]Document '{document_name}' not found[/yellow]")
            return False

        # Create archive entry
        archive_entry = ArchiveEntry(
            document=doc_to_archive.document,
            type=doc_to_archive.type,
            archive_date=datetime.now().strftime("%Y-%m-%d"),
            location=f"docs/archive/{datetime.now().strftime('%Y-%m-%d')}/",
            reason=reason,
        )

        archived_docs.append(archive_entry)

        # Move the actual file
        if self._move_to_archive(doc_to_archive):
            return self._write_registry(active_docs, archived_docs)

        return False

    def _move_to_archive(self, doc: DocumentEntry) -> bool:
        """Move a document file to the archive."""
        try:
            # Create archive date directory
            archive_date_dir = self.archive_dir / datetime.now().strftime("%Y-%m-%d")
            archive_date_dir.mkdir(parents=True, exist_ok=True)

            # Determine source and destination paths
            source_path = self.docs_dir / doc.location / doc.document
            dest_path = archive_date_dir / doc.document

            if source_path.exists():
                # Move the file
                dest_path.write_text(source_path.read_text())
                source_path.unlink()

                # Create archive manifest
                manifest_path = archive_date_dir / "ARCHIVE-MANIFEST.md"
                manifest_content = f"""# Archive Manifest
**Date**: {datetime.now().strftime("%Y-%m-%d")}

## Archived Documents

### {doc.document}
- **Type**: {doc.type}
- **Original Location**: {doc.location}
- **Status at Archive**: {doc.status}
- **Purpose**: {doc.purpose}
"""
                if manifest_path.exists():
                    manifest_content = manifest_path.read_text() + "\n" + manifest_content
                manifest_path.write_text(manifest_content)

                return True
            else:
                console.print(f"[yellow]Source file not found: {source_path}[/yellow]")
                return False

        except Exception as e:
            console.print(f"[red]Error archiving file: {e}[/red]")
            return False

    def _write_registry(
        self, active_docs: list[DocumentEntry], archived_docs: list[ArchiveEntry]
    ) -> bool:
        """Write the registry back to markdown format."""
        try:
            content = f"""# ClaudeCraftsman Document Registry
*Master index of all project documentation*

**Project**: ClaudeCraftsman Framework
**Last Updated**: {datetime.now().strftime("%Y-%m-%d")}

## Current Active Documents
| Document | Type | Location | Created | Status | Purpose |
|----------|------|----------|---------|--------|---------|
"""

            for doc in active_docs:
                content += f"| {doc.document} | {doc.type} | {doc.location} | "
                content += f"{doc.created} | {doc.status} | {doc.purpose} |\n"

            content += "\n## Recently Archived\n"
            content += "| Document | Type | Archive Date | Location | Reason |\n"
            content += "|----------|------|--------------|----------|--------|\n"

            for archive_doc in archived_docs:
                content += (
                    f"| {archive_doc.document} | {archive_doc.type} | {archive_doc.archive_date} | "
                )
                content += f"{archive_doc.location} | {archive_doc.reason} |\n"

            self.registry_file.write_text(content)
            return True

        except Exception as e:
            console.print(f"[red]Error writing registry: {e}[/red]")
            return False

    def display_registry(self) -> None:
        """Display the registry in a formatted table."""
        active_docs, archived_docs = self.parse_registry()

        # Display active documents
        console.print("\n[bold]Active Documents[/bold]")
        active_table = Table(show_header=True, header_style="bold cyan")
        active_table.add_column("Document", style="white")
        active_table.add_column("Type", style="yellow")
        active_table.add_column("Status", justify="center")
        active_table.add_column("Created", style="dim")
        active_table.add_column("Purpose", style="dim", max_width=40)

        for doc in active_docs:
            status_style = {
                "Active": "[green]Active[/green]",
                "Complete": "[blue]Complete[/blue]",
                "Draft": "[yellow]Draft[/yellow]",
            }.get(doc.status, doc.status)

            active_table.add_row(
                doc.document,
                doc.type,
                status_style,
                doc.created,
                doc.purpose,
            )

        console.print(active_table)

        # Display archived documents if any
        if archived_docs:
            console.print("\n[bold]Recently Archived[/bold]")
            archive_table = Table(show_header=True, header_style="bold cyan")
            archive_table.add_column("Document", style="dim")
            archive_table.add_column("Type", style="dim")
            archive_table.add_column("Archived", style="dim")
            archive_table.add_column("Reason", style="dim", max_width=40)

            for archive_doc in archived_docs:
                archive_table.add_row(
                    archive_doc.document,
                    archive_doc.type,
                    archive_doc.archive_date,
                    archive_doc.reason,
                )

            console.print(archive_table)
