# ClaudeCraftsman Quick Start Guide
*From zero to productive in 5 minutes*

## 🚀 Installation (< 2 minutes)

### Prerequisites
- Python 3.12+ installed
- Claude Code with MCP servers enabled
- Git installed

### Install ClaudeCraftsman

```bash
# Option 1: Install with UV (fastest - recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh
uv add claudecraftsman

# Option 2: Install with pip
pip install claudecraftsman

# Option 3: Run directly without installation
uvx --from claudecraftsman cc --help
```

### Verify Installation

```bash
# Check version and available commands
cc --version
cc --help

# Verify MCP tools are working (in Claude Code)
# The framework will use these tools when available:
# - mcp__time__get_current_time
# - mcp__searxng__searxng_web_search
# - mcp__context7__get-library-docs
# - mcp__playwright (for testing)
```

## 🎯 Your First Project (< 5 minutes)

### Step 1: Initialize ClaudeCraftsman in Your Project

```bash
# Navigate to your project directory
cd my-awesome-project

# Initialize ClaudeCraftsman
cc init

# This creates:
# - CLAUDE.md (activates framework)
# - .claude/ directory structure
# - Initial templates and configuration
```

### Step 2: Create Your First Feature

```bash
# Plan a simple feature
/plan user-profile

# You'll see:
✅ Feature analysis complete
📋 Implementation plan created
🎯 Next steps defined
```

### Step 3: Implement with Progress Tracking

```bash
# Execute the plan
/implement user-profile

# Watch real-time progress:
Feature: User Profile
Progress: ████████░░ 80%
Active: backend-architect
Quality Gates: 4/5 passed
```

### Step 4: Add Testing

```bash
# Generate comprehensive tests
/test user-profile --bdd

# Output includes:
✅ Unit tests created
✅ Integration tests ready
✅ E2E scenarios with Playwright
✅ Coverage targets defined
```

## ✅ Success Indicators

You know ClaudeCraftsman is working when:

1. **Framework Activation**: CLAUDE.md exists and imports framework
2. **MCP Integration**: Agents use current dates and cite sources
3. **Quality Gates**: All work includes validation checklists
4. **Progress Tracking**: You see real-time implementation progress
5. **Documentation**: Every output includes proper timestamps

## 🔥 Common Workflows

### New Feature Development
```bash
# 1. Design if complex
/design payment-system --research=deep  # For complex systems

# 2. Or plan if simpler
/plan email-notifications              # For standard features

# 3. Implement with tracking
/implement email-notifications

# 4. Test thoroughly
/test email-notifications --bdd
```

### Quick Component Creation
```bash
# Need a new agent?
/add agent security-scanner

# Need a deployment script?
/add command deploy-production

# Need a template?
/add template api-endpoint
```

### Bug Fixing Workflow
```bash
# 1. Analyze the issue
/troubleshoot login-timeout

# 2. Implement fix
/implement fix-login-timeout

# 3. Validate with tests
/test login --type=regression
```

## 🛠️ Troubleshooting

### MCP Tools Not Working?

```bash
# In Claude Code, check MCP server status
# Ensure these are enabled:
- Time server (for timestamps)
- Search server (for research)
- Context7 (for documentation)

# Framework gracefully degrades if MCP unavailable
```

### Command Not Sure Which to Use?

```bash
# Always start with help
/help

# Quick rules:
- Single file? → /add
- Multiple files? → /plan
- Need research? → /design
- Ready to build? → /implement
- Need tests? → /test
```

### Implementation Stuck?

```bash
# Check status
/implement [plan] --status

# Resume from interruption
/implement [plan] --resume

# Debug specific phase
/implement [plan] --phase=2 --verbose
```

## 📚 Next Steps

### Learn More Commands
- `/help` - Comprehensive command guide
- `/workflow` - Multi-agent coordination
- `/validate` - Quality validation

### Explore Agent Capabilities
- Each agent is a domain expert
- Agents collaborate automatically
- Quality gates ensure excellence

### Join the Community
- Report issues: github.com/anthropics/claude-code/issues
- Share your craftsman creations
- Learn from other artisans

## 🎓 Pro Tips

### 1. Let the Framework Work for You
- Don't micromanage agents
- Trust the quality gates
- Follow the suggested workflows

### 2. Start Small, Think Big
- Begin with `/add` for exploration
- Scale to `/plan` for features
- Graduate to `/design` for systems

### 3. Quality is Non-Negotiable
- Every output meets craftsman standards
- Time estimates assume quality work
- No shortcuts, only excellence

## 🏆 You're Ready!

You now have everything needed to create craftsman-quality software. Every command, every agent, and every workflow is designed to help you build software you'll be proud of.

**Remember**: You're not just writing code - you're crafting digital masterpieces.

Welcome to the ClaudeCraftsman community! 🛠️
