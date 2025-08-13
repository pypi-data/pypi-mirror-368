"""
Git utilities for ClaudeCraftsman.

Provides Python wrappers for common git operations.
"""

import contextlib
import subprocess
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field
from rich.console import Console

console = Console()


class GitStatus(BaseModel):
    """Git repository status information."""

    model_config = ConfigDict(extra="forbid")

    is_repo: bool
    current_branch: str | None = None
    modified_files: list[str] = Field(default_factory=list)
    untracked_files: list[str] = Field(default_factory=list)
    staged_files: list[str] = Field(default_factory=list)
    has_conflicts: bool = False
    commit_count: int = 0


class GitOperations:
    """Git operations wrapper."""

    def __init__(self, repo_path: Path | None = None) -> None:
        """Initialize git operations."""
        self.repo_path = repo_path or Path.cwd()

    def _run_git(self, *args: str) -> tuple[bool, str, str]:
        """Run a git command and return success, stdout, stderr."""
        try:
            result = subprocess.run(
                ["git", *args],
                check=False,
                capture_output=True,
                text=True,
                cwd=self.repo_path,
            )
            return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
        except Exception as e:
            return False, "", str(e)

    def is_git_repo(self) -> bool:
        """Check if current directory is a git repository."""
        success, _, _ = self._run_git("rev-parse", "--git-dir")
        return success

    def get_current_branch(self) -> str | None:
        """Get the current git branch."""
        success, branch, _ = self._run_git("rev-parse", "--abbrev-ref", "HEAD")
        return branch if success else None

    def get_status(self) -> GitStatus:
        """Get comprehensive git status."""
        status = GitStatus(is_repo=self.is_git_repo())

        if not status.is_repo:
            return status

        # Get current branch
        status.current_branch = self.get_current_branch()

        # Get file status
        success, output, _ = self._run_git("status", "--porcelain")
        if success:
            for line in output.split("\n"):
                if not line:
                    continue

                status_code = line[:2]
                filename = line[3:]

                if status_code[0] in ["M", "A", "D", "R", "C"]:
                    status.staged_files.append(filename)
                if status_code[1] == "M":
                    status.modified_files.append(filename)
                if status_code == "??":
                    status.untracked_files.append(filename)
                if status_code == "UU":
                    status.has_conflicts = True

        # Get commit count
        success, count, _ = self._run_git("rev-list", "--count", "HEAD")
        if success:
            with contextlib.suppress(ValueError):
                status.commit_count = int(count)

        return status

    def add_files(self, files: list[str]) -> bool:
        """Add files to git staging."""
        if not files:
            return True

        success, _, error = self._run_git("add", *files)
        if not success:
            console.print(f"[red]Error adding files: {error}[/red]")
        return success

    def commit(self, message: str, allow_empty: bool = False) -> bool:
        """Create a git commit."""
        args = ["commit", "-m", message]
        if allow_empty:
            args.append("--allow-empty")

        success, output, error = self._run_git(*args)
        if not success:
            console.print(f"[red]Error committing: {error}[/red]")
        else:
            console.print(f"[green]✓ Committed: {output}[/green]")

        return success

    def create_branch(self, branch_name: str, base_branch: str | None = None) -> bool:
        """Create a new git branch."""
        args = ["checkout", "-b", branch_name]
        if base_branch:
            args.append(base_branch)

        success, _, error = self._run_git(*args)
        if not success:
            console.print(f"[red]Error creating branch: {error}[/red]")
        else:
            console.print(f"[green]✓ Created and switched to branch: {branch_name}[/green]")

        return success

    def switch_branch(self, branch_name: str) -> bool:
        """Switch to a different branch."""
        success, _, error = self._run_git("checkout", branch_name)
        if not success:
            console.print(f"[red]Error switching branch: {error}[/red]")
        else:
            console.print(f"[green]✓ Switched to branch: {branch_name}[/green]")

        return success

    def get_recent_commits(self, count: int = 10) -> list[str]:
        """Get recent commit messages."""
        success, output, _ = self._run_git("log", f"-{count}", "--oneline", "--no-decorate")

        if success and output:
            return output.split("\n")
        return []

    def has_uncommitted_changes(self) -> bool:
        """Check if there are uncommitted changes."""
        status = self.get_status()
        return bool(status.modified_files or status.staged_files or status.untracked_files)
