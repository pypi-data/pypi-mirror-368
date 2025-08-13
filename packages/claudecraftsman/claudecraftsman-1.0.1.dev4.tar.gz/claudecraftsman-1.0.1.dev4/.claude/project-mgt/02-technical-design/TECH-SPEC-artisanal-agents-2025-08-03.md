# Technical Specification: Artisanal Agents System
*Comprehensive technical design for ClaudeCraftsman framework*

**Document**: TECH-SPEC-artisanal-agents-2025-08-03.md
**Created**: 2025-08-03
**Version**: 1.0
**Status**: Active

## System Overview

ClaudeCraftsman implements an artisanal agents system where specialized AI craftspeople collaborate to create high-quality software through research-driven, design-first development practices. The system operates within Claude Code's native agent framework while adding sophisticated coordination, context management, and quality assurance capabilities.

## Architecture Principles

### 1. Craftsman-First Design
Every component is designed as a master craftsperson would approach their work - with intention, pride, and attention to detail. No shortcuts that compromise long-term quality.

### 2. Research-Driven Decisions
All technical decisions are backed by current research using MCP tools (searxng, crawl4ai, context7, time). No assumptions without evidence.

### 3. Context Preservation Excellence
Agent handoffs maintain complete context through file-based systems. No information loss during transitions.

### 4. Time-Aware Implementation
All temporal references use current date from MCP time tool. No hardcoded dates anywhere in the system.

### 5. File Organization Mastery
Clean, logical directory structures with consistent naming prevent documentation sprawl and enable long-term maintainability.

## System Architecture

### High-Level Architecture

```
┌─────────────────────┐
│   User Intentions   │
│   (Feature Request) │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  Command Framework  │
│ (/design, /workflow)│
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│ Workflow Coordinator│
│  (Agent Selection   │
│   & Orchestration)  │
└──────────┬──────────┘
           │
  ┌────────┴────────┐
  │                 │
┌─▼────────┐ ┌─────▼──────┐
│ Planning │ │Implementation│
│ Artisans │ │ Craftspeople │
└─┬────────┘ └─────┬──────┘
  │                 │
  └────────┬────────┘
           │
┌──────────▼──────────┐
│ Context Management  │
│   (State Persist)   │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  File Organization  │
│  (Documentation)    │
└─────────────────────┘
```

### Component Layer Architecture

#### Layer 1: Command Interface
- **Command Parsers**: Interpret user intentions and route to appropriate agents
- **Parameter Validation**: Ensure commands have necessary context and requirements
- **MCP Integration**: Initialize time awareness and research tools
- **Error Handling**: Graceful degradation when tools unavailable

#### Layer 2: Workflow Orchestration
- **Agent Selection**: Choose appropriate craftspeople for the task
- **Workflow Planning**: Determine sequence and dependencies
- **Progress Tracking**: Monitor phase completion and quality gates
- **Context Routing**: Ensure proper information flow between agents

#### Layer 3: Specialized Agents
- **Planning Artisans**: PRD, technical specs, implementation planning
- **Implementation Craftspeople**: Architecture, backend, frontend development
- **Quality Assurance**: Testing, validation, documentation review
- **Coordination Agents**: Context management, handoff facilitation

#### Layer 4: Context Management
- **State Persistence**: File-based context preservation
- **Handoff Protocols**: Structured information transfer
- **Memory Management**: Efficient context loading and compression
- **Version Control**: Change tracking and rollback capabilities

#### Layer 5: File Organization
- **Directory Management**: Consistent structure creation and maintenance
- **Document Registry**: Centralized tracking of all project documents
- **Archive Management**: Proper versioning and superseded document handling
- **Template System**: Consistent formatting and structure enforcement

## Agent System Design

### Planning Artisans

#### product-architect
**Purpose**: Business requirements craftsperson and PRD creation master
**Specialization**: User needs research, market analysis, competitive positioning
**Tools**: MCP tools for research (searxng, crawl4ai, context7), time for current date
**Inputs**: Feature descriptions, business requirements, stakeholder input
**Outputs**: Comprehensive PRDs with research citations, BDD scenarios, success metrics
**Quality Standards**: All claims backed by verifiable sources, time-aware documentation

#### design-architect
**Purpose**: Technical specifications artisan and system design master
**Specialization**: Architecture decisions, technology selection, integration planning
**Tools**: MCP tools for technical research, existing system analysis
**Inputs**: PRDs, technical constraints, existing system context
**Outputs**: Technical specifications, architecture diagrams, integration plans
**Quality Standards**: Evidence-based technical decisions, scalability considerations

#### technical-planner
**Purpose**: Implementation planning craftsperson and resource management
**Specialization**: Task breakdown, dependency mapping, resource allocation
**Tools**: Project context analysis, complexity assessment
**Inputs**: Technical specifications, team capabilities, timeline constraints
**Outputs**: Implementation plans, task breakdowns, dependency maps, quality gates
**Quality Standards**: Phase-based planning, complexity-driven estimates, realistic dependencies

### Implementation Craftspeople

#### system-architect
**Purpose**: High-level architecture decisions with thoughtful consideration
**Specialization**: System design, technology integration, scalability planning
**Tools**: Sequential thinking modes, research integration
**Inputs**: Technical specifications, existing system analysis
**Outputs**: System architecture, technology choices, integration patterns
**Quality Standards**: Maintainable designs, evidence-based technology selection

#### backend-architect
**Purpose**: API and server-side development with quality focus
**Specialization**: API design, database architecture, server-side logic
**Tools**: TDD integration, research-backed best practices
**Inputs**: System architecture, functional requirements, performance criteria
**Outputs**: API specifications, database schemas, backend implementation
**Quality Standards**: Test-driven development, performance considerations, security best practices

#### frontend-developer
**Purpose**: UI and client-side development with user experience craftsmanship
**Specialization**: User interface design, client-side architecture, user experience
**Tools**: BDD integration, usability research
**Inputs**: User experience requirements, API specifications, design systems
**Outputs**: Frontend architecture, component specifications, user interfaces
**Quality Standards**: User-centered design, accessibility compliance, maintainable components

### Coordination Artisans

#### workflow-coordinator
**Purpose**: Multi-agent workflow management with intentional handoffs
**Specialization**: Agent coordination, progress tracking, quality gate enforcement
**Tools**: Context analysis, workflow state management
**Inputs**: Project requirements, agent capabilities, progress status
**Outputs**: Workflow plans, agent assignments, progress reports, handoff coordination
**Quality Standards**: Complete context preservation, efficient agent utilization

#### context-manager
**Purpose**: Context preservation and memory management with care
**Specialization**: Information organization, context compression, handoff facilitation
**Tools**: File system management, context analysis
**Inputs**: Agent outputs, project state, historical context
**Outputs**: Context files, handoff briefs, session memory, progress tracking
**Quality Standards**: Zero information loss, organized context structure

## MCP Tool Integration

### Time Awareness System
```yaml
Implementation:
  - All agents must call time MCP tool before generating any documents
  - Document naming uses actual current date: PRD-[project]-[YYYY-MM-DD].md
  - No hardcoded dates in any agent prompts or templates
  - Research queries include current year for relevance

Usage Pattern:
  1. Agent initialization: Call time MCP tool
  2. Document creation: Use current date in filename
  3. Research queries: Include current year/date context
  4. Citations: Include actual access date
```

### Research Integration System
```yaml
Research Tools:
  - searxng: General web search with current date context
  - crawl4ai: Deep content analysis from specific URLs
  - context7: Technical documentation and best practices

Research Protocol:
  1. Identify claims requiring validation
  2. Use appropriate MCP tool for research
  3. Cross-reference multiple sources
  4. Cite with URL, access date, relevant quotes
  5. Enable independent verification
```

## Context Management System

### File-Based Context Architecture

```
.claude/context/
├── WORKFLOW-STATE.md        # Current workflow status and active phase
├── CONTEXT.md               # Project context and accumulated knowledge
├── HANDOFF-LOG.md          # Agent transition history and decisions
├── SESSION-MEMORY.md       # Session continuity and temporary state
└── RESEARCH-CACHE.md       # Cached research findings with citations
```

### Context File Specifications

#### WORKFLOW-STATE.md
```yaml
Purpose: Track current workflow status and phase progression
Contents:
  - Current phase and active agents
  - Completed phases and quality gate status
  - Pending tasks and dependencies
  - Next actions and agent assignments
Update Frequency: Every agent transition
Responsibility: workflow-coordinator
```

#### CONTEXT.md
```yaml
Purpose: Maintain project context and accumulated knowledge
Contents:
  - Project overview and current objectives
  - Key decisions and rationale
  - Stakeholder requirements and constraints
  - Technical context and system information
Update Frequency: Major decisions or context changes
Responsibility: context-manager with agent contributions
```

#### HANDOFF-LOG.md
```yaml
Purpose: Track agent transitions and handoff quality
Contents:
  - Agent transition records with timestamps
  - Handoff brief summaries
  - Context preservation validation
  - Issues and resolutions
Update Frequency: Every agent handoff
Responsibility: context-manager
```

### Context Preservation Protocol

#### Pre-Handoff
1. **Context Compilation**: Current agent compiles all relevant context
2. **Decision Documentation**: All decisions and reasoning captured
3. **Research Preservation**: Citations and findings organized
4. **State Validation**: Current state verified and documented

#### Handoff Execution
1. **Handoff Brief Creation**: Comprehensive brief with all necessary context
2. **File Updates**: All context files updated with current information
3. **Next Agent Briefing**: Receiving agent provided complete context
4. **Validation Check**: Context preservation verified

#### Post-Handoff
1. **Context Verification**: Receiving agent confirms complete context
2. **Log Update**: Handoff logged with success metrics
3. **Continuity Check**: Work proceeds without information loss
4. **Issue Resolution**: Any gaps addressed immediately

## File Organization System

### Directory Structure Standard

```
.claude/
├── agents/                     # Agent definitions (.md files)
├── commands/                   # Command definitions (.md files)
├── docs/                       # Runtime documentation
│   ├── current/               # Active specifications
│   │   ├── registry.md        # Master document index
│   │   └── [project docs]     # PRDs, specs, plans
│   ├── archive/               # Superseded versions
│   │   └── [YYYY-MM-DD]/     # Date-organized archives
│   └── templates/             # Working templates
├── specs/                      # Technical specifications
│   ├── api-specifications/    # OpenAPI and API contracts
│   ├── database-schemas/      # Database design documents
│   └── component-specs/       # Frontend component specifications
├── context/                    # Runtime context files
│   ├── WORKFLOW-STATE.md      # Current workflow status
│   ├── CONTEXT.md             # Project context
│   ├── HANDOFF-LOG.md         # Agent handoff history
│   └── SESSION-MEMORY.md      # Session continuity
├── templates/                  # Reusable templates
└── project-mgt/               # Project management (static)
```

### Naming Conventions

#### Document Naming
```yaml
Pattern: [TYPE]-[project-name]-[YYYY-MM-DD].md
Examples:
  - PRD-user-authentication-2025-08-03.md
  - TECH-SPEC-payment-system-2025-08-03.md
  - IMPL-PLAN-mobile-app-2025-08-03.md

Requirements:
  - Use actual current date from time MCP tool
  - Lowercase with hyphens for project names
  - Consistent type prefixes (PRD, TECH-SPEC, IMPL-PLAN, etc.)
```

#### Directory Naming
```yaml
Pattern: lowercase-with-hyphens
Examples:
  - api-specifications
  - database-schemas
  - component-specs

Requirements:
  - Descriptive and logical organization
  - Consistent with overall structure
  - No spaces or special characters
```

### Document Registry System

#### Registry Structure
```markdown
# ClaudeCraftsman Document Registry

## Current Active Documents
| Document | Project | Created | Last Updated | Status |
|----------|---------|---------|--------------|--------|
| PRD-user-auth-2025-08-03.md | User Authentication | 2025-08-03 | 2025-08-03 | Active |

## Recently Archived
| Document | Archived Date | Reason | Archive Location |
|----------|---------------|--------|------------------|
| PRD-user-auth-v1.md | 2025-08-03 | Superseded | archive/2025-08-03/ |
```

#### Registry Maintenance
1. **Document Creation**: Add entry to registry with creation metadata
2. **Document Updates**: Update "Last Updated" field with current date
3. **Document Archival**: Move to archive section with archival reason
4. **Registry Validation**: Regular validation of registry accuracy

## Agent Communication Protocols

### Handoff Brief Standard

```markdown
## Agent Handoff Brief

**From**: [Agent Name] - [Agent Specialization]
**To**: [Next Agent Name] - [Next Agent Specialization]
**Date**: [Current Date from time MCP tool]
**Handoff ID**: [Unique identifier]

### Context Summary
[Comprehensive project context and current state]

### Completed Work
[Detailed summary of work completed with decisions made]

### Research Findings
[All research conducted with proper citations]

### Decisions Made
[Key decisions with rationale and alternatives considered]

### Next Actions Required
[Specific actions needed from receiving agent]

### Context Files Updated
[List of context files updated during this phase]

### Quality Validation
[Confirmation that work meets craftsman standards]

### Additional Notes
[Any additional context or considerations]
```

### Agent Interaction Patterns

#### Sequential Processing
1. **Planning Phase**: product-architect → design-architect → technical-planner
2. **Implementation Phase**: system-architect → backend-architect → frontend-developer
3. **Quality Phase**: testing agents → documentation agents → review agents

#### Parallel Processing (when possible)
- Backend and frontend development after system architecture complete
- Documentation and testing preparation during implementation
- Research activities parallel to implementation when dependencies allow

#### Cross-Phase Coordination
- **Context Updates**: All agents update relevant context files
- **Decision Consultation**: Agents can consult previous agents when needed
- **Quality Review**: workflow-coordinator validates handoffs and quality

## Quality Assurance System

### Quality Gates by Phase

#### Planning Phase Gates
- [ ] Market research completed with verifiable citations
- [ ] User needs validated through authoritative sources
- [ ] Technical feasibility confirmed through research
- [ ] All specifications use current date from time MCP tool
- [ ] BDD scenarios created for all user stories

#### Implementation Phase Gates
- [ ] Architecture decisions backed by research and best practices
- [ ] TDD/BDD protocols properly implemented
- [ ] Code quality meets craftsman standards
- [ ] Context preservation validated across agent handoffs
- [ ] Documentation maintains organization standards

#### Integration Phase Gates
- [ ] End-to-end workflows tested and validated
- [ ] Performance meets established benchmarks
- [ ] User acceptance criteria satisfied
- [ ] Documentation complete and accurate
- [ ] Migration validation successful

### Continuous Quality Monitoring

#### Automated Validation
- File organization compliance checking
- Document registry accuracy validation
- Context file integrity verification
- Time awareness validation (no hardcoded dates)

#### Manual Quality Review
- Agent output quality assessment
- Research citation verification
- Handoff brief completeness review
- User experience validation

## Performance and Scalability

### Performance Targets

#### Agent Response Times
- Simple tasks: <30 seconds
- Complex research tasks: <5 minutes
- Multi-agent workflows: <15 minutes
- Full design-to-implementation cycle: <2 hours

#### Context Management
- Context file loading: <5 seconds
- Handoff brief generation: <10 seconds
- Context compression when needed: <30 seconds
- Context integrity validation: <15 seconds

### Scalability Considerations

#### Project Size Scaling
- Small projects (single feature): All agents functional
- Medium projects (multiple features): Parallel agent execution
- Large projects (full applications): Context compression strategies
- Enterprise projects: Modular context management

#### Agent Scaling
- Core agents handle 80% of common workflows
- Specialized agents available for domain-specific needs
- Custom agent creation following template standards
- Agent coordination scales with workflow complexity

## Security and Privacy

### Context Security
- All context stored locally in project directory
- No external API calls for context management
- Research data cached locally with proper attribution
- Sensitive information handled according to project requirements

### Research Privacy
- MCP tool usage follows tool-specific privacy policies
- Research findings cited with public sources only
- No proprietary or confidential information in research citations
- Clear attribution enables independent verification

## Error Handling and Recovery

### Agent Failure Recovery
1. **Graceful Degradation**: Continue with reduced functionality when MCP tools unavailable
2. **Context Recovery**: Restore from context files when agents fail
3. **Handoff Retry**: Retry failed handoffs with additional context
4. **Manual Intervention**: Clear escalation path for human intervention

### Context Corruption Recovery
1. **Context Validation**: Regular integrity checks on context files
2. **Backup Strategy**: Version control for critical context files
3. **Recovery Procedures**: Step-by-step recovery from context corruption
4. **Prevention**: Atomic updates and validation before committing changes

## Deployment and Installation

### Installation Requirements
- Claude Code with native agent support
- MCP server access for research tools (time, searxng, crawl4ai, context7)
- File system access for context and documentation management
- No external dependencies beyond MCP tools

### Setup Process
1. **Directory Creation**: Establish .claude directory structure
2. **Agent Installation**: Deploy agent definitions to agents/ directory
3. **Command Installation**: Deploy command definitions to commands/ directory
4. **Template Setup**: Initialize templates and standards
5. **Validation**: Verify MCP tool access and basic functionality

### Configuration Management
- **Agent Configuration**: Agent parameters and specializations
- **File Organization**: Directory structure customization
- **Quality Standards**: Customizable quality gate criteria
- **Research Tools**: MCP tool configuration and fallback options

## Monitoring and Maintenance

### Operational Monitoring
- **Agent Performance**: Response times and success rates
- **Context Health**: File integrity and organization compliance
- **Quality Metrics**: Adherence to craftsman standards
- **User Satisfaction**: Feedback and usage patterns

### Maintenance Procedures
- **Regular Quality Reviews**: Periodic assessment of agent outputs
- **Context Cleanup**: Archive management and cleanup procedures
- **Agent Updates**: Procedure for updating agent definitions
- **Standard Evolution**: Process for improving quality standards

## Future Enhancements

### Planned Improvements
- **Advanced Context Compression**: Intelligent context summarization
- **Custom Agent Creation**: Tools for creating domain-specific craftspeople
- **Integration Expansion**: Additional MCP tool integrations
- **Analytics Dashboard**: Quality metrics and trend analysis

### Research Areas
- **Context Intelligence**: ML-based context relevance assessment
- **Quality Prediction**: Predictive quality analysis
- **Workflow Optimization**: Agent coordination efficiency improvements
- **User Experience**: Enhanced interaction patterns and feedback loops

---

**Technical Specification Owner**: ClaudeCraftsman Development Team
**Last Updated**: 2025-08-03
**Next Review**: Phase 1 Completion
**Implementation Status**: Design Complete, Implementation Pending

*"Every technical decision serves the ultimate goal of enabling craftspeople to create software they can be genuinely proud of."*
