---
name: deploy
description: Deployment and release management with zero-downtime strategies, rollback capabilities, and comprehensive monitoring. Orchestrates deployment pipelines across environments with craftsman reliability standards.
---

# Deploy Command

_Production deployment with craftsman reliability_

## Philosophy

Deployment is the moment of truth where craftsmanship meets reality. The deploy command orchestrates reliable, repeatable deployments with zero-downtime strategies, comprehensive validation, and instant rollback capabilities. Every deployment reflects our commitment to delivering value without disrupting users.

## Usage Patterns

- `/deploy [application] --env=staging|production` - Deploy to specific environment
- `/deploy [application] --strategy=blue-green|canary|rolling` - Deployment strategy
- `/deploy [application] --rollback` - Rollback to previous version
- `/deploy [application] --dry-run` - Preview deployment without execution
- `/deploy [application] --health-check` - Validate deployment health

## Core Capabilities

### Deployment Orchestration

The deploy command manages complex deployments:

- **Multi-environment support** with proper configuration management
- **Zero-downtime strategies** ensuring continuous availability
- **Automated rollback** on failure detection
- **Health monitoring** throughout deployment process
- **Post-deployment validation** ensuring successful release

### Deployment Process

1. **Pre-deployment Validation**: Verify all prerequisites met
2. **Environment Preparation**: Configure target environment
3. **Deployment Strategy**: Execute chosen deployment pattern
4. **Health Monitoring**: Continuous validation during rollout
5. **Traffic Management**: Gradual traffic shifting for safety
6. **Post-deployment Testing**: Smoke tests and validation
7. **Monitoring Integration**: Ensure observability active

## Deployment Strategies

### Blue-Green Deployment

```markdown
Blue-Green Strategy:
├── Prepare green environment with new version
├── Run comprehensive tests on green
├── Switch traffic from blue to green
├── Monitor for issues with instant rollback
└── Decommission blue after stability confirmed
```

**Implementation Pattern:**

```yaml
blue-green-deployment:
  stages:
    - prepare-green:
        environment: production-green
        health-check: comprehensive
    - validate-green:
        tests: [smoke, integration, performance]
        threshold: 100%
    - switch-traffic:
        method: dns-switch
        rollback-ready: true
    - monitor:
        duration: 30m
        alerts: enabled
    - cleanup:
        old-environment: production-blue
```

### Canary Deployment

```markdown
Canary Strategy:
├── Deploy to small percentage of infrastructure
├── Monitor error rates and performance
├── Gradually increase traffic percentage
├── Full rollout or rollback based on metrics
└── Complete deployment with confidence
```

**Traffic Progression:**

```typescript
const canaryStages = [
  { percentage: 1, duration: "5m", validation: "error-rate < 0.1%" },
  { percentage: 5, duration: "10m", validation: "p99 < 500ms" },
  { percentage: 25, duration: "15m", validation: "all-metrics-healthy" },
  { percentage: 50, duration: "20m", validation: "user-satisfaction" },
  { percentage: 100, duration: "stable", validation: "full-health" },
];
```

### Rolling Deployment

```markdown
Rolling Strategy:
├── Update instances in small batches
├── Maintain minimum healthy instances
├── Health check before proceeding
├── Automatic rollback on failures
└── Zero-downtime throughout process
```

## Environment Management

### Configuration Hierarchy

```markdown
Configuration Management:
├── Base configuration (shared across environments)
├── Environment-specific overrides
├── Secret management integration
├── Feature flags for gradual rollout
└── Runtime configuration validation
```

### Environment Promotion

```markdown
Promotion Pipeline:
Development → Staging → Production
↓ ↓ ↓
Testing Validation Monitoring
```

## CI/CD Integration

### Pipeline Configuration

```yaml
deploy-pipeline:
  triggers:
    - push-to-main
    - manual-approval

  stages:
    - build:
        artifact-creation: true
        versioning: semantic

    - test:
        unit: required
        integration: required
        e2e: required
        performance: baseline-comparison

    - security-scan:
        vulnerabilities: block-critical
        compliance: required

    - deploy-staging:
        strategy: rolling
        validation: automated

    - deploy-production:
        approval: manual
        strategy: blue-green
        monitoring: enhanced
```

### Deployment Gates

Quality checkpoints before production:

- [ ] All tests passing with coverage met
- [ ] Security scan completed with no critical issues
- [ ] Performance within acceptable thresholds
- [ ] Staging deployment successful
- [ ] Manual approval received
- [ ] Rollback plan documented

## Monitoring and Observability

### Deployment Metrics

```markdown
Key Deployment Indicators:
├── Deployment frequency
├── Lead time for changes
├── Mean time to recovery (MTTR)
├── Change failure rate
├── Deployment success rate
└── Rollback frequency
```

### Real-time Monitoring

```typescript
interface DeploymentMonitoring {
  healthChecks: {
    endpoint: string;
    interval: number;
    timeout: number;
    successThreshold: number;
  };

  metrics: {
    errorRate: MetricThreshold;
    responseTime: MetricThreshold;
    throughput: MetricThreshold;
    customMetrics: MetricThreshold[];
  };

  alerts: {
    channels: ["slack", "pagerduty", "email"];
    escalation: EscalationPolicy;
  };
}
```

## Rollback Strategies

### Automatic Rollback

Triggered by health check failures:

```markdown
Rollback Triggers:
├── Error rate exceeds threshold
├── Response time degradation
├── Health check failures
├── Resource exhaustion
└── Custom metric violations
```

### Manual Rollback

```bash
/deploy my-app --rollback
# or
/deploy my-app --rollback --version=1.2.3
```

## Infrastructure Support

### Container Orchestration

```markdown
Kubernetes Deployment:
├── Deployment manifests with resource limits
├── Service definitions for load balancing
├── ConfigMaps for configuration
├── Secrets for sensitive data
├── Horizontal Pod Autoscaler
└── Network policies for security
```

### Serverless Deployment

```markdown
Serverless Patterns:
├── Function deployment with versioning
├── API Gateway configuration
├── Event trigger setup
├── Cold start optimization
└── Cost monitoring integration
```

## Security Integration

### Deployment Security

```markdown
Security Measures:
├── Image scanning before deployment
├── Secret rotation during deployment
├── Network policy enforcement
├── RBAC configuration validation
├── Audit logging for compliance
└── SSL/TLS certificate management
```

### Compliance Validation

- **Data residency** requirements met
- **Regulatory compliance** verified
- **Security policies** enforced
- **Audit trail** maintained
- **Access controls** validated

## Post-Deployment Validation

### Smoke Tests

Essential functionality verification:

```typescript
const smokeTests = [
  { test: "API health check", endpoint: "/health" },
  { test: "Database connectivity", query: "SELECT 1" },
  { test: "Auth service", action: "validate-token" },
  { test: "Critical user flow", journey: "login-purchase-logout" },
];
```

### Performance Validation

```markdown
Performance Checks:
├── Response time within SLA
├── Throughput meets requirements
├── Resource utilization normal
├── No memory leaks detected
└── Database query performance
```

## File Organization

### Deployment Artifacts

```markdown
Deployment structure:
.claude/deployments/
├── manifests/
│ ├── [environment]/
│ │ └── [application].yaml
├── configs/
│ ├── base/
│ └── overlays/
├── scripts/
│ ├── pre-deploy/
│ └── post-deploy/
└── rollback/
└── [version-history]/
```

### Documentation

```markdown
Deployment documentation:
.claude/docs/current/deployments/
├── DEPLOY-PLAN-[app]-[YYYY-MM-DD].md
├── DEPLOY-RUNBOOK-[app]-[YYYY-MM-DD].md
├── ROLLBACK-PLAN-[app]-[YYYY-MM-DD].md
└── POST-MORTEM-[incident]-[YYYY-MM-DD].md
```

## Success Criteria

### Successful Deployment

A deployment is successful when:

- [ ] All health checks passing
- [ ] Performance within baselines
- [ ] No increase in error rates
- [ ] User experience unaffected
- [ ] Monitoring active and alerting
- [ ] Documentation updated
- [ ] Team notified of success

### Deployment Excellence

Every deployment must demonstrate:

- **Reliability**: Consistent, predictable deployments
- **Safety**: Zero-downtime with instant rollback
- **Observability**: Complete visibility into system state
- **Automation**: Minimal manual intervention required

## Usage Examples

### Production Deployment

```bash
/deploy user-service --env=production --strategy=blue-green

# Executes:
# - Pre-deployment validation
# - Blue-green environment setup
# - Comprehensive testing
# - Traffic switching
# - Monitoring and validation
```

### Canary Deployment

```bash
/deploy recommendation-engine --env=production --strategy=canary

# Progressive rollout:
# - 1% traffic for 5 minutes
# - 5% traffic for 10 minutes
# - 25% traffic for 15 minutes
# - 50% traffic for 20 minutes
# - 100% traffic after validation
```

### Emergency Rollback

```bash
/deploy payment-service --rollback --version=2.3.1

# Immediate actions:
# - Switch traffic to previous version
# - Validate service health
# - Notify team of rollback
# - Create incident report
```

## Integration with Other Commands

### Deployment Pipeline

```markdown
Complete deployment workflow:
/test → /validate → /deploy → /monitor
↓ ↓ ↓ ↓
Testing Verifying Releasing Tracking
```

### Continuous Delivery

- **From `/test`**: Test results gate deployment
- **From `/validate`**: Framework validation before deploy
- **To monitoring**: Deployment metrics and alerts
- **To incident management**: Rollback and recovery

## The Deployment Commitment

The deploy command represents our promise to users that new features and fixes will be delivered reliably, safely, and without disruption. Every deployment is an opportunity to demonstrate operational excellence and maintain user trust.

**Remember**: Deployment is not the end of development; it's the beginning of value delivery. The deploy command ensures this transition happens smoothly, safely, and with confidence.
