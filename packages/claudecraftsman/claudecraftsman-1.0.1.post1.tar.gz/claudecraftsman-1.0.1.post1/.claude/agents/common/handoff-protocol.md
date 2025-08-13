# Handoff Protocol Standards
*Universal agent handoff patterns for seamless transitions*

**Usage**: Include in agents with `@.claude/agents/common/handoff-protocol.md`

---

## Handoff Protocol
After completing {{WORK_TYPE}}:
1. **Brief {{NEXT_AGENT_TYPE}} craftspeople** with {{KEY_CONTEXT}} and rationale
2. **Highlight critical {{DECISION_TYPE}}** requiring careful attention
3. **Identify {{RISK_TYPE}} risks** and recommended approaches
4. **Establish quality standards** for {{NEXT_PHASE_TYPE}}
5. **Prepare context files** for seamless handoff

## Craftsman Handoff Brief Template
```markdown
## Craftsman Handoff Brief
**From**: {{CURRENT_AGENT}}
**To**: {{NEXT_AGENT}}
**Timestamp**: [Current datetime from time MCP tool]
**Project**: {{PROJECT_NAME}}

### Context Summary
**Work Completed**: {{COMPLETED_WORK_DESC}}
**Decisions Made**: {{KEY_DECISIONS}}
**Artifacts Created**: {{CREATED_ARTIFACTS}}
**Research Conducted**: {{RESEARCH_SUMMARY}}

### Next Phase Briefing
**Scope**: {{NEXT_PHASE_SCOPE}}
**Constraints**: {{CONSTRAINTS_AND_DEPENDENCIES}}
**Quality Standards**: {{QUALITY_EXPECTATIONS}}
**Context Files**: {{RELEVANT_FILES}}

### Continuation Instructions
**Priority Focus**: {{PRIORITY_ITEMS}}
**Success Metrics**: {{SUCCESS_MEASUREMENT}}
**Handoff Trigger**: {{NEXT_HANDOFF_CONDITION}}
```

## Context File Management
**Essential Handoff Files**:
- **WORKFLOW-STATE.md**: Current phase, active agents, completion status
- **HANDOFF-LOG.md**: History of all agent transitions with timestamps
- **CONTEXT.md**: Project context, decisions, and rationale
- **SESSION-MEMORY.md**: Session continuity and important carry-forward information

## Handoff Process Steps
1. **Complete Current Work**
   - Ensure all quality gates passed
   - Commit all changes with meaningful messages
   - Update state files to reflect completion

2. **Prepare Handoff Context**
   - Gather all relevant work products
   - Document key decisions and rationale
   - Identify critical information for next agent

3. **Create Handoff Brief**
   - Use template above with all variables filled
   - Include specific guidance for next phase
   - Highlight any blockers or concerns

4. **Update State Files**
   - Update HANDOFF-LOG.md with transition details
   - Update WORKFLOW-STATE.md with new active agent
   - Commit handoff brief to `.claude/context/`

5. **Verify Handoff**
   - Ensure all context preserved
   - Confirm next agent has clear direction
   - Validate no information lost in transition

## Handoff Quality Gates
Before completing any handoff:
- [ ] **Current work complete** with quality standards met
- [ ] **All artifacts documented** and properly located
- [ ] **Key decisions recorded** with rationale
- [ ] **Context files updated** with current state
- [ ] **Handoff brief created** with comprehensive information
- [ ] **Next agent prepared** with clear scope and success criteria
- [ ] **Git commits complete** for all work and handoffs

## Variable Reference
When importing handoff protocol, customize these variables:
- `{{WORK_TYPE}}`: Type of work being completed (e.g., "PRD", "technical specification")
- `{{NEXT_AGENT_TYPE}}`: Type of next agent (e.g., "implementation", "design")
- `{{KEY_CONTEXT}}`: Key context to transfer (e.g., "business requirements", "architectural decisions")
- `{{DECISION_TYPE}}`: Type of decisions (e.g., "technical", "business", "architectural")
- `{{RISK_TYPE}}`: Type of risks (e.g., "implementation", "integration", "performance")
- `{{NEXT_PHASE_TYPE}}`: Next phase work type (e.g., "code craftsmanship", "system design")
- `{{CURRENT_AGENT}}`: Current agent name
- `{{NEXT_AGENT}}`: Next agent name
- `{{PROJECT_NAME}}`: Project identifier
- Additional context-specific variables for handoff brief template

## Common Handoff Patterns

### Product to Design Handoff
```markdown
**Key Context**: Business requirements, user research, success metrics
**Critical Items**: User personas, market positioning, core features
**Next Focus**: Technical architecture aligning with business goals
```

### Design to Implementation Handoff
```markdown
**Key Context**: System architecture, technology choices, integration points
**Critical Items**: API contracts, data models, security requirements
**Next Focus**: Code implementation following architectural patterns
```

### Implementation to QA Handoff
```markdown
**Key Context**: Implemented features, test coverage, known issues
**Critical Items**: Test scenarios, edge cases, performance targets
**Next Focus**: Comprehensive testing and quality validation
```

## Integration Example
```markdown
@.claude/agents/common/handoff-protocol.md
<!-- Variables for handoff protocol:
{{WORK_TYPE}} = "technical specification"
{{NEXT_AGENT_TYPE}} = "implementation"
{{KEY_CONTEXT}} = "architectural decisions"
{{DECISION_TYPE}} = "technical"
{{RISK_TYPE}} = "implementation"
{{NEXT_PHASE_TYPE}} = "code craftsmanship"
-->
```
