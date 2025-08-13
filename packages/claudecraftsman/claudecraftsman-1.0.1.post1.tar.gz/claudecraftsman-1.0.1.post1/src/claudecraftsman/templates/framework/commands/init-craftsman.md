# Init Craftsman Command
*Bootstrap ClaudeCraftsman framework in new projects*

## Command: `/init-craftsman`
**Purpose**: Initialize the ClaudeCraftsman framework in a new project
**Philosophy**: Every project deserves the thoughtful structure that enables true craftsmanship

## Usage
```
/init-craftsman [project-name] [--type=web|api|mobile|desktop] [--framework=react|vue|express|flask]
```

## Parameters
- **project-name**: Name of the project (default: current directory name)
- **--type**: Project type for appropriate templates
  - `web`: Web application (default)
  - `api`: API/backend service
  - `mobile`: Mobile application
  - `desktop`: Desktop application
- **--framework**: Technology framework for customized setup
  - `react`: React.js frontend
  - `vue`: Vue.js frontend
  - `express`: Express.js backend
  - `flask`: Flask Python backend

## Initialization Process

### Phase 1: Time Context and Validation
**Actions**:
1. Use `time` MCP tool to establish current datetime
2. Validate project directory and permissions
3. Check for existing ClaudeCraftsman setup
4. Gather project requirements and preferences

### Phase 2: Directory Structure Creation
**Directory Structure**:
```
.claude/
├── agents/                      # Project-specific agent customizations
├── commands/                    # Project-specific commands
├── docs/                        # Runtime documentation
│   ├── current/                 # Active specifications
│   │   └── registry.md          # Document registry
│   ├── archive/                 # Superseded versions by date
│   └── templates/               # Working templates
├── specs/                       # Technical specifications
│   ├── api-specifications/      # OpenAPI and contracts
│   ├── database-schemas/        # Database designs
│   └── component-specifications/ # Frontend components
├── context/                     # Runtime context files
│   ├── WORKFLOW-STATE.md        # Current workflow status
│   ├── CONTEXT.md               # Project context
│   ├── HANDOFF-LOG.md           # Agent transitions
│   └── SESSION-MEMORY.md        # Session continuity
├── templates/                   # Reusable templates
└── project-mgt/                 # Project management (optional)
```

### Phase 3: CLAUDE.md Configuration
**Primary Configuration File**:
```markdown
# ClaudeCraftsman: [Project Name]
*Artisanal development with intention and care*

## Framework Activation
@~/.claude/claudecraftsman/framework.md

## Project Configuration
- **Project**: [Project Name]
- **Type**: [Project Type]
- **Framework**: [Technology Framework]
- **Initialized**: [Current Date]
- **Standards**: Research-driven specifications, time-aware documentation

## Project Context
[Project-specific context and requirements]

## Available Craftspeople
@~/.claude/claudecraftsman/agents/

## Available Commands
@~/.claude/claudecraftsman/commands/

## Quick Commands
- `/design` - Start comprehensive design process
- `/workflow` - Multi-agent coordination
- `/implement` - Implementation with design integration
```

### Phase 4: Template Installation
**Templates Created**:
- PRD template customized for project type
- Technical specification template
- BDD scenarios template
- Handoff brief template
- Quality checklist template

### Phase 5: Initial Context Setup
**Context Files Initialized**:
```markdown
# WORKFLOW-STATE.md
**Project**: [Project Name]
**Current Phase**: Initialization
**Framework Version**: ClaudeCraftsman 1.0
**Initialized**: [Current Date from time MCP tool]
**Status**: Ready for design phase

# CONTEXT.md
**Project Overview**: [Brief description]
**Key Stakeholders**: [To be defined]
**Success Criteria**: [To be defined]
**Quality Standards**: Craftsman-level quality throughout

# registry.md
# ClaudeCraftsman Document Registry: [Project Name]

## Current Active Documents
*No documents yet - ready for `/design` command*

## Project History
- [Current Date]: Project initialized with ClaudeCraftsman framework
```

## Validation and Testing
**Initialization Verification**:
- [ ] All directories created successfully
- [ ] CLAUDE.md configuration valid and imports working
- [ ] Context files initialized with current timestamps
- [ ] Templates available and properly formatted
- [ ] Framework activation confirmed
- [ ] Ready for design commands

## Post-Initialization Guidance
**Next Steps**:
1. **Define Project Goals**: Use `/design` to create comprehensive project requirements
2. **Research Phase**: Conduct market research and user analysis
3. **Architecture Planning**: Develop technical specifications
4. **Implementation Strategy**: Create detailed implementation plans

**Success Message**:
```
✅ ClaudeCraftsman Framework Initialized Successfully!

Project: [Project Name]
Location: [Project Directory]
Framework: ClaudeCraftsman v1.0
Initialized: [Current Date]

🎯 Ready for artisanal development!
   Use `/design [feature-name]` to begin with comprehensive planning.

📁 Project structure created with craftsman standards:
   - Documentation: .claude/docs/current/
   - Context management: .claude/context/
   - Quality templates: .claude/templates/

🔧 Framework activated in CLAUDE.md
   All subsequent sessions will use craftsman standards.

📚 Next steps:
   1. Run `/design [your-first-feature]` to create comprehensive specifications
   2. Review generated PRD and technical specifications
   3. Use `/implement` when ready to begin development

Happy crafting! 🛠️
```

## Error Handling
**Common Issues**:
- **Permission Denied**: Check write permissions in project directory
- **Existing Framework**: Handle upgrade/migration scenarios gracefully
- **Invalid Project Type**: Provide guidance on supported types
- **Framework Installation**: Verify ~/.claude/claudecraftsman/ exists

**Recovery Procedures**:
- Backup existing configuration before initialization
- Provide rollback option if initialization fails
- Clear error messages with specific resolution steps
- Support contact information for complex issues

## Integration
**Framework Dependencies**:
- Requires ~/.claude/claudecraftsman/ framework installation
- Uses MCP tools (time, searxng, crawl4ai, context7)
- Compatible with existing Claude Code projects
- Preserves existing CLAUDE.md with backup

**Command Relationships**:
- **Enables**: All other ClaudeCraftsman commands
- **Precedes**: `/design`, `/workflow`, `/implement`
- **Supports**: Project lifecycle from inception to deployment
- **Maintains**: Consistent craftsman standards across all projects
