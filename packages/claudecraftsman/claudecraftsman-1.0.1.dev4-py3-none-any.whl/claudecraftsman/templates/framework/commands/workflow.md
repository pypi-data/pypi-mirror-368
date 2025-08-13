# Workflow Command
*Multi-agent coordination for complex development workflows*

## Command: `/workflow`
**Purpose**: Orchestrate complex multi-agent development workflows with proper coordination
**Philosophy**: Like a master conductor, coordinate multiple craftspeople to create harmonious results

## Usage
```
/workflow [workflow-type] [project-name] [--agents=list] [--mode=sequential|parallel]
```

## Parameters
- **workflow-type**: Type of workflow to execute
  - `design-to-deploy`: Complete feature lifecycle
  - `troubleshoot`: Problem analysis and resolution
  - `refactor`: Code improvement and optimization
  - `feature`: Single feature development
  - `integration`: System integration workflow
- **project-name**: Project or feature being worked on
- **--agents**: Comma-separated list of specific agents to include
- **--mode**:
  - `sequential`: Agents work in sequence with handoffs (default)
  - `parallel`: Agents work simultaneously where possible

## Workflow Templates

### Design-to-Deploy Workflow
**Sequence**: Complete feature development from conception to deployment
```
1. product-architect → PRD and business requirements
   ↓ Handoff: Business context, user research, success metrics
2. design-architect → Technical specification and architecture
   ↓ Handoff: System design, technology choices, integration plans
3. system-architect → High-level implementation strategy
   ↓ Handoff: Code structure, patterns, quality standards
4. [backend-architect + frontend-developer] → Implementation (parallel)
   ↓ Handoff: Working code, tests, documentation
5. context-manager → Final documentation and knowledge capture
```

### Troubleshoot Workflow
**Sequence**: Systematic problem analysis and resolution
```
1. system-architect → Problem analysis with "ultrathink" mode
   ↓ Handoff: Root cause analysis, potential solutions
2. [backend-architect | frontend-developer] → Solution implementation
   ↓ Handoff: Fix implementation, test validation
3. context-manager → Resolution documentation and prevention
```

### Refactor Workflow
**Sequence**: Code improvement with quality focus
```
1. system-architect → Code analysis and improvement opportunities
   ↓ Handoff: Refactoring strategy, quality improvements
2. [backend-architect | frontend-developer] → Code refactoring
   ↓ Handoff: Improved code, maintained functionality
3. context-manager → Refactoring documentation and learnings
```

## Workflow Orchestration Process

### Phase 1: Workflow Planning (workflow-coordinator)
**Actions**:
1. **Time Context**: Use `time` MCP tool for all timestamps
2. **Workflow Analysis**: "Ultrathink about optimal agent sequence and dependencies"
3. **Context Gathering**: Collect all relevant project context
4. **Agent Preparation**: Brief each agent on their role and handoff requirements
5. **Quality Planning**: Define success criteria and quality gates

### Phase 2: Agent Coordination
**For Each Agent in Sequence**:
1. **Context Preparation**: Gather relevant context from previous agents
2. **Agent Briefing**: Provide clear scope, constraints, and success criteria
3. **Work Execution**: Agent performs their specialized work with quality focus
4. **Quality Validation**: Verify craftsman standards met before handoff
5. **Handoff Preparation**: Prepare context and deliverables for next agent

### Phase 3: Handoff Management
**Handoff Protocol for Each Transition**:
```markdown
## Agent Handoff Brief
**From**: [Current Agent]
**To**: [Next Agent]
**Timestamp**: [Current datetime]
**Workflow**: [Workflow type and project]

### Work Completed
- **Deliverables**: [Files created with proper naming and location]
- **Decisions Made**: [Key decisions with rationale]
- **Quality Status**: [Quality gates passed]
- **Research Conducted**: [MCP research with citations]

### Next Phase Context
- **Scope**: [What next agent should accomplish]
- **Constraints**: [Dependencies, limitations, considerations]
- **Success Criteria**: [How to measure successful completion]
- **Files**: [Relevant context files and locations]

### Continuation Requirements
- **Priority Focus**: [Most critical aspects for next agent]
- **Quality Standards**: [Specific craftsman standards to maintain]
- **Integration Notes**: [How work fits with previous phases]
```

## Context Management During Workflow

### Workflow State Tracking
**WORKFLOW-STATE.md Updates**:
```markdown
## Current Workflow Status
**Project**: [Project Name]
**Workflow Type**: [design-to-deploy|troubleshoot|refactor|etc.]
**Started**: [Start timestamp]
**Current Phase**: [Current phase number and description]
**Active Agent**: [Currently working agent]
**Completed Phases**: [List of completed phases with agents]
**Next Milestone**: [Upcoming phase or completion]
**Overall Progress**: [% complete with quality assessment]

## Phase Details
### Phase [N]: [Phase Name]
- **Agent**: [Agent name]
- **Started**: [Phase start time]
- **Status**: [In Progress|Completed|Blocked]
- **Deliverables**: [Expected outputs]
- **Quality Gates**: [Completion criteria]

## Blockers and Issues
- [Any current blockers or concerns]

## Next Actions
- [What needs to happen to progress]
```

### Handoff History
**HANDOFF-LOG.md Updates**:
```markdown
## Workflow Handoff Log: [Project Name]

### Handoff [N]: [From Agent] → [To Agent]
**Timestamp**: [Handoff time]
**Context Transferred**: [Key information passed]
**Deliverables Handed Over**: [Files and work products]
**Next Phase Briefing**: [Scope and expectations]
**Quality Status**: [Standards met confirmation]
```

## Quality Orchestration

### Quality Gates Between Phases
Before any handoff occurs:
- [ ] **Current phase quality standards met**
- [ ] **Deliverables complete and properly named**
- [ ] **Context properly documented for next agent**
- [ ] **Research citations complete and verifiable**
- [ ] **Integration with previous work validated**

### Workflow Completion Criteria
Before marking workflow complete:
- [ ] **All phases successfully completed**
- [ ] **Quality gates passed throughout**
- [ ] **Final deliverables meet craftsman standards**
- [ ] **Documentation complete and organized**
- [ ] **Context preserved for future reference**

## Example Usage

```bash
# Complete feature development workflow
/workflow design-to-deploy user-authentication

# Troubleshoot with specific agents
/workflow troubleshoot payment-gateway --agents=system-architect,backend-architect

# Parallel implementation for complex feature
/workflow feature dashboard-redesign --mode=parallel

# Code refactoring workflow
/workflow refactor legacy-api-endpoints
```

## Integration and Dependencies

### Command Relationships
- **Can initiate**: `/design` for comprehensive planning
- **Can trigger**: `/implement` for specific implementation
- **Coordinates with**: All craftsman agents
- **Updates**: All context files and documentation

### Context File Management
**Files Created/Updated**:
- `.claude/context/WORKFLOW-STATE.md` - Real-time workflow tracking
- `.claude/context/HANDOFF-LOG.md` - Complete handoff history
- `.claude/context/CONTEXT.md` - Project context evolution
- `.claude/docs/registry.md` - Document registry updates

### Success Measurement
**Workflow Success Criteria**:
- All phases completed with quality gates passed
- Seamless handoffs with context preservation
- Deliverables meet craftsman standards
- Documentation organized and complete
- Project objectives achieved with user value delivered

**The Workflow Craftsman's Commitment**:
You orchestrate development workflows not as task execution, but as the careful coordination of skilled artisans. Every transition preserves the intention and quality that defines true craftsmanship, ensuring the final result reflects the care and expertise of all contributors.
