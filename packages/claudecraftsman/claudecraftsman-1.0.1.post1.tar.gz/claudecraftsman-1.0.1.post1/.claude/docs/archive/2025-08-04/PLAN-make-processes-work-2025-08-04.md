# Plan: Make Framework Processes Actually Work
*Transform beautiful documentation into functional automation*

**Created**: 2025-08-04 15:21:15 UTC
**Status**: Active
**Type**: Process Automation Implementation
**Priority**: Critical

## Problem Statement

The ClaudeCraftsman framework has a fundamental gap: beautiful documentation describes ideal processes that don't actually work. Every agent claims to do things automatically that require manual intervention. This plan addresses making the documented processes actually functional.

## Root Causes

1. **Design vs Implementation Gap**: Agents describe processes they don't implement
2. **Manual Everything**: Despite automation claims, everything is manual
3. **No Enforcement**: Quality gates exist only in documentation
4. **State Decay**: State files become stale immediately after creation
5. **Fictional Integration**: Git operations described but never executed

## Success Criteria

- [ ] Agents actually perform their documented git operations
- [ ] Archive process happens automatically when documents complete
- [ ] State files update automatically during operations
- [ ] Quality gates actually prevent bad operations
- [ ] Framework uses its own processes (dogfooding works)

## Implementation Plan

### Phase 1: Git Integration Reality (Use What Exists)

**Objective**: Make agents actually use Claude Code's git capabilities

**Approach**:
- Use existing MCP git server when available
- Fall back to Bash git commands when needed
- No custom implementation - use what Claude Code provides

**Changes Required**:

1. **Update Core Agents** to actually use git:
   ```typescript
   // Instead of fictional git service
   // Use actual MCP or Bash
   await mcp__git__git_add({ files: [filePath] });
   await mcp__git__git_commit({
     message: "feat(agent): implement feature X",
     repo_path: "."
   });
   ```

2. **Agent Updates Needed**:
   - `product-architect`: Commit PRDs when created
   - `design-architect`: Commit tech specs
   - `workflow-coordinator`: Track handoffs in git
   - `system-architect`: Commit architectural decisions
   - All implementation agents: Commit their work

3. **Validation**: Each agent must demonstrate real git usage

### Phase 2: Automatic State Management

**Objective**: State files that actually stay current

**Implementation**:

1. **Hook Into Operations**:
   - When documents created → Update registry
   - When phases complete → Update workflow state
   - When handoffs occur → Update handoff log
   - When sessions end → Update session memory

2. **State Update Functions**:
   ```bash
   # Create simple utilities that agents actually call
   update-registry() {
     # Add entry to registry with current timestamp
   }

   update-workflow-state() {
     # Update current phase and status
   }
   ```

3. **Enforcement**: Operations fail if state not updated

### Phase 3: Working Archive Process

**Objective**: Documents actually get archived when complete

**Implementation**:

1. **Completion Triggers**:
   - Plan marked complete → Auto-archive
   - Implementation finished → Auto-archive
   - Document superseded → Auto-archive

2. **Archive Automation**:
   ```bash
   # Hook into document completion
   complete-document() {
     local doc="$1"
     local reason="$2"

     # Archive automatically
     ./.claude/scripts/archive-document.sh "$doc" "$reason"

     # Update registry
     update-registry-archived "$doc" "$reason"
   }
   ```

3. **Integration Points**:
   - Commands check and archive on completion
   - Agents archive superseded documents
   - Workflow coordinator archives at phase end

### Phase 4: Quality Gate Enforcement

**Objective**: Quality gates that actually block bad operations

**Implementation**:

1. **Pre-Operation Checks**:
   ```bash
   # Before any operation
   validate-operation() {
     check-time-context || fail "No time context"
     check-research-done || fail "No research conducted"
     check-file-location || fail "Wrong file location"
     check-naming-convention || fail "Bad naming"
   }
   ```

2. **Enforcement Points**:
   - Document creation requires validation
   - Handoffs require context verification
   - Commits require quality checks
   - Archives require completion status

3. **Failure Handling**: Operations abort with clear errors

### Phase 5: Framework Self-Usage (Dogfooding)

**Objective**: Framework actually uses its own processes

**Implementation**:

1. **This Plan as Test Case**:
   - Created with proper naming ✓
   - Will be archived when complete
   - State files will be updated
   - Git commits will track progress

2. **Ongoing Validation**:
   - Every framework operation uses framework
   - No manual workarounds allowed
   - Failures indicate process gaps

3. **Success Metrics**:
   - Zero manual operations for framework tasks
   - All state files current without intervention
   - Git history tells complete story

## Technical Approach

### Use Existing Tools
- **Git**: MCP server with Bash fallback (no custom implementation)
- **File Operations**: Claude Code's native capabilities
- **State Management**: Simple bash utilities
- **Archive Process**: Existing script with automation hooks

### Implementation Order
1. Git integration (biggest impact)
2. State management (prevents decay)
3. Archive automation (closes loops)
4. Quality enforcement (prevents regression)
5. Self-validation (ongoing verification)

## Validation Plan

### Phase Validation
Each phase must demonstrate:
- [ ] Documented behavior actually works
- [ ] No manual intervention required
- [ ] State files remain current
- [ ] Git history accurate

### Integration Testing
- [ ] Create document → Automatic git commit
- [ ] Complete plan → Automatic archive
- [ ] Agent handoff → State updates
- [ ] Quality failure → Operation blocked

### Success Demonstration
The completion of this plan itself must:
1. Archive automatically
2. Update all state files
3. Create proper git history
4. Require zero manual cleanup

## Risk Mitigation

### Risks
1. **Complexity Creep**: Adding elaborate systems
   - **Mitigation**: Use existing tools only

2. **Breaking Changes**: Disrupting current usage
   - **Mitigation**: Incremental implementation

3. **Performance Impact**: Slowing operations
   - **Mitigation**: Lightweight automation only

## Definition of Done

This plan is complete when:
- [ ] All agents use real git operations
- [ ] Documents archive automatically
- [ ] State files stay current
- [ ] Quality gates actually enforce
- [ ] This plan archives itself automatically
- [ ] Zero manual operations required

## Next Steps

1. Start with git integration in one agent
2. Test and validate the approach
3. Roll out to all agents systematically
4. Implement state management hooks
5. Add archive automation
6. Enforce quality gates
7. Validate through self-usage

---

*"The best framework is one that practices what it preaches."*
