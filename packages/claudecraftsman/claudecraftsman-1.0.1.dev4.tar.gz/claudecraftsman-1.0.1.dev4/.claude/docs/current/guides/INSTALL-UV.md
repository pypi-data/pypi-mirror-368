# Installing ClaudeCraftsman with UV/UVX
*Modern Python package installation for the artisanal framework*

## Prerequisites

### 1. Install UV (if not already installed)

UV is a fast, modern Python package manager. Install it with:

```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

After installation, restart your terminal or run:
```bash
source ~/.bashrc  # or ~/.zshrc on macOS
```

### 2. Verify UV Installation

```bash
uv --version
# Should show: uv 0.1.x or higher
```

## Installation Methods

### Method 1: Quick Install with UVX (Recommended)

UVX allows you to run Python applications without explicit installation:

```bash
# Install ClaudeCraftsman globally
uvx claudecraftsman install

# Or run any command directly
uvx claudecraftsman status
uvx claudecraftsman --help
```

### Method 2: Install in Virtual Environment

For development or isolated installation:

```bash
# Create a new virtual environment
uv venv

# Activate it
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install ClaudeCraftsman
uv pip install claudecraftsman

# Verify installation
claudecraftsman --version
```

### Method 3: Install from Source (Development)

For contributing or customization:

```bash
# Clone the repository
git clone https://github.com/yourusername/claudecraftsman.git
cd claudecraftsman

# Create virtual environment
uv venv
source .venv/bin/activate

# Install in development mode
uv pip install -e .

# Run tests
uv run pytest
```

## Post-Installation Setup

### 1. Initialize ClaudeCraftsman

After installation, initialize the framework:

```bash
# Run the installation command
claudecraftsman install

# This will:
# - Create ~/.claude/claudecraftsman/ directory
# - Copy framework files (agents, commands, templates)
# - Set up initial configuration
# - Verify installation integrity
```

### 2. Verify Installation

```bash
# Check status
claudecraftsman status

# Should show:
# ✅ ClaudeCraftsman v1.0.0
# ✅ Framework directory: ~/.claude/claudecraftsman/
# ✅ Configuration valid
# ✅ All quality gates passed
```

### 3. Configure Claude Code Hooks (Optional)

To integrate with Claude Code IDE:

```bash
# Generate hooks configuration
claudecraftsman hook generate > hooks.json

# This creates a hooks.json file for Claude Code integration
# Copy this file to your project root or configure in Claude Code settings
```

## Usage Examples

### Starting a New Project

```bash
# Create a new project with ClaudeCraftsman
mkdir my-project
cd my-project

# Initialize ClaudeCraftsman
claudecraftsman init --name "My Project" --type web

# This creates:
# - .claude/ directory structure
# - CLAUDE.md configuration
# - Initial project files
```

### Common Commands

```bash
# Framework commands
claudecraftsman status              # Check framework health
claudecraftsman validate quality    # Run quality gates
claudecraftsman archive check       # Check for archiveable documents

# State management
claudecraftsman state document-created "PRD-feature.md" "PRD" "docs/" "Feature PRD"
claudecraftsman state phase-started "implementation" "backend-architect"
claudecraftsman state workflow-update "design-to-deploy" "active"

# Registry management
claudecraftsman registry sync       # Sync document registry
claudecraftsman registry validate   # Validate registry integrity
```

## Migrating from Shell Scripts

If you have the previous shell-based installation:

```bash
# Run migration script
./scripts/migrate-to-python.sh

# Or manually:
# 1. Backup existing installation
cp -r ~/.claude/claudecraftsman ~/.claude/claudecraftsman-backup

# 2. Install Python package
uvx claudecraftsman install

# 3. Your project files in .claude/docs/, .claude/context/ are preserved
```

## Troubleshooting

### UV Not Found

If `uv` command is not found after installation:
- Ensure `~/.cargo/bin` is in your PATH
- Restart your terminal
- Run: `source ~/.bashrc` or `source ~/.zshrc`

### Permission Denied

If you get permission errors:
```bash
# Install in user space (recommended)
uv pip install --user claudecraftsman

# Or use sudo (not recommended)
sudo uv pip install claudecraftsman
```

### Import Errors

If you get import errors when running:
- Ensure you're in the correct virtual environment
- Check Python version: `python --version` (requires 3.9+)
- Reinstall: `uv pip install --force-reinstall claudecraftsman`

### Claude Code Hooks Not Working

If hooks don't trigger in Claude Code:
1. Verify hooks.json is in your project root
2. Check Claude Code console for errors
3. Ensure hook handlers have correct paths
4. Test with: `claudecraftsman hook test`

## Platform-Specific Notes

### macOS
- UV installs to `~/.cargo/bin/uv`
- May need to allow in Security & Privacy settings
- Use `~/.zshrc` for shell configuration

### Windows
- UV installs to `%USERPROFILE%\.cargo\bin\uv.exe`
- Add to PATH if not automatic
- Use PowerShell or Windows Terminal for best experience

### Linux
- UV installs to `~/.cargo/bin/uv`
- Works with all major distributions
- May need to install `python3-venv` package

## Advanced Configuration

### Development Mode

ClaudeCraftsman detects development mode automatically:
- If `.claude/` exists AND `pyproject.toml` contains `name = "claudecraftsman"`
- Uses local `.claude/` instead of global installation
- Allows testing changes immediately

### Environment Variables

```bash
# Override default locations
export CLAUDECRAFTSMAN_HOME=~/.claude/claudecraftsman
export CLAUDECRAFTSMAN_CONFIG=~/.config/claudecraftsman

# Enable debug logging
export CLAUDECRAFTSMAN_DEBUG=1

# Force development mode
export CLAUDECRAFTSMAN_DEV=1
```

### Configuration File

Create `~/.config/claudecraftsman/config.yaml`:
```yaml
# Framework settings
framework:
  enforce_quality: true
  strict_mode: false
  archive_days: 30

# Hook settings
hooks:
  enabled: true
  auto_validate: true

# Paths (usually auto-detected)
paths:
  framework: ~/.claude/claudecraftsman
  projects: ~/projects
```

## Getting Help

```bash
# Built-in help
claudecraftsman --help
claudecraftsman [command] --help

# Check documentation
claudecraftsman docs

# Report issues
# https://github.com/yourusername/claudecraftsman/issues
```

## Next Steps

1. **Initialize a project**: `claudecraftsman init --name "My Project"`
2. **Explore commands**: `claudecraftsman --help`
3. **Read the framework guide**: In `.claude/claudecraftsman/framework.md`
4. **Join the community**: [Community links]

Welcome to ClaudeCraftsman Python Edition! 🎉
