# ClaudeCraftsman FAQ
*Frequently Asked Questions*

## General Questions

### What is ClaudeCraftsman?

ClaudeCraftsman is an AI-powered development framework that elevates software creation to an artisanal craft. It orchestrates specialized AI agents to produce high-quality, research-backed code with comprehensive documentation and testing.

### How is this different from other AI coding tools?

**Key Differentiators:**
- **Craftsman Philosophy**: Every output meets artisanal quality standards
- **Multi-Agent Orchestration**: Specialized experts for each domain
- **Research-Driven**: All decisions backed by current sources via MCP tools
- **Progress Tracking**: Real-time visibility into development progress
- **Quality Gates**: Comprehensive validation at every step

### Do I need to be an expert developer to use it?

No! ClaudeCraftsman is designed for developers at all levels:
- **Beginners**: Learn from expert agents and best practices
- **Intermediate**: Accelerate development with quality patterns
- **Experts**: Focus on architecture while agents handle implementation

### What languages/frameworks are supported?

ClaudeCraftsman supports any language or framework, with specialized expertise in:
- **Backend**: Python (FastAPI), Node.js, Go, Java
- **Frontend**: React, Vue, Angular, Svelte
- **Mobile**: React Native, Flutter
- **Databases**: PostgreSQL, MongoDB, Redis
- **Cloud**: AWS, GCP, Azure
- **Testing**: Jest, Pytest, Playwright, Cypress

## Installation & Setup

### What are the system requirements?

**Minimum Requirements:**
- Python 3.12 or higher
- 8GB RAM
- 2GB free disk space
- Internet connection (for MCP tools)

**Recommended:**
- Python 3.12+
- 16GB RAM
- SSD with 10GB free space
- Claude Code with MCP servers enabled

### How do I update ClaudeCraftsman?

```bash
# With UV (recommended)
uv add --upgrade claudecraftsman

# With pip
pip install --upgrade claudecraftsman

# Check version
cc --version
```

### Can I use it without MCP tools?

Yes! ClaudeCraftsman gracefully degrades without MCP:
- Framework still works perfectly
- Uses fallback dates instead of live timestamps
- Skips research steps but maintains quality
- All core features remain functional

## Command Usage

### Which command should I use when?

**Quick Decision Guide:**
- **Single component** → `/add`
- **Feature (2-10 files)** → `/plan`
- **System (10+ files)** → `/design`
- **Have a plan** → `/implement`
- **Need tests** → `/test`

### Can I customize the output?

Yes! Every command supports flags for customization:
```bash
/plan feature --scope=backend    # Backend only
/implement --phase=2             # Specific phase
/test --type=unit               # Only unit tests
/design --research=minimal      # Less research
```

### How do I track progress?

Multiple ways to track progress:
```bash
# Real-time progress
/implement feature              # Shows live progress

# Check status anytime
/implement feature --status

# View detailed logs
cat .claude/context/WORKFLOW-STATE.md

# Project-level tracking
cat .claude/project-mgt/06-project-tracking/progress-log.md
```

## Agent Questions

### What agents are available?

**Core Framework Agents:**
- `product-architect`: Business requirements and PRDs
- `design-architect`: Technical specifications
- `system-architect`: High-level architecture
- `backend-architect`: Server-side development
- `frontend-developer`: UI/UX implementation
- `qa-architect`: Testing strategies
- `devops-architect`: Infrastructure and deployment
- `security-architect`: Security and compliance
- `data-architect`: Database design
- `ml-architect`: Machine learning systems
- `python-backend`: Python-specific expertise
- `workflow-coordinator`: Multi-agent orchestration

### Can I create custom agents?

Absolutely! Create specialized agents for your needs:
```bash
/add agent mobile-specialist
/add agent blockchain-expert
/add agent game-developer
```

### How do agents work together?

Agents collaborate through structured handoffs:
1. Each agent completes their specialized work
2. Creates comprehensive handoff documentation
3. Next agent receives full context
4. Workflow coordinator ensures smooth transitions

## Quality & Testing

### What are quality gates?

Quality gates are validation checkpoints that ensure:
- Code meets standards
- Tests pass with coverage targets
- Documentation is complete
- Security requirements are met
- Performance benchmarks achieved

### How much test coverage is required?

**Default Targets:**
- MVP/New features: 60% minimum
- Mature features: 80% minimum
- Critical paths: 95% recommended

Customize per project:
```bash
/plan feature --coverage=70
```

### Can I skip quality gates?

Not recommended, but possible with justification:
```bash
/implement feature --override-quality "MVP deadline, will improve"
```

Always document why and plan to address later.

## MCP Tools & Research

### What are MCP tools?

MCP (Model Context Protocol) tools provide:
- **Time**: Current timestamps (`mcp__time__get_current_time`)
- **Search**: Web research (`mcp__searxng__searxng_web_search`)
- **Docs**: Library documentation (`mcp__context7__get-library-docs`)
- **Testing**: Browser automation (`mcp__playwright`)

### Why do outputs include timestamps?

Timestamps ensure:
- Reproducibility of decisions
- Currency of research
- Audit trail for compliance
- Version tracking for documentation

### How does research validation work?

All claims are backed by sources:
```markdown
FastAPI provides 40% better performance^[1]

[1] FastAPI Benchmarks - URL - Accessed: 2025-08-08
```

## Troubleshooting

### What if implementation gets stuck?

```bash
# 1. Check status
/implement feature --status

# 2. View verbose logs
/implement feature --verbose

# 3. Resume from checkpoint
/implement feature --resume

# 4. Reset if needed
/implement feature --reset --preserve-work
```

### Commands are running slowly?

Speed up operations:
```bash
# Skip research for speed
/implement feature --no-research

# Single phase only
/implement feature --phase=1

# Disable parallel operations
/implement feature --sequential
```

### How do I debug issues?

Enable debug mode:
```bash
# Global debug
export CLAUDECRAFTSMAN_DEBUG=1

# Command debug
/implement feature --debug

# Check framework health
/validate framework
```

## Best Practices

### What's the recommended workflow?

**Standard Feature Development:**
1. `/plan feature-name` - Analyze and plan
2. `/implement feature-name` - Build with progress tracking
3. `/test feature-name` - Comprehensive testing
4. `/validate feature-name` - Final quality check

### How often should I commit?

ClaudeCraftsman encourages frequent commits:
- After each phase completion
- When switching between agents
- Before major operations
- End of each work session

### Should I review agent outputs?

Yes! While agents produce high-quality work:
- Review for business logic correctness
- Verify integration with existing code
- Ensure matches your specific requirements
- Learn from agent approaches

## Advanced Usage

### Can I run multiple implementations in parallel?

Yes, but coordinate carefully:
```bash
# Terminal 1
/implement feature-a

# Terminal 2
/implement feature-b

# Ensure no file conflicts!
```

### How do I handle large projects?

Break into manageable pieces:
```bash
# 1. Overall design
/design full-system

# 2. Separate plans for subsystems
/plan authentication-module
/plan payment-module
/plan reporting-module

# 3. Implement incrementally
/implement authentication-module
# Complete before next...
```

### Can I integrate with CI/CD?

Yes! ClaudeCraftsman works well in automation:
```yaml
# GitHub Actions example
- name: Run ClaudeCraftsman Tests
  run: |
    cc validate framework
    cc test all --ci-mode
```

## Philosophy Questions

### What does "craftsman" mean in this context?

Craftsman represents:
- **Pride in work**: Every output should make you proud
- **Attention to detail**: No shortcuts or compromises
- **Continuous learning**: Agents use latest best practices
- **Quality focus**: Excellence is non-negotiable
- **Thoughtful approach**: Every decision is intentional

### Why is everything so comprehensive?

We believe:
- Software should be built right the first time
- Documentation prevents future confusion
- Tests give confidence to change
- Quality compounds over time
- Your future self will thank you

### Can I use this for quick prototypes?

Yes! Adjust the scope, not the quality:
```bash
# Quick component
/add component user-card    # Still excellent, just focused

# MVP plan
/plan mvp-feature --scope=minimal

# Fast implementation
/implement mvp-feature --phases=1
```

## Getting Help

### Where can I get support?

1. **Built-in Help**: `/help` command
2. **Documentation**: This FAQ, Troubleshooting Guide
3. **GitHub Issues**: github.com/anthropics/claude-code/issues
4. **Community**: Share experiences and learn from others

### How do I report bugs?

Include in bug reports:
- ClaudeCraftsman version (`cc --version`)
- Command that failed
- Error messages
- Debug logs if available
- Steps to reproduce

### Can I contribute?

Yes! We welcome contributions:
- Report bugs and issues
- Share workflow improvements
- Create custom agents and templates
- Improve documentation
- Share your craftsman creations

## Future & Roadmap

### What's coming next?

Planned enhancements:
- More specialized agents
- Enhanced MCP tool integration
- Visual workflow designer
- Team collaboration features
- Performance optimizations

### Will it always be "craftsman" focused?

Yes! The commitment to quality and craftsmanship is fundamental to ClaudeCraftsman. We'll add features and capabilities, but never compromise on the artisanal approach to software development.

---

**Remember**: Every question is an opportunity to improve. If your question isn't here, please ask! We're committed to making ClaudeCraftsman the best tool for creating software you're proud of.
