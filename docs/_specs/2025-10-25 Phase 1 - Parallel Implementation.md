---
title: "Phase 1: Parallel Implementation - Orchestrator Migration"
created: 2025-10-25
tags:
  - implementation
  - orchestrator
  - migration
  - phase1
author:
  - "[[Claude]]"
related:
  - "[[2025-10-25 Orchestrator Detailed Design]]"
  - "[[2025-10-24 KTM to Multi-Agent Migration Plan]]"
---

# Phase 1: Parallel Implementation

## Overview
**Goal**: Build orchestrator alongside KTM without disrupting existing functionality
**Duration**: Week 1-2 (10 days)
**Risk Level**: Low (no changes to existing KTM code)

## Success Criteria
- [ ] Orchestrator directory structure created
- [ ] Core components implemented and unit tested
- [ ] KTM continues to work normally
- [ ] No file conflicts between systems
- [ ] All unit tests passing (>80% coverage)

---
# Task Breakdown

## Task 1: Directory Structure Setup
**Duration**: 30 minutes

### Actions
```bash
# Create orchestrator directory
mkdir -p ai4pkm_cli/orchestrator

# Create test directories
mkdir -p ai4pkm_cli/tests/unit/orchestrator
mkdir -p ai4pkm_cli/tests/integration/orchestrator
mkdir -p ai4pkm_cli/tests/fixtures
mkdir -p ai4pkm_cli/tests/mocks

# Create initial files
cd ai4pkm_cli/orchestrator
touch __init__.py core.py file_monitor.py agent_registry.py
touch execution_manager.py metrics.py models.py
```

### Validation
```bash
tree ai4pkm_cli/orchestrator
ai4pkm --version  # Verify KTM still works
```

---
## Task 2: Implement Data Models
**Duration**: 2-3 hours

### File: `ai4pkm_cli/orchestrator/models.py`
Create dataclasses for:
- `AgentDefinition` - Represents loaded agent configuration
- `ExecutionContext` - Tracks single agent execution
- `FileEvent` - Represents file system event

### Unit Tests: `ai4pkm_cli/tests/unit/orchestrator/test_models.py`
Test all dataclasses, properties, and default values.

### Validation
```bash
pytest ai4pkm_cli/tests/unit/orchestrator/test_models.py -v
```

---
## Task 3: Shared Utilities (Already Done ✅)
**Duration**: Completed

### File: `ai4pkm_cli/markdown_utils.py`
✅ Functions implemented:
- `extract_frontmatter(content)` - Parse YAML from markdown
- `read_frontmatter(file_path)` - Read frontmatter from file
- `update_frontmatter_field(content, field, value)` - Update single field
- `update_frontmatter_fields(content, updates)` - Update multiple fields
- `extract_body(content)` - Get content after frontmatter

### Validation
```bash
pytest ai4pkm_cli/tests/test_markdown_utils.py -v
# Result: 13/13 tests passed ✅
```

---
## Task 4: Implement File Monitor
**Duration**: 3-4 hours

### File: `ai4pkm_cli/orchestrator/file_monitor.py`
Create `FileSystemMonitor` class:
- Uses watchdog Observer to monitor file changes
- Queues events for processing
- Parses frontmatter from changed files
- Filters to .md files only

### Key Simplification
**No global semaphores** - Just queue events and let ExecutionManager handle concurrency.

### Unit Tests: `ai4pkm_cli/tests/unit/orchestrator/test_file_monitor.py`
Test event detection, queueing, filtering.

### Validation
```bash
pytest ai4pkm_cli/tests/unit/orchestrator/test_file_monitor.py -v
```

---
## Task 5: Implement Agent Registry
**Duration**: 4-5 hours

### File: `ai4pkm_cli/orchestrator/agent_registry.py`
Create `AgentRegistry` class:
- Load all agent definitions from `_Settings_/Agents/`
- Parse frontmatter and prompt body
- Validate using JSON schema
- Match file events to agent triggers
- Export config snapshot for debugging

### Unit Tests: `ai4pkm_cli/tests/unit/orchestrator/test_agent_registry.py`
Test loading, validation, trigger matching.

### Validation
```bash
pytest ai4pkm_cli/tests/unit/orchestrator/test_agent_registry.py -v
```

---
## Task 6: Implement Execution Manager
**Duration**: 4-5 hours

### File: `ai4pkm_cli/orchestrator/execution_manager.py`
Create `ExecutionManager` class:
- Spawn agent execution in separate threads
- Simple concurrency control (counter + lock, NOT semaphores)
- Track active executions
- Collect metrics
- Handle timeouts and errors

### Simplified Concurrency
**Instead of** complex global semaphores:
```python
# OLD (KTM - complex)
_generation_semaphore = None
_execution_semaphore = None
_semaphore_lock = threading.Lock()
```

**Use** simple instance counter:
```python
# NEW (Orchestrator - simple)
class ExecutionManager:
    def __init__(self, max_concurrent=3):
        self.max_concurrent = max_concurrent
        self.active_count = 0
        self.active_lock = threading.Lock()
```

### Unit Tests: `ai4pkm_cli/tests/unit/orchestrator/test_execution_manager.py`
Test concurrency limits, timeouts, error handling.

### Validation
```bash
pytest ai4pkm_cli/tests/unit/orchestrator/test_execution_manager.py -v
```

---
## Task 7: Implement Orchestrator Core
**Duration**: 3-4 hours

### File: `ai4pkm_cli/orchestrator/core.py`
Create `Orchestrator` class:
- Initialize all components
- Start file monitoring
- Run event loop
- Match events to agents
- Spawn agent executions
- Graceful shutdown

### Integration Tests: `ai4pkm_cli/tests/integration/orchestrator/test_orchestrator_lifecycle.py`
Test startup, event processing, shutdown.

### Validation
```bash
pytest ai4pkm_cli/tests/integration/orchestrator/ -v
```

---
## Task 8: Integration and Testing
**Duration**: 2-3 hours

### Actions
1. Run full test suite
2. Verify code coverage
3. Test parallel running with KTM
4. Update documentation

### Validation
```bash
# Run all orchestrator tests
pytest ai4pkm_cli/tests/unit/orchestrator/ \
       ai4pkm_cli/tests/integration/orchestrator/ \
       -v --cov=ai4pkm_cli/orchestrator

# Verify KTM still works
ai4pkm -t &
sleep 2
echo "---\ntitle: Test\n---\n# Content" > Ingest/Clipping/test.md
# Should see KTM process the file
```

---
# Implementation Timeline

## Days 1-2: Foundation
- [x] Task 1: Directory structure (30min)
- [x] Task 3: Markdown utils (DONE)
- [ ] Task 2: Data models + tests (2-3h)

## Days 3-5: Core Components
- [ ] Task 4: File Monitor + tests (3-4h)
- [ ] Task 5: Agent Registry + tests (4-5h)

## Days 6-8: Execution
- [ ] Task 6: Execution Manager + tests (4-5h)
- [ ] Task 7: Orchestrator Core + tests (3-4h)

## Days 9-10: Integration
- [ ] Task 8: Integration testing (2-3h)
- [ ] Code review and documentation
- [ ] Final validation

---
# Key Simplifications from KTM

## 1. No Global Semaphore Module
**KTM Approach**:
- Separate `task_semaphore.py` module
- Global `_generation_semaphore` and `_execution_semaphore`
- Thread locks for initialization
- Complex lifecycle management

**Orchestrator Approach**:
- Simple counter in `ExecutionManager` instance
- No global state
- Easier to test and reason about

**Benefit**: Simpler, clearer ownership, easier to test

## 2. No KTG/KTP Split
**KTM Approach**: 3-phase processing
1. KTG: Generate task request JSON
2. KTP Phase 1-2: Execute task
3. KTP Phase 3: Evaluate task

**Orchestrator Approach**: Direct execution
1. File event triggers agent
2. Agent executes
3. Done

**Benefit**: Fewer moving parts, clearer flow, faster

## 3. No JSON Task Requests
**KTM Approach**:
- Handlers create JSON files in `AI/Tasks/Requests/`
- KTG reads JSON and creates task MD files

**Orchestrator Approach**:
- Handlers directly trigger agents
- Tasks created immediately

**Benefit**: One less intermediate format, simpler flow

## 4. Shared Markdown Utilities
**New**: `markdown_utils.py` module
- Extracted from `ktp_runner.py`
- Used by both KTM and orchestrator
- Will remain after KTM is deprecated

**Benefit**: Code reuse, consistent behavior, easier migration

---
# Validation Checklist

## Code Quality
- [ ] All unit tests passing (>80% coverage)
- [ ] No linting errors
- [ ] Type hints added where appropriate
- [ ] Docstrings for all public functions

## Functionality
- [ ] File monitor detects file events correctly
- [ ] Agent registry loads agent definitions
- [ ] Execution manager enforces concurrency limits
- [ ] Task files created with correct frontmatter
- [ ] Orchestrator event loop processes events

## Non-Disruption
- [ ] KTM continues to work normally
- [ ] No file path conflicts between systems
- [ ] No import conflicts
- [ ] Can run both systems simultaneously

---
# Risks and Mitigations

## Risk 1: Watchdog Observer Conflicts
**Risk**: Running two observers (KTM + Orchestrator) on same vault
**Mitigation**: Orchestrator disabled by default, explicit enable flag
**Test**: Start KTM, then start orchestrator, verify both work

## Risk 2: File Path Conflicts
**Risk**: Both systems writing to `_Tasks_/`
**Mitigation**: Different filename patterns (orchestrator uses ISO timestamps)
**Test**: Verify no filename collisions in parallel run

## Risk 3: Import Conflicts
**Risk**: Circular imports between orchestrator and KTM
**Mitigation**: Keep orchestrator completely separate, no imports from watchdog/
**Test**: Import orchestrator modules independently

---
# Success Metrics

## Quantitative
- Unit test coverage: >80%
- All tests passing: 100%
- Test execution time: <30 seconds
- Zero KTM disruptions: 0 errors

## Qualitative
- Code is readable and well-documented
- Components are independently testable
- Clear separation from KTM code
- Easy to understand for new contributors

---
**Phase**: 1/5
**Status**: In Progress (3/8 tasks complete)
**Next**: [[2025-10-25 Phase 2 - Single Agent Migration]] (to be created)
