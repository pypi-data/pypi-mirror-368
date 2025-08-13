# Architecture Decision Record: Agent Framework Choice

**ADR Number**: ADR-001
**Decision Date**: 2025-08-03
**Status**: Accepted
**Deciders**: ClaudeCraftsman Project Team
**Decision Category**: Core Architecture

## Context

ClaudeCraftsman needs to provide SuperClaude workflow patterns within Claude Code's native system. Key considerations:

- SuperClaude users have invested time learning structured workflows
- Claude Code provides native agent support with better performance
- External dependencies create maintenance burden and adoption friction
- Users want enhanced capabilities, not just feature parity

## Decision

Build on Claude Code's native agent framework rather than creating external system.

**Rationale**:
- Native integration provides better performance and reliability
- No external dependencies reduces setup complexity and maintenance burden
- Leverages Claude Code's built-in tools and capabilities
- Enables future enhancements as Claude Code evolves
- Provides path for community adoption within Claude Code ecosystem

## Consequences

### Positive
- Seamless integration with existing Claude Code installations
- Better performance than external orchestration systems
- Reduced maintenance overhead
- Clear upgrade path as Claude Code evolves
- Lower barrier to adoption for Claude Code users

### Negative
- Limited to Claude Code's agent capabilities and constraints
- Cannot implement features requiring external services
- Dependent on Claude Code's architectural decisions
- May require workarounds for advanced coordination features

### Mitigation
- Design within Claude Code's constraints while maximizing capabilities
- Use file-based systems for features requiring persistence
- Plan enhancement requests for Claude Code feature gaps

## References
- Claude Code Agent Documentation: https://docs.anthropic.com/en/docs/claude-code/sub-agents
- SuperClaude Framework Analysis (internal research)

---
**ADR Maintainer**: ClaudeCraftsman Architecture Team
**Last Updated**: 2025-08-03
**Next Review**: Phase 2 Architecture Assessment
