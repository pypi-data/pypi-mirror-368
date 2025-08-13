---
name: design
description: Comprehensive design process for COMPLEX systems requiring market research, competitive analysis, and multi-agent coordination. Use sparingly for high-complexity projects only.
---

# Design Command - Complex Systems Only

_Comprehensive design process for complex, multi-system projects_

## ⚠️ When to Use Design

**ONLY use `/design` for complex systems that require:**

- Market research and competitive analysis
- Business requirements and user research
- Multi-system architecture coordination
- Comprehensive specifications and documentation
- Multiple stakeholder coordination
- Significant technical complexity

## ❌ Don't Use Design For

- Creating single agents (use `/add agent` instead)
- Simple feature additions (use `/plan` instead)
- Straightforward implementations (use `/add` instead)
- Internal tools or components (use `/plan` instead)

## Examples of Appropriate Design Usage

✅ **Good Design Usage:**

- "Multi-tenant SaaS platform with AI integration"
- "Cross-platform mobile app with complex workflow"
- "Enterprise integration system with multiple APIs"
- "New business product requiring market validation"

❌ **Wrong Design Usage:**

- "Create system-architect agent" (use `/add agent` instead)
- "Add new command to framework" (use `/add command` instead)
- "Enhance existing feature" (use `/plan` instead)
- "Fix bug in workflow" (direct fix, no command needed)

## Command Selection Guide

```
Task Complexity Decision Tree:

Simple Task? → /add [type] [name]
├─ Single component
├─ Clear requirements
├─ No coordination needed
└─ Examples: agents, commands, templates

Medium Task? → /plan [feature]
├─ Multi-step implementation
├─ Some coordination required
├─ Need basic analysis
└─ Examples: feature enhancements, integrations

Complex System? → /design [system] --research=deep
├─ Market research needed
├─ Multiple systems involved
├─ Business analysis required
└─ Examples: new products, platforms, major systems
```

## Usage (Complex Systems Only)

```
/design [system-name] --research=deep --scope=system
```

## Design Process (Multi-Agent Coordination)

When `/design` is appropriate, it follows this comprehensive process:

### Phase 1: Business Analysis

**Agent**: product-architect

- Market research using MCP tools
- Competitive analysis and positioning
- User research and persona development
- Business requirements and success metrics

### Phase 2: Technical Specification

**Agent**: design-architect

- System architecture and component design
- Technical requirements and constraints
- Integration patterns and data flows
- Performance and scalability considerations

### Phase 3: Implementation Planning

**Agent**: technical-planner

- Development phases and milestones
- Resource allocation and dependencies
- Risk assessment and mitigation
- Quality gates and acceptance criteria

## Outputs (Complex Systems)

- **PRD**: Comprehensive product requirements document
- **Technical Specification**: Detailed system architecture
- **Implementation Plan**: Phase-based development roadmap
- **BDD Scenarios**: Behavior-driven development specifications
- **Context Preservation**: Handoff logs and workflow state

## Quality Standards (Research-Driven)

- **Market Validation**: All claims backed by current research
- **Technical Feasibility**: Architecture validated against constraints
- **User-Centered**: Based on real user research and needs
- **Implementation Ready**: Clear path from design to delivery

## File Organization (Managed)

Design process creates organized documentation:

```
.claude/docs/current/
├─ PRDs/[system-name]-PRD-[date].md
├─ specs/[system-name]-SPEC-[date].md
├─ plans/[system-name]-PLAN-[date].md
└─ scenarios/[system-name]-BDD-[date].md
```

## Remember: Think Before You Design

Ask yourself:

- Do I need market research for this?
- Does this involve multiple complex systems?
- Am I creating a new product or major platform?
- Do I need comprehensive business analysis?

If the answer is no, use `/add` or `/plan` instead.

## Integration with Simpler Commands

- **After `/design`**: Use `/plan` for specific features within the designed system
- **Before `/design`**: Try `/plan` first - you might not need the full design process
- **Simple components**: Always use `/add` for individual agents, commands, or templates

The design process is powerful but heavy. Use it wisely for truly complex systems that justify the comprehensive approach.
