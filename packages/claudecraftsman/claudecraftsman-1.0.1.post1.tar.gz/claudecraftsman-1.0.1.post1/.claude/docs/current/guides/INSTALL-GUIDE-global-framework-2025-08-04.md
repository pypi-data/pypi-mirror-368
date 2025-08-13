# ClaudeCraftsman Global Installation Guide
*Complete guide for installing the ClaudeCraftsman framework globally*

**Document**: INSTALL-GUIDE-global-framework-2025-08-04.md
**Created**: 2025-08-04
**Last Updated**: 2025-08-04 05:54 UTC
**Version**: 1.0
**Purpose**: Global framework installation instructions

## Installation Architecture

### Global Framework Structure
```
~/.claude/claudecraftsman/           # Global framework installation
├── framework.md                     # Core craftsman principles
├── agents/                          # Agent definitions
│   ├── product-architect.md         # Business requirements craftsperson
│   ├── design-architect.md          # Technical specifications artisan
│   ├── workflow-coordinator.md      # Multi-agent orchestration
│   ├── system-architect.md          # Implementation architecture (Phase 2)
│   ├── backend-architect.md         # TDD-focused backend (Phase 2)
│   └── frontend-developer.md        # Component craftsperson (Phase 2)
├── commands/                        # Command definitions
│   ├── design.md                    # Design-first development
│   ├── workflow.md                  # Multi-agent coordination
│   ├── init-craftsman.md            # Project bootstrap
│   ├── implement.md                 # Implementation with design integration (Phase 2)
│   ├── troubleshoot.md              # Systematic analysis (Phase 2)
│   └── test.md                      # Comprehensive testing (Phase 2)
├── templates/                       # Reusable templates
│   ├── PRD-template.md
│   ├── tech-spec-template.md
│   └── handoff-brief-template.md
├── standards/                       # Quality standards
│   ├── research-citation-standards.md
│   ├── file-organization-standards.md
│   └── quality-gate-checklist.md
└── INSTALLATION.md                  # Installation metadata
```

### Project Structure (After Framework Activation)
```
PROJECT_ROOT/
├── CLAUDE.md                        # Framework imports (only framework activation)
└── .claude/                         # Project-specific runtime files
    ├── docs/                        # Project documentation (runtime)
    │   ├── current/                 # Active specifications
    │   └── archive/                 # Superseded versions
    ├── context/                     # Runtime context files
    │   ├── WORKFLOW-STATE.md
    │   ├── HANDOFF-LOG.md
    │   └── CONTEXT.md
    ├── specs/                       # Technical specifications
    └── project-mgt/                 # Project management (optional, for framework development)
```

## Installation Process

### Step 1: Global Framework Installation

**Python Package Installation (Recommended)**:
```bash
# Install with UV (recommended)
uv add claudecraftsman

# Or install with pip
pip install claudecraftsman

# Run directly without installation
uvx --from claudecraftsman cc --help

# Verify installation
claudecraftsman --version
# or use short alias
cc --version
```

**Development Installation**:
```bash
# Clone for development
git clone https://github.com/your-org/claudecraftsman.git
cd claudecraftsman

# Install with development dependencies
uv sync --all-extras

# Run in development mode
uv run claudecraftsman --help
```

### Step 2: Project Activation

**Option A: New Project Bootstrap**
```bash
# In new project directory
claudecraftsman init --name my-project --type web --framework react
# or use short alias
cc init --name my-project --type web --framework react
```

**Option B: Existing Project Activation**
```bash
# Add to existing project's CLAUDE.md
echo "# ClaudeCraftsman Framework" >> CLAUDE.md
echo "@~/.claude/claudecraftsman/framework.md" >> CLAUDE.md
echo "@~/.claude/claudecraftsman/agents/product-architect.md" >> CLAUDE.md
echo "@~/.claude/claudecraftsman/commands/design.md" >> CLAUDE.md
```

## Framework Activation Pattern

### Project CLAUDE.md (After Global Install)
```markdown
# ClaudeCraftsman Framework
*Artisanal development with intention and care*

## Framework Activation
@~/.claude/claudecraftsman/framework.md

## Core Craftspeople
@~/.claude/claudecraftsman/agents/product-architect.md
@~/.claude/claudecraftsman/agents/design-architect.md
@~/.claude/claudecraftsman/agents/workflow-coordinator.md

## Essential Commands
@~/.claude/claudecraftsman/commands/design.md
@~/.claude/claudecraftsman/commands/workflow.md
@~/.claude/claudecraftsman/commands/init-craftsman.md

## Project Configuration
- **Project**: [Project Name]
- **Framework Version**: ClaudeCraftsman v1.0
- **Standards**: Research-driven specifications, time-aware documentation
- **Quality Gates**: Phase-based completion with craftsman approval
```

## Verification

### Installation Verification
```bash
# Check Python package installation
claudecraftsman --version
cc --version

# Check available commands
claudecraftsman --help
cc --help

# Run status check
claudecraftsman status
cc status
```

### Project Activation Verification
```bash
# In project directory
cat CLAUDE.md | grep claudecraftsman

# Verify project structure created
ls -la .claude/
ls -la .claude/context/
```

## Benefits of Global Installation

### Framework Management
- **Single Installation**: Framework installed once, used across all projects
- **Easy Updates**: Update framework globally, all projects benefit
- **Version Control**: Clear framework versioning and upgrade paths
- **Clean Separation**: Framework code separate from project code

### Project Benefits
- **Clean Projects**: No framework files cluttering project directories
- **Consistent Standards**: All projects use same framework version and standards
- **Easy Setup**: New projects activate framework with simple imports
- **Portable**: Projects remain portable while leveraging global framework

### Development Benefits
- **Centralized Maintenance**: Framework improvements benefit all projects
- **Standard Updates**: Push standards updates to all framework users
- **Community**: Shared framework enables community improvements
- **Quality**: Consistent quality standards across all projects

## Migration from Local Installation

### Current State Analysis
If you currently have framework files in your project directory:
```
PROJECT/.claude/claudecraftsman/    # Local installation (to be removed)
PROJECT/CLAUDE.md                   # Imports from local paths (to be updated)
```

### Migration Steps
1. **Install framework globally** using installation script
2. **Update CLAUDE.md imports** to use global paths
3. **Remove local framework files** from project directory
4. **Test framework activation** in new Claude Code session
5. **Clean up project structure** to match target architecture

### Python Package Migration
```bash
# ClaudeCraftsman is now a Python package
# No migration script needed - just install the package
uv add claudecraftsman

# Update CLAUDE.md to remove old framework imports
# Add Python package references instead
```

## Troubleshooting

### Common Issues

**Framework not found**:
- Verify global installation: `ls ~/.claude/claudecraftsman/`
- Check CLAUDE.md import paths are correct
- Ensure Claude Code can access ~/.claude/ directory

**Imports not working**:
- Verify file paths in CLAUDE.md exactly match global installation
- Check for typos in import statements
- Test imports individually

**Framework not activating**:
- Start new Claude Code session after CLAUDE.md changes
- Verify CLAUDE.md is in project root directory
- Check Claude Code memory system is functioning

### Support
- Framework documentation: `.claude/claudecraftsman/`
- Installation verification checklist included
- Community resources and troubleshooting guides

---

**Installation Guide Maintainer**: ClaudeCraftsman Framework Team
**Next Review**: Framework v1.1 release
**Support**: Framework documentation and community resources

*"A properly installed framework serves as the foundation upon which all craftspeople build. Install once, craft everywhere."*
