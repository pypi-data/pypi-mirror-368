# ClaudeCraftsman BDD Scenarios
*Behavior-driven test scenarios for the artisanal agent framework*

**Document**: BDD-scenarios-claudecraftsman-2025-08-03.md
**Created**: 2025-08-03
**Version**: 1.0
**Status**: Active

## Feature Overview

ClaudeCraftsman enables artisanal software development through specialized AI craftspeople who work with intention, care, and pride. These scenarios validate that the framework delivers on its core promises of quality, research-driven development, and excellent user experience.

## Epic 1: Design-First Development

### Feature: Comprehensive Planning Before Implementation
As a developer-craftsperson
I want to create complete specifications before any implementation
So that all development work is guided by clear, research-backed requirements

#### Background:
Given ClaudeCraftsman is properly installed with MCP tools available
And I have a new feature request requiring planning
And the `.claude/` directory structure exists

#### Scenario: Complete Design Workflow
Given I have a feature request for "user authentication system"
When I run the `/design` command with the feature description
Then the product-architect agent researches current market conditions
And creates a comprehensive PRD with proper citations
And the design-architect agent creates technical specifications
And the technical-planner agent creates an implementation plan
And all documents are saved in `.claude/docs/current/` with proper naming
And the document registry is updated with new entries
And each document includes research citations with access dates

#### Scenario: Research Integration Validation
Given I'm using the `/design` command for market research
When the product-architect agent makes claims about user needs
Then it uses MCP tools (searxng, crawl4ai, context7) for research
And includes citations with URL, access date, and relevant quotes
And uses current date context from time MCP tool
And enables independent verification of all factual claims
And no assumptions are made without evidence backing

#### Scenario: File Organization Enforcement
Given I'm running any ClaudeCraftsman workflow
When agents create documentation during the process
Then no files are created at the project root level
And all documents follow the naming convention `TYPE-project-YYYY-MM-DD.md`
And documents are saved in appropriate `.claude/` subdirectories
And the document registry is updated with accurate metadata
And superseded versions are properly archived with date folders

## Epic 2: Agent Coordination Excellence

### Feature: Seamless Multi-Agent Workflows
As a developer-craftsperson
I want agents to coordinate automatically with preserved context
So that I don't lose information during complex workflows

#### Background:
Given multiple specialized agents are available
And a complex workflow requiring agent coordination
And context files are properly initialized

#### Scenario: Perfect Context Preservation
Given I'm running a multi-phase workflow with agent transitions
When the product-architect completes PRD creation
Then it creates a comprehensive handoff brief
And updates all relevant context files (WORKFLOW-STATE.md, CONTEXT.md, HANDOFF-LOG.md)
And the design-architect receives complete context
And can access all previous decisions and reasoning
And no information is lost during the transition
And the handoff is logged with success confirmation

#### Scenario: Agent Handoff Protocol
Given an agent has completed their specialized work
When transitioning to the next agent in the workflow
Then a handoff brief is created with comprehensive context
And includes all decisions made with rationale
And preserves research findings with citations
And documents next actions required
And validates context completeness before transition
And logs the handoff with metadata and success metrics

#### Scenario: Context Recovery
Given an agent handoff has failed or context appears incomplete
When the receiving agent detects missing context
Then the context-manager agent analyzes available information
And attempts to reconstruct missing context from files
And escalates to human intervention if reconstruction fails
And provides clear guidance on manual context restoration
And logs the issue for future prevention

## Epic 3: Research-Driven Development

### Feature: Evidence-Based Technical Decisions
As a developer-craftsperson
I want all technical decisions backed by current research
So that specifications reflect real market conditions and capabilities

#### Background:
Given MCP research tools are available (searxng, crawl4ai, context7, time)
And an agent needs to make technical or market claims
And research findings must be independently verifiable

#### Scenario: Market Research Integration
Given I need current market analysis for a product decision
When an agent makes claims about market conditions or user needs
Then it uses searxng for current market research
And searches with current date context (2025 terms, not outdated)
And cross-references multiple authoritative sources
And cites each source with URL, access date, and relevant quotes
And enables independent verification by third parties
And documents research methodology for transparency

#### Scenario: Technical Feasibility Validation
Given I need to validate technical approaches or capabilities
When an agent makes technical architecture decisions
Then it researches current best practices using MCP tools
And validates technical feasibility through authoritative sources
And considers multiple technical alternatives with trade-offs
And documents decision rationale with evidence backing
And cites technical documentation and industry standards
And ensures recommendations reflect current technology state

#### Scenario: Competitive Analysis
Given I need understanding of competitive landscape
When planning product positioning or feature priorities
Then agents research current competitor solutions and positioning
And analyze feature gaps and opportunities
And cite specific competitor examples with current data
And provide factual comparisons without subjective opinions
And document competitive advantages and disadvantages
And base strategic recommendations on evidence rather than assumptions

## Epic 4: Quality Craftsmanship

### Feature: Professional Standards Throughout Development
As a developer-craftsperson
I want every output to meet professional craftsperson standards
So that I can take pride in the quality of work produced

#### Background:
Given ClaudeCraftsman agents are designed with craftsman principles
And quality standards are defined for all outputs
And quality gates prevent progression until standards are met

#### Scenario: Sequential Thinking for Complex Problems
Given I have a complex architectural or design problem
When an agent encounters decisions requiring deep analysis
Then it automatically uses appropriate thinking modes ("think hard", "ultrathink")
And breaks down complex problems systematically
And considers multiple approaches and alternatives
And documents reasoning process for future reference
And reaches well-reasoned conclusions based on thorough analysis
And captures thinking process in handoff documentation

#### Scenario: Phase-Based Planning Quality
Given I need project planning for a development effort
When the technical-planner creates implementation plans
Then it organizes work by logical phases (Phase 1, 2, 3) not time-based
And assigns complexity ratings (Low/Medium/High) instead of time estimates
And maps dependencies clearly with critical path identification
And defines quality gates for each phase completion
And bases progression on quality achievement not calendar dates
And enables sustainable development pace focused on quality

#### Scenario: Craftsman Output Standards
Given any agent is producing work output
When completing specialized tasks in their domain
Then the output quality reflects professional craftsperson standards
And would be worthy of showing another master craftsperson
And includes proper research backing and evidence
And follows consistent formatting and organization standards
And serves the ultimate goal of creating valuable software for users
And demonstrates pride and intention in every component

## Epic 5: SuperClaude Migration Excellence

### Feature: Seamless Transition from SuperClaude
As a SuperClaude user
I want to migrate to ClaudeCraftsman without productivity loss
So that I can benefit from enhanced capabilities while preserving familiar workflows

#### Background:
Given I'm an experienced SuperClaude user with established workflows
And ClaudeCraftsman provides equivalent functionality with enhancements
And migration tools are available to assist transition

#### Scenario: Command Pattern Preservation
Given I'm familiar with SuperClaude command patterns
When I migrate to ClaudeCraftsman commands
Then `/sc:workflow` functionality is available through `/design` + `/workflow` + `/implement`
And `/sc:implement` patterns are preserved in enhanced `/implement` command
And `/sc:troubleshoot` systematic analysis is available in `/troubleshoot`
And `/sc:test` comprehensive testing is available in `/test`
And `/sc:document` auto-generation is available in `/document`
And all familiar workflow patterns are preserved with enhancements

#### Scenario: Setup and Migration Process
Given I want to start using ClaudeCraftsman
When I follow the setup instructions
Then directory structure is created automatically
And agent definitions are installed correctly
And MCP tool access is validated
And sample workflows are available for testing
And setup completes in under 30 minutes
And migration validation confirms successful installation

#### Scenario: Workflow Pattern Migration
Given I have established development patterns in SuperClaude
When I execute equivalent workflows in ClaudeCraftsman
Then sequential thinking (`--seq`) functionality is preserved through agent design
And iteration (`--iterate`) patterns are available through workflow commands
And BDD (`--bdd`) integration works with behavior-driven scenarios
And TDD (`--tdd`) protocols are enforced by implementation agents
And persona functionality (architect, backend, frontend) is enhanced as specialized craftspeople
And familiar patterns work with improved quality and research integration

## Error Scenarios and Edge Cases

### Feature: Graceful Error Handling
As a developer-craftsperson
I want the system to handle errors gracefully
So that I can recover from problems and continue working productively

#### Scenario: MCP Tool Unavailability
Given MCP research tools become unavailable during workflow execution
When an agent needs to conduct research for decision making
Then it gracefully degrades to available information
And provides clear messaging about reduced research capabilities
And continues with workflow execution where possible
And documents limitations in output for user awareness
And suggests manual research approaches for critical decisions

#### Scenario: Context File Corruption
Given context files become corrupted or unavailable
When an agent needs to access project context for coordination
Then the context-manager detects corruption and attempts recovery
And uses available backup or partial context for reconstruction
And escalates to human intervention with clear guidance
And provides manual context restoration procedures
And prevents workflow failure through graceful degradation

#### Scenario: Agent Coordination Failure
Given an agent handoff fails or produces incomplete results
When the workflow cannot proceed automatically
Then the system provides clear error messages and guidance
And suggests manual intervention points and procedures
And preserves all available context for human review
And enables workflow restart from appropriate checkpoint
And logs failure details for system improvement

## Performance and Scale Scenarios

### Feature: Efficient Performance at Scale
As a developer-craftsperson
I want ClaudeCraftsman to perform efficiently on projects of various sizes
So that quality standards don't compromise productivity

#### Scenario: Large Project Context Management
Given I'm working on a complex project with extensive context
When context files grow large with project history
Then context loading remains efficient (<10 seconds)
And context compression strategies activate automatically
And context integrity is maintained throughout compression
And agent performance remains consistent regardless of project size
And context queries return relevant information quickly

#### Scenario: Performance Baseline Maintenance
Given I'm migrating from SuperClaude workflows
When executing equivalent workflows in ClaudeCraftsman
Then response times are equal to or better than SuperClaude baseline
And research integration doesn't significantly impact performance
And multi-agent coordination completes efficiently
And quality enhancements don't compromise workflow speed
And overall productivity is maintained or improved

## Success Validation Scenarios

### Feature: Measurable Success Achievement
As a project stakeholder
I want to validate that ClaudeCraftsman achieves its success criteria
So that I can confirm the framework delivers on its promises

#### Scenario: Documentation Organization Success
Given ClaudeCraftsman has been used for a complete development project
When reviewing project file organization
Then zero files are created at project root level
And 100% of documents follow naming conventions
And document registry accurately reflects all project documents
And superseded versions are properly archived
And project maintains clean, navigable organization throughout

#### Scenario: Research Quality Validation
Given agents have made technical or market claims during development
When independently validating research backing
Then 100% of factual claims have verifiable citations
And sources are current and authoritative
And access dates enable verification of research timing
And independent verification is possible for all major claims
And research methodology is transparent and replicable

#### Scenario: User Satisfaction Achievement
Given users have completed migration from SuperClaude to ClaudeCraftsman
When measuring user satisfaction after 2 weeks of usage
Then average satisfaction rating exceeds 4.5/5
And users report maintained or improved productivity
And workflow quality is perceived as significantly enhanced
And users express pride in software created using the framework
And migration disruption was minimal and manageable

---

**BDD Scenarios Owner**: ClaudeCraftsman Project Team
**Last Updated**: 2025-08-03
**Test Coverage**: All major user stories and success criteria
**Validation Method**: Manual testing with automated validation where possible

*"Every scenario validates not just functionality, but the craftsman principles that make the work worthy of pride."*
