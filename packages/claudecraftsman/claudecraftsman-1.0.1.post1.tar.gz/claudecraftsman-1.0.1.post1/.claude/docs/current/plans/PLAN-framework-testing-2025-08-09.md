# ClaudeCraftsman Framework Testing Implementation Plan

## Overview
- **Feature**: Comprehensive testing approach for ClaudeCraftsman framework installation
- **Scope**: Local development installation via `uv`, component validation, and functional testing
- **Timeline**: 3 phases over 2-3 hours of testing
- **Mode**: Development testing with local source directory

## Requirements
- Validate framework installs correctly from local directory using `uv`
- Test editable installation for development workflow
- Ensure all framework components are present and accessible
- Test basic functionality of key framework features
- Verify framework can be used in real projects
- Confirm integration with Claude Code works properly
- Enable rapid iteration during development

## Implementation Phases

### Phase 1: Local Development Installation Testing (30 minutes)
**Objective**: Verify framework installs correctly from local source

1. **Development Environment Setup**
   - Use current `/workspace` directory as source
   - Create separate test project directory
   - Ensure clean test environment

2. **Local Installation Methods (WITH ISOLATION)**
   ```bash
   # CRITICAL: Never run these commands in /workspace itself!
   # Always create test directory OUTSIDE the framework source

   # Safe testing approach:
   cd /tmp  # or ~/testing or any directory OUTSIDE /workspace
   mkdir claudecraftsman-test-$(date +%s)
   cd claudecraftsman-test-*
   uv init test-project
   cd test-project

   # NOW it's safe to install from /workspace:
   # Method 1: Editable install from local path (RECOMMENDED for development)
   uv add --editable /workspace

   # Method 2: Direct install from local path
   uv add /workspace

   # Method 3: Using pip with uv for editable install
   uv pip install -e /workspace

   # Method 4: Direct execution without install
   uv run --with /workspace cc --help
   ```

3. **Installation Validation**
   - Check `uv.lock` contains local claudecraftsman reference
   - Verify `pyproject.toml` shows local path dependency
   - Confirm CLI accessible via `cc` command
   - Test that changes in `/workspace` reflect immediately (editable mode)

### Phase 2: Component Validation (45 minutes)
**Objective**: Ensure all framework components are present and functional

1. **File Structure Verification**
   ```bash
   # Test cc init creates proper structure
   cc init test-project

   # Verify created directories:
   test -d .claude/ || echo "FAIL: .claude/ not created"
   test -d .claude/agents/ || echo "FAIL: agents/ missing"
   test -d .claude/commands/ || echo "FAIL: commands/ missing"
   test -d .claude/docs/current/ || echo "FAIL: docs structure missing"
   test -d .claude/context/ || echo "FAIL: context/ missing"
   ```

2. **Core Files Validation**
   ```bash
   # Check essential files exist
   test -f CLAUDE.md || echo "FAIL: CLAUDE.md not created"
   test -f .claude/framework.md || echo "FAIL: framework.md missing"
   test -f .claude/docs/current/registry.md || echo "FAIL: registry missing"
   ```

3. **Framework Content Verification**
   - Validate agents are properly formatted with YAML frontmatter
   - Check commands have correct structure
   - Ensure templates are complete and usable
   - Verify MCP tool integration references

### Phase 3: Functional Testing (45 minutes)
**Objective**: Test framework functionality in real usage scenarios

1. **Command Execution Tests**
   ```bash
   # Test framework state management
   cc validate framework
   cc state document-created "test.md" "Test" "docs/" "Test document"

   # Test registry operations
   cc registry list
   cc registry add "test-doc.md" "Test" "Active"

   # Test archival system
   cc archive check
   ```

2. **Claude Code Integration Test**
   - Create test CLAUDE.md that imports framework
   - Verify framework activation in Claude Code
   - Test that agents are accessible
   - Confirm commands can be invoked

3. **End-to-End Workflow Test**
   ```bash
   # Initialize project
   cc init e2e-test

   # Create a test document
   echo "# Test Document" > .claude/docs/current/TEST-doc-2025-08-09.md

   # Update registry
   cc state document-created "TEST-doc-2025-08-09.md" "Test" "docs/current/" "E2E test"

   # Validate framework health
   cc validate framework

   # Check archival rules
   cc archive check --verbose
   ```

## Test Validation Criteria

### Success Metrics
- [ ] Framework installs without errors using `uv add claudecraftsman`
- [ ] CLI command `cc` is accessible after installation
- [ ] `cc init` creates complete directory structure
- [ ] All core framework files are present
- [ ] State management commands work correctly
- [ ] Registry operations function properly
- [ ] Archival system processes documents correctly
- [ ] Framework activates in Claude Code sessions
- [ ] Version information displays correctly
- [ ] Help commands provide useful information

### Error Conditions to Test
- Installing in directory with existing framework
- Running commands without initialization
- Invalid command arguments
- Missing dependencies
- Permission issues
- Malformed configuration files

## Dependencies
- Python 3.12+ environment
- `uv` package manager installed
- Write permissions in test directory
- Claude Code for integration testing
- Terminal access for CLI testing

## Testing Environment Setup (WITH ISOLATION & ROLLBACK)

### Safety Rules
1. **NEVER test in /workspace directory** - This would create circular dependencies
2. **ALWAYS use /tmp or dedicated test directory** - Keep tests isolated
3. **TIMESTAMP all test directories** - Easy identification and cleanup
4. **PRESERVE /workspace integrity** - No modifications to source during testing

### Setup with Rollback Strategy
```bash
# SAFETY CHECK: Ensure we're NOT in /workspace
if [[ $(pwd) == "/workspace"* ]]; then
    echo "ERROR: Cannot test from within framework source directory!"
    echo "Please cd to /tmp or another safe location first"
    exit 1
fi

# Create isolated test environment with timestamp for easy cleanup
TEST_ROOT="/tmp/claudecraftsman-tests"
TEST_ID=$(date +%Y%m%d-%H%M%S)
TEST_DIR="$TEST_ROOT/test-$TEST_ID"

# Create test directory
mkdir -p $TEST_DIR
cd $TEST_DIR

# Save test metadata for rollback
cat > test-metadata.json << EOF
{
  "test_id": "$TEST_ID",
  "framework_source": "/workspace",
  "created": "$(date -Iseconds)",
  "status": "in_progress"
}
EOF

# Initialize test project
uv init test-project
cd test-project

# Install framework from local source (editable for development)
uv add --editable /workspace

# Verify installation
uv run cc --version
uv run cc validate dependencies
```

### Rollback Procedures
```bash
# Complete cleanup of failed test
rollback_test() {
    TEST_DIR=$1
    echo "Rolling back test at $TEST_DIR..."

    # Remove test directory completely
    rm -rf $TEST_DIR

    # Verify /workspace is unchanged
    cd /workspace
    git status  # Should show no changes
}

# Cleanup all tests older than 1 day
cleanup_old_tests() {
    find /tmp/claudecraftsman-tests -type d -mtime +1 -exec rm -rf {} \;
}

# Emergency cleanup - remove ALL test directories
emergency_cleanup() {
    echo "WARNING: Removing all test directories..."
    rm -rf /tmp/claudecraftsman-tests
}
```

## Development Workflow Testing

```bash
# Development cycle testing
# 1. Make change in /workspace source
# 2. Test immediately in test project (no reinstall needed with --editable)

# Example workflow:
cd /workspace
# Edit src/claudecraftsman/cli.py

cd /tmp/claudecraftsman-test/test-project
# Changes are immediately available
uv run cc --help  # Should reflect changes
```

## Test Execution Script

Create `test_framework_local.sh`:
```bash
#!/bin/bash
set -e

FRAMEWORK_DIR="/workspace"
TEST_DIR="/tmp/claudecraftsman-test-$(date +%s)"

echo "ClaudeCraftsman Framework Local Testing Suite"
echo "============================================="
echo "Framework source: $FRAMEWORK_DIR"
echo "Test directory: $TEST_DIR"

# Setup test environment
echo -e "\n[Setup] Creating test environment..."
mkdir -p $TEST_DIR
cd $TEST_DIR

# Phase 1: Local Installation
echo -e "\n[Phase 1] Testing Local Installation..."
uv init test-project
cd test-project

# Test editable install
uv add --editable $FRAMEWORK_DIR
uv run cc --version || exit 1

# Phase 2: Initialization
echo -e "\n[Phase 2] Testing Project Initialization..."
uv run cc init my-test-app || exit 1

# Phase 3: Component Validation
echo -e "\n[Phase 3] Validating Components..."
cd my-test-app
test -d .claude/ && echo "✓ .claude/ directory created"
test -f CLAUDE.md && echo "✓ CLAUDE.md created"
test -f .claude/framework.md && echo "✓ framework.md present"

# Phase 4: Functional Tests
echo -e "\n[Phase 4] Testing Functionality..."
uv run cc validate framework || exit 1
uv run cc registry list || exit 1

# Phase 5: Development Change Testing
echo -e "\n[Phase 5] Testing Live Development Changes..."
# This would test that changes in $FRAMEWORK_DIR are immediately reflected
echo "Make a change in $FRAMEWORK_DIR and verify it works here"

echo -e "\n✅ All tests passed!"
echo "Test environment preserved at: $TEST_DIR"
```

## Rapid Development Testing

For quick iteration during development:
```bash
# One-time setup in test project
cd /tmp/test-project
uv add --editable /workspace

# Now you can test changes immediately
# Edit files in /workspace, then:
uv run cc [command]  # Tests your changes instantly

# No need to reinstall or rebuild!
```

## Success Criteria
- Framework installs cleanly in under 30 seconds
- All directory structures created correctly
- Commands execute without errors
- State management persists across invocations
- Framework integrates with Claude Code
- Documentation is accessible and complete

## Next Steps
1. **Immediate**: Create test environment and run installation test
2. **Next**: Validate all components are present
3. **Then**: Test functional operations
4. **Finally**: Document any issues found and create fixes
5. **Follow-up**: Create automated test suite for CI/CD

## Resource Requirements
- **Testing Time**: 2-3 hours for comprehensive validation
- **Environment**: Clean Python 3.12+ with uv
- **Tools**: Terminal, text editor, Claude Code
- **Documentation**: Test results log, issue tracker

## Risk Mitigation
- **Backup**: Keep copy of working framework before testing changes
- **Isolation**: Use virtual environment to prevent system conflicts
- **Logging**: Capture all test output for debugging
- **Rollback**: Have process to revert if critical issues found
