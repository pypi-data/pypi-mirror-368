# Getting Started with ClaudeCraftsman
*Your journey to artisanal software development begins here*

## Welcome to ClaudeCraftsman

ClaudeCraftsman is a comprehensive framework that elevates software development to an artisanal craft. Every line of code, every design decision, and every implementation reflects the care and intention of a master craftsperson.

## Quick Start (5 Minutes)

### 1. Prerequisites
- Claude Code installed and configured
- Access to a terminal/command line
- A project directory for your new application

### 2. Install ClaudeCraftsman

```bash
# Install with UV (recommended)
uv add claudecraftsman

# Or run directly without installation
uvx --from claudecraftsman cc --help

# Or install with pip
pip install claudecraftsman

# Verify installation
claudecraftsman --version
# or use short alias
cc --version
```

### 3. Initialize Your First Project

```bash
# Navigate to your project directory
cd ~/projects/my-awesome-app

# Initialize ClaudeCraftsman in your project
claudecraftsman init --name my-awesome-app --type web --framework react
# or use short alias
cc init --name my-awesome-app --type web --framework react

# Your project is now ready!
```

### 4. Start with Design

```bash
# For simple features, use plan
/plan user-authentication

# For complex systems, use design
/design e-commerce-platform --research=deep
```

## Core Concepts

### The Craftsman Philosophy

ClaudeCraftsman treats software development as a craft, not just engineering:

- **Intention**: Every decision is made with purpose and care
- **Quality**: No compromises on excellence - every output should make you proud
- **Research**: All claims backed by evidence and current data
- **Empathy**: Software serves people - understand their genuine needs

### Framework Structure

```
your-project/
├── CLAUDE.md              # Framework activation and configuration
└── .claude/               # Framework runtime directory
    ├── agents/            # Specialized AI craftspeople
    ├── commands/          # Development workflow commands
    ├── docs/current/      # Active project documentation
    ├── context/           # Workflow state and handoffs
    └── templates/         # Reusable patterns
```

### Available Craftspeople (Agents)

ClaudeCraftsman provides specialized agents for every aspect of development:

**Planning & Design**
- **product-architect**: Business requirements and user research
- **design-architect**: Technical specifications and system design
- **system-architect**: High-level architecture and integration

**Implementation**
- **backend-architect**: API design and server development
- **frontend-developer**: UI components and user experience
- **data-architect**: Database design and data pipelines
- **ml-architect**: Machine learning systems and AI

**Quality & Operations**
- **qa-architect**: Testing strategies and quality assurance
- **workflow-coordinator**: Multi-agent orchestration
- **security-architect**: Security and compliance (coming soon)
- **devops-architect**: Infrastructure and deployment (coming soon)

### Essential Commands

**Creation & Planning**
- `/add [type] [name]` - Create individual components with excellence
- `/plan [feature]` - Plan medium-complexity features
- `/design [system]` - Comprehensive system design with research

**Implementation & Quality**
- `/implement [plan]` - Execute plans with agent coordination
- `/test [feature]` - Create comprehensive test suites
- `/validate` - Health checks for framework and code
- `/deploy [app]` - Zero-downtime deployment strategies

**Workflow & Help**
- `/workflow [type]` - Orchestrate multi-agent workflows
- `/help` - Command selection guidance

## Your First Project Walkthrough

### Step 1: Design Your Application

```bash
# Start with comprehensive design
/design task-management-app --research=deep

# This will:
# 1. Research current task management solutions
# 2. Create a Product Requirements Document (PRD)
# 3. Generate technical specifications
# 4. Develop implementation plan
```

### Step 2: Implement Core Features

```bash
# Implement the designed features
/implement task-management-app

# The framework will:
# 1. Parse your plan
# 2. Coordinate appropriate agents
# 3. Generate code with quality standards
# 4. Track progress automatically
```

### Step 3: Add Testing

```bash
# Create comprehensive test suite
/test task-management

# Generates:
# - Unit tests with 80%+ coverage
# - Integration tests for APIs
# - E2E tests for user workflows
# - Performance benchmarks
```

### Step 4: Deploy with Confidence

```bash
# Deploy to production
/deploy task-management-app --env=production --strategy=blue-green

# Features:
# - Zero-downtime deployment
# - Automatic rollback on failure
# - Health monitoring
# - Performance validation
```

## Best Practices

### 1. Always Start with Design
- Use `/plan` for features, `/design` for systems
- Let the framework guide architecture decisions
- Research is automated - trust the process

### 2. Leverage Agent Expertise
- Each agent is a specialist - use them accordingly
- Agents collaborate automatically through handoffs
- Context is preserved across all interactions

### 3. Maintain Quality Standards
- Every component follows craftsman templates
- Quality gates ensure excellence
- Framework self-validates with `/validate`

### 4. Document as You Build
- Documentation is generated automatically
- Keep your CLAUDE.md updated
- Use consistent file naming

## Common Workflows

### Feature Development
```bash
/plan user-notifications
/implement user-notifications
/test user-notifications
/deploy user-notifications --env=staging
```

### Bug Fixing
```bash
/troubleshoot payment-processing
/implement payment-fix --from-file=troubleshoot-results.md
/test payment-processing --type=integration
/deploy payment-service --strategy=canary
```

### Performance Optimization
```bash
/analyze api-performance --deep
/plan performance-improvements
/implement performance-improvements
/test api --type=performance
```

## Integration with Existing Projects

### Adding to Existing Codebase
```bash
# Navigate to existing project
cd ~/projects/legacy-app

# Initialize framework
/init-craftsman legacy-app --type=web --preserve-existing

# Start improving
/analyze --scope=project
/plan modernization-phase-1
```

### Gradual Adoption
1. Start with new features using ClaudeCraftsman
2. Gradually refactor existing code
3. Use `/validate` to ensure quality
4. Maintain consistency with existing patterns

## Advanced Features

### Multi-Agent Workflows
```bash
# Complex workflows with coordination
/workflow design-to-deploy my-feature

# Automatic handoffs between:
# product-architect → design-architect → backend/frontend → qa → deployment
```

### Custom Templates
```bash
# Add custom templates for your team
/add template api-endpoint-template
/add template react-component-template
```

### Framework Extension
```bash
# Add domain-specific agents
/add agent security-architect
/add agent mobile-architect
```

## Troubleshooting Quick Fixes

### Framework Not Responding
```bash
/validate --fix
```

### Slow Performance
```bash
/validate --component=mcp --deep
```

### Context Lost Between Sessions
Check `.claude/context/SESSION-MEMORY.md` is being updated

### Commands Not Found
Ensure you have ClaudeCraftsman installed:
```bash
# Check installation
claudecraftsman --version

# Or reinstall
uv add claudecraftsman
```

For project integration, ensure CLAUDE.md has proper references.

## Next Steps

1. **Explore Commands**: Run `/help` for detailed command guide
2. **Read Best Practices**: See `best-practices.md` for patterns
3. **Check Examples**: Browse `examples/` directory
4. **Join Community**: Share your craftsman creations

## Getting Help

- **Documentation**: Full docs in `.claude/docs/`
- **Troubleshooting**: See `troubleshooting.md`
- **Community**: GitHub discussions and issues
- **Framework Health**: Run `/validate` anytime

---

Welcome to the ClaudeCraftsman community. May your code be as thoughtful as it is functional, and may every project reflect the pride of true craftsmanship.

*"Code is poetry, architecture is art, and software is craft."*
