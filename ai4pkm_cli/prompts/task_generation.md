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
   - `status`: TBD
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
- created: {current_datetime} (full ISO format: YYYY-MM-DDTHH:MM:SS)
- generation_log: "{generation_log_link}" (link to this KTG execution log)

Ensure the 'created' property uses full datetime format, not just date.

NOTE: Do NOT create separate log or report files in AI/Tasks/Logs/. System logging is handled automatically. Only create the task file in AI/Tasks/ as specified in the KTG workflow.
```

## Customization

The main KTG workflow logic is defined in `_Settings_/Prompts/Knowledge Task Generator (KTG).md`.

This system prompt ensures:
- Generation logs are properly linked to created tasks
- Created datetime uses full ISO format with time component
- All required properties are included in task frontmatter
