"""
Hook handlers for Claude Code integration.

Implements the actual logic for each hook event.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from rich.console import Console

from claudecraftsman.core.archival import DocumentArchiver
from claudecraftsman.core.config import get_config
from claudecraftsman.core.state_enhanced import EnhancedStateManager
from claudecraftsman.core.validation import QualityGates
from claudecraftsman.hooks.enforcers import FrameworkEnforcer
from claudecraftsman.hooks.validators import FrameworkValidator
from claudecraftsman.utils.logging import logger, set_correlation_id

console = Console()


class HookContext(BaseModel):
    """Context passed to hook handlers."""

    model_config = ConfigDict(extra="forbid")

    event: str
    timestamp: datetime = Field(default_factory=datetime.now)
    tool: str | None = None
    args: dict[str, Any] | None = None
    result: dict[str, Any] | None = None
    prompt: str | None = None
    cwd: Path = Field(default_factory=Path.cwd)
    correlation_id: str | None = None


class HookHandler:
    """Handles hook events from Claude Code."""

    def __init__(self) -> None:
        """Initialize hook handler."""
        self.config = get_config()
        # Use enhanced state manager with intelligent features
        self.state_manager = EnhancedStateManager(self.config)
        self.validator = QualityGates()
        self.framework_validator = FrameworkValidator()
        self.framework_enforcer = FrameworkEnforcer()
        self.document_archiver = DocumentArchiver(self.config)

    def handle_pre_tool_use(self, context: HookContext) -> dict[str, Any]:
        """Handle pre-tool use validation with framework enforcement."""
        set_correlation_id(context.correlation_id)
        logger.info(f"Pre-tool validation for {context.tool}")

        # Record MCP tool usage
        if context.tool and context.tool.startswith("mcp__"):
            tool_name = context.tool.split("__")[1]
            self.framework_validator.record_mcp_tool_usage(tool_name)

        # Skip validation for certain tools
        safe_tools = ["Read", "LS", "Grep", "Glob", "Bash"]
        if context.tool in safe_tools:
            return {"allowed": True}

        # Check if we're in a ClaudeCraftsman project
        if not self.config.paths.claude_dir.exists():
            return {"allowed": True, "message": "Not a ClaudeCraftsman project"}

        # Extract file path and content for validation
        filepath = None
        content = None

        if context.tool in ["Write", "Edit", "MultiEdit"] and context.args:
            filepath = context.args.get("file_path")
            content = context.args.get("content") or context.args.get("new_string")

        # Enhanced quality gate: Check for required state updates
        if filepath and ".claude/docs/current/" in filepath:
            # Ensure registry will be updated
            if operation := self._determine_operation(context):
                if operation == "create":
                    logger.info("Document creation detected - registry update will be enforced")
                elif operation == "update":
                    # Check if document status is changing
                    if content and any(
                        marker in content for marker in ["Status: Complete", "Phase: complete"]
                    ):
                        logger.info("Document completion detected - archive check will be enforced")

        # Run framework validations
        violations = []
        if filepath:
            violations = self.framework_validator.validate_all(filepath, content)

        # Run standard quality gates
        report = self.validator.validate_all("pre-operation")

        # Combine results
        if not violations and report.overall_passed:
            return {"allowed": True, "message": "All validations passed"}

        # Process violations - attempt to auto-correct what we can
        if violations:
            corrected_violations = []
            remaining_violations = []

            for violation_type, message in violations:
                if violation_type == "naming_convention" and filepath and context.args:
                    corrected_path = self.framework_enforcer.auto_correct_naming(filepath)
                    context.args["file_path"] = corrected_path
                    logger.info(f"Auto-corrected filepath: {filepath} -> {corrected_path}")
                    corrected_violations.append(violation_type)
                elif violation_type == "hardcoded_dates" and content and context.args:
                    current_date = datetime.now().strftime("%Y-%m-%d")
                    corrected_content = self.framework_enforcer.auto_correct_dates(
                        content, current_date
                    )
                    if "content" in context.args:
                        context.args["content"] = corrected_content
                    elif "new_string" in context.args:
                        context.args["new_string"] = corrected_content
                    logger.info("Auto-corrected hardcoded dates")
                    corrected_violations.append(violation_type)
                elif (
                    violation_type == "file_location"
                    and filepath
                    and ".claude/docs/current/" in filepath
                    and context.args
                ):
                    # Auto-organize the document
                    organized_path = self.framework_enforcer.organize_document(filepath)
                    if organized_path != filepath:
                        context.args["file_path"] = organized_path
                        logger.info(f"Auto-organized document: {filepath} -> {organized_path}")
                        corrected_violations.append(violation_type)
                    else:
                        remaining_violations.append((violation_type, message))
                else:
                    # Cannot auto-correct this violation
                    remaining_violations.append((violation_type, message))

            # If we corrected some violations, check if any remain
            if corrected_violations and not remaining_violations:
                return {
                    "allowed": True,
                    "message": "Framework violations auto-corrected",
                    "corrections": corrected_violations,
                }
            elif corrected_violations and remaining_violations:
                # Some corrected, some remain - block because we can't fix everything
                violations = remaining_violations  # Update violations to remaining ones

        # Build detailed error response
        details = []

        # Add remaining framework violations
        for violation_type, message in violations:
            details.append(
                {
                    "type": "framework",
                    "violation": violation_type,
                    "message": message,
                    "severity": "error",
                }
            )

        # Add quality gate failures
        for r in report.validation_results:
            if not r.passed:
                details.append(
                    {
                        "type": "quality",
                        "gate": r.step,
                        "message": r.message,
                        "severity": r.severity,
                    }
                )

        # If there are non-correctable framework violations, block the operation
        # (Quality gate failures alone don't block in flexible mode)
        framework_violations = [v for v in violations if isinstance(v, tuple)]
        if framework_violations:
            return {
                "allowed": False,
                "error": "Framework validation failed - violations cannot be auto-corrected",
                "details": details,
                "suggestion": "Fix violations manually (e.g., establish time context with MCP time tool)",
            }

        # Only quality gate issues remain - allow with warnings in flexible mode
        # TODO: Add hooks configuration to Config model
        strict_mode = False  # Default to flexible mode

        if strict_mode and not report.overall_passed:
            return {
                "allowed": False,
                "error": "Quality gates failed in strict mode",
                "details": details,
                "suggestion": "Fix quality issues or disable strict mode",
            }
        else:
            # Allow with warnings for quality issues only
            return {
                "allowed": True,
                "warning": "Quality gate warnings detected - proceed with caution",
                "details": details,
            }

    def handle_post_tool_use(self, context: HookContext) -> None:
        """Handle post-tool use state updates with comprehensive framework enforcement."""
        set_correlation_id(context.correlation_id)
        logger.info(f"Post-tool update for {context.tool}")

        if not context.result or not self.config.paths.claude_dir.exists():
            return

        # Determine operation type
        operation = "update"
        if context.tool == "Write":
            operation = "create"
        elif context.tool == "Bash" and context.args:
            # Check for rm/delete operations
            command = context.args.get("command", "")
            if "rm " in command or "delete" in command.lower():
                operation = "delete"

        # Extract file path
        filepath = None
        if context.tool in ["Write", "Edit", "MultiEdit"]:
            filepath = context.args.get("file_path") if context.args else None

        if filepath:
            # Use framework enforcer for comprehensive updates
            try:
                self.framework_enforcer.enforce_post_operation(
                    operation=operation, filepath=filepath, success=True
                )
                logger.info(f"Framework enforcement completed for {operation} on {filepath}")

                # Monitor document changes for archival
                if operation in ["create", "update"] and ".claude/docs/current/" in filepath:
                    self.document_archiver.monitor_document_changes(Path(filepath))

                # Auto-archive old completed documents on any document operation
                if ".claude/docs/" in filepath:
                    self._check_and_archive_old_documents()

                # Update progress log for significant operations
                self._update_progress_for_operation(operation, filepath)

            except Exception as e:
                logger.warning(f"Framework enforcement error: {e}")
                # Fall back to basic state update
                self._basic_state_update(context, operation, filepath)

        # Track additional operations
        if context.tool == "Bash" and context.args:
            command = context.args.get("command", "")
            # Check for git operations
            if command.startswith("git "):
                self._track_git_operation(command)
            # Check for test operations
            elif any(test_cmd in command for test_cmd in ["pytest", "test", "npm test"]):
                self._track_test_operation(command)

        # Check for hook chaining opportunities
        self._check_hook_chaining(context)

    def _basic_state_update(self, context: HookContext, operation: str, filepath: str) -> None:
        """Fallback basic state update if enforcer fails."""
        file_path = Path(filepath)

        # Check if it's in our docs directory
        docs_dir = self.config.paths.docs_dir
        if docs_dir in file_path.parents:
            # Extract document info
            filename = file_path.name
            location = str(file_path.parent.relative_to(self.config.paths.claude_dir))

            # Determine document type from filename
            doc_type = "DOC"
            if "PRD" in filename:
                doc_type = "PRD"
            elif "SPEC" in filename:
                doc_type = "SPEC"
            elif "PLAN" in filename:
                doc_type = "PLAN"

            # Record document creation
            if operation == "create":
                self.state_manager.document_created(
                    filename=filename,
                    doc_type=doc_type,
                    location=location,
                    purpose="Created via Claude Code",
                )

    def _track_git_operation(self, command: str) -> None:
        """Track git operations for workflow context."""
        # Extract git operation type
        git_ops = {
            "git add": "staged",
            "git commit": "committed",
            "git push": "pushed",
            "git pull": "pulled",
            "git checkout": "switched",
            "git merge": "merged",
        }

        for op, action in git_ops.items():
            if command.startswith(op):
                logger.info(f"Git operation tracked: {action}")
                # Could update workflow state here if needed
                break

    def _track_test_operation(self, command: str) -> None:
        """Track test operations for quality gates."""
        logger.info(f"Test operation tracked: {command}")
        # Could update quality gate status here

    def _check_and_archive_old_documents(self) -> None:
        """Check for and archive old completed documents automatically."""
        try:
            # Run auto-archive with default age threshold
            archived_count = self.document_archiver.auto_archive(dry_run=False)
            if archived_count > 0:
                logger.info(f"Auto-archived {archived_count} completed documents")
                console.print(
                    f"[green]✓ Auto-archived {archived_count} completed documents[/green]"
                )
        except Exception as e:
            logger.warning(f"Auto-archive check failed: {e}")

    def _update_progress_for_operation(self, operation: str, filepath: str) -> None:
        """Update progress log for significant file operations."""
        try:
            # Only log significant operations
            if not any(
                pattern in filepath
                for pattern in [
                    ".claude/docs/",
                    ".claude/specs/",
                    ".claude/agents/",
                    ".claude/commands/",
                    "src/",
                    "tests/",
                ]
            ):
                return

            file_path = Path(filepath)
            filename = file_path.name

            # Determine action description
            if operation == "create":
                if ".claude/docs/" in filepath:
                    action = f"Document Created: {filename}"
                    details = f"Created new document in {file_path.parent.name}"
                    # Use intelligent document update for tracking
                    self.state_manager.intelligent_update(
                        "document_status", filename=filename, new_status="Active"
                    )
                elif ".claude/agents/" in filepath:
                    action = f"Agent Created: {filename}"
                    details = "Created new craftsman agent"
                elif ".claude/commands/" in filepath:
                    action = f"Command Created: {filename}"
                    details = "Created new framework command"
                elif "src/" in filepath:
                    action = f"Code Created: {filename}"
                    details = f"Created source file in {file_path.parent.name}"
                else:
                    action = f"File Created: {filename}"
                    details = f"Created file in {file_path.parent.name}"
            elif operation == "update":
                if ".claude/docs/" in filepath:
                    action = f"Document Updated: {filename}"
                    details = f"Updated document in {file_path.parent.name}"
                elif "src/" in filepath:
                    action = f"Code Updated: {filename}"
                    details = f"Updated source file in {file_path.parent.name}"
                else:
                    action = f"File Updated: {filename}"
                    details = f"Updated file in {file_path.parent.name}"
            elif operation == "delete":
                action = f"File Deleted: {filename}"
                details = f"Removed file from {file_path.parent.name}"
            else:
                return

            # Update progress log
            self.state_manager.update_progress_log(action, details)

        except Exception as e:
            logger.warning(f"Failed to update progress log: {e}")

    def _check_hook_chaining(self, context: HookContext) -> None:
        """Check for hook chaining opportunities based on operation patterns."""
        try:
            # Check for document completion triggering archive
            if context.tool in ["Write", "Edit", "MultiEdit"] and context.args:
                filepath = context.args.get("file_path", "")
                content = context.args.get("content") or context.args.get("new_string", "")

                # If document marked as complete, trigger archive check
                if ".claude/docs/current/" in filepath and content:
                    completion_markers = [
                        "Status: Complete",
                        "Phase: complete",
                        "✅ Complete",
                        "Implementation complete",
                        "Document complete",
                    ]
                    if any(marker.lower() in content.lower() for marker in completion_markers):
                        logger.info(
                            f"Document completion detected in {filepath}, triggering archive check"
                        )
                        # Use intelligent document update
                        filename = Path(filepath).name
                        self.state_manager.intelligent_update(
                            "document_status", filename=filename, new_status="Complete"
                        )
                        self._check_and_archive_old_documents()

            # Check for Bash command chaining opportunities
            if context.tool == "Bash" and context.args:
                command = context.args.get("command", "")

                # Check for test completion triggering quality validation
                if any(test_cmd in command for test_cmd in ["pytest", "test"]):
                    if context.result and "passed" in str(context.result).lower():
                        logger.info("Test success detected, updating quality status")
                        # Could trigger quality gate validation here

                # Check for git commit triggering state sync
                if command.startswith("git commit"):
                    logger.info("Git commit detected, syncing framework state")
                    # Trigger registry sync after commit
                    from claudecraftsman.core.registry import RegistryManager

                    registry = RegistryManager(self.config)
                    registry.sync_registry()

        except Exception as e:
            logger.warning(f"Hook chaining check failed: {e}")

    def _determine_operation(self, context: HookContext) -> str | None:
        """Determine the operation type from the context."""
        if context.tool == "Write":
            return "create"
        elif context.tool in ["Edit", "MultiEdit"]:
            return "update"
        elif context.tool == "Bash" and context.args:
            command = context.args.get("command", "")
            if "rm " in command or "delete" in command.lower():
                return "delete"
            return "bash"
        return None

    def handle_user_prompt_submit(self, context: HookContext) -> dict[str, Any]:
        """Handle user prompt command routing."""
        set_correlation_id(context.correlation_id)

        if not context.prompt:
            return {"enhanced": False}

        prompt = context.prompt.strip()

        # Check for framework commands
        if prompt.startswith("/"):
            parts = prompt.split(maxsplit=1)
            command = parts[0][1:]  # Remove leading /
            args = parts[1] if len(parts) > 1 else ""

            # Map commands to CLI equivalents
            command_map = {
                "design": "claudecraftsman workflow design",
                "plan": "claudecraftsman workflow plan",
                "implement": "claudecraftsman workflow implement",
                "workflow": "claudecraftsman workflow",
                "add": "claudecraftsman add",
            }

            if command in command_map:
                cli_command = command_map[command]
                if args:
                    cli_command += f" {args}"

                return {
                    "enhanced": True,
                    "command": cli_command,
                    "message": f"Routing to ClaudeCraftsman: {cli_command}",
                }

        # Check for implicit commands
        implicit_patterns = [
            ("create.*agent", "claudecraftsman add agent"),
            ("create.*command", "claudecraftsman add command"),
            ("design.*system", "claudecraftsman workflow design"),
            ("plan.*feature", "claudecraftsman workflow plan"),
        ]

        prompt_lower = prompt.lower()
        for pattern, cli_command in implicit_patterns:
            if all(word in prompt_lower for word in pattern.split(".*")):
                return {
                    "enhanced": True,
                    "suggestion": cli_command,
                    "message": f"Suggested command: {cli_command}",
                }

        return {"enhanced": False}

    def handle_session_start(self, context: HookContext) -> dict[str, Any]:
        """Handle session initialization with framework validation setup."""
        set_correlation_id(context.correlation_id)
        logger.info("Session initialization")

        # Reset session tracking
        self.framework_validator.session_mcp_tools.clear()
        self.framework_validator.time_context_established = False

        # Check if we're in a ClaudeCraftsman project
        if not self.config.paths.claude_dir.exists():
            return {
                "initialized": False,
                "message": "Not a ClaudeCraftsman project",
            }

        # Run initialization checks
        checks = []

        # Check framework validity
        if self.config.paths.is_valid:
            checks.append("✓ Framework structure valid")
        else:
            checks.append("✗ Framework structure invalid")

        # Check state currency and consistency
        workflow_state = self.state_manager.workflow_state_file
        if workflow_state.exists():
            age = datetime.now() - datetime.fromtimestamp(workflow_state.stat().st_mtime)
            if age.days > 7:
                checks.append(f"⚠ Workflow state is {age.days} days old")
            else:
                checks.append("✓ Workflow state current")

            # Run state consistency check
            consistency_report = self.state_manager.check_consistency()
            if consistency_report.is_consistent:
                checks.append("✓ State files consistent")
            else:
                checks.append(
                    f"⚠ State inconsistencies detected: {len(consistency_report.issues)} issues"
                )
                # Auto-repair if issues found
                if self.state_manager.repair_state(consistency_report):
                    checks.append("✅ State inconsistencies automatically repaired")
                    logger.info("Automatically repaired state inconsistencies on session start")
                else:
                    checks.append("❌ Failed to repair state inconsistencies")
                    logger.warning("Could not repair state inconsistencies")

        # Check document registry
        registry_file = self.config.paths.docs_dir / "current" / "registry.md"
        if registry_file.exists():
            checks.append("✓ Document registry exists")
            # Sync registry on session start
            from claudecraftsman.core.registry import RegistryManager

            registry_manager = RegistryManager(self.config)
            try:
                registry_manager.sync_registry()
                checks.append("✓ Registry synced with filesystem")
            except Exception as e:
                checks.append(f"⚠ Registry sync failed: {e}")
        else:
            checks.append("⚠ Document registry missing")

        # Check for old documents that need archiving
        candidates = self.document_archiver.find_archival_candidates()
        if candidates:
            checks.append(f"📦 {len(candidates)} documents ready for archival")
            # Auto-archive in background
            self._check_and_archive_old_documents()
        else:
            checks.append("✓ No documents need archiving")

        # Check git status
        try:
            from claudecraftsman.utils.git import GitOperations

            git_ops = GitOperations()
            if git_ops.has_uncommitted_changes():
                checks.append("⚠ Uncommitted changes detected")
            else:
                checks.append("✓ Git working tree clean")
        except Exception:
            pass  # Git not available or not a repo

        # Framework enforcement mode
        # TODO: Add hooks configuration to Config model
        strict_mode = False  # Default to flexible mode
        enforcement_mode = "Strict" if strict_mode else "Flexible"
        checks.append(f"⚙ Enforcement mode: {enforcement_mode}")

        # Start framework health monitoring
        try:
            from claudecraftsman.core.enforcement import FrameworkEnforcer

            enforcer = FrameworkEnforcer(self.config)
            enforcer.start_continuous_validation()
            checks.append("✓ Framework health monitoring active")
            logger.info("Started continuous framework health monitoring")
        except Exception as e:
            logger.warning(f"Could not start health monitoring: {e}")
            checks.append("⚠ Health monitoring unavailable")

        # Return initialization status
        return {
            "initialized": True,
            "project": self.config.project_root.name,
            "mode": "Development" if self.config.dev_mode else "Production",
            "enforcement": enforcement_mode,
            "checks": checks,
            "message": f"ClaudeCraftsman ready in {self.config.project_root}",
            "reminders": [
                "Use MCP time tool for current dates",
                "Research with MCP tools for PRDs/SPECs",
                "Include citations for all claims",
                "Follow TYPE-name-YYYY-MM-DD.md naming",
            ],
        }

    def handle_event(self, event_data: dict[str, Any]) -> dict[str, Any]:
        """Main event handler dispatcher."""
        try:
            # Create context from event data
            context = HookContext(
                event=event_data.get("event", "unknown"),
                tool=event_data.get("tool"),
                args=event_data.get("args"),
                result=event_data.get("result"),
                prompt=event_data.get("prompt"),
                correlation_id=event_data.get("correlationId"),
            )

            # Dispatch to appropriate handler
            if context.event == "preToolUse":
                return self.handle_pre_tool_use(context)
            elif context.event == "postToolUse":
                self.handle_post_tool_use(context)
                return {"processed": True}
            elif context.event == "userPromptSubmit":
                return self.handle_user_prompt_submit(context)
            elif context.event == "sessionStart":
                return self.handle_session_start(context)
            else:
                return {"error": f"Unknown event: {context.event}"}

        except Exception as e:
            logger.error(f"Hook handler error: {e}")
            return {"error": str(e)}


def main() -> None:
    """CLI entry point for hook handlers."""
    if len(sys.argv) < 2:
        print("Usage: claudecraftsman hook <command>")
        sys.exit(1)

    command = sys.argv[1]

    # Read event data from stdin
    try:
        event_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        event_data = {}

    handler = HookHandler()

    # Route to appropriate handler based on command
    if command == "validate":
        result = handler.handle_pre_tool_use(HookContext(event="preToolUse", **event_data))
    elif command == "update-state":
        handler.handle_post_tool_use(HookContext(event="postToolUse", **event_data))
        result = {"processed": True}
    elif command == "route-command":
        result = handler.handle_user_prompt_submit(
            HookContext(event="userPromptSubmit", **event_data)
        )
    elif command == "initialize":
        result = handler.handle_session_start(HookContext(event="sessionStart", **event_data))
    else:
        result = {"error": f"Unknown command: {command}"}

    # Output result as JSON
    print(json.dumps(result))


if __name__ == "__main__":
    main()
