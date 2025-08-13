---
name: validate
description: Framework health checks and validation ensuring all components, agents, and integrations are functioning correctly. Provides comprehensive diagnostics and self-healing recommendations for the ClaudeCraftsman framework.
---

# Validate Command

_Framework health and integrity verification_

## Philosophy

A framework is only as strong as its weakest component. The validate command provides comprehensive health checks, ensuring every agent, command, and integration functions correctly. It serves as both a diagnostic tool and a quality guardian, maintaining the framework's operational excellence.

## Usage Patterns

- `/validate` - Run complete framework validation
- `/validate --component=agents|commands|mcp|structure` - Specific validation
- `/validate --fix` - Apply automatic fixes where possible
- `/validate --deep` - Extended validation with performance tests
- `/validate --report` - Generate detailed health report

## Core Capabilities

### Framework Validation

The validate command performs systematic checks:

- **Agent functionality** verification and integration testing
- **Command execution** validation and parameter checking
- **MCP tool integration** connectivity and response validation
- **File structure** compliance with framework standards
- **Quality standards** enforcement across all components

### Validation Process

1. **Component Discovery**: Inventory all framework components
2. **Syntax Validation**: Check all files for correct formatting
3. **Integration Testing**: Verify component interactions
4. **Performance Benchmarking**: Measure response times and efficiency
5. **Quality Assessment**: Validate craftsman standards compliance
6. **Issue Detection**: Identify problems and inconsistencies
7. **Recommendation Generation**: Provide fixes and improvements

## Validation Categories

### Agent Validation

```markdown
Agent Health Checks:
├── Metadata validation (name, description, model)
├── Template compliance verification
├── MCP tool integration testing
├── Inter-agent communication validation
├── Git workflow configuration check
└── Documentation completeness assessment
```

**Agent Test Suite:**

```typescript
interface AgentValidation {
  metadata: {
    hasValidName: boolean;
    hasDescription: boolean;
    modelSpecified: boolean;
    descriptionQuality: QualityScore;
  };

  structure: {
    followsTemplate: boolean;
    hasPhilosophy: boolean;
    hasMandatoryProcess: boolean;
    hasQualityGates: boolean;
  };

  integration: {
    mpcToolsConfigured: boolean;
    gitIntegrationPresent: boolean;
    handoffProtocolsDefined: boolean;
  };

  functionality: {
    canBeInvoked: boolean;
    respondsCorrectly: boolean;
    maintainsContext: boolean;
  };
}
```

### Command Validation

```markdown
Command Health Checks:
├── Command file structure validation
├── Usage pattern completeness
├── Parameter handling verification
├── Integration point testing
├── Documentation quality check
└── Example validation
```

### MCP Integration Validation

```markdown
MCP Tool Checks:
├── Time tool connectivity and response
├── Searxng search capability verification
├── Crawl4ai web fetching validation
├── Context7 documentation access
├── Playwright browser automation
└── Sequential thinking integration
```

**MCP Test Execution:**

```typescript
async function validateMCPTools() {
  const tests = {
    time: async () => {
      const result = await mcp.time.getCurrentTime("UTC");
      return result.datetime !== undefined;
    },

    searxng: async () => {
      const result = await mcp.searxng.search("test query");
      return result.results !== undefined;
    },

    playwright: async () => {
      const browser = await mcp.playwright.launch();
      const success = browser !== undefined;
      await browser.close();
      return success;
    },
  };

  return await runAllTests(tests);
}
```

### Structure Validation

```markdown
Directory Structure Checks:
.claude/
├── ✓ agents/ (all agent files present)
├── ✓ commands/ (all command files present)
├── ✓ docs/current/ (documentation organized)
├── ✓ context/ (context files maintained)
├── ✓ templates/ (reusable templates available)
└── ✓ tests/ (test suites present)
```

### Quality Standards Validation

```markdown
Quality Checks:
├── Documentation completeness
├── Citation standards compliance
├── Time awareness implementation
├── Research integration verification
├── File naming convention adherence
└── Craftsman philosophy alignment
```

## Diagnostic Reporting

### Health Report Generation

```markdown
# ClaudeCraftsman Framework Health Report

Generated: [Current DateTime from MCP]

## Overall Health: 95% ✅

### Component Status

- Agents: 12/12 operational ✅
- Commands: 10/10 functional ✅
- MCP Tools: 6/6 connected ✅
- File Structure: Compliant ✅

### Performance Metrics

- Average agent response: 120ms ✅
- Command execution time: 85ms ✅
- MCP tool latency: 200ms ✅

### Issues Detected

1. Minor: Outdated documentation in /docs/archive/

   - Impact: Low
   - Fix: Archive or update old documents

2. Warning: Slow response from ml-architect
   - Impact: Medium
   - Fix: Optimize ultrathink usage

### Recommendations

- Update framework.md with new agents
- Add integration tests for new commands
- Implement caching for MCP responses
```

## Self-Healing Capabilities

### Automatic Fixes

The validate command can automatically fix:

- **File permission issues**
- **Missing directory structures**
- **Outdated file references**
- **Broken symbolic links**
- **Configuration inconsistencies**

### Fix Application

```bash
/validate --fix

# Applies fixes for:
# - Creates missing directories
# - Updates file permissions
# - Fixes configuration issues
# - Regenerates corrupted indexes
# - Updates outdated references
```

## Performance Benchmarking

### Component Performance

```markdown
Performance Targets:
├── Agent invocation: < 200ms
├── Command execution: < 100ms
├── MCP tool response: < 500ms
├── File operations: < 50ms
└── Full validation: < 30s
```

### Benchmark Results

```typescript
interface BenchmarkResult {
  component: string;
  operation: string;
  averageTime: number;
  p95Time: number;
  p99Time: number;
  status: "pass" | "warning" | "fail";
  recommendation?: string;
}
```

## Integration Testing

### Cross-Component Validation

```markdown
Integration Test Scenarios:
├── Agent handoff simulation
├── Command chain execution
├── MCP tool coordination
├── File system operations
└── Git workflow integration
```

### Test Case Example

```typescript
async function testAgentHandoff() {
  // Simulate product-architect to design-architect handoff
  const context = await productArchitect.createPRD(project);
  const handoff = await workflowCoordinator.prepareHandoff(
    "product-architect",
    "design-architect",
    context
  );

  const result = await designArchitect.createTechSpec(handoff);

  return {
    contextPreserved: validateContext(context, result),
    qualityMaintained: validateQuality(result),
    handoffSuccessful: result.success,
  };
}
```

## Continuous Monitoring

### Scheduled Validation

```markdown
Validation Schedule:
├── Hourly: Quick health checks
├── Daily: Full component validation
├── Weekly: Deep performance analysis
├── Monthly: Comprehensive audit
└── On-demand: User triggered
```

### Alerting Integration

```typescript
interface ValidationAlert {
  severity: "info" | "warning" | "error" | "critical";
  component: string;
  issue: string;
  impact: string;
  recommendation: string;
  autoFixAvailable: boolean;
}
```

## Framework Evolution Support

### Version Compatibility

```markdown
Version Checks:
├── Framework version consistency
├── Agent compatibility matrix
├── Command version requirements
├── MCP tool version validation
└── Dependency version checking
```

### Migration Support

- **Version migration** assistance
- **Backward compatibility** validation
- **Deprecation warnings** for old patterns
- **Update recommendations** for improvements

## File Organization

### Validation Artifacts

```markdown
Validation structure:
.claude/validation/
├── reports/
│ ├── HEALTH-REPORT-[YYYY-MM-DD].md
│ └── BENCHMARK-[YYYY-MM-DD].json
├── logs/
│ ├── validation-[timestamp].log
│ └── errors-[timestamp].log
└── fixes/
└── applied-fixes-[YYYY-MM-DD].md
```

## Success Criteria

### Healthy Framework

A framework is healthy when:

- [ ] All agents respond correctly
- [ ] All commands execute successfully
- [ ] MCP tools are accessible
- [ ] File structure is compliant
- [ ] Performance meets benchmarks
- [ ] No critical issues detected
- [ ] Documentation is current

### Validation Excellence

Every validation must demonstrate:

- **Thoroughness**: Complete coverage of all components
- **Accuracy**: Reliable detection of issues
- **Actionability**: Clear fixes for problems
- **Performance**: Fast validation execution

## Usage Examples

### Complete Framework Validation

```bash
/validate

# Performs:
# - Full agent functionality tests
# - Command execution validation
# - MCP tool connectivity checks
# - Structure compliance verification
# - Performance benchmarking
# - Health report generation
```

### Component-Specific Validation

```bash
/validate --component=agents

# Validates:
# - All agent metadata
# - Template compliance
# - Integration capabilities
# - Documentation completeness
# - Performance metrics
```

### Deep Validation with Fixes

```bash
/validate --deep --fix

# Executes:
# - Extended performance tests
# - Integration scenario testing
# - Automatic issue resolution
# - Optimization recommendations
# - Detailed reporting
```

## Integration with Other Commands

### Validation Pipeline

```markdown
Development lifecycle integration:
/implement → /test → /validate → /deploy
↓ ↓ ↓ ↓
Building Testing Verifying Releasing
```

### Quality Assurance

- **Pre-deployment**: Validate before any deployment
- **Post-update**: Validate after framework changes
- **Continuous**: Regular scheduled validations
- **On-demand**: User-triggered health checks

## The Validation Commitment

The validate command embodies our commitment to operational excellence by ensuring the ClaudeCraftsman framework remains healthy, performant, and reliable. Every validation strengthens the foundation upon which great software is built.

**Remember**: A healthy framework is a productive framework. The validate command ensures our tools remain sharp, our processes remain smooth, and our standards remain high.
