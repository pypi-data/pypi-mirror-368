# ClaudeCraftsman Agents Directory

This directory contains all agents used in the ClaudeCraftsman framework, organized for scalability and maintainability.

## Directory Structure

```
agents/
├── framework/     # Core framework agents (built-in)
├── external/      # External/third-party agents
└── common/        # Shared functionality (future: @imports)
```

## Organization Benefits

1. **Discovery**: All agents remain discoverable by Claude Code
2. **Scalability**: Easy to add new categories (e.g., `custom/`, `experimental/`)
3. **Clarity**: Clear distinction between framework and external agents
4. **DRY Support**: `common/` directory ready for shared imports using `@` syntax

## Agent Categories

### Framework Agents (`framework/`)
Core agents that ship with ClaudeCraftsman:
- product-architect
- design-architect
- system-architect
- backend-architect
- frontend-developer
- workflow-coordinator
- security-architect
- devops-architect
- qa-architect
- data-architect
- ml-architect

### External Agents (`external/`)
Third-party or community-contributed agents:
- python-backend-expert
- (others as added)

### Common Resources (`common/`)
Future location for shared functionality:
- Common prompts
- Shared quality gates
- Reusable templates
- Standard procedures

## Usage

All agents are accessible using the standard Claude Code `@` syntax:
```
@.claude/agents/framework/product-architect.md
@.claude/agents/external/python-backend-expert.md
```

## Future Enhancements

The `common/` directory will support DRY patterns:
```markdown
# In an agent file:
@.claude/agents/common/quality-gates.md
@.claude/agents/common/git-integration.md
```

This structure ensures the framework remains scalable while keeping all agents discoverable and well-organized.
