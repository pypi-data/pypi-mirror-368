# Architecture Decision Record: Research Integration Approach

**ADR Number**: ADR-003
**Decision Date**: 2025-08-03
**Status**: Accepted
**Deciders**: ClaudeCraftsman Project Team
**Decision Category**: Research Integration

## Context

Craftsman philosophy requires research-driven decision making. Options:

1. **No Research Integration**: Rely on Claude's built-in knowledge
2. **Manual Research**: Users conduct research separately
3. **MCP Tool Integration**: Use available MCP research tools
4. **Custom Research System**: Build proprietary research system

## Decision

Integrate available MCP tools (searxng, crawl4ai, context7, time) with graceful degradation.

**Implementation**:
- All agents use MCP tools for research when available
- Proper citations with URL, access date, and relevant quotes
- Graceful degradation when MCP tools unavailable
- Research findings cached in context files

**Rationale**:
- MCP tools provide current, verifiable research capabilities
- Citations enable independent verification of claims
- Graceful degradation maintains functionality when tools unavailable
- Cached research reduces redundant API calls

## Consequences

### Positive
- Research-backed specifications with verifiable sources
- Current market and technical information in decisions
- Independent verification possible for all claims
- Reduced risk of outdated or incorrect assumptions

### Negative
- Dependency on MCP server availability
- Research operations add time to agent execution
- Potential for research tool API limitations
- Additional complexity in agent prompts

### Mitigation
- Clear error messages when research tools unavailable
- Research caching to minimize API usage
- Fallback to Claude's knowledge with appropriate disclaimers
- Research tool status monitoring and validation

## References
- MCP Tool Documentation: https://docs.anthropic.com/en/docs/mcp
- Research-Driven Development Best Practices (research conducted 2025-08-03)

---
**ADR Maintainer**: ClaudeCraftsman Architecture Team
**Last Updated**: 2025-08-03
**Next Review**: MCP Tool Integration Validation
