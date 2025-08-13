---
name: plan
description: Medium-complexity planning command for features that need some analysis but not full design process. Balanced approach between simple addition and comprehensive design.
---

# Plan Command
*Balanced planning for medium-complexity features*

## Usage Patterns
- `/plan [feature]` - Basic feature planning
- `/plan [feature] --scope=medium` - Medium complexity with some research
- `/plan [feature] --quick` - Fast planning with minimal documentation

## When to Use Plan
This command fills the gap between simple `/add` and complex `/design`:

✅ **Use `/plan` for:**
- Features requiring some analysis but not market research
- Multi-step implementations with dependencies
- Enhancements to existing systems
- Coordination between 2-3 components
- When you need a plan but not a full specification

❌ **Use `/add` for simpler tasks:**
- Single component creation
- Clear, straightforward requirements
- No coordination needed

❌ **Use `/design` for complex tasks:**
- Market research required
- Business analysis needed
- Complex multi-system coordination
- Full PRD and specifications required

## Process
1. **Requirements Gathering**: Understand what needs to be built
2. **Lightweight Analysis**: Basic research and constraint identification
3. **Implementation Planning**: Break into phases with dependencies
4. **Resource Planning**: Identify agents/tools needed
5. **Execution Roadmap**: Clear next steps

## Outputs
- **Planning Document**: Single plan file in `.claude/docs/current/plans/`
- **Task Breakdown**: Clear phases and dependencies
- **Resource Requirements**: What agents/tools are needed
- **Next Steps**: Immediate actionable items

## Documentation Approach
**Focused Documentation** (not document sprawl):
- Single planning document per feature
- Clear task breakdown with phases
- Dependencies and resource requirements
- Next steps and success criteria

**No Creation Of:**
- Complex PRDs
- Market research documents
- Multiple handoff briefs
- Extensive BDD scenarios

## File Organization
Plans created by `/plan` are organized as:
```
.claude/docs/current/plans/
├── PLAN-[feature-name]-[date].md
└── [Additional plans as needed]
```

## Planning Template
Plans follow this focused structure:
```markdown
# [Feature] Implementation Plan

## Overview
- **Feature**: [What we're building]
- **Scope**: [What's included/excluded]
- **Timeline**: [High-level phases]

## Requirements
- [Key requirements without extensive analysis]

## Implementation Phases
1. **Phase 1**: [Initial work]
2. **Phase 2**: [Next steps]
3. **Phase 3**: [Final delivery]

## Dependencies
- [What we need before starting]
- [Coordination requirements]

## Success Criteria
- [How we know it's done]

## Next Steps
- [Immediate actionable items]
```

## Quality Standards
- **Actionable**: Plan leads to clear next steps
- **Focused**: Single document, no sprawl
- **Practical**: Implementation-focused, not theoretical
- **Time-Bounded**: Reasonable scope and timeline

## Integration with Other Commands
- **After `/plan`**: Use `/add` for simple components or `/implement` for execution
- **Before `/plan`**: Consider if `/add` would be sufficient for simple tasks
- **Upgrade to `/design`**: If planning reveals complexity requiring full design process

Remember: This is the "goldilocks" command - not too simple, not too complex, just right for most feature development.
