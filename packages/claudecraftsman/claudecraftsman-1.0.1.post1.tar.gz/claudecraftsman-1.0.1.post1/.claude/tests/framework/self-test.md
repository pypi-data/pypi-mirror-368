# Framework Self-Test Capability
*Built-in validation for ClaudeCraftsman integrity*

## Overview

The self-test capability enables the framework to validate its own functionality, ensuring all components work correctly and maintain quality standards.

## Self-Test Components

### 1. Structural Integrity
```typescript
class StructuralValidator {
  async validate(): Promise<ValidationResult> {
    const checks = [
      this.checkDirectoryStructure(),
      this.checkFileNaming(),
      this.checkRequiredFiles(),
      this.checkPermissions()
    ];

    const results = await Promise.all(checks);
    return this.consolidateResults(results);
  }

  private async checkDirectoryStructure(): Promise<Check> {
    const requiredDirs = [
      '.claude/agents',
      '.claude/commands',
      '.claude/docs/current',
      '.claude/docs/archive',
      '.claude/context',
      '.claude/templates',
      '.claude/tests'
    ];

    const missing = [];
    for (const dir of requiredDirs) {
      if (!await this.dirExists(dir)) {
        missing.push(dir);
      }
    }

    return {
      name: 'Directory Structure',
      passed: missing.length === 0,
      issues: missing.map(d => `Missing directory: ${d}`)
    };
  }
}
```

### 2. Agent Validation
```typescript
class AgentValidator {
  private requiredAgents = [
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

  async validateAgents(): Promise<ValidationResult> {
    const results = await Promise.all(
      this.requiredAgents.map(agent => this.validateAgent(agent))
    );

    return {
      category: 'Agents',
      passed: results.every(r => r.passed),
      details: results
    };
  }

  private async validateAgent(name: string): Promise<AgentCheck> {
    const path = `.claude/agents/${name}.md`;

    // Check file exists
    if (!await this.fileExists(path)) {
      return { name, passed: false, error: 'File not found' };
    }

    const content = await this.readFile(path);

    // Validate structure
    const checks = {
      hasFrontmatter: this.checkFrontmatter(content),
      hasPhilosophy: content.includes('Craftsman Philosophy'),
      hasMCPIntegration: content.includes('MCP'),
      hasQualityGates: content.includes('Quality Gates'),
      hasIntegration: content.includes('Integration')
    };

    const passed = Object.values(checks).every(v => v === true);

    return {
      name,
      passed,
      checks,
      warnings: this.getWarnings(checks)
    };
  }
}
```

### 3. Command Validation
```typescript
class CommandValidator {
  private requiredCommands = [
    'help', 'add', 'plan', 'design',
    'implement', 'workflow', 'init-craftsman',
    'test', 'validate', 'deploy'
  ];

  async validateCommands(): Promise<ValidationResult> {
    const results = await Promise.all(
      this.requiredCommands.map(cmd => this.validateCommand(cmd))
    );

    return {
      category: 'Commands',
      passed: results.every(r => r.passed),
      details: results
    };
  }

  private async validateCommand(name: string): Promise<CommandCheck> {
    const path = `.claude/commands/${name}.md`;

    if (!await this.fileExists(path)) {
      return { name, passed: false, error: 'File not found' };
    }

    const content = await this.readFile(path);
    const metadata = this.extractMetadata(content);

    const checks = {
      hasName: metadata.name === name,
      hasDescription: !!metadata.description,
      hasUsageExamples: content.includes('Usage') || content.includes('Examples'),
      hasDocumentation: content.length > 500
    };

    return {
      name,
      passed: Object.values(checks).every(v => v === true),
      checks
    };
  }
}
```

### 4. Integration Tests
```typescript
class IntegrationValidator {
  async validate(): Promise<ValidationResult> {
    const tests = [
      this.testAgentHandoffs(),
      this.testCommandChaining(),
      this.testMCPIntegration(),
      this.testGitIntegration(),
      this.testContextPreservation()
    ];

    const results = await Promise.all(tests);

    return {
      category: 'Integration',
      passed: results.every(r => r.passed),
      details: results
    };
  }

  private async testAgentHandoffs(): Promise<TestResult> {
    // Simulate agent handoff
    const handoff = {
      from: 'product-architect',
      to: 'design-architect',
      context: { prd: 'test-prd', requirements: [] }
    };

    try {
      await this.simulateHandoff(handoff);
      return { test: 'Agent Handoffs', passed: true };
    } catch (error) {
      return {
        test: 'Agent Handoffs',
        passed: false,
        error: error.message
      };
    }
  }

  private async testMCPIntegration(): Promise<TestResult> {
    // Test MCP tool availability
    const tools = ['time', 'searxng', 'crawl4ai', 'context7'];
    const available = await this.checkMCPTools(tools);

    return {
      test: 'MCP Integration',
      passed: available.every(t => t.available),
      details: available
    };
  }
}
```

### 5. Performance Benchmarks
```typescript
class PerformanceValidator {
  private benchmarks = {
    commandExecution: {
      help: 1000,      // 1 second
      add: 5000,       // 5 seconds
      plan: 15000,     // 15 seconds
      design: 45000,   // 45 seconds
      validate: 5000   // 5 seconds
    },
    fileOperations: {
      read: 100,       // 100ms
      write: 200,      // 200ms
      search: 500      // 500ms
    }
  };

  async validate(): Promise<ValidationResult> {
    const results = await this.runBenchmarks();

    return {
      category: 'Performance',
      passed: results.every(r => r.withinLimit),
      details: results,
      metrics: this.calculateMetrics(results)
    };
  }

  private async runBenchmarks(): Promise<BenchmarkResult[]> {
    const results = [];

    // Test command execution times
    for (const [cmd, limit] of Object.entries(this.benchmarks.commandExecution)) {
      const start = Date.now();
      await this.simulateCommand(cmd);
      const duration = Date.now() - start;

      results.push({
        operation: `Command: ${cmd}`,
        duration,
        limit,
        withinLimit: duration < limit
      });
    }

    return results;
  }
}
```

## Self-Test Execution

### Via Validate Command
```bash
# Quick self-test
/validate

# Deep self-test
/validate --deep

# Component-specific test
/validate --component=agents
/validate --component=commands
/validate --component=integration

# With auto-fix
/validate --fix
```

### Programmatic Execution
```typescript
class FrameworkSelfTest {
  private validators = {
    structure: new StructuralValidator(),
    agents: new AgentValidator(),
    commands: new CommandValidator(),
    integration: new IntegrationValidator(),
    performance: new PerformanceValidator()
  };

  async runComplete(): Promise<TestReport> {
    console.log('Starting ClaudeCraftsman self-test...\n');

    const results = {};
    let totalPassed = 0;
    let totalFailed = 0;

    for (const [category, validator] of Object.entries(this.validators)) {
      console.log(`Testing ${category}...`);
      const result = await validator.validate();
      results[category] = result;

      if (result.passed) {
        console.log(`✓ ${category} PASSED\n`);
        totalPassed++;
      } else {
        console.log(`✗ ${category} FAILED\n`);
        totalFailed++;
      }
    }

    return {
      timestamp: new Date().toISOString(),
      frameworkVersion: '1.0',
      summary: {
        totalCategories: Object.keys(this.validators).length,
        passed: totalPassed,
        failed: totalFailed
      },
      results,
      recommendation: this.getRecommendation(results)
    };
  }
}
```

## Self-Healing Capabilities

### Automatic Fixes
```typescript
class FrameworkHealer {
  async healFramework(issues: Issue[]): Promise<HealingReport> {
    const fixes = [];

    for (const issue of issues) {
      const fix = await this.attemptFix(issue);
      fixes.push(fix);
    }

    return {
      attempted: fixes.length,
      successful: fixes.filter(f => f.success).length,
      failed: fixes.filter(f => !f.success),
      details: fixes
    };
  }

  private async attemptFix(issue: Issue): Promise<Fix> {
    switch (issue.type) {
      case 'missing-directory':
        return this.createMissingDirectory(issue.path);

      case 'missing-file':
        return this.createMissingFile(issue.path, issue.template);

      case 'invalid-configuration':
        return this.fixConfiguration(issue.path, issue.expected);

      case 'permission-error':
        return this.fixPermissions(issue.path);

      default:
        return {
          issue,
          success: false,
          reason: 'No automatic fix available'
        };
    }
  }
}
```

## Continuous Self-Testing

### Automated Schedule
```typescript
class ContinuousTesting {
  private schedule = {
    quick: '0 * * * *',      // Every hour
    deep: '0 0 * * *',       // Daily at midnight
    performance: '0 0 * * 0'  // Weekly on Sunday
  };

  async setupSchedule(): Promise<void> {
    // Quick tests every hour
    this.scheduleTest('quick', this.schedule.quick, async () => {
      await this.runTest('quick');
    });

    // Deep tests daily
    this.scheduleTest('deep', this.schedule.deep, async () => {
      await this.runTest('deep');
      await this.cleanupOldReports();
    });

    // Performance tests weekly
    this.scheduleTest('performance', this.schedule.performance, async () => {
      await this.runTest('performance');
      await this.generateTrendReport();
    });
  }
}
```

## Test Result Visualization

### Dashboard Output
```
ClaudeCraftsman Framework Health Dashboard
==========================================

Overall Health: 94% ████████████████████░

Categories:
├─ Structure:     100% ████████████████████
├─ Agents:        95%  ███████████████████░
├─ Commands:      100% ████████████████████
├─ Integration:   85%  █████████████████░░░
└─ Performance:   90%  ██████████████████░░

Recent Issues:
- Integration: MCP connection timeout (2 hours ago)
- Performance: /design command exceeded benchmark (1 day ago)

Recommendations:
1. Restart MCP servers to resolve connection issues
2. Clear cache to improve command performance
3. Run deep validation to identify other issues

Last Test: 2025-08-04 10:30:00
Next Test: 2025-08-04 11:00:00 (in 30 minutes)
```

## Success Criteria

The framework self-test passes when:
- All structural checks pass (100%)
- Agent validation >95%
- Command validation >95%
- Integration tests >90%
- Performance within benchmarks
- No critical issues detected

---

*A self-aware framework is a healthy framework. Test continuously, heal automatically.*
