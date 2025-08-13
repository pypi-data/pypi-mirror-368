# ClaudeCraftsman Troubleshooting Guide
*Solutions for common issues and errors*

## Table of Contents
- [Installation Issues](#installation-issues)
- [MCP Tool Problems](#mcp-tool-problems)
- [Command Errors](#command-errors)
- [Implementation Issues](#implementation-issues)
- [Testing Problems](#testing-problems)
- [Agent Coordination](#agent-coordination)
- [Performance Issues](#performance-issues)
- [Debug Tips](#debug-tips)

## Installation Issues

### Error: "claudecraftsman: command not found"

**Symptoms:**
```bash
$ cc init
bash: cc: command not found
```

**Solutions:**
```bash
# 1. Verify installation
pip show claudecraftsman

# 2. Check PATH
echo $PATH

# 3. Reinstall with UV (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh
uv add claudecraftsman

# 4. Use full path
python -m claudecraftsman init

# 5. Use uvx without installation
uvx --from claudecraftsman cc init
```

### Error: "Python version not supported"

**Symptoms:**
```
ERROR: claudecraftsman requires Python 3.12+
```

**Solutions:**
```bash
# 1. Check Python version
python --version

# 2. Install Python 3.12+
# macOS
brew install python@3.12

# Ubuntu/Debian
sudo apt update
sudo apt install python3.12

# 3. Use pyenv for version management
pyenv install 3.12.0
pyenv local 3.12.0
```

## MCP Tool Problems

### MCP Tools Not Available

**Symptoms:**
- Agents don't use current dates
- No research citations in outputs
- Missing timestamps in documentation

**Diagnosis:**
```bash
# In Claude Code, check if MCP tools work
# Try: Can you tell me the current time?
# Should use: mcp__time__get_current_time
```

**Solutions:**
1. **Enable MCP Servers in Claude Code:**
   - Open Claude Code settings
   - Enable required MCP servers:
     - Time server
     - Search (searxng)
     - Context7
     - Playwright (for testing)

2. **Verify MCP Tool Access:**
   ```
   Test each tool:
   - Time: "What's the current time?"
   - Search: "Search for Python best practices 2025"
   - Context7: "Get FastAPI documentation"
   ```

3. **Fallback Mode:**
   - Framework gracefully degrades without MCP
   - Uses fallback dates and skip research
   - Still produces quality outputs

### Research Not Working

**Symptoms:**
```
No research results found
Citations missing in output
```

**Solutions:**
```bash
# 1. Use current year in searches
/design system --research=deep
# Ensure searches use "2025" not "2024"

# 2. Be specific in queries
# Bad: "best practices"
# Good: "Python FastAPI best practices 2025"

# 3. Try alternative MCP tools
# If searxng fails, Context7 might work
```

## Command Errors

### Error: "Plan not found"

**Symptoms:**
```bash
/implement user-auth
ERROR: No plan found for 'user-auth'
```

**Solutions:**
```bash
# 1. Check available plans
ls .claude/docs/current/plans/

# 2. Use exact plan name
/implement user-authentication  # Not user-auth

# 3. Specify plan file explicitly
/implement user-auth --from-file=PLAN-user-authentication-2025-08-08.md

# 4. Create plan first
/plan user-authentication
/implement user-authentication
```

### Error: "Agent not available"

**Symptoms:**
```
ERROR: Agent 'custom-agent' not found
```

**Solutions:**
```bash
# 1. List available agents
ls .claude/agents/

# 2. Create missing agent
/add agent custom-agent

# 3. Use framework default agents
product-architect, design-architect, backend-architect, etc.
```

## Implementation Issues

### Implementation Stuck or Frozen

**Symptoms:**
- Progress stops at certain percentage
- No activity for extended time
- Agent appears blocked

**Solutions:**
```bash
# 1. Check implementation status
/implement [plan] --status

# Output shows:
# - Current phase and task
# - Active agent
# - Any blockers

# 2. View verbose logs
/implement [plan] --verbose

# 3. Resume from last checkpoint
/implement [plan] --resume

# 4. Force specific phase
/implement [plan] --phase=2 --force

# 5. Debug mode
/implement [plan] --debug
```

### Quality Gates Failing

**Symptoms:**
```
Quality Gate Failed: Test coverage below 80%
Cannot proceed to next phase
```

**Solutions:**
```bash
# 1. Check specific failures
/validate [feature] --detailed

# 2. Fix specific issues
/test [feature] --coverage  # Improve coverage
/document [feature]         # Add missing docs

# 3. Override with justification (use sparingly)
/implement [plan] --override-quality "MVP phase, will improve"

# 4. Update quality thresholds
# Edit plan to adjust expectations
```

## Testing Problems

### Playwright Tests Failing

**Symptoms:**
```
ERROR: browser_navigate failed
Playwright timeout
```

**Solutions:**
```bash
# 1. Verify Playwright MCP server enabled
# In Claude Code settings

# 2. Check browser installation
/test [feature] --playwright --install-browsers

# 3. Debug specific test
/test [feature] --playwright --debug --headed

# 4. Adjust timeouts
/test [feature] --playwright --timeout=30000

# 5. Fallback to other test types
/test [feature] --type=integration  # Skip E2E temporarily
```

### Coverage Not Meeting Targets

**Symptoms:**
```
Test coverage: 65% (target: 80%)
```

**Solutions:**
```bash
# 1. Generate coverage report
/test [feature] --coverage --report

# 2. Identify untested code
/analyze test-gaps [feature]

# 3. Add specific test types
/test [feature] --type=unit --focus=edge-cases

# 4. Update existing tests
/test [feature] --update

# 5. Adjust targets for MVP
/plan [feature] --update-coverage=60  # Temporary
```

## Agent Coordination

### Agent Handoff Failures

**Symptoms:**
```
WARNING: Context lost during handoff
Agent starting without previous context
```

**Solutions:**
```bash
# 1. Check handoff logs
cat .claude/context/HANDOFF-LOG.md

# 2. Verify context files
ls .claude/context/

# 3. Repair context
/workflow repair-context [feature]

# 4. Manual handoff
/workflow handoff --from=backend-architect --to=frontend-developer

# 5. Reset workflow state
/workflow reset [feature] --preserve-work
```

### Multiple Agents Conflicting

**Symptoms:**
- Agents overwriting each other's work
- Conflicting implementations

**Solutions:**
```bash
# 1. Check workflow coordination
/workflow status

# 2. Enforce sequential execution
/implement [plan] --sequential

# 3. Clear task assignments
/workflow clear-assignments

# 4. Use explicit coordination
/workflow coordinate [feature] --agents=backend,frontend
```

## Performance Issues

### Slow Command Execution

**Symptoms:**
- Commands taking >1 minute to start
- Long delays between phases

**Solutions:**
```bash
# 1. Check system resources
/validate system --performance

# 2. Disable intensive features
/implement [plan] --no-research  # Skip research phase
/implement [plan] --quick        # Minimal validation

# 3. Use focused operations
/implement [plan] --phase=2      # Single phase only

# 4. Clear caches
cc cache clear

# 5. Reduce parallel operations
/implement [plan] --max-parallel=1
```

### High Memory Usage

**Symptoms:**
- System slowdown during operations
- Out of memory errors

**Solutions:**
```bash
# 1. Limit operation scope
/implement [plan] --memory-limit=2G

# 2. Process in smaller chunks
/plan [feature] --chunked

# 3. Clear temporary files
rm -rf .claude/tmp/*

# 4. Disable caching
/implement [plan] --no-cache
```

## Debug Tips

### Enable Debug Mode

```bash
# Global debug
export CLAUDECRAFTSMAN_DEBUG=1

# Command-specific debug
/implement [plan] --debug
/test [feature] --debug

# Verbose logging
/implement [plan] --verbose --log-level=DEBUG
```

### Check Framework Health

```bash
# Full system check
/validate framework --comprehensive

# Checks:
# - File structure integrity
# - Agent availability
# - MCP tool access
# - Configuration validity
```

### View Internal State

```bash
# Implementation state
cat .claude/context/WORKFLOW-STATE.md

# Current progress
cat .claude/project-mgt/06-project-tracking/progress-log.md

# Agent activities
cat .claude/context/HANDOFF-LOG.md
```

### Common Debug Commands

```bash
# Reset stuck implementation
/implement [plan] --reset --preserve-work

# Force refresh
/workflow refresh

# Validate specific component
/validate agent backend-architect
/validate command implement

# Check MCP status
/validate mcp-tools

# Clear all caches
cc cache clear --all
```

## Getting Help

### Built-in Help

```bash
# General help
/help

# Command-specific help
/help implement
/help test

# Show examples
/help examples
```

### Community Support

1. **GitHub Issues**: github.com/anthropics/claude-code/issues
2. **Include in reports:**
   - Error messages
   - Command used
   - ClaudeCraftsman version
   - Debug logs

### Emergency Recovery

```bash
# Backup current state
cp -r .claude .claude.backup

# Reset to clean state
cc reset --preserve-docs

# Restore from backup
cp -r .claude.backup .claude
```

## Prevention Tips

### Best Practices

1. **Regular Saves**: Commit work frequently
2. **Status Checks**: Use `--status` regularly
3. **Incremental Work**: Complete phases before starting new ones
4. **Backup Plans**: Keep plan files backed up
5. **Version Control**: Use Git for all changes

### Healthy Workflow

```bash
# Start each session
/validate framework

# Check before major operations
/implement [plan] --dry-run

# Regular progress checks
/implement [plan] --status

# End of session
/workflow checkpoint
```

Remember: Most issues have simple solutions. The framework is designed to be resilient and helpful. When in doubt, `/help` is your friend!
