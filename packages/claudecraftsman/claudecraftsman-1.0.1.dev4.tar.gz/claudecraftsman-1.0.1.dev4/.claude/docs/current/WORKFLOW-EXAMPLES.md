# ClaudeCraftsman Workflow Examples
*Real-world patterns for craftsman development*

## Table of Contents
- [New Feature Development](#new-feature-development)
- [Bug Fixing Workflow](#bug-fixing-workflow)
- [Documentation Workflow](#documentation-workflow)
- [Refactoring Workflow](#refactoring-workflow)
- [API Development](#api-development)
- [Frontend Component Creation](#frontend-component-creation)
- [Database Migration](#database-migration)
- [Performance Optimization](#performance-optimization)

## New Feature Development

### Complete Feature: User Authentication

```bash
# 1. Start with planning (medium complexity)
/plan user-authentication

# Output structure:
# - Requirements analysis
# - Implementation phases
# - Resource requirements
# - Success criteria

# 2. Review the plan, then implement
/implement user-authentication

# Real-time progress:
# Phase 1: Foundation [████████] 100% ✓
# Phase 2: Backend API [████░░░░] 50% ⟳
# Active: backend-architect
# Task: JWT implementation

# 3. Create comprehensive tests
/test user-authentication --bdd

# Generates:
# - Unit tests for auth service
# - Integration tests for API
# - E2E tests for login flow
# - Performance benchmarks

# 4. Validate everything
/validate user-authentication

# Checks:
# ✓ Code quality standards
# ✓ Test coverage (>80%)
# ✓ Documentation complete
# ✓ Security validated
```

### Complex System: E-Commerce Platform

```bash
# 1. For complex systems, start with design
/design ecommerce-platform --research=deep

# Conducts:
# - Market research (via mcp__searxng)
# - Competitive analysis
# - Technical architecture
# - Scalability planning

# 2. Break into features and plan
/plan shopping-cart
/plan payment-processing
/plan inventory-management

# 3. Implement systematically
/implement shopping-cart
# ... complete before moving to next

# 4. Integration testing
/test ecommerce-integration --type=e2e
```

## Bug Fixing Workflow

### Critical Bug: Login Timeout

```bash
# 1. Analyze the issue
/troubleshoot login-timeout --analyze

# Investigates:
# - Error logs analysis
# - Recent code changes
# - System metrics
# - User impact assessment

# 2. Create fix plan
/plan fix-login-timeout --type=bugfix

# 3. Implement with careful testing
/implement fix-login-timeout

# 4. Regression testing
/test login --type=regression --comprehensive

# 5. Document the fix
/document login-timeout-fix --type=postmortem
```

### Performance Bug: Slow API Response

```bash
# 1. Performance analysis
/analyze api-performance --type=performance

# 2. Optimization plan
/plan api-optimization --focus=performance

# 3. Implement improvements
/implement api-optimization

# 4. Performance validation
/test api --type=performance --benchmark
```

## Documentation Workflow

### API Documentation

```bash
# 1. Generate from code
/document api --type=openapi

# Creates:
# - OpenAPI specification
# - Interactive documentation
# - Code examples
# - Authentication guide

# 2. Add user guides
/document api-guides --type=tutorial

# 3. Create SDK documentation
/document sdk --languages=python,javascript
```

### Project Documentation

```bash
# 1. Comprehensive project docs
/document project-overview

# Generates:
# - README.md
# - Architecture documentation
# - Setup instructions
# - Contribution guidelines

# 2. Deployment documentation
/document deployment --type=runbook
```

## Refactoring Workflow

### Legacy Code Modernization

```bash
# 1. Analyze current state
/analyze legacy-payment-system

# 2. Create refactoring plan
/plan payment-refactor --type=refactoring

# Includes:
# - Risk assessment
# - Phase breakdown
# - Rollback strategy
# - Testing approach

# 3. Implement incrementally
/implement payment-refactor --phase=1
# Test and validate before next phase

# 4. Comprehensive testing
/test payment --type=regression --full-suite
```

### Code Quality Improvement

```bash
# 1. Quality analysis
/analyze code-quality --metrics

# 2. Improvement plan
/plan quality-improvement --focus=maintainability

# 3. Systematic improvements
/implement quality-improvement

# 4. Validate improvements
/validate code-quality --before-after
```

## API Development

### RESTful API Creation

```bash
# 1. Design API
/design user-api --type=rest

# 2. Implementation
/add agent api-builder  # If needed
/implement user-api

# 3. Testing
/test user-api --type=contract
/test user-api --type=integration

# 4. Documentation
/document user-api --type=openapi
```

### GraphQL API

```bash
# 1. Schema design
/design graphql-api --research=patterns

# 2. Implementation
/implement graphql-api

# 3. Testing
/test graphql-api --type=schema
/test graphql-api --type=resolver
```

## Frontend Component Creation

### Reusable Component Library

```bash
# 1. Design component system
/design component-library --type=ui

# 2. Create individual components
/add component button
/add component form-input
/add component data-table

# 3. Testing
/test components --type=visual
/test components --type=accessibility

# 4. Documentation
/document component-library --type=storybook
```

### Complex UI Feature

```bash
# 1. Plan the feature
/plan dashboard-analytics

# 2. Implement with progress
/implement dashboard-analytics

# 3. Cross-browser testing
/test dashboard --playwright --browsers=all

# 4. Performance testing
/test dashboard --type=performance --metrics=web-vitals
```

## Database Migration

### Schema Evolution

```bash
# 1. Analyze current schema
/analyze database-schema

# 2. Plan migration
/plan schema-migration --version=2.0

# 3. Generate migration scripts
/implement schema-migration

# Includes:
# - Migration scripts
# - Rollback scripts
# - Data transformation
# - Zero-downtime strategy

# 4. Test migration
/test migration --type=data-integrity
```

## Performance Optimization

### Full Stack Optimization

```bash
# 1. Performance audit
/analyze performance --full-stack

# 2. Optimization plan
/plan performance-optimization

# Covers:
# - Frontend bundle size
# - API response times
# - Database queries
# - Caching strategy

# 3. Implement improvements
/implement performance-optimization

# 4. Validate improvements
/test performance --before-after --metrics
```

## Advanced Patterns

### Multi-Agent Workflow

```bash
# Complex feature requiring coordination
/workflow design-to-deploy payment-system

# Coordinates:
# 1. product-architect: Requirements
# 2. system-architect: Architecture
# 3. backend-architect: API design
# 4. frontend-developer: UI implementation
# 5. qa-architect: Test strategy
# 6. devops-architect: Deployment
```

### Iterative Development

```bash
# Start simple, enhance iteratively
/add feature user-search    # MVP
/plan search-enhancement    # Add filters
/implement search-enhancement
/plan search-ai            # Add AI capabilities
/implement search-ai
```

## Best Practices

### Always Start with the Right Scope
- Single file → `/add`
- Feature → `/plan`
- System → `/design`

### Let Agents Do Their Jobs
- Trust domain expertise
- Don't micromanage
- Review at quality gates

### Maintain Momentum
- Complete phases before starting new ones
- Use `--status` to check progress
- Resume interrupted work with `--resume`

### Document as You Go
- Each phase includes documentation
- Time stamps via MCP tools
- Decisions tracked with rationale

## Troubleshooting Workflows

### When Things Go Wrong

```bash
# Check implementation status
/implement [feature] --status

# View detailed logs
/implement [feature] --verbose

# Debug specific phase
/implement [feature] --phase=2 --debug

# Resume after fixing issues
/implement [feature] --resume
```

### Getting Help

```bash
# Comprehensive help
/help

# Command-specific help
/help implement

# Framework status
/validate framework
```

Remember: Every workflow is designed to produce craftsman-quality results. Trust the process, and you'll create software that makes you proud.
