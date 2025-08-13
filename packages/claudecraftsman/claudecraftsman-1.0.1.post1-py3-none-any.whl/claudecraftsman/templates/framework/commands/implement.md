---
name: implement
description: Execute comprehensive plans through orchestrated multi-agent coordination. Transforms detailed plans into systematic delivery with progress tracking and quality gates. The bridge between planning and results.
---

# Implement Command

_Orchestrated plan execution with craftsman coordination_

## Philosophy

Plans without execution are just documentation. The implement command transforms comprehensive plans into systematic delivery through coordinated agent work, progress tracking, and quality validation. Every implementation reflects our commitment to seeing excellent plans through to excellent results.

## Usage Patterns

- `/implement [plan-name]` - Execute plan from current plans directory
- `/implement [plan-name] --from-file=[path]` - Execute specific plan file
- `/implement [plan-name] --phase=[number]` - Execute specific phase only
- `/implement [plan-name] --resume` - Resume interrupted implementation
- `/implement [plan-name] --dry-run` - Preview implementation without execution

## Core Capabilities

### Plan Orchestration

The implement command serves as the master conductor, coordinating:

- **Multi-phase execution** with proper sequencing and dependencies
- **Agent coordination** with comprehensive handoffs and context preservation
- **Progress tracking** with milestone validation and quality gates
- **Resource management** ensuring agents have what they need when they need it
- **Quality assurance** maintaining craftsman standards throughout execution

### Implementation Process

1. **Plan Analysis**: Parse and validate the implementation plan
2. **Dependency Mapping**: Identify prerequisites and execution order
3. **Agent Orchestration**: Coordinate appropriate agents for each phase
4. **Progress Monitoring**: Track completion against plan milestones
5. **Quality Validation**: Ensure craftsman standards at each phase
6. **Context Management**: Maintain implementation state and handoff history
7. **Documentation Updates**: Keep project management tracking current

## Plan File Integration

### Supported Plan Formats

The implement command works with plans created by:

- **`/plan [feature]`** - Feature implementation plans
- **`/design [system]`** - System architecture plans
- **Project management plans** from `.claude/project-mgt/`
- **Custom plan formats** following framework standards

### Plan Parsing Intelligence

```markdown
# Implementation automatically extracts:

- Phase breakdown and sequencing
- Dependencies between phases and tasks
- Agent assignments and coordination requirements
- Success criteria and quality gates
- Resource requirements and constraints
- Timeline expectations and milestones
```

## Agent Coordination

### Multi-Agent Orchestration

The implement command coordinates multiple agents:

```markdown
Phase 1: Foundation
├── Assigns system-architect for infrastructure planning
├── Coordinates with design-architect for technical specs
└── Ensures proper handoffs with comprehensive context

Phase 2: Implementation
├── Orchestrates backend-architect and frontend-developer
├── Manages parallel work streams with dependency awareness
└── Maintains quality gates and craftsman standards

Phase 3: Integration
├── Coordinates testing and validation agents
├── Manages deployment and operational concerns
└── Ensures complete delivery against original plan
```

### Handoff Management

- **Context Preservation**: All agent context maintained across phases
- **Progress Tracking**: Each handoff logged with completion status
- **Quality Gates**: Validation before phase transitions
- **Dependency Resolution**: Blocking issues identified and resolved

## Progress Tracking System

### Implementation State Management

```markdown
Implementation Status Tracking:
├── Overall progress percentage
├── Phase completion status
├── Current active work streams
├── Blocked items and resolution status
├── Quality gate passage tracking
└── Resource utilization and constraints
```

### Documentation Updates

Automatic updates to:

- **`.claude/context/WORKFLOW-STATE.md`** - Current implementation focus
- **`.claude/context/HANDOFF-LOG.md`** - Agent coordination history
- **`.claude/project-mgt/06-project-tracking/progress-log.md`** - Project-level progress
- **Plan files themselves** - Progress annotations and completion markers

## Quality Assurance Integration

### Craftsman Standards Enforcement

Every implementation phase includes:

- **Time Awareness**: All work uses current datetime from MCP tools
- **Research Validation**: Claims and decisions backed by current sources
- **File Organization**: All outputs follow framework naming and organization
- **Quality Gates**: Comprehensive validation before phase completion
- **Standards Compliance**: Framework principles applied throughout

### Quality Gate Validation

Before phase transitions:

```markdown
Quality Gate Checklist:

- [ ] Phase deliverables meet craftsman quality standards
- [ ] All work properly documented with current timestamps
- [ ] Agent handoffs complete with full context preservation
- [ ] Dependencies satisfied for next phase
- [ ] No blocking issues or technical debt introduced
- [ ] Work aligns with original plan intent and success criteria
```

## Implementation Strategies

### Phase-Based Execution

```markdown
Sequential Phase Execution:

1. Validate prerequisites and dependencies
2. Assign appropriate agents with clear context
3. Monitor progress with regular quality checks
4. Complete handoffs with comprehensive documentation
5. Validate phase success criteria before proceeding
```

### Parallel Work Coordination

```markdown
Parallel Stream Management:
├── Independent work streams identified and coordinated
├── Dependency conflicts resolved proactively
├── Regular synchronization points with progress alignment
├── Context sharing between parallel agents
└── Unified integration and validation at completion
```

### Risk Management

- **Dependency Tracking**: Identify and resolve blocking dependencies
- **Quality Monitoring**: Continuous validation against craftsman standards
- **Progress Assessment**: Regular evaluation against plan timeline and scope
- **Issue Escalation**: Systematic handling of blockers and technical challenges

## Error Handling and Recovery

### Implementation Interruption

If implementation is interrupted:

- **State Preservation**: All progress and context saved automatically
- **Resume Capability**: `--resume` flag continues from last checkpoint
- **Context Recovery**: Agent states and handoffs fully restored
- **Progress Validation**: Verify completed work before proceeding

### Dependency Failures

When dependencies fail or block progress:

- **Alternative Path Analysis**: Identify workarounds and alternative approaches
- **Agent Consultation**: Leverage appropriate domain experts for resolution
- **Plan Adaptation**: Modify execution strategy while preserving intent
- **Stakeholder Communication**: Clear status and resolution timeline

## Integration with Other Commands

### Command Workflow Integration

```markdown
Complete Development Workflow:
/design system → /plan features → /implement plans → /test results → /deploy
↑ ↑ ↑ ↑ ↑
Architecture Feature Plans Execution Validation Delivery
```

### Framework Command Coordination

- **From `/plan`**: Execute comprehensive feature plans
- **From `/design`**: Implement complete system architectures
- **With `/add`**: Create individual components as needed during implementation
- **With `/test`**: Validate implementation results and quality
- **With workflow coordination**: Maintain context across all framework operations

## Project Management Integration

### Progress Reporting

Automatic updates to project management documentation:

```markdown
Implementation Progress Updates:
├── Phase completion percentages
├── Milestone achievement tracking
├── Resource utilization reports
├── Quality metrics and gate passage
├── Issue identification and resolution status
└── Timeline adherence and variance analysis
```

### Stakeholder Communication

- **Regular status updates** in project tracking documentation
- **Milestone notifications** when phases complete
- **Blocker identification** with clear resolution paths
- **Success celebration** when implementation completes successfully

## File Organization Standards

### Implementation Artifacts

```markdown
Implementation creates organized documentation:
.claude/docs/current/
├── implementation/
│ ├── IMPL-STATUS-[plan-name]-[YYYY-MM-DD].md
│ ├── IMPL-PROGRESS-[plan-name]-[YYYY-MM-DD].md
│ └── IMPL-RESULTS-[plan-name]-[YYYY-MM-DD].md
├── [component deliverables as specified in plan]
└── [quality validation artifacts]
```

### Context Management

```markdown
Implementation state preserved in:
.claude/context/
├── IMPLEMENTATION-STATE-[plan-name].md
├── AGENT-COORDINATION-[plan-name].md
└── QUALITY-TRACKING-[plan-name].md
```

## Success Criteria

### Implementation Completion

Implementation is complete when:

- [ ] All plan phases executed successfully with quality validation
- [ ] All deliverables created and meet craftsman standards
- [ ] All agents properly coordinated with complete handoffs
- [ ] All quality gates passed with documented validation
- [ ] Project management documentation updated with final status
- [ ] Implementation artifacts properly organized and documented
- [ ] Original plan intent fully realized with measurable results

### Quality Validation

Every implementation must demonstrate:

- **Craftsman Quality**: All deliverables reflect excellence and attention to detail
- **Framework Compliance**: All work follows established standards and patterns
- **Documentation Completeness**: Full implementation history preserved
- **Context Preservation**: Complete handoff chain from planning through delivery

## Usage Examples

### Feature Implementation

```markdown
# Execute a feature plan

/implement user-authentication

# Coordinates:

# - Requirements validation with product-architect

# - Technical specification with design-architect

# - Backend implementation with backend-architect

# - Frontend implementation with frontend-developer

# - Testing coordination with appropriate testing agents

# - Documentation updates throughout process
```

### System Implementation

```markdown
# Execute comprehensive system plan

/implement git-integration --from-file=PLAN-git-integration-2025-08-04.md

# Orchestrates:

# Phase 1: Foundation layer with systematic agent coordination

# Phase 2: Workflow automation with quality validation

# Phase 3: Pervasive integration with comprehensive testing
```

### Partial Implementation

```markdown
# Execute specific phase only

/implement git-integration --phase=1

# Focuses on:

# Single phase execution with full quality standards

# Context preparation for subsequent phases

# Milestone validation before phase completion
```

## The Implementation Commitment

The implement command transforms excellent plans into excellent results through systematic execution, thoughtful coordination, and unwavering commitment to craftsman quality. Every implementation serves as proof that thorough planning combined with disciplined execution creates outcomes worthy of our craftsmanship.

**Remember**: Plans are promises to ourselves and our stakeholders. The implement command ensures we keep those promises with the same excellence and care that went into creating the plans themselves.

## Quality Gates for Implementation Command

Before considering the implement command ready for use:

- [ ] Can successfully parse and validate all plan formats created by framework
- [ ] Demonstrates proper multi-agent coordination with handoff preservation
- [ ] Updates all project management tracking automatically
- [ ] Handles implementation interruption and recovery gracefully
- [ ] Maintains craftsman quality standards throughout execution
- [ ] Provides clear progress visibility and status reporting
- [ ] Integration tested with existing framework commands and workflows

The implement command completes our development workflow, ensuring that the excellent plans created by our craftsman framework result in excellent implementations worthy of the planning effort invested.
