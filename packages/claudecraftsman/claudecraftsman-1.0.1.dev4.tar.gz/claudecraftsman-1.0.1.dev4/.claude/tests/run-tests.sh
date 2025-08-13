#!/bin/bash
# ClaudeCraftsman Framework Test Runner
# Executes comprehensive framework validation tests

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test results
PASSED=0
FAILED=0
SKIPPED=0

# Timestamp for reports
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
REPORT_DIR=".claude/reports"
REPORT_FILE="$REPORT_DIR/test-report-$TIMESTAMP.json"

# Create report directory
mkdir -p "$REPORT_DIR"

echo "====================================="
echo "ClaudeCraftsman Framework Test Suite"
echo "====================================="
echo "Timestamp: $(date)"
echo ""

# Function to run a test category
run_test_category() {
    local category=$1
    local description=$2

    echo -e "${YELLOW}Testing: $description${NC}"
    echo "--------------------------------"
}

# Function to check test result
check_result() {
    local test_name=$1
    local result=$2

    if [ $result -eq 0 ]; then
        echo -e "✓ $test_name ${GREEN}PASSED${NC}"
        ((PASSED++))
    else
        echo -e "✗ $test_name ${RED}FAILED${NC}"
        ((FAILED++))
    fi
}

# 1. Framework Structure Tests
run_test_category "structure" "Framework Structure"

# Check required directories
for dir in ".claude/agents" ".claude/commands" ".claude/docs/current" ".claude/context" ".claude/templates"; do
    if [ -d "$dir" ]; then
        check_result "Directory: $dir" 0
    else
        check_result "Directory: $dir" 1
    fi
done

echo ""

# 2. Agent Configuration Tests
run_test_category "agents" "Agent Configuration"

# Check each agent file
for agent in "product-architect" "design-architect" "system-architect" "backend-architect" "frontend-developer" "qa-architect" "data-architect" "ml-architect" "workflow-coordinator"; do
    if [ -f ".claude/agents/$agent.md" ]; then
        # Check for required sections
        if grep -q "Craftsman Philosophy" ".claude/agents/$agent.md" && \
           grep -q "MCP" ".claude/agents/$agent.md" && \
           grep -q "Quality Gates" ".claude/agents/$agent.md"; then
            check_result "Agent: $agent" 0
        else
            check_result "Agent: $agent (missing sections)" 1
        fi
    else
        check_result "Agent: $agent (not found)" 1
    fi
done

echo ""

# 3. Command Tests
run_test_category "commands" "Command Configuration"

# Check each command file
for cmd in "help" "add" "plan" "design" "implement" "workflow" "init-craftsman" "test" "validate" "deploy"; do
    if [ -f ".claude/commands/$cmd.md" ]; then
        # Check for metadata
        if grep -q "name: $cmd" ".claude/commands/$cmd.md"; then
            check_result "Command: /$cmd" 0
        else
            check_result "Command: /$cmd (invalid metadata)" 1
        fi
    else
        check_result "Command: /$cmd (not found)" 1
    fi
done

echo ""

# 4. Documentation Tests
run_test_category "documentation" "Documentation Quality"

# Check documentation files
for doc in "getting-started.md" "agent-reference.md" "command-reference.md" "best-practices.md" "troubleshooting.md"; do
    if [ -f ".claude/docs/$doc" ]; then
        # Check minimum length
        lines=$(wc -l < ".claude/docs/$doc")
        if [ $lines -gt 50 ]; then
            check_result "Documentation: $doc" 0
        else
            check_result "Documentation: $doc (too short)" 1
        fi
    else
        check_result "Documentation: $doc (not found)" 1
    fi
done

echo ""

# 5. Integration Tests
run_test_category "integration" "Framework Integration"

# Check CLAUDE.md exists and has proper imports
if [ -f "CLAUDE.md" ]; then
    if grep -q "@.*framework.md" "CLAUDE.md"; then
        check_result "CLAUDE.md configuration" 0
    else
        check_result "CLAUDE.md configuration (missing imports)" 1
    fi
else
    check_result "CLAUDE.md configuration (not found)" 1
fi

# Check context files
for ctx in "WORKFLOW-STATE.md" "HANDOFF-LOG.md" "CONTEXT.md"; do
    if [ -f ".claude/context/$ctx" ]; then
        check_result "Context: $ctx" 0
    else
        # Context files may not exist initially, so we skip
        echo -e "- Context: $ctx ${YELLOW}SKIPPED${NC} (optional)"
        ((SKIPPED++))
    fi
done

echo ""

# 6. Generate Test Report
echo "====================================="
echo "Test Summary"
echo "====================================="
echo -e "Passed:  ${GREEN}$PASSED${NC}"
echo -e "Failed:  ${RED}$FAILED${NC}"
echo -e "Skipped: ${YELLOW}$SKIPPED${NC}"
echo "Total:   $((PASSED + FAILED + SKIPPED))"
echo ""

# Calculate pass rate
if [ $((PASSED + FAILED)) -gt 0 ]; then
    PASS_RATE=$((PASSED * 100 / (PASSED + FAILED)))
else
    PASS_RATE=0
fi

echo "Pass Rate: $PASS_RATE%"

# Generate JSON report
cat > "$REPORT_FILE" <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "framework_version": "1.0",
  "test_suite": "basic",
  "summary": {
    "total": $((PASSED + FAILED + SKIPPED)),
    "passed": $PASSED,
    "failed": $FAILED,
    "skipped": $SKIPPED,
    "pass_rate": $PASS_RATE
  },
  "duration": "$SECONDS seconds"
}
EOF

echo ""
echo "Report saved to: $REPORT_FILE"

# Exit with appropriate code
if [ $FAILED -gt 0 ]; then
    echo ""
    echo -e "${RED}TESTS FAILED${NC}"
    exit 1
else
    echo ""
    echo -e "${GREEN}ALL TESTS PASSED${NC}"
    exit 0
fi
