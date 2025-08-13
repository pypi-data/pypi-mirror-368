# ClaudeCraftsman Setup Guide
*Installation and configuration guide for artisanal software development*

**Document**: craftsman-setup-guide.md
**Created**: 2025-08-03
**Version**: 1.0
**Status**: Active

## Setup Overview

This guide walks you through setting up ClaudeCraftsman, the artisanal agent framework that transforms software development into a craft where specialized AI craftspeople work with intention, care, and pride.

**Setup Time**: Approximately 20-30 minutes for experienced developers
**Prerequisites**: Claude Code installed with MCP server access
**Outcome**: Complete ClaudeCraftsman framework ready for quality-focused development

## Prerequisites Validation

### Required Software

#### Claude Code Installation
**Requirement**: Claude Code with native agent support
**Validation**: Run `claude-code --version` to confirm installation
**Minimum Version**: Latest version with sub-agent functionality
**Documentation**: https://docs.anthropic.com/en/docs/claude-code

#### MCP Server Access
**Requirement**: MCP server with research tools available
**Required Tools**: time, searxng, crawl4ai, context7
**Validation**: Verify tools are accessible through Claude Code
**Fallback**: Graceful degradation when tools unavailable

### System Requirements

#### File System Access
**Requirement**: Read/write access to project directory
**Purpose**: Create .claude/ directory structure and manage documentation
**Validation**: Confirm ability to create directories and files

#### Terminal Access
**Requirement**: Command-line interface for Claude Code
**Purpose**: Execute ClaudeCraftsman commands
**Validation**: Confirm Claude Code commands work correctly

### Knowledge Prerequisites

#### Development Experience
**Recommended**: 3+ years of software development experience
**Understanding**: Basic familiarity with structured development workflows
**Mindset**: Appreciation for quality and thoughtful development practices

#### Tool Familiarity
**Claude Code**: Basic understanding of Claude Code agent functionality
**Command Line**: Comfortable with terminal/command-line interfaces
**Project Organization**: Understanding of file organization principles

## Step-by-Step Setup

### Step 1: Project Directory Setup

#### Create Project Directory
```bash
# Create main project directory
mkdir claudecraftsman-project
cd claudecraftsman-project

# Initialize as development project
git init  # Optional but recommended
```

#### Validate Directory Access
```bash
# Confirm read/write access
touch test-file.txt
ls -la test-file.txt
rm test-file.txt
```

### Step 2: ClaudeCraftsman Framework Installation

#### Download Agent Definitions
```bash
# Create agents directory
mkdir -p .claude/agents

# Agent definitions will be provided in Phase 1 implementation
# For now, create placeholder structure
touch .claude/agents/.placeholder
```

#### Create Directory Structure
```bash
# Core directories
mkdir -p .claude/docs/current
mkdir -p .claude/docs/archive
mkdir -p .claude/docs/templates
mkdir -p .claude/specs/api-specifications
mkdir -p .claude/specs/database-schemas
mkdir -p .claude/specs/component-specs
mkdir -p .claude/context
mkdir -p .claude/commands
mkdir -p .claude/templates

# Validate structure
find .claude -type d
```

#### Initialize Context Files
```bash
# Create initial context files
cp /path/to/claudecraftsman/templates/WORKFLOW-STATE.md .claude/context/
cp /path/to/claudecraftsman/templates/CONTEXT.md .claude/context/
cp /path/to/claudecraftsman/templates/HANDOFF-LOG.md .claude/context/
cp /path/to/claudecraftsman/templates/SESSION-MEMORY.md .claude/context/
```

### Step 3: MCP Tool Validation

#### Test Time Tool
```bash
# In Claude Code, validate time tool access
claude-code --agent test-agent "Use time MCP tool to get current date"
```
**Expected Output**: Current date and time
**Purpose**: Ensures time-aware documentation works correctly

#### Test Research Tools
```bash
# Test searxng availability
claude-code --agent test-agent "Use searxng to search for 'AI development 2025'"

# Test crawl4ai availability
claude-code --agent test-agent "Use crawl4ai to analyze a simple webpage"

# Test context7 availability
claude-code --agent test-agent "Use context7 to find technical documentation"
```
**Expected Output**: Research results from tools
**Purpose**: Confirms research-driven development capabilities

#### Fallback Configuration
If MCP tools unavailable:
```bash
# Create fallback configuration
echo "MCP_TOOLS_AVAILABLE=false" > .claude/config
echo "RESEARCH_MODE=fallback" >> .claude/config
```

### Step 4: Agent Installation

#### Core Planning Agents
```bash
# Install planning agents (will be available after Phase 1)
cp /path/to/agents/product-architect.md .claude/agents/
cp /path/to/agents/design-architect.md .claude/agents/
cp /path/to/agents/technical-planner.md .claude/agents/
```

#### Implementation Agents
```bash
# Install implementation agents (will be available after Phase 2)
cp /path/to/agents/system-architect.md .claude/agents/
cp /path/to/agents/backend-architect.md .claude/agents/
cp /path/to/agents/frontend-developer.md .claude/agents/
```

#### Coordination Agents
```bash
# Install coordination agents (will be available after Phase 2)
cp /path/to/agents/workflow-coordinator.md .claude/agents/
cp /path/to/agents/context-manager.md .claude/agents/
```

### Step 5: Command Installation

#### Core Commands
```bash
# Install command definitions (will be available after Phase 3)
cp /path/to/commands/design.md .claude/commands/
cp /path/to/commands/workflow.md .claude/commands/
cp /path/to/commands/implement.md .claude/commands/
cp /path/to/commands/troubleshoot.md .claude/commands/
cp /path/to/commands/test.md .claude/commands/
cp /path/to/commands/document.md .claude/commands/
```

#### Validate Command Installation
```bash
# Test command availability in Claude Code
claude-code --help | grep -E "(design|workflow|implement)"
```

### Step 6: Initial Configuration

#### Project Configuration
```bash
# Create project configuration
cat > .claude/project-config.yaml << EOF
project:
  name: "your-project-name"
  created: "$(date +%Y-%m-%d)"
  framework: "claudecraftsman"
  version: "1.0"

settings:
  research_mode: true
  quality_mode: "craftsman"
  file_organization: "strict"
  time_awareness: true
  context_preservation: "full"

agents:
  planning: ["product-architect", "design-architect", "technical-planner"]
  implementation: ["system-architect", "backend-architect", "frontend-developer"]
  coordination: ["workflow-coordinator", "context-manager"]
EOF
```

#### Quality Standards Configuration
```bash
# Initialize quality standards
cp /path/to/templates/quality-checklist.md .claude/templates/
cp /path/to/templates/research-citation-format.md .claude/templates/
cp /path/to/templates/file-naming-conventions.md .claude/templates/
```

### Step 7: Installation Validation

#### Basic Functionality Test
```bash
# Test basic directory structure
ls -la .claude/
ls -la .claude/docs/current/
ls -la .claude/context/

# Validate context files
cat .claude/context/WORKFLOW-STATE.md | head -10
```

#### Agent Availability Test
```bash
# Test agent accessibility (when agents are installed)
claude-code --list-agents | grep -E "(product-architect|design-architect)"
```

#### Command Functionality Test
```bash
# Test command availability (when commands are installed)
claude-code --help | grep -E "(design|workflow|implement)"
```

#### MCP Integration Test
```bash
# Test research capabilities
claude-code --agent product-architect "Use time tool to get current date for document naming"
```

## Validation Checklist

### Installation Validation
- [ ] **Directory Structure**: .claude/ hierarchy created correctly
- [ ] **Context Files**: All context files initialized properly
- [ ] **Agent Installation**: All agent definitions installed and accessible
- [ ] **Command Installation**: All commands available in Claude Code
- [ ] **MCP Tools**: Research tools accessible or fallback configured

### Configuration Validation
- [ ] **Project Config**: Project configuration file created and valid
- [ ] **Quality Standards**: Quality templates and standards accessible
- [ ] **File Organization**: Naming conventions and structure enforced
- [ ] **Research Integration**: Citation standards configured
- [ ] **Time Awareness**: Current date integration working

### Functionality Validation
- [ ] **Basic Commands**: Core commands respond correctly
- [ ] **Agent Coordination**: Multi-agent workflows can be initiated
- [ ] **Context Management**: Context files update during workflows
- [ ] **Research Capabilities**: MCP tools provide research functionality
- [ ] **Quality Standards**: Outputs meet craftsman standards

## Troubleshooting Common Issues

### Directory Structure Issues

#### Permission Problems
**Problem**: Cannot create .claude/ directory or files
**Solution**: Check file system permissions, run with appropriate privileges
**Prevention**: Validate directory access before beginning setup

#### Existing .claude/ Directory
**Problem**: .claude/ directory already exists with different structure
**Solution**: Backup existing, remove, and recreate with ClaudeCraftsman structure
**Prevention**: Check for existing directories before setup

### MCP Tool Issues

#### Tools Not Available
**Problem**: MCP research tools not accessible
**Solution**: Configure fallback mode, verify MCP server setup
**Graceful Degradation**: ClaudeCraftsman works with reduced functionality

#### Tool Authentication
**Problem**: MCP tools require authentication or configuration
**Solution**: Configure tools according to their specific requirements
**Documentation**: Refer to MCP tool documentation for setup

### Agent Installation Issues

#### Agent Not Found
**Problem**: Claude Code cannot find installed agents
**Solution**: Verify agent files in correct location with correct naming
**Validation**: Check agent definition format and syntax

#### Agent Syntax Errors
**Problem**: Agent definitions contain syntax errors
**Solution**: Validate agent definition format against template
**Prevention**: Use provided agent templates without modification

### Command Integration Issues

#### Commands Not Available
**Problem**: ClaudeCraftsman commands not accessible in Claude Code
**Solution**: Verify command installation and Claude Code configuration
**Alternative**: Use agents directly while debugging command issues

#### Command Syntax Errors
**Problem**: Commands don't execute correctly
**Solution**: Validate command syntax and parameter format
**Documentation**: Refer to command documentation for correct usage

## Migration from SuperClaude

### Pre-Migration Checklist
- [ ] **Backup SuperClaude**: Backup existing SuperClaude configuration and projects
- [ ] **Document Workflows**: Document current SuperClaude usage patterns
- [ ] **Identify Dependencies**: Note any SuperClaude-specific customizations
- [ ] **Plan Transition**: Schedule transition with minimal workflow disruption

### Migration Process

#### Workflow Pattern Mapping
**SuperClaude → ClaudeCraftsman**:
- `/sc:workflow` → `/design` + `/workflow` + `/implement`
- `/sc:implement` → `/implement --from-design`
- `/sc:troubleshoot` → `/troubleshoot`
- `/sc:test` → `/test`
- `/sc:document` → `/document`

#### Configuration Migration
```bash
# Migrate SuperClaude patterns to ClaudeCraftsman
# (Specific migration scripts will be provided in Phase 4)
```

#### Validation Testing
```bash
# Test equivalent workflows
claude-code --agent product-architect "Create PRD equivalent to SuperClaude workflow output"
```

### Post-Migration Validation
- [ ] **Workflow Equivalence**: All SuperClaude patterns work in ClaudeCraftsman
- [ ] **Quality Enhancement**: Research integration and organization improvements visible
- [ ] **Performance**: Response times meet or exceed SuperClaude baseline
- [ ] **User Satisfaction**: Workflow feels familiar with enhanced capabilities

## Post-Setup Configuration

### Project-Specific Setup

#### Initialize Project Context
```bash
# Set project-specific context
claude-code --agent context-manager "Initialize project context for [project-name]"
```

#### Configure Quality Standards
```bash
# Configure project-specific quality criteria
cp .claude/templates/quality-checklist.md .claude/project-quality-standards.md
# Customize standards for project needs
```

#### Setup Development Workflow
```bash
# Initialize development workflow
claude-code --agent workflow-coordinator "Setup development workflow for [project-type]"
```

### Team Configuration

#### Multi-User Setup
```bash
# Configure for team usage (if applicable)
# Document team-specific standards and conventions
# Setup shared context and coordination protocols
```

#### Integration with Development Tools
```bash
# Configure integration with existing tools
# Setup version control integration
# Configure CI/CD integration (if applicable)
```

## Verification and Testing

### Setup Verification Script
```bash
#!/bin/bash
# ClaudeCraftsman Setup Verification

echo "🔍 Verifying ClaudeCraftsman Setup..."

# Directory structure check
if [ -d ".claude" ]; then
    echo "✅ .claude directory exists"
else
    echo "❌ .claude directory missing"
    exit 1
fi

# Context files check
for file in WORKFLOW-STATE.md CONTEXT.md HANDOFF-LOG.md SESSION-MEMORY.md; do
    if [ -f ".claude/context/$file" ]; then
        echo "✅ Context file $file exists"
    else
        echo "❌ Context file $file missing"
    fi
done

# MCP tools check (when agents are available)
echo "🔧 Testing MCP tool integration..."
# Tool tests will be added when agents are implemented

echo "✅ ClaudeCraftsman setup verification complete!"
```

### First Workflow Test
```bash
# Test basic workflow (when agents are available)
claude-code "/design 'Simple test feature for validation'"

# Validate output
ls -la .claude/docs/current/
cat .claude/context/WORKFLOW-STATE.md
```

## Success Criteria

### Setup Success Indicators
- [ ] **Directory Structure**: Complete .claude/ hierarchy created
- [ ] **Agent Installation**: All agents accessible through Claude Code
- [ ] **Command Integration**: All commands available and functional
- [ ] **MCP Integration**: Research tools working or graceful fallback configured
- [ ] **Context Management**: Context files initialized and functional

### Workflow Success Indicators
- [ ] **First Workflow**: Successfully complete a simple design workflow
- [ ] **Quality Standards**: Outputs meet craftsman quality requirements
- [ ] **File Organization**: Documents created in proper locations with correct naming
- [ ] **Research Integration**: Claims backed by verifiable sources
- [ ] **Context Preservation**: Workflow state properly maintained

### User Experience Success
- [ ] **Setup Time**: Completed in under 30 minutes
- [ ] **Clarity**: Setup process clear and easy to follow
- [ ] **Validation**: All components working as expected
- [ ] **Documentation**: User can navigate and understand the system
- [ ] **Confidence**: User ready to begin development with ClaudeCraftsman

## Next Steps After Setup

### Immediate Actions
1. **Read User Guide**: Review complete user guide for comprehensive understanding
2. **Test Basic Workflow**: Try a simple `/design` command with a test feature
3. **Validate Quality**: Confirm outputs meet expected craftsman standards
4. **Explore Documentation**: Familiarize yourself with available templates and standards

### First Project Recommendations
1. **Start Small**: Begin with a simple feature to learn the workflow
2. **Focus on Quality**: Apply craftsman principles from the beginning
3. **Use Research**: Take advantage of research integration capabilities
4. **Maintain Organization**: Follow file organization standards consistently

### Learning Path
1. **Craftsman Philosophy**: Understand the principles behind quality-focused development
2. **Agent Specializations**: Learn when and how to use different craftspeople
3. **Research Integration**: Master the use of evidence-based development
4. **Workflow Optimization**: Develop efficient patterns for your specific needs

## Support and Resources

### Documentation Resources
- **User Guide**: `.claude/project-mgt/05-documentation/user-guide.md`
- **Craftsman Philosophy**: `.claude/project-mgt/01-project-overview/craftsman-philosophy.md`
- **Technical Specifications**: `.claude/project-mgt/02-technical-design/`
- **Templates and Standards**: `.claude/project-mgt/07-standards-templates/`

### Troubleshooting Resources
- **Common Issues**: Check troubleshooting section in user guide
- **Error Recovery**: Reference context recovery procedures
- **Quality Standards**: Review quality checklists and standards
- **File Organization**: Validate against naming conventions and structure

### Community and Support
- **Documentation**: Comprehensive documentation available in project-mgt/
- **Examples**: Sample workflows and usage patterns
- **Quality Standards**: Clear criteria for craftsman-quality outputs
- **Continuous Improvement**: Framework evolves based on user feedback

## Advanced Setup Options

### Custom Agent Creation
```bash
# Setup for creating custom specialized craftspeople
cp .claude/project-mgt/07-standards-templates/agent-template.md .claude/templates/
# Follow agent creation guide for custom specializations
```

### Team Collaboration Setup
```bash
# Configure for team usage
# Setup shared context and coordination protocols
# Document team-specific standards and conventions
```

### Integration with Development Tools
```bash
# Version control integration
echo ".claude/context/" >> .gitignore  # Exclude temporary context
git add .claude/agents/ .claude/commands/ .claude/templates/

# CI/CD integration (advanced)
# Configure quality gates in CI/CD pipeline
# Setup automated quality validation
```

## Maintenance and Updates

### Regular Maintenance
**Weekly**: Validate directory structure and file organization
**Monthly**: Review and update project configuration
**Quarterly**: Assess setup effectiveness and improvement opportunities
**As Needed**: Update agents and commands when new versions available

### Update Procedures
**Agent Updates**: Replace agent definitions with new versions
**Command Updates**: Update command definitions as enhancements become available
**Standard Updates**: Incorporate improved standards and templates
**Configuration Updates**: Adjust configuration based on usage patterns

### Backup and Recovery
**Context Backup**: Regular backup of .claude/context/ directory
**Configuration Backup**: Backup project configuration and customizations
**Recovery Procedures**: Steps to restore from backup if needed
**Version Control**: Use git to track changes and enable rollback

---

**Setup Guide Maintained By**: ClaudeCraftsman Project Team
**Last Updated**: 2025-08-03
**User Testing**: Validated with typical development environment setups
**Support**: Reference user guide and documentation for ongoing support

*"A well-prepared workspace enables the craftsman to focus on creation rather than fighting with tools. Take time to set up properly, and the investment will pay dividends in every project."*
