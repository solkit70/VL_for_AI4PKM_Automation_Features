---
title: "Migration Plan: KTM to Generalized Multi-Agent Architecture"
created: 2025-10-24
tags:
  - architecture
  - migration
  - multi-agent
  - orchestrator
author:
  - "[[Claude]]"
---

# Migration Plan: KTM to Generalized Multi-Agent Architecture

## Executive Summary

The current KTM system already implements a multi-agent architecture with file-based communication. This migration will **refactor and generalize** the existing components into a cleaner framework while preserving all current functionality.

## Current State Analysis

### Existing KTM Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    CURRENT KTM SYSTEM                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  File Watchdog (Orchestrator-like)                               │
│  ├─ Pattern-based handler registration                          │
│  ├─ Event routing to handlers                                   │
│  ├─ Concurrency control (semaphore)                             │
│  └─ Multi-status startup detection                              │
│                                                                   │
│  Specialized Agents (Task-level)                                │
│  ├─ KTG (Generator): Request → Task File                        │
│  ├─ KTP-Exec (Processor): Task → Output                         │
│  └─ KTP-Eval (Evaluator): Output → Quality Check                │
│                                                                   │
│  Source Handlers (Detection)                                    │
│  ├─ HashtagFileHandler                                          │
│  ├─ ClippingFileHandler                                         │
│  ├─ LimitlessFileHandler                                        │
│  └─ GobiFileHandler                                             │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### How KTM Maps to General Agent Framework

```
┌──────────────────────────────────────────────────────────────────┐
│              MAPPING: KTM → GENERAL AGENT FRAMEWORK               │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│  KTM Component          →    General Framework Component         │
│  ═════════════════════       ══════════════════════════          │
│                                                                    │
│  KTG Agent              →    Agent (Type: Generator)             │
│  │ Input: Request JSON        Input Files: AI/Tasks/Requests/    │
│  │ Process: KTG.md            Process: Prompt Template           │
│  │ Output: Task MD            Output Files: AI/Tasks/*.md        │
│  └─ Thread logging            Skill Library: Task validation     │
│                                                                    │
│  KTP-Exec Agent         →    Agent (Type: Executor)              │
│  │ Input: Task MD (TBD)       Input Files: AI/Tasks/*.md         │
│  │ Process: KTP.md            Process: Prompt Template           │
│  │ Output: Content files      Output Files: Various locations    │
│  └─ Status: PROCESSED         MCP Servers: File operations       │
│                                                                    │
│  KTP-Eval Agent         →    Agent (Type: Evaluator)             │
│  │ Input: Task + Output       Input Files: Task + outputs        │
│  │ Process: KTE.md            Process: Prompt Template           │
│  │ Output: Status update      Output Files: Updated task         │
│  └─ Status: COMPLETED/FAILED  Skill Library: Validation          │
│                                                                    │
│  File Watchdog          →    Orchestrator Core                   │
│  │ Pattern handlers           Input monitoring rules             │
│  │ Event routing              Agent spawning logic               │
│  │ Semaphore                  Concurrency control                │
│  │ Status detection           Task state management              │
│  └─ Handler chain             Agent workflow coordination        │
│                                                                    │
│  Source Handlers        →    Input Detection Agents              │
│  │ Hashtag/Clipping           Specialized input processors       │
│  │ Pattern matching           Trigger condition logic            │
│  └─ Request creation          Agent invocation                   │
│                                                                    │
└──────────────────────────────────────────────────────────────────┘
```

## Visual Architecture Comparison

### Current KTM Flow (Specific)

```
┌─────────────────────────────────────────────────────────────────┐
│                    CURRENT: TASK-SPECIFIC FLOW                   │
└─────────────────────────────────────────────────────────────────┘

Source File Change
      │
      ▼
┌─────────────┐
│  Hashtag    │ (Handler detects #AI)
│  Handler    │ Creates request JSON
└──────┬──────┘
       │
       ▼ Request file created
┌─────────────────────┐
│ TaskRequestFile     │ (Handler detects .json)
│ Handler             │ Spawns KTG agent
└──────┬──────────────┘
       │
       ▼ Acquire semaphore
┌─────────────────────┐        ┌──────────────┐
│  KTG Agent          │───────▶│ Thread Log   │
│  Input: Request     │        │ YYYY-MM-DD-  │
│  Process: KTG.md    │        │ ms-gen.log   │
│  Output: Task.md    │        └──────────────┘
└──────┬──────────────┘
       │ Creates task with status=TBD
       ▼
┌─────────────────────┐
│ TaskProcessor       │ (Handler detects status=TBD)
│ Handler             │ Spawns KTP-Exec agent
└──────┬──────────────┘
       │
       ▼ Phase 1 & 2
┌─────────────────────┐        ┌──────────────┐
│ KTP-Exec Agent      │───────▶│ Thread Log   │
│ Input: Task.md      │        │ TaskName-    │
│ Process: KTP.md     │        │ exec.log     │
│ Output: Content     │        └──────────────┘
│ Status → PROCESSED  │
└──────┬──────────────┘
       │
       ▼ Status changed to PROCESSED
┌─────────────────────┐
│ TaskEvaluator       │ (Handler detects status=PROCESSED)
│ Handler             │ Spawns KTP-Eval agent
└──────┬──────────────┘
       │
       ▼ Phase 3
┌─────────────────────┐        ┌──────────────┐
│ KTP-Eval Agent      │───────▶│ Thread Log   │
│ Input: Task+Output  │        │ TaskName-    │
│ Process: KTE.md     │        │ eval.log     │
│ Output: Status      │        └──────────────┘
│ Status → COMPLETED  │
└─────────────────────┘
```

### Target: Generalized Multi-Agent Flow

**Key Design Decision**: The file system serves as the unified state database. Input Monitor and State Manager are combined into a single **File System Monitor** that tracks all file changes (input files, task files with status, output files). The current task file schema (with frontmatter status field) is reused with minor extensions for agent metadata.

```
┌─────────────────────────────────────────────────────────────────┐
│              TARGET: GENERALIZED MULTI-AGENT FLOW                │
└─────────────────────────────────────────────────────────────────┘

                    ┌──────────────────────────┐
                    │     ORCHESTRATOR         │
                    │  (Unified Coordinator)   │
                    └───────────┬──────────────┘
                                │
                    ┌───────────┴──────────────┐
                    │  Core Responsibilities:  │
                    │  • File system monitoring│
                    │  • Agent spawning        │
                    │  • Workflow management   │
                    │  • User interaction      │
                    └───────────┬──────────────┘
                                │
                ┌───────────────┴───────────────┐
                │                               │
                ▼                               ▼
        ┌───────────────┐            ┌───────────────┐
        │ File System   │            │ Agent Manager │
        │ Monitor       │            │               │
        │               │            │ • Load agents │
        │ • Watch files │            │ • Spawn agent │
        │ • Patterns    │            │ • Route work  │
        │ • Events      │            │ • Monitor     │
        │ • State from  │            └───────┬───────┘
        │   frontmatter │                    │
        └───────┬───────┘                    │
                │                            │
                │ Detects change & triggers  │
                └───────────────────────────▶│
                                             │ Spawns agent
                                             ▼
                                  ┌─────────────────────┐
                                  │   AGENT TEMPLATE    │
                                  │   (Generalized)     │
                                  └──────────┬──────────┘
                                             │
        ┌────────────────────────────────────┼──────────────────┐
        │                                    │                  │
        ▼                                    ▼                  ▼
┌──────────────┐                    ┌──────────────┐   ┌──────────────┐
│ Input Files  │                    │   Process    │   │ Output Files │
│              │                    │              │   │              │
│ • Spec       │───────────────────▶│ • Prompt     │──▶│ • Spec       │
│ • Validation │                    │ • Skills     │   │ • Validation │
└──────────────┘                    │ • MCP        │   └──────┬───────┘
                                    └──────────────┘          │
                                                              │ Updates
                                                              │ status in
                                                              │ frontmatter
                                                              ▼
                                                   ┌─────────────────┐
                                                   │  Task File      │
                                                   │  (status: X)    │
                                                   └────────┬────────┘
                                                            │
                               ┌────────────────────────────┘
                               │ File System Monitor detects
                               ▼
                     ┌─────────────────┐
                     │  ORCHESTRATOR   │
                     │  (Next action)  │
                     └─────────────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
     ┌────────────┐   ┌────────────┐  ┌────────────┐
     │ Spawn next │   │   Report   │  │  Improve   │
     │   agent    │   │   status   │  │   system   │
     └────────────┘   └────────────┘  └────────────┘
```

## Detailed Agent Design

Based on existing prompts in `_Settings_/Prompts/` and workflows, agents follow a consistent **Input → Process → Output** pattern.

### Input Specification

Agents can be triggered by two types of events:

**1. File Creation Triggers** (e.g., new input files)
- New clipping in `Ingest/Clippings/`
- New request JSON in `AI/Tasks/Requests/`
- New lifelog entry in `Limitless/` or `Gobi/`

**2. File Modification Triggers** (e.g., status changes)
- Task status change: `TBD` → triggers Processor
- Task status change: `PROCESSED` → triggers Evaluator
- Hashtag addition: `#AI` detected → triggers request generation

**Common Input Patterns** (from existing prompts):

```yaml
# Pattern 1: File creation with glob pattern
input:
  trigger:
    event_type: created
    pattern: "Ingest/Clippings/*.md"

# Pattern 2: Status-based trigger
input:
  trigger:
    event_type: modified
    status_field: status
    status_value: TBD
    pattern: "AI/Tasks/*.md"

# Pattern 3: Content-based trigger (hashtag detection)
input:
  trigger:
    event_type: modified
    content_match: "#AI"
    pattern: "**/*.md"
```

### Process Specification

The process is defined entirely in the **prompt body** (Markdown content). Based on existing prompts:

**Key Process Patterns**:
1. **Generation** (KTG, DIR, CKU): Create new structured content
2. **Transformation** (EIC, ICT): Enhance/restructure existing content
3. **Evaluation** (KTE): Validate outputs and determine next steps
4. **Aggregation** (WRP, Roundup): Collect and synthesize information

**Process Requirements**:
- Clear step-by-step instructions
- Input format specifications
- Output format specifications
- Error handling guidance
- Quality criteria

### Output Specification

Outputs define what the agent produces and how state transitions occur.

**Common Output Patterns** (from existing workflows):

```yaml
# Pattern 1: Create new file with status
output:
  files:
    - pattern: "AI/Tasks/YYYY-MM-DD {title}.md"
      template: task_template
  status_update:
    property: status
    value: TBD

# Pattern 2: Modify existing file, update status
output:
  status_update:
    property: status
    value: PROCESSED

# Pattern 3: Create multiple files (e.g., roundup + topic updates)
output:
  files:
    - pattern: "AI/Roundup/YYYY-MM-DD.md"
    - pattern: "Topics/**/*.md"  # Multiple files updated
```

## Skills Architecture

A key insight from analyzing existing prompts is that many operations are **reusable across multiple agents**. Rather than duplicating logic in each agent's prompt, we extract these capabilities into a **Skill Library**.

### What are Skills?

Skills are reusable, composable functions that agents can invoke during processing. Each skill encapsulates a specific capability that can be combined with other skills to accomplish complex tasks.

**Examples from Existing Prompts**:
- **Wiki Link Validation**: Check if `[[links]]` point to existing files
- **Topic Update**: Add entry to relevant topic file
- **Frontmatter Parsing**: Extract YAML properties from markdown
- **Duplicate Detection**: Check if similar content already exists
- **Publishing Format**: Convert content to Substack/Thread/LinkedIn format

### Domain-Specific Skill Categories

Based on existing prompts in `_Settings_/Prompts/`, skills are organized into four domains:

#### 📥 Content Collection Skills
**Purpose**: Process incoming content from various sources

- `parse_clipping`: Extract metadata from web clippings
- `parse_limitless`: Process Limitless lifelog entries
- `parse_photolog`: Extract and organize photo metadata
- `detect_hashtags`: Identify hashtags for task routing
- `extract_quotes`: Pull significant quotes from content

#### 📤 Publishing Skills
**Purpose**: Format content for different publishing channels

- `format_for_substack`: Convert to Substack newsletter format
- `format_for_thread`: Create threaded posts for X/Twitter
- `format_for_linkedin`: Format for LinkedIn article
- `optimize_for_mobile`: Ensure mobile-friendly formatting
- `generate_excerpt`: Create compelling summaries

#### 🗂️ Knowledge Organization Skills
**Purpose**: Maintain and update knowledge structure

- `update_topic_index`: Add entries to topic files
- `validate_wiki_links`: Ensure all `[[links]]` are valid
- `detect_duplicates`: Find similar existing content
- `suggest_topics`: Recommend relevant topic assignments
- `update_backlinks`: Maintain bidirectional link integrity
- `create_roundup_entry`: Add to daily/weekly roundup

#### 📝 Obsidian Rules Skills
**Purpose**: Enforce vault conventions and standards

- `validate_frontmatter`: Check required properties
- `enforce_link_format`: Use full filename in wiki links
- `check_folder_structure`: Validate file placement
- `apply_naming_convention`: Ensure consistent file naming
- `validate_property_types`: Check YAML property types

### Skill Definition Format
%% Skills are defined in md document with python library
https://www.anthropic.com/news/skills
 %%
Skills are defined as Python modules with standard interface:

**Example: `_Settings_/Skills/validate_wiki_links.py`**

```python
from typing import List, Dict
from pathlib import Path

class ValidateWikiLinksSkill:
    """Validate that all wiki links point to existing files"""

    def __init__(self, vault_path: Path):
        self.vault_path = vault_path

    def execute(self, content: str) -> Dict:
        """
        Args:
            content: Markdown content to validate

        Returns:
            {
                'valid': bool,
                'broken_links': List[str],
                'suggestions': Dict[str, List[str]]
            }
        """
        broken_links = []
        suggestions = {}

        # Extract all [[wiki links]]
        links = self.extract_wiki_links(content)

        # Check each link
        for link in links:
            if not self.link_exists(link):
                broken_links.append(link)
                suggestions[link] = self.find_similar_files(link)

        return {
            'valid': len(broken_links) == 0,
            'broken_links': broken_links,
            'suggestions': suggestions
        }
```

### Skill Loading in Agents

Agents declare required skills in their frontmatter:

```yaml
---
name: Knowledge Task Processor
skills: ["validate_wiki_links", "update_topic_index", "create_roundup_entry"]
---
```

The Agent Manager loads these skills and makes them available during execution:

```python
class AgentManager:
    def execute_agent(self, agent_def: AgentDefinition, input_file: str):
        # Load required skills
        skills = self.skill_library.load_skills(agent_def.skills)

        # Make skills available to agent
        context = {
            'input_file': input_file,
            'skills': skills,
            'vault_path': self.vault_path
        }

        # Execute agent with skills
        result = self.execute_with_skills(agent_def, context)
```

### Skill Extraction Strategy

**Phase 1**: Identify reusable patterns in existing prompts
- Analyze all prompts in `_Settings_/Prompts/`
- Find duplicated logic across prompts
- Extract common operations

**Phase 2**: Create skill modules
- Implement each skill with standard interface
- Add comprehensive error handling
- Include usage examples and tests

**Phase 3**: Refactor agent prompts
- Replace duplicated logic with skill calls
- Simplify agent prompts
- Document skill dependencies

## Detailed Orchestrator Design

### File System Monitor

**Responsibilities**:
1. **Watch entire vault** for file system events (create, modify, delete)
2. **Parse frontmatter** to extract status and metadata
3. **Match events to agent triggers** using pattern matching and status checks
4. **Queue agent invocations** based on trigger matches
5. **Prevent duplicate triggers** during startup (multi-status detection)

**Implementation** (reuses existing FileWatchdog):

```python
class FileSystemMonitor:
    def __init__(self, agents_dir: str):
        self.agent_definitions = self.load_all_agents(agents_dir)
        self.watchdog = FileWatchdogHandler()

    def on_file_event(self, event):
        # Parse frontmatter to get current state
        frontmatter = self.parse_frontmatter(event.file_path)

        # Find matching agent triggers
        for agent in self.agent_definitions:
            if self.matches_trigger(event, frontmatter, agent.trigger):
                self.queue_agent(agent, event.file_path)

    def matches_trigger(self, event, frontmatter, trigger):
        # Check event type (created/modified)
        # Check file pattern match
        # Check status field match (if applicable)
        # Check content match (if applicable)
        return all_conditions_met
```

### Agent Manager

**Responsibilities**:
1. **Load agent definitions** from `_Settings_/Agents/`
2. **Spawn agent processes** with proper isolation (threads/processes)
3. **Monitor execution**: track time, resources, completion
4. **Manage concurrency**: use semaphore to limit parallel agents
5. **Collect metrics**: execution time, success/failure rates

**Execution Monitoring**:

```python
class AgentManager:
    def spawn_agent(self, agent_def: AgentDefinition, input_file: str):
        # Setup logging
        log_file = self.create_log_file(agent_def.logging)

        # Track execution metrics
        start_time = time.time()

        # Spawn agent (via AgentFactory)
        result = self.agent_factory.create_agent(
            executor=agent_def.executor,
            prompt=agent_def.prompt_body,
            input_file=input_file
        )

        # Record metrics
        execution_time = time.time() - start_time
        self.metrics.record({
            'agent': agent_def.name,
            'duration': execution_time,
            'status': result.status,
            'timestamp': datetime.now()
        })

        return result
```

### System Improvement Loop

**Key Principle**: The orchestrator continuously learns from execution data to improve both **agent definitions** and **skill implementations**. This creates a self-improving system that gets better over time.

**Responsibilities**:
1. **Collect performance data**: execution times, failure rates, user feedback
2. **Analyze patterns**: identify bottlenecks, common failures, skill inefficiencies
3. **Generate improvement suggestions**:
   - Agent prompt refinements
   - Skill implementation optimizations
   - Workflow adjustments
4. **Auto-update where safe**: configuration tweaks, retry logic, skill parameters
5. **Request user review**: for significant changes to agent/skill definitions

**Improvement Targets**:

1. **Agent Definitions** (`_Settings_/Agents/*.md`)
   - Prompt clarity and specificity
   - Trigger condition accuracy
   - Output specification completeness
   - Error handling instructions

2. **Skill Definitions** (`_Settings_/Skills/*.py`)
   - Skill performance optimization
   - Error handling robustness
   - Skill parameter tuning
   - Skill composition patterns

3. **Workflow Orchestration**
   - Agent sequencing optimization
   - Parallel execution opportunities
   - Retry strategies
   - Resource allocation

**Continuous Improvement Flow**:

```
┌─────────────────────────────────────────────────────────────────┐
│              CONTINUOUS IMPROVEMENT LOOP                         │
└─────────────────────────────────────────────────────────────────┘

  ┌──────────────┐
  │ Agent/Skill  │
  │  Execution   │
  └──────┬───────┘
         │ Collect metrics
         ▼
  ┌──────────────┐         ┌──────────────┐
  │   Metrics    │────────▶│   Analysis   │
  │  Database    │         │    Engine    │
  └──────────────┘         └──────┬───────┘
                                  │ Identify patterns
                                  ▼
                           ┌──────────────┐
                           │  Improvement │
                           │ Suggestions  │
                           └──────┬───────┘
                                  │
                  ┌───────────────┼───────────────┐
                  │               │               │
                  ▼               ▼               ▼
          ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
          │ Agent Prompt │ │ Skill Code   │ │ Workflow     │
          │ Refinement   │ │ Optimization │ │ Adjustment   │
          └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
                 │                │                │
                 └────────────────┼────────────────┘
                                  │ Apply changes
                                  ▼
                           ┌──────────────┐
                           │   Updated    │
                           │  Definitions │
                           └──────┬───────┘
                                  │
                                  └─────────┐
                                           │ Next execution
                                           ▼
                                    (Loop continues)
```

**Weekly System Review Process**:

```yaml
# Workflow: Weekly System Review
name: System Performance Review and Improvement
trigger_schedule: weekly

process:
  1. Collect Metrics:
     - Agent execution times and success rates
     - Skill usage frequency and performance
     - Error patterns and failure modes
     - User feedback and manual interventions

  2. Analyze Performance:
     - Identify slowest agents (> 2 std dev from mean)
     - Find highest failure rate agents (> 10% failure)
     - Detect underutilized or redundant skills
     - Spot workflow bottlenecks

  3. Generate Improvement Recommendations:
     a) Agent Improvements:
        - Simplify overly complex prompts
        - Add missing error handling instructions
        - Clarify ambiguous specifications
        - Optimize trigger conditions

     b) Skill Improvements:
        - Optimize slow skill implementations
        - Enhance error handling in fragile skills
        - Combine frequently co-used skills
        - Extract new skills from repeated patterns

     c) Workflow Improvements:
        - Parallelize independent agent executions
        - Adjust concurrency limits
        - Optimize retry strategies

  4. Implement Safe Changes:
     - Auto-apply: parameter tuning, retry logic
     - Request review: prompt changes, skill refactoring

output:
  file: "AI/System/YYYY-MM-DD System Review.md"
  includes:
    - Performance summary with metrics
    - Issue analysis with root causes
    - Recommended changes to agents/skills
    - Auto-applied optimizations log
    - Changes pending user review
```

**Example Improvement Cycle**:

```
Week 1: Detection
- KTP-Exec agent has 20% failure rate
- Common error: "Invalid wiki link format"
- Pattern: Links missing file extension

Week 2: Analysis
- Root cause: Agent prompt unclear about link format
- Skill gap: No wiki link formatter available

Week 3: Implementation
- Update KTP-Exec prompt: Add explicit link format instructions
- Create new skill: `format_wiki_link`
- Add skill to KTP-Exec dependencies

Week 4: Validation
- KTP-Exec failure rate drops to 3%
- Wiki link errors eliminated
- New skill reused by 3 other agents
```

## Detailed Component Migration

### 1. Agent Template (Generalized)

**Current Implementation:** Three distinct agent types (KTG, KTP-Exec, KTP-Eval)

**Target:** Unified agent interface with configurable behavior

**Key Design Decision**: There is no hardcoded "agent_type" field. Each agent is simply defined by its prompt template which specifies input requirements, processing logic, and output expectations. The prompt itself is the agent definition.

**Important**: Frontmatter properties use flat structure (no nesting) for Obsidian compatibility. Complex configurations are stored as JSON strings or separate fields.

```
┌─────────────────────────────────────────────────────────────────┐
│                    AGENT TEMPLATE STRUCTURE                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌────────────────┐                                              │
│  │  Agent Config  │  (Markdown file with YAML frontmatter)      │
│  └────────┬───────┘                                              │
│           │                                                       │
│  ┌────────▼─────────────────────────────────────────┐           │
│  │  ---                                              │           │
│  │  name: Knowledge Task Generator                  │           │
│  │  trigger_pattern: "AI/Tasks/Requests/*/*.json"   │           │
│  │  trigger_event: created                          │           │
│  │  output_pattern: "AI/Tasks/*.md"                 │           │
│  │  output_status: TBD                              │           │
│  │  log_prefix: KTG                                 │           │
│  │  log_pattern: "{timestamp}-gen.log"              │           │
│  │  skills: ["task_validation", "duplicate_detection"]          │
│  │  executor: claude_code                            │           │
│  │  ---                                              │           │
│  │                                                    │           │
│  │  # Agent Prompt (defines behavior)                │           │
│  │                                                    │           │
│  │  You are a Knowledge Task Generator...            │           │
│  │  [Full prompt defining input/process/output]      │           │
│  └────────────────────────────────────────────────────┘           │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

**Migration of Existing Agents:**

Each agent is defined as a **Markdown file with YAML frontmatter** (similar to task files). This allows prompts to be version-controlled, human-readable, and easily modified.

**Obsidian Compatibility**: All properties use flat structure (no nesting). Arrays and complex data use JSON arrays or separate flat fields with naming conventions (e.g., `trigger_pattern`, `trigger_event` instead of nested `trigger.pattern`, `trigger.event`).

**Example: `_Settings_/Agents/Knowledge Task Generator.md`**

```markdown
---
name: Knowledge Task Generator
trigger_pattern: "AI/Tasks/Requests/*/*.json"
trigger_event: created
output_pattern: "AI/Tasks/YYYY-MM-DD *.md"
output_status: TBD
log_prefix: KTG
log_pattern: "{timestamp}-gen.log"
skills: ["task_validation", "duplicate_detection"]
executor: claude_code
---

# Knowledge Task Generator (KTG)

You are a Knowledge Task Generator agent. Your role is to...

## Input Requirements
- Read request JSON from `AI/Tasks/Requests/`
- Extract task parameters...

## Processing Steps
1. Validate request format
2. Check for duplicate tasks
3. Generate task file with proper frontmatter

## Output Specification
Create a task file in `AI/Tasks/` with:
- Filename: `YYYY-MM-DD Task Name.md`
- Status: `TBD`
- [Full task template specification]
```

**Example: `_Settings_/Agents/Knowledge Task Processor.md`**

```markdown
---
name: Knowledge Task Processor
trigger_pattern: "AI/Tasks/*.md"
trigger_event: modified
trigger_status_field: status
trigger_status_value: TBD
output_status: PROCESSED
log_prefix: KTP-exec
log_pattern: "{task_name}-exec.log"
skills: ["file_operations"]
executor_mapping: '{"EIC": "claude_code", "Research": "gemini_cli", "default": "claude_code"}'
---

# Knowledge Task Processor (KTP)

You are a Knowledge Task Processor agent. Your role is to execute tasks...

## Input Requirements
- Task file with status=TBD
- Read task parameters from frontmatter

## Processing Steps
[Full execution logic from current KTP.md prompt]

## Output Specification
- Update task status to PROCESSED
- Create output files as specified in task
```

**Example: `_Settings_/Agents/Knowledge Task Evaluator.md`**

```markdown
---
name: Knowledge Task Evaluator
trigger_pattern: "AI/Tasks/*.md"
trigger_event: modified
trigger_status_field: status
trigger_status_value: PROCESSED
output_status_values: ["COMPLETED", "FAILED"]
output_status_agent_determined: true
log_prefix: KTP-eval
log_pattern: "{task_name}-eval.log"
skills: ["file_validation", "quality_check"]
executor: claude_code
---

# Knowledge Task Evaluator (KTE)

You are a Knowledge Task Evaluator agent. Your role is to validate task outputs...

## Input Requirements
- Task file with status=PROCESSED
- Access to all generated output files

## Processing Steps
[Full evaluation logic from current KTE.md prompt]

## Output Specification
- Update task status to COMPLETED or FAILED
- Document evaluation results in task file
```

### 2. Orchestrator Architecture

**Current:** File Watchdog + Handler Chain

**Target:** Unified Orchestrator with clear responsibilities

**Key Design Decision**: Input Monitor and State Manager are combined into a single **File System Monitor** component since the file system itself is the state database (via frontmatter status fields).

```
┌─────────────────────────────────────────────────────────────────┐
│                   ORCHESTRATOR ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                  ORCHESTRATOR CORE                        │   │
│  │                                                            │   │
│  │  Responsibilities:                                        │   │
│  │  1. Monitor file system for changes (input & state)      │   │
│  │  2. Match changes to agent triggers                      │   │
│  │  3. Spawn appropriate agents                             │   │
│  │  4. Manage workflow transitions                          │   │
│  │  5. Report status to user                                │   │
│  │  6. Collect feedback and improve                         │   │
│  └───────┬──────────────────────────────────────────────────┘   │
│          │                                                        │
│  ┌───────┴────────────────────────────────────────────────┐     │
│  │                                                          │     │
│  │  Components (Reuse from KTM):                           │     │
│  │                                                          │     │
│  │  ┌────────────────────────────────────────────────┐    │     │
│  │  │  1. File System Monitor                         │    │     │
│  │  │     (Reuse: FileWatchdogHandler + Status)      │    │     │
│  │  │                                                 │    │     │
│  │  │     • Pattern-based file watching              │    │     │
│  │  │     • Event deduplication                      │    │     │
│  │  │     • Exclusion rules                          │    │     │
│  │  │     • Read status from frontmatter             │    │     │
│  │  │     • Detect status transitions                │    │     │
│  │  │     • Startup detection                        │    │     │
│  │  └────────────────────────────────────────────────┘    │     │
│  │                                                          │     │
│  │  ┌────────────────────────────────────────────────┐    │     │
│  │  │  2. Agent Manager                               │    │     │
│  │  │     (Reuse: Handler process() + AgentFactory)  │    │     │
│  │  │                                                 │    │     │
│  │  │     • Load agent definitions (Markdown files)  │    │     │
│  │  │     • Match triggers to events                 │    │     │
│  │  │     • Spawn agent threads                      │    │     │
│  │  │     • Manage concurrency (semaphore)           │    │     │
│  │  └────────────────────────────────────────────────┘    │     │
│  │                                                          │     │
│  │  ┌────────────────────────────────────────────────┐    │     │
│  │  │  3. Workflow Coordinator                        │    │     │
│  │  │     (NEW - generalize 3-phase KTP)             │    │     │
│  │  │                                                 │    │     │
│  │  │     • Define agent chains                      │    │     │
│  │  │     • Manage transitions                       │    │     │
│  │  │     • Handle retries                           │    │     │
│  │  └────────────────────────────────────────────────┘    │     │
│  │                                                          │     │
│  │  ┌────────────────────────────────────────────────┐    │     │
│  │  │  4. User Interface                              │    │     │
│  │  │     (NEW - expand logging)                     │    │     │
│  │  │                                                 │    │     │
│  │  │     • Status reporting                         │    │     │
│  │  │     • Feedback collection                      │    │     │
│  │  │     • System diagnostics                       │    │     │
│  │  └────────────────────────────────────────────────┘    │     │
│  │                                                          │     │
│  └──────────────────────────────────────────────────────────┘     │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 3. Task File Schema (State Storage)

**Key Design Decision**: The file system serves as the state database. Task files with frontmatter properties store all state information, eliminating the need for a separate state database.

**Current Task File Schema** (reused with minor extensions):

```yaml
---
title: "EIC for Article X"
created: 2025-10-24
status: TBD  # State field: TBD → IN_PROGRESS → PROCESSED → UNDER_REVIEW → COMPLETED/FAILED
task_type: EIC
source_file: "[[Ingest/Clippings/2025-10-24 Article X]]"

# Optional: Agent execution metadata (NEW)
agent_history:
  - agent: Knowledge Task Generator
    timestamp: 2025-10-24T10:30:00
    status: COMPLETED
  - agent: Knowledge Task Processor
    timestamp: 2025-10-24T10:35:00
    status: IN_PROGRESS
---

# Task Content
[Task description and requirements]
```

**Benefits of File-Based State**:
- No separate database to maintain
- State is version-controlled with git
- Human-readable and editable
- Already implemented in current KTM
- File system events trigger state transitions automatically

### 4. Component Reuse Strategy

```
┌─────────────────────────────────────────────────────────────────┐
│               COMPONENT REUSE: KTM → GENERAL FRAMEWORK           │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  REUSE AS-IS (95% ready):                                        │
│  ━━━━━━━━━━━━━━━━━━━━━━━                                        │
│                                                                   │
│  ✓ FileWatchdogHandler                                           │
│    [ai4pkm_cli/watchdog/file_watchdog.py]                       │
│    → Becomes: Orchestrator.FileSystemMonitor                    │
│    Changes: Add frontmatter parsing to extract status           │
│                                                                   │
│  ✓ Task Semaphore                                                │
│    [ai4pkm_cli/watchdog/task_semaphore.py]                      │
│    → Becomes: Orchestrator.ConcurrencyControl                   │
│    Changes: None (already generic)                              │
│                                                                   │
│  ✓ Thread-Specific Logging                                       │
│    [ai4pkm_cli/logger.py]                                       │
│    → Becomes: Agent.LoggingSystem                               │
│    Changes: None (already supports arbitrary thread names)      │
│                                                                   │
│  ✓ AgentFactory                                                  │
│    [ai4pkm_cli/agents/agent_factory.py]                         │
│    → Becomes: Orchestrator.AgentManager.create_agent()          │
│    Changes: Load agent definitions from Markdown files          │
│                                                                   │
│  ✓ Task File Schema                                              │
│    [Current task frontmatter with status field]                │
│    → Becomes: Universal state storage mechanism                 │
│    Changes: Add optional agent metadata fields                  │
│                                                                   │
│  REFACTOR (Extract & Generalize):                               │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                                │
│                                                                   │
│  ⟳ BaseFileHandler                                               │
│    [ai4pkm_cli/watchdog/handlers/base_file_handler.py]          │
│    → Becomes: Agent base class                                  │
│    Changes:                                                      │
│      - Extract process() logic to config-driven                 │
│      - Add input/output spec validation                         │
│      - Support skill library integration                        │
│                                                                   │
│  ⟳ TaskProcessor / TaskEvaluator                                 │
│    [ai4pkm_cli/watchdog/handlers/task_*.py]                     │
│    → Becomes: Generic agent instances                           │
│    Changes:                                                      │
│      - Remove hardcoded logic                                   │
│      - Load behavior from YAML configs                          │
│      - Use generic trigger matching                             │
│                                                                   │
│  ⟳ KTPRunner 3-phase logic                                       │
│    [ai4pkm_cli/commands/ktp_runner.py]                          │
│    → Becomes: Orchestrator.WorkflowCoordinator                  │
│    Changes:                                                      │
│      - Extract phase transitions to workflow config             │
│      - Support arbitrary agent chains                           │
│      - Generalize routing logic                                 │
│                                                                   │
│  BUILD NEW:                                                      │
│  ━━━━━━━━━━━                                                     │
│                                                                   │
│  + Agent Definition Loader                                       │
│    Load Markdown files from _Settings_/Agents/ directory        │
│    Parse YAML frontmatter + prompt body                         │
│                                                                   │
│  + Workflow Definition System                                    │
│    Define agent chains and transitions                          │
│                                                                   │
│  + User Interface Module                                         │
│    Status reporting and feedback collection                     │
│                                                                   │
│  + Skill Library Integration                                     │
│    Connect to MCP servers and Claude Code skills                │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Migration Phases

### Phase 1: Foundation (Weeks 1-2)
**Goal:** Create generalized agent framework without breaking existing KTM

```
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 1: FOUNDATION                                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  New Components:                                                 │
│  ├─ orchestrator/                                                │
│  │  ├─ core.py                  (Main orchestrator class)       │
│  │  ├─ file_system_monitor.py   (Enhanced FileWatchdog)         │
│  │  ├─ agent_manager.py          (Agent spawning & routing)     │
│  │  └─ workflow_coordinator.py   (Chain management)             │
│  │                                                                │
│  ├─ agents/                                                      │
│  │  ├─ base_agent.py        (Generic agent class)               │
│  │  ├─ agent_loader.py      (Markdown definition parser)        │
│  │  └─ agent_runner.py      (Execution logic)                   │
│  │                                                                │
│  └─ _Settings_/                                                  │
│     ├─ Agents/                                                   │
│     │  ├─ Knowledge Task Generator.md                            │
│     │  ├─ Knowledge Task Processor.md                            │
│     │  └─ Knowledge Task Evaluator.md                            │
│     └─ Workflows/                                                │
│        └─ Knowledge Task Workflow.md                             │
│                                                                   │
│  Deliverables:                                                   │
│  ✓ Agent definition schema (Markdown + frontmatter)             │
│  ✓ Agent definition loader                                      │
│  ✓ Generic agent base class                                     │
│  ✓ Orchestrator core structure                                  │
│  ✓ Existing KTM still works (no breaking changes)               │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Phase 2: Migration (Weeks 3-4)
**Goal:** Convert KTG, KTP-Exec, KTP-Eval to config-driven agents

```
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 2: MIGRATION                                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Tasks:                                                          │
│  1. Convert KTG to definition-driven agent                       │
│     ├─ Create Knowledge Task Generator.md                        │
│     ├─ Migrate TaskRequestFileHandler logic to Markdown         │
│     └─ Test: Request JSON → Task creation                        │
│                                                                   │
│  2. Convert KTP-Exec to definition-driven agent                  │
│     ├─ Create Knowledge Task Processor.md                        │
│     ├─ Extract routing logic to frontmatter                      │
│     ├─ Migrate phase 1 & 2 logic to prompt body                  │
│     └─ Test: TBD → IN_PROGRESS → PROCESSED                       │
│                                                                   │
│  3. Convert KTP-Eval to definition-driven agent                  │
│     ├─ Create Knowledge Task Evaluator.md                        │
│     ├─ Migrate evaluation logic to prompt body                   │
│     └─ Test: PROCESSED → UNDER_REVIEW → COMPLETED/FAILED        │
│                                                                   │
│  4. Create knowledge task workflow                               │
│     ├─ Define agent chain: Generator → Executor → Evaluator     │
│     ├─ Define status transitions                                 │
│     └─ Test: End-to-end workflow                                 │
│                                                                   │
│  5. Dual-mode operation                                          │
│     ├─ Add flag: --legacy-ktm vs --orchestrator                  │
│     ├─ Both systems work side-by-side                            │
│     └─ Test: Compare outputs                                     │
│                                                                   │
│  Deliverables:                                                   │
│  ✓ All KTM agents converted to Markdown definitions             │
│  ✓ Workflow definition for knowledge tasks                       │
│  ✓ Feature parity with existing KTM                              │
│  ✓ Comprehensive test suite                                      │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Phase 3: Enhancement (Weeks 5-6)
**Goal:** Add new orchestrator capabilities

```
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 3: ENHANCEMENT                                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  New Capabilities:                                               │
│  1. Skills Infrastructure                                        │
│     ├─ Extract skills from existing prompts                      │
│     ├─ Build skill extraction tool                               │
│     ├─ Implement skill library manager                           │
│     ├─ Create 4 domain skill categories                          │
│     └─ Test: Agent with skill dependencies                       │
│                                                                   │
│  2. User Interface Module                                        │
│     ├─ Status dashboard                                          │
│     ├─ Agent execution monitoring                                │
│     ├─ Feedback collection UI                                    │
│     └─ System diagnostics                                        │
│                                                                   │
│  3. Advanced Workflow Features                                   │
│     ├─ Conditional agent chains                                  │
│     ├─ Parallel agent execution                                  │
│     ├─ Dynamic routing based on results                          │
│     └─ Workflow templates for common patterns                    │
│                                                                   │
│  4. System Improvement Loop                                      │
│     ├─ Collect agent performance metrics                         │
│     ├─ Analyze failures and bottlenecks                          │
│     ├─ Suggest agent/skill improvements                          │
│     └─ Auto-update where safe                                    │
│                                                                   │
│  5. Configurable Repository                                      │
│     ├─ Build installation wizard                                 │
│     ├─ Create migration tool (KTM → new system)                  │
│     ├─ Generate repository template                              │
│     ├─ Test fresh installation                                   │
│     └─ Test migration from existing KTM                          │
│                                                                   │
│  Deliverables:                                                   │
│  ✓ Skill library with extracted skills                          │
│  ✓ User interaction system                                       │
│  ✓ Advanced workflow capabilities                                │
│  ✓ Self-improvement mechanisms                                   │
│  ✓ Installation wizard                                           │
│  ✓ Migration tool for existing users                             │
│  ✓ Clean repository template for distribution                    │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Phase 4: Cleanup & Documentation (Week 7)
**Goal:** Remove legacy code, finalize documentation

```
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 4: CLEANUP                                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Tasks:                                                          │
│  ✓ Remove legacy KTM handlers                                   │
│  ✓ Archive old code in git                                       │
│  ✓ Update all documentation                                      │
│  ✓ Create migration guide                                        │
│  ✓ Write agent development guide                                 │
│  ✓ Performance benchmarks                                        │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Configurable Repository Design

**Vision**: Transform AI4PKM from a personal system into a **reusable, installable framework** that others can adopt and customize for their own knowledge management needs.

### Simplified Repository Structure

The repository will contain **only the essentials**, making it easy to understand, customize, and maintain:

```
AI4PKM/
├── _Settings_/
│   ├── Agents/           # Agent definitions (Markdown + frontmatter)
│   │   ├── Knowledge Task Generator.md
│   │   ├── Knowledge Task Processor.md
│   │   ├── Knowledge Task Evaluator.md
│   │   ├── Content Ingestion.md
│   │   └── Weekly Roundup.md
│   │
│   ├── Skills/           # Reusable skill library
│   │   ├── content_collection/
│   │   ├── publishing/
│   │   ├── knowledge_organization/
│   │   └── obsidian_rules/
│   │
│   ├── Templates/        # File templates
│   │   ├── Task.md
│   │   ├── Roundup.md
│   │   └── Topic.md
│   │
│   └── Rules/            # Global rules (AGENTS.md, etc.)
│       ├── AGENTS.md
│       └── CLAUDE.md
│
├── orchestrator/         # Core orchestrator code
├── agents/               # Generic agent runner
├── skills/               # Skill loading infrastructure
│
└── install/              # Installation wizard
    ├── config.yaml       # User configuration template
    └── setup.py          # Installation script
```

**What's NOT in the repository**:
- User's content (AI/, Ingest/, Topics/, Journal/)
- User-specific configurations
- Logs and temporary files
- Environment-specific settings

### Installation Process

**Step 1: Clone Repository**
```bash
git clone https://github.com/user/AI4PKM
cd AI4PKM
```

**Step 2: Run Installation Wizard**
```bash
python install/setup.py
```

**Step 3: Interactive Configuration**

The wizard asks:

1. **Vault Location**
   ```
   Where is your Obsidian vault?
   > /Users/username/MyVault
   ```

2. **Agent Selection**
   ```
   Select agents to enable:
   [x] Knowledge Task Management (KTG, KTP, KTE)
   [x] Content Ingestion (Clippings, Limitless)
   [ ] Publishing Automation (Substack, Thread)
   [x] Weekly Roundup
   [ ] Daily Review
   ```

3. **Input/Output Locations**
   ```
   Configure folder structure:

   Tasks folder: AI/Tasks
   Clippings folder: Ingest/Clippings
   Topics folder: Topics
   Roundup folder: AI/Roundup

   [Use defaults] [Customize]
   ```

4. **Executor Configuration**
   ```
   Select AI executor:
   ( ) Claude Code (default)
   ( ) Gemini CLI
   ( ) Custom

   API keys: [Configure]
   ```

**Step 4: Auto-Generate Structure**

The installer creates:
```
/Users/username/MyVault/
├── AI/
│   ├── Tasks/
│   │   ├── Requests/
│   │   └── Logs/
│   └── Roundup/
│
├── Ingest/
│   └── Clippings/
│
├── Topics/
│
└── _Settings_/  (symlinked to AI4PKM/_Settings_/)
    ├── Agents/
    ├── Skills/
    ├── Templates/
    └── Rules/
```

### User Configuration File

**Generated: `{vault}/.ai4pkm/config.yaml`**

```yaml
# AI4PKM Configuration
version: 1.0
vault_path: /Users/username/MyVault

# Enabled Agents
agents:
  - Knowledge Task Generator
  - Knowledge Task Processor
  - Knowledge Task Evaluator
  - Content Ingestion
  - Weekly Roundup

# Folder Structure
paths:
  tasks: AI/Tasks
  tasks_requests: AI/Tasks/Requests
  tasks_logs: AI/Tasks/Logs
  clippings: Ingest/Clippings
  limitless: Limitless
  topics: Topics
  roundup: AI/Roundup

# Executor Configuration
executor:
  default: claude_code
  mapping:
    EIC: claude_code
    Research: gemini_cli

# Orchestrator Settings
orchestrator:
  max_concurrent_agents: 3
  startup_detection: true
  auto_retry: true
  max_retries: 2

# Skill Configuration
skills:
  enabled:
    - validate_wiki_links
    - update_topic_index
    - create_roundup_entry
    - format_for_substack
```

### Customization Options

Users can customize without touching code:

**1. Add Custom Agents**
```markdown
<!-- MyVault/_Settings_/Agents/My Custom Agent.md -->
---
name: My Custom Agent
trigger_pattern: "MyFolder/*.md"
trigger_event: created
output_pattern: "Output/*.md"
skills: ["my_custom_skill"]
---

# My Custom Agent

You are a custom agent that does...
```

**2. Modify Existing Agents**
- Edit agent Markdown files
- Change trigger patterns
- Add/remove skills
- Adjust prompts

**3. Create Custom Skills**
```python
# MyVault/_Settings_/Skills/my_custom_skill.py
class MyCustomSkill:
    def execute(self, input_data):
        # Custom logic
        return result
```

**4. Adjust Folder Structure**
- Modify `config.yaml` paths
- Orchestrator adapts automatically

### Benefits of Configurable Design

**For Users**:
- ✅ Easy installation (one command)
- ✅ Choose only needed features
- ✅ Customize without coding
- ✅ Update system independently of content

**For Developers**:
- ✅ Clean separation of framework vs. content
- ✅ Easy to add new agents/skills
- ✅ Version control for system only
- ✅ Community can share agents/skills

**For Community**:
- ✅ Share agent definitions
- ✅ Create skill packages
- ✅ Build agent marketplaces
- ✅ Contribute improvements upstream

### Migration from Current KTM

**For Existing Users**:

```bash
# 1. Backup current setup
cp -r AI4PKM AI4PKM-backup

# 2. Install new system
python install/migrate.py --from-ktm

# 3. Wizard detects existing structure
# 4. Auto-generates config matching current setup
# 5. Enables equivalent agents
# 6. Preserves all content and configurations
```

The migration tool:
- Detects current folder structure
- Maps existing handlers to new agents
- Preserves all content files
- Creates compatible config.yaml
- Runs validation tests

## What Needs to Be Built (New Components)

### 1. Agent Definition Loader
```python
# orchestrator/agent_loader.py
class AgentDefinitionLoader:
    """Load and validate agent Markdown definitions"""
    def load_agent(md_path: str) -> AgentDefinition
        # Parse YAML frontmatter + prompt body
    def validate_definition(agent_def: dict) -> bool
    def get_all_agents(agents_dir: str = "_Settings_/Agents") -> List[AgentDefinition]
```

### 2. Generic Agent Runner
```python
# agents/agent_runner.py
class GenericAgent:
    """Execute agent based on config specification"""
    def __init__(config: AgentConfig)
    def validate_input() -> bool
    def execute() -> AgentResult
    def validate_output() -> bool
    def update_state() -> None
```

### 3. Workflow Coordinator
```python
# orchestrator/workflow_coordinator.py
class WorkflowCoordinator:
    """Manage agent chains and transitions"""
    def load_workflow(config_path: str) -> Workflow
    def execute_workflow(workflow: Workflow, context: dict)
    def handle_transition(from_state: str, to_state: str)
    def retry_failed_agent(agent_id: str)
```

### 4. User Interface Module
```python
# orchestrator/user_interface.py
class UserInterface:
    """Status reporting and feedback collection"""
    def report_status(workflow_id: str)
    def collect_feedback(task_id: str)
    def show_diagnostics()
    def suggest_improvements()
```

### 5. Skill Library Manager
```python
# skills/skill_library.py
class SkillLibrary:
    """Manage available skills and MCP servers"""
    def register_skill(name: str, handler: callable)
    def get_skill(name: str) -> callable
    def list_available_skills() -> List[str]
    def load_skills_for_agent(skill_names: List[str]) -> Dict[str, callable]
    def connect_mcp_server(config: dict)
```

### 6. Skill Extraction Tool
```python
# tools/extract_skills.py
class SkillExtractor:
    """Extract reusable skills from existing prompts"""
    def analyze_prompts(prompts_dir: str) -> List[SkillCandidate]
    def find_duplicated_logic() -> List[DuplicationPattern]
    def suggest_skills() -> List[SkillSuggestion]
    def generate_skill_stub(skill_name: str) -> str
```

### 7. Installation Wizard
```python
# install/setup.py
class InstallationWizard:
    """Interactive installation and configuration"""
    def prompt_vault_location() -> Path
    def select_agents() -> List[str]
    def configure_paths() -> Dict[str, str]
    def configure_executor() -> Dict
    def generate_config(user_choices: Dict) -> str
    def create_folder_structure(vault_path: Path, config: Dict)
    def symlink_settings(vault_path: Path)
```

### 8. Migration Tool
```python
# install/migrate.py
class KTMMigrationTool:
    """Migrate from current KTM to new system"""
    def detect_current_structure(vault_path: Path) -> Dict
    def map_handlers_to_agents() -> Dict[str, str]
    def generate_compatible_config() -> str
    def preserve_content_files()
    def validate_migration() -> bool
```

### 9. Repository Template Generator
```python
# tools/create_template.py
class RepositoryTemplateGenerator:
    """Generate clean repository for distribution"""
    def extract_framework_only() -> None
    def remove_user_content() -> None
    def create_example_agents() -> None
    def generate_documentation() -> None
```

## Benefits of Migration

### Immediate Benefits
1. **Cleaner Architecture**: Separation of concerns between orchestrator and agents
2. **Easier Testing**: Config-driven agents can be tested independently
3. **Better Visibility**: Centralized state management and monitoring
4. **Code Reuse**: 95% of existing KTM components are reusable

### Long-term Benefits
1. **Extensibility**: Add new agents by creating YAML config (no code changes)
2. **Flexibility**: Define custom workflows without touching core code
3. **Maintainability**: Clear boundaries and responsibilities
4. **Scalability**: Easy to add parallel execution, distributed agents
5. **User Interaction**: Systematic feedback and improvement loop

## Risk Mitigation

### Risks
1. **Breaking existing workflows**: KTM is critical infrastructure
2. **Performance regression**: New abstractions might slow things down
3. **Configuration complexity**: YAML configs could become unwieldy

### Mitigation Strategies
1. **Dual-mode operation**: Run old and new systems in parallel during migration
2. **Comprehensive testing**: Unit, integration, and end-to-end tests
3. **Performance benchmarks**: Measure before and after
4. **Incremental rollout**: One agent at a time, validate each step
5. **Rollback plan**: Keep legacy code until full validation

## Summary

This migration transforms the KTM system from a specialized task management system into a **generalized multi-agent orchestration framework** while:

- **Preserving 95% of existing code** (FileWatchdog, Semaphore, Logging, AgentFactory)
- **Maintaining full backward compatibility** during transition
- **Adding powerful new capabilities** (user interaction, skill integration, workflow templates)
- **Improving maintainability** through config-driven architecture
- **Enabling future extensibility** for new agent types and workflows

The key insight is that **KTM already implements the core concepts** of the generalized framework - we're just extracting, formalizing, and generalizing what's already there.

## Next Steps

1. **Review and validate this plan** with stakeholders
2. **Set up development branch** for migration work
3. **Begin Phase 1** (Foundation) implementation
4. **Create test cases** for each migration phase
5. **Document migration progress** in project wiki

---

*Document created: 2025-10-24*
*Related: [[2025-10-24 Next Steps in AI4PKM]], [[README_KTM]]*
