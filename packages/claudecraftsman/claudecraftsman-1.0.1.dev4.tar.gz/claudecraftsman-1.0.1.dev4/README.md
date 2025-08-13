# ClaudeCraftsman 🛠️

[![CI](https://github.com/darth-veitcher/claude-craftsman/actions/workflows/ci.yml/badge.svg)](https://github.com/darth-veitcher/claude-craftsman/actions/workflows/ci.yml)
[![Publish to TestPyPI](https://github.com/darth-veitcher/claude-craftsman/actions/workflows/publish-test.yml/badge.svg)](https://github.com/darth-veitcher/claude-craftsman/actions/workflows/publish-test.yml)
[![PyPI version](https://badge.fury.io/py/claudecraftsman.svg)](https://badge.fury.io/py/claudecraftsman)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![UV Compatible](https://img.shields.io/badge/uv-compatible-green.svg)](https://github.com/astral-sh/uv)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Framework: Craftsman](https://img.shields.io/badge/framework-craftsman-purple.svg)]()

**Artisanal development framework for Claude Code - where every line of code is crafted with intention.**

## Table of Contents
- [5-Minute Quickstart](#5-minute-quickstart)
- [Documentation](#documentation)
- [How It Works](#how-it-works)
- [Installation](#installation-methods)
- [Core Commands](#core-commands)
- [Features](#features)
- [Framework Philosophy](#framework-philosophy)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## Overview

ClaudeCraftsman transforms your development workflow with craftsman-quality standards, thoughtful automation, and seamless Claude Code integration. Every line of code crafted with intention, every decision made with care.

## 5-Minute Quickstart

### Prerequisites
- Python 3.9+
- Claude Code installed
- UV (recommended) or pip

### Install & Initialize

```bash
# 1. Install ClaudeCraftsman globally (30 seconds)
# Option A: Run without installation (recommended)
uvx --from claudecraftsman cc --version

# Option B: Install as global tool
uv tool install claudecraftsman
# Or: pip install --user claudecraftsman

# 2. Initialize your project (30 seconds)
cd your-project
uvx --from claudecraftsman cc init --name my-app --type web
# Or if installed globally: cc init --name my-app --type web

# This creates:
# - .claude/ directory with framework files
# - CLAUDE.md that activates the framework
# - All agents, commands, and templates locally

# 3. Start building with craftsman quality! (4 minutes)
# In Claude Code, use framework commands:
/design user-authentication    # For comprehensive planning
/add agent custom-backend      # For single components
/help                         # For guidance
```

That's it! You're now using ClaudeCraftsman. The framework provides:
- 🎯 **Craftsman-quality components** - Every output is production-ready
- 🔧 **Intelligent automation** - MCP tools integration for research & validation
- 📚 **Living documentation** - Self-updating, time-aware docs
- 🤝 **Multi-agent coordination** - Specialized AI craftspeople working together

## Documentation

### 📚 Essential Guides
- **[Quick Start Guide](.claude/docs/current/QUICKSTART.md)** - Get productive in 5 minutes
- **[Workflow Examples](.claude/docs/current/WORKFLOW-EXAMPLES.md)** - Real-world development patterns
- **[Troubleshooting Guide](.claude/docs/current/TROUBLESHOOTING.md)** - Solutions for common issues
- **[FAQ](.claude/docs/current/FAQ.md)** - Frequently asked questions

### 🛠️ Command Documentation
- **[Command Overview](.claude/commands/help.md)** - Complete command reference
- **[Design Command](.claude/commands/design.md)** - System design with market research
- **[Plan Command](.claude/commands/plan.md)** - Feature planning and coordination
- **[Implement Command](.claude/commands/implement.md)** - Execute plans with progress tracking
- **[Test Command](.claude/commands/test.md)** - BDD/TDD testing workflows

### 🤖 Agent Documentation
- **[Agent Overview](.claude/agents/)** - All available craftsman agents
- **[Product Architect](.claude/agents/framework/product-architect.md)** - PRDs and requirements
- **[Design Architect](.claude/agents/framework/design-architect.md)** - Technical specifications
- **[QA Architect](.claude/agents/framework/qa-architect.md)** - Testing strategies

### What's New in v1.0 🎉
- **Self-Managing Framework**: Automatic health monitoring and violation correction
- **Document Lifecycle**: Automatic archival of completed documents
- **Enhanced CLI**: New `cc health` and `cc archive` commands
- **10+ Specialized Agents**: Including security, performance, and data architects
- **Pure Python**: No more shell scripts - everything is Python now
- **MCP Tool Integration**: Research-driven development with real citations
- **Progress Tracking**: Real-time visibility into implementation progress
- **BDD/TDD Support**: Comprehensive testing with Playwright integration

## How It Works

1. **Python Package Installation**: ClaudeCraftsman installs as a CLI tool (globally or via uvx)
2. **Project Initialization**: `cc init` extracts framework files to your project's `.claude/` directory
3. **Claude Code Integration**: CLAUDE.md imports local `.claude/` files, activating the framework
4. **Framework Commands**: Once activated, use `/design`, `/add`, etc. in Claude Code sessions

The key insight: The Python package **delivers** the framework files to your project, where Claude Code can access them.

## Installation Methods

### Understanding Installation Locations
- **`uvx`**: Runs without installation, temporary isolated environment
- **`uv tool install`**: Installs globally to `~/.local/share/uv/tools/`
- **`pip install --user`**: Installs globally to `~/.local/`
- **`uv add`**: Installs to current project's `.venv/` only

### Quick Install (Recommended)
```bash
# Option 1: Run without installation (recommended for global use)
uvx --from claudecraftsman cc --help

# Option 2: Install as global CLI tool
uv tool install claudecraftsman

# Option 3: Install with pip globally
pip install --user claudecraftsman

# Option 4: Add to current project only
uv add claudecraftsman  # Only available in this project
```

### Development Installation
```bash
# Clone for development
git clone https://github.com/your-org/claudecraftsman.git
cd claudecraftsman

# Install with development dependencies
uv sync --all-extras

# Run tests
uv run pytest
```

## Core Commands

### CLI Commands (Python)
```bash
cc init         # Initialize project with craftsman framework
cc status       # Check framework status and configuration
cc health       # Monitor framework health and compliance
cc archive      # Manage document archival lifecycle
cc state        # View/update project state and workflow
cc registry     # Manage document registry
cc quality      # Run quality gates validation
cc validate     # Run pre-operation validation checks
cc hook         # Configure Claude Code integration hooks
cc migrate      # Migrate from older framework versions
```

### Claude Code Commands (In-Session)
```bash
/design [system]        # Comprehensive system design with research
/plan [feature]         # Feature planning and coordination
/add [type] [name]      # Create craftsman-quality components
/implement [feature]    # Execute plans with multi-agent coordination
/test [component]       # Comprehensive testing strategies
/help                   # Command selection guidance
```

## Framework Philosophy

**The Craftsman's Creed:**
- **Intention over Speed**: Every decision thoughtfully considered
- **Quality over Quantity**: Better to build one thing excellently
- **Research over Assumptions**: Evidence-based development
- **User Value over Features**: Build what genuinely helps people

## Project Structure

### Framework Package
```
claudecraftsman/
├── cli/                      # Command-line interface
│   ├── app.py               # Main CLI application
│   └── commands/            # CLI commands
├── core/                     # Core functionality
│   ├── config.py            # Configuration management
│   ├── state.py             # State management
│   └── validation.py        # Quality gates
├── hooks/                    # Claude Code integration
└── templates/                # Framework templates
```

### Your Project Structure
```
YOUR_PROJECT/
├── CLAUDE.md                 # Framework activation
└── .claude/                  # Runtime directory
    ├── docs/current/         # Active documentation
    ├── context/              # Workflow state
    └── templates/            # Project templates
```

## Features

### 🎨 Craftsman-Quality Components
Every component created follows production-ready standards:
- Comprehensive error handling
- Full MCP tool integration
- Research-backed decisions
- Time-aware documentation
- Quality gates validation

### 🤖 Specialized AI Craftspeople
- **product-architect**: Business requirements and user research
- **design-architect**: Technical specifications and system design
- **system-architect**: High-level architecture with ultrathink methodology
- **backend-architect**: TDD-focused API development
- **frontend-developer**: Component-driven UI development
- **workflow-coordinator**: Multi-agent orchestration
- **qa-architect**: Testing strategies and quality assurance
- **security-architect**: Threat modeling and security analysis
- **performance-architect**: Optimization and scalability
- **data-architect**: Database design and data pipelines

### 🔧 Modern Python Tooling
- UV package manager support
- Pydantic v2 validation
- Typer CLI framework
- Rich terminal output
- Async-first design

### 🔗 Claude Code Integration
- Hook system for tool validation
- Command routing and enhancement
- Session state management
- Quality gates enforcement
- Automatic context preservation

### 🏥 Self-Managing Framework
- **Health Monitoring**: Real-time compliance tracking
- **Auto-Correction**: Fixes common violations automatically
- **Document Lifecycle**: Automatic archival of completed work
- **State Management**: Self-healing state consistency
- **Continuous Validation**: Background enforcement every 5 minutes

## Configuration

### Environment Variables
```bash
export CLAUDE_DEBUG=true              # Enable debug logging
export CLAUDE_UPDATE_CHECK=weekly     # Update check frequency
```

### Project Configuration
In your `CLAUDE.md`:
```markdown
## Framework Configuration
- **Standards**: Craftsman quality only
- **Research**: Always current with MCP tools
- **Testing**: Minimum 80% coverage
- **Documentation**: Comprehensive and current
```

## Updating

```bash
# Update global tool installation
uv tool install --upgrade claudecraftsman
# Or: pip install --user --upgrade claudecraftsman

# Update project-local installation
uv add --upgrade claudecraftsman

# Check current version
cc --version
```

## Development

This project uses itself (self-hosting) for development:

```bash
# The framework being developed
.claude/              # Framework files used for self-development
src/claudecraftsman/  # Python package source
tests/               # Test suite

# Running in development mode
uv run claudecraftsman --help
```

## Troubleshooting

### Quick Solutions

For comprehensive troubleshooting, see our **[Troubleshooting Guide](.claude/docs/current/TROUBLESHOOTING.md)**.

**Common Issues:**
```bash
# Verify installation
cc --version

# Check framework health
cc health check --auto-correct

# MCP tools not working?
# Ensure MCP servers are enabled in Claude Code

# Implementation stuck?
/implement [plan] --status
/implement [plan] --resume
```

**Need Help?**
- Check the [FAQ](.claude/docs/current/FAQ.md)
- Read the [Troubleshooting Guide](.claude/docs/current/TROUBLESHOOTING.md)
- Use `/help` in Claude Code for command guidance

## Contributing

We welcome contributions that enhance the craftsman experience:

1. Fork the repository
2. Create a feature branch
3. Follow craftsman standards
4. Add tests for new features
5. Submit a pull request

## Support

- **Documentation**: See `.claude/docs/` in your project
- **Issues**: GitHub issue tracker
- **Discussions**: GitHub discussions
- **Community**: Share your craftsman creations

## License

MIT License - See LICENSE file for details

---

*Welcome to ClaudeCraftsman. May your code be as thoughtful as it is functional.*
