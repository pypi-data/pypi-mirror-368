# ClaudeCraftsman Best Practices
*Patterns and principles for artisanal software development*

## Overview

This guide presents battle-tested patterns and practices that embody the ClaudeCraftsman philosophy. These aren't just recommendations - they're the distilled wisdom of crafting excellent software with intention and care.

## Core Principles

### 1. Evidence Over Assumptions
```markdown
❌ "This should improve performance"
✅ "Benchmarks show 40% reduction in response time"

❌ "Users probably want this feature"
✅ "User research indicates 73% need this capability"
```

**Practice**: Always use MCP tools to validate claims:
- `searxng` for market research
- `crawl4ai` for documentation
- `context7` for library best practices
- `time` for current context

### 2. Design Before Implementation
```markdown
❌ Jump straight into coding
✅ /plan or /design → /implement → /test → /deploy
```

**Practice**: Let requirements drive architecture:
- Simple features: `/plan` for quick analysis
- Complex systems: `/design` for comprehensive research
- Always document decisions and rationale

### 3. Quality at Every Layer
```markdown
❌ "We'll add tests later"
✅ TDD/BDD from the start with qa-architect

❌ "Good enough for now"
✅ Every component meets craftsman standards
```

**Practice**: Non-negotiable quality gates:
- 80%+ unit test coverage
- Integration tests for all APIs
- E2E tests for critical user journeys
- Performance benchmarks established

## Command Usage Patterns

### Choosing the Right Command

**Pattern: Scope-Driven Selection**
```bash
# Single component
/add agent security-architect         # ✅ Right tool for the job
/design security-architect-agent      # ❌ Overkill for single component

# Feature development
/plan user-notifications              # ✅ Appropriate analysis level
/design user-notifications            # ❌ Unnecessary complexity

# Platform development
/design marketplace-platform          # ✅ Needs market research
/plan marketplace-platform           # ❌ Insufficient analysis
```

### Command Chaining

**Pattern: Natural Workflow Progression**
```bash
# Feature Development Flow
/plan payment-integration
  ↓ (output: PLAN-payment-integration-2025-08-04.md)
/implement PLAN-payment-integration-2025-08-04.md
  ↓ (coordinated implementation)
/test payment-integration
  ↓ (comprehensive test suite)
/deploy payment-service --env=staging
  ↓ (staged rollout)
/deploy payment-service --env=production --strategy=canary
```

### Multi-Agent Coordination

**Pattern: Let Workflow Handle Complexity**
```bash
# ❌ Manual agent coordination
"Hey product-architect, create a PRD"
"Now design-architect, create tech spec"
"Finally backend-architect, implement"

# ✅ Automated workflow
/workflow design-to-deploy new-feature
```

## Agent Collaboration Patterns

### Sequential Handoffs
**Pattern: Preserve Context Through Transitions**
```markdown
Product-Architect completes PRD
  ↓ HANDOFF includes:
  - Business requirements
  - User research findings
  - Success metrics
  - Key decisions made

Design-Architect receives context
  ↓ HANDOFF includes:
  - Technical specifications
  - Architecture decisions
  - Integration requirements
  - Risk assessments
```

### Parallel Work Streams
**Pattern: Maximize Efficiency Without Conflicts**
```markdown
After Design-Architect:
  ├─ Backend-Architect: API implementation
  ├─ Frontend-Developer: UI components
  └─ Data-Architect: Schema design

Coordination Points:
  - Shared data models
  - API contracts
  - Integration tests
```

### Domain Expertise Respect
**Pattern: Use Agents for Their Strengths**
```bash
# ✅ Correct agent usage
ML feature → ml-architect
Database optimization → data-architect
API design → backend-architect
UI components → frontend-developer

# ❌ Wrong agent usage
Database design → frontend-developer
UI accessibility → backend-architect
```

## Development Patterns

### Test-Driven Development

**Pattern: qa-architect Leads Quality**
```typescript
// 1. qa-architect designs test strategy
describe('PaymentService', () => {
  it('should process valid payments', async () => {
    // Test specification before implementation
  });

  it('should handle payment failures gracefully', async () => {
    // Edge case coverage from the start
  });
});

// 2. backend-architect implements to pass tests
class PaymentService {
  async processPayment(data: PaymentData): Promise<PaymentResult> {
    // Implementation driven by tests
  }
}
```

### Progressive Enhancement

**Pattern: Build in Layers**
```markdown
1. Core Functionality (MVP)
   - Essential features only
   - Basic error handling
   - Minimal UI

2. Enhanced Features
   - Advanced capabilities
   - Comprehensive error handling
   - Polished UI

3. Optimization Layer
   - Performance tuning
   - Caching strategies
   - Advanced UX
```

### API Design First

**Pattern: Contract Before Implementation**
```yaml
# design-architect creates API spec first
openapi: 3.0.0
paths:
  /users:
    post:
      summary: Create new user
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUserDto'
      responses:
        201:
          description: User created successfully
```

## Quality Patterns

### Comprehensive Validation

**Pattern: Multi-Layer Quality Checks**
```bash
# Before deployment
/validate                    # Framework health
/test my-feature            # Feature tests
/validate --component=git   # Git status
/deploy --dry-run          # Deployment preview
```

### Performance Budgets

**Pattern: Define Metrics Early**
```typescript
// Set in design phase
const performanceBudgets = {
  pageLoad: { target: 3000, critical: 5000 },  // ms
  apiResponse: { target: 200, critical: 500 },  // ms
  bundleSize: { target: 500, critical: 750 },   // KB
  memoryUsage: { target: 100, critical: 200 }  // MB
};

// Enforce throughout development
/test my-app --type=performance --budgets=performance-budgets.json
```

### Security by Default

**Pattern: Security in Every Phase**
```markdown
Design Phase:
- Threat modeling with security-architect
- Authentication/authorization planning
- Data encryption requirements

Implementation:
- Secure coding practices
- Input validation
- OWASP compliance

Testing:
- Security scanning
- Penetration testing
- Vulnerability assessment

Deployment:
- Secret management
- Network policies
- Monitoring and alerts
```

## Documentation Patterns

### Living Documentation

**Pattern: Documentation as Code**
```markdown
# ✅ Documentation next to code
src/
├── components/
│   ├── Button/
│   │   ├── Button.tsx
│   │   ├── Button.test.tsx
│   │   └── Button.md        # Component documentation
│   └── Card/
│       ├── Card.tsx
│       ├── Card.test.tsx
│       └── Card.md          # Component documentation

# Automated updates
/workflow update-docs        # Regenerates documentation
```

### Decision Records

**Pattern: Document Why, Not Just What**
```markdown
# ADR-001: Database Selection

## Status
Accepted

## Context
Need scalable database for user data with strong consistency.

## Decision
Use PostgreSQL with read replicas.

## Rationale
- ACID compliance for financial data
- Proven scalability to 10M+ users
- Strong ecosystem and tooling
- Team expertise

## Consequences
- Need to plan for replication lag
- Requires connection pooling at scale
```

## Deployment Patterns

### Progressive Rollout

**Pattern: Risk Mitigation Through Gradual Deployment**
```bash
# 1. Development environment
/deploy my-app --env=development

# 2. Staging with full testing
/deploy my-app --env=staging
/test my-app --env=staging --type=all

# 3. Production canary
/deploy my-app --env=production --strategy=canary
# 1% → 5% → 25% → 50% → 100%

# 4. Monitor and validate
/validate --component=monitoring
```

### Feature Flags

**Pattern: Decouple Deployment from Release**
```typescript
// Design phase: Plan feature flags
interface FeatureFlags {
  newCheckoutFlow: {
    enabled: boolean;
    rolloutPercentage: number;
    userGroups: string[];
  };
}

// Implementation: Use flags
if (featureFlags.newCheckoutFlow.enabled) {
  return <NewCheckoutFlow />;
} else {
  return <LegacyCheckoutFlow />;
}

// Deployment: Safe rollout
/deploy my-app --feature-flags=progressive
```

## Anti-Patterns to Avoid

### 1. Skipping Planning
```bash
# ❌ Wrong
"Let's just start coding and figure it out"

# ✅ Right
/plan feature-name  # Even for "simple" features
```

### 2. Manual Agent Coordination
```bash
# ❌ Wrong
"First run product-architect, then manually copy to design-architect..."

# ✅ Right
/workflow design-to-deploy feature-name
```

### 3. Ignoring Test Failures
```bash
# ❌ Wrong
/deploy my-app --skip-tests  # Never do this

# ✅ Right
/test my-app
# Fix all failures
/deploy my-app
```

### 4. Premature Optimization
```bash
# ❌ Wrong
"Let's use microservices from day one"

# ✅ Right
Start monolithic → Measure → Split when needed
```

### 5. Documentation Debt
```bash
# ❌ Wrong
"We'll document it later"

# ✅ Right
Documentation is part of the implementation
```

## Framework Extension Patterns

### Adding Custom Agents

**Pattern: Extend Without Breaking**
```bash
# 1. Create agent following standards
/add agent mobile-architect

# 2. Define integration points
- Receives from: design-architect
- Hands off to: qa-architect
- Collaborates with: frontend-developer

# 3. Test integration
/workflow test-mobile-flow --agents=design,mobile,qa
```

### Custom Commands

**Pattern: Maintain Consistency**
```bash
# 1. Follow command patterns
/add command analyze

# 2. Include standard features
- Progress tracking
- Agent coordination
- Quality validation
- Documentation generation

# 3. Integrate with existing commands
- Works with /workflow
- Respects /validate
- Updates tracking files
```

## Performance Optimization Patterns

### Measure First

**Pattern: Data-Driven Optimization**
```bash
# 1. Establish baseline
/test my-app --type=performance --baseline

# 2. Identify bottlenecks
/analyze performance-report.json

# 3. Implement improvements
/implement performance-optimizations.md

# 4. Validate improvements
/test my-app --type=performance --compare-baseline
```

### Caching Strategy

**Pattern: Cache at Multiple Layers**
```markdown
1. CDN Layer
   - Static assets
   - API responses (where appropriate)

2. Application Layer
   - Computed values
   - Database query results

3. Database Layer
   - Query result caching
   - Materialized views

4. Client Layer
   - Local storage
   - Service workers
```

## Continuous Improvement

### Regular Validation

**Pattern: Proactive Health Checks**
```bash
# Daily
/validate --quick

# Weekly
/validate --deep
/test --type=all

# Monthly
/analyze --scope=project
/plan improvements
```

### Retrospectives

**Pattern: Learn and Improve**
```markdown
After each major feature:
1. What went well?
2. What could improve?
3. What did we learn?
4. How do we apply learnings?

Document in:
.claude/docs/retrospectives/RETRO-[feature]-[date].md
```

## Git Integration Patterns

### Semantic Commits

**Pattern: Meaningful Git History**
```bash
# Framework generates semantic commits
feat(auth): implement OAuth2 integration
test(auth): add OAuth2 integration tests
docs(auth): update authentication guide
fix(auth): resolve token refresh issue
```

### Branch Strategy

**Pattern: Feature Branch Workflow**
```bash
main
  ├─ feature/user-auth
  ├─ feature/payment-integration
  └─ fix/login-bug

# Automated by commands
/workflow creates feature branches
/deploy merges to main
```

## Success Metrics

### Framework Health

**Pattern: Regular Monitoring**
```markdown
Weekly Metrics:
- Command success rate: >95%
- Agent coordination: >90%
- Test coverage: >80%
- Deployment success: >99%
- Documentation coverage: 100%
```

### Project Quality

**Pattern: Continuous Measurement**
```markdown
Quality Indicators:
- Code review approval rate
- Bug discovery rate
- Performance benchmarks
- User satisfaction scores
- Team velocity trends
```

## Conclusion

These best practices aren't rigid rules but guiding principles that help maintain the craftsman standard. Every project is unique, but these patterns provide a foundation for excellence.

Remember: **We're not just writing code; we're crafting solutions that serve real people with real needs.**

---

*"Best practices are discovered, not dictated. Let your craftsmanship guide you."*
