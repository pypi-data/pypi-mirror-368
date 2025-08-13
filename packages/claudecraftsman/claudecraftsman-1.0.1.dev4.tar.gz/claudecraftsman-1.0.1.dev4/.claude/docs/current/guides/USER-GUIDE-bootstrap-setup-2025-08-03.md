# ClaudeCraftsman Bootstrap User Guide
*Complete guide for framework activation and project initialization*

**Document Type**: User Guide
**Created**: 2025-08-03
**Last Updated**: 2025-08-03 23:19 UTC
**Version**: 1.0
**Audience**: ClaudeCraftsman Users

## Architecture

### Global Framework Installation
```
~/.claude/claudecraftsman/          # Global framework installation
├── framework.md                    # Core craftsman principles
├── agents/                         # Agent definitions
│   ├── product-architect.md        # PRD creation craftsperson
│   ├── design-architect.md         # Technical specifications artisan
│   └── workflow-coordinator.md     # Multi-agent orchestration
├── commands/                       # Command definitions
│   ├── design.md                   # Design-first development
│   ├── workflow.md                 # Multi-agent coordination
│   └── init-craftsman.md           # Project bootstrap
└── INSTALLATION.md                 # Installation record
```

### Project Activation via CLAUDE.md
```markdown
# ClaudeCraftsman Framework
@~/.claude/claudecraftsman/framework.md

# Project Configuration
- **Project**: [Project Name]
- **Framework**: ClaudeCraftsman v1.0
- **Standards**: Artisanal development with research-driven specifications

# Available Craftspeople
@~/.claude/claudecraftsman/agents/product-architect.md
@~/.claude/claudecraftsman/agents/design-architect.md
@~/.claude/claudecraftsman/agents/workflow-coordinator.md

# Available Commands
@~/.claude/claudecraftsman/commands/design.md
@~/.claude/claudecraftsman/commands/workflow.md
@~/.claude/claudecraftsman/commands/init-craftsman.md
```

## Installation Process

### Step 1: Framework Installation
```bash
# Install with UV (recommended)
uv add claudecraftsman

# Or run directly without installation
uvx --from claudecraftsman cc --help

# Or install with pip
pip install claudecraftsman

# Verify installation
claudecraftsman --version
cc --version
```

ClaudeCraftsman is now a Python package that provides CLI commands for framework operations.

### Step 2: Project Activation

#### Option A: Manual Activation (Existing Projects)
Add to your project's `CLAUDE.md`:
```markdown
# ClaudeCraftsman Framework
@~/.claude/claudecraftsman/framework.md
```

#### Option B: Bootstrap New Project
```bash
# In your project directory
claudecraftsman init --name [project-name]
# or use short alias
cc init --name [project-name]
```

This creates the complete project structure and CLAUDE.md configuration.

## Bootstrap Benefits

### 1. Opt-In Activation
- Only projects that explicitly import the framework get craftsman mode
- Existing Claude Code projects remain unaffected
- Clean activation without global behavior changes

### 2. Native Claude Code Integration
- Uses built-in memory import system (`@path/to/file`)
- No external dependencies or custom tooling required
- Automatic context loading on session start

### 3. Persistent Framework Awareness
- Framework loaded into context every session
- Craftsman standards automatically enforced
- Agent definitions available for sub-agent calls

### 4. Clean Project Organization
- Structured `.claude/` directory prevents documentation sprawl
- Consistent naming conventions across all projects
- Context management for multi-agent workflows

## Framework Components

### Core Framework (framework.md)
- Craftsman philosophy and principles
- Mandatory process requirements (time awareness, research-driven, citations)
- Quality gates and standards
- Context management protocols

### Agents Directory
- **product-architect**: Business requirements and PRD creation
- **design-architect**: Technical specifications and system design
- **workflow-coordinator**: Multi-agent orchestration and handoffs

### Commands Directory
- **design**: Comprehensive design-first development process
- **workflow**: Multi-agent workflow coordination
- **init-craftsman**: Project bootstrap and framework activation

## Usage Patterns

### Design-First Development
```bash
# Start with comprehensive planning
/design user-authentication

# This orchestrates:
# 1. product-architect → PRD with research and user stories
# 2. design-architect → Technical specification
# 3. technical-planner → Implementation plan
```

### Multi-Agent Workflows
```bash
# Complex feature development
/workflow design-to-deploy payment-processing

# This coordinates multiple craftspeople through:
# Planning → Architecture → Implementation → Testing → Documentation
```

### Project Bootstrap
```bash
# Initialize new project with framework
claudecraftsman init --name ecommerce-platform --type web --framework react
# or use short alias
cc init --name ecommerce-platform --type web --framework react
```

## Quality Enforcement

### Automatic Standards
- All agents use `time` MCP tool for current timestamps
- Research requirements enforced through MCP tool integration
- Citation standards mandatory for all claims
- File organization standards automatically applied

### Context Preservation
- Workflow state tracking across sessions
- Agent handoff protocols maintain context
- Quality gates prevent progression until standards met

## Migration from SuperClaude

### Workflow Preservation
- Sequential thinking (`--seq`) → "ultrathink" mode in agents
- Iteration patterns (`--iterate`) → Quality gates and refinement cycles
- BDD/TDD workflows → Integrated into agent processes
- Specialized personas → Dedicated craftsman agents

### Command Migration
- `/sc:workflow` → `/workflow` with enhanced coordination
- `/sc:implement` → `/implement` with design integration
- `/sc:troubleshoot` → `/troubleshoot` with systematic analysis
- `/sc:test` → `/test` with comprehensive coverage
- `/sc:document` → Built into all agent processes

## Framework Philosophy

### Artisanal Development
Every aspect of the framework embodies the craftsman philosophy:
- **Intention**: Every decision made with purpose and care
- **Quality**: Standards that would make a craftsperson proud
- **Research**: Evidence-based decisions with proper citations
- **User Focus**: Genuine empathy for human needs
- **Sustainability**: Building for long-term maintenance and growth

### Time Awareness
- All work uses current date/time from MCP tools
- No hardcoded timestamps or outdated references
- Current market research and technology context
- Documentation reflects actual development timeline

### Research-Driven
- Claims backed by verifiable sources
- Market analysis using current data
- Technical decisions validated through authoritative sources
- Competitive analysis reflecting current landscape

## Success Metrics

### Technical Success
- Framework loads successfully via CLAUDE.md imports
- Agents coordinate seamlessly through handoff protocols
- Context preserved across session boundaries
- Quality gates enforced throughout development process

### User Success
- Setup time < 30 minutes for experienced developers
- Clear migration path from existing workflows
- Improved development quality and sustainability
- Enhanced collaboration through structured handoffs

## Troubleshooting

### Common Issues
- **Import failures**: Verify framework installation path
- **Agent coordination**: Check context file permissions
- **Quality gate failures**: Review craftsman standards compliance
- **Research tool access**: Ensure MCP tools available

### Support
- Documentation in `.claude/claudecraftsman/`
- Example projects and templates
- Clear error messages with resolution steps
- Community resources and best practices

---

**The Bootstrap Craftsman's Commitment:**
This framework transforms development from task execution to purposeful creation. Every project initialized with ClaudeCraftsman begins a journey toward software that reflects the care, intention, and pride of true craftsmanship.
