# Common Components Extraction Implementation Plan
**STATUS: IMPLEMENTED ✅** - Completed 2025-08-05

## Overview
- **Feature**: Extract repeated patterns from agents into shared components in `.claude/agents/common/`
- **Scope**: Identify and implement DRY patterns across all framework agents using `@` imports
- **Timeline**: 3 phases over 2-3 days
- **Implementation**: Successfully completed all phases with 14 common components created

## Requirements
- Analyze all framework agents for repeated patterns
- Create modular, reusable components in `common/` directory
- Implement `@` import pattern for shared functionality
- Maintain backward compatibility with existing agents
- Ensure no loss of functionality or quality

## Current State Analysis

### Repeated Patterns Identified
1. **Mandatory Process Sections** - All agents have 7-step process
2. **Quality Gates** - Identical checklists across agents
3. **Git Integration** - Same git workflow in every agent
4. **File Organization** - Repeated directory structure guidance
5. **State Management** - Common update requirements
6. **Research Standards** - Same citation format everywhere
7. **Handoff Protocols** - Identical context transfer process
8. **Time Context** - Same MCP time tool usage pattern

### Existing Standards to Leverage
- `.claude/project-mgt/07-standards-templates/` has templates
- `.claude/standards/git-workflow.md` has git standards
- `.claude/scripts/` has state management utilities
- Framework already has established patterns

## Implementation Phases

### Phase 1: Core Process Components (Day 1)
**Objective**: Extract fundamental craftsman processes

1. **Create Common Process Files**:
   - `common/mandatory-process.md` - 7-step craftsman process
   - `common/quality-gates.md` - Universal quality checklists
   - `common/research-standards.md` - Citation and research requirements
   - `common/time-context.md` - MCP time tool usage pattern

2. **Define Import Syntax**:
   ```markdown
   # In agent files:
   @.claude/agents/common/mandatory-process.md
   @.claude/agents/common/quality-gates.md
   ```

3. **Test with One Agent**:
   - Refactor `product-architect.md` as proof of concept
   - Validate functionality remains intact
   - Document any issues or improvements

### Phase 2: Workflow Components (Day 2)
**Objective**: Extract workflow and integration patterns

1. **Create Workflow Components**:
   - `common/git-integration.md` - Standard git operations
   - `common/file-organization.md` - Directory structure standards
   - `common/state-management.md` - Context update requirements
   - `common/handoff-protocol.md` - Agent transition process

2. **Integration Patterns**:
   - `common/mcp-tools.md` - Standard MCP tool usage
   - `common/agent-coordination.md` - Inter-agent communication
   - `common/documentation-standards.md` - Doc creation patterns

3. **Refactor Additional Agents**:
   - Apply to `design-architect.md` and `workflow-coordinator.md`
   - Validate cross-agent consistency
   - Test handoff mechanisms

### Phase 3: Domain-Specific Extraction (Day 3)
**Objective**: Create specialized shared components

1. **Domain Components**:
   - `common/architect-standards.md` - Shared by architect agents
   - `common/implementation-standards.md` - Developer agent patterns
   - `common/quality-standards.md` - QA and testing patterns
   - `common/infrastructure-standards.md` - DevOps patterns

2. **Utility Components**:
   - `common/templates/` - Reusable document templates
   - `common/examples/` - Standard code examples
   - `common/validation/` - Quality validation scripts

3. **Complete Agent Migration**:
   - Refactor all remaining framework agents
   - Ensure consistency across the board
   - Document the new structure

## Dependencies
- Existing agent files remain functional during transition
- Git history preserved for all changes
- Framework state management scripts updated to recognize imports
- Documentation updated to reflect new patterns

## Success Criteria
- [ ] All repeated patterns extracted to `common/`
- [ ] Every framework agent uses `@` imports for shared content
- [ ] No loss of functionality in any agent
- [ ] Code reduction of 40-60% in agent files
- [ ] Clear documentation of import patterns
- [ ] Easier maintenance and updates going forward

## Benefits Analysis

### Immediate Benefits
1. **DRY Compliance**: Eliminate 70%+ of duplicated content
2. **Easier Updates**: Change once, apply everywhere
3. **Consistency**: Guaranteed identical processes across agents
4. **Smaller Files**: Agent files focus on unique expertise only

### Long-term Benefits
1. **Scalability**: New agents inherit common patterns automatically
2. **Maintainability**: Single source of truth for standards
3. **Quality**: Easier to enforce and update standards
4. **Onboarding**: New contributors understand patterns faster

## Risk Mitigation
- **Backward Compatibility**: Keep original content during transition
- **Testing**: Validate each agent after refactoring
- **Rollback Plan**: Git history allows easy reversion
- **Gradual Migration**: Phase approach reduces risk

## Next Steps
1. Create `common/` subdirectory structure
2. Extract first component (`mandatory-process.md`)
3. Test with `product-architect.md` refactoring
4. Document import pattern for other agents
5. Create migration checklist for systematic conversion

## Technical Considerations

### Import Resolution
```markdown
# Current (duplicated in every agent):
**Mandatory Craftsman Process - The Art of [Domain]:**
1. **Time Context**: Use `time` MCP tool...
[... 20+ lines repeated ...]

# After extraction:
@.claude/agents/common/mandatory-process.md
```

### Variable Substitution Pattern
```markdown
# In common/mandatory-process.md:
**Mandatory Craftsman Process - The Art of {{DOMAIN}}:**

# In agent file:
@.claude/agents/common/mandatory-process.md[DOMAIN="Product Requirements"]
```

### Validation Script
Create `validate-imports.sh` to verify all imports resolve correctly.

## Measurement
- **Before**: ~500 lines per agent × 11 agents = 5,500 lines
- **After Target**: ~150 lines per agent × 11 agents = 1,650 lines
- **Common Components**: ~1,000 lines shared
- **Net Reduction**: 2,850 lines (52% reduction)

---
*Plan created: 2025-08-04 16:31 UTC*
