"""
Backward compatibility layer for ClaudeCraftsman.

This module provides compatibility shims and helpers for users
transitioning from the old shell script commands to the new Python CLI.
"""

import os
from pathlib import Path

from rich.console import Console

console = Console()


class CompatibilityLayer:
    """Manages backward compatibility for old shell commands."""

    def __init__(self) -> None:
        """Initialize compatibility layer with command mappings."""
        self.compat_dir = Path.home() / ".local" / "bin"
        self.command_map = {
            "cc-state-update": "claudecraftsman state",
            "cc-validate": "claudecraftsman validate",
            "cc-quality-check": "claudecraftsman validate quality",
            "cc-archive": "claudecraftsman archive",
            "cc-registry-update": "claudecraftsman registry",
            "cc-install": "claudecraftsman install",
            "cc-hook-config": "claudecraftsman hook",
            "framework-state-update.sh": "claudecraftsman state",
            "enforce-quality-gates.sh": "claudecraftsman validate quality",
            "update-registry.sh": "claudecraftsman registry sync",
        }

        self.shell_configs = [
            Path.home() / ".bashrc",
            Path.home() / ".zshrc",
            Path.home() / ".bash_profile",
            Path.home() / ".profile",
        ]

    def ensure_bin_directory(self) -> bool:
        """
        Ensure the compatibility binary directory exists and is in PATH.

        Returns:
            True if directory is ready, False otherwise
        """
        # Create directory
        self.compat_dir.mkdir(parents=True, exist_ok=True)

        # Check if in PATH
        path_dirs = os.environ.get("PATH", "").split(":")
        if str(self.compat_dir) not in path_dirs:
            console.print(f"[yellow]📝 Adding {self.compat_dir} to PATH...[/yellow]")

            # Add to shell configs
            path_line = 'export PATH="$HOME/.local/bin:$PATH"'
            for config_path in self.shell_configs:
                if config_path.exists():
                    try:
                        content = config_path.read_text()
                        if path_line not in content:
                            with open(config_path, "a") as f:
                                f.write("\n# ClaudeCraftsman compatibility layer\n")
                                f.write(f"{path_line}\n")
                            console.print(f"  ✅ Updated {config_path.name}")
                    except Exception as e:
                        console.print(
                            f"  [yellow]⚠️  Could not update {config_path.name}: {e}[/yellow]"
                        )

            console.print("\n[yellow]⚠️  PATH update requires shell restart[/yellow]")
            console.print("  Run: [cyan]source ~/.bashrc[/cyan] (or your shell config)")
            return False

        return True

    def create_shim_script(self, old_command: str, new_command: str) -> bool:
        """
        Create a compatibility shim script.

        Args:
            old_command: Old command name
            new_command: New command to forward to

        Returns:
            True if shim created successfully
        """
        shim_path = self.compat_dir / old_command

        # Generate shim content based on command
        if old_command == "cc-state-update":
            shim_content = f"""#!/bin/bash
# Compatibility shim for {old_command}
# Forwards to: {new_command}

echo "⚠️  Warning: '{old_command}' is deprecated. Please use '{new_command}' instead." >&2
echo "" >&2

# Forward all arguments
exec {new_command} "$@"
"""
        elif old_command == "cc-validate":
            shim_content = f"""#!/bin/bash
# Compatibility shim for {old_command}
# Forwards to: {new_command}

echo "⚠️  Warning: '{old_command}' is deprecated. Please use '{new_command}' instead." >&2
echo "" >&2

# Special handling for 'all' argument
if [[ "$1" == "all" ]]; then
    exec claudecraftsman validate quality
else
    exec {new_command} "$@"
fi
"""
        elif old_command == "cc-quality-check":
            shim_content = f"""#!/bin/bash
# Compatibility shim for {old_command}
# Forwards to: claudecraftsman validate quality

echo "⚠️  Warning: '{old_command}' is deprecated. Please use 'claudecraftsman validate quality' instead." >&2
echo "" >&2

exec claudecraftsman validate quality "$@"
"""
        else:
            # Default shim
            shim_content = f"""#!/bin/bash
# Compatibility shim for {old_command}
# Forwards to: {new_command}

echo "⚠️  Warning: '{old_command}' is deprecated. Please use '{new_command}' instead." >&2
echo "" >&2

exec {new_command} "$@"
"""

        try:
            shim_path.write_text(shim_content)
            shim_path.chmod(0o755)  # Make executable
            return True
        except Exception as e:
            console.print(f"[red]❌ Failed to create shim for {old_command}: {e}[/red]")
            return False

    def create_cc_shorthand(self) -> bool:
        """
        Create 'cc' shorthand for claudecraftsman.

        Returns:
            True if created successfully
        """
        cc_path = self.compat_dir / "cc"

        cc_content = """#!/bin/bash
# Shorthand for claudecraftsman
exec claudecraftsman "$@"
"""

        try:
            cc_path.write_text(cc_content)
            cc_path.chmod(0o755)
            return True
        except Exception as e:
            console.print(f"[red]❌ Failed to create cc shorthand: {e}[/red]")
            return False

    def create_migration_guide(self) -> bool:
        """
        Create cc-migrate helper command.

        Returns:
            True if created successfully
        """
        migrate_path = self.compat_dir / "cc-migrate"

        migrate_content = """#!/bin/bash
# Help users migrate to new commands

echo "🔄 ClaudeCraftsman Command Migration Guide"
echo "========================================="
echo ""
echo "Old Command → New Command:"
echo ""
echo "  cc-state-update ... → claudecraftsman state ..."
echo "  cc-validate all → claudecraftsman validate quality"
echo "  cc-quality-check → claudecraftsman validate quality"
echo "  cc-archive ... → claudecraftsman archive ..."
echo "  cc-registry-update → claudecraftsman registry sync"
echo "  cc-install → claudecraftsman install"
echo "  cc-hook-config → claudecraftsman hook generate"
echo ""
echo "Shorthand available:"
echo "  cc → claudecraftsman"
echo ""
echo "Examples:"
echo "  Old: cc-state-update document-created PRD-test.md PRD docs/ 'Test PRD'"
echo "  New: claudecraftsman state document-created PRD-test.md PRD docs/ 'Test PRD'"
echo "  Or:  cc state document-created PRD-test.md PRD docs/ 'Test PRD'"
echo ""
echo "To remove compatibility layer after migration:"
echo "  rm ~/.local/bin/cc-*"
echo ""
"""

        try:
            migrate_path.write_text(migrate_content)
            migrate_path.chmod(0o755)
            return True
        except Exception as e:
            console.print(f"[red]❌ Failed to create migration guide: {e}[/red]")
            return False

    def install_compatibility_layer(self) -> bool:
        """
        Install the complete compatibility layer.

        Returns:
            True if installation successful
        """
        console.print("[bold cyan]🔧 Installing ClaudeCraftsman Compatibility Layer[/bold cyan]")
        console.print("=" * 47)
        console.print()

        # Ensure bin directory
        if not self.ensure_bin_directory():
            return False

        console.print("\n[cyan]📦 Creating compatibility shims...[/cyan]")

        # Create shims for all old commands
        success_count = 0
        for old_cmd, new_cmd in self.command_map.items():
            if self.create_shim_script(old_cmd, new_cmd):
                console.print(f"  ✅ Created shim: {old_cmd} → {new_cmd}")
                success_count += 1
            else:
                console.print(f"  ❌ Failed: {old_cmd}")

        console.print(f"\n[green]Created {success_count}/{len(self.command_map)} shims[/green]")

        # Create additional helpers
        console.print("\n[cyan]📝 Creating helper commands...[/cyan]")

        if self.create_cc_shorthand():
            console.print("  ✅ Created shorthand: cc → claudecraftsman")

        if self.create_migration_guide():
            console.print("  ✅ Created migration guide: cc-migrate")

        # Summary
        console.print("\n[green]✅ Compatibility layer installed successfully![/green]")
        console.print()
        console.print("[bold]📋 Summary:[/bold]")
        console.print(f"  - Shell script shims created in {self.compat_dir}")
        console.print("  - Old commands will forward to new Python CLI")
        console.print("  - Deprecation warnings will guide migration")
        console.print("  - Run 'cc-migrate' for migration help")
        console.print()
        console.print("[bold]🎯 Next steps:[/bold]")
        console.print("  1. Restart your shell or run: [cyan]source ~/.bashrc[/cyan]")
        console.print("  2. Your old commands will continue working")
        console.print("  3. Gradually migrate to new commands")
        console.print("  4. Remove shims when ready: [cyan]rm ~/.local/bin/cc-*[/cyan]")

        return True

    def check_installed_shims(self) -> list[str]:
        """
        Check which compatibility shims are installed.

        Returns:
            List of installed shim names
        """
        if not self.compat_dir.exists():
            return []

        installed = []
        for old_cmd in self.command_map:
            shim_path = self.compat_dir / old_cmd
            if shim_path.exists():
                installed.append(old_cmd)

        # Check for cc shorthand
        if (self.compat_dir / "cc").exists():
            installed.append("cc")

        # Check for migration guide
        if (self.compat_dir / "cc-migrate").exists():
            installed.append("cc-migrate")

        return installed

    def remove_compatibility_layer(self) -> bool:
        """
        Remove all compatibility shims.

        Returns:
            True if removal successful
        """
        console.print("[cyan]🧹 Removing compatibility layer...[/cyan]")

        if not self.compat_dir.exists():
            console.print("[yellow]No compatibility layer found[/yellow]")
            return True

        removed_count = 0

        # Remove all shims
        for old_cmd in self.command_map:
            shim_path = self.compat_dir / old_cmd
            if shim_path.exists():
                try:
                    shim_path.unlink()
                    console.print(f"  ✅ Removed {old_cmd}")
                    removed_count += 1
                except Exception as e:
                    console.print(f"  ❌ Failed to remove {old_cmd}: {e}")

        # Remove helpers
        for helper in ["cc", "cc-migrate"]:
            helper_path = self.compat_dir / helper
            if helper_path.exists():
                try:
                    helper_path.unlink()
                    console.print(f"  ✅ Removed {helper}")
                    removed_count += 1
                except Exception as e:
                    console.print(f"  ❌ Failed to remove {helper}: {e}")

        console.print(f"\n[green]Removed {removed_count} compatibility shims[/green]")
        console.print(
            "\n[yellow]Note: PATH modifications in shell configs were not removed[/yellow]"
        )
        console.print("You can manually remove them if no longer needed")

        return True


def install_compatibility() -> bool:
    """
    Main entry point for installing compatibility layer.

    Returns:
        True if installation successful
    """
    layer = CompatibilityLayer()
    return layer.install_compatibility_layer()


def check_compatibility() -> list[str]:
    """
    Check installed compatibility shims.

    Returns:
        List of installed shim names
    """
    layer = CompatibilityLayer()
    return layer.check_installed_shims()


def remove_compatibility() -> bool:
    """
    Remove compatibility layer.

    Returns:
        True if removal successful
    """
    layer = CompatibilityLayer()
    return layer.remove_compatibility_layer()
