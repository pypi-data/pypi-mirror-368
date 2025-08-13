# ClaudeCraftsman Command Reference
*Complete guide to framework commands*

## Overview

ClaudeCraftsman commands orchestrate your development workflow with craftsman precision. Each command represents a specific phase of software development, from initial planning to production deployment.

## Command Categories

### 🎯 Planning & Design
- [/help](#help) - Command selection guidance
- [/add](#add) - Create framework components
- [/plan](#plan) - Medium-complexity feature planning
- [/design](#design) - Comprehensive system design

### 🚀 Implementation & Development
- [/implement](#implement) - Execute plans with agent coordination
- [/workflow](#workflow) - Multi-agent workflow orchestration
- [/init-craftsman](#init-craftsman) - Bootstrap framework in projects

### ✅ Quality & Deployment
- [/test](#test) - Comprehensive testing workflows
- [/validate](#validate) - Framework health checks
- [/deploy](#deploy) - Production deployment management

---

## Planning & Design Commands

### /help

**Purpose**: Command selection guide that helps you choose the right command for your task.

**Usage**:
```bash
/help
```

**What it provides**:
- Decision tree for command selection
- Command comparison matrix
- Scope guidance (component vs feature vs system)
- Common misconceptions clarification
- Integration patterns between commands

**Example Scenarios**:
- "Which command should I use for creating a new agent?"
- "I need to build a complex system - where do I start?"
- "What's the difference between /add, /plan, and /design?"

---

### /add

**Purpose**: Create individual framework components with uncompromising craftsman quality.

**Usage**:
```bash
/add [type] [name]
```

**Types**:
- `agent` - Specialized AI craftspeople
- `command` - Framework workflow commands
- `template` - Reusable templates

**What you get**:
- Complete craftsman-quality component
- Full MCP tool integration (where applicable)
- Framework standards compliance
- Quality gates and process documentation
- Ready for immediate use

**Examples**:
```bash
# Create a new agent
/add agent security-architect

# Create a new command
/add command analyze

# Create a new template
/add template api-endpoint-template
```

**Quality Standards**:
- Every component follows craftsman template
- Comprehensive documentation included
- Integration points defined
- MCP tools properly integrated
- Git workflows configured

---

### /plan

**Purpose**: Medium-complexity planning for features that need analysis but not full design process.

**Usage**:
```bash
/plan [feature] [--scope=medium] [--quick]
```

**When to use**:
- Multi-step implementations
- Features with dependencies
- Enhancements to existing systems
- Coordination between 2-3 components

**What you get**:
- Planning document with task breakdown
- Implementation phases with dependencies
- Resource requirements identification
- Clear next steps

**Examples**:
```bash
# Plan a new feature
/plan user-notifications

# Quick planning mode
/plan api-optimization --quick

# Medium scope with research
/plan payment-integration --scope=medium
```

**Output**:
- `PLAN-[feature-name]-[YYYY-MM-DD].md` in `.claude/docs/current/plans/`

---

### /design

**Purpose**: Comprehensive design process for complex systems requiring market research and business analysis.

**Usage**:
```bash
/design [system-name] --research=deep --scope=system
```

**When to use**:
- New products or platforms
- Market validation needed
- Complex multi-system architecture
- Business analysis required

**Multi-Agent Process**:
1. **product-architect**: Market research, PRD creation
2. **design-architect**: Technical specifications
3. **technical-planner**: Implementation roadmap

**Examples**:
```bash
# Design a new platform
/design e-commerce-platform --research=deep

# Complex system with integrations
/design enterprise-dashboard --scope=system
```

**Outputs**:
- Product Requirements Document (PRD)
- Technical Specifications
- Implementation Plan
- BDD Scenarios
- Market Research

---

## Implementation & Development Commands

### /implement

**Purpose**: Execute plans with intelligent agent coordination and progress tracking.

**Usage**:
```bash
/implement [plan-file]
/implement [feature] --from-plan
```

**Process**:
1. Parse plan or specification
2. Create task breakdown
3. Coordinate appropriate agents
4. Track progress with TodoWrite
5. Validate quality at each step

**Examples**:
```bash
# Implement from plan file
/implement .claude/docs/current/plans/PLAN-user-auth-2025-08-04.md

# Direct implementation
/implement user-dashboard --from-plan
```

**Features**:
- Automatic agent selection
- Progress tracking
- Quality validation
- Context preservation
- Git integration

---

### /workflow

**Purpose**: Orchestrate complex multi-agent workflows with context preservation.

**Usage**:
```bash
/workflow [workflow-type] [project-name] [--agents=list] [--mode=sequential|parallel]
```

**Workflow Types**:
- `design-to-deploy` - Complete feature lifecycle
- `troubleshoot` - Problem analysis and resolution
- `refactor` - Code improvement workflow
- `feature` - Single feature development
- `integration` - System integration

**Examples**:
```bash
# Complete feature workflow
/workflow design-to-deploy user-authentication

# Troubleshooting workflow
/workflow troubleshoot payment-issues --agents=system-architect,backend-architect

# Parallel implementation
/workflow feature dashboard --mode=parallel
```

**Coordination Features**:
- Automatic handoffs between agents
- Context preservation across phases
- Progress tracking and monitoring
- Quality gates between phases

---

### /init-craftsman

**Purpose**: Bootstrap ClaudeCraftsman framework in new or existing projects.

**Usage**:
```bash
/init-craftsman [project-name] [--type=web|api|mobile|desktop] [--framework=react|vue|express|flask]
```

**What it creates**:
- Complete `.claude/` directory structure
- CLAUDE.md configuration file
- Context management files
- Template library
- Document registry

**Examples**:
```bash
# New web project
/init-craftsman my-app --type=web --framework=react

# API service
/init-craftsman api-service --type=api --framework=express

# Existing project
/init-craftsman legacy-app --preserve-existing
```

**Post-initialization**:
- Ready for `/design` or `/plan` commands
- All agents available
- Framework fully activated

---

## Quality & Deployment Commands

### /test

**Purpose**: Create and execute comprehensive testing strategies with qa-architect integration.

**Usage**:
```bash
/test [feature] [--type=unit|integration|e2e|performance|all]
/test [feature] --strategy=tdd|bdd
/test [feature] --coverage=80
```

**Testing Layers**:
- **Unit Tests**: Component-level testing (80%+ coverage)
- **Integration Tests**: API and service integration
- **E2E Tests**: User workflow validation (Playwright)
- **Performance Tests**: Load and stress testing
- **Security Tests**: Vulnerability scanning

**Examples**:
```bash
# Comprehensive test suite
/test user-authentication

# Specific test type
/test api --type=integration

# TDD approach
/test new-feature --strategy=tdd

# Performance testing
/test checkout-flow --type=performance
```

**Integration**:
- Uses qa-architect agent
- Playwright MCP for E2E testing
- CI/CD pipeline integration
- Coverage reporting

---

### /validate

**Purpose**: Framework health checks and validation with self-healing capabilities.

**Usage**:
```bash
/validate [--component=all|agents|commands|mcp|git] [--fix] [--deep]
```

**Validation Checks**:
- **Framework Structure**: Directory and file organization
- **Agent Configuration**: Proper formatting and integration
- **Command Availability**: All commands accessible
- **MCP Integration**: Tool connectivity and performance
- **Git Health**: Repository status and configuration

**Examples**:
```bash
# Full framework validation
/validate

# Fix identified issues
/validate --fix

# Deep component analysis
/validate --component=mcp --deep

# Specific validation
/validate --component=agents
```

**Self-Healing**:
- Automatic fixing of common issues
- Configuration restoration
- Missing file regeneration
- Performance optimization

---

### /deploy

**Purpose**: Production deployment with zero-downtime strategies and rollback capabilities.

**Usage**:
```bash
/deploy [application] --env=staging|production
/deploy [application] --strategy=blue-green|canary|rolling
/deploy [application] --rollback [--version=x.x.x]
```

**Deployment Strategies**:

**Blue-Green**:
- Prepare parallel environment
- Comprehensive testing
- Instant traffic switching
- Immediate rollback available

**Canary**:
- Progressive traffic increase
- Metric-based validation
- Automatic rollback triggers
- Risk minimization

**Rolling**:
- Gradual instance updates
- Maintain availability
- Health checks between batches

**Examples**:
```bash
# Production deployment
/deploy my-app --env=production --strategy=blue-green

# Canary deployment
/deploy api-service --env=production --strategy=canary

# Emergency rollback
/deploy my-app --rollback --version=2.3.1

# Dry run
/deploy my-app --dry-run
```

**Features**:
- CI/CD integration
- Health monitoring
- Automatic rollback
- Post-deployment validation

---

## Command Integration Patterns

### Sequential Workflows

```bash
# Feature development flow
/plan user-feature
  ↓
/implement user-feature
  ↓
/test user-feature
  ↓
/deploy user-feature
```

### Parallel Workflows

```bash
# System development
/design platform
  ↓
/workflow design-to-deploy platform
  ├─ Backend implementation
  ├─ Frontend implementation
  └─ Testing (all streams)
```

### Iterative Development

```bash
# Continuous improvement
/validate
  ↓
/plan improvements
  ↓
/implement improvements
  ↓
/test --type=all
  ↓
/deploy --strategy=canary
```

## Command Selection Matrix

| Scope | Time | Command | Use Case |
|-------|------|---------|----------|
| Single Component | 2-5min | `/add` | Creating agents, commands, templates |
| Feature | 5-15min | `/plan` | Multi-step features with dependencies |
| System | 15-45min | `/design` | Complex systems with research needs |
| Execution | Varies | `/implement` | Executing any plan or design |
| Multi-Agent | Varies | `/workflow` | Complex coordinated workflows |
| Quality | 10-30min | `/test` | Comprehensive testing strategies |
| Health | 2-5min | `/validate` | Framework and code validation |
| Release | 10-30min | `/deploy` | Production deployment management |

## Best Practices

### 1. Choose the Right Command
- Use `/add` for single components
- Use `/plan` for features
- Use `/design` for complex systems
- Let scope guide your choice

### 2. Follow the Flow
- Always start with planning (`/plan` or `/design`)
- Implement with progress tracking
- Test comprehensively before deployment
- Validate throughout the process

### 3. Leverage Integration
- Commands work together seamlessly
- Context preserved across commands
- Agents coordinate automatically
- Quality maintained throughout

### 4. Trust the Process
- Each command embodies craftsman principles
- Quality gates ensure excellence
- Framework guides best practices
- Documentation generated automatically

## Troubleshooting Commands

### Command Not Found
```bash
# Validate framework installation
/validate --component=commands

# Check CLAUDE.md imports
cat CLAUDE.md | grep "@.*commands"
```

### Command Failing
```bash
# Run framework validation
/validate --fix

# Check MCP tools
/validate --component=mcp --deep
```

### Performance Issues
```bash
# Analyze command performance
/validate --component=all --performance

# Optimize framework
/validate --fix --optimize
```

## Extending Commands

### Adding New Commands
```bash
# Create custom command
/add command my-custom-command

# Automatically includes:
# - Craftsman template
# - Integration points
# - Documentation
# - Quality standards
```

### Customizing Commands
Edit command files in `.claude/commands/`:
- Add new parameters
- Enhance functionality
- Integrate new tools
- Maintain standards

---

*Every command in the ClaudeCraftsman framework reflects our commitment to excellence. Choose wisely, execute with confidence, and create software that makes you proud.*
