---
title: Orchestrator Design for Multi-Agent AI4PKM System
created: 2025-10-25
updated: 2025-11-01
tags:
  - architecture
  - orchestrator
  - multi-agent
  - design
status: IMPLEMENTED
author:
  - "[[Claude]]"
related:
  - "[[2025-10-24 KTM to Multi-Agent Migration Plan - Claude Code]]"
  - "[[2025-10-24 Next Steps in AI4PKM]]"
  - "[[2025-10-30 New Architecture for Agentic AI]]"
---

> **📋 Document Status**: This is the **original design document** from October 2025. The orchestrator has been **successfully implemented** and is now in production use.
>
> **⚠️ Important Changes**: The implementation uses a **nodes-based configuration** in `orchestrator.yaml` instead of individual agent files in `_Settings_/Agents/`. Agent prompts are now stored in `_Settings_/Prompts/`.
>
> **📖 Current Documentation**: For usage instructions and current configuration format, see:
> - **User Guide**: [docs/orchestrator.md](../orchestrator.md)
> - **Architecture Overview**: [Blog Post](https://jykim.github.io/AI4PKM/blog/2025/10/30/new-architecture-for-agentic-ai.html)

---

# Orchestrator Design for Multi-Agent AI4PKM System

## Executive Summary
This document provides the **original design** for the orchestrator that coordinates multiple AI agents in the AI4PKM system. The orchestrator manages any number of agents through configuration rather than code.

**Implementation Status**: ✅ Complete (as of October 2025)

**Key Innovations**:
- Agent definitions as Markdown files with flat YAML frontmatter (Obsidian compatible)
- File system as the state database (no separate DB needed)
- Automatic agent triggering based on file system events
- Agent chaining through input/output path matching
- Skills as reusable, composable functions

---
# Multi-Agent Ecosystem

## Current Agents (7 total)
**Note**: These are example agents for illustration. Any agent can be defined using templates.

**Ingestion Agents (5)**: EIC, PLL, PPP, GES, GDR
**Publishing Agents (1)**: CTP
**Research Agents (1)**: ARP

## Data Flow Patterns
%% remove this section %%
### Pattern 1: Sequential Processing Chain
```
External Source → Ingestion Agent → Processing Agent → Publication Agent
Example: Web Article → EIC → GDR → CTP
```

### Pattern 2: Aggregation Pattern
```
Multiple Sources → Single Aggregation Agent
Example: EIC + PLL + GES → GDR (daily roundup)
```

### Pattern 3: Parallel Processing
```
Single Source → Multiple Agents (different purposes)
Example: Limitless → [PLL (lifelog) + GES (events)]
```

### Pattern 4: Ad-hoc Research
```
User Query + Vault Content → Research Agent → Output
Example: Question → ARP → Research Report
```

## Ecosystem Diagram
*Example for illustration. Actual agent ecosystem will vary by user.*

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        MULTI-AGENT ECOSYSTEM                                     │
│                     (Input/Output Connection Map)                                │
└─────────────────────────────────────────────────────────────────────────────────┘

EXTERNAL SOURCES                 INGESTION LAYER              PROCESSING LAYER       OUTPUT LAYER
═══════════════                 ═══════════════              ════════════════       ════════════

┌─────────────┐
│   Web       │
│  Clippings  │
└──────┬──────┘
       │
       │ saved to
       ▼
  Ingest/Clipping/
  {title}.md
       │
       │ new_file event
       ▼
  ┌─────────┐           AI/Clipping/              AI/Roundup/            AI/Sharable/
  │   EIC   │────────▶  {title} - EIC.md  ────┐   YYYY-MM-DD - GDR.md     Thread*.md
  │  Agent  │           (processed)           │        │                      ▲
  └─────────┘                                  │        │                      │
                                              │        │                      │
┌─────────────┐                                  │        │                      │
│  Limitless  │                                  │        │ aggregates           │
│Voice Capture│                                  ├───────▶│                      │
└──────┬──────┘                                  │        │                      │
       │                                         │        ▼                      │
       │ daily capture                           │   ┌─────────┐                │
       ▼                                         │   │   CTP   │                │
  Ingest/Limitless/                              │   │  Agent  │────────────────┘
  YYYY-MM-DD.md                                  │   └─────────┘
       │                                         │   (publishes)
       │                                         │
       ├──────────────┐                          │
       │              │                          │
       │ daily_file   │ updated_file            │
       ▼              ▼                          │
  ┌─────────┐   ┌─────────┐                    │
  │   PLL   │   │   GES   │                    │
  │  Agent  │   │  Agent  │◄─── MCP#gcal       │
  └────┬────┘   └────┬────┘                    │
       │             │                          │
       │             │                          │
       ▼             ▼                          │
  AI/Lifelog/   AI/Events/                     │
  YYYY-MM-DD    YYYY-MM-DD                     │
  Lifelog*.md   Summary*.md ────────────────────┘
       │
       │ integrates
       ▲
       │
  ┌────┴─────┐
  │Ingest/   │
  │Photolog/ │
  │YYYYMMDD  │
  │Photolog  │
  │.md       │
  └────▲─────┘
       │
       │
  ┌────┴─────┐
  │   PPP    │
  │  Agent   │
  └──────────┘
       ▲
       │
       │ daily_files
  Ingest/Photolog/
  Processed/
  {images + metadata}


RESEARCH FLOW (Ad-hoc)
══════════════════════

  User Question
       │
       ▼
  ┌─────────┐
  │   ARP   │◄──── Full Vault Access
  │  Agent  │      (Topics, Roundup,
  └────┬────┘       Journal, etc.)
       │
       │ synthesize
       ▼
  AI/Research/
  {topic} - ARP.md
       │
       └──────────────────────────────┐
                                      │
                                      ▼
                                 ┌─────────┐
                                 │   CTP   │
                                 │  Agent  │
                                 └─────────┘
```

---
# Agent Definition Schema (ORIGINAL DESIGN)

> **⚠️ This section describes the ORIGINAL design.** The actual implementation uses a different approach:
> - Configuration is in `orchestrator.yaml` nodes (not individual agent files)
> - Prompt files in `_Settings_/Prompts/` have minimal frontmatter (title, abbreviation, category only)
> - See [docs/orchestrator.md](../orchestrator.md) for current implementation details.

## Frontmatter Format (Original Design - Not Implemented)
Each agent is defined in a Markdown file in `_Settings_/Agents/` with YAML frontmatter:

```yaml
---
# Basic Identity
title: Enrich Ingested Content
abbreviation: EIC
category: ingestion

# Trigger Configuration (when to run)
trigger_pattern: "Ingest/Clipping/*.md"
trigger_event: created
trigger_exclude_pattern: "*EIC*"
trigger_schedule: ""
trigger_wait_for: []

# Input/Output Paths
input_path: "Ingest/Clipping/"
input_type: new_file
output_path: "AI/Clipping/"
output_type: new_file
output_naming: "{title} - {agent}.md"

# Dependencies
skills:
  - obsidian_links
  - topic_matching
mcp_servers: []

# Execution
executor: claude_code
max_parallel: 1
timeout_minutes: 30
---

# Agent Instructions
[Prompt body with detailed instructions]
```

## Field Definitions
### Trigger Configuration
- **trigger_pattern**: Glob pattern for files that trigger this agent
- **trigger_event**: `created` | `modified` | `deleted` | `scheduled` | `manual`
- **trigger_exclude_pattern**: Optional glob pattern to exclude files
- **trigger_schedule**: Cron-like schedule (e.g., `daily@07:00`)
- **trigger_wait_for**: List of agent abbreviations to wait for completion

### Input/Output
- **input_path**: Primary input directory (can be list)
- **input_type**: `new_file` | `updated_file` | `daily_files` | `date_range` | `vault_wide`
- **output_path**: Output directory
- **output_type**: `new_file` | `new_files` | `daily_file`
- **output_naming**: Template for output filename

### Dependencies
- **skills**: List of skill names to load
- **mcp_servers**: List of MCP servers required (e.g., `gcal`, `web_search`)

### Execution
- **executor**: `claude_code` | `gemini_cli` | `custom_script`
- **max_parallel**: Maximum concurrent executions
- **timeout_minutes**: Execution timeout

## Task Schema

> **⚠️ Implementation Note:** Task files are actually created in `_Settings_/Tasks/`, not `_Tasks_/` at root level.

When the orchestrator triggers an agent, it creates a task file in `_Settings_/Tasks/` based on the task template. The task file tracks execution state and is updated by the agent during execution:

```yaml
---
title: "EIC: Process Web Clipping"
agent: EIC
status: in_progress
trigger_file: "Ingest/Clipping/Article Title.md"
created: 2025-10-25T10:30:00
started: 2025-10-25T10:30:05
completed: ""
error: ""
output_files: []
---

# Task Execution Log
[Agent updates this section during execution]
```

**Task Lifecycle**:
1. Orchestrator creates task file with `status: pending`
2. Execution Manager updates to `status: in_progress` when agent starts
3. Agent updates task file during execution (logs, progress)
4. Agent sets `status: completed` or `status: failed` on finish
5. Orchestrator can query task files to monitor system health

---
# Orchestrator Architecture

## High-Level Components
```
┌───────────────────────────────────────────────────────────────────┐
│                         ORCHESTRATOR                               │
├───────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │                  Orchestrator Core                        │    │
│  │                                                            │    │
│  │  1. Load agent definitions from _Settings_/Agents/       │    │
│  │  2. Monitor file system for events                       │    │
│  │  3. Match events to agent triggers                       │    │
│  │  4. Spawn agents with proper context                     │    │
│  │  5. Track execution state                                │    │
│  │  6. Manage concurrency                                   │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                     │
│  ┌────────────────────┬────────────────────┬──────────────────┐  │
│  │                    │                    │                  │  │
│  ▼                    ▼                    ▼                  │  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │  │
│  │ File System  │  │    Agent     │  │  Execution   │       │  │
│  │   Monitor    │  │   Registry   │  │   Manager    │       │  │
│  └──────────────┘  └──────────────┘  └──────────────┘       │  │
│                                                                     │
└───────────────────────────────────────────────────────────────────┘
           │                      │                      │
           ▼                      ▼                      ▼
    ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
    │   Watchdog  │      │   Agent     │      │   Agent     │
    │   Events    │      │ Definitions │      │  Threads    │
    └─────────────┘      └─────────────┘      └─────────────┘
```

**Note**: Skills are managed by individual agents, not centrally by the orchestrator. Each agent specifies its required skills in frontmatter, and skills are loaded/invoked within the agent's execution context.

## Component 1: File System Monitor
**Responsibilities**:
1. Watch vault for file system events (create, modify, delete)
2. Filter events based on patterns
3. Debounce rapid-fire events
4. Parse frontmatter to extract state
5. Queue events for processing

**Key Methods**:
```python
class FileSystemMonitor:
    def __init__(self, vault_path, agent_registry):
        self.vault_path = vault_path
        self.agent_registry = agent_registry
        self.observer = Observer()
        self.event_queue = Queue()

    def start(self):
        """Start monitoring file system."""

    def _on_file_event(self, event):
        """Handle file system event."""
        # Parse frontmatter, queue event

    def _parse_frontmatter(self, file_path) -> Dict:
        """Extract YAML from markdown."""
```

## Component 2: Agent Registry
**Responsibilities**:
1. Load all agent definitions from `_Settings_/Agents/`
2. Parse frontmatter and prompt body
3. Validate agent definitions (using JSON schema)
4. Provide agent lookup by trigger conditions
5. Hot-reload when agent definitions change
6. Export current configurations to JSON for debugging

**Agent Definition JSON Schema**:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["title", "abbreviation", "category", "trigger_pattern", "trigger_event"],
  "properties": {
    "title": {"type": "string"},
    "abbreviation": {"type": "string", "pattern": "^[A-Z]{3}$"},
    "category": {"enum": ["ingestion", "publish", "research"]},
    "trigger_pattern": {"type": "string"},
    "trigger_event": {"enum": ["created", "modified", "deleted", "scheduled", "manual"]},
    "executor": {"enum": ["claude_code", "gemini_cli", "custom_script"]},
    "max_parallel": {"type": "integer", "minimum": 1},
    "timeout_minutes": {"type": "integer", "minimum": 1}
  }
}
```

**Key Methods**:
```python
class AgentRegistry:
    def __init__(self, agents_dir, vault_path):
        self.agents_dir = agents_dir
        self.agents: Dict[str, AgentDefinition] = {}
        self.load_all_agents()

    def load_all_agents(self):
        """Load all agent definitions from directory."""

    def find_matching_agents(self, event_data) -> List[AgentDefinition]:
        """Find agents whose triggers match the event."""

    def _matches_trigger(self, agent, event_path, event_type, frontmatter) -> bool:
        """Check if event matches agent's trigger conditions."""

    def export_config_snapshot(self, output_path):
        """Export current agent configurations to JSON for debugging."""
        # Creates _Tasks_/Logs/orchestrator/agent_config_snapshot.json
```

## Component 3: Execution Manager
**Responsibilities**:
1. Spawn agent execution threads/processes (non-blocking)
2. Manage concurrency (limit parallel agents)
3. Track execution state and metrics
4. Handle agent failures and retries
5. Collect logs and results

**Key Methods**:
```python
class ExecutionManager:
    def __init__(self, max_concurrent=3):
        self.max_concurrent = max_concurrent
        self.semaphore = Semaphore(max_concurrent)
        self.active_executions: Dict[str, ExecutionContext] = {}
        self.metrics = MetricsCollector()

    def execute_agent(self, agent_def, trigger_data):
        """Execute an agent in a separate thread (non-blocking)."""
        # Uses threading to avoid blocking orchestrator event loop

    def _run_agent(self, context):
        """Run agent in current thread."""

    def _execute_via_executor(self, executor, prompt, context, log_file):
        """Execute agent via specified executor (claude_code, etc.)."""
```

## Orchestrator Main Loop
**Note**: Event loop uses queue with timeout to avoid blocking. Agent execution happens in separate threads.

```python
class Orchestrator:
    def __init__(self, vault_path):
        self.vault_path = vault_path
        self.agent_registry = AgentRegistry(vault_path / '_Settings_' / 'Agents')
        self.file_monitor = FileSystemMonitor(vault_path, self.agent_registry)
        self.execution_manager = ExecutionManager(max_concurrent=3)

    def start(self):
        """Start the orchestrator."""
        self.file_monitor.start()
        self._event_loop()

    def _event_loop(self):
        """Main event processing loop (non-blocking with timeout)."""
        while True:
            event = self.file_monitor.event_queue.get(timeout=1.0)
            matching_agents = self.agent_registry.find_matching_agents(event)

            for agent in matching_agents:
                # Non-blocking: spawns thread and continues
                self.execution_manager.execute_agent(
                    agent_def=agent,
                    trigger_data=event
                )
```

---
# System Architecture

**Important Notes**:
- `AI/` folders are NOT created automatically - user must create them
- Task files moved to `_Tasks_/` at root level (not `AI/Tasks/`)

```
AI4PKM/
├── ai4pkm_cli/
│   └── orchestrator/
│       ├── __init__.py
│       ├── core.py                    # Orchestrator main class
│       ├── file_monitor.py            # FileSystemMonitor
│       ├── agent_registry.py          # AgentRegistry
│       ├── execution_manager.py       # ExecutionManager
│       ├── metrics.py                 # MetricsCollector
│       ├── models.py                  # Data classes
│       └── utils.py                   # Orchestrator utilities
│           # - YAML frontmatter parsing
│           # - Multi-executor spawning (Claude/Gemini/OpenAI)
│           # - Task file creation/updates
├── _Settings_/
│   ├── Agents/
│   │   ├── EIC Agent.md               # Agent definitions with skills in frontmatter
│   │   ├── PLL Agent.md
│   │   ├── PPP Agent.md
│   │   ├── GES Agent.md
│   │   ├── GDR Agent.md
│   │   ├── CTP Agent.md
│   │   └── ARP Agent.md
│   └── Skills/                        # Skill definitions (Python + Markdown)
│       ├── content_collection/
│       ├── publishing/
│       ├── knowledge_organization/
│       └── obsidian_rules/
├── _Tasks_/                           # Root-level task tracking
│   ├── YYYY-MM-DD Task Name.md        # Individual task files
│   └── Logs/
│       └── orchestrator/
│           ├── orchestrator.log
│           ├── metrics.json
│           └── agent_config_snapshot.json
└── AI/                                # User-created content folders
    ├── Clipping/
    ├── Lifelog/
    └── Roundup/
```

**Note**: Skills are stored in `_Settings_/Skills/` and loaded by individual agents. The orchestrator uses utilities in `utils.py` for common operations (YAML parsing, spawning executors, task management).

---
# Key Design Decisions

## 1. File System as State Database
**Decision**: Use file frontmatter to store execution state instead of separate database.

**Rationale**:
- Keeps state close to content (Obsidian-friendly)
- No separate DB to maintain
- Easy to inspect and debug
- Supports Obsidian's property editor

**Trade-offs**:
- File I/O for state checks (slower than DB)
- Limited query capabilities

## 2. Flat Frontmatter Structure
**Decision**: Use flat key-value pairs instead of nested YAML.

**Rationale**:
- Obsidian property editor requires flat structure
- Easier to parse and validate
- Reduces YAML syntax errors

## 3. Thread-Based Execution
**Decision**: Use Python threads instead of processes for agent execution.

**Rationale**:
- Simpler concurrency model
- Shared memory (easier to access vault state)
- Lower resource overhead

**Mitigation**: Add timeout and error handling

## 4. Agent = Prompt Body
**Decision**: Agent is entirely defined by its prompt body (no hardcoded types). Agents can be run as prompts at will by the user.

**Rationale**:
- Maximum flexibility (easy to modify behavior)
- No code changes needed to update agents
- Supports user-created custom agents
- Users can invoke any agent manually via CLI with custom context
- Example: `ai4pkm run EIC --input "custom-file.md"` or `ai4pkm run ARP --question "your research question"`

## 5. Skills as Python Modules and Markdown Instructions
**Decision**: Skills can be both Python modules and Markdown instructions, managed by individual agents (not centrally by orchestrator).

**Rationale**:
- Follows Anthropic's skills architecture (https://www.anthropic.com/news/skills)
- Python skills: Reusable code, leverage full Python ecosystem
- Markdown skills: Simple instructions, easy to create and modify
- Agent-level management: Each agent loads only the skills it needs
- Easy to test independently

---
# FAQ

### How is Agent different from Prompt?
Agent is simply runtime for prompts, where a given task is run using input and output specified. Users can run prompt manually, and use Orchestrator to run prompt automatically.

### How do I make complex workflows?
You can chain prompts to build a complex workflow. Just write prompts so that the output of one prompt becomes the input of another prompt. Use file property if you'd like to chain one input agent (=prompt) to multiple output agents.

### How do I debug agent execution?
1. Check task files in `_Tasks_/` for execution logs and status
2. Review `_Tasks_/Logs/orchestrator/orchestrator.log` for system events
3. Export agent configurations using `agent_config_snapshot.json` for debugging
4. Use `ai4pkm run <AGENT> --debug` to run agents manually with verbose logging

### Can I create custom agents?
Yes! Simply create a new Markdown file in `_Settings_/Agents/` with proper frontmatter. The orchestrator will automatically load and execute it based on trigger conditions.

### How do I handle agent dependencies?
Use the `trigger_wait_for` field in frontmatter to specify which agents must complete before this agent runs. Example: GDR waits for EIC, PLL, GES to finish.

---
# Conclusion

This design provides a complete architecture for the orchestrator that will power the AI4PKM multi-agent system. Key features:

1. **Multi-Agent Ecosystem**: Clear visualization of all agent connections and data flows
2. **Flexible Agent Definitions**: Markdown files with Obsidian-compatible frontmatter
3. **Modular Architecture**: Three core components (File System Monitor, Agent Registry, Execution Manager)
4. **Skills Framework**: Both Python and Markdown skills, managed by individual agents
5. **File-Based State**: No separate database needed

---
# Migration Path from KTM

## Current KTM Architecture Analysis
The existing Knowledge Task Management (KTM) system has several components we can reuse:

### Reusable Components
1. **File Watchdog Infrastructure** (`ai4pkm_cli/watchdog/file_watchdog.py`)
   - Watchdog Observer setup
   - Pattern matching logic
   - BaseFileHandler abstract class
   - Reuse: ~80%

2. **Task Semaphore** (`ai4pkm_cli/watchdog/task_semaphore.py`)
   - Concurrency control logic
   - Shared semaphore management
   - Reuse: 100% (rename to ConcurrencyManager)

3. **Thread-Specific Logging** (`ai4pkm_cli/logger.py`)
   - Log file creation per task
   - Log path management
   - Reuse: 100% (integrate into utils.py)

4. **Existing Handlers** (all in `ai4pkm_cli/watchdog/handlers/`)
   - Pattern definitions
   - File detection logic
   - Reuse: Extract patterns to agent definitions

### Components to Replace
1. **KTG (Knowledge Task Generator)** → Agent Registry
   - Task request JSON creation → Agent trigger matching
   - Pattern: Reuse handler patterns as `trigger_pattern` in agent frontmatter

2. **KTP (Knowledge Task Processor)** → Execution Manager
   - 3-phase processing → Thread-based agent execution
   - Task status management → Task file frontmatter updates

3. **Handler Classes** → Agent Definitions
   - Each handler becomes agent configuration
   - Code logic moves to agent prompts and skills

## Migration Strategy

### Phase 1: Parallel Implementation (Week 1-2)
**Goal**: Build orchestrator alongside KTM without disruption

**Tasks**:
1. Create `ai4pkm_cli/orchestrator/` directory structure
2. Implement core components:
   - Copy `file_watchdog.py` → `file_monitor.py` (modify for orchestrator)
   - Copy `task_semaphore.py` → Integrate into `execution_manager.py`
   - Copy logging logic → `utils.py`
3. Create minimal agent definitions for testing
4. DO NOT modify existing KTM code

**Validation**:
- KTM continues to work normally
- Orchestrator components pass unit tests
- No file conflicts between systems

### Phase 2: Single Agent Migration (Week 3)
**Goal**: Migrate EIC agent as proof of concept

**Tasks**:
1. Create `_Settings_/Agents/EIC Agent.md` with full frontmatter
2. Extract EIC prompt from existing code
3. Test EIC via orchestrator (parallel to KTM)
4. Compare outputs: KTM-EIC vs Orchestrator-EIC
5. Keep both systems running

**Validation**:
- Both systems produce identical outputs for same input
- Orchestrator EIC completes without errors
- Task files tracked correctly in `_Tasks_/`

### Phase 3: Disable KTM Handlers One-by-One (Week 4-5)
**Goal**: Gradually switch traffic to orchestrator

**Migration Order** (low-risk first):
1. **PPP** (Photo Processing) - Lowest risk, simple workflow
2. **EIC** (Enrich Clippings) - Already tested in Phase 2
3. **GES** (Event Summary) - Medium risk, MCP dependency
4. **PLL** (Process Lifelogs) - Medium risk, complex integration
5. **GDR** (Daily Roundup) - Higher risk, aggregates multiple sources
6. **CTP** (Thread Posts) - Manual trigger, low risk
7. **ARP** (Research) - Manual trigger, low risk

**For Each Agent**:
1. Create agent definition in `_Settings_/Agents/`
2. Add orchestrator flag: `orchestrator_enabled: true`
3. Run both systems in parallel for 24 hours
4. Compare outputs side-by-side
5. If identical → disable KTM handler
6. If different → debug, fix, retry

**Rollback**: Set `orchestrator_enabled: false` to revert to KTM

### Phase 4: Complete Cutover (Week 6)
**Goal**: Remove KTM code entirely

**Tasks**:
1. All agents running via orchestrator for 1 week with no issues
2. Archive KTM code:
   ```bash
   mkdir -p archive/ktm-legacy
   mv ai4pkm_cli/watchdog/handlers/* archive/ktm-legacy/
   mv ai4pkm_cli/commands/ktg_runner.py archive/ktm-legacy/
   mv ai4pkm_cli/commands/ktp_runner.py archive/ktm-legacy/
   ```
3. Update CLI entry points to use orchestrator
4. Update documentation
5. Create git tag: `ktm-to-orchestrator-migration-complete`

**Validation**:
- All 7 agents running successfully
- No KTM code in active codebase
- All tests passing

### Phase 5: Enhancements (Week 7+)
**Goal**: Add orchestrator-specific features

**New Capabilities**:
1. Agent dependencies (`trigger_wait_for`)
2. Scheduled execution (cron triggers)
3. Agent configuration snapshots
4. System improvement loop
5. User installation wizard

## Detailed Handler → Agent Mapping

### 1. ClippingFileHandler → EIC Agent
**Current** (`clipping_file_handler.py`):
```python
def get_patterns(self) -> List[str]:
    return ['Ingest/Clipping/*.md']

def should_process(self, file_path: Path) -> bool:
    return 'EIC' not in file_path.name
```

**New** (Agent frontmatter):
```yaml
trigger_pattern: "Ingest/Clipping/*.md"
trigger_event: created
trigger_exclude_pattern: "*EIC*"
```

**Reuse**: Pattern logic, exclusion logic
**Change**: Execution method (KTG → direct agent spawn)

### 2. LimitlessFileHandler → PLL + GES Agents
**Current** (`limitless_file_handler.py`):
- Single handler triggers multiple tasks
- Conditional logic for meeting detection

**New**:
- Split into two agent definitions
- PLL: Daily schedule trigger
- GES: Modified file trigger

**Reuse**: File patterns, meeting detection logic (move to skill)
**Change**: Split single handler into two agents

### 3. Task Request Handler → Agent Registry
**Current** (`task_request_file_handler.py`):
- Watches `AI/Tasks/Requests/*/*.json`
- Parses JSON to create task

**New**:
- Agent Registry directly creates tasks
- No intermediate JSON files

**Reuse**: Task file creation logic
**Change**: Remove JSON layer, direct task creation

### 4. Task Processor → Execution Manager
**Current** (`task_processor.py`):
- 3-phase processing (TBD → PROCESSING → PROCESSED)
- Status transitions via frontmatter updates

**New**:
- Thread-based execution
- Same status transitions
- Cleaner status management

**Reuse**: Status state machine, frontmatter updates
**Change**: Threading model, simpler execution flow


---
# Conclusion

This design provides a complete architecture for the orchestrator that will power the AI4PKM multi-agent system. Key features:

1. **Multi-Agent Ecosystem**: Clear visualization of all agent connections and data flows
2. **Flexible Agent Definitions**: Markdown files with Obsidian-compatible frontmatter
3. **Modular Architecture**: Three core components (File System Monitor, Agent Registry, Execution Manager)
4. **Skills Framework**: Both Python and Markdown skills, managed by individual agents
5. **File-Based State**: No separate database needed
6. **Safe Migration Path**: Gradual migration from KTM with parallel running and rollback capability
7. **Comprehensive Testing**: Unit, integration, and E2E tests ensure quality and compatibility

Next steps:
1. **Start with Phase 1**: See [[2025-10-25 Phase 1 - Parallel Implementation]] for detailed implementation plan
2. Migrate EIC agent as proof of concept (Week 3)
3. Follow migration order for remaining agents (Week 4-5)
4. Complete cutover and remove KTM code (Week 6)
5. Add orchestrator-specific enhancements (Week 7+)

---
**Document Version**: 2.0
**Last Updated**: 2025-10-25 (Design), 2025-11-01 (Status Update)
**Status**: HISTORICAL REFERENCE - Implementation Complete with Modifications

**For Current Implementation**: See [docs/orchestrator.md](../orchestrator.md)
