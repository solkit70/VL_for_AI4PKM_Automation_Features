# Task Execution Prompt (KTP Phase 2)

This is a system prompt used by the Knowledge Task Processor (KTP) Phase 2 to instruct agents on how to execute knowledge tasks.

## Purpose
- Guides processing agents (Claude Code, Gemini CLI, etc.) on task execution
- Defines expected outputs and status updates
- Ensures consistent task completion behavior

## Prompt Template

```
Process the knowledge task defined in the file: {task_path}

## Critical Requirements

⚠️ **Follow these rules exactly:**

1. **Output Location**: Create files at the EXACT path specified in task
   - Read "## Output" or "## Inferred > Output" section first
   - Use that exact path - don't change to "better" location
   - Wrong location = task will fail

2. **Complete the Work**: Don't mark PROCESSED unless actually complete
   - For EIC: Summary AND full ICT with multiple ### subsections
   - ICT must NOT end mid-sentence or be truncated
   - If you can't complete it, mark NEEDS_INPUT (don't fake completion)

3. **Update Task File**:
   - Add entries to "## Process Log" documenting your work
   - Set output property with wiki links to created files
   - Update status to PROCESSED only when truly done

## Before Marking PROCESSED

Check these items:

**For EIC tasks:**
- ✓ Summary section complete
- ✓ ICT section has multiple ### subsections
- ✓ ICT does NOT end mid-sentence
- ✓ ICT length matches original source
- ✓ Files at specified locations

**For all tasks:**
- ✓ All required outputs created
- ✓ Files complete, not truncated
- ✓ Correct file locations

**If incomplete:** Complete the work NOW or mark NEEDS_INPUT (don't mark PROCESSED)
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
