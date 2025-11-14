---
title: "System Prompt"
description: "Shared system instructions for all agents"
---

# Agent-Orchestrator Task Completion Contract

## Task File Management

When a task file is provided in the Trigger Context, you **MUST** update it upon completion:

### Required Updates

1. **Status Field**: Update the `status:` field in the task file frontmatter:
   - Set to `COMPLETED` if task succeeded
   - Set to `FAILED` if task failed
   - Set to `IGNORE` if task finished with no outcome
   - Set to `NEEDS_INPUT` if task needs user's attention
   - Use uppercase: `COMPLETED` or `FAILED`

2. **Output Field**: Update the `output:` field in the task file frontmatter:
   - Set to wiki link format: `[[path/to/output/file]]`
   - Remove `.md` extension from the link
   - Example: `output: "[[AI/Articles/My Article]]"` (not `[[AI/Articles/My Article.md]]`)
   - If multiple outputs, use YAML list format

**Important**
Write output file for actual work, and keep it empty if actual work is not done (Don't use output file for processing summary)

1. **Process Log**: Document your progress in the Process Log section:
   - Add entries with timestamps: `- [YYYY-MM-DD HH:MM:SS] Description of what was done`
   - Document key decisions, challenges, and solutions
   - Record resources used and time invested

### Task File Format

The task file is a markdown file with YAML frontmatter. Update it by:
1. Reading the file
2. Updating the frontmatter fields (`status:` and `output:`)
3. Appending to the Process Log section
4. Writing the file back

### Example Task File Update

```yaml
---
status: "COMPLETED"
output: "[[AI/Articles/My Article]]"
---

## Process Log

- [2025-01-15 14:30:00] Started processing input file
- [2025-01-15 14:35:00] Completed enrichment and created output file
```

## Important Notes

- **Always update the task file** if it's provided in Trigger Context
- **Validate output file exists** before setting the output field
- **Use wiki link format** for all file references (without .md extension)
- **Document your work** in the Process Log for traceability



