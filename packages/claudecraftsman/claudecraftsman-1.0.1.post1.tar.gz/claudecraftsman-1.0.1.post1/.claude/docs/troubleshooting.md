# ClaudeCraftsman Troubleshooting Guide
*Solutions for common issues and debugging strategies*

## Overview

This guide helps you diagnose and resolve common issues with the ClaudeCraftsman framework. Each solution has been tested and verified to work effectively.

## Quick Diagnostics

### Framework Health Check
```bash
# Run this first for any issue
/validate

# For specific problems
/validate --component=agents --deep
/validate --component=mcp --fix
/validate --component=git --deep
```

## Common Issues and Solutions

### Installation Issues

#### Framework Not Found
**Symptoms**:
- Commands return "not found"
- CLAUDE.md imports failing
- Agents not available

**Solution**:
```bash
# Verify installation
claudecraftsman --version
# or
cc --version

# If missing, install with UV
uv add claudecraftsman

# Or with pip
pip install claudecraftsman

# For development mode
git clone https://github.com/your-org/claudecraftsman.git
cd claudecraftsman
uv sync --all-extras

# Run directly without installation
uvx --from claudecraftsman cc --help
```

#### Permission Denied
**Symptoms**:
- Cannot create files in .claude/
- Installation script fails
- Write operations blocked

**Solution**:
```bash
# Fix permissions for project files
chmod -R u+w .claude/

# For system-wide issues
sudo chown -R $(whoami) ~/.claude/

# If installed globally with UV, ensure PATH is set
export PATH="$HOME/.local/bin:$PATH"
```

### Command Issues

#### Command Not Responding
**Symptoms**:
- Command hangs indefinitely
- No output after running command
- Timeout errors

**Solution**:
```bash
# 1. Check MCP server status
/validate --component=mcp --deep

# 2. Restart MCP servers if needed
# In Claude Code settings, restart MCP servers

# 3. Check for syntax errors
/validate --component=commands

# 4. Try with minimal parameters
/help  # Should always work
```

#### Wrong Command Executed
**Symptoms**:
- Different command runs than expected
- Parameters ignored
- Unexpected behavior

**Solution**:
```markdown
1. Check command syntax:
   - Ensure proper spacing
   - Verify parameter format
   - Use quotes for multi-word arguments

2. Examples of correct syntax:
   /add agent security-architect
   /plan "user authentication system"
   /design e-commerce-platform --research=deep
```

#### Command Fails Midway
**Symptoms**:
- Partial execution
- Error messages during run
- Incomplete outputs

**Solution**:
```bash
# 1. Check error logs
cat .claude/logs/error.log

# 2. Validate framework state
/validate --fix

# 3. Check for file conflicts
ls -la .claude/docs/current/
# Remove any conflicting files

# 4. Retry with verbose mode
/plan my-feature --verbose
```

### Agent Issues

#### Agent Not Found
**Symptoms**:
- "Agent not available" errors
- Workflow coordination fails
- Handoffs not working

**Solution**:
```bash
# 1. List available agents
ls .claude/agents/

# 2. Validate agent configuration
/validate --component=agents

# 3. Reinstall missing agent
/add agent [missing-agent-name]

# 4. Check agent file format
head -20 .claude/agents/[agent-name].md
# Should see proper YAML frontmatter
```

#### Agent Handoff Failures
**Symptoms**:
- Context lost between agents
- Workflow stops unexpectedly
- Missing handoff documentation

**Solution**:
```bash
# 1. Check handoff logs
cat .claude/context/HANDOFF-LOG.md

# 2. Verify workflow state
cat .claude/context/WORKFLOW-STATE.md

# 3. Reset workflow if corrupted
rm .claude/context/WORKFLOW-STATE.md
/workflow [type] [project] --reset

# 4. Enable detailed logging
export CLAUDE_DEBUG=true
```

#### Agent Quality Issues
**Symptoms**:
- Output doesn't meet standards
- Missing citations or research
- Incomplete documentation

**Solution**:
```markdown
1. Verify agent is using MCP tools:
   - Check for time tool usage (no hardcoded dates)
   - Ensure research with searxng/crawl4ai
   - Validate citations present

2. Re-run with quality enforcement:
   /workflow [type] [project] --enforce-quality

3. Update agent if needed:
   /add agent [agent-name] --update
```

### MCP Tool Issues

#### MCP Connection Failed
**Symptoms**:
- "MCP server unavailable" errors
- Tools not responding
- Research capabilities disabled

**Solution**:
```bash
# 1. Check MCP configuration
/validate --component=mcp

# 2. Test individual MCP servers
# Time tool test
/validate --component=mcp --tool=time

# 3. Restart MCP servers
# In Claude Code: Settings → Restart MCP Servers

# 4. Fallback mode
/plan my-feature --no-mcp  # Uses native capabilities
```

#### Slow MCP Performance
**Symptoms**:
- Long delays in tool responses
- Timeouts on searches
- Framework feels sluggish

**Solution**:
```bash
# 1. Check performance metrics
/validate --component=mcp --performance

# 2. Clear MCP cache
rm -rf .claude/cache/mcp/

# 3. Optimize MCP usage
/workflow my-project --mcp-optimize

# 4. Use selective MCP
/design my-system --mcp=essential
```

### File and Documentation Issues

#### File Organization Broken
**Symptoms**:
- Files in wrong locations
- Cannot find documentation
- Registry out of sync

**Solution**:
```bash
# 1. Audit file structure
find .claude -type f -name "*.md" | sort

# 2. Fix common issues
# Move files to correct locations
mv .claude/docs/PRD-*.md .claude/docs/current/
mv .claude/docs/old/* .claude/docs/archive/$(date +%Y-%m-%d)/

# 3. Rebuild registry
/validate --component=docs --rebuild-registry

# 4. Set up proper structure
/init-craftsman . --fix-structure
```

#### Documentation Not Generating
**Symptoms**:
- Expected docs missing
- Incomplete documentation
- Templates not applied

**Solution**:
```bash
# 1. Check template availability
ls .claude/templates/

# 2. Regenerate documentation
/workflow update-docs [project]

# 3. Force documentation creation
/plan my-feature --force-docs

# 4. Manual documentation trigger
/add template doc-template --apply-to=[project]
```

### Git Integration Issues

#### Git Operations Failing
**Symptoms**:
- Commits not created
- Branch management issues
- PR creation failures

**Solution**:
```bash
# 1. Check Git status
git status
/validate --component=git

# 2. Fix common Git issues
git config user.name "Your Name"
git config user.email "your.email@example.com"

# 3. Reset Git integration
/validate --component=git --reset

# 4. Manual Git mode
/workflow my-feature --git-manual
```

#### Merge Conflicts
**Symptoms**:
- Cannot complete workflow
- Git blocking operations
- Conflicting changes

**Solution**:
```bash
# 1. Identify conflicts
git status
git diff --name-only --diff-filter=U

# 2. Resolve conflicts
# Use your preferred merge tool
git mergetool

# 3. Continue workflow
git add .
git commit -m "Resolve merge conflicts"
/workflow continue

# 4. Prevent future conflicts
/workflow my-feature --branch-strategy=isolated
```

### Performance Issues

#### Slow Command Execution
**Symptoms**:
- Commands take too long
- System feels unresponsive
- Timeouts frequent

**Solution**:
```bash
# 1. Performance diagnostics
/validate --performance

# 2. Clear caches
rm -rf .claude/cache/
rm -rf .claude/tmp/

# 3. Optimize operations
/workflow my-project --optimize

# 4. Use faster strategies
/plan my-feature --quick
/implement my-feature --parallel
```

#### High Memory Usage
**Symptoms**:
- System slowdown
- Out of memory errors
- Claude Code crashes

**Solution**:
```bash
# 1. Check resource usage
/validate --component=resources

# 2. Limit concurrent operations
/workflow my-project --max-parallel=2

# 3. Use streaming mode
/design my-system --stream

# 4. Clean up old data
/validate --cleanup --older-than=30d
```

### Workflow Issues

#### Workflow Stuck
**Symptoms**:
- Progress halted
- No agent responding
- State corrupted

**Solution**:
```bash
# 1. Check workflow state
cat .claude/context/WORKFLOW-STATE.md

# 2. Identify stuck phase
/validate --component=workflow --current

# 3. Resume or reset
/workflow resume  # Try to continue
/workflow reset   # Start over

# 4. Manual progression
/workflow next-phase --force
```

#### Context Lost
**Symptoms**:
- Agents missing information
- Handoffs incomplete
- Work being repeated

**Solution**:
```bash
# 1. Check context files
ls -la .claude/context/

# 2. Restore from backup
cp .claude/context/.backup/* .claude/context/

# 3. Rebuild context
/workflow rebuild-context [project]

# 4. Enable context preservation
/workflow my-project --preserve-context=max
```

## Advanced Debugging

### Enable Debug Mode
```bash
# Set environment variable
export CLAUDE_DEBUG=true
export CLAUDE_LOG_LEVEL=debug

# Run commands with verbose output
/plan my-feature --verbose --debug
```

### Framework Logs
```bash
# View recent logs
tail -f .claude/logs/framework.log

# Search for errors
grep -i error .claude/logs/*.log

# Check specific component
grep -i "agent:backend" .claude/logs/framework.log
```

### MCP Tool Debugging
```bash
# Test individual tools
/validate --tool=time --test
/validate --tool=searxng --test --query="test"
/validate --tool=context7 --test --library="react"

# Monitor MCP communication
/validate --component=mcp --monitor
```

### Performance Profiling
```bash
# Run with profiling
/plan my-feature --profile

# View performance report
cat .claude/reports/performance-[timestamp].json

# Identify bottlenecks
/analyze performance-report.json
```

## Prevention Strategies

### Regular Maintenance
```bash
# Weekly tasks
/validate
/validate --component=all --quick

# Monthly tasks
/validate --deep
/validate --cleanup
/validate --optimize

# Quarterly tasks
/validate --component=all --deep --fix
```

### Backup Important Work
```bash
# Automatic backups
/workflow my-project --backup

# Manual backup
cp -r .claude/docs/current/ .claude/docs/backup-$(date +%Y%m%d)/

# Git-based backup
git add .claude/
git commit -m "Backup Claude framework state"
```

### Monitor Framework Health
```bash
# Set up monitoring
/validate --monitor --alert-on-error

# Check health metrics
/validate --metrics

# Review reports
ls .claude/reports/health-*.json
```

## Getting Help

### Self-Help Resources
1. **Documentation**: Check `.claude/docs/` directory
2. **Examples**: Browse `.claude/examples/` for patterns
3. **Logs**: Review `.claude/logs/` for detailed errors
4. **Community**: Search GitHub issues for similar problems

### Diagnostic Information
When reporting issues, include:
```bash
# Framework version
cat .claude/version

# System information
/validate --system-info

# Recent operations
tail -50 .claude/logs/framework.log

# Current state
/validate --diagnostic-dump > diagnostic.json
```

### Emergency Recovery
If all else fails:
```bash
# 1. Backup current state
mv .claude .claude.backup

# 2. Reinstall framework
/init-craftsman . --fresh

# 3. Restore selective data
cp -r .claude.backup/docs/current/* .claude/docs/current/

# 4. Validate recovery
/validate --deep
```

## Common Error Messages

### "MCP server unavailable"
- **Cause**: MCP connection lost
- **Fix**: Restart MCP servers in Claude Code settings

### "Agent handoff failed"
- **Cause**: Context file corruption
- **Fix**: `/workflow reset` or check handoff logs

### "Command not found"
- **Cause**: Import path issues
- **Fix**: Verify CLAUDE.md imports

### "Quality gate failed"
- **Cause**: Output doesn't meet standards
- **Fix**: Review quality criteria, ensure MCP tools used

### "Git operation blocked"
- **Cause**: Uncommitted changes or conflicts
- **Fix**: Resolve Git state before continuing

## Prevention Best Practices

1. **Regular Validation**: Run `/validate` weekly
2. **Keep Updated**: Check for framework updates
3. **Clean Workspace**: Remove old files periodically
4. **Monitor Performance**: Watch for degradation
5. **Document Issues**: Track problems and solutions

---

*Remember: Most issues have simple solutions. Start with `/validate` and work systematically through the debugging steps.*
