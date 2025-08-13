"""
Enhanced state management for ClaudeCraftsman.

Provides intelligent state updates, consistency checking, repair functionality,
history tracking, and rollback capabilities.
"""

import json
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from rich.console import Console

from claudecraftsman.core.state import StateManager
from claudecraftsman.utils.logging import logger

console = Console()


class StateChangeType(str, Enum):
    """Types of state changes for history tracking."""

    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    REPAIR = "repair"
    ROLLBACK = "rollback"


class StateChange(BaseModel):
    """Represents a change to the state."""

    model_config = ConfigDict(extra="forbid")

    timestamp: datetime = Field(default_factory=datetime.now)
    change_type: StateChangeType
    target: str  # What was changed (workflow, phase, handoff, etc.)
    details: dict[str, Any]
    previous_value: dict[str, Any] | None = None
    new_value: dict[str, Any] | None = None
    source: str  # What triggered the change (hook, command, repair, etc.)
    correlation_id: str | None = None


class StateConsistencyReport(BaseModel):
    """Report of state consistency check results."""

    model_config = ConfigDict(extra="forbid")

    timestamp: datetime = Field(default_factory=datetime.now)
    is_consistent: bool
    issues: list[dict[str, str]] = Field(default_factory=list)
    repairs_needed: list[dict[str, Any]] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class EnhancedStateManager(StateManager):
    """Enhanced state manager with intelligent features."""

    def __init__(self, config=None) -> None:
        """Initialize enhanced state manager."""
        super().__init__(config)

        # Additional paths for enhanced features
        self.state_history_dir = self.context_dir / "history"
        self.state_backup_dir = self.context_dir / "backups"
        self.state_cache_file = self.context_dir / ".state_cache.json"

        # Ensure directories exist
        self.state_history_dir.mkdir(parents=True, exist_ok=True)
        self.state_backup_dir.mkdir(parents=True, exist_ok=True)

        # State change history
        self.history: list[StateChange] = []
        self._load_recent_history()

    def _load_recent_history(self) -> None:
        """Load recent state change history."""
        # Load last 100 changes from history
        history_files = sorted(self.state_history_dir.glob("*.json"))[-100:]
        for history_file in history_files:
            try:
                with open(history_file) as f:
                    change_data = json.load(f)
                    self.history.append(StateChange(**change_data))
            except Exception as e:
                logger.warning(f"Failed to load history file {history_file}: {e}")

    def _record_change(self, change: StateChange) -> None:
        """Record a state change to history."""
        # Add to in-memory history
        self.history.append(change)

        # Save to disk
        timestamp = change.timestamp.strftime("%Y%m%d_%H%M%S_%f")
        history_file = self.state_history_dir / f"{timestamp}_{change.change_type.value}.json"

        try:
            with open(history_file, "w") as f:
                json.dump(change.model_dump(mode="json"), f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save state change history: {e}")

    def intelligent_update(self, update_type: str, **kwargs) -> bool:
        """
        Intelligently update state based on context and patterns.

        Args:
            update_type: Type of update (phase_progress, document_status, etc.)
            **kwargs: Update-specific parameters

        Returns:
            True if update successful
        """
        # Analyze update context
        if update_type == "phase_progress":
            return self._intelligent_phase_update(**kwargs)
        elif update_type == "document_status":
            return self._intelligent_document_update(**kwargs)
        elif update_type == "workflow_transition":
            return self._intelligent_workflow_transition(**kwargs)
        else:
            logger.warning(f"Unknown update type: {update_type}")
            return False

    def _intelligent_phase_update(self, phase_name: str, new_status: str, **kwargs) -> bool:
        """Intelligently update phase with validation and side effects."""
        state = self.read_workflow_state()
        if not state:
            logger.warning("No workflow state found for phase update")
            return False

        # Find the phase
        phase = None
        for p in state.phases:
            if p.name == phase_name:
                phase = p
                break

        if not phase:
            logger.warning(f"Phase '{phase_name}' not found")
            return False

        # Validate state transition
        valid_transitions = {
            "pending": ["in_progress", "blocked"],
            "in_progress": ["completed", "blocked", "pending"],
            "blocked": ["in_progress", "pending"],
            "completed": [],  # Completed phases shouldn't change
        }

        if new_status not in valid_transitions.get(phase.status, []):
            logger.warning(f"Invalid state transition: {phase.status} -> {new_status}")
            return False

        # Record the change
        old_value = phase.model_dump()

        # Update phase intelligently
        phase.status = new_status

        # Handle status-specific updates
        if new_status == "in_progress":
            if not phase.started_at:
                phase.started_at = datetime.now()
            state.current_phase = phase_name

            # Auto-complete previous in_progress phases
            for other_phase in state.phases:
                if other_phase != phase and other_phase.status == "in_progress":
                    logger.info(f"Auto-completing previous phase: {other_phase.name}")
                    other_phase.status = "completed"
                    if not other_phase.completed_at:
                        other_phase.completed_at = datetime.now()

        elif new_status == "completed":
            if not phase.completed_at:
                phase.completed_at = datetime.now()

            # Check if all phases complete
            all_complete = all(p.status == "completed" for p in state.phases)
            if all_complete:
                state.status = "completed"
                logger.info("All phases complete, marking workflow as completed")

        elif new_status == "blocked":
            # Record blocker reason
            if "reason" in kwargs:
                phase.notes = f"Blocked: {kwargs['reason']}"

        # Apply any additional updates
        if "agent" in kwargs:
            phase.agent = kwargs["agent"]
        if "deliverables" in kwargs:
            phase.deliverables = kwargs["deliverables"]
        if "notes" in kwargs:
            phase.notes = kwargs["notes"]

        # Save state
        if self.write_workflow_state(state):
            # Record change
            self._record_change(
                StateChange(
                    change_type=StateChangeType.UPDATE,
                    target=f"phase:{phase_name}",
                    details={"status": new_status, **kwargs},
                    previous_value=old_value,
                    new_value=phase.model_dump(),
                    source="intelligent_update",
                )
            )

            # Update progress log
            self.update_progress_log(
                f"Phase Update: {phase_name}", f"Status changed to {new_status}"
            )

            return True

        return False

    def _intelligent_document_update(self, filename: str, new_status: str, **kwargs) -> bool:
        """Intelligently update document status with cascading effects."""
        # This would integrate with registry and trigger appropriate actions
        try:
            from claudecraftsman.core.registry import RegistryManager

            registry = RegistryManager(self.config)
        except ImportError:
            logger.warning("Registry module not available")
            return False

        # Update registry
        if registry.update_document_status(filename, new_status):
            # Record change
            self._record_change(
                StateChange(
                    change_type=StateChangeType.UPDATE,
                    target=f"document:{filename}",
                    details={"status": new_status, **kwargs},
                    source="intelligent_update",
                )
            )

            # Trigger side effects
            if new_status == "Complete":
                # Could trigger archive check here
                logger.info(f"Document {filename} marked complete, consider archiving")

            return True

        return False

    def _intelligent_workflow_transition(self, new_status: str, **kwargs) -> bool:
        """Intelligently transition workflow status."""
        state = self.read_workflow_state()
        if not state:
            return False

        old_status = state.status

        # Validate transition
        valid_transitions = {
            "active": ["paused", "completed", "cancelled"],
            "paused": ["active", "cancelled"],
            "completed": [],
            "cancelled": [],
        }

        if new_status not in valid_transitions.get(old_status, []):
            logger.warning(f"Invalid workflow transition: {old_status} -> {new_status}")
            return False

        # Update status
        state.status = new_status

        # Handle status-specific logic
        if new_status == "completed":
            # Ensure all phases are complete
            for phase in state.phases:
                if phase.status != "completed":
                    logger.warning(f"Cannot complete workflow with incomplete phase: {phase.name}")
                    return False

        # Save state
        if self.write_workflow_state(state):
            self._record_change(
                StateChange(
                    change_type=StateChangeType.UPDATE,
                    target="workflow",
                    details={"status": new_status, **kwargs},
                    previous_value={"status": old_status},
                    new_value={"status": new_status},
                    source="intelligent_update",
                )
            )
            return True

        return False

    def check_consistency(self) -> StateConsistencyReport:
        """
        Check state consistency and identify issues.

        Returns:
            StateConsistencyReport with findings
        """
        report = StateConsistencyReport(is_consistent=True)

        # Check workflow state
        state = self.read_workflow_state()
        if not state:
            report.warnings.append("No workflow state found")
            return report

        # Check 1: Current phase should be in_progress
        current_phase = None
        for phase in state.phases:
            if phase.name == state.current_phase:
                current_phase = phase
                break

        if current_phase and current_phase.status != "in_progress":
            report.is_consistent = False
            report.issues.append(
                {
                    "type": "phase_status_mismatch",
                    "description": f"Current phase '{state.current_phase}' is marked as '{current_phase.status}', not 'in_progress'",
                }
            )
            report.repairs_needed.append(
                {
                    "action": "update_phase_status",
                    "phase": state.current_phase,
                    "new_status": "in_progress",
                }
            )

        # Check 2: Only one phase should be in_progress
        in_progress_phases = [p for p in state.phases if p.status == "in_progress"]
        if len(in_progress_phases) > 1:
            report.is_consistent = False
            report.issues.append(
                {
                    "type": "multiple_active_phases",
                    "description": f"Multiple phases in progress: {[p.name for p in in_progress_phases]}",
                }
            )
            # Keep only the current phase as in_progress
            for phase in in_progress_phases:
                if phase.name != state.current_phase:
                    report.repairs_needed.append(
                        {
                            "action": "update_phase_status",
                            "phase": phase.name,
                            "new_status": "pending",
                        }
                    )

        # Check 3: Completed phases should have timestamps
        for phase in state.phases:
            if phase.status == "completed" and not phase.completed_at:
                report.is_consistent = False
                report.issues.append(
                    {
                        "type": "missing_completion_timestamp",
                        "description": f"Phase '{phase.name}' is completed but lacks completion timestamp",
                    }
                )
                report.repairs_needed.append(
                    {"action": "add_completion_timestamp", "phase": phase.name}
                )

            if phase.status in ["in_progress", "completed"] and not phase.started_at:
                report.is_consistent = False
                report.issues.append(
                    {
                        "type": "missing_start_timestamp",
                        "description": f"Phase '{phase.name}' is {phase.status} but lacks start timestamp",
                    }
                )
                report.repairs_needed.append({"action": "add_start_timestamp", "phase": phase.name})

        # Check 4: Workflow status consistency
        all_complete = all(p.status == "completed" for p in state.phases)
        if all_complete and state.status != "completed":
            report.is_consistent = False
            report.issues.append(
                {
                    "type": "workflow_status_mismatch",
                    "description": "All phases complete but workflow not marked as completed",
                }
            )
            report.repairs_needed.append(
                {"action": "update_workflow_status", "new_status": "completed"}
            )

        # Check 5: Registry sync
        try:
            from claudecraftsman.core.registry import RegistryManager

            registry = RegistryManager(self.config)

            # Check if registry has find_unregistered_documents method
            if hasattr(registry, "find_unregistered_documents"):
                unregistered = registry.find_unregistered_documents()
                if unregistered:
                    report.warnings.append(f"Found {len(unregistered)} unregistered documents")
                    report.repairs_needed.append({"action": "sync_registry"})
        except Exception as e:
            report.warnings.append(f"Could not check registry: {e}")

        # Check 6: Orphaned state files
        state_files = [
            self.workflow_state_file,
            self.handoff_log_file,
            self.context_file,
            self.session_memory_file,
        ]

        for state_file in state_files:
            if state_file.exists():
                # Check if file is stale (not updated in 7 days)
                age = datetime.now() - datetime.fromtimestamp(state_file.stat().st_mtime)
                if age > timedelta(days=7):
                    report.warnings.append(f"State file '{state_file.name}' is {age.days} days old")

        return report

    def repair_state(self, report: StateConsistencyReport | None = None) -> bool:
        """
        Repair state inconsistencies.

        Args:
            report: Consistency report to act on (will generate if not provided)

        Returns:
            True if all repairs successful
        """
        if not report:
            report = self.check_consistency()

        if report.is_consistent:
            logger.info("State is consistent, no repairs needed")
            return True

        logger.info(f"Repairing {len(report.repairs_needed)} state issues")

        state = self.read_workflow_state()
        if not state:
            logger.error("Cannot repair without workflow state")
            return False

        # Create backup before repairs
        self.create_backup("pre_repair")

        all_repairs_successful = True

        for repair in report.repairs_needed:
            try:
                if repair["action"] == "update_phase_status":
                    # Find and update phase
                    for phase in state.phases:
                        if phase.name == repair["phase"]:
                            phase.status = repair["new_status"]
                            logger.info(
                                f"Updated phase '{phase.name}' status to '{repair['new_status']}'"
                            )
                            break

                elif repair["action"] == "add_completion_timestamp":
                    for phase in state.phases:
                        if phase.name == repair["phase"]:
                            phase.completed_at = datetime.now()
                            logger.info(f"Added completion timestamp to phase '{phase.name}'")
                            break

                elif repair["action"] == "add_start_timestamp":
                    for phase in state.phases:
                        if phase.name == repair["phase"]:
                            phase.started_at = datetime.now()
                            logger.info(f"Added start timestamp to phase '{phase.name}'")
                            break

                elif repair["action"] == "update_workflow_status":
                    state.status = repair["new_status"]
                    logger.info(f"Updated workflow status to '{repair['new_status']}'")

                elif repair["action"] == "sync_registry":
                    from claudecraftsman.core.registry import RegistryManager

                    registry = RegistryManager(self.config)
                    registry.sync_registry()
                    logger.info("Synced document registry")

            except Exception as e:
                logger.error(f"Failed to apply repair {repair}: {e}")
                all_repairs_successful = False

        # Save repaired state
        if self.write_workflow_state(state):
            self._record_change(
                StateChange(
                    change_type=StateChangeType.REPAIR,
                    target="workflow_state",
                    details={"repairs_applied": len(report.repairs_needed)},
                    source="repair_state",
                )
            )
        else:
            all_repairs_successful = False

        return all_repairs_successful

    def create_backup(self, reason: str = "manual") -> Path | None:
        """
        Create a backup of current state.

        Args:
            reason: Reason for backup (manual, pre_repair, etc.)

        Returns:
            Path to backup directory or None if failed
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.state_backup_dir / f"{timestamp}_{reason}"

        try:
            backup_dir.mkdir(parents=True, exist_ok=True)

            # Backup all state files
            state_files = {
                "workflow_state": self.workflow_state_file,
                "handoff_log": self.handoff_log_file,
                "context": self.context_file,
                "session_memory": self.session_memory_file,
                "progress_log": self.progress_log_file,
            }

            for _name, source_file in state_files.items():
                if source_file.exists():
                    dest_file = backup_dir / source_file.name
                    dest_file.write_text(source_file.read_text())

            # Save backup metadata
            metadata = {
                "timestamp": timestamp,
                "reason": reason,
                "files_backed_up": [name for name, f in state_files.items() if f.exists()],
            }

            with open(backup_dir / "backup_metadata.json", "w") as f:
                json.dump(metadata, f, indent=2)

            logger.info(f"Created state backup: {backup_dir}")
            return backup_dir

        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return None

    def rollback_to(self, backup_path: Path) -> bool:
        """
        Rollback state to a previous backup.

        Args:
            backup_path: Path to backup directory

        Returns:
            True if rollback successful
        """
        if not backup_path.exists():
            logger.error(f"Backup path does not exist: {backup_path}")
            return False

        # Create backup of current state before rollback
        self.create_backup("pre_rollback")

        try:
            # Restore each file
            for backup_file in backup_path.glob("*.md"):
                if backup_file.name == "WORKFLOW-STATE.md":
                    target = self.workflow_state_file
                elif backup_file.name == "HANDOFF-LOG.md":
                    target = self.handoff_log_file
                elif backup_file.name == "CONTEXT.md":
                    target = self.context_file
                elif backup_file.name == "SESSION-MEMORY.md":
                    target = self.session_memory_file
                elif backup_file.name == "progress-log.md":
                    target = self.progress_log_file
                else:
                    continue

                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(backup_file.read_text())
                logger.info(f"Restored {backup_file.name}")

            # Record rollback
            self._record_change(
                StateChange(
                    change_type=StateChangeType.ROLLBACK,
                    target="all_state_files",
                    details={"backup_path": str(backup_path)},
                    source="rollback_to",
                )
            )

            logger.info(f"Successfully rolled back to {backup_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to rollback: {e}")
            return False

    def get_state_history(self, limit: int = 50) -> list[StateChange]:
        """
        Get recent state change history.

        Args:
            limit: Maximum number of changes to return

        Returns:
            List of recent state changes
        """
        # Return from in-memory cache first
        if self.history:
            return sorted(self.history, key=lambda x: x.timestamp, reverse=True)[:limit]

        # Load from disk if needed
        history_files = sorted(self.state_history_dir.glob("*.json"), reverse=True)[:limit]
        changes = []

        for history_file in history_files:
            try:
                with open(history_file) as f:
                    change_data = json.load(f)
                    changes.append(StateChange(**change_data))
            except Exception as e:
                logger.warning(f"Failed to load history file {history_file}: {e}")

        return changes

    def prune_old_backups(self, keep_days: int = 7) -> int:
        """
        Remove old backups to save space.

        Args:
            keep_days: Number of days to keep backups

        Returns:
            Number of backups removed
        """
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        removed_count = 0

        for backup_dir in self.state_backup_dir.iterdir():
            if backup_dir.is_dir():
                # Parse timestamp from directory name
                try:
                    timestamp_str = backup_dir.name.split("_")[0] + backup_dir.name.split("_")[1]
                    backup_date = datetime.strptime(timestamp_str[:8], "%Y%m%d")

                    if backup_date < cutoff_date:
                        # Remove old backup
                        import shutil

                        shutil.rmtree(backup_dir)
                        removed_count += 1
                        logger.info(f"Removed old backup: {backup_dir.name}")

                except Exception as e:
                    logger.warning(f"Could not process backup directory {backup_dir}: {e}")

        return removed_count
