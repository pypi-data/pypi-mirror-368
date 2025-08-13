# Mandatory Context Maintenance Protocol
*Non-negotiable requirements for all ClaudeCraftsman agents*

**Document**: mandatory-context-maintenance.md
**Created**: 2025-08-03
**Version**: 1.0
**Status**: Active

## Overview

This protocol defines **mandatory, non-negotiable requirements** for context maintenance that every ClaudeCraftsman agent must follow. Context maintenance is not optional - it's fundamental to the craftsman approach and ensures project continuity and quality.

## Core Principle

**"No work is complete until context is preserved."**

Every agent session must end with comprehensive context updates. This ensures that future agents (and future sessions) have complete information to continue the craftsman's work without loss of knowledge, decisions, or progress.

## Mandatory Context Files

Every agent must update these files at the end of every work session:

### 1. WORKFLOW-STATE.md (Required)
**Location**: `.claude/context/WORKFLOW-STATE.md`
**Required Updates**:
```markdown
### [Current Date] - [Agent Name] Session
**Agent**: [agent-name]
**Session Type**: [Brief description of work type]
**Work Completed**: [Specific tasks completed]
**Decisions Made**: [Key decisions with rationale]
**Quality Gate Status**: [Pass/Fail with criteria]
**Next Actions**: [Specific next steps]
**Context for Next Agent**: [Critical handoff information]
**Files Created/Modified**: [List with locations]
```

### 2. CONTEXT.md (Required)
**Location**: `.claude/context/CONTEXT.md`
**Required Updates**:
Add new section under appropriate category (Decision History, Research Context, etc.):
```markdown
### [Current Date] - [Agent Name] Context Update
**Research Findings**: [Key insights with proper citations]
**Technical Decisions**: [Architecture/implementation decisions]
**User Requirements**: [New or refined requirements]
**Risk Updates**: [New risks or mitigation strategies]
**Quality Standards Applied**: [How craftsman standards were maintained]
```

### 3. Registry.md (Required)
**Location**: `.claude/docs/current/registry.md`
**Required Updates**:
- Add any documents created during session
- Update "Last Updated" field for modified documents
- Ensure all entries follow naming conventions
- Verify all locations are accurate

### 4. Progress-Log.md (Required)
**Location**: `.claude/project-mgt/06-project-tracking/progress-log.md`
**Required Updates**:
```markdown
### [Current Date] - [Agent Name] Progress
**Phase**: [Current phase name]
**Tasks Completed**:
- [x] [Specific task] - [Brief outcome]
- [x] [Another task] - [Result achieved]

**Quality Metrics**:
- Research backing: [All claims cited: Yes/No]
- File organization: [Standards followed: Yes/No]
- Craftsman quality: [Standards met: Yes/No]

**Blockers Resolved**: [Any issues fixed]
**New Blockers**: [Any new issues discovered]
**Next Session Plan**: [What should happen next]
```

### 5. HANDOFF-LOG.md (Required if handing off)
**Location**: `.claude/context/HANDOFF-LOG.md`
**Required for Agent Transitions**:
```markdown
#### HB-[YYYYMMDD]-[HHMMSS]: [From Agent] → [To Agent]
**Date**: [Current date and time]
**From**: [current agent name]
**To**: [next agent name]
**Handoff Type**: [Planning/Implementation/Testing/etc.]

**Work Completed**: [Comprehensive summary]
**Decisions Made**: [All decisions with rationale]
**Research Findings**: [Key insights with citations]
**Files Created**: [All new files with locations]
**Quality Validation**: [All quality gates passed]
**Context for Next Agent**: [Everything they need to know]
**Next Actions**: [Specific tasks for receiving agent]

**Handoff Brief Quality Check**:
- [ ] Complete work summary provided
- [ ] All decisions documented with rationale
- [ ] Research findings preserved with citations
- [ ] All files listed with correct locations
- [ ] Quality standards confirmed as met
- [ ] Next actions clearly specified
- [ ] Context sufficient for agent to proceed independently
```

## Implementation Protocol

### Start of Session
1. **Read Current Context**: Review WORKFLOW-STATE.md and CONTEXT.md
2. **Check Latest Updates**: Read most recent progress-log.md entries
3. **Verify Current Date**: Use `time` MCP tool for accurate timestamps

### During Work
1. **Document Decisions**: Note key decisions as they're made
2. **Preserve Research**: Save findings with proper citations
3. **Track Progress**: Monitor completion of planned tasks

### End of Session (MANDATORY)
1. **Update All Context Files**: Complete all required updates
2. **Quality Validation**: Verify all craftsman standards met
3. **File Organization Check**: Ensure proper directory structure
4. **Handoff Preparation**: If transitioning to another agent

## Quality Gate Requirements

Before any agent can consider their work complete:

### Context Update Quality Gates
- [ ] **WORKFLOW-STATE.md updated** with current session information
- [ ] **CONTEXT.md updated** with decisions and research findings
- [ ] **registry.md updated** to reflect all document changes
- [ ] **progress-log.md updated** with completed work and progress
- [ ] **HANDOFF-LOG.md updated** if handing off to another agent
- [ ] **All timestamps current** using date from `time` MCP tool
- [ ] **All file locations correct** following .claude/ directory structure
- [ ] **Research properly cited** with verifiable sources
- [ ] **Decisions documented** with clear rationale
- [ ] **Quality standards verified** as met throughout work

### Context Integrity Validation
- [ ] **Information Complete**: All critical information preserved
- [ ] **Context Sufficient**: Next agent can proceed without gaps
- [ ] **Research Verifiable**: All citations enable independent validation
- [ ] **Standards Maintained**: Craftsman quality applied throughout
- [ ] **File Organization**: No documentation sprawl, proper structure

## Enforcement

### Non-Compliance Consequences
**Incomplete Context Updates = Incomplete Work**

If an agent fails to complete context maintenance:
1. **Work Status**: Session marked as incomplete
2. **Handoff Block**: Cannot transition to next agent
3. **Quality Gate Failure**: Cannot proceed to next phase
4. **Context Recovery**: Must return and complete updates

### Recovery Procedures
If context updates are missed:
1. **Immediate Recovery**: Return to incomplete session
2. **Context Reconstruction**: Rebuild missing context from available information
3. **Validation**: Ensure all mandatory updates completed
4. **Quality Check**: Verify craftsman standards maintained

## Templates and Automation

### Context Update Templates
**Location**: `.claude/project-mgt/07-standards-templates/`
- `workflow-state-update-template.md`
- `context-update-template.md`
- `progress-update-template.md`
- `handoff-brief-template.md`

### Automated Validation
Where possible, implement checks:
1. **File Modification Dates**: Verify context files are current
2. **Required Sections**: Check that mandatory sections exist
3. **Citation Format**: Validate research citations are complete
4. **Directory Structure**: Ensure files in correct locations

## Success Metrics

### Context Maintenance Success
- **Update Compliance**: 100% of sessions include context updates
- **Information Integrity**: 0% context loss between agent transitions
- **File Organization**: 100% compliance with .claude/ structure
- **Research Quality**: 100% of claims backed by verifiable citations

### Quality Indicators
- **Context Sufficiency**: Next agents can proceed without information gaps
- **Decision Traceability**: All decisions traceable through context files
- **Progress Visibility**: Current status always clear from context
- **Research Continuity**: Findings preserved and accessible across sessions

## Common Mistakes to Avoid

### Context Update Failures
1. **"I'll update context later"** - Context must be updated immediately
2. **"Brief updates are enough"** - Updates must be comprehensive
3. **"Previous context is sufficient"** - Each session requires updates
4. **"Quality checks slow me down"** - Quality validation is mandatory

### File Organization Errors
1. **Creating files at project root** - Use .claude/ structure
2. **Inconsistent naming** - Follow established conventions
3. **Missing registry updates** - Registry must reflect all changes
4. **Archive confusion** - Current files in current/, old files in archive/

### Research and Citation Gaps
1. **Unsupported claims** - All statements need research backing
2. **Missing citations** - Include source, date, relevant quote
3. **Outdated research** - Use current date context for searches
4. **Unverifiable sources** - Citations must enable independent validation

## Training and Onboarding

### New Agent Requirements
Before any agent begins work:
1. **Protocol Training**: Understand mandatory context maintenance
2. **File Structure**: Master .claude/ directory organization
3. **Quality Standards**: Understand craftsman requirements
4. **Template Usage**: Practice with all required templates

### Ongoing Development
- **Regular Review**: Periodic validation of context maintenance quality
- **Process Improvement**: Refinement based on usage patterns
- **Template Evolution**: Enhancement of templates based on experience
- **Automation Enhancement**: Addition of validation and automated checks

---

**Mandatory Protocol Maintained By**: All ClaudeCraftsman agents
**Compliance Level**: 100% required - no exceptions
**Quality Validation**: Enforced through quality gates
**Review Frequency**: Continuous during all work sessions

*"Context maintenance is not overhead - it's the foundation that enables craftspeople to build upon each other's work with confidence and continuity."*
