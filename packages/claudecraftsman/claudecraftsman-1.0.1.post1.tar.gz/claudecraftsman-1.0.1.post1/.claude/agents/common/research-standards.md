# Research and Citation Standards
*Universal research validation and citation format for all agents*

**Usage**: Include in agents with `@.claude/agents/common/research-standards.md`

---

**Research and Citation Standards:**
Every {{CLAIM_TYPE}} must include proper {{VALIDATION_TYPE}}:
```markdown
[{{STATEMENT_TYPE}}]^[1]
{{ADDITIONAL_EVIDENCE_SECTIONS}}

---
**Sources and Citations:**
[1] [{{SOURCE_TYPE}}] - [URL] - [Date Accessed: YYYY-MM-DD] - [Relevant {{EVIDENCE_TYPE}}]
[2] [Additional sources as needed...]

**Research Context:**
- Analysis Date: [Current date from mcp__time__get_current_time]
- {{RESEARCH_DIMENSION_1}}: [{{RESEARCH_DETAIL_1}}]
- {{RESEARCH_DIMENSION_2}}: [{{RESEARCH_DETAIL_2}}]
- {{RESEARCH_DIMENSION_3}}: [{{RESEARCH_DETAIL_3}}]
- Research Tools Used: [mcp__searxng__searxng_web_search, mcp__crawl4ai__md, mcp__context7__get-library-docs]
```

## Variable Reference
When importing research standards, customize these variables:
- `{{CLAIM_TYPE}}`: Type of claim requiring validation (e.g., "architectural decision", "requirement", "implementation choice")
- `{{VALIDATION_TYPE}}`: How to validate (e.g., "validation", "evidence", "benchmarking")
- `{{STATEMENT_TYPE}}`: What you're stating (e.g., "Architectural decision or technology choice", "User requirement", "Security measure")
- `{{SOURCE_TYPE}}`: Type of source (e.g., "Architecture Resource", "User Research", "Security Standard")
- `{{EVIDENCE_TYPE}}`: What evidence provides (e.g., "architectural guidance", "user insights", "compliance requirements")
- `{{ADDITIONAL_EVIDENCE_SECTIONS}}`: Domain-specific evidence sections (e.g., "**Performance Benchmarks**: [...]", "**Security Considerations**: [...]")
- `{{RESEARCH_DIMENSION_N}}`: Research context dimensions (e.g., "Technology Research", "Market Analysis", "User Studies")
- `{{RESEARCH_DETAIL_N}}`: What to include (e.g., "Current versions and capabilities researched", "Competitor analysis", "User feedback")

## Common Evidence Sections
```markdown
# For technical decisions:
**Performance Benchmarks**: [Specific metrics and comparisons]^[2]
**Security Considerations**: [Security implications and mitigation strategies]^[3]

# For business decisions:
**Market Validation**: [Market research and competitive analysis]^[2]
**User Research**: [User studies and feedback]^[3]

# For implementation:
**Best Practices**: [Industry standards and patterns]^[2]
**Testing Evidence**: [Test results and coverage]^[3]
```

## MCP Tool Research Process
```markdown
# Standard Research Workflow:
1. **Establish Time Context**:
   - Use mcp__time__get_current_time for all timestamps

2. **Broad Market/Industry Search**:
   - Tool: mcp__searxng__searxng_web_search
   - Parameters: query with current year, time_range: "month" or "year"

3. **Deep Content Extraction**:
   - Tool: mcp__crawl4ai__md
   - Parameters: url, f: "fit", q: specific extraction query

4. **Technical Documentation**:
   - Step 1: mcp__context7__resolve-library-id
   - Step 2: mcp__context7__get-library-docs

5. **Citation with Tools**:
   - Format: [Source] - [URL] - [Accessed YYYY-MM-DD via {{MCP_TOOL}}]
```

## Integration Pattern
```markdown
# In your agent file, replace the research standards section with:
@.claude/agents/common/research-standards.md

# Then customize for your domain's specific evidence needs
```
