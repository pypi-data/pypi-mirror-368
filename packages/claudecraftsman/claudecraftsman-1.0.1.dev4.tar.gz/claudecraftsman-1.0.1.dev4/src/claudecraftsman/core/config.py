"""
Configuration management for ClaudeCraftsman.

Handles development mode detection, path resolution, and framework configuration.
"""

from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from rich.console import Console

console = Console()


class FrameworkPaths(BaseModel):
    """Framework path configuration."""

    model_config = ConfigDict(frozen=True)

    claude_dir: Path
    framework_file: Path
    agents_dir: Path
    commands_dir: Path
    docs_dir: Path
    context_dir: Path
    scripts_dir: Path

    @property
    def is_valid(self) -> bool:
        """Check if framework paths exist and are valid."""
        return (
            self.claude_dir.exists()
            and self.framework_file.exists()
            and self.agents_dir.exists()
            and self.commands_dir.exists()
        )


class Config(BaseSettings):
    """
    ClaudeCraftsman configuration with smart mode detection.

    Three modes of operation:
    1. Development Mode: Developing ClaudeCraftsman itself (self-hosting)
    2. User Project Mode: User project with .claude/ directory
    3. Installed Mode: Global commands, no local project
    """

    model_config = SettingsConfigDict(
        env_prefix="CLAUDECRAFTSMAN_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Configuration fields
    debug: bool = Field(default=False, description="Enable debug output")
    verbose: bool = Field(default=False, description="Enable verbose output")

    # Computed properties (not from env)
    _dev_mode: bool | None = None
    _paths: FrameworkPaths | None = None
    _project_root: Path | None = None

    def __init__(self, **data: Any) -> None:
        """Initialize configuration with mode detection."""
        # Filter the data to only include BaseSettings fields
        settings_data = {k: v for k, v in data.items() if k in {"debug", "verbose"}}
        super().__init__(**settings_data)
        self._detect_mode()
        self._setup_paths()

    def _detect_mode(self) -> None:
        """Detect if running in ClaudeCraftsman development mode."""
        self._dev_mode = False
        self._project_root = Path.cwd()

        # Check for .claude directory
        claude_dir = self._project_root / ".claude"
        if not claude_dir.exists():
            return

        # Check for pyproject.toml
        pyproject_path = self._project_root / "pyproject.toml"
        if not pyproject_path.exists():
            return

        # Check if this is ClaudeCraftsman project
        try:
            content = pyproject_path.read_text()
            if 'name = "claudecraftsman"' in content.lower():
                self._dev_mode = True
                if self.verbose:
                    console.print("[green]✓ Development mode detected (self-hosting)[/green]")
        except Exception as e:
            if self.debug:
                console.print(f"[yellow]Warning: Could not read pyproject.toml: {e}[/yellow]")

    def _setup_paths(self) -> None:
        """Set up framework paths based on detected mode."""
        # Ensure _project_root is set
        if self._project_root is None:
            self._project_root = Path.cwd()

        if self._dev_mode:
            # Development mode: use local .claude/
            claude_dir = self._project_root / ".claude"
        elif (self._project_root / ".claude").exists():
            # User project mode: use their .claude/
            claude_dir = self._project_root / ".claude"
        else:
            # Installed mode: use home directory
            claude_dir = Path.home() / ".claude" / "claudecraftsman"

        self._paths = FrameworkPaths(
            claude_dir=claude_dir,
            framework_file=claude_dir / "framework.md",
            agents_dir=claude_dir / "agents",
            commands_dir=claude_dir / "commands",
            docs_dir=claude_dir / "docs",
            context_dir=claude_dir / "context",
            scripts_dir=claude_dir / "scripts",
        )

    @property
    def dev_mode(self) -> bool:
        """Check if running in development mode."""
        return self._dev_mode or False

    @property
    def paths(self) -> FrameworkPaths:
        """Get framework paths."""
        if self._paths is None:
            self._setup_paths()
        assert self._paths is not None
        return self._paths

    @property
    def project_root(self) -> Path:
        """Get project root directory."""
        return self._project_root or Path.cwd()

    def get_user_claude_dir(self) -> Path | None:
        """Get user's .claude directory if in user project mode."""
        if not self.dev_mode and (self.project_root / ".claude").exists():
            return self.project_root / ".claude"
        return None

    def get_framework_source_dir(self) -> Path:
        """Get framework source directory (for installation)."""
        if self.dev_mode:
            # In dev mode, framework source is local .claude/
            return self.paths.claude_dir
        else:
            # Otherwise, look for installed package data
            import claudecraftsman

            package_dir = Path(claudecraftsman.__file__).parent
            framework_data = package_dir / "data" / "framework"
            if framework_data.exists():
                return framework_data
            else:
                # Fallback to home directory
                return Path.home() / ".claude" / "claudecraftsman"

    def ensure_paths_exist(self) -> bool:
        """Ensure all required paths exist."""
        try:
            # Create directories if they don't exist
            for path_attr in ["claude_dir", "docs_dir", "context_dir"]:
                path = getattr(self.paths, path_attr)
                path.mkdir(parents=True, exist_ok=True)

            # Check critical files
            if not self.paths.framework_file.exists() and not self.dev_mode:
                console.print(
                    "[red]Error: Framework not installed. "
                    "Run 'claudecraftsman install' first.[/red]"
                )
                return False

            return True

        except Exception as e:
            console.print(f"[red]Error creating directories: {e}[/red]")
            return False

    def display_status(self) -> None:
        """Display current configuration status."""
        console.print("\n[bold]ClaudeCraftsman Configuration[/bold]")
        console.print(f"Mode: {'Development (self-hosting)' if self.dev_mode else 'Production'}")
        console.print(f"Project Root: {self.project_root}")
        console.print(f"Claude Directory: {self.paths.claude_dir}")
        console.print(f"Framework Valid: {self.paths.is_valid}")

        if self.get_user_claude_dir():
            console.print(f"User Project: {self.get_user_claude_dir()}")

        if self.debug:
            console.print("\n[dim]All Paths:[/dim]")
            for name, value in self.paths.model_dump().items():
                console.print(f"  {name}: {value}")


# Global configuration instance
_config: Config | None = None


def get_config() -> Config:
    """Get or create global configuration instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config


def reset_config() -> None:
    """Reset global configuration (mainly for testing)."""
    global _config
    _config = None
