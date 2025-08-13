# Quality Gates - The Craftsman's Standards
*Universal quality checklist ensuring excellence across all agents*

**Usage**: Include in agents with `@.claude/agents/common/quality-gates.md`

---

**Quality Gates - The {{AGENT_TYPE}}'s Standards:**
Before declaring your {{OUTPUT_TYPE}} complete, ensure:
- [ ] **Used `time` MCP tool** to establish current datetime and used it throughout all work
- [ ] Used "ultrathink" for deep {{ANALYSIS_FOCUS}} analysis
- [ ] **Conducted thorough research** using available MCP tools (`searxng`, `crawl4ai`, `context7`) with current date context
- [ ] **All claims and statements have proper citations** with sources, current timestamps, and footnotes
- [ ] **Created files in proper `.claude/docs/current/` location using actual current date in filename**
- [ ] **Updated document registry with new entries using correct timestamps**
- [ ] **Committed all work to git** using real MCP git operations
- [ ] **Updated all state files** to reflect current status
- [ ] Every {{DELIVERABLE}} serves a genuine {{STAKEHOLDER}} need (validated through current research)
- [ ] The {{OUTPUT}} would make you proud to show another craftsperson

## Additional Domain-Specific Gates
Add any domain-specific quality gates after the universal ones above:
- [ ] {{DOMAIN_SPECIFIC_GATE_1}}
- [ ] {{DOMAIN_SPECIFIC_GATE_2}}
- [ ] {{DOMAIN_SPECIFIC_GATE_3}}

## Variable Reference
When importing quality gates, customize these variables:
- `{{AGENT_TYPE}}`: Your agent type (e.g., "Craftsman", "Architect", "Developer")
- `{{OUTPUT_TYPE}}`: What you're producing (e.g., "PRD", "Technical Specification", "Implementation")
- `{{ANALYSIS_FOCUS}}`: What you analyze deeply (e.g., "stakeholder", "technical", "security")
- `{{DELIVERABLE}}`: Specific deliverable (e.g., "requirement", "design decision", "component")
- `{{STAKEHOLDER}}`: Primary stakeholder (e.g., "user", "developer", "business")
- `{{OUTPUT}}`: Final output (e.g., "specification", "architecture", "code")
- `{{DOMAIN_SPECIFIC_GATE_N}}`: Any additional gates specific to your domain

## Integration Pattern
```markdown
# In your agent file, replace the quality gates section with:
@.claude/agents/common/quality-gates.md

# Then add any domain-specific gates below the import
```
