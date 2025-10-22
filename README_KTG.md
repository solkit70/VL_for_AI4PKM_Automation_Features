# Knowledge Task Generator (KTG) System

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [File Watchdog System](#file-watchdog-system)
- [Task Request Sources](#task-request-sources)
- [KTG Processing Workflow](#ktg-processing-workflow)
- [Task File Structure](#task-file-structure)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

## Overview

The Knowledge Task Generator (KTG) is an automated system that monitors your PKM workspace for various sources of work and automatically creates task requests. It integrates with multiple input sources including:

- 🏷️ Hashtag tags (`#AI`)
- 📄 Clipping files
- 🎙️ Transcription services (Limitless, Gobi)
- 📝 Action tags in markdown files
- And more...

The system follows a two-stage architecture:
1. **File Handlers** → Detect events and create task requests
2. **KTG Agent** → Processes task requests and creates/executes tasks

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    File Watchdog System                      │
│                                                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Hashtag   │  │  Clipping   │  │  Limitless  │         │
│  │   Handler   │  │   Handler   │  │   Handler   │   ...   │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
│         │                 │                 │                │
│         └─────────────────┼─────────────────┘                │
│                           ▼                                  │
│                 AI/Tasks/Requests/{Source}/                  │
│                   YYYY-MM-DD-{ms}.md                         │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Task Request File Handler                       │
│                                                               │
│  Triggers: AI/Tasks/Requests/*/*.md (on creation)           │
│  Action: Invokes KTG Agent                                   │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    KTG Agent                                 │
│                                                               │
│  1. VALIDATE - Check for duplicates and consistency         │
│  2. CATEGORIZE - Simple (execute now) vs Complex (defer)    │
│  3. CREATE   - Generate task file for ALL tasks             │
│  4. EXECUTE  - Run simple tasks immediately (COMPLETED)     │
│  5. CLEANUP  - Remove processed tags                         │
│                                                               │
│  Output: AI/Tasks/YYYY-MM-DD [Description].md               │
└─────────────────────────────────────────────────────────────┘
```

## File Watchdog System

The file watchdog continuously monitors the workspace for changes and triggers appropriate handlers based on file patterns.

### Handler Registration

Handlers are registered in order of specificity (most specific first):

```python
pattern_handlers=[
    ('AI/Tasks/Requests/*/*.md', TaskRequestFileHandler),  # Task requests
    ('Ingest/Gobi/*.md', GobiFileHandler),                 # Gobi transcripts
    ('Ingest/Limitless/*.md', LimitlessFileHandler),       # Limitless transcripts
    ('Ingest/Clippings/*.md', ClippingFileHandler),        # Clippings
    ('*.md', HashtagFileHandler),                          # Hashtag detection
    ('*.md', MarkdownFileHandler),                         # Generic markdown
]
```

### Excluded Patterns

Certain directories are excluded from monitoring to improve performance:

```python
excluded_patterns=[
    '.git',           # Git internals
    'ai4pkm_cli',     # CLI source code
    '_Settings_',     # Settings directory
    'AI/Tasks',       # Task files themselves
]
```

## Task Request Sources

### 1. Hashtag Handler (`#AI`)

**Trigger**: Any markdown file containing `#AI` hashtag

**Pattern Matching**:
- ✅ Matches: `#AI`, `tags: #AI`, `I need #AI help`
- ❌ Doesn't match: `#AIR`, `#AIDING`, `#AIRFLOW` (word boundaries enforced)

**Task Request Location**: `AI/Tasks/Requests/Hashtag/`

**Example Usage**:
```markdown
# My Note

I'm stuck on this problem. #AI please help analyze this.
```

**Special Handling for Task Files**:
When `#AI` appears in existing task files (`AI/Tasks/*.md`):
- **Does NOT create a new task file**
- Instead, KTG resolves the request within the same task file
- Adds response to the **Process Log** section
- Removes the `#AI` tag after addressing the request
- This keeps related work consolidated in one place

**Task Request Format**:
```markdown
---
generated: 2025-10-15 14:30:45
handler: HashtagFileHandler
task_type: Hashtag
target_file: path/to/note.md
---

# AI Task Request - 2025-10-15 14:30:45

File with #AI hashtag detected. Requesting task creation.

## Target File
`path/to/note.md`

## Instructions
Review the file content and determine the appropriate action:
- Create appropriate task(s) based on the context around #AI hashtag
- Remove or update the #AI hashtag after processing
```

**Features**:
- Duplicate prevention (tracks processed files)
- Works on both file creation and modification
- Automatic cleanup of old cache entries

### 2. Clipping Handler

**Trigger**: New files in `Ingest/Clippings/` (excluding files with "EIC" in filename)

**Purpose**: Automatically queue clippings for EIC (Enrich Ingested Content) processing

**Task Request Location**: `AI/Tasks/Requests/Clipping/`

**Task Request Format**:
```markdown
---
generated: 2025-10-15 14:30:45
handler: ClippingFileHandler
task_type: EIC
target_file: Ingest/Clippings/2025-10-15-article.md
---

# EIC Task Request - 2025-10-15 14:30:45

New clipping file detected. Requesting EIC (Enrich Ingested Content) processing.

## Target File
`Ingest/Clippings/2025-10-15-article.md`
```

**Features**:
- Only triggers on new file creation
- Skips files already processed (with "EIC" in name)
- Automatically queues for content enrichment

### 3. Limitless Handler

**Trigger**: Files in `Ingest/Limitless/` with new entries

**Pattern Recognition**: 
- Line format: `- {SpeakerName} (MM/DD/YY H:MM AM/PM): content`
- Example: `- You (10/14/25 2:30 PM): hey pkm, please analyze this`

**PKM Request Detection**: Case-insensitive `hey pkm` or `heypkm` patterns

**Task Request Location**: `AI/Tasks/Requests/Limitless/`

**Features**:
- Timestamp-based incremental processing
- Only processes new entries since last sync
- Detects task creation requests in transcripts
- Tracks speaker information

### 4. Gobi Handler

**Trigger**: Files in `Ingest/Gobi/` with new entries

**Pattern Recognition**:
- Line format: `YYYY-MM-DD HH:MM:SS {speaker_id}: content`
- Example: `2025-10-15 14:30:45 user_123: hey pkm, create a summary`

**PKM Request Detection**: Case-insensitive `hey pkm` or `heypkm` patterns

**Task Request Location**: `AI/Tasks/Requests/Gobi/`

**Features**:
- Timestamp-based incremental processing
- Only processes new entries since last sync
- Detects task creation requests in transcripts
- Tracks speaker IDs

### 5. Task Request Handler

**Trigger**: New files in `AI/Tasks/Requests/*/*.md`

**Purpose**: Automatically invokes KTG agent when task request files are created

**Special Behavior**:
- Only responds to file creation (not modification)
- Triggers the KTG agent with the request file
- This is the bridge between detection and processing

## KTG Processing Workflow

When the KTG agent is triggered, it follows this workflow:

### 1. VALIDATE

```
├─ Duplicate Check
│  └─ Scan AI/Tasks/YYYY-MM-DD* for similar tasks
│  └─ Compare by description, source, and timing
│
└─ Status Consistency
   └─ Verify proper statuses: TBD, COMPLETED, NEEDS_INPUT
   └─ Check due dates are future dates
   └─ Clean up outdated pending tasks
```

### 2. CATEGORIZE & ROUTE

```
├─ Determine Complexity
│  ├─ Simple Tasks (execute immediately)
│  │  ├─ File operations and lookups
│  │  ├─ Quick reference tasks
│  │  ├─ Journal updates
│  │  └─ Single-step operations
│  │
│  └─ Complex Tasks (defer to TaskProcessor)
│     ├─ EIC (Enrich Ingested Content)
│     ├─ Research and analysis
│     ├─ Writing and documentation
│     └─ Multi-step workflows
│
└─ Determine Priority
   ├─ P1: Content creation
   └─ P2: Workflow and maintenance
```

**Categorization Guide:**

*Simple Tasks* - Execute immediately, set status to COMPLETED/FAILED:
- ✅ Adding content to existing files (Journal, Topics)
- ✅ File lookups and searches
- ✅ Simple file operations (rename, move, copy)
- ✅ Quick data extraction or formatting
- ✅ Single-step operations with immediate results
- ✅ Operations that take <2 minutes

*Complex Tasks* - Create with status TBD for TaskProcessor:
- ❌ EIC (Enrich Ingested Content) - always complex
- ❌ Content requiring deep analysis or research
- ❌ Multi-step workflows or processes
- ❌ Tasks requiring multiple file modifications
- ❌ Tasks requiring external context or research
- ❌ Operations estimated to take >5 minutes

*When in doubt:* If the task might fail or require retries, make it complex.

### 3. CREATE TASK FILE (REQUIRED FOR ALL TASKS)

**CRITICAL:** ALL tasks must create task files, regardless of complexity.
Task files provide essential audit trails and execution tracking.

**EXCEPTIONS - Update existing task files instead:**
1. **#AI tags in task files**: Update the existing task file, don't create new task
2. **Task outcome updates**: When reporting results for existing tasks, update that task file directly
   - Examples: "update task X with results", "mark task Y as completed", "record outcome for task Z"

**Execution Strategy:**
- **Simple tasks**: Create file → Execute immediately → Set status to COMPLETED/FAILED
- **Complex tasks**: Create file with status TBD → Leave for TaskProcessor to handle

```
File: AI/Tasks/YYYY-MM-DD [Description].md

Structure:
├─ Properties (YAML frontmatter)
│  ├─ Priority: P1 (content) or P2 (workflow)
│  ├─ Status: TBD, IN_PROGRESS, PROCESSED, COMPLETED, FAILED, NEEDS_INPUT
│  ├─ Archived: false
│  ├─ Source: Link to original request
│  └─ generation_log: Link to KTG execution log
│
├─ ## Input
│  └─ Full context with blockquotes
│
├─ ## Context
│  └─ Time, speaker, type information
│
├─ ## Requirements
│  └─ Structured preferences and constraints
│
└─ ## Inferred
   ├─ Input specifications
   ├─ Output format
   ├─ Processing instructions
   └─ Budget/effort estimate
```

### 4. CLEANUP

- For markdown-sourced requests: Remove trigger tags (`#AI`, etc.)
- Update request file status
- Log completion

## Special Cases: Update vs Create

⚠️ **CRITICAL**: Not all requests should create new task files. Some should update existing tasks.

### When to UPDATE Existing Task Files

**1. #AI Tags in Task Files**
```
Location: AI/Tasks/*.md
Trigger: #AI tag found in an existing task file
Action: Update the existing task, don't create new one
Process:
  1. Read the task file to understand context
  2. Address the #AI request or question
  3. Add response to "Process Log" section
  4. Remove the #AI tag
Reason: Keeps related work consolidated, prevents task fragmentation
```

**2. Task Outcome/Result Updates**
```
Trigger: Request explicitly mentions updating existing task
Keywords: "update task", "mark task as", "record outcome", "add results to"
Action: Locate and update the existing task file
Process:
  1. Find the existing task file in AI/Tasks/
  2. Add outcome/result to "Process Log" or "Evaluation Log"
  3. Update status if appropriate (COMPLETED, NEEDS_INPUT, etc.)
  4. Update "output" property if deliverables provided
Examples:
  - "update task 2025-10-22 Research with findings"
  - "mark task X as completed with notes"
  - "record outcome for yesterday's analysis task"
Reason: Task updates should modify the task record, not create new tasks about updates
```

### When to CREATE New Task Files

**Always create new tasks for:**
- ✅ New work requests (not about existing tasks)
- ✅ New #AI tags in regular notes (outside AI/Tasks/)
- ✅ Any request that doesn't reference an existing task
- ✅ Follow-up work that's distinct from original task

**Decision Flow:**
```
Is this about an EXISTING task? 
├─ Yes, updating outcome/result → UPDATE existing task file
├─ Yes, #AI tag in task file → UPDATE existing task file
└─ No, new work request → CREATE new task file
```

### Time Scope Restrictions

⚠️ **CRITICAL**: KTG only processes sources from the **last 3 days** to prevent generating outdated tasks. This applies to all source types.

### Task Status Flow

⚠️ **CRITICAL**: Different flows for simple vs complex tasks

**Simple Tasks** (executed immediately by KTG):
```
TBD → [Execute] → COMPLETED (success) or FAILED (error)
```
- FAILED indicates an error occurred during immediate execution
- No retry loops - task remains FAILED for user review
- Examples: file not found, permission error, invalid input

**Complex Tasks** (processed through TaskProcessor/Evaluator):
```
TBD → IN_PROGRESS → PROCESSED → COMPLETED or NEEDS_INPUT
```
- No FAILED status in this flow
- Evaluator completes remaining work or marks NEEDS_INPUT
- One-time evaluation model (no retry loops)

**Design Philosophy:**
- Simple tasks fail fast with FAILED status (clear error indicator)
- Complex tasks use one-time evaluation model
- Evaluation is not a "review and retry" process
- Evaluator is responsible for **completing** unfinished work, not just flagging issues
- No retry loops in either flow

**Why This Design:**
- Prevents infinite retry loops (common failure mode)
- Clear distinction between immediate errors (FAILED) and blocked work (NEEDS_INPUT)
- Evaluator agents are capable enough to complete most incomplete work
- Forces evaluator to take ownership of completion
- Saves compute resources (no redundant re-execution)
- Clear ownership: Executor creates draft, Evaluator finalizes

**Evaluator Responsibilities:**
- Complete truncated ICT sections by continuing from where they cut off
- Add missing subsections or formatting
- Fix wiki links and minor errors
- Only escalate to NEEDS_INPUT when truly blocked (missing source files, unclear requirements)

**Preventing Double Evaluation:**
Tasks are marked with `evaluated: true` after first evaluation to prevent re-evaluation.

## Task File Structure

### Template (from `_Settings_/Templates/Task Template.md`)

```markdown
---
Priority: "P1"
Status: "TBD"
Archived: false
Source: "[[Source File]]"
created: YYYY-MM-DD
---

# [Task Description]

## Input

> Original request or context here
> Can span multiple lines

## Context

- **Time**: YYYY-MM-DD HH:MM:SS
- **Speaker**: Name or ID
- **Type**: Task type (EIC, Research, etc.)

## Requirements

- Specific requirement 1
- Specific requirement 2
- Constraints or preferences

## Inferred

### Input
- What needs to be processed

### Output
- Expected deliverable format
- Location for output

### Instructions
1. Step-by-step processing plan
2. Tools or methods to use
3. Quality criteria

### Budget
- Estimated time or effort
```

### Priority Levels

- **P1**: Content-focused tasks (writing, analysis, creation)
- **P2**: Workflow/maintenance tasks (organization, cleanup)

### Status Values

- **TBD**: To be done (default for new tasks)
- **COMPLETED**: Task finished
- **NEEDS_INPUT**: Waiting for user input or clarification

## Configuration

### Starting the Watchdog

The file watchdog runs as part of the CLI system:

```bash
# Start the continuous monitoring system (includes watchdog)
ai4pkm --cron
# or
ai4pkm -c

# The watchdog will automatically monitor and create task requests
```

### Handler Configuration

Handlers can be customized in `ai4pkm_cli/cli.py`:

```python
event_handler = FileWatchdogHandler(
    pattern_handlers=[
        # Add or modify handlers here
        ('*.md', CustomHandler),
    ],
    excluded_patterns=[
        # Add exclusions here
        'temp',
    ],
    logger=self.logger,
    workspace_path=os.getcwd()
)
```

### Custom Handler Development

To create a custom handler:

1. Inherit from `BaseFileHandler`
2. Implement the `process(file_path, event_type)` method
3. Use `_create_task_request()` or `_save_candidates_to_file()` for task creation
4. Register in the pattern_handlers list

Example:

```python
from ai4pkm_cli.watchdog.file_watchdog import BaseFileHandler

class CustomHandler(BaseFileHandler):
    def process(self, file_path: str, event_type: str) -> None:
        # Your detection logic here
        if self._should_create_task(file_path):
            self._create_task_request(file_path)
```

## Usage Examples

### Example 1: Quick Task via Hashtag

1. Open any note in your PKM
2. Add `#AI` where you need help
3. Save the file
4. Task request automatically created
5. KTG processes and creates task or executes immediately

### Example 2: Clipping Import

1. Save article to `Ingest/Clippings/2025-10-15-article.md`
2. ClippingHandler detects new file
3. EIC task request created automatically
4. KTG creates formal EIC task in `AI/Tasks/`

### Example 3: Voice Request via Limitless

1. In Limitless: "Hey PKM, analyze my last week's work patterns"
2. Transcript saved to `Ingest/Limitless/`
3. LimitlessHandler detects "hey pkm" pattern
4. Task request created with full context
5. KTG processes and creates analysis task

### Example 4: Checking Task Status

```bash
# View all tasks
ls AI/Tasks/

# View tasks by date
ls AI/Tasks/2025-10-*

# View task requests
ls AI/Tasks/Requests/*/
```

## Testing

### Running Handler Tests

Test individual handlers:

```bash
# Test hashtag handler
python ai4pkm_cli/tests/test_hashtag_handler.py

# Test other handlers
python ai4pkm_cli/tests/test_watchdog.py
```

### Manual Testing Workflow

1. **Start the system**:
   ```bash
   ai4pkm --cron
   ```

2. **Trigger an event** (e.g., create file with `#AI`)

3. **Check task request created**:
   ```bash
   ls AI/Tasks/Requests/Hashtag/
   ```

4. **Verify KTG processed**:
   ```bash
   # Check for new task file
   ls AI/Tasks/2025-*
   ```

5. **Review logs**:
   ```bash
   tail -f _Settings_/Logs/ai4pkm_*.log
   ```

### Test Coverage

All handlers include tests for:
- ✅ Pattern detection accuracy
- ✅ False positive filtering
- ✅ Task request file creation
- ✅ Duplicate prevention
- ✅ Timestamp tracking (for transcription handlers)

## Troubleshooting

### Task Requests Not Being Created

1. **Check watchdog is running**:
   ```bash
   # Look for "File Watchdog Monitoring started" message
   ```

2. **Verify file pattern matches**:
   - Hashtag: Must be exact `#AI` in markdown file
   - Clippings: Must be in `Ingest/Clippings/` directory
   - Limitless: Must be in `Ingest/Limitless/` directory

3. **Check excluded patterns**:
   - Files in `_Settings_/`, `.git`, `ai4pkm_cli` are excluded
   - Task files themselves are excluded to prevent loops

4. **Review logs**:
   ```bash
   tail -100 _Settings_/Logs/ai4pkm_*.log
   ```

### KTG Not Processing Requests

1. **Verify request file format**:
   - Must be in `AI/Tasks/Requests/{Source}/`
   - Must have `.md` extension
   - Must be a new file (creation event)

2. **Check KTG agent is running**:
   - Look for "Executing Knowledge Task Generator" in logs

3. **Review request file content**:
   - Should have YAML frontmatter with `task_type`, `target_file`

### Duplicate Tasks Being Created

1. **For Hashtag Handler**:
   - Check if file modification time changed
   - Handler tracks by `file_path:mtime` combination

2. **For Transcription Handlers**:
   - Verify timestamp tracking is working
   - Check `AI/Tasks/Requests/{Source}/` for latest timestamp

3. **For KTG**:
   - Review duplicate detection logic in KTG prompt
   - Check existing tasks in `AI/Tasks/` directory

### Performance Issues

1. **Too many file events**:
   - Add directories to `excluded_patterns`
   - Reduce number of monitored files

2. **Slow handler processing**:
   - Check handler logs for bottlenecks
   - Consider optimizing pattern matching

3. **High CPU usage**:
   - Review watchdog polling interval
   - Check for infinite loops in handlers

## Advanced Topics

### Timestamp Tracking

Transcription handlers (Limitless, Gobi) use filename-based timestamp tracking:

```python
# Last sync determined by most recent request file
last_sync = handler.get_last_sync_timestamp()

# Request files named: YYYY-MM-DD-{milliseconds}.md
# Milliseconds extracted from filename to determine last sync time
```

### Handler Priority

Handlers are checked in order. First match wins:

```python
# This order matters!
('AI/Tasks/Requests/*/*.md', TaskRequestFileHandler),  # Most specific
('Ingest/Gobi/*.md', GobiFileHandler),
('*.md', HashtagFileHandler),                          # More general
('*.md', MarkdownFileHandler),                         # Catch-all
```

### Task Execution Policy

⚠️ **CRITICAL**: All tasks create task files for audit trail

**Simple Tasks** (executed immediately by KTG):
- File lookups and operations
- Journal updates and additions
- Quick reference tasks
- Single-step operations
- Status: TBD → COMPLETED/FAILED (bypasses TaskProcessor)

**Complex Tasks** (deferred to TaskProcessor):
- EIC (Enrich Ingested Content) - never executed by KTG
- Research and analysis
- Multi-step workflows
- Content creation
- Status: TBD (picked up by TaskProcessor)

### Integration with Other Prompts

KTG works with other prompts in the system:

- **EIC** (Enrich Ingested Content): Process clippings
- **IWA** (Interactive Writing Assistant): TODO, TOWRITE tags
- **ARP** (Ad-hoc Research within PKM): TOSEARCH tags
- **PLL** (Process Life Logs): Limitless/Gobi transcripts

## Contributing

To add a new handler:

1. Create handler file in `ai4pkm_cli/watchdog/handlers/`
2. Inherit from `BaseFileHandler`
3. Implement `process()` method
4. Add to pattern_handlers in `cli.py`
5. Create tests in `ai4pkm_cli/tests/`
6. Update this README

## References

- **KTG Prompt**: `_Settings_/Prompts/Knowledge Task Generator (KTG).md`
- **Task Template**: `_Settings_/Templates/Task Template.md`
- **Base Handler**: `ai4pkm_cli/watchdog/file_watchdog.py`
- **Handler Examples**: `ai4pkm_cli/watchdog/handlers/`

---

**Last Updated**: 2025-10-15
**Version**: 1.0
**Maintainer**: AI4PKM Team

