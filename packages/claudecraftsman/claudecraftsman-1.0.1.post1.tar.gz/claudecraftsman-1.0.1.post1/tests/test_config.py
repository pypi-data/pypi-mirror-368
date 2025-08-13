"""
Tests for ClaudeCraftsman configuration module.
"""

from pathlib import Path

from claudecraftsman.core.config import get_config, reset_config


def test_config_development_mode(tmp_path: Path):
    """Test development mode detection."""
    # Create a project structure that looks like ClaudeCraftsman development
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[project]\nname = "claudecraftsman"\nversion = "1.0.0"')

    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()

    # Change to test directory
    import os

    original_cwd = Path.cwd()
    try:
        os.chdir(tmp_path)
        reset_config()  # Clear any cached config

        config = get_config()
        assert config.dev_mode is True
        assert config.paths.claude_dir == claude_dir

    finally:
        os.chdir(original_cwd)
        reset_config()


def test_config_user_mode(tmp_path: Path):
    """Test user project mode detection."""
    # Create a user project with .claude directory
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()

    # Create a different project
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[project]\nname = "myproject"\nversion = "1.0.0"')

    import os

    original_cwd = Path.cwd()
    try:
        os.chdir(tmp_path)
        reset_config()

        config = get_config()
        assert config.dev_mode is False
        assert config.paths.claude_dir == claude_dir

    finally:
        os.chdir(original_cwd)
        reset_config()


def test_config_installed_mode(tmp_path: Path):
    """Test installed mode (no .claude directory)."""
    import os

    original_cwd = Path.cwd()
    try:
        os.chdir(tmp_path)
        reset_config()

        config = get_config()
        assert config.dev_mode is False
        assert ".claude/claudecraftsman" in str(config.paths.claude_dir)

    finally:
        os.chdir(original_cwd)
        reset_config()
