# MCP Tools Integration Standards
*Universal patterns for MCP tool usage across all agents*

**Usage**: Include in agents with `@.claude/agents/common/mcp-tools.md`

---

## Core MCP Tools

### Time Tool (Mandatory)
**Tool**: `mcp__time__get_current_time`
**Purpose**: Establish current datetime for all work
**Usage Pattern**:
```typescript
// Always at the beginning of any work:
const currentTime = await mcp__time__get_current_time({ timezone: "Etc/UTC" });
const workDate = currentTime.datetime;
```

### Research Tools
**Primary Research Stack**:
1. **mcp__searxng__searxng_web_search**: General web search for current information
2. **mcp__crawl4ai__md**: Deep web content extraction and analysis
3. **mcp__context7__get-library-docs**: Library documentation and code patterns

**Research Pattern**:
```markdown
Research {{RESEARCH_DOMAIN}} using MCP tools:
- mcp__searxng__searxng_web_search: Current {{SEARCH_TARGET}} and industry trends
- mcp__crawl4ai__md: Deep analysis of {{CRAWL_TARGET}}
- mcp__context7__get-library-docs: {{LIBRARY_TARGET}} documentation and patterns
```

## Research Integration Patterns

### Market Research
```markdown
**Market Analysis** (using mcp__searxng__searxng_web_search with current date context):
- Tool Call: mcp__searxng__searxng_web_search
  - query: "{{MARKET_QUERY}} [current year] trends"
  - time_range: "month" or "year"
  - language: "en"
- Focus: {{MARKET_FOCUS}}
- Validation: Cross-reference multiple sources
```

### Technical Research
```markdown
**Technical Investigation** (using mcp__context7__get-library-docs and mcp__crawl4ai__md):
- Step 1: Resolve Library ID
  - Tool: mcp__context7__resolve-library-id
  - libraryName: "{{LIBRARY_NAME}}"
- Step 2: Get Documentation
  - Tool: mcp__context7__get-library-docs
  - context7CompatibleLibraryID: "[resolved-id]"
  - topic: "{{TECH_TOPIC}}"
  - tokens: 15000
- Step 3: Extract Web Resources
  - Tool: mcp__crawl4ai__md
  - url: "{{TECH_RESOURCE_URL}}"
  - f: "fit"
  - q: "{{EXTRACTION_QUERY}}"
- Validation: Verify with current version information
```

### User Research
```markdown
**User Insights** (using mcp__searxng__searxng_web_search and mcp__crawl4ai__md):
- Search Phase:
  - Tool: mcp__searxng__searxng_web_search
  - query: "{{USER_QUERY}} user experience studies [current year]"
  - time_range: "month"
- Deep Analysis:
  - Tool: mcp__crawl4ai__md
  - url: "[relevant study URL]"
  - f: "fit"
- Validation: Current user behavior patterns
```

## MCP Tool Usage Standards

### Research Workflow
1. **Time Context First**: Always establish current datetime with mcp__time__get_current_time
2. **Broad Search**: Start with mcp__searxng__searxng_web_search for overview
3. **Deep Dive**: Use mcp__crawl4ai__md for detailed extraction
4. **Technical Docs**: Use mcp__context7__get-library-docs for library specifics
5. **Citation**: Document all sources with access dates

### Quality Standards for MCP Usage
- [ ] mcp__time__get_current_time used at session start
- [ ] Research includes current date context
- [ ] Multiple sources consulted for validation
- [ ] All findings properly cited with timestamps
- [ ] Tool failures handled gracefully

### Error Handling
```markdown
**MCP Tool Fallbacks**:
- mcp__searxng__searxng_web_search unavailable → Use WebSearch or manual research
- mcp__crawl4ai__md fails → Try direct WebFetch or document findings
- mcp__context7__get-library-docs timeout → Use cached knowledge with disclaimer
- mcp__time__get_current_time fails → Document with system time and note
```

## Citation Standards with MCP Tools
```markdown
**Source Citation Format**:
[Statement requiring evidence]^[1]

---
**Sources and Citations:**
[1] [Source Name] - [URL] - [Accessed: {{DATE}} via {{MCP_TOOL}}] - [Key Finding]
```

## Integration with Research Standards
This component works with `@.claude/agents/common/research-standards.md` to ensure:
- Consistent citation format
- Proper source validation
- Current information usage
- Evidence-based claims

## Variable Reference
When importing MCP tools integration, customize these variables:
- `{{RESEARCH_DOMAIN}}`: Your research focus (e.g., "market conditions", "technologies")
- `{{SEARCH_TARGET}}`: What to search for (e.g., "competitor solutions", "best practices")
- `{{CRAWL_TARGET}}`: Deep dive targets (e.g., "technical documentation", "user reviews")
- `{{LIBRARY_TARGET}}`: Specific libraries/frameworks to research
- `{{MARKET_QUERY}}`, `{{TECH_STACK}}`, `{{USER_QUERY}}`: Specific search queries
- `{{MARKET_FOCUS}}`, `{{TECH_DOMAIN}}`: Research focus areas
- `{{MCP_TOOL}}`: Which tool was used (searxng, crawl4ai, context7)
- `{{DATE}}`: Current date from time tool

## Common MCP Tool Patterns

### For Product Research
```markdown
@.claude/agents/common/mcp-tools.md
<!-- Variables:
{{RESEARCH_DOMAIN}} = "market conditions and competitor landscape"
{{SEARCH_TARGET}} = "competitor products and market trends"
{{MARKET_QUERY}} = "[product category] market analysis"
-->
```

### For Technical Research
```markdown
@.claude/agents/common/mcp-tools.md
<!-- Variables:
{{RESEARCH_DOMAIN}} = "technical architectures and patterns"
{{LIBRARY_TARGET}} = "React, Node.js, PostgreSQL"
{{TECH_DOMAIN}} = "microservices architecture"
-->
```

### For Quality Research
```markdown
@.claude/agents/common/mcp-tools.md
<!-- Variables:
{{RESEARCH_DOMAIN}} = "testing methodologies and tools"
{{SEARCH_TARGET}} = "BDD/TDD best practices"
{{TECH_STACK}} = "Jest, Cypress, Playwright"
-->
```
