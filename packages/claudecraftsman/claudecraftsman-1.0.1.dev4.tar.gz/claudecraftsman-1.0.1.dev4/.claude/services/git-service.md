---
name: git-service
description: Framework-wide Git service wrapper providing seamless MCP Git tools integration with Bash fallback. Makes Git operations a pervasive, invisible part of the ClaudeCraftsman fabric.
type: service
---

# Git Service
*Seamless version control integration for the ClaudeCraftsman framework*

## Service Overview

The Git Service provides a unified interface for all Git operations throughout the ClaudeCraftsman framework. It prioritizes MCP Git tools for optimal integration while maintaining robust Bash fallback for reliability.

## Architecture

### Service Interface
```typescript
interface GitService {
  // Core Operations
  status(): GitStatus;

  branch: {
    create(name: string, from?: string): void;
    switch(name: string): void;
    delete(name: string): void;
    current(): string;
    list(pattern?: string): string[];
  };

  commit: {
    create(message: string, files?: string[]): void;
    amend(message?: string): void;
    semantic(action: AgentAction): string;
    withContext(message: string, metadata: CommitMetadata): void;
  };

  remote: {
    push(branch?: string, options?: PushOptions): void;
    pull(branch?: string, options?: PullOptions): void;
    fetch(remote?: string): void;
  };

  // GitHub Flow Operations
  flow: {
    startFeature(name: string): void;
    finishFeature(squash?: boolean): void;
    createPR(title: string, body: string): PRResult;
    updatePR(prNumber: number, additions: string): void;
    mergePR(prNumber: number, method?: MergeMethod): void;
  };

  // Framework-Specific Operations
  context: {
    getCurrentPhase(): WorkflowPhase;
    getAgentHistory(): AgentCommit[];
    suggestBranch(workType: string): string;
    getFrameworkMetadata(): FrameworkMetadata;
  };

  // Utility Operations
  utils: {
    isClean(): boolean;
    hasConflicts(): boolean;
    resolveConflicts(strategy: ConflictStrategy): void;
    stash(message?: string): void;
    unstash(stashId?: number): void;
  };
}
```

### Implementation Strategy

```typescript
class GitServiceImpl implements GitService {
  private mcpAvailable: boolean = false;

  constructor() {
    this.checkMCPAvailability();
  }

  private async checkMCPAvailability(): Promise<void> {
    try {
      // Test MCP git tool availability
      await this.executeMCP('git_status', { repo_path: '.' });
      this.mcpAvailable = true;
    } catch {
      this.mcpAvailable = false;
      console.log('MCP Git tools not available, using Bash fallback');
    }
  }

  private async executeGitOperation(
    operation: string,
    mcpParams?: any,
    bashCommand?: string
  ): Promise<any> {
    if (this.mcpAvailable) {
      try {
        return await this.executeMCP(operation, mcpParams);
      } catch (error) {
        // Fallback to Bash on MCP failure
        if (bashCommand) {
          return await this.executeBash(bashCommand);
        }
        throw error;
      }
    } else if (bashCommand) {
      return await this.executeBash(bashCommand);
    } else {
      throw new Error(`Operation ${operation} not available without MCP`);
    }
  }
}
```

## Core Operations

### Status Operations
```typescript
async status(): Promise<GitStatus> {
  const result = await this.executeGitOperation(
    'git_status',
    { repo_path: '.' },
    'git status --porcelain'
  );

  return this.parseStatus(result);
}
```

### Branch Management
```typescript
branch = {
  async create(name: string, from?: string): Promise<void> {
    const base = from || 'HEAD';
    await this.executeGitOperation(
      'git_create_branch',
      { repo_path: '.', branch_name: name, base_branch: base },
      `git checkout -b ${name} ${base}`
    );
  },

  async switch(name: string): Promise<void> {
    await this.executeGitOperation(
      'git_checkout',
      { repo_path: '.', branch_name: name },
      `git checkout ${name}`
    );
  },

  async current(): Promise<string> {
    const result = await this.executeGitOperation(
      'git_branch',
      { repo_path: '.', branch_type: 'local' },
      'git branch --show-current'
    );
    return this.parseCurrentBranch(result);
  }
};
```

### Semantic Commit Generation
```typescript
commit = {
  async semantic(action: AgentAction): Promise<string> {
    const { type, scope, description, agent, phase } = action;

    // Generate semantic commit message
    const header = `${type}(${scope}): ${description}`;

    const body = [
      '',
      `Agent: ${agent}`,
      `Phase: ${phase}`,
      `Framework: ClaudeCraftsman v1.0`,
      `Quality: ✓ Passed gates`,
      `Timestamp: ${new Date().toISOString()}`
    ].join('\n');

    return `${header}\n${body}`;
  },

  async withContext(message: string, metadata: CommitMetadata): Promise<void> {
    const enrichedMessage = this.enrichCommitMessage(message, metadata);

    await this.executeGitOperation(
      'git_commit',
      { repo_path: '.', message: enrichedMessage },
      `git commit -m "${enrichedMessage}"`
    );
  }
};
```

## GitHub Flow Integration

### Feature Branch Workflow
```typescript
flow = {
  async startFeature(name: string): Promise<void> {
    const branchName = `feature/${name}`;

    // Ensure we're on main/master
    await this.branch.switch('main');

    // Pull latest changes
    await this.remote.pull();

    // Create and switch to feature branch
    await this.branch.create(branchName);

    // Initial commit
    await this.commit.withContext(
      `feat: start ${name} feature`,
      { agent: 'git-service', phase: 'initialization' }
    );
  },

  async finishFeature(squash: boolean = false): Promise<void> {
    const currentBranch = await this.branch.current();

    if (!currentBranch.startsWith('feature/')) {
      throw new Error('Not on a feature branch');
    }

    // Push branch
    await this.remote.push(currentBranch);

    // Create PR
    const pr = await this.createPR(
      `Feature: ${currentBranch.replace('feature/', '')}`,
      this.generatePRBody()
    );

    console.log(`PR created: ${pr.url}`);
  }
};
```

## Framework Context Integration

### Agent-Aware Git Operations
```typescript
context = {
  async getAgentHistory(): Promise<AgentCommit[]> {
    const log = await this.executeGitOperation(
      'git_log',
      { repo_path: '.', max_count: 100 },
      'git log --format="%H|%s|%b" -100'
    );

    return this.parseAgentCommits(log);
  },

  suggestBranch(workType: string): string {
    const timestamp = new Date().toISOString().split('T')[0];

    const branchPatterns = {
      'agent': (name: string) => `feature/agent-${name}`,
      'command': (name: string) => `feature/command-${name}`,
      'bugfix': (desc: string) => `fix/${desc}-${timestamp}`,
      'feature': (name: string) => `feature/${name}`,
      'refactor': (area: string) => `refactor/${area}-${timestamp}`,
      'docs': (topic: string) => `docs/${topic}-${timestamp}`
    };

    return branchPatterns[workType] || `feature/unnamed-${timestamp}`;
  }
};
```

## Quality Gate Integration

### Pre-Commit Validation
```typescript
async validateCommit(files: string[]): Promise<ValidationResult> {
  const checks = [
    this.checkCraftsmanStandards(files),
    this.checkFileNaming(files),
    this.checkDocumentation(files),
    this.runTests(files)
  ];

  const results = await Promise.all(checks);

  return {
    passed: results.every(r => r.passed),
    issues: results.flatMap(r => r.issues || [])
  };
}
```

### Commit Message Standards
```typescript
private validateCommitMessage(message: string): boolean {
  const semanticPattern = /^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .+/;
  const agentPattern = /Agent: .+/m;
  const qualityPattern = /Quality: ✓ Passed gates/m;

  return semanticPattern.test(message) &&
         agentPattern.test(message) &&
         qualityPattern.test(message);
}
```

## Error Handling and Recovery

### Conflict Resolution
```typescript
utils = {
  async resolveConflicts(strategy: ConflictStrategy): Promise<void> {
    const hasConflicts = await this.hasConflicts();

    if (!hasConflicts) return;

    switch (strategy) {
      case 'ours':
        await this.executeBash('git checkout --ours .');
        break;
      case 'theirs':
        await this.executeBash('git checkout --theirs .');
        break;
      case 'manual':
        throw new Error('Manual conflict resolution required');
      case 'smart':
        await this.smartConflictResolution();
        break;
    }

    await this.executeGitOperation(
      'git_add',
      { repo_path: '.', files: ['.'] },
      'git add .'
    );
  }
};
```

## Service Configuration

### Environment Variables
```bash
# Git Service Configuration
GIT_SERVICE_MCP_PRIORITY=true      # Prefer MCP over Bash
GIT_SERVICE_AUTO_COMMIT=true       # Auto-commit on significant operations
GIT_SERVICE_BRANCH_PROTECTION=true # Prevent direct main branch commits
GIT_SERVICE_PR_TEMPLATE=true       # Use framework PR templates
```

### Integration Points
- **Commands**: All commands use GitService for version control
- **Agents**: Agents track their Git context through the service
- **Workflows**: Workflow coordinator manages Git flow through service
- **Quality Gates**: Pre-commit hooks validate through service

## Usage Examples

### From Commands
```typescript
// In /add command
const gitService = new GitService();
const branchName = gitService.context.suggestBranch('agent');
await gitService.branch.create(branchName);
await gitService.commit.semantic({
  type: 'feat',
  scope: 'agent',
  description: 'add payment-processor agent',
  agent: 'add-command',
  phase: 'creation'
});
```

### From Agents
```typescript
// In any agent
const gitService = new GitService();
await gitService.commit.withContext(
  'docs: update API documentation',
  {
    agent: 'product-architect',
    phase: 'documentation',
    quality: 'passed',
    files: ['api-docs.md']
  }
);
```

### From Workflows
```typescript
// In workflow coordinator
const gitService = new GitService();
await gitService.flow.startFeature('user-authentication');
// ... coordinate implementation ...
await gitService.flow.finishFeature(true); // Squash commits
```

## Quality Standards

The Git Service maintains craftsman quality through:
- **Semantic Commits**: Every commit tells a story with proper context
- **Branch Hygiene**: Consistent naming and lifecycle management
- **Quality Gates**: Automated validation before commits
- **Context Preservation**: Full framework metadata in commits
- **Graceful Degradation**: Seamless MCP to Bash fallback

---
*Service created: 2025-08-04*
*Framework: ClaudeCraftsman v1.0*
*Making Git invisible yet powerful*
