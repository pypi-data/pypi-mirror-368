# Architecture Decision Records Index
*Master index of all architectural decisions for ClaudeCraftsman*

**Document**: ARCH-DECISION-RECORD.md
**Created**: 2025-08-03
**Last Updated**: 2025-08-03 23:19 UTC
**Version**: 2.0 - Migrated to standalone ADR pattern

## ADR Format and Standards

Each architectural decision is documented in a standalone file following the standard ADR format:
- **Status**: Proposed, Accepted, Deprecated, Superseded
- **Context**: The situation and forces at play
- **Decision**: The chosen solution
- **Consequences**: The results of the decision, both positive and negative

**File Naming Convention**: `ADR-###-[decision-name]-[YYYY-MM-DD].md`
**Location**: `.claude/project-mgt/02-technical-design/`

## Current Architecture Decision Records

| ADR | Decision | Status | Impact | File |
|-----|----------|--------|--------|------|
| [ADR-001](./ADR-001-agent-framework-choice-2025-08-03.md) | Agent Framework Choice | Accepted | High - Architectural foundation | ADR-001-agent-framework-choice-2025-08-03.md |
| [ADR-002](./ADR-002-context-management-strategy-2025-08-03.md) | Context Management Strategy | Accepted | High - Context preservation | ADR-002-context-management-strategy-2025-08-03.md |
| [ADR-003](./ADR-003-research-integration-approach-2025-08-03.md) | Research Integration Approach | Accepted | Medium - Research capabilities | ADR-003-research-integration-approach-2025-08-03.md |
| [ADR-004](./ADR-004-file-organization-standard-2025-08-03.md) | File Organization Standard | Accepted | Medium - Project organization | ADR-004-file-organization-standard-2025-08-03.md |
| [ADR-005](./ADR-005-agent-specialization-strategy-2025-08-03.md) | Agent Specialization Strategy | Accepted | High - Agent capabilities | ADR-005-agent-specialization-strategy-2025-08-03.md |
| [ADR-006](./ADR-006-time-awareness-implementation-2025-08-03.md) | Time Awareness Implementation | Accepted | Low - Time accuracy | ADR-006-time-awareness-implementation-2025-08-03.md |
| [ADR-007](./ADR-007-command-interface-design-2025-08-03.md) | Command Interface Design | Accepted | High - User interface | ADR-007-command-interface-design-2025-08-03.md |
| [ADR-008](./ADR-008-bootstrap-system-design-2025-08-03.md) | Bootstrap System Design | Accepted | High - Framework activation | ADR-008-bootstrap-system-design-2025-08-03.md |

## Decision Categories

### Core Architecture (High Impact)
- **ADR-001**: Agent Framework Choice - Foundation technology decisions
- **ADR-002**: Context Management Strategy - Cross-session state preservation
- **ADR-005**: Agent Specialization Strategy - Agent design and capabilities
- **ADR-007**: Command Interface Design - User interaction patterns
- **ADR-008**: Bootstrap System Design - Framework activation mechanism

### Quality Standards (Medium Impact)
- **ADR-003**: Research Integration Approach - Research-driven development
- **ADR-004**: File Organization Standard - Project structure and naming
- **ADR-006**: Time Awareness Implementation - Current date enforcement

## Decision Review Process

### Quarterly Review Schedule
- **Review Date**: End of each project phase
- **Reviewers**: ClaudeCraftsman Architecture Team
- **Process**: Assess decision outcomes, identify superseding needs
- **Documentation**: Update status and record lessons learned

### Change Management
- **New ADRs**: Require architecture team consensus
- **Superseding**: Must reference original ADR with rationale
- **Deprecation**: Clear migration path required
- **Impact Assessment**: Required for all changes

## ADR Lifecycle

### Proposed → Accepted
- Architecture team review and consensus
- Implementation plan defined
- Quality gates established

### Accepted → Implemented
- Decision implemented in codebase/documentation
- Validation testing completed
- Impact assessment confirmed

### Accepted → Superseded
- New decision addresses changed requirements
- Clear migration path documented
- Original decision marked as superseded

### Accepted → Deprecated
- Decision no longer applicable
- Removal plan documented
- Dependencies identified and addressed

## Quick Reference

### Creating New ADRs
1. **Use next sequential number**: Check current highest number
2. **Follow naming convention**: `ADR-###-[decision-name]-[YYYY-MM-DD].md`
3. **Include all required sections**: Context, Decision, Consequences
4. **Get team review**: Architecture team consensus required
5. **Update this index**: Add entry to table above

### Reviewing Existing ADRs
1. **Check implementation status**: Verify decisions are reflected in code
2. **Assess continued relevance**: Do decisions still serve current needs?
3. **Identify superseding needs**: Have requirements changed significantly?
4. **Document lessons learned**: What worked well, what didn't?

## Standards Migration (2025-08-03)

### What Changed
- **Pattern Shift**: Migrated from combined ADR file to standalone ADR files
- **Numbering Fix**: Resolved ADR-003 conflict between research integration and bootstrap system
- **Organization**: Standardized on individual files with consistent naming
- **Index**: Created this master index for navigation and status tracking

### Migration Actions Completed
- ✅ Extracted all decisions from combined file into individual ADRs
- ✅ Fixed numbering conflict (bootstrap system → ADR-008)
- ✅ Created consistent naming pattern across all ADRs
- ✅ Updated documentation standards to reflect standalone pattern

### Benefits
- **Clear Navigation**: Each decision easily findable and linkable
- **Version Control**: Individual files enable granular change tracking
- **Maintenance**: Easier to update specific decisions without affecting others
- **Standards**: Consistent pattern prevents future numbering conflicts

---

**ADR Index Maintainer**: ClaudeCraftsman Architecture Team
**Next ADR Number**: ADR-009
**Index Review Schedule**: After each new ADR addition

*"Every architectural decision shapes the foundation upon which craftspeople build. Document them with the same care you expect in the code they enable."*
