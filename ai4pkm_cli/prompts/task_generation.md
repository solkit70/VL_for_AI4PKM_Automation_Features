# Task Generation Prompt (KTG)

This is a system prompt used by the Knowledge Task Generator (KTG) to create tasks from request files.

## Purpose
- Instructs agents on how to process task generation requests
- Defines task creation requirements
- Specifies when to execute immediately vs create task files

## Key Instructions

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

IMPORTANT: When creating a task file, include these properties in frontmatter:
- status: "TBD" (CRITICAL: Must be exactly "TBD" in quotes - this is required for task processing)
- created: {current_datetime} (full ISO format: YYYY-MM-DDTHH:MM:SS)
- generation_log: "{generation_log_link}" (link to this KTG execution log)

Ensure the 'created' property uses full datetime format, not just date.
NEVER use "pending" or other status values - only "TBD", "COMPLETED", or "NEEDS_INPUT".

NOTE: Do NOT create separate log or report files in AI/Tasks/Logs/. System logging is handled automatically. Only create the task file in AI/Tasks/ as specified in the KTG workflow.

CRITICAL: Special handling for #AI tags in task files (AI/Tasks/):
- When the target file is in AI/Tasks/ (existing task file), DO NOT create a new task
- Instead, resolve the #AI request within the same task file:
  1. Read the task file to understand the context
  2. Address the request or question marked with #AI
  3. Add your response to the "Process Log" section
  4. Remove the #AI tag after addressing it
- This keeps related work consolidated in one task file instead of fragmenting into multiple tasks
- Only create NEW task files when the #AI tag appears in regular notes (outside AI/Tasks/)
```
