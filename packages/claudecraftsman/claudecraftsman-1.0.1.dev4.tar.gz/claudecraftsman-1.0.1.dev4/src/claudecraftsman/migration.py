"""
Migration utilities for transitioning from shell-based to Python ClaudeCraftsman.

This module provides functionality to help users migrate from the old shell script
implementation to the new Python package.
"""

import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm

console = Console()


class ClaudeCraftsmanMigrator:
    """Handles migration from shell scripts to Python package."""

    def __init__(self) -> None:
        """Initialize migrator with paths and configuration."""
        self.home = Path.home()
        self.old_install_dir = self.home / ".claude" / "claudecraftsman"
        self.old_scripts_dir = self.old_install_dir / "scripts"
        self.backup_dir: Path | None = None
        self.user_data_dirs = ["docs", "context", "project-mgt"]
        self.shell_configs = [
            self.home / ".bashrc",
            self.home / ".zshrc",
            self.home / ".bash_profile",
            self.home / ".profile",
        ]

    def check_existing_installation(self) -> bool:
        """
        Check if old shell scripts installation exists.

        Returns:
            True if old installation found, False otherwise
        """
        if not self.old_scripts_dir.exists():
            console.print("[green]✅ No shell-based installation found.[/green]")
            console.print("\nYou can install the Python package directly:")
            console.print("  [cyan]uvx claudecraftsman install[/cyan]")
            return False

        console.print("[yellow]📦 Found existing shell-based ClaudeCraftsman installation[/yellow]")
        return True

    def create_backup(self) -> Path:
        """
        Create backup of existing installation.

        Returns:
            Path to backup directory
        """
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.backup_dir = self.home / ".claude" / f"claudecraftsman-backup-{timestamp}"

        console.print(f"\n[cyan]📁 Creating backup at: {self.backup_dir}[/cyan]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Backing up existing installation...", total=1)
            # self.backup_dir is guaranteed to be set at this point
            assert self.backup_dir is not None
            shutil.copytree(self.old_install_dir, self.backup_dir)
            progress.update(task, completed=1)

        console.print("[green]✅ Backup created successfully[/green]")
        return self.backup_dir

    def check_uv_installed(self) -> bool:
        """
        Check if UV package manager is installed.

        Returns:
            True if UV is installed, False otherwise
        """
        try:
            subprocess.run(["uv", "--version"], check=True, capture_output=True)
            console.print("\n[green]✅ UV is installed[/green]")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            console.print("\n[red]❌ UV not found. Please install UV first:[/red]")
            console.print("  [cyan]curl -LsSf https://astral.sh/uv/install.sh | sh[/cyan]")
            console.print("\nAfter installing UV, run this migration again.")
            return False

    def preserve_user_data(self) -> Path:
        """
        Preserve user data directories.

        Returns:
            Path to temporary data directory
        """
        console.print("\n[cyan]📋 Preserving user data...[/cyan]")

        temp_dir = Path(f"/tmp/claudecraftsman-userdata-{datetime.now().strftime('%Y%m%d%H%M%S')}")
        temp_dir.mkdir(parents=True, exist_ok=True)

        for dir_name in self.user_data_dirs:
            source_dir = self.home / ".claude" / dir_name
            if source_dir.exists():
                console.print(f"  - Preserving {dir_name}/")
                shutil.copytree(source_dir, temp_dir / dir_name)

        console.print("[green]✅ User data preserved[/green]")
        return temp_dir

    def install_python_package(self) -> bool:
        """
        Install ClaudeCraftsman Python package.

        Returns:
            True if installation successful, False otherwise
        """
        console.print("\n[cyan]🐍 Installing ClaudeCraftsman Python package...[/cyan]\n")

        # Check if we're in development directory
        pyproject_path = Path("pyproject.toml")
        if pyproject_path.exists():
            try:
                content = pyproject_path.read_text()
                if 'name = "claudecraftsman"' in content:
                    console.print(
                        "[yellow]📦 Installing from local development directory...[/yellow]"
                    )
                    result = subprocess.run(
                        [sys.executable, "-m", "pip", "install", "-e", "."],
                        check=False,
                        capture_output=True,
                        text=True,
                    )
                    if result.returncode == 0:
                        console.print("[green]✅ Development installation successful[/green]")
                        return True
                    else:
                        console.print(f"[red]❌ Installation failed: {result.stderr}[/red]")
                        return False
            except Exception as e:
                console.print(f"[red]❌ Error checking pyproject.toml: {e}[/red]")

        # Install from PyPI
        console.print("[yellow]📦 Installing from PyPI...[/yellow]")
        result = subprocess.run(
            ["uvx", "claudecraftsman", "install"], check=False, capture_output=True, text=True
        )

        if result.returncode == 0:
            console.print("[green]✅ Python package installed successfully[/green]")
            return True
        else:
            console.print(f"[red]❌ Installation failed: {result.stderr}[/red]")
            return False

    def restore_user_data(self, temp_dir: Path) -> None:
        """
        Restore user data from temporary directory.

        Args:
            temp_dir: Path to temporary data directory
        """
        console.print("\n[cyan]📋 Restoring user data...[/cyan]")

        for dir_name in self.user_data_dirs:
            source_dir = temp_dir / dir_name
            if source_dir.exists():
                console.print(f"  - Restoring {dir_name}/")
                dest_dir = self.home / ".claude" / dir_name

                # Copy files without overwriting newer ones
                if dest_dir.exists():
                    # Copy individual files to avoid overwriting
                    for file_path in source_dir.rglob("*"):
                        if file_path.is_file():
                            relative_path = file_path.relative_to(source_dir)
                            dest_path = dest_dir / relative_path

                            # Only copy if destination doesn't exist or is older
                            if not dest_path.exists() or (
                                dest_path.stat().st_mtime < file_path.stat().st_mtime
                            ):
                                dest_path.parent.mkdir(parents=True, exist_ok=True)
                                shutil.copy2(file_path, dest_path)
                else:
                    shutil.copytree(source_dir, dest_dir)

        # Clean up temp directory
        shutil.rmtree(temp_dir)
        console.print("[green]✅ User data restored[/green]")

    def update_shell_configs(self) -> None:
        """Update shell configuration files to remove old PATH entries."""
        console.print("\n[cyan]🔧 Updating shell configuration...[/cyan]")

        for config_path in self.shell_configs:
            if config_path.exists():
                try:
                    # Read config file
                    content = config_path.read_text()

                    # Remove lines containing old script paths
                    lines = content.split("\n")
                    filtered_lines = [
                        line for line in lines if ".claude/claudecraftsman/scripts" not in line
                    ]

                    # Only write if changes were made
                    if len(lines) != len(filtered_lines):
                        # Create backup
                        backup_path = config_path.with_suffix(config_path.suffix + ".bak")
                        shutil.copy2(config_path, backup_path)

                        # Write filtered content
                        config_path.write_text("\n".join(filtered_lines))
                        console.print(f"  - Cleaned up {config_path.name}")
                except Exception as e:
                    console.print(
                        f"  [yellow]- Warning: Could not update {config_path.name}: {e}[/yellow]"
                    )

        console.print("[green]✅ Shell configuration updated[/green]")

    def verify_installation(self) -> bool:
        """
        Verify that the Python installation is working.

        Returns:
            True if verification successful, False otherwise
        """
        console.print("\n[cyan]🔍 Verifying installation...[/cyan]")

        try:
            result = subprocess.run(
                ["claudecraftsman", "--version"], check=False, capture_output=True, text=True
            )

            if result.returncode == 0:
                console.print("[green]✅ ClaudeCraftsman Python CLI is available[/green]")
                console.print("\n[cyan]📊 Version information:[/cyan]")
                console.print(result.stdout)
                return True
            else:
                raise subprocess.CalledProcessError(result.returncode, "claudecraftsman")

        except (subprocess.CalledProcessError, FileNotFoundError):
            console.print("[yellow]⚠️  ClaudeCraftsman command not found in PATH[/yellow]")
            console.print("  You may need to restart your shell or run:")
            console.print("    [cyan]source ~/.bashrc[/cyan]  # or ~/.zshrc")
            return False

    def show_migration_summary(self) -> None:
        """Display migration summary and next steps."""
        console.print("\n[bold cyan]📝 Migration Summary[/bold cyan]")
        console.print("=" * 40)
        console.print()

        if self.backup_dir:
            console.print(f"✅ Backup created at: {self.backup_dir}")
        console.print("✅ Python package installed")
        console.print("✅ User data preserved")
        console.print("✅ Shell configuration cleaned up")
        console.print()

        console.print("[bold]🎯 Next Steps:[/bold]")
        console.print("1. Restart your shell or source your shell config")
        console.print("2. Run 'claudecraftsman status' to verify installation")
        if self.backup_dir:
            console.print(f"3. Old shell scripts backed up to: {self.backup_dir}")
        console.print()

        console.print("[bold]📚 Command changes:[/bold]")
        console.print("  [dim]Old:[/dim] cc-state-update document-created ...")
        console.print("  [green]New:[/green] claudecraftsman state document-created ...")
        console.print()
        console.print("  [dim]Old:[/dim] cc-validate all")
        console.print("  [green]New:[/green] claudecraftsman validate quality")
        console.print()
        console.print("  [dim]Old:[/dim] cc-install")
        console.print("  [green]New:[/green] claudecraftsman install")
        console.print()
        console.print("For full documentation, run: [cyan]claudecraftsman --help[/cyan]")
        console.print()
        console.print(
            "[bold green]🎉 Migration complete! Welcome to ClaudeCraftsman Python Edition![/bold green]"
        )

    def run_migration(self, skip_backup: bool = False, auto_confirm: bool = False) -> bool:
        """
        Run the complete migration process.

        Args:
            skip_backup: Skip creating backup
            auto_confirm: Auto-confirm all prompts

        Returns:
            True if migration successful, False otherwise
        """
        console.print("[bold cyan]🔄 ClaudeCraftsman Migration to Python Package[/bold cyan]")
        console.print("=" * 45)
        console.print()

        # Check for existing installation
        if not self.check_existing_installation():
            return True  # No migration needed

        # Confirm migration
        if not auto_confirm and not Confirm.ask("\nProceed with migration?"):
            console.print("[yellow]Migration cancelled[/yellow]")
            return False

        # Create backup
        if not skip_backup:
            self.create_backup()

        # Check UV installation
        if not self.check_uv_installed():
            return False

        # Preserve user data
        temp_data_dir = self.preserve_user_data()

        try:
            # Install Python package
            if not self.install_python_package():
                return False

            # Restore user data
            self.restore_user_data(temp_data_dir)

            # Update shell configs
            self.update_shell_configs()

            # Verify installation
            self.verify_installation()

            # Show summary
            self.show_migration_summary()

            return True

        except Exception as e:
            console.print(f"\n[red]❌ Migration failed: {e}[/red]")
            if temp_data_dir.exists():
                console.print(f"[yellow]User data preserved at: {temp_data_dir}[/yellow]")
            return False


def migrate_from_shell() -> bool:
    """
    Main entry point for migration from shell scripts.

    Returns:
        True if migration successful, False otherwise
    """
    migrator = ClaudeCraftsmanMigrator()
    return migrator.run_migration()
