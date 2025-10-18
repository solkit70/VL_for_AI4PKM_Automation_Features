# Task Evaluation Prompt (KTP Phase 3)

This is a system prompt used by the Knowledge Task Processor (KTP) Phase 3 to evaluate completed tasks.

## Purpose
- Guides evaluation agents on quality assessment
- Defines criteria for APPROVED vs NEEDS_REWORK decisions
- Ensures consistent task validation

## Prompt Template

```
Review and complete this task to mark it as COMPLETED.

Task File: {task_path}
Task Type: {task_type}
Priority: {priority}

## Original Instructions
{instructions}

## Output Files
{output_section}

## Your Role: Complete the Work

⚠️ **This is your only chance to complete this task.**

Your job is to ensure the work is finished and meets requirements. If the work is incomplete:
1. **Complete it yourself** (preferred) - finish truncated sections, add missing parts, fix errors
2. **Mark NEEDS_INPUT** (only if truly blocked) - explain what's missing and why you can't complete it

**DO NOT use FAILED status** - there are no retries.

## What to Check

For EIC tasks:
- ✓ Summary section exists and is complete
- ✓ ICT section has multiple ### subsections
- ✓ ICT does NOT end mid-sentence or with "..."
- ✓ ICT length matches original source (not significantly shorter)
- ✓ **Output files exist at specified locations** (CRITICAL)
- ✓ **Output property contains wiki links to created files** (CRITICAL)
- ✓ Wiki links are valid

For all tasks:
- ✓ All required outputs created
- ✓ **Output files physically exist on disk** (CRITICAL - check file existence)
- ✓ **Output property updated with wiki links** (CRITICAL - [[path/to/file]] format)
- ✓ Output files complete, not truncated
- ✓ Files in correct locations (not moved to "better" folders)

## What to Do

**If incomplete:** Finish the work yourself
- Continue truncated ICT sections from where they stopped
- Add missing subsections
- Fix formatting and links
- Fill in gaps
- **Ensure output files exist and are properly linked in output property**

**If output property missing/incorrect:**
- Read output files to find what was created
- Update task frontmatter with: `output: "[[path/to/file]]"`
- Use wiki link format with proper path from workspace root

**If output files missing:**
- If work product missing entirely → Mark NEEDS_INPUT
- If execution completed but files not found → Check file paths, update output property

**If blocked:** Mark NEEDS_INPUT
- Only if missing source files, unclear requirements, or fundamentally wrong approach
- Missing output files that should have been created
- Document specific issue in "## Evaluation Log"

## Final Step - REQUIRED

Update task status in frontmatter to:
- **COMPLETED** - work is done (you completed any missing parts)
- **NEEDS_INPUT** - you're blocked and need human help

Add notes to "## Evaluation Log" section (NOT "## Process Log") explaining what you did.
```

## Placeholders
- `{task_path}`: Absolute path to the task file
- `{task_type}`: Task type from frontmatter (e.g., EIC, Research, Analysis)
- `{priority}`: Task priority (P0, P1, P2, P3)
- `{instructions}`: Task instructions extracted from task file
- `{output_section}`: List of output file paths or "No output files specified"

## Agent Expectations
The evaluation agent should:
1. Read the task file to understand requirements
2. Access and review all output files
3. **Attempt to fix minor issues** (missing links, formatting, incomplete content)
4. Update output files and 'output' property as needed to meet standards
5. **Document work in "## Evaluation Log" section** - NOT in "## Process Log"
6. Only fail tasks that require substantial rework (wrong source, flawed approach, missing critical input)
7. **Update task status directly**: Set to "COMPLETED" if successful, "FAILED" if needs substantial rework
8. This direct status update is more robust than returning structured text responses

## Customization
To modify evaluation criteria or decision-making logic, edit this template. Changes apply immediately to new task evaluations.
