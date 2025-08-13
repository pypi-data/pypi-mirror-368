# Git Integration Standards
*Universal Git workflow and operations for all agents*

**Usage**: Include in agents with `@.claude/agents/common/git-integration.md`

---

## Git Integration - Version Control Excellence
As a {{AGENT_TYPE}}, you maintain Git awareness throughout your work using Claude Code's actual git capabilities:

**Real Git Operations You Must Perform:**
- **Branch Creation**: Create feature branches for {{WORK_TYPE}} work
- **Semantic Commits**: Commit each significant {{SECTION_TYPE}} with meaningful messages
- **Documentation Tracking**: All {{OUTPUT_TYPE}} versions tracked with proper commit history

**Actual Git Workflow for {{WORK_ARTIFACT}}:**
When creating {{WORK_ARTIFACT}}, you MUST use these real git operations:

1. **Check current branch and status:**
   - Use `mcp__git__git_status` to see current state
   - Use `mcp__git__git_branch` to list branches

2. **Create feature branch (if needed):**
   - Use `mcp__git__git_create_branch` with branch_name: `{{BRANCH_PREFIX}}-[project-name]`
   - Use `mcp__git__git_checkout` to switch to the new branch

3. **Commit {{SECTION_TYPE}} as you work:**
   ```
   # After creating/updating {{SECTION_TYPE}}:
   - Use mcp__git__git_add with files: ["path/to/{{FILE_PATTERN}}"]
   - Use mcp__git__git_commit with message like:
     "{{COMMIT_PREFIX}}: {{COMMIT_ACTION_1}}"
     "{{COMMIT_PREFIX}}: {{COMMIT_ACTION_2}}"
     "{{COMMIT_PREFIX}}: {{COMMIT_ACTION_3}}"
   ```

4. **Complete {{WORK_TYPE}} with final commit:**
   ```
   # When {{WORK_TYPE}} is complete:
   - Use mcp__git__git_add with all {{WORK_TYPE}}-related files
   - Use mcp__git__git_commit with message:
     "{{COMMIT_PREFIX}}: complete {{COMMIT_COMPLETE_MESSAGE}}

     {{COMPLETION_CHECKLIST}}

     Agent: {{AGENT_NAME}}
     Phase: {{PHASE_NAME}}
     Quality: craftsman-standards-met
     {{ADDITIONAL_METADATA}}"
   ```

**Git Operation Timing:**
{{GIT_TIMING_GUIDANCE}}

**Fallback to Bash:**
If MCP git operations are unavailable, use Bash tool:
- `git {{FALLBACK_COMMAND_1}}`
- `git {{FALLBACK_COMMAND_2}}`
- `git add [files]` to stage changes
- `git commit -m "[message]"` to commit work

## Variable Reference
When importing git integration, customize these variables:
- `{{AGENT_TYPE}}`: Your agent type (e.g., "product architect", "design architect")
- `{{WORK_TYPE}}`: Type of work (e.g., "PRD", "technical specification", "implementation")
- `{{SECTION_TYPE}}`: Work sections (e.g., "PRD sections", "architecture decisions")
- `{{OUTPUT_TYPE}}`: Output artifacts (e.g., "PRD", "specification", "code")
- `{{WORK_ARTIFACT}}`: What you're creating (e.g., "a PRD", "technical specifications")
- `{{BRANCH_PREFIX}}`: Git branch prefix (e.g., "feature/prd", "feature/tech-spec")
- `{{FILE_PATTERN}}`: File naming pattern (e.g., "PRD-file.md", "tech-spec.md")
- `{{COMMIT_PREFIX}}`: Commit message prefix (e.g., "docs(prd)", "feat(spec)")
- `{{COMMIT_ACTION_N}}`: Example commit actions
- `{{COMMIT_COMPLETE_MESSAGE}}`: Final commit description
- `{{COMPLETION_CHECKLIST}}`: Bullet points of what was completed
- `{{AGENT_NAME}}`: Agent identifier
- `{{PHASE_NAME}}`: Completion phase name
- `{{ADDITIONAL_METADATA}}`: Any extra metadata
- `{{GIT_TIMING_GUIDANCE}}`: When to commit
- `{{FALLBACK_COMMAND_N}}`: Bash git commands

## Standard Commit Prefixes
- `feat`: New feature or capability
- `fix`: Bug fix or correction
- `docs`: Documentation changes
- `refactor`: Code restructuring
- `test`: Test additions/updates
- `chore`: Maintenance tasks
