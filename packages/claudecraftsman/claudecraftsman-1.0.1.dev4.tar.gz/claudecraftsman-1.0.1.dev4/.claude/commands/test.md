---
name: test
description: Comprehensive testing workflows leveraging qa-architect expertise. Creates and executes test strategies covering unit, integration, E2E, and performance testing with craftsman quality standards.
---

# Test Command

_Systematic quality validation with craftsman excellence_

## Quick Start Examples

### BDD Workflow
```bash
# Generate BDD scenarios from requirements
/test user-registration --bdd

# Output: Gherkin scenarios with step definitions
Feature: User Registration
  Background:
    Given the registration page is accessible

  Scenario: Successful registration
    When a new user completes registration
    Then account should be created
    And welcome email should be sent
```

### TDD Workflow
```bash
# Start with failing tests
/test calculate-discount --tdd

# Process:
1. Write failing test (RED)
2. Implement minimal code (GREEN)
3. Refactor with confidence (REFACTOR)
4. Repeat until feature complete
```

### Playwright E2E Testing
```bash
# Generate E2E tests with Playwright
/test checkout-flow --playwright

# Creates:
- Cross-browser test suite
- Visual regression tests
- Performance measurements
- Accessibility validation
```

## Philosophy

Testing is not about finding bugs; it's about building confidence. The test command orchestrates comprehensive quality validation through systematic test strategies, automated execution, and continuous quality assurance. Every test suite reflects our commitment to delivering software that users can trust.

## Usage Patterns

- `/test [feature]` - Create comprehensive test suite for a feature
- `/test [feature] --type=unit|integration|e2e|performance` - Specific test type
- `/test [feature] --bdd` - Generate BDD scenarios with Gherkin
- `/test [feature] --tdd` - Test-first development workflow
- `/test [feature] --playwright` - Browser automation tests
- `/test [feature] --run` - Execute existing test suites
- `/test [feature] --coverage` - Generate coverage reports
- `/test [feature] --update` - Update tests for code changes
- `/test [feature] --visual` - Visual regression testing

## Core Capabilities

### Test Strategy Orchestration with MCP Tools

The test command coordinates comprehensive testing with modern tooling:

- **Multi-layer testing** with unit, integration, E2E, and performance tests
- **Test automation** with maintainable, reliable test suites
- **Coverage analysis** ensuring critical paths are validated
- **Performance benchmarking** establishing and monitoring baselines
- **Accessibility validation** ensuring inclusive software
- **Playwright integration** via `mcp__playwright` for browser automation
- **BDD/TDD workflows** with Gherkin scenarios and test-first development

### Playwright MCP Integration

```markdown
E2E Testing with mcp__playwright:
├── Cross-browser testing (Chrome, Firefox, Safari, Edge)
├── Visual regression testing with screenshots
├── Performance metrics during test execution
├── Accessibility validation (WCAG compliance)
├── Mobile device emulation
└── Network condition simulation

Example capabilities:
- browser_navigate: Navigate to URLs
- browser_click: Interact with elements
- browser_type: Fill forms and inputs
- browser_snapshot: Capture page state
- browser_wait_for: Handle async operations
```

### Testing Process with BDD/TDD Integration

1. **Requirements Analysis**: Extract testable criteria from specifications
   - Convert user stories to Gherkin scenarios
   - Define acceptance criteria with stakeholders

2. **Risk Assessment**: Identify high-risk areas requiring focused testing
   - Use `mcp__searxng` to research common vulnerabilities
   - Prioritize based on business impact

3. **TDD Red-Green-Refactor Cycle**:
   ```gherkin
   # BDD Scenario Example
   Feature: User Authentication
     Scenario: Successful login with valid credentials
       Given a registered user with email "user@example.com"
       When they enter valid credentials
       And click the login button
       Then they should be redirected to dashboard
       And see a welcome message
   ```

4. **Test Implementation**: Generate test cases covering all scenarios
   - Unit tests with framework-specific tools
   - Integration tests for API contracts
   - E2E tests using `mcp__playwright`

5. **Execution Management**: Run tests with proper reporting
   - Parallel test execution for speed
   - Real-time progress tracking
   - Failure analysis and debugging

6. **Quality Validation**: Ensure coverage and performance targets
   - Code coverage analysis (target: 80%+)
   - Performance benchmarks validation
   - Accessibility compliance checks

7. **Continuous Monitoring**: Track quality metrics over time
   - Test execution trends
   - Coverage evolution
   - Performance regression detection

## Agent Integration

### Primary Agent: qa-architect with MCP Integration

The test command leverages qa-architect with full MCP tool access:

- **Test Strategy Design**: Comprehensive planning based on risk analysis
  - Research current testing best practices via `mcp__searxng__searxng_web_search`
  - Access testing framework documentation via `mcp__context7__get-library-docs`
  - Time-stamp all test documentation with `mcp__time__get_current_time`
- **BDD/TDD Implementation**: Behavior and test-driven methodologies
- **Tool Selection**: Choosing appropriate testing frameworks
- **Quality Metrics**: Defining meaningful quality indicators
- **Performance Baselines**: Establishing acceptable thresholds

### Supporting Agents

- **backend-architect**: API contract testing and backend validation
- **frontend-developer**: UI testing and user experience validation
- **data-architect**: Database testing and data integrity validation
- **ml-architect**: Model testing and ML pipeline validation

## Test Types and Strategies

### Unit Testing

```markdown
Unit Test Focus:
├── Isolated component testing
├── Fast, deterministic execution
├── High code coverage (minimum 80%)
├── Clear test naming and structure
└── Effective mocking strategies
```

**Generated Test Example:**

```typescript
describe("UserService", () => {
  describe("createUser", () => {
    it("should create user with valid data", async () => {
      // Arrange
      const userData = { name: "Test User", email: "test@example.com" };
      const mockRepository = createMockRepository();

      // Act
      const result = await userService.createUser(userData);

      // Assert
      expect(result).toBeDefined();
      expect(result.id).toBeTruthy();
      expect(mockRepository.save).toHaveBeenCalledWith(userData);
    });

    it("should validate email format", async () => {
      // Test invalid email handling
    });
  });
});
```

### Integration Testing

```markdown
Integration Test Focus:
├── Component interaction validation
├── API contract testing
├── Database transaction testing
├── External service integration
└── Error propagation handling
```

### End-to-End Testing

```markdown
E2E Test Focus:
├── User journey validation
├── Cross-browser compatibility
├── Mobile responsiveness
├── Performance during workflows
└── Visual regression testing
```

**Playwright Integration:**

```typescript
test("user authentication flow", async ({ page }) => {
  // Navigate to login
  await page.goto("/login");

  // Perform login
  await page.fill('[data-testid="email"]', "user@example.com");
  await page.fill('[data-testid="password"]', "password");
  await page.click('[data-testid="login-button"]');

  // Verify successful login
  await expect(page).toHaveURL("/dashboard");
  await expect(page.locator('[data-testid="welcome-message"]')).toBeVisible();
});
```

### Performance Testing

```markdown
Performance Test Categories:
├── Load Testing: Normal traffic validation
├── Stress Testing: Breaking point identification
├── Spike Testing: Traffic surge handling
├── Endurance Testing: Long-term stability
└── Scalability Testing: Growth accommodation
```

## Quality Metrics and Reporting

### Coverage Targets

```markdown
Coverage Requirements:
├── Unit Tests: 80% minimum coverage
├── Integration Tests: Critical paths covered
├── E2E Tests: User journeys validated
├── Performance Tests: All endpoints benchmarked
└── Security Tests: Vulnerability scanning complete
```

### Test Report Generation

Automatic generation of comprehensive test reports:

```markdown
Test Execution Report:
├── Summary: Pass/fail statistics
├── Coverage: Line, branch, function coverage
├── Performance: Response time percentiles
├── Failures: Detailed failure analysis
├── Trends: Historical comparison
└── Recommendations: Quality improvements
```

## MCP Tool Integration

### Playwright MCP for E2E Testing

```markdown
Playwright Capabilities:

- Multi-browser testing (Chrome, Firefox, Safari, Edge)
- Mobile device emulation
- Network request interception
- Screenshot and video capture
- Accessibility validation
```

### Sequential Thinking for Test Planning

Complex test scenario planning with systematic analysis:

- Test case generation from requirements
- Edge case identification
- Test data design
- Dependency mapping

## File Organization

### Test Structure

```markdown
Test files organized by type and feature:
.claude/tests/
├── unit/
│ ├── [feature]/
│ │ └── [component].test.ts
├── integration/
│ ├── api/
│ │ └── [endpoint].test.ts
│ └── services/
│ └── [service].test.ts
├── e2e/
│ ├── [user-journey].spec.ts
│ └── fixtures/
└── performance/
└── [scenario].perf.ts
```

### Test Documentation

```markdown
Documentation structure:
.claude/docs/current/testing/
├── TEST-STRATEGY-[feature]-[YYYY-MM-DD].md
├── TEST-CASES-[feature]-[YYYY-MM-DD].md
├── TEST-RESULTS-[run-id]-[YYYY-MM-DD].md
└── COVERAGE-REPORT-[feature]-[YYYY-MM-DD].md
```

## CI/CD Integration

### Continuous Testing Pipeline

```yaml
# Example CI/CD integration
test-pipeline:
  stages:
    - unit-tests:
        coverage-threshold: 80%
        fail-fast: true
    - integration-tests:
        parallel: true
        retry: 2
    - e2e-tests:
        browsers: [chrome, firefox, safari]
        screenshots: on-failure
    - performance-tests:
        baseline-comparison: true
        alert-threshold: 10%
```

### Quality Gates

Automated quality validation before deployment:

- [ ] All tests passing
- [ ] Coverage targets met
- [ ] Performance within baselines
- [ ] No security vulnerabilities
- [ ] Accessibility standards met

## Error Handling and Debugging

### Test Failure Analysis

Systematic approach to test failures:

1. **Failure Categorization**: Environment, data, or code issue
2. **Root Cause Analysis**: Systematic investigation
3. **Fix Verification**: Ensure fix doesn't break other tests
4. **Regression Prevention**: Add tests for failure scenario

### Debugging Support

- **Detailed error messages** with stack traces
- **Screenshot capture** at failure point
- **Network request logs** for API issues
- **Performance profiling** for slow tests
- **Test replay capability** for intermittent failures

## Success Criteria

### Test Suite Completion

A test suite is complete when:

- [ ] All acceptance criteria have corresponding tests
- [ ] Edge cases and error scenarios covered
- [ ] Performance benchmarks established
- [ ] Security vulnerabilities tested
- [ ] Accessibility standards validated
- [ ] Documentation complete with examples
- [ ] CI/CD integration configured

### Quality Validation

Every test suite must demonstrate:

- **Reliability**: Tests are deterministic and stable
- **Maintainability**: Clear structure and naming
- **Performance**: Fast execution without flakiness
- **Coverage**: Comprehensive validation of functionality

## Usage Examples

### Feature Test Suite Creation

```bash
/test user-authentication

# Generates:
# - Unit tests for auth service methods
# - Integration tests for auth API endpoints
# - E2E tests for login/logout flows
# - Performance tests for auth operations
# - Security tests for vulnerabilities
```

### Specific Test Type

```bash
/test payment-processing --type=e2e

# Focuses on:
# - User payment workflows
# - Multiple payment method testing
# - Error handling scenarios
# - Cross-browser validation
```

### Test Execution with Coverage

```bash
/test shopping-cart --run --coverage

# Executes all tests and generates:
# - Detailed test results
# - Code coverage report
# - Performance metrics
# - Quality recommendations
```

## Integration with Other Commands

### Command Workflow

```markdown
Development → Testing → Deployment Pipeline:
/implement → /test → /validate → /deploy
↓ ↓ ↓ ↓
Building Validating Verifying Releasing
```

### Quality Feedback Loop

- **From `/implement`**: Test requirements from implementation
- **To `/validate`**: Test results for validation
- **To `/deploy`**: Quality gates for deployment
- **Continuous**: Ongoing quality monitoring

## The Testing Commitment

The test command embodies our commitment to quality through systematic validation, comprehensive coverage, and continuous improvement. Every test we write serves as a guardian of user trust and software reliability.

**Remember**: Quality is not an accident; it's the result of intelligent effort and systematic validation. The test command ensures this effort is applied consistently and effectively throughout the development process.
