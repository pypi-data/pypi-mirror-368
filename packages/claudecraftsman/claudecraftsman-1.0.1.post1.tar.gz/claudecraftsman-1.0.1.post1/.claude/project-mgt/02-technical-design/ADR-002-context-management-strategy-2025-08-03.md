# Architecture Decision Record: Context Management Strategy

**ADR Number**: ADR-002
**Decision Date**: 2025-08-03
**Status**: Accepted
**Deciders**: ClaudeCraftsman Project Team
**Decision Category**: Context Management

## Context

Multi-agent workflows require context preservation across agent transitions. Options considered:

1. **In-Memory Context**: Keep context in conversation memory
2. **External Database**: Use external system for context storage
3. **File-Based Context**: Use local files for context persistence
4. **Hybrid Approach**: Combine in-memory and file-based systems

## Decision

Implement file-based context management with structured context files.

**Architecture**:
```
.claude/context/
├── WORKFLOW-STATE.md    # Current workflow and phase status
├── CONTEXT.md           # Project context and accumulated knowledge
├── HANDOFF-LOG.md       # Agent transition history
└── SESSION-MEMORY.md    # Session continuity data
```

**Rationale**:
- File-based system provides persistence across sessions
- No external dependencies maintains system simplicity
- Structured files enable human inspection and debugging
- Version control friendly for project history
- Scalable to large projects through file organization

## Consequences

### Positive
- Context persists across Claude Code sessions
- Human-readable context files enable debugging
- No external dependencies or additional setup
- Version control integration possible
- Context can be manually edited if needed

### Negative
- File I/O overhead for context operations
- Context file management adds complexity
- Potential for context file corruption
- Manual cleanup required for large projects

### Mitigation
- Implement atomic file operations to prevent corruption
- Regular context validation and cleanup procedures
- Clear context file structure and documentation
- Context compression strategies for large projects

## References
- Context Management Best Practices (research conducted 2025-08-03)
- File-based State Management Patterns (internal analysis)

---
**ADR Maintainer**: ClaudeCraftsman Architecture Team
**Last Updated**: 2025-08-03
**Next Review**: Phase 2 Context System Validation
