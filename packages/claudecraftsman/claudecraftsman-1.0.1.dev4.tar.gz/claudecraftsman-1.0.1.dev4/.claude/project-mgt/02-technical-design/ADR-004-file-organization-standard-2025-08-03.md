# Architecture Decision Record: File Organization Standard

**ADR Number**: ADR-004
**Decision Date**: 2025-08-03
**Status**: Accepted
**Deciders**: ClaudeCraftsman Project Team
**Decision Category**: Project Organization

## Context

SuperClaude users report documentation sprawl as major pain point. Requirements:

- Prevent files created at project root
- Enable long-term project maintainability
- Support multiple project types and scales
- Maintain consistency across all projects

## Decision

Implement comprehensive file organization standard with `.claude/` directory structure.

**Structure**:
```
.claude/
├── agents/                 # Agent definitions
├── commands/              # Command definitions
├── docs/                  # Runtime documentation
│   ├── current/          # Active specifications
│   ├── archive/          # Superseded versions
│   └── templates/        # Working templates
├── specs/                # Technical specifications
├── context/              # Runtime context files
├── templates/            # Reusable templates
└── project-mgt/          # Project management
```

**Naming Convention**: `[TYPE]-[project-name]-[YYYY-MM-DD].md`

**Rationale**:
- Hidden `.claude/` directory prevents project root pollution
- Logical organization enables efficient navigation
- Consistent naming supports automated tools
- Archive system preserves project history
- Template system ensures consistency

## Consequences

### Positive
- Zero documentation sprawl at project root
- Logical, navigable organization structure
- Consistent naming enables automated processing
- Project history preserved through archive system
- Templates ensure consistency across projects

### Negative
- Additional complexity in file management
- Learning curve for new file organization
- Risk of over-organization creating bureaucracy
- Maintenance overhead for directory structure

### Mitigation
- Automated directory creation during setup
- Clear documentation and examples for file organization
- Tools to validate and maintain organization standards
- Balance organization with practical usability

## References
- Documentation Organization Best Practices (research conducted 2025-08-03)
- Project Structure Analysis from Open Source Projects (internal research)

---
**ADR Maintainer**: ClaudeCraftsman Architecture Team
**Last Updated**: 2025-08-03
**Next Review**: Phase 2 Organization Standards Validation
