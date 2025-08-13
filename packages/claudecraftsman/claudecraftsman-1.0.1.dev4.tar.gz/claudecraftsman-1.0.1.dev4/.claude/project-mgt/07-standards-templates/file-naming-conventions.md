# File Naming Conventions
*Consistent naming standards for ClaudeCraftsman projects*

**Document**: file-naming-conventions.md
**Created**: 2025-08-03
**Version**: 1.0
**Status**: Active Standard

## Naming Philosophy

Consistent file naming prevents documentation sprawl, enables automated processing, and supports long-term project maintainability. Every file name should clearly communicate the file's purpose, project context, and temporal relevance.

## Standard Naming Conventions

### Document Naming Format

#### Primary Format
```
[TYPE]-[project-name]-[YYYY-MM-DD].md
```

#### Examples
```
PRD-user-authentication-2025-08-03.md
TECH-SPEC-payment-system-2025-08-03.md
IMPL-PLAN-mobile-app-2025-08-03.md
BDD-scenarios-checkout-flow-2025-08-03.md
```

#### Element Specifications

**TYPE**: Document type using standard abbreviations
- `PRD` - Product Requirements Document
- `TECH-SPEC` - Technical Specification
- `IMPL-PLAN` - Implementation Plan
- `BDD-scenarios` - Behavior-Driven Development scenarios
- `API-spec` - API Specification
- `DB-schema` - Database Schema
- `ARCH-decision` - Architecture Decision Record
- `TEST-plan` - Test Plan
- `USER-guide` - User Guide

**project-name**: Descriptive project identifier
- Use lowercase with hyphens for word separation
- Be descriptive but concise (2-4 words typically)
- Avoid abbreviations unless widely understood
- Examples: `user-authentication`, `payment-system`, `mobile-app`

**YYYY-MM-DD**: Creation date using MCP time tool
- Always use actual current date from MCP time tool
- Never use hardcoded or estimated dates
- Format: 4-digit year, 2-digit month, 2-digit day
- Example: `2025-08-03` (not `2025-8-3` or `25-08-03`)

### Special Document Types

#### Context Files
```
WORKFLOW-STATE.md
CONTEXT.md
HANDOFF-LOG.md
SESSION-MEMORY.md
```
**Rationale**: Context files are unique and don't follow project-date pattern

#### Registry and Index Files
```
registry.md
README.md
```
**Rationale**: Master index files serve multiple projects and don't have project-specific dates

#### Template Files
```
agent-template.md
handoff-brief-template.md
PRD-template.md
```
**Rationale**: Templates are reusable across projects and don't have creation dates

## Directory Naming Standards

### Directory Structure
```
.claude/
├── agents/                     # lowercase, descriptive
├── commands/                   # lowercase, descriptive
├── docs/                       # lowercase, abbreviated where clear
│   ├── current/               # lowercase, descriptive
│   ├── archive/               # lowercase, descriptive
│   └── templates/             # lowercase, descriptive
├── specs/                      # lowercase, abbreviated where clear
│   ├── api-specifications/    # lowercase with hyphens
│   ├── database-schemas/      # lowercase with hyphens
│   └── component-specs/       # lowercase with hyphens
├── context/                    # lowercase, descriptive
├── templates/                  # lowercase, descriptive
└── project-mgt/               # lowercase with hyphens
    ├── 01-project-overview/   # numbered with hyphens
    ├── 02-technical-design/   # numbered with hyphens
    └── [etc...]
```

### Directory Naming Rules
**Format**: lowercase-with-hyphens
**Descriptive**: Names clearly indicate directory purpose
**Consistent**: Follow established patterns throughout structure
**Logical**: Organization reflects functional relationships

## Agent and Command Naming

### Agent File Naming
```
[agent-role].md
```

#### Examples
```
product-architect.md
design-architect.md
backend-architect.md
frontend-developer.md
workflow-coordinator.md
context-manager.md
```

#### Agent Naming Rules
**Role-Based**: Names reflect agent specialization and role
**Descriptive**: Clear indication of agent capabilities
**Consistent**: Follow established pattern for all agents
**Professional**: Names reflect craftsman expertise

### Command File Naming
```
[command-name].md
```

#### Examples
```
design.md
workflow.md
implement.md
troubleshoot.md
test.md
document.md
```

#### Command Naming Rules
**Action-Based**: Names reflect command purpose and action
**Concise**: Single word or clear phrase
**Intuitive**: Names match user expectations
**Consistent**: Follow established pattern for all commands

## Archive and Version Management

### Archive Directory Structure
```
.claude/docs/archive/
└── [YYYY-MM-DD]/
    ├── PRD-project-name-[original-date].md
    ├── TECH-SPEC-project-name-[original-date].md
    └── ARCHIVE-MANIFEST.md
```

### Archive Naming Rules
**Date Folders**: Use date when archival occurred (not original document date)
**Original Names**: Preserve original document names in archive
**Manifest Files**: `ARCHIVE-MANIFEST.md` documents what was archived and why
**No Renaming**: Don't rename documents when archiving (preserve history)

### Version Control Integration
**Git-Friendly**: All names compatible with version control systems
**No Spaces**: Use hyphens instead of spaces for cross-platform compatibility
**Case Consistency**: Use lowercase for directories, standard case for documents
**Character Safety**: Avoid special characters that cause file system issues

## Automation and Validation

### Automated Naming Validation

#### Validation Rules
```javascript
// Document naming validation pattern
const documentPattern = /^[A-Z-]+-[a-z-]+-\d{4}-\d{2}-\d{2}\.md$/;

// Directory naming validation pattern
const directoryPattern = /^[a-z-]+$/;

// Agent naming validation pattern
const agentPattern = /^[a-z-]+\.md$/;

// Command naming validation pattern
const commandPattern = /^[a-z-]+\.md$/;
```

#### Validation Checklist
- [ ] **Document Format**: Matches TYPE-project-YYYY-MM-DD.md pattern
- [ ] **Current Date**: Uses actual current date from MCP time tool
- [ ] **Type Valid**: Document type from approved list
- [ ] **Project Name**: Follows lowercase-with-hyphens format
- [ ] **Extension Correct**: Uses .md for markdown documents
- [ ] **Directory Correct**: Saved in appropriate .claude/ subdirectory

### Naming Tools and Helpers

#### Automatic Date Integration
```bash
# Example: Get current date for file naming
current_date=$(date +%Y-%m-%d)
filename="PRD-${project_name}-${current_date}.md"
```

#### Naming Convention Checker
```bash
# Validate file naming convention
validate_filename() {
    if [[ $1 =~ ^[A-Z-]+-[a-z-]+-[0-9]{4}-[0-9]{2}-[0-9]{2}\.md$ ]]; then
        echo "✅ Valid filename: $1"
    else
        echo "❌ Invalid filename: $1"
        echo "Expected format: TYPE-project-name-YYYY-MM-DD.md"
    fi
}
```

## Common Naming Scenarios

### New Feature Development
```
# Planning Phase
PRD-user-settings-2025-08-03.md
TECH-SPEC-user-settings-2025-08-03.md
IMPL-PLAN-user-settings-2025-08-03.md

# Implementation Phase
API-spec-user-settings-2025-08-03.md
DB-schema-user-settings-2025-08-03.md
TEST-plan-user-settings-2025-08-03.md

# Testing Phase
BDD-scenarios-user-settings-2025-08-03.md
```

### System Architecture
```
# Architecture Documents
ARCH-decision-microservices-2025-08-03.md
TECH-SPEC-system-architecture-2025-08-03.md
IMPL-PLAN-architecture-migration-2025-08-03.md
```

### Bug Investigation and Resolution
```
# Troubleshooting Documents
ISSUE-analysis-login-failure-2025-08-03.md
FIX-plan-login-timeout-2025-08-03.md
TEST-validation-login-fix-2025-08-03.md
```

### Documentation and Guides
```
# User-Facing Documentation
USER-guide-api-integration-2025-08-03.md
SETUP-guide-development-environment-2025-08-03.md
TROUBLESHOOT-guide-common-issues-2025-08-03.md
```

## Error Prevention

### Common Naming Mistakes

#### Date-Related Errors
**Hardcoded Dates**: Using fixed dates instead of current date from MCP time tool
**Wrong Format**: Using MM-DD-YYYY or DD-MM-YYYY instead of YYYY-MM-DD
**Inconsistent Dating**: Mixing date formats within same project

**Prevention**: Always use MCP time tool for current date, validate format

#### Project Name Issues
**Spaces**: Using spaces instead of hyphens in project names
**Mixed Case**: Using CamelCase or UPPERCASE instead of lowercase
**Abbreviations**: Using unclear abbreviations that aren't self-explanatory

**Prevention**: Follow lowercase-with-hyphens standard consistently

#### Type Standardization
**Custom Types**: Creating new document types instead of using standard ones
**Inconsistent Types**: Using variations of standard types (SPEC vs TECH-SPEC)
**Missing Types**: Not including document type in filename

**Prevention**: Use only approved document types, maintain type registry

### Validation and Correction

#### File Naming Validation Process
1. **Automated Check**: Run naming convention validation on all files
2. **Manual Review**: Human review of complex or edge case names
3. **Correction Process**: Systematic correction of naming violations
4. **Prevention**: Training and templates to prevent future errors

#### Registry Maintenance
**Naming Compliance**: Regular audit of document registry for naming compliance
**Correction Tracking**: Track naming corrections and common error patterns
**Standard Evolution**: Update standards based on practical usage patterns
**Tool Integration**: Integrate naming validation with development tools

## Standards Evolution

### Review and Update Process

#### Regular Review Schedule
**Monthly**: Review naming patterns and identify improvement opportunities
**Quarterly**: Assess naming standard effectiveness and user feedback
**Annually**: Comprehensive review of all naming conventions and standards
**As Needed**: Address specific issues or new requirements as they arise

#### Change Management
**Backward Compatibility**: Ensure changes don't break existing projects
**Migration Path**: Provide clear migration guidance for standard changes
**Documentation Updates**: Update all templates and documentation consistently
**Community Input**: Incorporate user feedback and practical usage insights

#### Continuous Improvement
**Usage Analysis**: Monitor naming pattern usage and effectiveness
**Error Tracking**: Track common naming errors and prevention strategies
**Tool Enhancement**: Improve automation and validation tools
**Standard Refinement**: Refine standards based on real-world usage

---

**File Naming Standards Maintained By**: All agents (enforced by context-manager)
**Compliance Monitoring**: Automated validation with manual review
**Update Authority**: ClaudeCraftsman Project Team
**Standard Evolution**: Based on usage patterns and user feedback

*"Consistent naming is the foundation of organized thinking - when every file has its proper place and clear purpose, the craftsman can focus on creating rather than searching."*
