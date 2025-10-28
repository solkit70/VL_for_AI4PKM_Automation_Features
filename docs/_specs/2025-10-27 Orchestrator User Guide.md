---
title: "Orchestrator User Guide - Running the Multi-Agent System"
created: 2025-10-27
tags:
  - orchestrator
  - user-guide
  - cli
  - operations
author:
  - "[[Claude]]"
related:
  - "[[2025-10-25 Orchestrator Detailed Design]]"
  - "[[2025-10-24 KTM to Multi-Agent Migration Plan]]"
  - "[[2025-10-25 Phase 1 - Parallel Implementation]]"
---

# Orchestrator User Guide

## Overview

The Orchestrator is a new multi-agent system that monitors your vault for file changes and automatically triggers configured agents to process content. It runs in parallel with the existing KTM system and uses the same Claude CLI execution pattern.

**Current Status**: Phase 1 Complete ✅
- Core infrastructure implemented (1,451 lines)
- All 47 unit tests passing
- 8 agent definitions created
- CLI tool functional
- Ready for testing and validation

---

## Quick Start

### Check What's Available

```bash
cd /Users/lifidea/dev/AI4PKM
python -m ai4pkm_cli.orchestrator_cli status
```

**Output:**
```
╭─ Orchestrator Status ─────────────╮
│ Vault: /Users/.../ai4pkm_vault    │
│ Agents loaded: 8                  │
│ Max concurrent: 3                 │
╰───────────────────────────────────╯

Available Agents:
  • [HTC] Hashtag Task Creator
    Category: ingestion
  • [EIC] Enrich Ingested Content
    Category: ingestion
  • [ARP] ARP Agent
    Category: research
  ...
```

### Run the Orchestrator

```bash
python -m ai4pkm_cli.orchestrator_cli daemon
```

This starts the orchestrator in daemon mode - it will:
1. Load all agent definitions from `_Settings_/Agents/*.md`
2. Start monitoring vault files for changes
3. Match file events to agent triggers
4. Execute agents automatically when triggers fire
5. Run until you press Ctrl+C

**With custom settings:**
```bash
# Increase concurrent execution limit
python -m ai4pkm_cli.orchestrator_cli daemon --max-concurrent 5
```

---

## How It Works

### Architecture

```
File Change → File Monitor → Agent Registry → Execution Manager → Claude CLI
                    ↓              ↓                  ↓
                Queue Event    Match Triggers    Run in Thread
```

### Components

1. **File Monitor** ([file_monitor.py](../../ai4pkm_cli/orchestrator/file_monitor.py))
   - Uses watchdog to monitor vault files
   - Detects created/modified/deleted events
   - Parses frontmatter from changed files
   - Queues events for processing

2. **Agent Registry** ([agent_registry.py](../../ai4pkm_cli/orchestrator/agent_registry.py))
   - Loads agent definitions from `_Settings_/Agents/*.md`
   - Matches file events to agent triggers
   - Validates agent configurations

3. **Execution Manager** ([execution_manager.py](../../ai4pkm_cli/orchestrator/execution_manager.py))
   - Spawns agent execution in threads
   - Controls concurrency (max 3 by default)
   - Handles timeouts and errors
   - Creates task tracking files
   - Writes execution logs

4. **Orchestrator Core** ([core.py](../../ai4pkm_cli/orchestrator/core.py))
   - Coordinates all components
   - Main event loop
   - Status reporting

---

## Agent Definitions

Agents are defined in Markdown files with YAML frontmatter in `_Settings_/Agents/`.

### Example: Hashtag Task Creator (HTC)

**File**: `_Settings_/Agents/Hashtag Task Creator (HTC).md`

```yaml
---
title: Hashtag Task Creator
abbreviation: HTC
category: ingestion
trigger_pattern: "**/*.md"
trigger_event: modified
trigger_content_pattern: "#AI"
trigger_exclude_pattern: "AI/Tasks/**"
executor: claude_code
max_parallel: 1
timeout_minutes: 10
post_process_action: remove_trigger_content
log_prefix: HTC
log_pattern: "{timestamp}-htc.log"
---

# Hashtag Task Creator

You are a task creator agent that detects #AI hashtags...

[Full prompt body follows]
```

### Trigger Types

**1. File Creation Trigger**
```yaml
trigger_pattern: "Ingest/Clippings/*.md"
trigger_event: created
```
Fires when a new file matching the pattern is created.

**2. File Modification Trigger**
```yaml
trigger_pattern: "**/*.md"
trigger_event: modified
```
Fires when any markdown file is modified.

**3. Content Pattern Trigger**
```yaml
trigger_pattern: "**/*.md"
trigger_event: modified
trigger_content_pattern: "#AI"
```
Fires when file is modified AND contains `#AI` in content.

**4. Exclusion Pattern**
```yaml
trigger_pattern: "**/*.md"
trigger_exclude_pattern: "AI/Tasks/**"
```
Matches pattern but excludes files in `AI/Tasks/` directory.

### Available Agents (Phase 1)

| Abbreviation | Name | Category | Trigger | Description |
|--------------|------|----------|---------|-------------|
| **HTC** | Hashtag Task Creator | ingestion | `#AI` in any .md file | Converts hashtag to task request |
| **EIC** | Enrich Ingested Content | ingestion | New file in Clippings | Improves captured content |
| **ARP** | ARP Agent | research | TBD | Academic research processor |
| **CTP** | CTP Agent | publish | TBD | Content to publish processor |
| **GDR** | GDR Agent | research | TBD | General document research |
| **GES** | GES Agent | research | TBD | General essay synthesizer |
| **PLL** | PLL Agent | research | TBD | Lifelog processor |
| **PPP** | PPP Agent | publish | TBD | Publishing preparation |

---

## CLI Commands

### `status` - Show System Status

```bash
python -m ai4pkm_cli.orchestrator_cli status
```

**Shows:**
- Vault path
- Number of loaded agents
- Max concurrent executions
- List of available agents with categories

**Use when:**
- Checking if agents are configured correctly
- Verifying agent definitions are loaded
- Debugging agent configuration issues

---

### `daemon` - Run Orchestrator

```bash
python -m ai4pkm_cli.orchestrator_cli daemon [OPTIONS]
```

**Options:**
- `--max-concurrent N` or `-m N`: Set maximum concurrent executions (default: 3)

**Example:**
```bash
# Standard mode
python -m ai4pkm_cli.orchestrator_cli daemon

# Higher concurrency for faster processing
python -m ai4pkm_cli.orchestrator_cli daemon -m 5
```

**When running:**
- Press `Ctrl+C` to stop gracefully
- Check logs in `ai4pkm_vault/AI/Tasks/Logs/`
- Task files created in `ai4pkm_vault/AI/Tasks/`

---

## Execution Flow

### Example: Adding #AI Hashtag

**1. User adds `#AI` to a note**
```markdown
# My Research Notes

I need to analyze this #AI

Some content...
```

**2. Orchestrator detects change**
```
File Monitor: detected modified event for "Notes/My Research Notes.md"
Agent Registry: matching against 8 agents...
Agent Registry: matched [HTC] Hashtag Task Creator
```

**3. HTC agent executes**
```
Execution Manager: Starting [HTC] (ID: abc-123)
Execution Manager: Claude CLI: /Users/lifidea/.claude/local/claude
Execution Manager: Executing with 10 minute timeout
```

**4. Task file created**
```
AI/Tasks/2025-10-27 My Research Notes - HTC.md
AI/Tasks/Logs/2025-10-27-171234-htc.log
```

**5. Post-processing**
```
Execution Manager: Post-process action: remove_trigger_content
Removing "#AI" from source file
Execution Manager: [HTC] completed (duration: 45.2s)
```

---

## Logs and Output

### Task Tracking Files

**Location**: `ai4pkm_vault/AI/Tasks/`

**Format**:
```yaml
---
title: "My Research Notes - HTC"
created: 2025-10-27T17:12:34
agent: HTC
execution_id: abc-123
status: PENDING
priority: medium
source_file: "[[Notes/My Research Notes]]"
---

# Task: Process Research Notes

[Agent's response/output here]
```

### Execution Logs

**Location**: `ai4pkm_vault/AI/Tasks/Logs/`

**Naming**: `{timestamp}-{agent}.log`

**Content**:
```markdown
# Execution Log: HTC
# Start: 2025-10-27T17:12:34
# Execution ID: abc-123

## Prompt

[Full prompt sent to Claude]

## Response

[Claude's complete response]
```

---

## Concurrency Control

### Global Limit

**Default**: 3 concurrent executions across all agents

Controls total system load:
```bash
daemon --max-concurrent 3  # Conservative
daemon --max-concurrent 5  # Moderate
daemon --max-concurrent 10 # Aggressive
```

### Per-Agent Limit

**Defined in agent frontmatter:**
```yaml
max_parallel: 1  # Only one instance of this agent at a time
```

**Example**:
- HTC has `max_parallel: 1` - prevents duplicate task creation
- EIC has `max_parallel: 2` - can process 2 clippings simultaneously

### Execution States

**Queued** → Waiting for available slot
**Running** → Currently executing
**Completed** → Finished successfully
**Failed** → Error occurred
**Timeout** → Exceeded timeout limit

---

## Differences from KTM

| Aspect | KTM (Legacy) | Orchestrator (New) |
|--------|--------------|-------------------|
| **Architecture** | Hardcoded handlers | Config-driven agents |
| **Agents** | Python classes | Markdown definitions |
| **Triggers** | Handler registration | Pattern matching |
| **Execution** | Mixed (SDK/CLI) | CLI only |
| **Concurrency** | Global semaphore | Per-agent + global limits |
| **Status** | No visibility | Status command |
| **Testing** | Limited | 47 unit tests |

---

## Troubleshooting

### No Agents Loaded

**Symptom**: `status` shows "Agents loaded: 0"

**Check:**
1. Agent directory exists: `_Settings_/Agents/`
2. Files have `.md` extension
3. Valid YAML frontmatter with required fields
4. Check orchestrator logs for parsing errors

**Required fields:**
```yaml
title: "Agent Name"
abbreviation: "ABC"
category: "ingestion|research|publish"
trigger_pattern: "**/*.md"
trigger_event: "created|modified"
```

### Agent Not Triggering

**Symptom**: File changes but agent doesn't execute

**Debug steps:**
1. Check trigger pattern matches file path
2. Verify trigger event type (created vs modified)
3. Check exclusion patterns
4. Look for content pattern requirements
5. Review file monitor logs

**Example debug:**
```bash
# Run with verbose logging
python -m ai4pkm_cli.orchestrator_cli daemon

# Watch for:
# "Agent Registry: matched [ABC] Agent Name" ✓
# "No agents match event: path/to/file.md" ✗
```

### Claude CLI Not Found

**Symptom**: `RuntimeError: Claude CLI not found`

**Fix:**
1. Verify Claude installed: `which claude`
2. Check location: `~/.claude/local/claude`
3. Or set custom path in execution_manager.py

**Claude CLI discovery order:**
1. `~/.claude/local/claude` (user installation)
2. `which claude` (PATH lookup)
3. `/usr/local/bin/claude` (global installation)
4. `~/node_modules/.bin/claude` (local npm)

### Execution Timeout

**Symptom**: Task marked as `timeout` status

**Solutions:**
1. Increase timeout in agent definition:
   ```yaml
   timeout_minutes: 30  # Increase from default 10
   ```
2. Reduce prompt complexity
3. Process in chunks if content is large

---

## Testing the Orchestrator

### Unit Tests (All Passing ✅)

```bash
# Run all orchestrator tests
python -m pytest ai4pkm_cli/tests/unit/orchestrator/ -v

# Results: 47 passed in 5.84s
```

**Test Coverage:**
- Agent loading and validation
- Trigger pattern matching
- Event queue processing
- Concurrency control
- Timeout and error handling
- Task file creation
- Log file generation

### Manual Testing

**Test 1: Hashtag Detection**
```bash
# Start orchestrator
python -m ai4pkm_cli.orchestrator_cli daemon

# In another terminal, create test file
echo "Test content #AI" > ai4pkm_vault/test.md

# Expected: HTC agent triggers and creates task file
```

**Test 2: Content Ingestion**
```bash
# Create clipping
echo "---\ntitle: Test\n---\nContent" > ai4pkm_vault/Ingest/Clippings/test.md

# Expected: EIC agent triggers if configured
```

---

## Next Steps

### Immediate (Phase 1 Completion)

1. **Create Integration Test**
   - End-to-end test with real vault
   - Verify file → trigger → execution → output
   - Location: `ai4pkm_cli/tests/integration/test_orchestrator_integration.py`

2. **Validate Agent Definitions**
   - Review 8 existing agent configs
   - Test each agent's trigger pattern
   - Verify prompts are complete

3. **Documentation Review**
   - User guide (this doc)
   - Developer guide for creating agents
   - Migration guide from KTM

### Future (Phase 2)

1. **Convert KTM Agents**
   - KTG (Knowledge Task Generator)
   - KTP-Exec (Task Processor)
   - KTP-Eval (Task Evaluator)

2. **Dual-Mode Operation**
   - Run both KTM and Orchestrator
   - Compare outputs
   - Gradual migration

3. **Advanced Features**
   - Skills library integration
   - Workflow chains
   - Conditional execution
   - Status dashboard

---

## Resources

### Code Locations

- **Orchestrator Core**: [ai4pkm_cli/orchestrator/](../../ai4pkm_cli/orchestrator/)
- **CLI Tool**: [ai4pkm_cli/orchestrator_cli.py](../../ai4pkm_cli/orchestrator_cli.py)
- **Agent Definitions**: [ai4pkm_vault/_Settings_/Agents/](../../ai4pkm_vault/_Settings_/Agents/)
- **Tests**: [ai4pkm_cli/tests/unit/orchestrator/](../../ai4pkm_cli/tests/unit/orchestrator/)

### Related Documents

- [[2025-10-25 Orchestrator Detailed Design]] - Technical architecture
- [[2025-10-24 KTM to Multi-Agent Migration Plan]] - Overall migration strategy
- [[2025-10-25 Phase 1 - Parallel Implementation]] - Implementation plan

### Getting Help

**Check logs:**
```bash
# Orchestrator logs (application level)
tail -f ai4pkm_vault/AI/Tasks/Logs/*.log

# System logs (file monitor events)
# Shown in console when running daemon
```

**Debug mode:**
```python
# In orchestrator_cli.py, add:
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

*Last Updated: 2025-10-27*
*Status: Phase 1 Complete - Ready for Testing*
