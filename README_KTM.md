# AI4PKM Knowledge Task Management (KTM) Implementation Flow

This document provides detailed implementation flow documentation for the AI4PKM Knowledge Task Management (KTM) system, showing how KTG (Knowledge Task Generator) and KTP (Knowledge Task Processor) work together.

## Table of Contents
- [System Architecture](#system-architecture)
- [Entry Points](#entry-points)
- [Complete Flow Overview](#complete-flow-overview)
- [KTG Implementation Flow](#ktg-implementation-flow)
- [KTP Implementation Flow](#ktp-implementation-flow)
- [File Watchdog System](#file-watchdog-system)
- [Concurrency Control](#concurrency-control)
- [Status State Machine](#status-state-machine)
- [Configuration](#configuration)
- [Code References](#code-references)

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│              AI4PKM Knowledge Task Management (KTM)              │
│                                                                   │
│  ┌──────────────────┐                 ┌──────────────────┐     │
│  │       KTG        │                 │       KTP        │     │
│  │ Task Generator   │ ────────────▶   │ Task Processor   │     │
│  │                  │   Creates Tasks │                  │     │
│  │  Detects sources │                 │  Executes tasks  │     │
│  │  Creates tasks   │                 │  3-phase flow    │     │
│  └──────────────────┘                 └──────────────────┘     │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Key Components

1. **File Watchdog System** ([ai4pkm_cli/watchdog/file_watchdog.py](ai4pkm_cli/watchdog/file_watchdog.py))
   - Monitors file system changes
   - Routes events to appropriate handlers
   - Pattern-based handler registration

2. **Task Handlers** ([ai4pkm_cli/watchdog/handlers/](ai4pkm_cli/watchdog/handlers/))
   - Source detection handlers (Hashtag, Clipping, Limitless, Gobi)
   - Task request handler (triggers KTG)
   - Task processor handler (triggers KTP Phase 1 & 2)
   - Task evaluator handler (triggers KTP Phase 3)

3. **KTP Runner** ([ai4pkm_cli/commands/ktp_runner.py](ai4pkm_cli/commands/ktp_runner.py))
   - Implements 3-phase task processing
   - Routes tasks to agents
   - Manages task status transitions

4. **Task Semaphore** ([ai4pkm_cli/watchdog/task_semaphore.py](ai4pkm_cli/watchdog/task_semaphore.py))
   - Controls concurrent task operations
   - Shared across all handlers

## Entry Points

### 1. Task Management Mode
Started via CLI command:
```bash
ai4pkm -t
# or
ai4pkm --task-management
```

**Location**: [ai4pkm_cli/cli.py:307-399](ai4pkm_cli/cli.py#L307-L399) - `run_task_management()`

**What it does at startup**:
1. **Scans for all tasks that need processing** (multi-status detection):
   - **PROCESSED tasks**: Evaluates completed work waiting for review (Phase 3)
   - **UNDER_REVIEW tasks**: Checks for interrupted evaluations
   - **IN_PROGRESS tasks**: Checks for potentially stuck/interrupted executions
   - **TBD tasks**: Processes new work (Phase 1 & 2)
2. Sets up file watchdog with all handlers
3. Monitors for file changes continuously

**Why multi-status startup detection?**
- **PROCESSED**: Execution finished, waiting for evaluation to begin
- **UNDER_REVIEW**: Evaluation in progress but may have been interrupted
- Ensures completed work is evaluated even if system restarted
- Detects tasks stuck in various phases from crashes/interruptions
- Picks up where the system left off without data loss
- Watchdog handlers only trigger on file *changes*, not existing states

**Registered Handlers** (in order):
```python
('AI/Tasks/Requests/*/*.json', TaskRequestFileHandler),  # KTG trigger
('AI/Tasks/*.md', TaskProcessor),                        # KTP Phase 1 & 2
('AI/Tasks/*.md', TaskEvaluator),                        # KTP Phase 3
('Ingest/Gobi/*.md', GobiFileHandler),                   # Source detection
('Ingest/Limitless/*.md', LimitlessFileHandler),         # Source detection
('Ingest/Clippings/*.md', ClippingFileHandler),          # Source detection
('*.md', HashtagFileHandler),                            # Source detection
```

### 2. Manual KTP Execution
Can be triggered manually via:
```bash
ai4pkm --ktp                    # Process all TBD tasks
ai4pkm --ktp --status PROCESSED  # Evaluate PROCESSED tasks
ai4pkm --ktp --status UNDER_REVIEW  # Retry UNDER_REVIEW tasks
ai4pkm --ktp --task "2025-10-15 Task Name.md"  # Process specific task
```

### 3. Startup Task Detection Sequence

When task management mode starts, it performs a comprehensive scan:

```
┌─────────────────────────────────────────────────────────────┐
│              STARTUP TASK DETECTION SEQUENCE                 │
└─────────────────────────────────────────────────────────────┘

1. PROCESSED Tasks (Priority: Evaluate completed work first)
   ├─ Scans: AI/Tasks/*.md with status=PROCESSED
   ├─ Action: Runs Phase 3 evaluation (sets UNDER_REVIEW → evaluates)
   └─ Result: Tasks move to COMPLETED or back to TBD with feedback

2. UNDER_REVIEW Tasks (Priority: Detect interrupted evaluations)
   ├─ Scans: AI/Tasks/*.md with status=UNDER_REVIEW
   ├─ Action: Logs warnings about interrupted evaluations
   └─ Result: User notified; evaluation may be retried

3. IN_PROGRESS Tasks (Priority: Detect interrupted executions)
   ├─ Scans: AI/Tasks/*.md with status=IN_PROGRESS
   ├─ Action: Logs warnings about potentially stuck tasks
   └─ Result: User notified; tasks will retry on file modification

4. TBD Tasks (Priority: Start new work)
   ├─ Scans: AI/Tasks/*.md with status=TBD
   ├─ Action: Runs Phase 1 (task routing) and Phase 2 (execution)
   └─ Result: Tasks move to IN_PROGRESS then PROCESSED

After startup detection completes:
├─ File watchdog monitoring begins
└─ System processes file changes in real-time
```

**Implementation**: [ai4pkm_cli/cli.py:324-351](ai4pkm_cli/cli.py#L324-L351)

## Complete Flow Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        DETECTION SOURCES                             │
├─────────────────────────────────────────────────────────────────────┤
│  #AI Hashtag  │  Clippings  │  Limitless  │  Gobi  │  Other...     │
└──────┬────────┴──────┬──────┴──────┬──────┴───┬────┴───────────────┘
       │               │              │          │
       │ HashtagFile   │ ClippingFile │ Limitless│ GobiFile
       │ Handler       │ Handler      │ Handler  │ Handler
       │               │              │          │
       ▼               ▼              ▼          ▼
┌─────────────────────────────────────────────────────────────────────┐
│              CREATE TASK REQUEST (JSON)                              │
│         AI/Tasks/Requests/{Source}/YYYY-MM-DD-{ms}.json             │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               │ File creation detected
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│         TaskRequestFileHandler (Watchdog)                            │
│         • Acquires semaphore slot                                    │
│         • Triggers KTG agent                                         │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    KTG AGENT EXECUTION                               │
│  • Reads request file                                                │
│  • Validates for duplicates                                          │
│  • Determines if simple (execute) or complex (create task)          │
│  • For complex: Creates task file in AI/Tasks/                      │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               │ Task file created with Status: TBD
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│         TaskProcessor (Watchdog)                                     │
│         • Detects TBD status                                         │
│         • Acquires semaphore slot                                    │
│         • Triggers KTP Phase 1 & 2                                   │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│              KTP PHASE 1: TASK ROUTING                               │
│         TBD → IN_PROGRESS                                            │
│  • Determine agent from processing_agent config                      │
│  • Update task status                                                │
│  • Proceed to Phase 2                                                │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│         KTP PHASE 2: EXECUTION & MONITORING                          │
│         IN_PROGRESS → PROCESSED                                      │
│  • Create agent instance (from processing_agent config)              │
│  • Build execution prompt                                            │
│  • Run task with agent                                               │
│  • Agent updates task file with:                                     │
│    - Process log entries                                             │
│    - Output property with wiki links                                 │
│    - Status: PROCESSED                                               │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               │ Status changed to PROCESSED
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│         TaskEvaluator (Watchdog)                                     │
│         • Detects PROCESSED status                                   │
│         • Acquires semaphore slot                                    │
│         • Triggers KTP Phase 3                                       │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│         KTP PHASE 3: RESULTS EVALUATION                              │
│         PROCESSED → UNDER_REVIEW → COMPLETED or FAILED               │
│  • Set status to UNDER_REVIEW                                        │
│  • AI-powered evaluation (uses evaluation_agent):                    │
│    - Are output files specified?                                     │
│    - Do output files exist and are accessible?                       │
│    - Does output address instructions?                               │
│    - Is output complete and well-structured?                         │
│    - Any errors or omissions?                                        │
│  • Decision:                                                         │
│    ✓ APPROVED → Status: COMPLETED                                    │
│    ✗ NEEDS_REWORK → Status: FAILED (with feedback)                  │
└─────────────────────────────────────────────────────────────────────┘
```

## KTG Implementation Flow

### Step 1: Source Detection

**Example: Hashtag Handler** ([ai4pkm_cli/watchdog/handlers/hashtag_file_handler.py](ai4pkm_cli/watchdog/handlers/hashtag_file_handler.py))

```python
class HashtagFileHandler(BaseFileHandler):
    def process(self, file_path: str, event_type: str):
        # Check for #AI hashtag
        if self._contains_ai_hashtag(file_path):
            # Create task request
            self._create_task_request(file_path)
```

**Detection Logic**:
- Pattern: `(?:^|\s|-)#AI(?:\s|$|,)`
- Word boundary matching (avoids #AIR, #AIDING)
- Tracks processed files to avoid duplicates

### Step 2: Task Request Creation

**Output**: `AI/Tasks/Requests/{Source}/YYYY-MM-DD-{milliseconds}.json`

**Request Format**:
```json
{
  "generated": "2025-10-15 14:30:45",
  "handler": "HashtagFileHandler",
  "task_type": "Hashtag",
  "target_file": "path/to/file.md",
  "description": "File with #AI hashtag detected. Requesting task creation.",
  "instructions": [
    "Review the file content and determine the appropriate action:",
    "- Create appropriate task(s) based on the context around #AI hashtag",
    "- Remove or update the #AI hashtag after processing"
  ]
}
```

### Step 3: TaskRequestFileHandler Trigger

**Location**: [ai4pkm_cli/watchdog/handlers/task_request_file_handler.py](ai4pkm_cli/watchdog/handlers/task_request_file_handler.py)

```python
class TaskRequestFileHandler(BaseFileHandler):
    def process(self, file_path: str, event_type: str):
        # Only process newly created files
        if event_type != 'created':
            return

        # Acquire semaphore (blocks if at max concurrent limit)
        with self.semaphore:
            self._execute_ktg(file_path)
```

**Key Features**:
- Only reacts to file **creation** (not modification)
- Uses shared semaphore for concurrency control
- Simple prompt: "Run Knowledge Task Generator given the task generation request file in {file_path}"

### Step 4: KTG Agent Execution

The KTG agent (defined in `_Settings_/Prompts/Knowledge Task Generator (KTG).md`) performs:

1. **VALIDATE**
   - Check for duplicate tasks
   - Verify status consistency
   - Clean up outdated tasks

2. **PROCESS**
   - Categorize as simple or complex
   - Simple tasks: Execute immediately
   - Complex tasks: Create task file

3. **CREATE TASK** (if complex)
   - Use template from `_Settings_/Templates/Task Template.md`
   - Set appropriate priority (P1 or P2)
   - Set status: TBD
   - Include source link

4. **CLEANUP**
   - Remove trigger tags from source
   - Update request file status

## KTP Implementation Flow

### Phase 1: Task Routing (TBD → IN_PROGRESS)

**Location**: [ai4pkm_cli/commands/ktp_runner.py:202-224](ai4pkm_cli/commands/ktp_runner.py#L202-L224)

```python
def _phase1_route_task(self, task_file: str, task_data: Dict[str, Any]):
    # Determine agent based on task type
    task_type = task_data.get('task_type', 'Unknown')
    agent_name = self.processing_agent.get(task_type,
                                           self.processing_agent.get('default', 'claude_code'))

    # Update task status to IN_PROGRESS
    self._update_task_status(task_file, 'IN_PROGRESS', worker=agent_name)

    # Proceed to Phase 2
    self._phase2_execute_task(task_file, task_data)
```

**Processing Agent Configuration** (from `ai4pkm_cli.json`):
```json
{
  "task_management": {
    "processing_agent": {
      "default": "claude_code",
      "EIC": "claude_code",
      "Research": "gemini_cli",
      "Analysis": "gemini_cli"
    }
  }
}
```

### Phase 2: Execution & Monitoring (IN_PROGRESS → PROCESSED)

**Location**: [ai4pkm_cli/commands/ktp_runner.py:226-287](ai4pkm_cli/commands/ktp_runner.py#L226-L287)

```python
def _phase2_execute_task(self, task_file: str, task_data: Dict[str, Any]):
    # Get agent
    worker = task_data.get('worker', self.processing_agent.get('default', 'claude_code'))
    agent = AgentFactory.create_agent_by_name(worker, self.logger, self.config)

    # Build prompt for agent
    prompt = f"Process the knowledge task defined in the file: {task_path}\n\n"
    prompt += "Follow the instructions in the task file and update the task file with:\n"
    prompt += "- Process Log entries documenting your work\n"
    prompt += "- Output property with wiki links to created files\n"
    prompt += "- Status updated to PROCESSED when complete\n"

    # Execute the task
    result = agent.run_prompt(inline_prompt=prompt)

    # Check if agent updated status to UNDER_REVIEW
    # If not, update manually
```

**Expected Task Updates by Agent**:
1. Add process log entries in task file
2. Update `output` property with wiki links: `[[File/Path]]`
3. Update status to `PROCESSED` (waiting for evaluation)

**Error Handling**:
- Tracks retry count in task frontmatter
- Max retries configurable (default: 3)
- On max retries exceeded: Status → FAILED

### Phase 3: Results Evaluation (PROCESSED → UNDER_REVIEW → COMPLETED/FAILED)

**Location**: [ai4pkm_cli/commands/ktp_runner.py:289-333](ai4pkm_cli/commands/ktp_runner.py#L289-L333)

**Agent**: Uses `config.get_evaluation_agent()` (default: `claude_code`)
- Configurable via `task_management.evaluation_agent` in `ai4pkm_cli.json`
- Can be different from processing agents for independent review

```python
def _phase3_evaluate_task(self, task_file: str, task_data: Dict[str, Any]):
    # 1. Read task content
    task_content = self._read_file_content(task_path)

    # 2. AI-powered evaluation (includes output validation)
    evaluation_result = self._evaluate_with_ai(task_file, task_data,
                                                current_data, task_content)

    # 3. Decision
    if evaluation_result['approved']:
        self._update_task_status(task_file, 'COMPLETED', worker=worker)
    else:
        self._fail_task(task_file, evaluation_result['reason'],
                        evaluation_result['feedback'])
```

**AI Evaluation Prompt**:
```
Review this task and its output to determine if it should be marked COMPLETED or FAILED.

Task File: /path/to/AI/Tasks/2025-10-16 Task.md
Task Type: EIC
Priority: P2

## Original Instructions
[Task instructions extracted from task file]

## Output Files
The following output files were created:
- /path/to/output1.md
- /path/to/output2.md

Please review these files to evaluate if the task was completed successfully.

## Evaluation Criteria
1. Are output files specified in the 'output' property?
2. Do the output files exist and are they accessible?
3. Does the output address the task instructions?
4. Is the output complete and well-structured?
5. Are there any obvious errors or omissions?

Respond with:
- APPROVED if the task is complete and meets all requirements
- NEEDS_REWORK if the task has issues (missing outputs, incorrect content, etc.)

Format your response as:
DECISION: [APPROVED or NEEDS_REWORK]
REASON: [brief explanation]
FEEDBACK: [specific improvements needed if NEEDS_REWORK]
```

**Key Features**:
- **File-based evaluation**: Agent receives file paths and reads them directly (no content truncation)
- **AI-driven validation**: Agent validates output existence and accessibility by accessing files
- **Comprehensive review**: Checks both technical requirements (files exist) and quality (content meets instructions)
- **Failure handling**: Failed reviews result in FAILED status with detailed feedback
- **Thread-safe logging**: Runs in dedicated thread named `KTP-eval-{filename}` with automatic thread name in logs

## File Watchdog System

### Handler Registration

**Location**: [ai4pkm_cli/cli.py:342-358](ai4pkm_cli/cli.py#L342-L358)

```python
event_handler = FileWatchdogHandler(
    pattern_handlers=[
        ('AI/Tasks/Requests/*/*.json', TaskRequestFileHandler),
        ('AI/Tasks/*.md', TaskProcessor),
        ('AI/Tasks/*.md', TaskEvaluator),
        ('Ingest/Gobi/*.md', GobiFileHandler),
        ('Ingest/Limitless/*.md', LimitlessFileHandler),
        ('Ingest/Clippings/*.md', ClippingFileHandler),
        ('*.md', HashtagFileHandler),
    ],
    excluded_patterns=[
        '.git',
        'ai4pkm_cli',
    ],
    logger=self.logger,
    workspace_path=os.getcwd()
)
```

### Pattern Matching Logic

**Location**: [ai4pkm_cli/watchdog/file_watchdog.py:170-196](ai4pkm_cli/watchdog/file_watchdog.py#L170-L196)

1. Converts absolute paths to relative paths
2. Uses `fnmatch` for glob pattern matching
3. Returns **all** matching handlers (multiple handlers can process same file)

**Important**:
- Same file can trigger multiple handlers
- `AI/Tasks/*.md` matches both TaskProcessor and TaskEvaluator
- Each handler checks status to determine if it should process

### Event Processing

**Location**: [ai4pkm_cli/watchdog/file_watchdog.py:198-223](ai4pkm_cli/watchdog/file_watchdog.py#L198-L223)

```python
def _process_with_handler(self, event, event_type: str):
    if event.is_directory:
        return

    # Check if file is excluded
    if self._is_excluded(file_path):
        return

    # Find all matching handlers
    handlers = self._find_matching_handlers(file_path)

    # Process with all matching handlers
    for handler in handlers:
        handler.process(file_path, event_type)
```

## Concurrency Control

### Task Semaphore

**Location**: [ai4pkm_cli/watchdog/task_semaphore.py](ai4pkm_cli/watchdog/task_semaphore.py)

**Purpose**: Limit concurrent task operations (generation, processing, evaluation)

**Implementation**:
```python
# Global singleton semaphore
_task_semaphore = None

def get_task_semaphore(config, logger):
    global _task_semaphore

    with _semaphore_lock:
        if _task_semaphore is None:
            max_concurrent = config.get_max_concurrent_tasks()
            _task_semaphore = threading.Semaphore(max_concurrent)

    return _task_semaphore
```

**Usage in Handlers**:
```python
# Acquire semaphore (blocks if at max concurrent limit)
with self.semaphore:
    # Protected operation
    self._execute_ktg(file_path)
```

**Configuration** (in `ai4pkm_cli.json`):
```json
{
  "max_concurrent_tasks": 2
}
```

### Threading Model

**Processing Agent Threading** ([ai4pkm_cli/watchdog/handlers/task_processor.py:55-61](ai4pkm_cli/watchdog/handlers/task_processor.py#L55-L61)):

```python
def process(self, file_path: str, event_type: str):
    # Spawn background thread immediately
    thread = threading.Thread(
        target=self._process_async,
        args=(file_path,),
        daemon=True,
        name=f"KTP-exec-{os.path.basename(file_path)}"
    )
    thread.start()
```

**Evaluation Agent Threading** ([ai4pkm_cli/watchdog/handlers/task_evaluator.py:55-61](ai4pkm_cli/watchdog/handlers/task_evaluator.py#L55-L61)):

```python
def process(self, file_path: str, event_type: str):
    # Spawn background thread immediately
    thread = threading.Thread(
        target=self._process_async,
        args=(file_path,),
        daemon=True,
        name=f"KTP-eval-{os.path.basename(file_path)}"
    )
    thread.start()
```

**Logger Thread Support** ([ai4pkm_cli/logger.py:70-73](ai4pkm_cli/logger.py#L70-L73)):

```python
# Get current thread name
thread_name = threading.current_thread().name
# Always add thread prefix for visibility
thread_prefix = f"[{thread_name}] "
```

Log format: `[timestamp] [thread-name] LEVEL: message`
- Processing: `[KTP-exec-claude-2025-10-16 Task.md] INFO: Executing task...`
- Evaluation: `[KTP-eval-claude-2025-10-16 Task.md] INFO: Running AI evaluation...`
- With Gemini: `[KTP-exec-gemini-2025-10-16 Research.md] INFO: Executing task...`

Thread name format: `KTP-{phase}-{agent}-{filename}`
- phase: `exec` (processing) or `eval` (evaluation)
- agent: `claude`, `gemini`, or `codex`
- filename: Task filename
```

**Startup Threading** ([ai4pkm_cli/commands/ktp_runner.py:182-216](ai4pkm_cli/commands/ktp_runner.py#L182-L216)):

When tasks are processed during startup (via `execute_command("ktp", {"status": "PROCESSED"})`), the KTPRunner also spawns dedicated threads:

```python
def _spawn_evaluation_thread(self, task_file: str) -> threading.Thread:
    """Spawn a thread for task evaluation."""
    # Get evaluation agent name from config
    agent_name = self.config.get_evaluation_agent()
    agent_short = agent_name.replace('_cli', '').replace('_code', '')  # claude, gemini, codex

    thread = threading.Thread(
        target=self.evaluate_task,
        args=(task_file,),
        daemon=True,
        name=f"KTP-eval-{agent_short}-{task_file}"
    )
    thread.start()
    return thread
```

**Why Threading?**
- Watchdog observer must not be blocked
- Task execution can be long-running
- Multiple tasks can be processed concurrently (up to semaphore limit)
- Consistent thread naming across startup and watchdog operations
- All operations (processing and evaluation) run in named threads for traceability

**Thread Comparison**:

| Aspect | Processing Agent | Evaluation Agent |
|--------|------------------|------------------|
| **Thread Name** | `KTP-exec-{agent}-{filename}` | `KTP-eval-{agent}-{filename}` |
| **Handler** | TaskProcessor | TaskEvaluator |
| **Trigger Status** | TBD | PROCESSED |
| **KTP Phases** | Phase 1 & 2 | Phase 3 |
| **Agent Config** | `processing_agent` mapping | `evaluation_agent` setting |
| **Agent in Thread Name** | Determined from task type | From `evaluation_agent` config |
| **Log Example** | `[KTP-exec-claude-...] INFO: Executing task...` | `[KTP-eval-claude-...] INFO: Running AI evaluation...` |
| **Location** | [task_processor.py](ai4pkm_cli/watchdog/handlers/task_processor.py) | [task_evaluator.py](ai4pkm_cli/watchdog/handlers/task_evaluator.py) |

## Status State Machine

```
                                  ┌─────────────┐
                                  │     TBD     │
                                  │  (To Do)    │
                                  └──────┬──────┘
                                         │
                            TaskProcessor detects TBD
                                         │
                                         ▼
                  ┌──────────────────────────────────────┐
                  │          Phase 1: Routing            │
                  │     TBD → IN_PROGRESS                │
                  │  • Determine agent                    │
                  │  • Update status                      │
                  └──────────────┬───────────────────────┘
                                 │
                                 ▼
                  ┌─────────────────────────┐
                  │      IN_PROGRESS        │
                  │  (Agent Working)        │
                  └──────────┬──────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
   ┌────────┐        ┌──────────────┐      ┌─────────┐
   │ FAILED │◄───────┤  Phase 2:    │      │ Timeout │
   │        │ Max    │  Execution   │      │ Retry   │
   └────────┘ Retry  └──────┬───────┘      └─────────┘
                             │
                    Task completed,
                    status updated
                             │
                             ▼
                  ┌─────────────────────────┐
                  │      PROCESSED          │
                  │ (Awaiting Evaluation)   │
                  └──────────┬──────────────┘
                             │
                 TaskEvaluator detects PROCESSED
                             │
                             ▼
                  ┌──────────────────────────────────────┐
                  │       Phase 3: Evaluation            │
                  │  • Set status: UNDER_REVIEW          │
                  │  • Validate outputs                   │
                  │  • AI evaluation                      │
                  │  • Decision                           │
                  └──────────┬───────────────────────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
     ┌────────────┐   ┌──────────┐   ┌──────────┐
     │   FAILED   │   │COMPLETED │   │NEEDS_INPUT│
     │ (Failed)   │   │          │   │          │
     │+ Feedback  │   │          │   │          │
     └────────────┘   └──────────┘   └──────────┘
```

### Status Values

**TBD** (To Be Done)
- Initial status for new tasks
- Also used for tasks sent back for rework
- Triggers TaskProcessor

**IN_PROGRESS**
- Task is being executed by an agent
- Set by Phase 1 (Routing)
- Updated to PROCESSED by agent or Phase 2

**PROCESSED**
- Task execution completed, waiting for evaluation to begin
- Set by agent or Phase 2
- Passive state (no active work happening)
- Triggers TaskEvaluator

**UNDER_REVIEW**
- Task is actively being evaluated (Phase 3 in progress)
- Set by Phase 3 when evaluation starts
- Active state (evaluation happening now)
- May be interrupted and need retry

**COMPLETED**
- Task successfully completed
- Set by Phase 3 after approval
- Terminal state

**FAILED**
- Task failed after max execution retries or failed review
- Set by Phase 2 on max execution retries or by Phase 3 on review failure
- Terminal state

**NEEDS_INPUT**
- Task requires user clarification
- Can be set manually
- Does not trigger automatic processing

## Configuration

### Main Configuration File: `ai4pkm_cli.json`

```json
{
  "default-agent": "claude_code",

  "task_management": {
    "max_concurrent": 5,
    "processing_agent": {
      "EIC": "claude_code",
      "Research": "gemini_cli",
      "Analysis": "gemini_cli",
      "Writing": "claude_code",
      "default": "claude_code"
    },
    "evaluation_agent": "claude_code",
    "timeout_minutes": 30,
    "max_retries": 2
  },

  "agents-config": {
    "claude_code": {
      "permission_mode": "bypassPermissions"
    },
    "gemini_cli": {
      "command": "gemini"
    }
  }
}
```

### Configuration Methods

**Location**: [ai4pkm_cli/config.py](ai4pkm_cli/config.py)

**KTP-specific getters**:
```python
config.get_ktp_routing()           # Task type → agent mapping (Phase 1 & 2)
config.get_evaluation_agent()      # Agent used for Phase 3 evaluation
config.get_ktp_timeout()           # Timeout in minutes
config.get_ktp_max_retries()       # Max retry attempts
config.get_max_concurrent_tasks()  # Semaphore limit
```

**Key Configuration Options**:
- **processing_agent**: Maps task types to agents for execution (Phase 1 & 2)
  - Example: `"EIC": "claude_code"` routes EIC tasks to Claude Code
  - `"default"` catches all unmapped task types
- **evaluation_agent**: Agent used for Phase 3 evaluation (default: `"claude_code"`)
  - This agent reviews task outputs and decides COMPLETED or FAILED
  - Can be different from processing agents to provide independent review

## Code References

### Core Components

| Component | File Path | Key Methods |
|-----------|-----------|-------------|
| **CLI Entry** | [ai4pkm_cli/cli.py](ai4pkm_cli/cli.py) | `run_task_management()` (line 307) |
| **KTP Runner** | [ai4pkm_cli/commands/ktp_runner.py](ai4pkm_cli/commands/ktp_runner.py) | `run_tasks()`, `_phase1_route_task()`, `_phase2_execute_task()`, `_phase3_evaluate_task()` |
| **File Watchdog** | [ai4pkm_cli/watchdog/file_watchdog.py](ai4pkm_cli/watchdog/file_watchdog.py) | `FileWatchdogHandler`, `BaseFileHandler` |
| **Task Semaphore** | [ai4pkm_cli/watchdog/task_semaphore.py](ai4pkm_cli/watchdog/task_semaphore.py) | `get_task_semaphore()` |

### Handler Implementations

| Handler | File Path | Purpose |
|---------|-----------|---------|
| **TaskRequestFileHandler** | [ai4pkm_cli/watchdog/handlers/task_request_file_handler.py](ai4pkm_cli/watchdog/handlers/task_request_file_handler.py) | Triggers KTG agent |
| **TaskProcessor** | [ai4pkm_cli/watchdog/handlers/task_processor.py](ai4pkm_cli/watchdog/handlers/task_processor.py) | Triggers KTP Phase 1 & 2 |
| **TaskEvaluator** | [ai4pkm_cli/watchdog/handlers/task_evaluator.py](ai4pkm_cli/watchdog/handlers/task_evaluator.py) | Triggers KTP Phase 3 |
| **HashtagFileHandler** | [ai4pkm_cli/watchdog/handlers/hashtag_file_handler.py](ai4pkm_cli/watchdog/handlers/hashtag_file_handler.py) | Detects #AI hashtag |
| **ClippingFileHandler** | [ai4pkm_cli/watchdog/handlers/clipping_file_handler.py](ai4pkm_cli/watchdog/handlers/clipping_file_handler.py) | Detects new clippings |
| **LimitlessFileHandler** | [ai4pkm_cli/watchdog/handlers/limitless_file_handler.py](ai4pkm_cli/watchdog/handlers/limitless_file_handler.py) | Detects "hey pkm" in Limitless |
| **GobiFileHandler** | [ai4pkm_cli/watchdog/handlers/gobi_file_handler.py](ai4pkm_cli/watchdog/handlers/gobi_file_handler.py) | Detects "hey pkm" in Gobi |

### Support Scripts

| Script | File Path | Purpose |
|--------|-----------|---------|
| **Task Status Manager** | [ai4pkm_cli/scripts/task_status.py](ai4pkm_cli/scripts/task_status.py) | Query and update task status |

## Summary

The AI4PKM Knowledge Task Management (KTM) system implements a fully automated workflow:

1. **Startup Detection**: Multi-status scan ensures no task is left behind
   - PROCESSED tasks are evaluated (passive, waiting for evaluation)
   - UNDER_REVIEW tasks are checked (active evaluation may be interrupted)
   - IN_PROGRESS tasks are detected and logged
   - TBD tasks are processed
2. **Detection**: Multiple sources (hashtags, files, transcripts) are monitored
3. **Generation (KTG)**: Task requests trigger automated task creation
4. **Processing (KTP)**: Tasks are routed, executed, and evaluated through a 3-phase pipeline
5. **Concurrency**: Semaphore controls parallel operations
6. **Automation**: File watchdog triggers appropriate handlers based on file patterns and task status

The system is designed to be:
- **Resilient**: Comprehensive startup detection prevents task loss on restarts
- **Extensible**: Easy to add new source handlers
- **Robust**: Retry logic, error handling, and duplicate prevention
- **Concurrent**: Multiple tasks can be processed in parallel
- **Automated**: Minimal manual intervention required

---

**Related Documentation**:
- [README_KTG.md](README_KTG.md) - Knowledge Task Generator (KTG) specification
- [README_KTP.md](README_KTP.md) - Knowledge Task Processor (KTP) specification

**Last Updated**: 2025-10-16
**Version**: 1.0
