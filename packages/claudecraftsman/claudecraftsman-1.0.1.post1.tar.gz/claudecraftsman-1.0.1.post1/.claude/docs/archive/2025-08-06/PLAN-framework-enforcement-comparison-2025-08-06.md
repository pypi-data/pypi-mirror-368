# Framework Enforcement Comparison Plan
*Date: 2025-08-06*

## Overview
- **Feature**: Analyzing ClaudeCraftsman framework enforcement mechanisms
- **Scope**: Compare current CLI implementation with potential Claude Code lifecycle hooks
- **Timeline**: Analysis and recommendations

## Framework Core Principles Analysis

### 1. Mandatory Standards from Framework
The ClaudeCraftsman framework mandates:

#### **Process Enforcement**
1. **Time Awareness**: All dates must use MCP `time` tool
2. **Research Driven**: Claims require MCP tool validation
3. **Citations Required**: All facts need proper attribution
4. **File Organization**: Strict naming conventions
5. **Quality Gates**: Phase-based standards
6. **Agent Coordination**: Context preservation
7. **Intentional Design**: User-focused requirements

#### **Quality Checklist Requirements**
- Used `time` MCP tool throughout
- Conducted research using MCP tools
- All claims have citations
- Files follow naming conventions
- Work reflects user empathy
- Quality meets craftsman standards

#### **State Management Requirements**
- Document registry updates
- Workflow state tracking
- Handoff logs between agents
- Context preservation
- Progress tracking
- Git integration

## Current CLI Implementation Analysis

### Strengths
1. **State Management Commands**
   - `cc state document-created/completed/archive`
   - `cc state phase-started/completed`
   - `cc state handoff`
   - Centralized Python implementation

2. **Validation Commands**
   - `cc validate pre-operation`
   - `cc validate quality`
   - Framework structure checks
   - State currency validation
   - Git cleanliness checks

3. **Benefits**
   - Cross-platform compatibility
   - Better error handling
   - Rich terminal output
   - Testable code

### Gaps in Current Implementation
1. **No Automatic Enforcement**
   - Relies on manual CLI invocation
   - Agent must remember to run commands
   - No prevention of non-compliant actions

2. **Missing Framework Checks**
   - No MCP tool usage validation
   - No citation requirement enforcement
   - No automatic date format checking
   - No research validation

3. **Limited Git Integration**
   - Basic status checks only
   - No automatic commit enforcement
   - No semantic commit validation

## Claude Code Lifecycle Hooks Potential

### Available Hook Events
1. **preToolUse**: Before any tool execution
2. **postToolUse**: After tool execution
3. **userPromptSubmit**: When user submits prompt
4. **sessionStart**: New session initialization

### Proposed Hook Enhancements

#### 1. **Pre-Operation Validation Hook**
```json
{
  "event": "preToolUse",
  "handler": "claudecraftsman hook pre-validate",
  "filter": {
    "tools": ["Write", "Edit", "MultiEdit"],
    "actions": [
      "check-naming-convention",
      "verify-registry-current",
      "validate-workflow-state",
      "ensure-time-context"
    ]
  }
}
```

#### 2. **Post-Operation State Update Hook**
```json
{
  "event": "postToolUse",
  "handler": "claudecraftsman hook post-update",
  "filter": {
    "tools": ["Write", "Edit", "MultiEdit"],
    "actions": [
      "update-registry",
      "track-progress",
      "update-workflow-state",
      "create-git-commit"
    ]
  }
}
```

#### 3. **Research Validation Hook**
```json
{
  "event": "preToolUse",
  "handler": "claudecraftsman hook validate-research",
  "filter": {
    "tools": ["Write"],
    "patterns": ["PRD-*", "SPEC-*", "PLAN-*"],
    "checks": [
      "verify-mcp-tool-usage",
      "validate-citations",
      "check-date-formats"
    ]
  }
}
```

## Implementation Phases

### Phase 1: Enhanced Hook System
1. Implement comprehensive pre/post validation hooks
2. Add automatic state management triggers
3. Create citation and research validators
4. Build naming convention enforcers

### Phase 2: Deterministic Enforcement
1. Block non-compliant operations
2. Auto-generate required state updates
3. Enforce git commit patterns
4. Validate MCP tool usage

### Phase 3: Intelligent Assistance
1. Suggest corrections for violations
2. Auto-fix common issues
3. Provide inline guidance
4. Track compliance metrics

## Dependencies
- Claude Code hook system understanding
- Enhanced CLI hook handlers
- State management integration
- Git operation automation

## Success Criteria
- Framework standards enforced automatically
- No manual intervention required
- 100% compliance with naming conventions
- All state updates happen automatically
- Git history reflects all changes

## Next Steps
1. Design detailed hook specifications
2. Implement enhanced hook handlers
3. Test deterministic enforcement
4. Create compliance reporting
