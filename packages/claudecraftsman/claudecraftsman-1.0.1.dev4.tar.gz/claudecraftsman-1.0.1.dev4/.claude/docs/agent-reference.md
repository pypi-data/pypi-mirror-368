# ClaudeCraftsman Agent Reference
*Complete guide to your AI craftspeople*

## Overview

ClaudeCraftsman agents are specialized AI craftspeople, each mastering a specific domain of software development. They work together seamlessly, passing context and maintaining quality standards throughout your project.

## Agent Categories

### 🏗️ Planning & Architecture
- [product-architect](#product-architect) - Business requirements and user research
- [design-architect](#design-architect) - Technical specifications and system design
- [system-architect](#system-architect) - High-level architecture and integration

### 💻 Implementation
- [backend-architect](#backend-architect) - API design and server development
- [frontend-developer](#frontend-developer) - UI components and user experience
- [data-architect](#data-architect) - Database design and data pipelines
- [ml-architect](#ml-architect) - Machine learning systems and AI

### ✅ Quality & Operations
- [qa-architect](#qa-architect) - Testing strategies and quality assurance
- [workflow-coordinator](#workflow-coordinator) - Multi-agent orchestration

### 🔜 Coming Soon
- security-architect - Security and compliance
- devops-architect - Infrastructure and deployment
- mobile-architect - Mobile application development

---

## Planning & Architecture Agents

### product-architect

**Purpose**: Creates comprehensive Product Requirements Documents (PRDs) with user research and market analysis.

**When to Use**:
- Starting new projects or major features
- Need market research and competitive analysis
- Defining business requirements and success metrics
- Creating user personas and journey maps

**Capabilities**:
- Market research using MCP tools with current data
- Competitive analysis and positioning
- User persona development
- Business requirement documentation
- Success metric definition
- BDD scenario creation

**Integration**:
- **Receives from**: Initial project ideas, business objectives
- **Hands off to**: design-architect for technical specifications
- **Collaborates with**: All agents for requirement clarification

**Example Usage**:
```bash
# Triggered automatically by /design command
/design task-management-app

# Or directly for requirements only
/workflow requirements task-management-app
```

**Output Files**:
- `PRD-[project-name]-[YYYY-MM-DD].md`
- `BDD-scenarios-[project-name]-[YYYY-MM-DD].md`

---

### design-architect

**Purpose**: Transforms business requirements into comprehensive technical specifications and system designs.

**When to Use**:
- After PRD completion
- Need technical architecture decisions
- Planning system integrations
- Defining API contracts and data models

**Capabilities**:
- System architecture design
- Technology stack selection
- API specification
- Data model design
- Integration planning
- Performance architecture
- Security design

**Integration**:
- **Receives from**: product-architect (PRD and requirements)
- **Hands off to**: system-architect, implementation agents
- **Collaborates with**: backend-architect, frontend-developer

**Example Usage**:
```bash
# Automatically triggered after product-architect
# Or manually for technical design
/workflow technical-design my-feature
```

**Output Files**:
- `TECH-SPEC-[project-name]-[YYYY-MM-DD].md`
- `API-SPEC-[project-name]-[YYYY-MM-DD].md`
- `DATA-MODEL-[project-name]-[YYYY-MM-DD].md`

---

### system-architect

**Purpose**: High-level system architecture with ultrathink methodology for complex technical challenges.

**When to Use**:
- Complex architectural decisions
- System integration planning
- Performance architecture
- Scalability planning
- Technology evaluation

**Capabilities**:
- Ultrathink deep analysis
- System component design
- Integration architecture
- Performance optimization strategies
- Technology trade-off analysis
- Architectural decision records (ADRs)

**Integration**:
- **Receives from**: design-architect specifications
- **Hands off to**: Implementation agents
- **Collaborates with**: All technical agents

**Special Features**:
- Uses extended reasoning (ultrathink) for complex problems
- Creates architectural decision records
- Evaluates multiple approaches systematically

**Output Files**:
- `ARCHITECTURE-[system-name]-[YYYY-MM-DD].md`
- `ADR-[decision-number]-[title].md`

---

## Implementation Agents

### backend-architect

**Purpose**: TDD-focused backend development with emphasis on reliability, security, and performance.

**When to Use**:
- API development
- Backend service implementation
- Database integration
- Authentication/authorization
- Background job processing

**Capabilities**:
- RESTful API design
- GraphQL implementation
- Database query optimization
- Authentication systems
- Message queue integration
- Microservices architecture
- TDD/BDD implementation

**Integration**:
- **Receives from**: design-architect, system-architect
- **Hands off to**: qa-architect for testing
- **Collaborates with**: data-architect, frontend-developer

**Code Standards**:
- Test-first development
- SOLID principles
- Clean architecture
- Comprehensive error handling
- Performance optimization

**Output Examples**:
```typescript
// Example API endpoint with TDD
describe('UserController', () => {
  it('should create user with valid data', async () => {
    // Test implementation
  });
});

class UserController {
  async createUser(userData: CreateUserDto): Promise<User> {
    // Implementation following TDD
  }
}
```

---

### frontend-developer

**Purpose**: Component-focused UI development with emphasis on user experience and accessibility.

**When to Use**:
- UI component creation
- User interface implementation
- Responsive design
- Accessibility improvements
- Frontend performance optimization

**Capabilities**:
- React/Vue/Angular components
- Responsive design
- Accessibility (WCAG 2.1 AA)
- State management
- CSS-in-JS
- Performance optimization
- Progressive enhancement

**Integration**:
- **Receives from**: design-architect, product-architect
- **Hands off to**: qa-architect for testing
- **Collaborates with**: backend-architect for APIs

**Quality Standards**:
- Component reusability
- Accessibility by default
- Performance budgets
- Responsive design
- Cross-browser compatibility

**Output Examples**:
```tsx
// Example React component with accessibility
const Button: React.FC<ButtonProps> = ({
  children,
  onClick,
  variant = 'primary',
  disabled = false,
  ariaLabel
}) => {
  return (
    <button
      className={styles[variant]}
      onClick={onClick}
      disabled={disabled}
      aria-label={ariaLabel}
      role="button"
    >
      {children}
    </button>
  );
};
```

---

### data-architect

**Purpose**: Database design, data modeling, and data pipeline architecture for scalable solutions.

**When to Use**:
- Database schema design
- Data pipeline creation
- ETL/ELT processes
- Data warehouse design
- Performance optimization
- Data migration planning

**Capabilities**:
- Relational database design (PostgreSQL, MySQL)
- NoSQL modeling (MongoDB, DynamoDB)
- Data warehouse architecture
- Stream processing
- Data quality frameworks
- Performance tuning
- Scalability planning

**Integration**:
- **Receives from**: design-architect, backend-architect
- **Hands off to**: backend-architect, ml-architect
- **Collaborates with**: All data-consuming agents

**Expertise Areas**:
- Schema normalization
- Index optimization
- Query performance
- Data integrity
- Backup strategies
- Replication patterns

**Output Files**:
- `DATA-MODEL-[project]-[YYYY-MM-DD].md`
- `SCHEMA-[database]-[YYYY-MM-DD].sql`
- `MIGRATION-[version]-[description].sql`

---

### ml-architect

**Purpose**: Machine learning systems design with focus on production deployment and MLOps.

**When to Use**:
- ML feature development
- Model architecture design
- ML pipeline creation
- Production deployment
- A/B testing setup
- Model monitoring

**Capabilities**:
- Neural network architecture
- Classical ML algorithms
- Feature engineering
- Model serving strategies
- MLOps pipeline design
- Experiment tracking
- Model versioning
- Responsible AI practices

**Integration**:
- **Receives from**: data-architect, product-architect
- **Hands off to**: backend-architect for serving
- **Collaborates with**: data-architect for pipelines

**Framework Support**:
- PyTorch, TensorFlow
- scikit-learn, XGBoost
- MLflow, Kubeflow
- Model serving platforms

**Output Examples**:
```python
# Example ML pipeline architecture
class RecommendationPipeline:
    def __init__(self):
        self.preprocessor = DataPreprocessor()
        self.feature_engineer = FeatureEngineer()
        self.model = RecommendationModel()

    def train(self, data: pd.DataFrame) -> ModelArtifact:
        # Training pipeline with MLOps integration
        pass
```

---

## Quality & Operations Agents

### qa-architect

**Purpose**: Comprehensive testing strategies and quality assurance with BDD/TDD focus.

**When to Use**:
- Test strategy design
- Test suite creation
- Quality metrics definition
- Performance testing
- Security testing
- Accessibility testing

**Capabilities**:
- Test strategy design
- BDD/TDD implementation
- E2E test creation (Playwright)
- Performance testing
- Security testing
- Accessibility validation
- Test automation
- CI/CD integration

**Integration**:
- **Receives from**: All implementation agents
- **Hands off to**: deployment pipeline
- **Collaborates with**: All agents for quality

**Testing Layers**:
- Unit tests (80%+ coverage)
- Integration tests
- E2E tests
- Performance tests
- Security tests
- Accessibility tests

**MCP Tool Usage**:
- Playwright for E2E testing
- Sequential for test planning
- Time tool for test timing

---

### workflow-coordinator

**Purpose**: Orchestrates multi-agent workflows with context preservation and handoff management.

**When to Use**:
- Complex multi-phase projects
- Need coordination between agents
- Context preservation critical
- Workflow automation required

**Capabilities**:
- Multi-agent orchestration
- Context preservation
- Handoff management
- Progress tracking
- Dependency coordination
- Parallel work streams
- Quality gate enforcement

**Integration**:
- **Coordinates**: All other agents
- **Manages**: Handoff briefs and context
- **Tracks**: Workflow state and progress

**Workflow Types**:
- Design-to-deploy
- Troubleshooting
- Refactoring
- Feature development
- System integration

**Context Files**:
- `WORKFLOW-STATE.md`
- `HANDOFF-LOG.md`
- `CONTEXT.md`

---

## Agent Collaboration Patterns

### Sequential Handoffs
```
product-architect → design-architect → system-architect → implementation
```

### Parallel Coordination
```
                ┌→ backend-architect
design-architect ┤
                └→ frontend-developer
```

### Iterative Refinement
```
implementation ⟷ qa-architect ⟷ implementation
```

## Best Practices

### 1. Let Agents Focus on Their Domain
Each agent is optimized for specific tasks. Don't force backend-architect to do frontend work.

### 2. Maintain Context Through Handoffs
Always use workflow-coordinator for complex multi-agent tasks to preserve context.

### 3. Trust Agent Expertise
Agents have deep domain knowledge. Let them guide technical decisions.

### 4. Quality Gates Between Agents
Each handoff includes quality validation to maintain standards.

### 5. Use Appropriate Communication
Agents communicate through structured handoff documents, not informal chats.

## Common Agent Workflows

### Full Feature Development
```bash
/workflow design-to-deploy new-feature
```
Agents involved: product-architect → design-architect → backend/frontend → qa-architect

### API Development
```bash
/workflow api-development user-service
```
Agents involved: design-architect → backend-architect → qa-architect

### Database Optimization
```bash
/workflow database-optimization
```
Agents involved: data-architect → backend-architect → qa-architect

### ML Feature Development
```bash
/workflow ml-feature recommendation-engine
```
Agents involved: ml-architect → data-architect → backend-architect → qa-architect

## Agent Configuration

### Model Selection
Most agents use `opus` model for deep reasoning, except:
- frontend-developer: Can use faster models for component generation
- workflow-coordinator: Uses fast models for orchestration

### MCP Tool Integration
All agents have access to:
- `time`: Current datetime awareness
- `searxng`: Web research
- `crawl4ai`: Documentation fetching
- `context7`: Library documentation
- `playwright`: Testing (qa-architect primary)
- `sequential`: Complex reasoning

### Quality Standards
Every agent enforces:
- Time awareness (no hardcoded dates)
- Research backing (citations required)
- File organization standards
- Craftsman quality principles
- Git integration

## Extending the Agent System

### Adding New Agents
```bash
/add agent security-architect
```

Template automatically includes:
- Craftsman philosophy
- MCP tool integration
- Quality gates
- Handoff protocols

### Customizing Agents
Edit agent files in `.claude/agents/` to:
- Add domain-specific knowledge
- Integrate new tools
- Modify quality standards
- Enhance capabilities

---

*Remember: Each agent is a master craftsperson in their domain. Respect their expertise, maintain their standards, and let them collaborate to create something beautiful.*
