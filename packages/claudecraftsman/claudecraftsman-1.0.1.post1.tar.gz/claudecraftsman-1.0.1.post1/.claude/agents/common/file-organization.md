# File Organization Standards
*Universal file organization patterns for all agents*

**Usage**: Include in agents with `@.claude/agents/common/file-organization.md`

---

## File Organization - The Craftsman's Workshop
All documents are created in proper locations:

**Document Hierarchy:**
```
.claude/docs/
├── current/                    # Current active specifications
│   ├── {{DOCUMENT_PREFIX}}-[project-name].md   # Always use consistent naming
│   └── {{ADDITIONAL_DOCS}}
├── archive/                    # Superseded versions
│   └── [date]/                 # Organized by date when superseded
└── registry.md                # Master index of all documents
```

## Document Naming Standards
- **Primary Documents**: `{{DOCUMENT_PREFIX}}-[project-name]-[YYYY-MM-DD].md`
- **Supporting Documents**: `{{SUPPORT_DOC_PATTERN}}`
- **Time Awareness**: Use current date from `time` MCP tool for all timestamps
- **Consistency**: Always follow framework naming conventions

## Directory Organization
**{{DOMAIN}} Specific Structure**:
```
.claude/{{BASE_PATH}}/
├── {{PRIMARY_FOLDER}}/         # {{PRIMARY_DESC}}
├── {{SECONDARY_FOLDER}}/       # {{SECONDARY_DESC}}
└── {{ADDITIONAL_FOLDERS}}
```

## Registry Management
All created documents MUST be registered:
- Update `.claude/docs/current/registry.md` immediately after creation
- Include: filename, type, location, date, status, purpose
- Use atomic updates to prevent conflicts
- Maintain chronological order

## Archive Process
When documents are superseded:
1. Create archive folder: `.claude/docs/archive/[YYYY-MM-DD]/`
2. Move superseded documents to archive
3. Update registry to reflect new status
4. Preserve all version history

## State File Updates
After creating any document:
```bash
# Update registry
- Read current registry.md
- Add new entry to active documents table
- Write updated registry.md
- Commit the registry update

# Update workflow state
- Update WORKFLOW-STATE.md with document creation
- Note phase progress and next steps
- Commit state changes
```

## Quality Standards
- [ ] All files in proper `.claude/` directories
- [ ] Consistent naming with `{{DOCUMENT_PREFIX}}-[name]-[date].md` format
- [ ] Registry updated immediately after file creation
- [ ] Archive process followed for superseded documents
- [ ] State files kept current with all changes

## Variable Reference
When importing file organization, customize these variables:
- `{{DOCUMENT_PREFIX}}`: Primary document type prefix (e.g., "PRD", "TECH-SPEC", "ADR")
- `{{ADDITIONAL_DOCS}}`: Other document patterns for this agent
- `{{SUPPORT_DOC_PATTERN}}`: Supporting document naming pattern
- `{{DOMAIN}}`: Agent's domain (e.g., "Product", "Technical", "Architecture")
- `{{BASE_PATH}}`: Base directory path under .claude/
- `{{PRIMARY_FOLDER}}`: Main folder name
- `{{PRIMARY_DESC}}`: Description of primary folder contents
- `{{SECONDARY_FOLDER}}`: Secondary folder name (if applicable)
- `{{SECONDARY_DESC}}`: Description of secondary folder contents
- `{{ADDITIONAL_FOLDERS}}`: Any additional folder structures

## Integration Example
```markdown
@.claude/agents/common/file-organization.md
<!-- Variables for file organization:
{{DOCUMENT_PREFIX}} = "PRD"
{{ADDITIONAL_DOCS}} = "BDD-scenarios-[project-name].md"
{{SUPPORT_DOC_PATTERN}} = "BDD-[feature]-[date].md"
{{DOMAIN}} = "Product"
{{BASE_PATH}} = "docs"
{{PRIMARY_FOLDER}} = "PRDs"
{{PRIMARY_DESC}} = "Product Requirements Documents"
{{SECONDARY_FOLDER}} = "scenarios"
{{SECONDARY_DESC}} = "BDD test scenarios"
{{ADDITIONAL_FOLDERS}} = "research/          # Market research and user studies"
-->
```
