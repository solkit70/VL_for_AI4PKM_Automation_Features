# Task Generation Prompt (KTG)

This is a system prompt used by the Knowledge Task Generator (KTG) to create tasks from request files.

## Purpose
- Instructs agents on how to process task generation requests
- Defines task creation requirements
- Ensures ALL tasks create task files for proper record-keeping

## Key Instructions

**CRITICAL: ALL tasks MUST create task files, regardless of complexity.**
This includes simple tasks, quick lookups, and immediate operations.
Task files provide essential audit trails and execution tracking.

**EXCEPTIONS - Update existing task files instead of creating new ones:**
- When #AI tag is in an existing task file (AI/Tasks/)
- When request is to update outcome/result of an existing task
- See detailed exceptions at end of this document

**Task Execution Strategy:**
- Simple tasks: Execute immediately, set status to COMPLETED or FAILED
- Complex tasks: Create task file with status TBD for TaskProcessor to handle

When creating a task file, the agent should:

1. **Include generation_log property** in frontmatter
   - Format: `generation_log: "{generation_log_link}"`
   - This links the created task to the KTG execution log

2. **Required frontmatter properties**:
   - `title`: Task title/description
   - `priority`: P1 (content creation) or P2 (workflow/maintenance)
   - `status`: "TBD" (MUST be exactly "TBD" in quotes)
   - `archived`: false
   - `created`: Full datetime in ISO format (YYYY-MM-DDTHH:MM:SS)
   - `source`: Wiki link to original document
   - `generation_log`: Wiki link to KTG execution log (provided in prompt context)

3. **Required sections**:
   - Input (full context with blockquotes)
   - Context (time/speaker/type)
   - Requirements (structured preferences)
   - Inferred (input/output/instructions/budget)

## Prompt Context

When KTG is executed, the prompt includes:
- Path to the task request file
- Generation log link (if available): `{generation_log_link}`

The agent should extract the generation log link from the prompt and add it to the task file frontmatter.

## System Prompt Template

This prompt is automatically added to KTG execution context:

```
{ktg_request_prompt}

=== TASK FILE CREATION ===

ALWAYS create task files for ALL requests (audit trail required).

File naming: AI/Tasks/YYYY-MM-DD [Informative Description].md
• Use descriptive names that indicate the actual work, not generic labels
• Good: "2025-10-22 EIC Process Article on AI Agents.md"
• Good: "2025-10-22 Research PKM Best Practices.md"
• Bad: "2025-10-22 Task.md" or "2025-10-22 Process File.md"
• Include key subject/topic in filename for easy identification

EXCEPTIONS - Update existing task instead:
• Request is to update outcome of EXISTING task → Update that task file
• #AI tag is in existing task file (AI/Tasks/) → Update that task file

=== EXECUTION ===

Simple tasks (file ops, lookups, journal updates):
1. Create task file with status "TBD"
2. Execute immediately
3. Update status to "COMPLETED" or "FAILED"

Complex tasks (EIC, research, multi-step work):
1. Create task file with status "TBD"
2. Do NOT execute - leave for TaskProcessor

=== REQUIRED PROPERTIES ===

Frontmatter:
- created: {current_datetime}
- status: "TBD" then "COMPLETED"/"FAILED" (simple) or "TBD" (complex)
- generation_log: "{generation_log_link}"
- source: "[[Original/Source/File]]"
- priority: "P1" or "P2"
- task_type: descriptive type

Valid statuses: TBD, IN_PROGRESS, PROCESSED, COMPLETED, FAILED, NEEDS_INPUT
```
