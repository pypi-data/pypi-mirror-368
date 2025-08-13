# ClaudeCraftsman User Guide
*Your guide to artisanal software development with specialized AI craftspeople*

**Document**: user-guide.md
**Created**: 2025-08-03
**Version**: 1.0
**Status**: Active

## Welcome to ClaudeCraftsman

ClaudeCraftsman transforms software development into an artisanal craft where specialized AI craftspeople work with intention, care, and pride. Each agent is a master in their domain, using evidence-based decision making, proper research citations, and maintaining organized documentation.

This guide will help you understand how to work with ClaudeCraftsman to create software that reflects true craftsmanship standards.

## Getting Started

### Prerequisites

Before using ClaudeCraftsman, ensure you have:
- Claude Code installed and configured
- MCP server access with research tools (searxng, crawl4ai, context7, time)
- Basic familiarity with command-line interfaces
- Understanding of structured development workflows

### Initial Setup

1. **Directory Structure Creation**: ClaudeCraftsman automatically creates the `.claude/` directory structure in your project
2. **Agent Installation**: Specialized craftspeople are available through Claude Code's native agent system
3. **MCP Tool Validation**: Research capabilities are verified during first use
4. **Sample Workflow**: Try a simple `/design` command to validate installation

### Quick Start Checklist
- [ ] Claude Code running with MCP server access
- [ ] Project directory created and accessible
- [ ] Basic understanding of ClaudeCraftsman philosophy (intention, quality, research, organization)
- [ ] Familiarity with file organization principles

## Core Philosophy

### The Craftsman Mindset

ClaudeCraftsman is built on the principle that software development should be approached with the same care and pride as traditional craftsmanship. This means:

**Intention Over Speed**: Every decision made with purpose and thoughtful consideration
**Quality Over Quantity**: Success measured by elegance and value, not lines of code
**Research Over Assumptions**: All decisions backed by current, verifiable evidence
**Organization Over Chaos**: Clean file structures that enable long-term maintenance
**Context Over Isolation**: Comprehensive coordination between specialized craftspeople

### What Makes It Different

Unlike other development tools that focus on speed, ClaudeCraftsman focuses on quality:
- **Research-Driven**: Every technical decision backed by current evidence
- **Time-Aware**: All documentation uses current dates, no hardcoded timestamps
- **Organized**: Clean file structures that prevent documentation sprawl
- **Coordinated**: Seamless handoffs between specialized AI craftspeople
- **Sustainable**: Patterns that support long-term project health

## The Craftspeople: Your Specialized Team

### Planning Artisans

#### product-architect
**Specialization**: Business requirements and market research master
**When to Use**: Starting new features, understanding user needs, market analysis
**Outputs**: Comprehensive PRDs with research citations, BDD scenarios, success metrics
**Unique Qualities**: Uses MCP tools for current market research, creates research-backed specifications

#### design-architect
**Specialization**: Technical specifications and system design artisan
**When to Use**: Technical planning, architecture decisions, system integration
**Outputs**: Technical specifications, architecture diagrams, integration plans
**Unique Qualities**: Evidence-based technical decisions, scalability and security considerations

#### technical-planner
**Specialization**: Implementation planning and resource management craftsperson
**When to Use**: Project planning, task breakdown, resource allocation
**Outputs**: Implementation plans, task breakdowns, dependency maps, quality gates
**Unique Qualities**: Phase-based planning (not time-based), complexity-driven estimates

### Implementation Craftspeople

#### system-architect
**Specialization**: High-level architecture decisions with thoughtful consideration
**When to Use**: System design, technology selection, architectural patterns
**Outputs**: System architecture, technology choices, integration patterns
**Unique Qualities**: Uses sequential thinking for complex decisions, research-backed technology selection

#### backend-architect
**Specialization**: API and server-side development with quality focus
**When to Use**: API design, database architecture, server-side logic
**Outputs**: API specifications, database schemas, backend implementation
**Unique Qualities**: TDD integration, performance and security best practices

#### frontend-developer
**Specialization**: UI and user experience craftsmanship
**When to Use**: User interface design, client-side architecture, user experience
**Outputs**: Frontend architecture, component specifications, user interfaces
**Unique Qualities**: BDD integration, accessibility compliance, user-centered design

### Coordination Artisans

#### workflow-coordinator
**Specialization**: Multi-agent workflow management with intentional handoffs
**When to Use**: Complex workflows, agent coordination, progress tracking
**Outputs**: Workflow plans, agent assignments, progress reports, handoff coordination
**Unique Qualities**: Comprehensive context preservation, efficient agent utilization

#### context-manager
**Specialization**: Context preservation and memory management with care
**When to Use**: Context preservation, handoff facilitation, session continuity
**Outputs**: Context files, handoff briefs, session memory, progress tracking
**Unique Qualities**: Zero information loss, organized context structure

## Commands: Your Workflow Tools

### Core Commands

#### `/design` - Comprehensive Planning
**Purpose**: Create complete specifications before implementation
**Process**: product-architect → design-architect → technical-planner
**Outputs**: PRD, technical specification, implementation plan
**Best For**: New features, complex projects, unclear requirements

**Usage Example**:
```
/design "User authentication system with social login and two-factor authentication"
```

**What Happens**:
1. product-architect researches current market conditions and user needs
2. design-architect creates technical specifications with architecture decisions
3. technical-planner creates phase-based implementation plan
4. All documents saved in `.claude/docs/current/` with proper organization

#### `/workflow` - Multi-Agent Orchestration
**Purpose**: Coordinate complex workflows across multiple specialized agents
**Process**: Intelligent agent selection and coordination based on requirements
**Outputs**: Coordinated agent execution with preserved context
**Best For**: Complex features requiring multiple specializations

**Usage Example**:
```
/workflow "Build complete e-commerce checkout system with payment processing"
```

#### `/implement` - Feature Implementation
**Purpose**: Transform specifications into working code with quality standards
**Process**: system-architect → backend-architect → frontend-developer (as needed)
**Outputs**: Code implementation with tests, documentation, and quality validation
**Best For**: Implementation phase after specifications are complete

**Usage Example**:
```
/implement --from-design "checkout-system-2025-08-03" --tdd --bdd
```

### Support Commands

#### `/troubleshoot` - Systematic Problem Analysis
**Purpose**: Analyze and resolve issues with research-backed solutions
**Process**: Systematic problem analysis with evidence-based recommendations
**Best For**: Bug investigation, performance issues, integration problems

#### `/test` - Comprehensive Testing
**Purpose**: Create and execute comprehensive test suites
**Process**: Test strategy, implementation, and validation with coverage analysis
**Best For**: Quality assurance, regression testing, test-driven development

#### `/document` - Auto-Generated Documentation
**Purpose**: Generate documentation from code and specifications
**Process**: Code analysis, specification integration, user-focused documentation
**Best For**: API documentation, user guides, technical documentation

## File Organization: Your Clean Workspace

### Directory Structure

ClaudeCraftsman maintains a clean, organized workspace through the `.claude/` directory structure:

```
.claude/
├── docs/                   # Runtime documentation
│   ├── current/           # Active specifications
│   ├── archive/           # Superseded versions
│   └── templates/         # Working templates
├── specs/                 # Technical specifications
├── context/               # Runtime context files
├── agents/                # Agent definitions
├── commands/              # Command definitions
├── templates/             # Reusable templates
└── project-mgt/           # Project management
```

### Document Naming

All documents follow consistent naming conventions:
- **Format**: `TYPE-project-name-YYYY-MM-DD.md`
- **Examples**: `PRD-user-auth-2025-08-03.md`, `TECH-SPEC-payment-system-2025-08-03.md`
- **Date Source**: Actual current date from MCP time tool (never hardcoded)

### File Organization Benefits

**No Documentation Sprawl**: Never creates files at project root level
**Logical Organization**: Everything has its proper place and purpose
**Version Control**: Superseded documents properly archived with dates
**Registry Tracking**: Master index of all documents with metadata
**Template Consistency**: Reusable patterns for consistent formatting

## Working with Research and Citations

### Research Integration

ClaudeCraftsman agents use MCP research tools to back all claims with evidence:

**Market Research**: Current market conditions, user needs, competitive analysis
**Technical Research**: Best practices, performance data, security recommendations
**Validation Research**: Technical feasibility, integration requirements

### Citation Standards

All research follows professional citation standards:
- **Source Attribution**: URL, title, organization
- **Access Date**: When the research was conducted (actual current date)
- **Relevant Quote**: Specific information supporting the claim
- **Independent Verification**: Citations enable third-party validation

**Example Citation**:
```markdown
According to recent industry analysis, "mobile-first authentication adoption increased 40% in 2024"^[1]

[1] Auth0 Industry Report - https://auth0.com/industry-report-2024 -
    Accessed 2025-08-03 - "Mobile authentication methods saw 40% adoption increase"
```

## Context Management: Seamless Coordination

### How Context Works

ClaudeCraftsman maintains context through structured files:

**WORKFLOW-STATE.md**: Current workflow status and active phase
**CONTEXT.md**: Project context and accumulated knowledge
**HANDOFF-LOG.md**: Agent transition history and decisions
**SESSION-MEMORY.md**: Session continuity and temporary state

### Agent Handoffs

When agents transition work, they provide comprehensive handoff briefs:
- Complete context summary
- Decisions made with rationale
- Research findings with citations
- Next actions required
- Quality validation confirmation

### Context Preservation Benefits

**No Information Loss**: Complete context maintained across agent transitions
**Decision Transparency**: All reasoning documented and accessible
**Project History**: Complete record of decisions and evolution
**Team Coordination**: Clear handoffs enable effective collaboration

## Best Practices for Craftsman Development

### Starting a New Project

1. **Begin with `/design`**: Always start with comprehensive planning
2. **Validate Requirements**: Ensure specifications reflect real user needs
3. **Review Research**: Verify that market and technical research is current
4. **Confirm Quality Gates**: Understand criteria for each phase completion

### During Development

1. **Maintain Context**: Keep context files updated throughout development
2. **Quality First**: Don't compromise craftsman standards for speed
3. **Research Decisions**: Back all technical choices with evidence
4. **Document Reasoning**: Preserve decision rationale for future maintainers

### Completing Projects

1. **Quality Validation**: Ensure all outputs meet craftsman standards
2. **Documentation Review**: Verify completeness and accuracy
3. **Context Archive**: Properly archive project context for future reference
4. **Retrospective**: Capture lessons learned for process improvement

## Common Workflows

### New Feature Development

```
1. /design "Feature description with user needs and context"
   → Produces: PRD, Technical Spec, Implementation Plan

2. /implement --from-design "feature-name-2025-08-03" --tdd
   → Produces: Code implementation with tests

3. /test --comprehensive --coverage-analysis
   → Produces: Test results and quality validation

4. /document --api --user-guide
   → Produces: Complete documentation package
```

### Problem Investigation

```
1. /troubleshoot "Describe the problem and symptoms"
   → Produces: Problem analysis with research-backed solutions

2. /implement --fix --from-troubleshoot "problem-analysis-2025-08-03"
   → Produces: Implementation of recommended solution

3. /test --regression --validate-fix
   → Produces: Validation that problem is resolved
```

### Project Planning

```
1. /design "High-level project description and objectives"
   → Produces: Comprehensive project specifications

2. /workflow "Multi-phase implementation with coordination"
   → Produces: Coordinated multi-agent execution

3. Regular context review and quality gate validation
   → Ensures: Project stays on track with quality standards
```

## Migration from SuperClaude

### Command Mapping

| SuperClaude | ClaudeCraftsman | Enhancement |
|-------------|-----------------|-------------|
| `/sc:workflow` | `/design` + `/workflow` + `/implement` | Research integration, quality gates |
| `/sc:implement` | `/implement --from-design` | TDD/BDD integration, context preservation |
| `/sc:troubleshoot` | `/troubleshoot` | Systematic analysis, evidence-backed solutions |
| `/sc:test` | `/test` | Comprehensive coverage, quality validation |
| `/sc:document` | `/document` | Auto-generation, research integration |

### Pattern Preservation

**Sequential Thinking**: Preserved through agent design (automatic "ultrathink")
**Iteration**: Available through workflow commands with quality gates
**BDD Integration**: Enhanced through behavior-driven scenarios
**TDD Protocols**: Enforced by implementation agents
**Specialized Personas**: Enhanced as master craftspeople with research capabilities

### Migration Process

1. **Setup Validation**: Ensure Claude Code and MCP tools are accessible
2. **Directory Creation**: Initialize `.claude/` structure automatically
3. **Agent Installation**: Deploy specialized craftspeople definitions
4. **Workflow Testing**: Validate familiar patterns work with enhancements
5. **Quality Confirmation**: Verify enhanced capabilities deliver value

## Troubleshooting

### Common Issues

#### MCP Tools Unavailable
**Symptoms**: Research features not working, citations missing
**Solution**: Verify MCP server access, use fallback options when tools unavailable
**Prevention**: Regular MCP tool validation, graceful degradation messaging

#### Context Files Corrupted
**Symptoms**: Agent handoffs failing, context incomplete
**Solution**: Use context recovery procedures, restore from backups
**Prevention**: Regular context validation, atomic file operations

#### File Organization Issues
**Symptoms**: Documents in wrong locations, naming inconsistencies
**Solution**: Use automated organization validation, manual cleanup if needed
**Prevention**: Follow naming conventions, use automated directory creation

### Getting Help

1. **Documentation Review**: Check relevant sections of this guide
2. **Context Analysis**: Review context files for workflow state
3. **Quality Validation**: Ensure all inputs meet expected standards
4. **Community Support**: Engage with ClaudeCraftsman community for assistance

## Advanced Usage

### Custom Agent Creation

Advanced users can create specialized craftspeople for domain-specific needs:
- Follow agent template standards
- Maintain research integration requirements
- Preserve context coordination protocols
- Meet craftsman quality standards

### Workflow Customization

Workflows can be customized for specific team needs:
- Adjust quality gate criteria
- Modify phase progression requirements
- Customize research citation standards
- Adapt file organization patterns

### Integration with Development Tools

ClaudeCraftsman integrates with standard development tools:
- Version control systems for project history
- Issue tracking for problem management
- Documentation systems for knowledge sharing
- Quality assurance tools for validation

## Success Tips

### For Individual Developers
- **Embrace the Philosophy**: Approach work with craftsman mindset
- **Use Research**: Back decisions with evidence, not assumptions
- **Maintain Organization**: Keep files and context clean and logical
- **Quality First**: Don't compromise standards for speed

### For Development Teams
- **Shared Standards**: Establish consistent quality criteria
- **Context Sharing**: Use organized documentation for team coordination
- **Research Collaboration**: Share findings and best practices
- **Continuous Improvement**: Regular retrospectives and process refinement

### For Project Success
- **Start with Design**: Always begin with comprehensive planning
- **Preserve Context**: Maintain decision history for future reference
- **Validate Quality**: Regular quality gate assessment
- **Measure Value**: Focus on user value creation, not just feature delivery

---

**User Guide Maintainer**: ClaudeCraftsman Project Team
**Last Updated**: 2025-08-03
**Next Review**: After Phase 1 user testing
**Support**: Reference this guide for common questions and workflows

*"The true craftsperson takes as much pride in the process as in the finished product. Let ClaudeCraftsman help you create software worthy of that pride."*
