# Plan: Proper Git Integration Using Claude Code
*Leveraging existing capabilities instead of reinventing*

**Document**: PLAN-git-integration-fix-2025-08-04.md
**Created**: 2025-08-04
**Priority**: High
**Impact**: Enables actual git automation in framework

## Current Situation

The ClaudeCraftsman framework documents extensive git integration that doesn't actually work. Agents claim to make commits, preserve context, and track changes - but none of this happens. Meanwhile, Claude Code already provides:

1. **MCP Git Server**: Full git capabilities through `mcp__git__*` commands
2. **Bash Fallback**: Direct git command execution via `Bash` tool
3. **Proven Patterns**: These tools are already used successfully

## Implementation Strategy

### Use What Already Works

Instead of building custom git integration, agents should use Claude Code's existing capabilities:

```markdown
## Git Operations in Agents

When performing git operations, use Claude Code's built-in capabilities:

1. **Check git status**:
   - Primary: `mcp__git__git_status({ repo_path: "/workspace" })`
   - Fallback: `Bash({ command: "git status" })`

2. **Stage changes**:
   - Primary: `mcp__git__git_add({ repo_path: "/workspace", files: ["path/to/file"] })`
   - Fallback: `Bash({ command: "git add path/to/file" })`

3. **Commit with context**:
   - Primary: `mcp__git__git_commit({ repo_path: "/workspace", message: "feat: detailed message" })`
   - Fallback: `Bash({ command: 'git commit -m "feat: detailed message"' })`

4. **View history**:
   - Primary: `mcp__git__git_log({ repo_path: "/workspace", max_count: 10 })`
   - Fallback: `Bash({ command: "git log --oneline -n 10" })`
```

### Agent Update Requirements

Each agent needs updates to actually use git operations:

1. **product-architect**: Commit after creating PRD
2. **design-architect**: Commit after technical specs
3. **workflow-coordinator**: Commit at each handoff
4. **All implementation agents**: Commit after significant work

### Example Agent Git Integration

```markdown
# In any agent after completing work:

## Git Integration
After completing [specific work], I'll commit the changes:

<check_status>
Using mcp__git__git_status to see what changed...
</check_status>

<stage_files>
Using mcp__git__git_add to stage:
- New PRD document
- Updated registry
- Context files
</stage_files>

<commit_work>
Using mcp__git__git_commit with message:
"docs(prd): create comprehensive PRD for [project]

- Added business requirements with market research
- Defined success metrics and KPIs
- Created BDD scenarios for validation
- Updated document registry

Crafted by: product-architect
Phase: requirements-gathering"
</commit_work>
```

### State Management Integration

Combine git operations with state updates:

1. **Before major work**: Check git status, ensure clean state
2. **During work**: Track files created/modified
3. **After work**: Commit changes, update state files
4. **At handoffs**: Ensure all changes committed before transition

### Benefits of This Approach

1. **Already Works**: No new implementation needed
2. **Reliable**: Claude Code's git integration is proven
3. **Flexible**: MCP when available, Bash as fallback
4. **Maintainable**: Using standard tools, not custom code
5. **Discoverable**: Other Claude Code users understand it

## Implementation Steps

### Phase 1: Update Core Agents (Immediate)
1. Add git operations to product-architect
2. Add git operations to design-architect
3. Add git operations to workflow-coordinator
4. Test with real commits

### Phase 2: Update All Agents (Day 1)
1. Add git integration to all implementation agents
2. Ensure consistent commit message format
3. Include phase and quality information
4. Test multi-agent workflows

### Phase 3: Documentation Reality (Day 2)
1. Update agent docs to show actual git usage
2. Remove fictional git service references
3. Add examples of MCP + Bash patterns
4. Create git troubleshooting guide

### Phase 4: State + Git Integration (Day 3)
1. Combine state updates with commits
2. Use commit messages for context
3. Track work through git history
4. Enable git-based progress tracking

## Success Criteria

- [ ] Agents actually make commits during work
- [ ] Commit messages include context and phase
- [ ] Git history reflects development progress
- [ ] State files reference recent commits
- [ ] Documentation matches implementation

## Common Patterns

### Pattern 1: Document Creation
```javascript
// After creating document
await mcp__git__git_add({
  repo_path: "/workspace",
  files: ["path/to/new-doc.md"]
});
await mcp__git__git_commit({
  repo_path: "/workspace",
  message: "docs(type): create [description]\n\nAgent: [name]\nPhase: [phase]"
});
```

### Pattern 2: Multi-file Update
```javascript
// After updating multiple files
await mcp__git__git_add({
  repo_path: "/workspace",
  files: ["file1.md", "file2.md", "registry.md"]
});
await mcp__git__git_commit({
  repo_path: "/workspace",
  message: "feat: [comprehensive description]"
});
```

### Pattern 3: Handoff Commit
```javascript
// At agent handoff
await mcp__git__git_commit({
  repo_path: "/workspace",
  message: "chore(handoff): from [agent1] to [agent2]\n\nCompleted: [work]\nNext: [planned]"
});
```

## Conclusion

The solution is simple: use Claude Code's existing git capabilities instead of pretending to have custom integration. This makes the framework actually work while being honest about how it works.

---
*"The best code is often the code you don't write - use what already works."*
