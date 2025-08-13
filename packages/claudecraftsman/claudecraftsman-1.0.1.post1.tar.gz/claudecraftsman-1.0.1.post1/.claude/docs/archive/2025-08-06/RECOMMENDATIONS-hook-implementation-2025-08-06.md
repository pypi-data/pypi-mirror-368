# Hook Implementation Recommendations
*Date: 2025-08-06*

## Executive Summary

The ClaudeCraftsman framework has excellent principles but enforcement relies on manual CLI commands. Claude Code's lifecycle hooks can transform this into a deterministic, automatic system that ensures 100% compliance with framework standards.

## Key Findings

### Current State Gaps
1. **Manual Enforcement**: All quality gates require explicit CLI invocation
2. **No Prevention**: Non-compliant operations proceed unchecked
3. **State Drift**: Registry and workflow state can become stale
4. **Missing Validations**: No checks for MCP usage, citations, or research

### Hook System Advantages
1. **Automatic Enforcement**: No manual steps required
2. **Pre-Operation Prevention**: Block non-compliant actions
3. **Real-Time State**: Always current documentation
4. **Complete Validation**: All framework requirements checked

## Recommended Hook Implementations

### 1. Essential Enforcement Hooks

#### File Operation Hook
```python
# Hook: preToolUse for Write/Edit/MultiEdit
def pre_file_operation(tool_name: str, args: dict) -> dict:
    """Enforce framework standards before file operations"""

    if tool_name in ["Write", "Edit", "MultiEdit"]:
        filename = args.get("file_path", "")

        # 1. Validate naming convention
        if not validate_naming_convention(filename):
            raise ValueError(f"Filename '{filename}' doesn't follow TYPE-name-YYYY-MM-DD.md format")

        # 2. Check location compliance
        if not is_approved_location(filename):
            raise ValueError(f"Location '{filename}' not in approved directories")

        # 3. Ensure time context exists
        if not has_time_context():
            raise ValueError("No time context established. Use MCP time tool first.")

    return args
```

#### State Management Hook
```python
# Hook: postToolUse for Write/Edit/MultiEdit
def post_file_operation(tool_name: str, result: dict) -> None:
    """Automatically update state after file operations"""

    if tool_name in ["Write", "Edit", "MultiEdit"]:
        filename = result.get("file_path", "")

        # 1. Update document registry
        update_registry(filename, determine_doc_type(filename))

        # 2. Track progress
        log_progress(f"{tool_name} operation on {filename}")

        # 3. Update workflow state
        update_workflow_phase(get_current_phase(), "in_progress")

        # 4. Stage for git commit
        stage_file_for_commit(filename)
```

### 2. Quality Validation Hooks

#### Research Validation Hook
```python
# Hook: preToolUse for Write (PRD/SPEC/PLAN files)
def validate_research_documents(tool_name: str, args: dict) -> dict:
    """Ensure research documents meet quality standards"""

    if tool_name == "Write":
        filename = args.get("file_path", "")
        content = args.get("content", "")

        if is_research_document(filename):
            # 1. Check MCP tool usage
            if not session_used_mcp_tools():
                raise ValueError("Research documents require MCP tool usage (searxng, crawl4ai, context7)")

            # 2. Validate citations
            if not has_valid_citations(content):
                raise ValueError("Missing citations. Use [Statement]^[1] format with sources section")

            # 3. Verify time awareness
            if has_hardcoded_dates(content):
                raise ValueError("Hardcoded dates found. Use MCP time tool for all dates")

    return args
```

### 3. Git Integration Hooks

#### Automatic Commit Hook
```python
# Hook: postToolUse for all file operations
def auto_git_commit(tool_name: str, result: dict) -> None:
    """Create semantic commits automatically"""

    if tool_name in ["Write", "Edit", "MultiEdit", "Bash"]:
        changes = get_staged_changes()

        if changes:
            # Generate semantic commit message
            message = generate_commit_message(tool_name, changes)

            # Create commit
            create_git_commit(message, include_metadata=True)
```

## Implementation Priority

### Phase 1: Core Enforcement (Week 1)
1. **Naming Convention Enforcement**
   - Block non-compliant filenames
   - Suggest corrections
   - Auto-fix common issues

2. **Automatic State Updates**
   - Registry updates on file operations
   - Progress tracking
   - Workflow state management

3. **Basic Git Integration**
   - Auto-stage changes
   - Generate commit messages
   - Track file history

### Phase 2: Quality Validation (Week 2)
1. **MCP Tool Usage Tracking**
   - Monitor tool calls per session
   - Validate usage for documents
   - Generate usage reports

2. **Citation Validation**
   - Pattern matching for citations
   - Source section verification
   - Format validation

3. **Time Context Enforcement**
   - Track MCP time usage
   - Detect hardcoded dates
   - Auto-replace with current dates

### Phase 3: Advanced Features (Week 3)
1. **Intelligent Assistance**
   - Context-aware suggestions
   - Auto-completion for common tasks
   - Learning from patterns

2. **Compliance Reporting**
   - Real-time dashboards
   - Quality metrics
   - Trend analysis

3. **Cross-Session Context**
   - Preserve state between sessions
   - Intelligent handoffs
   - Context reconstruction

## Technical Implementation

### Hook Configuration Enhancement
```json
{
  "version": "2.0",
  "description": "ClaudeCraftsman Framework Hooks - Deterministic Enforcement",
  "hooks": [
    {
      "event": "preToolUse",
      "handler": "claudecraftsman hook enforce-standards",
      "enabled": true,
      "enforcement": {
        "level": "strict",
        "blockNonCompliant": true,
        "autoCorrect": true
      },
      "validations": [
        "naming-convention",
        "file-location",
        "time-context",
        "research-requirements",
        "citation-format"
      ]
    },
    {
      "event": "postToolUse",
      "handler": "claudecraftsman hook update-everything",
      "enabled": true,
      "actions": [
        "update-registry",
        "track-progress",
        "update-workflow",
        "create-commit",
        "update-context"
      ]
    }
  ]
}
```

### CLI Enhancement
```python
# claudecraftsman/hooks/handlers.py
class EnhancedHookHandler:
    def __init__(self):
        self.validator = FrameworkValidator()
        self.enforcer = FrameworkEnforcer()
        self.state_manager = StateManager()

    def enforce_standards(self, event: HookEvent) -> HookResult:
        """Strict enforcement of all framework standards"""

        # Pre-operation validation
        violations = self.validator.validate_all(event)

        if violations:
            # Attempt auto-correction
            if self.enforcer.can_auto_correct(violations):
                event = self.enforcer.auto_correct(event, violations)
            else:
                # Block operation with helpful message
                return HookResult.block(
                    reason=format_violations(violations),
                    suggestions=get_correction_suggestions(violations)
                )

        return HookResult.proceed(event)
```

## Expected Outcomes

### Immediate Benefits
1. **100% Naming Compliance**: No more manual fixes
2. **Always Current State**: Registry never stale
3. **Complete Git History**: Every change tracked
4. **Reduced Cognitive Load**: Framework enforces itself

### Long-Term Benefits
1. **Higher Quality Output**: Standards consistently met
2. **Faster Development**: No manual overhead
3. **Better Collaboration**: Consistent practices
4. **Learning System**: Improves over time

## Conclusion

Implementing these lifecycle hooks will transform ClaudeCraftsman from a manual framework requiring discipline into an automatic system that ensures compliance. This represents a paradigm shift from "you should" to "the system ensures" - the true mark of a craftsman framework.
