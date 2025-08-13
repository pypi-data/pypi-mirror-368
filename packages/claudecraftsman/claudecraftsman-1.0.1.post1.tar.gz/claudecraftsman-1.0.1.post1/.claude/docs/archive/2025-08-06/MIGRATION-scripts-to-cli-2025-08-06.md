# Script to CLI Migration Analysis
*Date: 2025-08-06*

## Overview
Analysis of which `.claude/scripts/` are replaced by our CLI implementation and which might still be needed.

## Script Status

### ✅ Fully Replaced by CLI

1. **framework-state-update.sh** → `cc state` commands
   - `cc state document-created` - Record new documents
   - `cc state document-completed` - Mark documents complete
   - `cc state phase-started` - Record phase starts
   - `cc state phase-completed` - Record phase completions
   - `cc state handoff` - Record agent handoffs
   - `cc state show` - Display current state

2. **enforce-quality-gates.sh** → `cc validate` commands
   - `cc validate pre-operation` - Pre-operation quality gates
   - `cc validate quality` - Comprehensive quality validation
   - `cc validate checklist` - Generate quality checklist

3. **validate-operation.sh** → `cc validate pre-operation`
   - Merged into the pre-operation validation command

### ⚠️ Partially Replaced

1. **auto-archive.sh** - Not directly replaced
   - The `StateManager` class has archiving methods
   - But no CLI command explicitly triggers archiving
   - Could add: `cc state archive [document]`

2. **update-registry.sh** - Indirectly replaced
   - Registry updates happen automatically via `cc state document-created`
   - No standalone registry update command

3. **update-workflow-state.sh** - Indirectly replaced
   - Workflow updates happen via `cc state phase-*` commands
   - No direct workflow state manipulation command

4. **update-progress-log.sh** - Indirectly replaced
   - Progress logging happens automatically in state commands
   - No standalone progress log command

### ❓ Not Replaced (May Not Be Needed)

1. **archive-integration-example.sh** - Example script, not core functionality
2. **example-command-integration.sh** - Example script, not core functionality
3. **command-hooks.sh** - Hook system handled differently in CLI
4. **quality-gate-integration.sh** - Integration example, not core functionality

## Recommendation

### Option 1: Complete Migration (Recommended)
Remove `.claude/scripts/` entirely and update all references:

1. **Add missing CLI commands:**
   ```bash
   cc state archive [document] [reason]  # Archive a document
   cc state clean-archives              # Clean old archives
   ```

2. **Update framework templates:**
   - Replace all script references in `/add` command template
   - Update to use CLI commands instead

3. **Benefits:**
   - Single source of truth (Python implementation)
   - Better error handling and validation
   - Consistent interface
   - No bash dependency

### Option 2: Keep Minimal Scripts
Keep only scripts that provide value beyond CLI:
- `auto-archive.sh` - For automated archiving workflows
- Remove all example and integration scripts
- Remove replaced scripts

### Option 3: Keep All Scripts (Not Recommended)
- Maintains backward compatibility
- But creates confusion and duplication
- Harder to maintain two implementations

## Implementation Plan for Option 1

1. **Add `cc state archive` command:**
   ```python
   @app.command("archive")
   def archive_document(
       filename: str,
       reason: str = typer.Argument("Superseded"),
   ) -> None:
       """Archive a document with reason."""
       state_manager = StateManager()
       if state_manager.archive_document(filename, reason):
           console.print(f"✓ Archived '{filename}'")
   ```

2. **Update add.md template:**
   ```bash
   # Old:
   framework-state-update.sh document-created "file.md" "Type" "location" "purpose"

   # New:
   cc state document-created "file.md" "Type" "location" "purpose"
   ```

3. **Remove scripts directory:**
   ```bash
   rm -rf .claude/scripts/
   ```

## Decision Needed
Should we complete the migration to CLI-only (Option 1) or keep some scripts (Option 2)?
