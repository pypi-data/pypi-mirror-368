"""
Framework enforcement hooks for ClaudeCraftsman.

Automatically enforces framework standards and updates state.
"""

import os
import re
from datetime import datetime
from pathlib import Path

from claudecraftsman.core.registry import RegistryManager
from claudecraftsman.core.state import StateManager
from claudecraftsman.utils.git import GitOperations


class FrameworkEnforcer:
    """Enforces framework standards through automatic actions."""

    # Document type to subdirectory mapping
    DOCUMENT_TYPE_DIRS = {
        "PLAN": "plans",
        "IMPL": "implementation",
        "ARCH": "architecture",
        "MAINT": "maintenance",
        "MIGRATION": "migration",
        "TECH": "technical",
        "TECH-SPEC": "technical",  # Added compound type
        "PRD": "PRDs",
        "SPEC": "specs",
        "TEST": "testing",
        "USER-GUIDE": "guides",
        "INSTALL-GUIDE": "guides",
        "ANALYSIS": "plans",
        "RECOMMENDATIONS": "plans",
        "SUMMARY": "implementation",
        "VALIDATION": "implementation",
    }

    def __init__(self) -> None:
        """Initialize enforcer with managers."""
        self.state_manager = StateManager()
        self.registry_manager = RegistryManager()
        self.git_operations = GitOperations()

    def can_auto_correct(self, violations: list[tuple[str, str]]) -> bool:
        """
        Check if violations can be automatically corrected.

        Args:
            violations: List of (violation_type, error_message) tuples

        Returns:
            True if all violations can be auto-corrected
        """
        auto_correctable = [
            "naming_convention",  # Can suggest correct format
            "hardcoded_dates",  # Can replace with dynamic dates
        ]

        return all(violation_type in auto_correctable for violation_type, _ in violations)

    def auto_correct_naming(self, filepath: str) -> str:
        """
        Auto-correct file naming to match convention.

        Args:
            filepath: Original filepath

        Returns:
            Corrected filepath
        """
        path = Path(filepath)
        filename = path.name

        # Extract components from filename
        # First check for lowercase prefixes
        lowercase_prefixes = {
            "plan-": "PLAN",
            "spec-": "SPEC",
            "prd-": "PRD",
            "impl-": "IMPL",
            "arch-": "ARCH",
            "doc-": "DOC",
            "test-": "TEST",
        }

        doc_type = "DOC"  # Default
        name_part = filename

        # Check lowercase prefixes first
        for prefix, doc_type_value in lowercase_prefixes.items():
            if filename.lower().startswith(prefix):
                doc_type = doc_type_value
                name_part = filename[len(prefix) :]
                break
        else:
            # Try to identify uppercase type
            type_match = re.search(r"^([A-Z]+)", filename)
            if type_match:
                doc_type = type_match.group(1)
                name_part = re.sub(r"^[A-Z]+-?", "", filename)  # Remove type prefix

        # Clean up name part
        name_part = re.sub(r"\.[^.]+$", "", name_part)  # Remove extension
        name_part = re.sub(r"-?\d{4}-\d{2}-\d{2}", "", name_part)  # Remove dates
        name_part = re.sub(r"-old-date$", "", name_part)  # Remove "old-date" suffix
        name_part = name_part.strip("-_")

        if not name_part:
            name_part = "document"

        # Generate correct filename
        today = datetime.now().strftime("%Y-%m-%d")
        correct_name = f"{doc_type}-{name_part}-{today}.md"

        # Build path with correct subdirectory
        corrected_path = str(path.parent / correct_name)

        # Organize into correct subdirectory
        organized_path = self.organize_document(corrected_path)

        return organized_path

    def auto_correct_dates(self, content: str, current_date: str) -> str:
        """
        Replace hardcoded dates with template markers.

        Args:
            content: Document content
            current_date: Current date in YYYY-MM-DD format

        Returns:
            Content with dates replaced
        """
        # Pattern for dates to replace
        date_patterns = [
            (r"\b202[0-9]-[0-1][0-9]-[0-3][0-9]\b", current_date),
            (
                r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+202[0-9]\b",
                datetime.now().strftime("%B %d, %Y"),
            ),
        ]

        # Skip dates in headers
        lines = content.split("\n")
        for i, line in enumerate(lines):
            # Skip header lines
            if re.match(r"^\*?Date:", line) or re.match(r"^Created:", line):
                continue

            # Replace dates in this line
            for pattern, replacement in date_patterns:
                lines[i] = re.sub(pattern, replacement, lines[i])

        return "\n".join(lines)

    def get_correct_subdirectory(self, filename: str) -> str | None:
        """
        Determine the correct subdirectory for a document based on its type.

        Args:
            filename: Document filename

        Returns:
            Subdirectory name or None if not applicable
        """
        # Extract document type from filename
        type_match = re.match(r"^([A-Z-]+)-", filename)
        if not type_match:
            return None

        doc_type = type_match.group(1)

        # Check direct mapping
        if doc_type in self.DOCUMENT_TYPE_DIRS:
            return self.DOCUMENT_TYPE_DIRS[doc_type]

        # Check compound types (e.g., USER-GUIDE)
        for compound_type, subdir in self.DOCUMENT_TYPE_DIRS.items():
            if doc_type == compound_type:
                return subdir

        return None

    def organize_document(self, filepath: str) -> str:
        """
        Organize document into correct subdirectory.

        Args:
            filepath: Current file path

        Returns:
            New file path in correct subdirectory
        """
        path = Path(filepath)
        filename = path.name

        # Skip if not in .claude/docs/current/
        if ".claude/docs/current/" not in str(path):
            return filepath

        # Determine correct subdirectory
        subdir = self.get_correct_subdirectory(filename)
        if not subdir:
            return filepath

        # Extract the base path from the filepath
        path_str = str(path).replace(os.sep, "/")
        if ".claude/docs/current/" in path_str:
            # Find the base path up to .claude/
            claude_idx = path_str.find(".claude/")
            if claude_idx >= 0:
                base_path = path_str[:claude_idx]
                docs_current = Path(base_path) / ".claude" / "docs" / "current"
            else:
                docs_current = Path(".claude/docs/current")
        else:
            # Fallback to current directory
            docs_current = Path(".claude/docs/current")

        correct_dir = docs_current / subdir

        # Create directory if it doesn't exist
        correct_dir.mkdir(parents=True, exist_ok=True)

        # Build new path
        new_path = correct_dir / filename

        # Move file if it exists and is in wrong location
        if path.exists() and path != new_path:
            import shutil

            shutil.move(str(path), str(new_path))
            return str(new_path)

        return str(new_path)

    def update_registry_for_file(self, filepath: str, operation: str) -> bool:
        """
        Update document registry for file operation.

        Args:
            filepath: Path to file
            operation: Type of operation (create, update, delete)

        Returns:
            True if registry updated successfully
        """
        path = Path(filepath)

        # Only track files in .claude/docs/current/
        if ".claude/docs/current/" not in str(path):
            return True

        # Skip registry.md itself
        if path.name == "registry.md":
            return True

        try:
            if operation == "create":
                # Use the new auto-register method that parses metadata
                return self.registry_manager.auto_register_document(path)
            elif operation == "update":
                # Check if document exists in registry
                active_docs, _ = self.registry_manager.parse_registry()
                doc_exists = any(doc.document == path.name for doc in active_docs)

                if not doc_exists:
                    # Auto-register if not in registry
                    return self.registry_manager.auto_register_document(path)
                else:
                    # Parse current status from document
                    metadata = self.registry_manager.parse_document_metadata(path)
                    return self.registry_manager.update_document_status(
                        path.name, metadata["status"]
                    )
            elif operation == "delete":
                # Archive the document if it exists
                active_docs, _ = self.registry_manager.parse_registry()
                if any(doc.document == path.name for doc in active_docs):
                    return self.registry_manager.archive_document(path.name, "Document deleted")

            return True

        except Exception as e:
            # Log but don't fail the operation
            print(f"Warning: Registry update failed for {filepath}: {e}")
            return True

    def track_progress(self, operation: str, filepath: str) -> bool:
        """
        Track progress in the progress log.

        Args:
            operation: Type of operation
            filepath: Path to file

        Returns:
            True if progress tracked successfully
        """
        # This would integrate with progress tracking
        # For now, we'll use state manager methods
        return True

    def update_workflow_state(self, operation: str, filepath: str) -> bool:
        """
        Update workflow state based on operation.

        Args:
            operation: Type of operation
            filepath: Path to file

        Returns:
            True if state updated successfully
        """
        # Determine if this affects workflow state
        path = Path(filepath)
        filename = path.name

        # Key files that affect workflow
        workflow_files = {
            "PRD-": "requirements",
            "TECH-SPEC-": "design",
            "IMPL-": "implementation",
            "TEST-": "testing",
        }

        for prefix, phase in workflow_files.items():
            if filename.startswith(prefix):
                # This operation affects a workflow phase
                if operation == "create":
                    return self.state_manager.phase_started(
                        phase=phase,
                        agent="framework-user",
                        description=f"Started {phase} phase with {filename}",
                    )
                elif operation == "update" and "COMPLETE" in filename:
                    return self.state_manager.phase_completed(
                        phase=phase, agent="framework-user", description=f"Completed {phase} phase"
                    )

        return True

    def create_semantic_commit(self, operation: str, files: list[str]) -> bool:
        """
        Create a semantic commit for the operation.

        Args:
            operation: Type of operation
            files: List of affected files

        Returns:
            True if commit created successfully
        """
        if not files:
            return True

        # Determine commit type and scope
        commit_types = {
            "create": "feat",
            "update": "docs",
            "fix": "fix",
            "refactor": "refactor",
        }

        commit_type = commit_types.get(operation, "chore")

        # Determine scope from files
        if any(".claude/docs/" in f for f in files):
            scope = "docs"
        elif any(".claude/agents/" in f for f in files):
            scope = "agents"
        elif any("src/" in f for f in files):
            scope = "core"
        else:
            scope = "framework"

        # Generate commit message
        file_count = len(files)
        if file_count == 1:
            filename = Path(files[0]).name
            message = f"{commit_type}({scope}): {operation} {filename}"
        else:
            message = f"{commit_type}({scope}): {operation} {file_count} files"

        # Add file list to commit body
        body_lines = [message, ""]
        for file in files:
            body_lines.append(f"- {file}")
        body_lines.extend(["", "Automated commit by ClaudeCraftsman framework enforcement"])

        commit_message = "\n".join(body_lines)

        # Stage files and create commit
        try:
            if self.git_operations.add_files(files):
                return self.git_operations.commit(commit_message)
            return False
        except Exception:
            # Git operations are optional
            return True

    def enforce_post_operation(self, operation: str, filepath: str, success: bool = True) -> None:
        """
        Enforce post-operation updates.

        Args:
            operation: Type of operation (create, update, delete)
            filepath: Path to affected file
            success: Whether the operation succeeded
        """
        if not success:
            return

        # Update registry
        self.update_registry_for_file(filepath, operation)

        # Track progress
        self.track_progress(operation, filepath)

        # Update workflow state
        self.update_workflow_state(operation, filepath)

        # Stage for commit (actual commit happens later)
        try:
            self.git_operations.add_files([filepath])
        except Exception:
            # Git operations are optional
            pass
