# Document Type Standards
*Comprehensive standards for ClaudeCraftsman document organization and naming*

**Document**: document-type-standards.md
**Created**: 2025-08-03
**Last Updated**: 2025-08-03 23:19 UTC
**Version**: 1.0
**Status**: Active Framework Standard

## Overview

ClaudeCraftsman enforces strict document organization to prevent documentation sprawl and maintain project clarity. This document defines document types, naming conventions, and location requirements.

## Core Principle

**Zero Project Root Pollution**: No documentation files created at project root level except CLAUDE.md for framework activation.

## Document Categories and Locations

### `.claude/docs/current/` - Runtime Project Documents

**Purpose**: Active project specifications and documentation that evolve with the project

#### Document Types

**PRD (Product Requirements Document)**
- **Format**: `PRD-[project-name]-[YYYY-MM-DD].md`
- **Purpose**: Business requirements, user stories, success metrics
- **Created by**: product-architect agent
- **Example**: `PRD-user-authentication-2025-08-03.md`

**TECH-SPEC (Technical Specification)**
- **Format**: `TECH-SPEC-[project-name]-[YYYY-MM-DD].md`
- **Purpose**: System architecture, technology choices, implementation guidance
- **Created by**: design-architect agent
- **Example**: `TECH-SPEC-payment-processing-2025-08-03.md`

**IMPL-PLAN (Implementation Plan)**
- **Format**: `IMPL-PLAN-[project-name]-[YYYY-MM-DD].md`
- **Purpose**: Phase-based implementation roadmap, task breakdown, dependencies
- **Created by**: technical-planner agent
- **Example**: `IMPL-PLAN-microservices-migration-2025-08-03.md`

**USER-GUIDE (User Documentation)**
- **Format**: `USER-GUIDE-[topic]-[YYYY-MM-DD].md`
- **Purpose**: Setup guides, usage instructions, troubleshooting
- **Created by**: Various agents, documentation specialists
- **Example**: `USER-GUIDE-bootstrap-setup-2025-08-03.md`

**API-SPEC (API Specification)**
- **Format**: `API-SPEC-[service-name]-[YYYY-MM-DD].md`
- **Purpose**: OpenAPI specifications, endpoint documentation
- **Created by**: backend-architect agent
- **Example**: `API-SPEC-user-service-2025-08-03.md`

**TEST-PLAN (Test Strategy)**
- **Format**: `TEST-PLAN-[project-name]-[YYYY-MM-DD].md`
- **Purpose**: Testing approach, coverage requirements, validation criteria
- **Created by**: Test planning agents
- **Example**: `TEST-PLAN-integration-testing-2025-08-03.md`

### `.claude/project-mgt/` - Project Management Documents

**Purpose**: Project management, architecture decisions, and governance documentation

#### Subdirectory Organization

**`01-project-overview/`** - Business context and planning
- `PRD-[project-name]-[YYYY-MM-DD].md` - Master PRD
- `project-charter.md` - Project vision and objectives
- `stakeholder-analysis.md` - Stakeholder mapping
- `success-criteria.md` - Definition of success

**`02-technical-design/`** - Architecture and technical decisions
- `ADR-###-[decision-name]-[YYYY-MM-DD].md` - Individual architecture decisions
- `ARCH-DECISION-RECORD.md` - ADR index and navigation
- `TECH-ANALYSIS-[topic]-[YYYY-MM-DD].md` - Technical analysis documents

**`03-implementation-plan/`** - Implementation strategy
- `IMPL-PLAN-[project-name]-[YYYY-MM-DD].md` - Master implementation plan
- `phase-breakdown.md` - Work breakdown structure
- `dependency-mapping.md` - Task dependencies

**`04-testing-validation/`** - Quality assurance
- `BDD-scenarios-[project-name]-[YYYY-MM-DD].md` - Behavior-driven scenarios
- `test-strategy.md` - Testing approach
- `quality-standards.md` - Quality requirements

**`05-documentation/`** - User and developer documentation
- `user-guide.md` - Master user guide
- `setup-instructions.md` - Installation and configuration
- `troubleshooting-guide.md` - Common issues and solutions

**`06-project-tracking/`** - Progress and issue management
- `progress-log.md` - Development progress tracking
- `issue-tracker.md` - Bugs and blockers
- `change-requests.md` - Scope changes

**`07-standards-templates/`** - Framework standards and templates
- `agent-template.md` - Template for creating agents
- `handoff-brief-template.md` - Agent handoff template
- `document-type-standards.md` - This document

**`08-research-evidence/`** - Research and validation
- `market-research-[YYYY-MM-DD].md` - Market analysis
- `competitive-analysis-[YYYY-MM-DD].md` - Competitor research
- `citation-registry.md` - Master source registry

### `.claude/context/` - Runtime Context Files

**Purpose**: Agent coordination and session continuity

**Files**:
- `WORKFLOW-STATE.md` - Current workflow status
- `CONTEXT.md` - Project context and decisions
- `HANDOFF-LOG.md` - Agent transition history
- `SESSION-MEMORY.md` - Session continuity data

## Naming Convention Standards

### Universal Format
`[TYPE]-[descriptive-name]-[YYYY-MM-DD].md`

### Date Requirements
- **Always use current date** from MCP time tool
- **Format**: YYYY-MM-DD (ISO 8601)
- **No hardcoded dates** anywhere in the system
- **Example**: `2025-08-03` for August 3rd, 2025

### Descriptive Names
- **Use kebab-case**: `user-authentication`, `payment-processing`
- **Be specific**: `api-endpoints` not `api`, `user-registration` not `users`
- **Avoid abbreviations**: `authentication` not `auth`, `implementation` not `impl`
- **Project context**: Include project/component name when relevant

### Examples by Type
```
PRD-user-authentication-2025-08-03.md
TECH-SPEC-payment-gateway-integration-2025-08-03.md
IMPL-PLAN-microservices-architecture-2025-08-03.md
USER-GUIDE-deployment-setup-2025-08-03.md
API-SPEC-user-management-service-2025-08-03.md
ADR-009-database-selection-2025-08-03.md
```

## Architecture Decision Record (ADR) Standards

### ADR-Specific Requirements
- **Individual files**: Each decision in separate file
- **Sequential numbering**: ADR-001, ADR-002, ADR-003, etc.
- **No gaps in numbering**: Maintain sequence integrity
- **Conflict resolution**: Check existing numbers before creating new ADR

### ADR Lifecycle
1. **Check existing ADRs**: Review ARCH-DECISION-RECORD.md index
2. **Use next number**: Sequential numbering from highest existing
3. **Create individual file**: `ADR-###-[decision-name]-[YYYY-MM-DD].md`
4. **Update index**: Add entry to ARCH-DECISION-RECORD.md
5. **Link from relevant docs**: Reference ADR from other documents

## Document Lifecycle Management

### Creation Process
1. **Determine document type** based on content and purpose
2. **Use appropriate naming convention** with current date
3. **Create in correct location** based on document category
4. **Update document registry** in `.claude/docs/current/registry.md`
5. **Maintain context files** if agent coordination involved

### Version Management
- **Archive superseded versions**: Move to `.claude/docs/archive/[YYYY-MM-DD]/`
- **Update registry**: Mark old version as archived, new as active
- **Preserve history**: Maintain clear version lineage
- **Reference changes**: Document what changed and why

### Quality Standards
- **Research backing**: All claims supported with MCP tool research and citations
- **Time accuracy**: All dates current using MCP time tool
- **User focus**: Documentation serves genuine user needs
- **Craftsman quality**: Would you be proud to show this to another craftsperson?

## Common Anti-Patterns to Avoid

### ❌ Document Sprawl
- **Problem**: Creating files at project root
- **Solution**: Always use `.claude/` directory structure
- **Example**: DON'T create `README.md`, `NOTES.md`, `TODO.md` at root

### ❌ Undefined Document Types
- **Problem**: Using non-standard document type prefixes
- **Solution**: Use only defined document types from this standard
- **Example**: DON'T use `ARCH-DESIGN-`, `NOTES-`, `MISC-`

### ❌ Inconsistent Naming
- **Problem**: Mixing naming conventions within project
- **Solution**: Follow strict naming convention standards
- **Example**: DON'T mix `user_auth_2025_08_03.md` with `user-auth-2025-08-03.md`

### ❌ Hardcoded Dates
- **Problem**: Using outdated or incorrect dates in filenames
- **Solution**: Always use current date from MCP time tool
- **Example**: DON'T use `PRD-project-2024-01-01.md` when creating in 2025

### ❌ ADR Numbering Conflicts
- **Problem**: Creating ADRs with conflicting numbers
- **Solution**: Check existing ADRs and use sequential numbering
- **Example**: DON'T create `ADR-003-new-decision.md` when ADR-003 already exists

## Framework Integration

### Agent Requirements
All ClaudeCraftsman agents MUST:
- **Use current date**: Call MCP time tool for all document naming
- **Follow naming conventions**: Strict adherence to format standards
- **Update registries**: Maintain document registries and context files
- **Quality gates**: Verify document standards before completion

### Quality Enforcement
- **Mandatory standards**: Document standards are non-negotiable framework requirements
- **Quality gates**: Document creation includes standards compliance check
- **Context maintenance**: All document operations update relevant context files
- **Registry updates**: Document registry maintained with every change

### Validation Checklist
Before completing any document creation or update:
- [ ] **Document type defined**: Using standard document type from this specification
- [ ] **Naming convention followed**: Correct format with current date
- [ ] **Location correct**: File created in appropriate directory
- [ ] **Registry updated**: Document registry reflects new/changed document
- [ ] **Context maintained**: Relevant context files updated
- [ ] **Quality standards met**: Research backing, citations, craftsman quality

## Evolution and Maintenance

### Standards Updates
- **Consensus required**: Changes require architecture team agreement
- **Version controlled**: Document standard changes tracked and versioned
- **Migration support**: Clear guidance for updating existing documents
- **Impact assessment**: Evaluate effect on existing documentation

### Review Schedule
- **Quarterly review**: Assess effectiveness and identify improvements
- **Project milestone review**: Validate standards serving project needs
- **User feedback integration**: Incorporate user suggestions and pain points
- **Continuous improvement**: Evolve standards based on practical experience

---

**Document Standards Maintainer**: ClaudeCraftsman Architecture Team
**Next Review Date**: Phase 2 Completion
**Version History**: v1.0 - Initial comprehensive standards definition

*"Clear documentation standards prevent the chaos that undermines craftsmanship. Every file has a purpose, every name has meaning, every location serves organization."*
