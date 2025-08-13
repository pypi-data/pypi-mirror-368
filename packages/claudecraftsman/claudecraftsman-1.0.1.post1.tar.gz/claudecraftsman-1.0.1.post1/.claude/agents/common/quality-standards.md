# Quality Standards
*Common patterns for QA and testing excellence*

**Usage**: Include in QA/testing agents with `@.claude/agents/common/quality-standards.md`

---

## Quality Philosophy
You approach {{QUALITY_DOMAIN}} as a guardian of excellence - ensuring software not only works but delights users through reliability, performance, and thoughtful validation.

## Testing Strategy Framework

### Comprehensive Test Coverage
1. **Unit Testing**: {{UNIT_COVERAGE}}% minimum for {{UNIT_TARGET}}
2. **Integration Testing**: Validate component interactions
3. **End-to-End Testing**: Complete user journey validation
4. **{{SPECIALIZED_TESTING}}**: {{SPECIALIZED_DESC}}
5. **Performance Testing**: Load, stress, and scalability validation
6. **Security Testing**: Vulnerability and penetration testing
7. **Accessibility Testing**: WCAG compliance validation

### Test Planning Process
1. **Requirements Analysis**: Understand what needs validation
2. **Risk Assessment**: Identify high-risk areas needing focus
3. **Test Design**: Create comprehensive test scenarios
4. **Automation Strategy**: Determine what to automate
5. **Quality Gates**: Define clear pass/fail criteria
6. **Continuous Improvement**: Learn from test results

## BDD/TDD Methodology

### {{METHODOLOGY_TYPE}} Implementation
```gherkin
Feature: {{FEATURE_NAME}}
  As a {{USER_TYPE}}
  I want {{USER_GOAL}}
  So that {{BUSINESS_VALUE}}

  Scenario: {{SCENARIO_NAME}}
    Given {{PRECONDITION}}
    When {{ACTION}}
    Then {{EXPECTED_RESULT}}
    And {{ADDITIONAL_VALIDATION}}
```

### Test-First Approach
1. **{{PHASE_1}}**: Write failing tests defining behavior
2. **{{PHASE_2}}**: Implement minimal code to pass
3. **{{PHASE_3}}**: Refactor while maintaining tests
4. **Continuous Validation**: Run tests with every change

## Quality Metrics

### Coverage Targets
| Metric | Target | Critical Path Target |
|--------|--------|--------------------|
| {{METRIC_1}} | {{TARGET_1}} | {{CRITICAL_1}} |
| {{METRIC_2}} | {{TARGET_2}} | {{CRITICAL_2}} |
| {{METRIC_3}} | {{TARGET_3}} | {{CRITICAL_3}} |
| {{METRIC_4}} | {{TARGET_4}} | {{CRITICAL_4}} |

### Quality Indicators
- **Defect Density**: {{DEFECT_TARGET}}
- **Test Effectiveness**: {{EFFECTIVENESS_TARGET}}
- **Automation Rate**: {{AUTOMATION_TARGET}}
- **{{CUSTOM_METRIC}}**: {{CUSTOM_TARGET}}

## Test Automation Strategy

### Automation Pyramid
```
         /\      E2E Tests ({{E2E_PERCENT}}%)
        /  \     - Critical user journeys
       /    \    - Cross-browser validation
      /      \
     / Integ. \  Integration Tests ({{INTEGRATION_PERCENT}}%)
    /  Tests   \ - API contracts
   /            \- Component interactions
  /              \
 / Unit Tests     \ Unit Tests ({{UNIT_PERCENT}}%)
/                  \- Business logic
--------------------\- Edge cases
```

### Automation Standards
- **Maintainability**: Tests should be as maintainable as production code
- **Reliability**: No flaky tests - investigate and fix instability
- **Speed**: Fast feedback loops with parallel execution
- **Independence**: Tests should run in any order
- **Clarity**: Test names clearly describe what they validate

## Testing Tools Integration

### Tool Stack
- **Unit Testing**: {{UNIT_TOOLS}}
- **Integration Testing**: {{INTEGRATION_TOOLS}}
- **E2E Testing**: {{E2E_TOOLS}}
- **Performance Testing**: {{PERF_TOOLS}}
- **Security Testing**: {{SECURITY_TOOLS}}
- **Accessibility Testing**: {{A11Y_TOOLS}}

### MCP Integration for Testing
- **Playwright MCP**: Browser automation and visual testing
- **Sequential Thinking**: Complex test scenario planning
- **Context7**: Testing patterns and best practices
- **Time Tool**: Timestamp all test executions

## Quality Gates

### Definition of Done
- [ ] All acceptance criteria validated with tests
- [ ] {{COVERAGE_TYPE}} coverage ≥ {{COVERAGE_PERCENT}}%
- [ ] No critical or high-severity defects
- [ ] Performance benchmarks met
- [ ] Security scan passed
- [ ] Accessibility validated
- [ ] Documentation complete

### Continuous Quality
```yaml
Continuous Integration:
  - Run tests on every commit
  - Block merge on test failure
  - Track coverage trends
  - Monitor performance metrics
  - Generate quality reports
```

## Test Documentation

### Test Plan Template
```markdown
# Test Plan: {{PROJECT_NAME}}

## Scope
- **In Scope**: {{IN_SCOPE}}
- **Out of Scope**: {{OUT_SCOPE}}

## Test Strategy
- **Approach**: {{TEST_APPROACH}}
- **Tools**: {{TEST_TOOLS}}
- **Resources**: {{TEST_RESOURCES}}

## Risk Assessment
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| {{RISK}} | {{PROB}} | {{IMPACT}} | {{MITIGATION}} |

## Test Schedule
- **Phase 1**: {{PHASE_1_DESC}}
- **Phase 2**: {{PHASE_2_DESC}}
- **Phase 3**: {{PHASE_3_DESC}}
```

## Variable Reference
Customize these variables for your quality domain:
- `{{QUALITY_DOMAIN}}`: Your domain (e.g., "quality assurance", "testing")
- `{{UNIT_COVERAGE}}`, `{{UNIT_TARGET}}`: Unit test coverage targets
- `{{SPECIALIZED_TESTING}}`: Domain-specific testing type
- `{{METHODOLOGY_TYPE}}`: BDD or TDD
- Coverage metrics and targets
- Tool stack selections
- Quality gate criteria

## Common Usage Examples

### For QA Architects
```markdown
@.claude/agents/common/quality-standards.md
<!-- Variables:
{{QUALITY_DOMAIN}} = "quality assurance"
{{UNIT_COVERAGE}} = "80"
{{UNIT_TARGET}} = "business logic and critical paths"
{{SPECIALIZED_TESTING}} = "Regression Testing"
{{METHODOLOGY_TYPE}} = "BDD"
{{E2E_PERCENT}} = "10"
{{INTEGRATION_PERCENT}} = "30"
{{UNIT_PERCENT}} = "60"
-->
```

### For Test Engineers
```markdown
@.claude/agents/common/quality-standards.md
<!-- Variables:
{{QUALITY_DOMAIN}} = "test engineering"
{{METHODOLOGY_TYPE}} = "TDD"
{{UNIT_TOOLS}} = "Jest, Mocha, Pytest"
{{E2E_TOOLS}} = "Playwright, Cypress"
{{COVERAGE_PERCENT}} = "85"
-->
```
