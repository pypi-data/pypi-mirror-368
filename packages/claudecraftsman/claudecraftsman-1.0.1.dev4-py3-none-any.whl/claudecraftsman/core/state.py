"""
State management for ClaudeCraftsman.

Handles workflow state, progress tracking, and handoff coordination.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator
from rich.console import Console

from claudecraftsman.core.config import Config, get_config

console = Console()


class WorkflowPhase(BaseModel):
    """Represents a workflow phase."""

    model_config = ConfigDict(extra="forbid")

    name: str
    status: str = Field(default="pending", pattern="^(pending|in_progress|completed|blocked)$")
    agent: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    deliverables: list[str] = Field(default_factory=list)
    notes: str | None = None


class WorkflowState(BaseModel):
    """Represents the current workflow state."""

    model_config = ConfigDict(extra="forbid")

    project: str
    workflow_type: str | None = None
    current_phase: str
    status: str = Field(default="active", pattern="^(active|paused|completed|cancelled)$")
    phases: list[WorkflowPhase] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @field_validator("updated_at", mode="before")
    @classmethod
    def update_timestamp(cls, v: datetime | object) -> datetime:
        """Always update the timestamp when model is modified."""
        return datetime.now()


class HandoffEntry(BaseModel):
    """Represents a handoff between agents."""

    model_config = ConfigDict(extra="forbid")

    timestamp: datetime = Field(default_factory=datetime.now)
    from_agent: str
    to_agent: str
    workflow: str
    context_summary: str
    deliverables: list[str] = Field(default_factory=list)
    next_phase_briefing: str
    quality_status: str = Field(default="pending")


class StateManager:
    """Manages ClaudeCraftsman state files."""

    def __init__(self, config: Config | None = None) -> None:
        """Initialize state manager."""
        self.config = config or get_config()
        self.context_dir = self.config.paths.context_dir
        self.docs_dir = self.config.paths.docs_dir
        self.project_mgt_dir = self.config.paths.claude_dir / "project-mgt"

        # Define state file paths
        self.workflow_state_file = self.context_dir / "WORKFLOW-STATE.md"
        self.handoff_log_file = self.context_dir / "HANDOFF-LOG.md"
        self.context_file = self.context_dir / "CONTEXT.md"
        self.session_memory_file = self.context_dir / "SESSION-MEMORY.md"
        self.progress_log_file = self.project_mgt_dir / "06-project-tracking" / "progress-log.md"

    def ensure_context_dir(self) -> bool:
        """Ensure context directory exists."""
        try:
            self.context_dir.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            console.print(f"[red]Error creating context directory: {e}[/red]")
            return False

    def read_workflow_state(self) -> WorkflowState | None:
        """Read current workflow state from markdown file."""
        if not self.workflow_state_file.exists():
            return None

        try:
            content = self.workflow_state_file.read_text()
            lines = content.strip().split("\n")

            # Parse basic metadata
            project = None
            workflow_type = None
            current_phase = None
            status = "active"

            for line in lines:
                if line.startswith("**Project**:"):
                    project = line.split(":", 1)[1].strip()
                elif line.startswith("**Workflow Type**:"):
                    workflow_type = line.split(":", 1)[1].strip()
                elif line.startswith("**Current Phase**:"):
                    current_phase = line.split(":", 1)[1].strip()
                elif line.startswith("**Status**:"):
                    status = line.split(":", 1)[1].strip()

            if not project:
                return None

            # Create state object (phases will be empty for now)
            state = WorkflowState(
                project=project,
                workflow_type=workflow_type,
                current_phase=current_phase or "Unknown",
                status=status,
                phases=[],
            )

            # Parse phases
            in_phase = False
            current_phase_data: dict[str, object] = {}

            for line in lines:
                if line.startswith("### "):
                    # Start of a new phase
                    if current_phase_data:
                        # Save previous phase
                        phase = WorkflowPhase(**current_phase_data)  # type: ignore[arg-type]
                        state.phases.append(phase)

                    # Extract phase name and status icon
                    phase_line = line[4:].strip()
                    if "✅" in phase_line:
                        phase_status = "completed"
                    elif "🔄" in phase_line:
                        phase_status = "in_progress"
                    elif "🚧" in phase_line:
                        phase_status = "blocked"
                    else:
                        phase_status = "pending"

                    phase_name = (
                        phase_line.replace("✅", "")
                        .replace("🔄", "")
                        .replace("🚧", "")
                        .replace("⏳", "")
                        .strip()
                    )

                    current_phase_data = {
                        "name": phase_name,
                        "status": phase_status,
                    }
                    in_phase = True
                elif in_phase and line.startswith("- **"):
                    # Parse phase details
                    if "**Agent**:" in line:
                        current_phase_data["agent"] = line.split(":", 1)[1].strip()
                    elif "**Notes**:" in line:
                        current_phase_data["notes"] = line.split(":", 1)[1].strip()

            # Don't forget the last phase
            if current_phase_data:
                phase = WorkflowPhase(**current_phase_data)  # type: ignore[arg-type]
                state.phases.append(phase)

            return state

        except Exception as e:
            console.print(f"[red]Error reading workflow state: {e}[/red]")
            return None

    def write_workflow_state(self, state: WorkflowState) -> bool:
        """Write workflow state to markdown file."""
        if not self.ensure_context_dir():
            return False

        try:
            # Generate markdown content
            content = f"""# Workflow State

**Project**: {state.project}
**Workflow Type**: {state.workflow_type or "General"}
**Current Phase**: {state.current_phase}
**Status**: {state.status}
**Created**: {state.created_at.strftime("%Y-%m-%d %H:%M UTC")}
**Updated**: {state.updated_at.strftime("%Y-%m-%d %H:%M UTC")}

## Phases

"""
            for phase in state.phases:
                status_emoji = {
                    "pending": "⏳",
                    "in_progress": "🔄",
                    "completed": "✅",
                    "blocked": "🚧",
                }.get(phase.status, "❓")

                content += f"### {phase.name} {status_emoji}\n"
                content += f"- **Status**: {phase.status}\n"
                if phase.agent:
                    content += f"- **Agent**: {phase.agent}\n"
                if phase.started_at:
                    content += f"- **Started**: {phase.started_at.strftime('%Y-%m-%d %H:%M UTC')}\n"
                if phase.completed_at:
                    content += (
                        f"- **Completed**: {phase.completed_at.strftime('%Y-%m-%d %H:%M UTC')}\n"
                    )
                if phase.deliverables:
                    content += f"- **Deliverables**: {', '.join(phase.deliverables)}\n"
                if phase.notes:
                    content += f"- **Notes**: {phase.notes}\n"
                content += "\n"

            self.workflow_state_file.write_text(content)
            return True

        except Exception as e:
            console.print(f"[red]Error writing workflow state: {e}[/red]")
            return False

    def add_handoff_entry(self, entry: HandoffEntry) -> bool:
        """Add a handoff entry to the log."""
        if not self.ensure_context_dir():
            return False

        try:
            # Read existing content or create new
            if self.handoff_log_file.exists():
                content = self.handoff_log_file.read_text()
            else:
                content = "# Handoff Log\n\n"

            # Append new entry
            content += f"""## Handoff: {entry.from_agent} → {entry.to_agent}
**Timestamp**: {entry.timestamp.strftime("%Y-%m-%d %H:%M UTC")}
**Workflow**: {entry.workflow}

### Context Summary
{entry.context_summary}

### Deliverables
{chr(10).join(f"- {d}" for d in entry.deliverables)}

### Next Phase Briefing
{entry.next_phase_briefing}

**Quality Status**: {entry.quality_status}

---

"""
            self.handoff_log_file.write_text(content)
            return True

        except Exception as e:
            console.print(f"[red]Error adding handoff entry: {e}[/red]")
            return False

    def update_progress(self, phase_name: str, status: str, notes: str | None = None) -> bool:
        """Update progress for a specific phase."""
        state = self.read_workflow_state()
        if not state:
            console.print("[yellow]No active workflow state found[/yellow]")
            return False

        # Find and update the phase
        phase_found = False
        for phase in state.phases:
            if phase.name == phase_name:
                phase.status = status
                if status == "in_progress" and not phase.started_at:
                    phase.started_at = datetime.now()
                elif status == "completed" and not phase.completed_at:
                    phase.completed_at = datetime.now()
                if notes:
                    phase.notes = notes
                phase_found = True
                break

        if not phase_found:
            console.print(f"[yellow]Phase '{phase_name}' not found in workflow[/yellow]")
            return False

        # Update current phase if needed
        if status == "in_progress":
            state.current_phase = phase_name

        return self.write_workflow_state(state)

    def get_current_context(self) -> dict[str, WorkflowState | str | None]:
        """Get current context from all state files."""
        context: dict[str, WorkflowState | str | None] = {
            "workflow_state": None,
            "last_handoff": None,
            "project_context": None,
            "session_memory": None,
        }

        # Read workflow state
        workflow = self.read_workflow_state()
        if workflow:
            context["workflow_state"] = workflow

        # Read other context files
        if self.context_file.exists():
            context["project_context"] = self.context_file.read_text()

        if self.session_memory_file.exists():
            context["session_memory"] = self.session_memory_file.read_text()

        return context

    def update_progress_log(self, action: str, details: str) -> bool:
        """Update the progress log with a new entry."""
        try:
            # Ensure directory exists
            self.progress_log_file.parent.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
            entry = f"\n## {timestamp} - {action}\n{details}\n"

            # Append to log file
            if self.progress_log_file.exists():
                content = self.progress_log_file.read_text()
                content += entry
            else:
                content = f"# Progress Log\n\n{entry}"

            self.progress_log_file.write_text(content)
            return True

        except Exception as e:
            console.print(f"[red]Error updating progress log: {e}[/red]")
            return False

    def document_created(self, filename: str, doc_type: str, location: str, purpose: str) -> bool:
        """Record creation of a new document."""
        from claudecraftsman.core.registry import DocumentEntry, RegistryManager

        # Update registry
        registry = RegistryManager(self.config)
        entry = DocumentEntry(
            document=filename,
            type=doc_type,
            location=location,
            created=datetime.now().strftime("%Y-%m-%d"),
            status="Active",
            purpose=purpose,
        )

        if not registry.add_document(entry):
            return False

        # Log progress
        self.update_progress_log(
            f"Document Created: {filename}", f"Created {doc_type} document in {location}: {purpose}"
        )

        return True

    def document_completed(self, filename: str) -> bool:
        """Mark a document as completed."""
        from claudecraftsman.core.registry import RegistryManager

        registry = RegistryManager(self.config)

        # Update registry status
        if not registry.update_document_status(filename, "Complete"):
            return False

        # Log progress
        self.update_progress_log(f"Document Completed: {filename}", "Marked document as complete")

        # TODO: Trigger auto-archive check

        return True

    def phase_started(self, phase: str, agent: str, description: str | None = None) -> bool:
        """Record the start of a new phase."""
        desc = description or f"Starting {phase} phase"

        # Update workflow state
        state = self.read_workflow_state()
        if not state:
            # Create new workflow state
            state = WorkflowState(
                project=self.config.project_root.name,
                workflow_type="General",
                current_phase=phase,
                status="active",
            )

        # Find or create phase
        phase_found = False
        for p in state.phases:
            if p.name == phase:
                p.status = "in_progress"
                p.agent = agent
                p.started_at = datetime.now()
                p.notes = desc
                phase_found = True
                break

        if not phase_found:
            state.phases.append(
                WorkflowPhase(
                    name=phase,
                    status="in_progress",
                    agent=agent,
                    started_at=datetime.now(),
                    notes=desc,
                )
            )

        state.current_phase = phase

        if not self.write_workflow_state(state):
            return False

        # Log progress
        self.update_progress_log(
            f"Phase Started: {phase}", f"Agent {agent} started {phase} phase. {desc}"
        )

        return True

    def phase_completed(self, phase: str, agent: str, description: str | None = None) -> bool:
        """Record the completion of a phase."""
        desc = description or f"Completed {phase} phase"

        # Update workflow state
        state = self.read_workflow_state()
        if not state:
            console.print("[yellow]No active workflow state found[/yellow]")
            return False

        # Find and update phase
        phase_found = False
        for p in state.phases:
            if p.name == phase:
                p.status = "completed"
                p.completed_at = datetime.now()
                p.notes = desc
                phase_found = True
                break

        if not phase_found:
            console.print(f"[yellow]Phase '{phase}' not found in workflow[/yellow]")
            return False

        if not self.write_workflow_state(state):
            return False

        # Log progress
        self.update_progress_log(
            f"Phase Completed: {phase}", f"Agent {agent} completed {phase} phase. {desc}"
        )

        return True

    def handoff(self, from_agent: str, to_agent: str, context: str) -> bool:
        """Record a handoff between agents."""
        # Create handoff entry
        entry = HandoffEntry(
            from_agent=from_agent,
            to_agent=to_agent,
            workflow=self.config.project_root.name,
            context_summary=context,
            next_phase_briefing=f"Received handoff from {from_agent}",
            quality_status="pending",
        )

        if not self.add_handoff_entry(entry):
            return False

        # Update workflow state to new agent
        state = self.read_workflow_state()
        if state:
            state.current_phase = "Handoff"
            # Find or create handoff phase
            handoff_phase = None
            for p in state.phases:
                if p.name == "Handoff" and p.agent == to_agent:
                    handoff_phase = p
                    break

            if not handoff_phase:
                state.phases.append(
                    WorkflowPhase(
                        name="Handoff",
                        status="in_progress",
                        agent=to_agent,
                        started_at=datetime.now(),
                        notes=f"Received handoff from {from_agent}",
                    )
                )

            self.write_workflow_state(state)

        # Log progress
        self.update_progress_log(
            "Agent Handoff", f"Handoff from {from_agent} to {to_agent}: {context}"
        )

        return True
