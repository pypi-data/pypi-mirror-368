# State Management Standards
*Universal state management patterns for framework consistency*

**Usage**: Include in agents with `@.claude/agents/common/state-management.md`

---

## Automatic State Management - Keep Framework Current
As a {{AGENT_TYPE}}, you MUST update framework state files to prevent decay:

**Required State Updates:**
1. **When creating any {{DOCUMENT_TYPE}}:**
   - Update `.claude/docs/current/registry.md` with new entry
   - Include: filename, type, location, date, status, purpose

2. **When completing {{WORK_TYPE}} phases:**
   - Update `.claude/context/WORKFLOW-STATE.md` with current phase
   - Update `.claude/project-mgt/06-project-tracking/progress-log.md` with progress

3. **When handing off to next agent:**
   - Update `.claude/context/HANDOFF-LOG.md` with handoff details
   - Create handoff brief in `.claude/context/`

**State Update Process:**
```
# After creating {{DOCUMENT_TYPE}}:
- Read registry.md
- Add new row to active documents table
- Write updated registry.md
- Commit the update

# After completing work:
- Read WORKFLOW-STATE.md
- Update current phase and status
- Write updated file
- Commit the state change
```

## State File Locations
**Core State Files:**
- `.claude/docs/current/registry.md` - Document registry
- `.claude/context/WORKFLOW-STATE.md` - Current workflow status
- `.claude/context/HANDOFF-LOG.md` - Agent handoff history
- `.claude/context/CONTEXT.md` - Project context and decisions
- `.claude/context/SESSION-MEMORY.md` - Session continuity
- `.claude/project-mgt/06-project-tracking/progress-log.md` - Progress tracking

## Registry Update Pattern
```markdown
# Registry Entry Format
| Filename | Type | Location | Date | Status | Purpose |
|----------|------|----------|------|--------|----------|
| {{FILENAME}} | {{DOC_TYPE}} | {{PATH}} | {{DATE}} | Active | {{PURPOSE}} |
```

## Workflow State Update Pattern
```markdown
## Current Workflow Status
**Project**: {{PROJECT_NAME}}
**Current Phase**: {{PHASE_NAME}}
**Active Agent**: {{AGENT_NAME}}
**Phase Progress**: {{PROGRESS}}%
**Last Updated**: {{TIMESTAMP}}

## Phase Details
- **Started**: {{START_TIME}}
- **Expected Completion**: {{TARGET_TIME}}
- **Deliverables**: {{DELIVERABLES}}
- **Blockers**: {{BLOCKERS}}
```

## Handoff Log Update Pattern
```markdown
## Handoff Entry: {{FROM_AGENT}} → {{TO_AGENT}}
**Timestamp**: {{HANDOFF_TIME}}
**Project**: {{PROJECT_NAME}}
**Phase**: {{PHASE_NAME}}

### Work Completed
- {{COMPLETED_ITEMS}}

### Context Transferred
- {{CONTEXT_ITEMS}}

### Next Steps
- {{NEXT_STEPS}}
```

## Progress Log Update Pattern
```markdown
### {{DATE}} - {{AGENT_NAME}} Progress
**Time**: {{TIMESTAMP}}
**Phase**: {{PHASE_NAME}}
**Status**: {{STATUS}}

**Activities Completed**:
- {{ACTIVITY_1}}
- {{ACTIVITY_2}}

**Next Actions**:
- {{NEXT_ACTION_1}}
- {{NEXT_ACTION_2}}
```

## State Update Automation
**Using Framework CLI**:
```bash
# Update document registry
cc state document-created \
  "{{FILENAME}}" "{{DOC_TYPE}}" "{{LOCATION}}" "{{PURPOSE}}"

# Update workflow state
cc state phase-started \
  "{{PHASE_NAME}}" "{{AGENT_NAME}}" "{{DESCRIPTION}}"

# Log handoff
cc state handoff \
  "{{FROM_AGENT}}" "{{TO_AGENT}}" "{{CONTEXT}}"

# Archive document when needed
cc state archive \
  "{{FILENAME}}" "{{REASON}}"
```

## Quality Gates for State Management
- [ ] Registry updated immediately after document creation
- [ ] Workflow state reflects current phase and progress
- [ ] Handoff log complete before agent transition
- [ ] All timestamps from MCP time tool
- [ ] State changes committed with work changes
- [ ] No orphaned documents without registry entries

## Variable Reference
When importing state management, customize these variables:
- `{{AGENT_TYPE}}`: Your agent type (e.g., "product architect")
- `{{DOCUMENT_TYPE}}`: Primary document type (e.g., "document", "PRD", "specification")
- `{{WORK_TYPE}}`: Type of work phases (e.g., "PRD", "design", "implementation")
- `{{DOC_TYPE}}`: Document type for registry (e.g., "PRD", "Tech Spec", "ADR")
- `{{FILENAME}}`, `{{PATH}}`, `{{DATE}}`, `{{PURPOSE}}`: Registry fields
- `{{PROJECT_NAME}}`, `{{PHASE_NAME}}`, `{{AGENT_NAME}}`: Workflow identifiers
- `{{PROGRESS}}`, `{{STATUS}}`, `{{TIMESTAMP}}`: Status indicators
- `{{FROM_AGENT}}`, `{{TO_AGENT}}`: Handoff parties
- Additional context-specific variables as needed

## Common Patterns
```markdown
# Always update state files atomically
1. Read current state
2. Make modifications
3. Write updated state
4. Commit changes immediately

# Never leave state files out of sync
- Document creation → Registry update
- Phase completion → Workflow state update
- Agent handoff → Handoff log update
```
