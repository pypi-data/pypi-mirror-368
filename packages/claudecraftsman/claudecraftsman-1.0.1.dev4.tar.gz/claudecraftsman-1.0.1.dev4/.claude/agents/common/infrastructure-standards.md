# Infrastructure Standards
*Common patterns for DevOps and infrastructure excellence*

**Usage**: Include in DevOps/infrastructure agents with `@.claude/agents/common/infrastructure-standards.md`

---

## Infrastructure Philosophy
You approach {{INFRASTRUCTURE_DOMAIN}} as a master craftsperson - creating systems that empower teams, ensure reliability, and deliver value continuously through thoughtful automation and resilient design.

## Infrastructure as Code (IaC)

### IaC Principles
1. **Declarative Over Imperative**: Describe desired state, not steps
2. **Version Control Everything**: All infrastructure in Git
3. **Immutable Infrastructure**: Replace, don't modify
4. **Environment Parity**: Dev/staging/prod consistency
5. **Automated Testing**: Test infrastructure changes

### IaC Standards
```yaml
{{IAC_TOOL}}:
  structure:
    - {{STRUCTURE_1}}
    - {{STRUCTURE_2}}
    - {{STRUCTURE_3}}

  standards:
    iac_coverage: {{IAC_COVERAGE}}%
    drift_detection: {{DRIFT_DETECTION}}
    state_management: {{STATE_MANAGEMENT}}
    module_reuse: {{MODULE_STANDARD}}
```

## Reliability Engineering

### SLO Framework
```yaml
Service Level Objectives:
  availability: {{AVAILABILITY_TARGET}}%
  latency:
    p50: < {{P50_TARGET}}ms
    p99: < {{P99_TARGET}}ms
  error_rate: < {{ERROR_TARGET}}%

Reliability Targets:
  mttr: < {{MTTR_TARGET}} minutes
  mtbf: > {{MTBF_TARGET}} days
  deployment_failure: < {{DEPLOY_FAIL_TARGET}}%
```

### Disaster Recovery
- **RPO**: {{RPO_TARGET}} (Recovery Point Objective)
- **RTO**: {{RTO_TARGET}} (Recovery Time Objective)
- **Backup Strategy**: {{BACKUP_STRATEGY}}
- **Failover**: {{FAILOVER_APPROACH}}

## CI/CD Excellence

### Pipeline Standards
```yaml
Pipeline Architecture:
  stages:
    - {{STAGE_1}}: {{STAGE_1_DESC}}
    - {{STAGE_2}}: {{STAGE_2_DESC}}
    - {{STAGE_3}}: {{STAGE_3_DESC}}
    - {{STAGE_4}}: {{STAGE_4_DESC}}

  quality_gates:
    - {{GATE_1}}: {{GATE_1_CRITERIA}}
    - {{GATE_2}}: {{GATE_2_CRITERIA}}
    - {{GATE_3}}: {{GATE_3_CRITERIA}}
```

### Deployment Strategies
1. **{{DEPLOY_STRATEGY_1}}**: {{STRATEGY_1_DESC}}
2. **{{DEPLOY_STRATEGY_2}}**: {{STRATEGY_2_DESC}}
3. **Rollback**: < {{ROLLBACK_TIME}} automated
4. **Feature Flags**: {{FEATURE_FLAG_APPROACH}}

## Observability Standards

### Three Pillars
1. **Metrics**
   - Coverage: {{METRICS_COVERAGE}}%
   - Retention: {{METRICS_RETENTION}}
   - Granularity: {{METRICS_GRANULARITY}}

2. **Logs**
   - Aggregation: {{LOG_AGGREGATION}}
   - Structure: {{LOG_STRUCTURE}}
   - Retention: {{LOG_RETENTION}}

3. **Traces**
   - Coverage: {{TRACE_COVERAGE}}
   - Sampling: {{TRACE_SAMPLING}}
   - Analysis: {{TRACE_ANALYSIS}}

### Alerting Philosophy
- **Alert Fatigue Prevention**: < {{ALERT_NOISE}}% false positives
- **Actionable Alerts**: Every alert has a runbook
- **Severity Levels**: {{SEVERITY_FRAMEWORK}}
- **Escalation**: {{ESCALATION_POLICY}}

## Security Automation

### DevSecOps Integration
```yaml
Security Automation:
  scanning:
    - {{SCAN_TYPE_1}}: {{SCAN_SCHEDULE_1}}
    - {{SCAN_TYPE_2}}: {{SCAN_SCHEDULE_2}}
    - {{SCAN_TYPE_3}}: {{SCAN_SCHEDULE_3}}

  compliance:
    framework: {{COMPLIANCE_FRAMEWORK}}
    automation: {{COMPLIANCE_AUTOMATION}}%
    reporting: {{COMPLIANCE_REPORTING}}

  secrets:
    management: {{SECRETS_TOOL}}
    rotation: {{ROTATION_SCHEDULE}}
    audit: {{AUDIT_FREQUENCY}}
```

## Container & Orchestration

### Container Standards
- **Base Images**: {{BASE_IMAGE_POLICY}}
- **Size Optimization**: < {{IMAGE_SIZE_TARGET}}
- **Security Scanning**: {{CONTAINER_SCANNING}}
- **Registry**: {{REGISTRY_STRATEGY}}

### Orchestration Platform
```yaml
{{ORCHESTRATION_PLATFORM}}:
  cluster_standards:
    - {{CLUSTER_STANDARD_1}}
    - {{CLUSTER_STANDARD_2}}
    - {{CLUSTER_STANDARD_3}}

  resource_management:
    requests: {{RESOURCE_REQUESTS}}
    limits: {{RESOURCE_LIMITS}}
    autoscaling: {{AUTOSCALING_POLICY}}
```

## Cost Optimization

### Cost Management
- **Visibility**: {{COST_VISIBILITY}}
- **Tagging Strategy**: {{TAGGING_STANDARD}}
- **Optimization Reviews**: {{REVIEW_FREQUENCY}}
- **Waste Reduction**: {{WASTE_TARGET}}

### Resource Efficiency
```yaml
Efficiency Targets:
  utilization:
    compute: > {{COMPUTE_UTIL}}%
    storage: > {{STORAGE_UTIL}}%
    network: optimized

  rightsizing:
    review: {{RIGHTSIZING_FREQUENCY}}
    automation: {{RIGHTSIZING_AUTO}}
```

## Documentation Standards

### Required Documentation
1. **Architecture Diagrams**: Current system design
2. **Runbooks**: Operational procedures
3. **Disaster Recovery Plans**: Recovery procedures
4. **Security Documentation**: Controls and compliance
5. **Cost Analysis**: Budget and optimization

### Documentation Format
```markdown
# {{DOC_TYPE}}: {{SYSTEM_NAME}}

## Overview
{{OVERVIEW_CONTENT}}

## Architecture
{{ARCHITECTURE_DESC}}

## Operations
- **Monitoring**: {{MONITORING_APPROACH}}
- **Alerting**: {{ALERTING_SETUP}}
- **Maintenance**: {{MAINTENANCE_WINDOWS}}

## Emergency Procedures
{{EMERGENCY_CONTACTS}}
{{ESCALATION_PROCEDURES}}
```

## Variable Reference
Customize these variables for your infrastructure domain:
- `{{INFRASTRUCTURE_DOMAIN}}`: Your domain (e.g., "DevOps", "SRE", "Platform")
- `{{IAC_TOOL}}`: Infrastructure as Code tool (Terraform, CloudFormation, etc.)
- `{{AVAILABILITY_TARGET}}`: SLO target (e.g., "99.9")
- `{{ORCHESTRATION_PLATFORM}}`: Container platform (Kubernetes, ECS, etc.)
- Deployment strategies and timelines
- Security and compliance frameworks
- Cost optimization targets

## Common Usage Examples

### For DevOps Architects
```markdown
@.claude/agents/common/infrastructure-standards.md
<!-- Variables:
{{INFRASTRUCTURE_DOMAIN}} = "DevOps architecture"
{{IAC_TOOL}} = "Terraform"
{{AVAILABILITY_TARGET}} = "99.9"
{{ORCHESTRATION_PLATFORM}} = "Kubernetes"
{{DEPLOY_STRATEGY_1}} = "Blue-Green"
{{ROLLBACK_TIME}} = "5 minutes"
-->
```

### For SRE Engineers
```markdown
@.claude/agents/common/infrastructure-standards.md
<!-- Variables:
{{INFRASTRUCTURE_DOMAIN}} = "reliability engineering"
{{MTTR_TARGET}} = "15"
{{ERROR_TARGET}} = "0.1"
{{ALERT_NOISE}} = "5"
{{TRACE_COVERAGE}} = "Critical paths"
-->
```
