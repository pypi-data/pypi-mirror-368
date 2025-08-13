"""
Tests for core configuration module.
"""

from claudecraftsman.core.config import Config, get_config


class TestConfig:
    """Test configuration detection and paths."""

    def test_dev_mode_detection(self, tmp_path):
        """Test development mode detection."""
        # Create project structure
        (tmp_path / ".claude").mkdir()
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('name = "claudecraftsman"')

        # Change to tmp directory
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            config = Config()
            assert config.dev_mode is True
        finally:
            os.chdir(original_cwd)

    def test_user_mode_detection(self, tmp_path):
        """Test user project mode detection."""
        # Create user project with .claude
        (tmp_path / ".claude").mkdir()
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('name = "myproject"')

        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            config = Config()
            assert config.dev_mode is False
            assert config.paths.claude_dir == tmp_path / ".claude"
        finally:
            os.chdir(original_cwd)

    def test_installed_mode_detection(self, tmp_path):
        """Test installed mode detection."""
        # Create project without .claude
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('name = "myproject"')

        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            config = Config()
            assert config.dev_mode is False
            # When no .claude dir exists, framework files come from installed location
            assert not (tmp_path / ".claude").exists()
        finally:
            os.chdir(original_cwd)

    def test_path_construction(self):
        """Test path construction in different modes."""
        config = get_config()

        # Basic paths should exist
        assert config.project_root.exists()

        # Claude dir paths
        assert config.paths.claude_dir.name == ".claude"
        assert config.paths.docs_dir.name == "docs"
        assert config.paths.context_dir.name == "context"

        # Framework paths
        if config.dev_mode:
            assert config.paths.framework_file.name == "framework.md"
            assert config.paths.agents_dir.name == "agents"
            assert config.paths.commands_dir.name == "commands"
