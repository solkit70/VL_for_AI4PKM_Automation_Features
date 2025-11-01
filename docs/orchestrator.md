# Orchestrator

The AI4PKM Orchestrator is a multi-agent system that monitors your Obsidian vault for file changes and automatically triggers AI agents to process content.

## Overview

### What is the Orchestrator?

The Orchestrator provides an automated, event-driven workflow for personal knowledge management. When you add content to your vault—whether it's a web clipping, a voice note, or a manual hashtag—the orchestrator automatically routes it to the appropriate AI agent for processing.

**Key Features:**

- **Automatic Processing**: File changes trigger AI agents automatically
- **Multi-Agent Support**: Route tasks to different CLI agents (Claude, Gemini, Codex)
- **Concurrent Execution**: Process multiple tasks simultaneously with configurable limits
- **Task Tracking**: Full transparency with task files and execution logs
- **Flexible Configuration**: Define agents and workflows through simple YAML configuration

### Architecture

```
File Change Event
      |
      v
File Monitor (watchdog)
      |
      v
Agent Registry (pattern matching)
      |
      v
Execution Manager (concurrency control)
      |
      v
Background Thread -> CLI Agent -> Task File
```

For more details, see the [architecture blog post](https://jykim.github.io/AI4PKM/blog/2025/10/30/new-architecture-for-agentic-ai.html).

---

## Quick Start

### 1. Check System Status

```bash
cd /path/to/your/vault
ai4pkm --orchestrator-status
```

**Expected Output:**
```
+--- Orchestrator Status -----------+
| Vault: /Users/.../ai4pkm_vault    |
| Agents loaded: 7                  |
| Max concurrent: 3                 |
+-----------------------------------+

Available Agents:
  * [HTC] Hashtag Task Creator
    Category: ingestion
  * [EIC] Enrich Ingested Content
    Category: ingestion
  ...
```

### 2. Start the Orchestrator

```bash
# Start with default settings
ai4pkm -o

# Or with custom concurrency
ai4pkm -o --max-concurrent 5
```

The orchestrator will:
- Load agent definitions from `orchestrator.yaml`
- Start monitoring vault files for changes
- Display real-time notifications for agent execution
- Run until you press `Ctrl+C`

### 3. Test It Out

**Option A: Add a web clipping**
```bash
# Save a web clipping to trigger EIC agent
# File: Ingest/Clippings/2025-10-30 Article.md
```

**Option B: Add a hashtag**
```markdown
# In any note, add:
%% #ai summarize this content %%
```

You'll see the orchestrator respond with:
```
> Starting EIC: Ingest/Clippings/2025-10-30 Article.md
[OK] EIC completed (120.5s)
```

---

## Configuration

### Directory Structure

The orchestrator requires the following directories in your vault:

```
your-vault/
├── orchestrator.yaml          # Main configuration file
├── _Settings_/
│   ├── Prompts/              # Agent prompt definitions
│   │   ├── Enrich Ingested Content (EIC).md
│   │   ├── Hashtag Task Creator (HTC).md
│   │   └── ...
│   ├── Tasks/                # Task tracking files (auto-created)
│   └── Logs/                 # Execution logs (auto-created)
├── Ingest/
│   └── Clippings/            # Input: Web clippings
└── AI/
    └── Articles/             # Output: Processed content
```

### orchestrator.yaml

The main configuration file defines orchestrator settings, defaults, and agent routing.

**Location**: `<vault_root>/orchestrator.yaml`

**Complete Example:**

```yaml
# AI4PKM Orchestrator Configuration
version: "1.0"

# Orchestrator runtime settings
orchestrator:
  prompts_dir: "_Settings_/Prompts"      # Agent prompt definitions
  tasks_dir: "_Settings_/Tasks"          # Task tracking files
  logs_dir: "_Settings_/Logs"            # Execution logs
  skills_dir: "_Settings_/Skills"        # Skills library (future)
  bases_dir: "_Settings_/Bases"          # Knowledge bases (future)
  max_concurrent: 3                      # Global concurrency limit
  poll_interval: 1.0                     # Event queue poll interval (seconds)

# Global defaults for all agents
defaults:
  executor: claude_code                  # Default CLI agent
  timeout_minutes: 30                    # Default timeout
  max_parallel: 3                        # Default per-agent limit
  task_create: true                      # Create task files
  task_priority: medium                  # Default priority
  task_archived: false                   # Default archived status

# Agent definitions (nodes-based configuration)
nodes:
  # Enrich Ingested Content
  - type: agent
    name: Enrich Ingested Content (EIC)
    input_path: Ingest/Clippings         # Auto-triggers on new files
    output_path: AI/Articles

  # Process Life Logs
  - type: agent
    name: Process Life Logs (PLL)
    input_path: Ingest/Limitless
    output_path: AI/Lifelog

  # Generate Daily Roundup (scheduled - future feature)
  - type: agent
    name: Generate Daily Roundup (GDR)
    cron: 0 1 * * *                      # 1AM every day (not yet implemented)
    output_path: AI/Roundup

  # Manual-only agent (no input_path)
  - type: agent
    name: Ad-hoc Research within PKM (ARP)
    output_path: AI/Research
```

### Configuration Reference

#### orchestrator Section

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `prompts_dir` | string | `_Settings_/Prompts` | Agent prompt definitions directory |
| `tasks_dir` | string | `_Settings_/Tasks` | Task tracking files directory |
| `logs_dir` | string | `_Settings_/Logs` | Execution logs directory |
| `max_concurrent` | integer | 3 | Max concurrent executions (global) |
| `poll_interval` | float | 1.0 | Event queue poll interval (seconds) |

#### defaults Section

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `executor` | string | `claude_code` | Default CLI agent |
| `timeout_minutes` | integer | 30 | Default execution timeout |
| `max_parallel` | integer | 3 | Default per-agent concurrency |
| `task_create` | boolean | true | Create task tracking files |
| `task_priority` | string | `medium` | Default task priority |

#### nodes Section

Each node defines an agent with the following fields:

**Required:**
- `type: agent` - Node type (required)
- `name: "Full Name (ABBR)"` - Agent name with abbreviation in parentheses

**Optional:**
- `input_path` - Input directory to monitor (string or list)
  - If omitted or null: manual-only agent (no auto-trigger)
  - Single path: watches for new files in that directory
  - Multiple paths: triggers on first path (full multi-input support coming soon)
- `output_path` - Output directory for results
- `cron` - Cron schedule for periodic execution (future feature)

**Agent-Specific Settings** (override defaults):
- `trigger_exclude_pattern` - Glob pattern to exclude files (e.g., `"*-EIC*"`)
- `trigger_content_pattern` - Regex to match in file content (e.g., `"(?i)%%.*?#ai\\b.*?%%"`)
- `post_process_action` - Action after completion (e.g., `"remove_trigger_content"`)
- `executor` - CLI agent to use (e.g., `"claude_code"`, `"gemini_cli"`)
- `timeout_minutes` - Execution timeout in minutes (e.g., `60`)
- `max_parallel` - Max concurrent executions for this agent (e.g., `1`)
- `task_priority` - Task priority level: `"low"`, `"medium"`, or `"high"`

**Example with agent-specific settings:**

```yaml
nodes:
  # Agent with custom settings
  - type: agent
    name: Hashtag Task Creator (HTC)
    trigger_exclude_pattern: "_Settings_/*"
    trigger_content_pattern: "(?i)%%.*?#ai\\b.*?%%"
    post_process_action: remove_trigger_content
    task_priority: high
    max_parallel: 1
    timeout_minutes: 10

  # Agent with minimal settings (uses defaults)
  - type: agent
    name: Enrich Ingested Content (EIC)
    input_path: Ingest/Clippings
    output_path: AI/Articles
    trigger_exclude_pattern: "*-EIC*"
```

**How Triggers Work:**

The orchestrator automatically derives trigger patterns from `input_path`:

```yaml
# Example 1: Auto-trigger on new files
input_path: Ingest/Clippings
# Derived: watches "Ingest/Clippings/**/*.md", triggers on "created"

# Example 2: Manual-only agent
# input_path omitted or set to null
# No automatic triggering, must be invoked manually

# Example 3: Multi-input (planned)
input_path:
  - AI/Articles
  - AI/Roundup
# Future: will trigger on new files in any of these directories
```

### Prompt Files

Agent prompts are stored as Markdown files with minimal frontmatter and prompt instructions.

**Location**: `<vault_root>/_Settings_/Prompts/`

**Naming Convention**: `{Full Name} ({ABBR}).md`

**Example**: `_Settings_/Prompts/Enrich Ingested Content (EIC).md`

```yaml
---
title: Enrich Ingested Content (EIC)
abbreviation: EIC
category: ingestion
---
Improve captured content through transcript correction, summarization, and knowledge linking.

## Input
- Target note file with original clipped content
- May contain grammar or transcript errors

## Output
- Improved formatting and structure
- Summary section added at beginning
- Related topics linked
- Status property set to "processed"

## Main Process

1. **Fix Transcript Errors**
   - Correct grammar and spelling
   - Remove extra/duplicated newlines
   - Add proper formatting (lists, highlights)

2. **Add Summary**
   - Write catchy summary for sharing
   - Use quotes verbatim to convey author's voice
   - Keep concise and engaging

3. **Enrich with Links**
   - Link related knowledge base topics (existing only)
   - Add one-line summary to relevant KB topics
   - Connect to related summaries
```

**Required Frontmatter Fields:**
- `title` - Full agent name (must match name in orchestrator.yaml)
- `abbreviation` - 3-4 letter abbreviation (e.g., "EIC", "HTC")
- `category` - Agent category: `ingestion`, `publish`, or `research`

**Note**: All configuration (input/output paths, triggers, timeouts, priorities, etc.) is defined in `orchestrator.yaml`, NOT in prompt file frontmatter. Prompt files only contain metadata (title, abbreviation, category) and instructions.

---

## CLI Usage

### Commands

#### Show Status

```bash
ai4pkm --orchestrator-status
```

Displays:
- Vault path
- Number of loaded agents
- Max concurrent executions
- List of available agents with categories

Use this command to:
- Verify agents are configured correctly
- Check agent definitions are loaded
- Debug configuration issues

#### Start Orchestrator

```bash
# Standard mode
ai4pkm -o

# With custom concurrency
ai4pkm -o --max-concurrent 5

# Full form also works
ai4pkm --orchestrator --max-concurrent 5
```

**Options:**
- `--max-concurrent N` - Set maximum concurrent executions (default: 3)

**When Running:**
- Press `Ctrl+C` to stop gracefully
- Check logs in `_Settings_/Logs/`
- Task files created in `_Settings_/Tasks/`

### Console Output

The orchestrator provides real-time notifications:

**Starting Execution:**
```
> Starting EIC: Ingest/Clippings/2025-10-28 Article.md
```

**Successful Completion:**
```
[OK] EIC completed (120.5s)
```

**Failure:**
```
[FAIL] EIC failed: timeout (180.0s)
   Error: Execution timed out after 30 minutes
```

**Concurrency Limit:**
```
[QUEUED] PLL: concurrency limit reached
```

**Full Session Example:**
```
+------------- Starting ---------------+
| AI4PKM Orchestrator                  |
| Vault: /Users/you/vault              |
| Max concurrent: 3                    |
+--------------------------------------+

* Loaded 7 agent(s):
  * [EIC] Enrich Ingested Content (ingestion)
  * [PLL] Process Life Logs (ingestion)
  * [GDR] Generate Daily Roundup (research)
  ...

Starting orchestrator...
> Starting EIC: Ingest/Clippings/2025-10-28 Article.md
[OK] EIC completed (125.3s)
> Starting PLL: Ingest/Limitless/2025-10-28 Activities.md
[OK] PLL completed (89.7s)
```

---

## Agent Types

### 1. Auto-Trigger Agents

Agents with `input_path` automatically trigger when new files are created in the specified directory.

**Example: Enrich Ingested Content (EIC)**

```yaml
# In orchestrator.yaml
nodes:
  - type: agent
    name: Enrich Ingested Content (EIC)
    input_path: Ingest/Clippings
    output_path: AI/Articles
```

**Behavior:**
- Watches: `Ingest/Clippings/**/*.md`
- Triggers: When new file created
- Creates: Task file in `_Settings_/Tasks/`
- Outputs: Enriched content in `AI/Articles/`

### 2. Content-Triggered Agents

Agents that trigger based on file content patterns (like hashtags).

**Example: Hashtag Task Creator (HTC)**

```yaml
# In orchestrator.yaml
nodes:
  - type: agent
    name: Hashtag Task Creator (HTC)
    # No input_path -> watches entire vault
    trigger_exclude_pattern: "_Settings_/*"
    trigger_content_pattern: "(?i)%%.*?#ai\\b.*?%%"
    post_process_action: remove_trigger_content
    task_priority: high
```

The prompt file `_Settings_/Prompts/Hashtag Task Creator (HTC).md` contains minimal frontmatter and instructions:

```yaml
---
title: Hashtag Task Creator (HTC)
abbreviation: HTC
category: ingestion
---

[Prompt instructions for HTC agent]
```

**Behavior:**
- Watches: Entire vault (`**/*.md`)
- Excludes: `_Settings_/*` files
- Triggers: Only if content matches `%% #ai %%`
- Post-process: Removes `%% #ai %%` from source file

### 3. Manual-Only Agents

Agents without `input_path` that must be invoked manually.

**Example: Ad-hoc Research (ARP)**

```yaml
# In orchestrator.yaml
nodes:
  - type: agent
    name: Ad-hoc Research within PKM (ARP)
    # input_path omitted -> manual-only
    output_path: AI/Research
```

**Behavior:**
- No automatic triggering
- Must be invoked manually via CLI or other means
- Used for on-demand research tasks

### 4. Scheduled Agents (Future)

Agents with `cron` schedules for periodic execution.

```yaml
# Future feature - not yet implemented
nodes:
  - type: agent
    name: Generate Daily Roundup (GDR)
    cron: 0 1 * * *  # 1AM every day
    output_path: AI/Roundup
```

---

## Appendix A: Common Patterns

### Sequential Processing Chain

Create a pipeline where one agent's output becomes another's input:

```yaml
nodes:
  # Step 1: Ingest and enrich
  - type: agent
    name: Enrich Ingested Content (EIC)
    input_path: Ingest/Clippings
    output_path: AI/Articles

  # Step 2: Create shareable posts
  - type: agent
    name: Create Thread Postings (CTP)
    input_path: AI/Articles
    output_path: AI/Sharable
```

### Parallel Processing

Process the same input with multiple agents:

```yaml
nodes:
  # Both process same input directory
  - type: agent
    name: Process Life Logs (PLL)
    input_path: Ingest/Limitless
    output_path: AI/Lifelog

  - type: agent
    name: Generate Event Summary (GES)
    input_path: Ingest/Limitless
    output_path: AI/Events
```

### Conditional Triggering

Use content patterns for conditional execution:

```yaml
# In prompt file frontmatter:
---
trigger_content_pattern: "%%.*#urgent.*%%"
task_priority: high
timeout_minutes: 60
---
```

### Concurrency Tuning

**Conservative** (low resource usage):
```yaml
orchestrator:
  max_concurrent: 1
defaults:
  max_parallel: 1
```

**Balanced** (recommended):
```yaml
orchestrator:
  max_concurrent: 3
defaults:
  max_parallel: 2
```

**Aggressive** (high throughput):
```yaml
orchestrator:
  max_concurrent: 10
defaults:
  max_parallel: 5
```

---

## Appendix B: Task Management

### Task File Structure

Task files track execution and provide transparency.

**Location**: `_Settings_/Tasks/`

**Naming**: `{YYYY-MM-DD} {input_name} - {agent_abbr}.md`

**Example**: `_Settings_/Tasks/2025-10-30 Article - EIC.md`

```yaml
---
title: "Article - EIC"
created: 2025-10-30T14:23:45
task_type: EIC
status: IN_PROGRESS
priority: high
archived: false
trigger_data_json: '{"path": "Ingest/Clippings/Article.md"}'
log_file: "_Settings_/Logs/2025-10-30-142345-eic.log"
---

# Task: Enrich Article

[Agent's output will appear here]
```

### Task Lifecycle

1. **QUEUED** - Waiting for execution slot
2. **IN_PROGRESS** - Currently executing
3. **COMPLETED** - Finished successfully
4. **FAILED** - Error occurred
5. **TIMEOUT** - Exceeded timeout limit

### Execution Logs

**Location**: `_Settings_/Logs/`

**Naming**: `{timestamp}-{agent_abbr}.log`

**Example**: `_Settings_/Logs/2025-10-30-142345-eic.log`

```markdown
# Execution Log: EIC
# Start: 2025-10-30T14:23:45
# Execution ID: abc-123

## Prompt

[Full prompt sent to CLI agent]

## Response

[Complete response from CLI agent]
```

### Concurrency Control

**Two-Level System:**

1. **Global Limit**: Max total concurrent executions across all agents
2. **Per-Agent Limit**: Max concurrent executions per specific agent

**Example:**
- Global: `max_concurrent: 3` (only 3 agents running at once)
- EIC Agent: `max_parallel: 2` (only 2 EIC instances at once)
- HTC Agent: `max_parallel: 1` (only 1 HTC instance at once)

**Queue Handling:**
- When capacity reached, task created with `QUEUED` status
- Orchestrator polls for queued tasks after each event
- Executes queued tasks FIFO when slots free up

---

## Appendix C: Troubleshooting

### No Agents Loaded

**Symptom**: `ai4pkm --orchestrator-status` shows "Agents loaded: 0"

**Diagnosis:**
```bash
# Check orchestrator.yaml exists
ls orchestrator.yaml

# Check nodes list
grep -A 20 "^nodes:" orchestrator.yaml

# Check prompt files exist
ls _Settings_/Prompts/*.md
```

**Solutions:**
1. Create `orchestrator.yaml` if missing (use example above)
2. Verify `nodes` list has `type: agent` entries
3. Ensure prompt files match naming pattern: `{Name} ({ABBR}).md`
4. Check abbreviation extraction: name must contain `(XXX)` pattern

### Agent Not Triggering

**Symptom**: File changes but no "> Starting..." message

**Common Causes:**

1. **Path Mismatch**
   - Config: `input_path: Ingest/Clipping` (singular)
   - Actual: `Ingest/Clippings/` (plural)
   - Solution: Fix spelling in `orchestrator.yaml`

2. **Wrong Event Type**
   - Agent expects `created` but file was modified
   - Solution: Modify triggers on `created`, create new file or restart orchestrator

3. **File Created Before Orchestrator Started**
   - Orchestrator only detects NEW events after startup
   - Solution: Modify file to trigger event, or restart orchestrator

4. **Excluded by Pattern**
   - File matches `trigger_exclude_pattern`
   - Solution: Check prompt file frontmatter, adjust pattern

5. **Content Pattern Not Matched**
   - Agent requires content match (e.g., `%% #ai %%`)
   - File doesn't contain required pattern
   - Solution: Add trigger content or remove content requirement

### Concurrency Limit Blocking

**Symptom**: Seeing "[QUEUED]..." messages repeatedly

**Diagnosis:**
```bash
# Check current running tasks
grep -r "IN_PROGRESS" _Settings_/Tasks/*.md

# Count running executions
ps aux | grep claude
```

**Solutions:**
```bash
# Increase global limit
ai4pkm -o --max-concurrent 5

# Or reduce per-agent limit in orchestrator.yaml
defaults:
  max_parallel: 1  # Only one instance per agent
```

### Claude CLI Not Found

**Symptom**: `RuntimeError: Claude CLI not found`

**Diagnosis:**
```bash
# Check Claude installation
which claude
ls ~/.claude/local/claude
```

**Solutions:**
```bash
# Install Claude Code (if not installed)
# Visit: https://docs.anthropic.com/claude/docs/claude-code

# Login
claude /login

# Verify installation
claude --version
```

### Execution Timeout

**Symptom**: Task marked as `timeout` status

**Solutions:**

1. **Increase timeout in defaults:**
```yaml
# orchestrator.yaml
defaults:
  timeout_minutes: 60  # Increase from 30
```

2. **Override for specific agent:**
```yaml
# In prompt file frontmatter
---
timeout_minutes: 120  # 2 hours
---
```

3. **Optimize prompt:**
   - Reduce input size
   - Process in chunks
   - Simplify instructions

### Tasks Stuck in QUEUED State

**Symptom**: Task files remain QUEUED indefinitely

**Diagnosis:**
```bash
# Check for hung processes
ps aux | grep claude

# Check task file status
grep "status:" _Settings_/Tasks/*.md
```

**Solutions:**
1. Restart orchestrator (will process queued tasks)
2. Increase `max_concurrent` limit
3. Kill hung processes if any

---

## Appendix D: Migration Guide

### From Legacy KTM System

The orchestrator replaces the legacy KTM (Knowledge Task Management) system with a more flexible, configuration-driven approach.

**Key Differences:**

| Aspect | KTM (Legacy) | Orchestrator (New) |
|--------|--------------|-------------------|
| **Architecture** | Hardcoded handlers | Config-driven agents |
| **Agent Definitions** | Python classes | YAML + Markdown |
| **Triggers** | Handler registration | Pattern matching |
| **Configuration** | Prompt frontmatter | Centralized YAML |
| **Concurrency** | Global semaphore | Per-agent + global limits |
| **Status** | No visibility | Status command |

### From Agent Files to Nodes Config

**Before** (old agent definition in `_Settings_/Agents/EIC Agent.md`):
```yaml
---
title: Enrich Ingested Content
abbreviation: EIC
input_path: Ingest/Clippings
output_path: AI/Articles
trigger_pattern: "Ingest/Clippings/*.md"
trigger_event: created
trigger_exclude_pattern: "*-EIC*"
---

[Prompt body]
```

**After** (new approach):

1. **orchestrator.yaml** - All configuration in one place:
```yaml
nodes:
  - type: agent
    name: Enrich Ingested Content (EIC)
    input_path: Ingest/Clippings
    output_path: AI/Articles
    trigger_exclude_pattern: "*-EIC*"
    # trigger_pattern derived automatically from input_path
```

2. **_Settings_/Prompts/Enrich Ingested Content (EIC).md** - Minimal frontmatter + prompt:
```yaml
---
title: Enrich Ingested Content (EIC)
abbreviation: EIC
category: ingestion
---

[Prompt body with instructions]
```

**Benefits:**
- Single source of truth for ALL configuration (`orchestrator.yaml`)
- Easier to visualize agent connections and settings
- Simpler prompt files (only metadata + instructions, no config)
- Clear separation: configuration in YAML, instructions in Markdown

### Migration Steps

1. **Create orchestrator.yaml**
   - Use example above as template
   - Define all agents in `nodes` list with complete configuration

2. **Update Prompt Files**
   - Move `_Settings_/Agents/*.md` to `_Settings_/Prompts/*.md`
   - Keep minimal frontmatter: `title`, `abbreviation`, `category`
   - Remove all configuration frontmatter (input_path, output_path, triggers, etc.)
   - Keep the prompt body text

3. **Test Configuration**
   ```bash
   ai4pkm --orchestrator-status
   # Should show all agents loaded
   ```

4. **Start Orchestrator**
   ```bash
   ai4pkm -o
   # Test with actual file changes
   ```

---

## Resources

### Documentation

- [New Architecture Blog Post](https://jykim.github.io/AI4PKM/blog/2025/10/30/new-architecture-for-agentic-ai.html) - Overview of orchestrator-agent architecture
- [On-demand Task Processing](https://jykim.github.io/AI4PKM/blog/2025/10/20/on-demand-knowledge-task.html) - Background and evolution
- [GitHub Repository](https://github.com/jykim/AI4PKM) - Source code and issues

### Code Locations

- **Orchestrator Core**: [ai4pkm_cli/orchestrator/](../ai4pkm_cli/orchestrator/)
- **CLI Tool**: [ai4pkm_cli/orchestrator_cli.py](../ai4pkm_cli/orchestrator_cli.py)
- **Configuration**: [ai4pkm_vault/orchestrator.yaml](../ai4pkm_vault/orchestrator.yaml)
- **Example Prompts**: [ai4pkm_vault/_Settings_/Prompts/](../ai4pkm_vault/_Settings_/Prompts/)

### Getting Help

**Check logs:**
```bash
# Execution logs
tail -f _Settings_/Logs/*.log

# Console output shows file monitor events
ai4pkm -o
```

**Report issues:**
- [GitHub Issues](https://github.com/jykim/AI4PKM/issues)

---

*Last Updated: 2025-11-01*
*Version: 1.0 (Nodes-based configuration with orchestrator.yaml)*
