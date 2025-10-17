# Task Execution Prompt (KTP Phase 2)

This is a system prompt used by the Knowledge Task Processor (KTP) Phase 2 to instruct agents on how to execute knowledge tasks.

## Purpose
- Guides processing agents (Claude Code, Gemini CLI, etc.) on task execution
- Defines expected outputs and status updates
- Ensures consistent task completion behavior

## Prompt Template

```
Process the knowledge task defined in the file: {task_path}

Follow the instructions in the task file and update the task file with:
- Process Log entries documenting your work
- Output property with wiki links to created files
- Status updated to PROCESSED when complete
```

## Placeholders
- `{task_path}`: Absolute path to the task file being executed

## Agent Expectations
The processing agent should:
1. Read and understand the task instructions
2. Execute the required work
3. Document all actions in the Process Log section
4. Update the `output` frontmatter property with wiki links to created files (format: `[[File/Path]]`)
5. Update the `status` property to `PROCESSED` when complete

## Customization
To modify how agents execute tasks, edit this template. Changes apply immediately to new task executions.
