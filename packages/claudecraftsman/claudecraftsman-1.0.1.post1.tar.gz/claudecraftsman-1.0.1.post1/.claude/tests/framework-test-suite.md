# ClaudeCraftsman Framework Test Suite
*Comprehensive validation for framework integrity*

## Overview

This test suite validates the ClaudeCraftsman framework's functionality, ensuring all components work correctly and maintain craftsman quality standards.

## Test Categories

### 1. Framework Structure Tests
- Directory structure validation
- File naming conventions
- Required files presence
- Template availability

### 2. Agent Tests
- Agent configuration validation
- MCP integration verification
- Handoff protocol testing
- Quality gate enforcement

### 3. Command Tests
- Command execution validation
- Parameter handling
- Error recovery
- Integration verification

### 4. Integration Tests
- Multi-agent workflows
- Command chaining
- Context preservation
- Git integration

### 5. Quality Tests
- Documentation standards
- Code quality metrics
- Performance benchmarks
- Security validation

## Test Execution

### Quick Test (5 minutes)
```bash
# Basic framework validation
/validate

# Component checks
/validate --component=agents --quick
/validate --component=commands --quick
/validate --component=mcp --quick
```

### Comprehensive Test (30 minutes)
```bash
# Full framework validation
/validate --deep

# Run all test suites
/test framework --comprehensive

# Generate test report
/validate --report=test-results.json
```

### Continuous Testing
```bash
# Set up automated testing
/workflow test-framework --schedule=daily

# Monitor test results
/validate --monitor --dashboard
```

## Test Implementation

### Framework Validation Script
```typescript
// .claude/tests/framework/validate-framework.ts
interface FrameworkValidation {
  structure: StructureTest[];
  agents: AgentTest[];
  commands: CommandTest[];
  integration: IntegrationTest[];
  quality: QualityTest[];
}

class FrameworkValidator {
  async validateAll(): Promise<ValidationReport> {
    const results = {
      structure: await this.validateStructure(),
      agents: await this.validateAgents(),
      commands: await this.validateCommands(),
      integration: await this.validateIntegration(),
      quality: await this.validateQuality()
    };

    return this.generateReport(results);
  }

  private async validateStructure(): Promise<StructureResult> {
    // Check directory structure
    const requiredDirs = [
      '.claude/agents',
      '.claude/commands',
      '.claude/docs/current',
      '.claude/context',
      '.claude/templates'
    ];

    const results = await Promise.all(
      requiredDirs.map(dir => this.checkDirectory(dir))
    );

    return {
      passed: results.every(r => r.exists),
      details: results
    };
  }
}
```

### Agent Validation Tests
```typescript
// .claude/tests/unit/test-agents.ts
describe('Agent Validation', () => {
  const agents = [
    'product-architect',
    'design-architect',
    'system-architect',
    'backend-architect',
    'frontend-developer',
    'qa-architect',
    'data-architect',
    'ml-architect',
    'workflow-coordinator'
  ];

  agents.forEach(agent => {
    describe(`${agent} agent`, () => {
      it('should have valid configuration', async () => {
        const config = await loadAgentConfig(agent);
        expect(config).toHaveProperty('name');
        expect(config).toHaveProperty('description');
        expect(config).toHaveProperty('model');
      });

      it('should include craftsman philosophy', async () => {
        const content = await readAgentFile(agent);
        expect(content).toContain('Craftsman Philosophy');
        expect(content).toContain('MCP');
        expect(content).toContain('Quality Gates');
      });

      it('should define integration points', async () => {
        const content = await readAgentFile(agent);
        expect(content).toContain('Integration');
        expect(content).toContain('Receives from');
        expect(content).toContain('Hands off to');
      });
    });
  });
});
```

### Command Validation Tests
```typescript
// .claude/tests/unit/test-commands.ts
describe('Command Validation', () => {
  const commands = [
    'help', 'add', 'plan', 'design',
    'implement', 'workflow', 'init-craftsman',
    'test', 'validate', 'deploy'
  ];

  commands.forEach(command => {
    describe(`/${command} command`, () => {
      it('should have valid metadata', async () => {
        const meta = await loadCommandMetadata(command);
        expect(meta).toHaveProperty('name');
        expect(meta).toHaveProperty('description');
      });

      it('should handle parameters correctly', async () => {
        const testCases = getCommandTestCases(command);
        for (const testCase of testCases) {
          const result = await executeCommand(command, testCase.params);
          expect(result.success).toBe(true);
        }
      });

      it('should produce expected outputs', async () => {
        const outputs = await getCommandOutputs(command);
        expect(outputs).toMatchSnapshot();
      });
    });
  });
});
```

### Integration Tests
```typescript
// .claude/tests/integration/test-workflows.ts
describe('Workflow Integration', () => {
  it('should complete design-to-deploy workflow', async () => {
    const project = 'test-project-' + Date.now();

    // Start workflow
    const workflow = await executeCommand('workflow', [
      'design-to-deploy',
      project
    ]);

    // Verify each phase
    expect(workflow.phases.productArchitect).toHaveProperty('prd');
    expect(workflow.phases.designArchitect).toHaveProperty('techSpec');
    expect(workflow.phases.implementation).toHaveProperty('code');
    expect(workflow.phases.testing).toHaveProperty('coverage');

    // Verify handoffs
    const handoffs = await readHandoffLog();
    expect(handoffs).toHaveLength(4);
    expect(handoffs[0].from).toBe('product-architect');
    expect(handoffs[0].to).toBe('design-architect');
  });

  it('should preserve context across sessions', async () => {
    const context1 = await createContext('session1');
    await endSession();

    const context2 = await resumeSession('session1');
    expect(context2).toEqual(context1);
  });
});
```

### Quality Validation Tests
```typescript
// .claude/tests/unit/test-quality.ts
describe('Quality Standards', () => {
  it('should enforce documentation standards', async () => {
    const docs = await getAllDocuments();

    docs.forEach(doc => {
      expect(doc.name).toMatch(/^[A-Z]+-.*-\d{4}-\d{2}-\d{2}\.md$/);
      expect(doc.content).toContain('## ');
      expect(doc.content.length).toBeGreaterThan(100);
    });
  });

  it('should maintain test coverage', async () => {
    const coverage = await getTestCoverage();
    expect(coverage.unit).toBeGreaterThanOrEqual(80);
    expect(coverage.integration).toBeGreaterThanOrEqual(70);
    expect(coverage.e2e).toBeGreaterThanOrEqual(60);
  });

  it('should validate MCP tool usage', async () => {
    const agents = await getAllAgents();

    for (const agent of agents) {
      const mcpUsage = await analyzeMCPUsage(agent);
      expect(mcpUsage.usesTimeToolCorrectly).toBe(true);
      expect(mcpUsage.hasProperCitations).toBe(true);
    }
  });
});
```

### Performance Tests
```typescript
// .claude/tests/performance/test-performance.ts
describe('Performance Benchmarks', () => {
  it('should execute commands within time limits', async () => {
    const benchmarks = {
      'help': 1000,      // 1 second
      'add': 5000,       // 5 seconds
      'plan': 15000,     // 15 seconds
      'design': 45000,   // 45 seconds
      'validate': 5000   // 5 seconds
    };

    for (const [command, limit] of Object.entries(benchmarks)) {
      const start = Date.now();
      await executeCommand(command, ['test']);
      const duration = Date.now() - start;

      expect(duration).toBeLessThan(limit);
    }
  });

  it('should handle concurrent operations', async () => {
    const operations = Array(5).fill(null).map((_, i) =>
      executeCommand('add', ['agent', `test-agent-${i}`])
    );

    const results = await Promise.all(operations);
    expect(results.every(r => r.success)).toBe(true);
  });
});
```

## Test Data and Fixtures

### Test Project Structure
```markdown
.claude/tests/fixtures/
├── sample-project/
│   ├── CLAUDE.md
│   ├── .claude/
│   └── src/
├── agents/
│   └── test-agent.md
├── commands/
│   └── test-command.md
└── workflows/
    └── test-workflow.json
```

### Mock Data
```typescript
// .claude/tests/fixtures/mock-data.ts
export const mockPRD = {
  title: 'Test Product Requirements',
  sections: {
    overview: 'Test application for framework validation',
    requirements: ['REQ-001', 'REQ-002'],
    userStories: ['US-001', 'US-002'],
    successMetrics: ['Metric 1', 'Metric 2']
  }
};

export const mockTechSpec = {
  architecture: 'Microservices',
  technologies: ['Node.js', 'React', 'PostgreSQL'],
  apis: ['/users', '/products', '/orders'],
  deployment: 'Kubernetes'
};
```

## Continuous Integration

### GitHub Actions Workflow
```yaml
# .github/workflows/framework-tests.yml
name: Framework Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 0 * * *'  # Daily

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Setup Claude Code
      run: |
        # Install Claude Code CLI
        # Setup framework

    - name: Run Framework Tests
      run: |
        /validate --deep
        /test framework --comprehensive

    - name: Upload Test Results
      uses: actions/upload-artifact@v3
      with:
        name: test-results
        path: .claude/reports/test-*.json
```

## Test Reporting

### Test Result Format
```json
{
  "timestamp": "2025-08-04T10:00:00Z",
  "framework_version": "1.0",
  "test_suite": "comprehensive",
  "summary": {
    "total": 150,
    "passed": 148,
    "failed": 2,
    "skipped": 0
  },
  "categories": {
    "structure": { "passed": 25, "failed": 0 },
    "agents": { "passed": 45, "failed": 1 },
    "commands": { "passed": 40, "failed": 0 },
    "integration": { "passed": 20, "failed": 1 },
    "quality": { "passed": 20, "failed": 0 }
  },
  "failures": [
    {
      "test": "agent-handoff-context-preservation",
      "category": "agents",
      "error": "Context file not found",
      "severity": "medium"
    }
  ],
  "performance": {
    "total_duration": 1800000,
    "average_test_time": 12000
  }
}
```

### Test Dashboard
The `/validate --dashboard` command provides:
- Real-time test execution
- Historical trends
- Performance metrics
- Quality indicators
- Failure analysis

## Manual Testing Checklist

### New Agent Testing
- [ ] Configuration validates
- [ ] MCP tools integrate properly
- [ ] Handoffs work correctly
- [ ] Quality gates enforce
- [ ] Documentation complete

### New Command Testing
- [ ] Parameters parse correctly
- [ ] Execution completes
- [ ] Outputs meet standards
- [ ] Errors handled gracefully
- [ ] Integration verified

### Workflow Testing
- [ ] All phases execute
- [ ] Context preserved
- [ ] Handoffs successful
- [ ] Quality maintained
- [ ] Documentation generated

## Success Criteria

The framework test suite passes when:
- All structural tests pass (100%)
- Agent tests pass (>95%)
- Command tests pass (>95%)
- Integration tests pass (>90%)
- Quality tests pass (100%)
- Performance within benchmarks
- No critical failures

---

*A framework is only as good as its tests. Test thoroughly, test often, test with pride.*
