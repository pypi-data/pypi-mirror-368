# Time Context Pattern
*Universal time awareness using MCP tools*

**Usage**: Include in agents with `@.claude/agents/common/time-context.md`

---

## Time Context Establishment

**Always start with time context**:
```typescript
// At the beginning of any work session:
const currentTime = await mcp__time__get_current_time({ timezone: "Etc/UTC" });
const workDate = currentTime.datetime; // Use throughout all work
```

## Time Context Usage Patterns

### Document Creation
- **File Naming**: Always use current date in format `[TYPE]-[name]-[YYYY-MM-DD].md`
- **Timestamps**: Use actual datetime from MCP tool, never hardcoded
- **Created/Updated Fields**: Always use current time from tool

### Research Context
- **Search Queries**: Include current year/date for relevant results
- **Market Research**: "as of [current date]" for all market claims
- **Technology Versions**: Research current versions using date context

### State Management
- **Session Tracking**: Log start/end times using MCP time
- **Progress Updates**: Timestamp all progress entries
- **Handoff Timing**: Record exact handoff times

### Git Operations
- **Commit Timestamps**: Automatic, but reference in messages
- **Branch Names**: Can include date for temporal context
- **Archive Dates**: Use current date for archive organization

## Common Time Patterns

```markdown
# Document header
**Created**: [Use datetime from MCP time tool]
**Last Updated**: [Current datetime when updating]

# Progress log entry
### [Current Date] - [Agent Name] Progress
**Time**: [Specific time from MCP tool]

# Research citation
[Source] - [URL] - [Date Accessed: YYYY-MM-DD from MCP tool]

# Archive operation
Archive Date: [Current date from MCP tool]
```

## Integration Pattern
```markdown
# At the start of every agent operation:
1. Use `time` MCP tool to establish current datetime
2. Store datetime for consistent use throughout session
3. Never hardcode dates or timestamps
4. Always use current date for file naming
```

## Quality Gate
- [ ] **Time context established** at start of session
- [ ] **All timestamps** from MCP tool, not hardcoded
- [ ] **File names** include current date
- [ ] **Research** uses current date context
