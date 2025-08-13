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
- **MCP tool integration** for research validation and time awareness

### Real-Time Progress Visibility

```markdown
Implementation Progress Dashboard:
┌─────────────────────────────────────┐
│ Feature: User Authentication        │
│ Overall Progress: ████████░░ 75%    │
├─────────────────────────────────────┤
│ Phase 1: Foundation     ✅ Complete │
│ Phase 2: Implementation █▌  In Progress │
│ Phase 3: Integration    ⏳ Pending  │
├─────────────────────────────────────┤
│ Active Agent: backend-architect     │
│ Current Task: API endpoint design   │
│ Quality Gates: 3/4 Passed          │
└─────────────────────────────────────┘
```

### Implementation Process with MCP Integration

1. **Plan Analysis**: Parse and validate the implementation plan
   - Use `mcp__time__get_current_time` for timestamp awareness
   - Validate plan currency and relevance

2. **Dependency Mapping**: Identify prerequisites and execution order
   - Analyze task dependencies and critical path
   - Identify potential bottlenecks and risks

3. **Agent Orchestration**: Coordinate appropriate agents for each phase
   - Brief agents with full context and MCP tool access
   - Enable research validation through MCP tools

4. **Progress Monitoring**: Track completion against plan milestones
   - Real-time progress updates using TodoWrite
   - Quality gate validation at each checkpoint

5. **Quality Validation**: Ensure craftsman standards at each phase
   - Research-backed decisions using `mcp__searxng__searxng_web_search`
   - Documentation validation with current timestamps

6. **Context Management**: Maintain implementation state and handoff history
   - Preserve MCP research results across handoffs
   - Track decision rationale with citations

7. **Documentation Updates**: Keep project management tracking current
   - Automatic progress log updates
   - State file synchronization

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

### Multi-Agent Orchestration with MCP Tools

The implement command coordinates multiple agents with full MCP integration:

```markdown
Phase 1: Foundation (Research-Driven)
├── Assigns system-architect for infrastructure planning
│   └── Uses mcp__context7 for architecture patterns
├── Coordinates with design-architect for technical specs
│   └── Leverages mcp__searxng for market research
└── Ensures proper handoffs with comprehensive context
    └── Includes all MCP research results and citations

Phase 2: Implementation (Tool-Enabled)
├── Orchestrates backend-architect and frontend-developer
│   ├── Backend uses mcp__context7 for framework docs
│   └── Frontend uses mcp__magic for UI components
├── Manages parallel work streams with dependency awareness
│   └── TodoWrite for real-time progress tracking
└── Maintains quality gates and craftsman standards
    └── Research validation at each checkpoint

Phase 3: Integration (Quality-Focused)
├── Coordinates testing and validation agents
│   └── qa-architect uses mcp__playwright for E2E tests
├── Manages deployment and operational concerns
│   └── devops-architect validates with current best practices
└── Ensures complete delivery against original plan
    └── Final validation with time-stamped documentation
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

### Quality Gate Validation with MCP Tools

Before phase transitions:

```markdown
Quality Gate Checklist:

- [ ] Phase deliverables meet craftsman quality standards
- [ ] All work properly documented with current timestamps (mcp__time)
- [ ] Agent handoffs complete with full context preservation
- [ ] Research validation complete with proper citations (mcp__searxng)
- [ ] Technical decisions backed by current documentation (mcp__context7)
- [ ] Dependencies satisfied for next phase
- [ ] No blocking issues or technical debt introduced
- [ ] Work aligns with original plan intent and success criteria
- [ ] Progress tracked in TodoWrite with status updates
```

### Progress Tracking Integration

```typescript
// Automatic progress tracking during implementation
interface ImplementationProgress {
  overallPercent: number;
  currentPhase: string;
  activeAgents: string[];
  tasksCompleted: number;
  tasksTotal: number;
  qualityGatesPassed: number;
  blockers: string[];
  estimatedCompletion: Date;
}

// Real-time updates via TodoWrite
await updateProgress({
  task: "API endpoint implementation",
  status: "in_progress",
  agent: "backend-architect",
  progress: 65
});
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

### Feature Implementation with Full Workflow

```markdown
# Execute a feature plan with progress tracking
/implement user-authentication

# Real-time coordination:
- Requirements validation with product-architect
  └── MCP research on auth best practices
- Technical specification with design-architect
  └── Architecture patterns from mcp__context7
- Backend implementation with backend-architect
  └── FastAPI patterns and security standards
- Frontend implementation with frontend-developer
  └── UI components from mcp__magic
- Testing coordination with qa-architect
  └── E2E tests via mcp__playwright
- Documentation updates throughout process
  └── Time-stamped with mcp__time

# Progress visibility:
[████████░░] 80% - Backend API complete, frontend in progress
Active: frontend-developer | Task: Login form implementation
Quality Gates: 4/5 passed | ETA: 2 hours
```

### Advanced Usage Examples

```markdown
# Resume interrupted implementation
/implement user-auth --resume
> Resuming from Phase 2, Task 3...
> Previous context restored
> Active agent: backend-architect

# Execute with dry run to preview
/implement payment-integration --dry-run
> Plan validation: ✓ Valid
> Phases: 4 | Agents: 5 | Est. Duration: 6 hours
> Dependencies: Stripe API key required

# Focus on specific phase
/implement data-migration --phase=2
> Executing Phase 2: Schema Migration only
> Prerequisites from Phase 1 validated
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
