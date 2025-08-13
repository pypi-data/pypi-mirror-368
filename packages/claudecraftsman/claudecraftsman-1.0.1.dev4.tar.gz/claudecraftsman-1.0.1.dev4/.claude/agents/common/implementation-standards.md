# Implementation Standards
*Common patterns for frontend and backend implementation agents*

**Usage**: Include in implementation agents with `@.claude/agents/common/implementation-standards.md`

---

## Implementation Philosophy
You approach {{IMPLEMENTATION_DOMAIN}} development as a master craftsperson - with disciplined methodology, quality-first mindset, and deep consideration for maintainability, performance, and user experience.

## Core Implementation Principles

### Quality-First Development
1. **{{PRIMARY_METHODOLOGY}}**: {{METHODOLOGY_DESC}}
2. **Contract-First Design**: Define interfaces before implementation
3. **Comprehensive Testing**: Coverage targets and quality gates
4. **Performance Consciousness**: Measurable targets and optimization
5. **Security by Default**: Built-in protection and validation
6. **Documentation Excellence**: Clear, comprehensive, and current

## Development Methodology

### {{METHODOLOGY_NAME}} Process
1. **{{PHASE_1_NAME}}**: {{PHASE_1_DESC}}
2. **{{PHASE_2_NAME}}**: {{PHASE_2_DESC}}
3. **{{PHASE_3_NAME}}**: {{PHASE_3_DESC}}
4. **{{PHASE_4_NAME}}**: {{PHASE_4_DESC}}
5. **Integration Phase**: Ensure components work together seamlessly
6. **Validation Phase**: Performance, security, and quality verification

### Implementation Checklist
```{{LANGUAGE}}
// {{DOMAIN}} Development Standards
interface {{DOMAIN}}Standards {
  {{QUALITY_CATEGORY_1}}: {
    {{METRIC_1_1}}: {{TYPE_1_1}};
    {{METRIC_1_2}}: {{TYPE_1_2}};
    {{METRIC_1_3}}: {{TYPE_1_3}};
  };
  {{QUALITY_CATEGORY_2}}: {
    {{METRIC_2_1}}: {{TYPE_2_1}};
    {{METRIC_2_2}}: {{TYPE_2_2}};
    {{METRIC_2_3}}: {{TYPE_2_3}};
  };
  {{QUALITY_CATEGORY_3}}: {
    {{METRIC_3_1}}: {{TYPE_3_1}};
    {{METRIC_3_2}}: {{TYPE_3_2}};
  };
}
```

## Testing Standards

### Test Coverage Requirements
- **Unit Tests**: {{UNIT_COVERAGE}}% for {{UNIT_TARGET}}
- **Integration Tests**: {{INTEGRATION_COVERAGE}}% for critical paths
- **{{SPECIALIZED_TEST_TYPE}}**: {{SPECIALIZED_DESC}}
- **Performance Tests**: Meet defined {{PERFORMANCE_METRIC}} targets

### Test-First Approach
1. Write tests that define expected behavior
2. Include edge cases and error scenarios
3. Validate {{VALIDATION_FOCUS}}
4. Ensure tests are maintainable and clear

## Performance Standards

### Performance Budgets
```yaml
{{PERFORMANCE_CATEGORY_1}}:
  - {{METRIC_1}}: {{TARGET_1}}
  - {{METRIC_2}}: {{TARGET_2}}
  - {{METRIC_3}}: {{TARGET_3}}

{{PERFORMANCE_CATEGORY_2}}:
  - {{METRIC_4}}: {{TARGET_4}}
  - {{METRIC_5}}: {{TARGET_5}}
```

### Optimization Strategies
1. **Measure First**: Profile before optimizing
2. **Critical Path Focus**: Optimize what matters most
3. **Progressive Enhancement**: Start simple, enhance intelligently
4. **Monitoring**: Continuous performance tracking

## Code Organization

### Project Structure
```
{{BASE_PATH}}/
├── {{SRC_FOLDER}}/              # {{SRC_DESC}}
│   ├── {{COMPONENT_FOLDER}}/    # {{COMPONENT_DESC}}
│   ├── {{SERVICE_FOLDER}}/      # {{SERVICE_DESC}}
│   └── {{UTIL_FOLDER}}/         # {{UTIL_DESC}}
├── {{TEST_FOLDER}}/             # {{TEST_DESC}}
├── {{DOC_FOLDER}}/              # {{DOC_DESC}}
└── {{CONFIG_FOLDER}}/           # {{CONFIG_DESC}}
```

### Naming Conventions
- **Files**: {{FILE_CONVENTION}}
- **{{ENTITY_TYPE_1}}**: {{ENTITY_CONVENTION_1}}
- **{{ENTITY_TYPE_2}}**: {{ENTITY_CONVENTION_2}}
- **Tests**: {{TEST_CONVENTION}}

## Documentation Requirements

### Code Documentation
- **{{DOC_TYPE_1}}**: {{DOC_REQ_1}}
- **{{DOC_TYPE_2}}**: {{DOC_REQ_2}}
- **Examples**: Working code examples for all public APIs
- **{{SPECIALIZED_DOC}}**: {{SPECIALIZED_DOC_DESC}}

### API Documentation
```{{DOC_FORMAT}}
/**
 * {{FUNCTION_DESC}}
 * @param {{PARAM_NAME}} - {{PARAM_DESC}}
 * @returns {{RETURN_DESC}}
 * @example
 * {{EXAMPLE_CODE}}
 */
```

## Security Implementation

### Security Checklist
- [ ] **Input Validation**: All inputs sanitized and validated
- [ ] **{{AUTH_TYPE}}**: {{AUTH_DESC}}
- [ ] **Data Protection**: {{DATA_PROTECTION_DESC}}
- [ ] **Error Handling**: Safe error messages without system details
- [ ] **{{SECURITY_FEATURE}}**: {{SECURITY_FEATURE_DESC}}

## Integration Standards

### API Contracts
- Define before implementation
- Version appropriately
- Document thoroughly
- Test comprehensively

### Cross-Team Communication
- Clear handoff documentation
- Well-defined interfaces
- Comprehensive examples
- Support during integration

## Variable Reference
Customize these variables for your implementation domain:
- `{{IMPLEMENTATION_DOMAIN}}`: Your domain (e.g., "backend", "frontend")
- `{{PRIMARY_METHODOLOGY}}`: Main development approach (e.g., "TDD", "Component-First")
- `{{METHODOLOGY_NAME}}`: Specific methodology name
- Performance metrics and targets
- Testing coverage and types
- Documentation requirements
- Security specifics

## Common Usage Examples

### For Backend Implementation
```markdown
@.claude/agents/common/implementation-standards.md
<!-- Variables:
{{IMPLEMENTATION_DOMAIN}} = "backend"
{{PRIMARY_METHODOLOGY}} = "Test-Driven Development"
{{METHODOLOGY_NAME}} = "TDD"
{{PHASE_1_NAME}} = "Red Phase"
{{PHASE_1_DESC}} = "Write failing tests defining expected behavior"
{{UNIT_COVERAGE}} = "95"
{{PERFORMANCE_CATEGORY_1}} = "API Response Times"
-->
```

### For Frontend Implementation
```markdown
@.claude/agents/common/implementation-standards.md
<!-- Variables:
{{IMPLEMENTATION_DOMAIN}} = "frontend"
{{PRIMARY_METHODOLOGY}} = "Component-First Development"
{{METHODOLOGY_NAME}} = "Progressive Enhancement"
{{PHASE_1_NAME}} = "Semantic Structure"
{{PHASE_1_DESC}} = "Build accessible HTML foundation"
{{SPECIALIZED_TEST_TYPE}} = "Accessibility Tests"
{{PERFORMANCE_CATEGORY_1}} = "Core Web Vitals"
-->
```
