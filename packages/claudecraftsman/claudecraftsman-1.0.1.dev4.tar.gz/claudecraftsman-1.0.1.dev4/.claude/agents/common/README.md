# Common Components Library
*Shared patterns and standards for ClaudeCraftsman agents*

## Overview
This directory contains reusable components that implement common patterns across all framework agents. Each component uses a variable substitution pattern to allow customization while maintaining consistency.

## Available Components

### Core Process Components
1. **mandatory-process.md** - Universal 7-step craftsman process
2. **quality-gates.md** - Standard quality checklists
3. **research-standards.md** - Citation and validation patterns
4. **time-context.md** - MCP time tool usage patterns

### Workflow Components
5. **git-integration.md** - Universal Git workflow patterns
6. **file-organization.md** - Standardized file organization
7. **state-management.md** - Framework state update patterns
8. **handoff-protocol.md** - Agent transition standards

## Usage Pattern
Agents import common components using `@` syntax with variable customization:

```markdown
@.claude/agents/common/mandatory-process.md
<!-- Variables for mandatory process:
{{DOMAIN}} = "Requirements"
{{DEEP_ANALYSIS_FOCUS}} = "all stakeholders and their needs"
{{RESEARCH_DOMAIN}} = "market"
... additional variables ...
-->
```

## Variable Substitution
Each component defines variables using `{{VARIABLE_NAME}}` syntax. Agents provide values through HTML comments immediately after the import.

## Benefits
- **Consistency**: All agents follow the same core patterns
- **Maintainability**: Update patterns in one place
- **Customization**: Each agent adapts patterns to its domain
- **Code Reduction**: ~50% reduction in agent file sizes
- **Quality**: Enforces craftsman standards universally

## Component Details

### mandatory-process.md
The universal 7-step craftsman process that all agents follow:
1. Time Context
2. Deep Contemplation
3. Evidence Gathering
4. Context Mastery
5. Stakeholder Empathy
6. Output Craftsmanship
7. Success Vision

### quality-gates.md
Standard quality checklist ensuring:
- Time awareness
- Research validation
- Citation completeness
- File organization
- State management
- Craftsman standards

### research-standards.md
Ensures all claims are:
- Backed by evidence
- Properly cited
- Currently validated
- Contextually relevant

### time-context.md
Mandatory time awareness:
- MCP tool usage
- File naming with dates
- Timestamp accuracy
- No hardcoded dates

### git-integration.md
Universal Git workflow:
- Branch management
- Semantic commits
- Work tracking
- Fallback strategies

### file-organization.md
Consistent file structure:
- Document hierarchy
- Naming conventions
- Registry management
- Archive process

### state-management.md
Framework state consistency:
- Registry updates
- Workflow tracking
- Handoff logging
- Progress management

### handoff-protocol.md
Seamless agent transitions:
- Context preservation
- Brief templates
- Quality validation
- Continuation guidance

## Future Extensions
Planned additions:
- Domain-specific patterns
- MCP tool integration patterns
- Testing standards
- Documentation templates
