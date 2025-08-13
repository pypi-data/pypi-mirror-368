# ClaudeCraftsman Python Package Refactoring Plan

## Overview
- **Feature**: Refactor ClaudeCraftsman into an installable Python package
- **Scope**: Convert shell scripts to Python CLI, enable UV/UVX installation, integrate with Claude Code hooks
- **Timeline**: 4 phases over 2-3 weeks
- **Critical Constraint**: MUST maintain self-hosting capability - framework must work for developing itself

## Requirements
1. **Python Package Structure**: Standard Python package installable via UV/UVX
2. **Typer CLI**: Replace brittle shell scripts with robust Python CLI using Typer
3. **Claude Code Hooks Integration**: Enable framework functions as hooks
4. **Backward Compatibility**: Maintain existing functionality while improving reliability
5. **Installation Simplicity**: One-command installation like SuperClaude
6. **Self-Hosting**: Framework must remain usable for its own development

## Implementation Phases

### Phase 1: Package Structure Setup
**Duration**: 2-3 days
**Tasks**:
- Create standard Python package structure
- Set up pyproject.toml with UV compatibility
- Configure package metadata and dependencies
- Create src/claudecraftsman directory structure
- Set up proper version management

**Directory Structure (Self-Hosting Approach)**:
```
PROJECT_ROOT/
├── CLAUDE.md                    # Active - uses framework for development
├── pyproject.toml               # Package configuration
├── README.md
├── LICENSE
├── .claude/                     # Framework files (ACTIVE for self-hosting)
│   ├── framework.md             # Core framework - used by this project
│   ├── agents/                  # Framework agents - active for development
│   ├── commands/                # Framework commands - active for development
│   ├── scripts/                 # Legacy scripts (being replaced)
│   └── docs/current/            # Project documentation
├── src/
│   └── claudecraftsman/         # Python package source
│       ├── __init__.py
│       ├── __main__.py          # Entry point: python -m claudecraftsman
│       ├── cli/
│       │   ├── __init__.py
│       │   ├── app.py           # Typer app definition
│       │   └── commands/
│       │       ├── __init__.py
│       │       ├── state.py     # State management commands
│       │       ├── validate.py   # Quality gate commands
│       │       ├── install.py    # Installation command
│       │       └── hook.py       # Hook configuration
│       ├── core/
│       │   ├── __init__.py
│       │   ├── state.py         # State management logic
│       │   ├── registry.py      # Document registry
│       │   ├── validation.py    # Quality gates
│       │   └── config.py        # Configuration management
│       ├── hooks/
│       │   ├── __init__.py
│       │   ├── handlers.py      # Hook event handlers
│       │   └── config.py        # Hook configuration generator
│       └── utils/
│           ├── __init__.py
│           ├── git.py           # Git operations
│           └── paths.py         # Path management
└── tests/
```

**Key Design Decisions for Self-Hosting**:
1. Keep `.claude/` directory active in the project root
2. Python package reads from `.claude/` when in development mode
3. Installation copies `.claude/` contents to user's home directory
4. Development mode uses local `.claude/`, installed mode uses `~/.claude/claudecraftsman/`

### Phase 2: Core Python Implementation
**Duration**: 3-4 days
**Tasks**:
- Implement Typer CLI structure with development/production mode detection
- Convert shell scripts to Python modules:
  - `framework-state-update.sh` → `state.py`
  - `enforce-quality-gates.sh` → `validation.py`
  - `update-registry.sh` → `registry.py`
  - Git operations → `git.py`
- Implement proper error handling and logging
- Add type hints and documentation
- Create development mode detection (looks for local `.claude/`)

**Key Components**:
1. **Configuration Management** (`core/config.py`):
   ```python
   class Config:
       def __init__(self):
           self.dev_mode = self._detect_dev_mode()
           self.claude_dir = self._get_claude_dir()

       def _detect_dev_mode(self) -> bool:
           """Check if running in ClaudeCraftsman development mode"""
           if not (Path(".claude").exists() and Path("pyproject.toml").exists()):
               return False

           # Check if this is actually ClaudeCraftsman project
           try:
               with open("pyproject.toml", "r") as f:
                   content = f.read()
                   # Look for our package name in pyproject.toml
                   return 'name = "claudecraftsman"' in content or \
                          'name = "ClaudeCraftsman"' in content
           except Exception:
               return False

       def _get_claude_dir(self) -> Path:
           """Return .claude/ path based on mode"""
           if self.dev_mode:
               # Development mode: use local .claude/
               return Path(".claude").absolute()
           elif Path(".claude").exists():
               # User project with .claude/: use their .claude/
               return Path(".claude").absolute()
           else:
               # No local .claude/: use installed framework
               return Path.home() / ".claude" / "claudecraftsman"
   ```

2. **State Management** (`core/state.py`):
   - Document lifecycle tracking
   - Workflow state management
   - Progress logging
   - Handoff coordination
   - Works with both dev and installed paths

3. **Quality Gates** (`core/validation.py`):
   - Pre-operation validation
   - Framework structure checks
   - Git state verification
   - Documentation standards
   - Path-aware validation

4. **CLI Commands** (`cli/commands/`):
   - `install`: Framework installation (copies .claude/ to ~/.claude/claudecraftsman/)
   - `state`: State management operations
   - `validate`: Quality gate enforcement
   - `archive`: Document archiving
   - `hook`: Hook configuration
   - `dev`: Development mode utilities

### Phase 3: Claude Code Hooks Integration
**Duration**: 2-3 days
**Tasks**:
- Design hook configuration system
- Implement hook handlers for:
  - PreToolUse: Quality gate validation
  - PostToolUse: State updates
  - UserPromptSubmit: Command routing
  - SessionStart: Framework initialization
- Create hook installation/configuration command
- Generate hooks JSON configuration

**Hook Architecture**:
```python
# hooks/handlers.py
class HookHandler:
    def pre_tool_use(self, tool: str, args: dict) -> dict:
        """Validate operations before tool execution"""

    def post_tool_use(self, tool: str, result: dict) -> None:
        """Update state after tool execution"""

    def user_prompt_submit(self, prompt: str) -> dict:
        """Handle command routing and enhancement"""
```

### Phase 4: Testing and Migration
**Duration**: 2-3 days
**Tasks**:
- Write comprehensive test suite
- Create migration script from shell to Python
- Update documentation
- Test UV/UVX installation process
- Create backward compatibility layer
- Release preparation

## Dependencies
- **Python**: 3.9+ (for broad compatibility)
- **Core Dependencies**:
  - `typer[all]`: CLI framework with rich support
  - `pydantic`: Configuration validation
  - `gitpython`: Git operations
  - `rich`: Enhanced terminal output
  - `watchdog`: File system monitoring (optional)

## Success Criteria
1. **Installation**: Single command installation via `uvx claudecraftsman install`
2. **Reliability**: Zero shell script dependencies, pure Python implementation
3. **Performance**: Equal or better performance than shell scripts
4. **Integration**: Seamless Claude Code hooks integration
5. **Compatibility**: Works with existing framework structure
6. **Documentation**: Comprehensive docs for installation and usage
7. **Self-Hosting**: Framework remains fully functional for its own development

## Next Steps
1. **Create pyproject.toml** with proper UV configuration
2. **Set up package structure** following Python best practices
3. **Begin Phase 1 implementation** with basic CLI skeleton
4. **Port first shell script** as proof of concept
5. **Test self-hosting**: Ensure framework can still develop itself

## Technical Decisions

### Why Typer?
- Modern CLI framework with excellent type hints
- Built-in help generation and validation
- Rich terminal output support
- Active development and community

### Why UV?
- Fast, modern Python package manager
- Built-in virtual environment management
- Excellent caching and performance
- Growing adoption in Python community

### Hook Integration Strategy
- JSON-based configuration for flexibility
- Python handlers for reliability
- Backward compatible with manual execution
- Progressive enhancement approach

## Risk Mitigation
1. **Migration Risk**: Keep shell scripts during transition
2. **Compatibility Risk**: Extensive testing on multiple platforms
3. **Performance Risk**: Profile and optimize critical paths
4. **User Experience Risk**: Maintain familiar command structure

## Estimated Timeline
- **Week 1**: Phases 1-2 (Package structure and core implementation)
- **Week 2**: Phase 3 (Hooks integration)
- **Week 3**: Phase 4 (Testing and release)

## Self-Hosting Strategy

### Mode Detection Logic

#### Development Mode (Self-Hosting)
When developing ClaudeCraftsman itself:
1. **Detection**: Has `.claude/` AND `pyproject.toml` with `name = "claudecraftsman"`
2. **Behavior**: Python CLI reads from local `.claude/` for framework files
3. **CLAUDE.md active**: Uses framework for its own development
4. **Real-time testing**: Changes to framework immediately affect development

#### User Project Mode
When user has a project with ClaudeCraftsman:
1. **Detection**: Has `.claude/` but `pyproject.toml` has different project name
2. **Behavior**: Python CLI reads from user's `.claude/` for project files
3. **Framework files**: Come from installed `~/.claude/claudecraftsman/`
4. **Clear separation**: User's project files vs framework files

#### Installed Mode (No Local Project)
When running ClaudeCraftsman commands globally:
1. **Detection**: No local `.claude/` directory
2. **Behavior**: Everything from `~/.claude/claudecraftsman/`
3. **Use case**: Global commands, new project initialization
4. **Standard behavior**: Like any installed Python tool

### Path Resolution Examples

```python
# Scenario 1: Developing ClaudeCraftsman
# cwd: /projects/claudecraftsman/
# pyproject.toml: name = "claudecraftsman"
config = Config()
config.dev_mode == True
config.claude_dir == "/projects/claudecraftsman/.claude"
# Uses: Local framework files (self-hosting)

# Scenario 2: User project using ClaudeCraftsman
# cwd: /projects/my-saas-app/
# pyproject.toml: name = "my-saas-app"
config = Config()
config.dev_mode == False
config.claude_dir == "/projects/my-saas-app/.claude"
# Uses: User's .claude/ for project files
# Framework from: ~/.claude/claudecraftsman/

# Scenario 3: Global command (no project)
# cwd: /home/user/
# No .claude/ or pyproject.toml
config = Config()
config.dev_mode == False
config.claude_dir == "/home/user/.claude/claudecraftsman"
# Uses: Installed framework only
```

### Benefits of Three-Mode Design
- **Self-hosting preserved**: ClaudeCraftsman development uses itself
- **User projects supported**: Clear separation of project vs framework
- **Global commands work**: Can run `claudecraftsman` anywhere
- **No confusion**: Each mode has clear detection and behavior
- **Clean distribution**: Users get standard Python package experience

This plan transforms ClaudeCraftsman from a collection of shell scripts into a professional Python package that's easier to install, more reliable, and better integrated with Claude Code's capabilities - while maintaining the critical self-hosting capability that ensures quality through dogfooding.
