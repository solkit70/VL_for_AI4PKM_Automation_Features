# Manual Integration Test Guide
## orchestrator.yaml Format Migration Testing

**Document Version:** 1.0
**Last Updated:** 2025-10-30
**Related PR:** Orchestrator YAML Format Migration (nodes-based configuration)

---

## Overview

This guide provides step-by-step instructions for manually testing the orchestrator system after the YAML format migration from dict-based `agents` to list-based `nodes` configuration.

### What Changed

- **Configuration Format**: `agents: {EIC: {...}}` → `nodes: [{type: agent, name: "..."}]`
- **Abbreviation Extraction**: From dict keys → regex extraction from name field
- **Configuration Source**: Frontmatter + YAML → YAML only (single source of truth)
- **Agent Loading**: Updated `agent_registry.py` to parse nodes format
- **Deprecated**: HTC (Hashtag Task Creator) removed from configuration

---

## Prerequisites

### 1. Environment Setup

```bash
# Ensure you're in the project root
cd /Users/lifidea/dev/AI4PKM

# Verify vault configuration exists
ls -l ai4pkm_vault/orchestrator.yaml
ls -l ai4pkm_vault/ai4pkm_cli.json

# Check agent prompt files exist
ls ai4pkm_vault/_Settings_/Prompts/*.md
```

### 2. Configuration Validation

Verify [ai4pkm_vault/orchestrator.yaml](../ai4pkm_vault/orchestrator.yaml) has correct format:

```yaml
version: "1.0"

defaults:
  executor: claude_code
  timeout_minutes: 30
  max_parallel: 3
  # ... other defaults

nodes:
  - type: agent
    name: Enrich Ingested Content (EIC)
    input_path: Ingest/Clippings
    output_path: AI/Articles

  - type: agent
    name: Create Thread Postings (CTP)
    input_path:
      - AI/Articles
      - AI/Roundup
      - AI/Research
    output_path: AI/Sharable

  # ... other agents
```

**Critical**: Each agent name must follow format `"Full Name (ABBR)"` with 3-4 letter abbreviation.

### 3. Stop Running Orchestrator

```bash
# Kill any existing orchestrator processes
pkill -f "ai4pkm_cli.orchestrator_cli"

# Verify no processes running
ps aux | grep orchestrator_cli
```

---

## Test Procedures

### Test 1: EIC (Enrich Ingested Content)

**Purpose**: Verify EIC agent loads correctly and processes new clipping files.

**Configuration**:
- Input: `Ingest/Clippings/`
- Output: `AI/Articles/`
- Trigger: New file creation
- Expected: `max_parallel=3` concurrent executions

#### Steps

**1. Start Orchestrator Daemon**

```bash
cd ai4pkm_vault
python -m ai4pkm_cli.orchestrator_cli daemon
```

**Expected Console Output**:
```
INFO: Loading agents from orchestrator.yaml
INFO: Loading 7 agents from orchestrator.yaml
INFO: Loaded agent: EIC (Enrich Ingested Content)
INFO: Loaded agent: GDR (Generate Daily Roundup)
INFO: Loaded agent: PLL (Process Life Logs)
INFO: Loaded agent: CTP (Create Thread Postings)
INFO: Loaded agent: PPP (Pick and Process Photos)
INFO: Loaded agent: GES (Generate Event Summary)
INFO: Loaded agent: ARP (Ad-hoc Research within PKM)
INFO: Total agents loaded: 7
```

**⚠️ Watch for Errors**:
- `Cannot extract abbreviation from: {name}` → Agent name format incorrect
- `No prompt file found for agent: {abbr}` → Missing prompt file in `_Settings_/Prompts/`

**2. Create Test Clipping Files**

**IMPORTANT**: Create files with **3+ second delays** between each to ensure watchdog detects events properly.

```bash
# Open new terminal, navigate to vault
cd ai4pkm_vault/Ingest/Clippings

# Create test file 1
cat > "2025-10-30 Manual Test A $(date +%H%M%S).md" << 'EOF'
---
title: "Manual Integration Test Article A"
source: "https://example.com/test-a"
author:
  - "Test Author"
created: 2025-10-30
status: "processed"
tags:
  - clippings
  - test
---

## Summary

This is a test article for manual integration testing of the EIC agent after orchestrator.yaml format migration. The article discusses the importance of proper testing when refactoring core system components.

## Improve Capture & Transcript (ICT)

### Testing Best Practices

Integration testing ensures that system components work together correctly after architectural changes. Key principles include:

- **Realistic Scenarios**: Tests should mirror actual usage patterns
- **Observable Stages**: Break workflows into verifiable steps
- **Proper Cleanup**: Remove test artifacts to avoid pollution

### Format Migration Testing

When migrating configuration formats, comprehensive testing validates:

1. Agent loading works with new format
2. File triggers are detected correctly
3. Tasks are created and executed
4. Concurrency limits are respected
5. Output files are generated properly

This test validates the EIC agent functionality after migration from dict-based to list-based node configuration.
EOF

# Wait 3 seconds
sleep 3

# Create test file 2
cat > "2025-10-30 Manual Test B $(date +%H%M%S).md" << 'EOF'
---
title: "Manual Integration Test Article B"
source: "https://example.com/test-b"
author:
  - "Test Author"
created: 2025-10-30
status: "processed"
tags:
  - clippings
  - test
---

## Summary

Second test article for EIC integration testing, focusing on concurrent execution capabilities with max_parallel=3 setting.

## Improve Capture & Transcript (ICT)

### Concurrency Testing

With max_parallel=3, the orchestrator should:
- Execute up to 3 tasks simultaneously
- Queue additional tasks until slots free up
- Avoid race conditions in task creation
- Properly track task status transitions

This validates the concurrency handling in the refactored system.
EOF

# Wait 3 seconds
sleep 3

# Create test file 3
cat > "2025-10-30 Manual Test C $(date +%H%M%S).md" << 'EOF'
---
title: "Manual Integration Test Article C"
source: "https://example.com/test-c"
author:
  - "Test Author"
created: 2025-10-30
status: "processed"
tags:
  - clippings
  - test
---

## Summary

Third test article validating task queueing behavior when more than max_parallel tasks are created.

## Improve Capture & Transcript (ICT)

### Queue Management

When 4 tasks are created but max_parallel=3:
- First 3 should execute immediately
- Fourth should queue until slot opens
- No duplicate task creation
- All tasks complete successfully

EOF

# Wait 3 seconds
sleep 3

# Create test file 4
cat > "2025-10-30 Manual Test D $(date +%H%M%S).md" << 'EOF'
---
title: "Manual Integration Test Article D"
source: "https://example.com/test-d"
author:
  - "Test Author"
created: 2025-10-30
status: "processed"
tags:
  - clippings
  - test
---

## Summary

Fourth test article completing the concurrent execution test suite.

## Improve Capture & Transcript (ICT)

### Final Validation

This final test file validates:
- All 4 tasks are created
- Tasks execute without errors
- Output files generated correctly
- Status transitions work properly
- No duplicate executions occur

EOF
```

**3. Monitor Task Creation**

Watch the orchestrator console for task creation:

```
Expected output pattern:
INFO: File event: created /path/to/2025-10-30 Manual Test A {timestamp}.md
INFO: Matched agent: EIC
INFO: Creating task for EIC: 2025-10-30 Manual Test A {timestamp}.md
INFO: Task created: _Tasks_/2025-10-30 EIC - Manual Test A {timestamp}.md
INFO: Executing task: EIC - Manual Test A {timestamp}
```

**Check task directory** (in separate terminal):

```bash
cd ai4pkm_vault/_Tasks_   # or your configured tasks_dir
ls -lt | head -10

# Watch for task files:
# 2025-10-30 EIC - Manual Test A {timestamp}.md
# 2025-10-30 EIC - Manual Test B {timestamp}.md
# 2025-10-30 EIC - Manual Test C {timestamp}.md
# 2025-10-30 EIC - Manual Test D {timestamp}.md
```

**4. Verify Task Status Transitions**

Open a task file and watch status field:

```bash
# Initial status
grep -i "status:" "_Tasks_/2025-10-30 EIC - Manual Test A"*.md

# Expected: status: IN_PROGRESS
```

Wait for execution (can take 1-5 minutes per task):

```bash
# Watch for status change
watch -n 5 'grep -i "status:" _Tasks_/2025-10-30\ EIC\ -\ Manual\ Test\ A*.md'

# Expected final: status: PROCESSED
```

**5. Verify Output Files**

```bash
cd ../AI/Articles
ls -lt | head -10

# Expected output files:
# 2025-10-30 Manual Test A {timestamp} - EIC.md
# 2025-10-30 Manual Test B {timestamp} - EIC.md
# 2025-10-30 Manual Test C {timestamp} - EIC.md
# 2025-10-30 Manual Test D {timestamp} - EIC.md
```

Open an output file and verify:
- Has enriched content
- More detailed than input
- Proper markdown structure
- Links to source file

**6. Check for Duplicate Tasks**

```bash
cd ../_Tasks_
ls -1 | grep "EIC - Manual Test" | sort

# Should see exactly 4 tasks (one per input file)
# Count them:
ls -1 | grep "EIC - Manual Test" | wc -l
# Expected: 4
```

#### Success Criteria

✅ **PASS** if:
- All 7 agents loaded without errors
- 4 task files created in `_Tasks_/`
- No duplicate task files
- All tasks transitioned: `IN_PROGRESS` → `PROCESSED`
- 4 output files created in `AI/Articles/`
- No more than 3 tasks executing concurrently (check logs)
- Output files contain enriched content

❌ **FAIL** if:
- Any agent failed to load
- Abbreviation extraction errors
- Duplicate tasks created
- Tasks stuck in `IN_PROGRESS`
- Missing output files
- More than `max_parallel=3` concurrent executions

---

### Test 2: CTP (Create Thread Postings)

**Purpose**: Verify CTP agent processes article files and creates shareable content.

**Configuration**:
- Input: `AI/Articles/`, `AI/Roundup/`, `AI/Research/`
- Output: `AI/Sharable/`
- Trigger: New file in input paths

#### Steps

**1. Ensure Orchestrator Running**

```bash
# If not already running from Test 1
cd ai4pkm_vault
python -m ai4pkm_cli.orchestrator_cli daemon
```

**2. Create Test Article Files**

```bash
cd ai4pkm_vault/AI/Articles

# Article 1
cat > "2025-10-30 CTP Test A $(date +%H%M%S).md" << 'EOF'
---
title: "CTP Test Article A - Configuration Migration"
created: 2025-10-30
tags:
  - test
  - orchestrator
source: "[[Ingest/Clippings/Test Source]]"
---

## Summary

Test article for CTP (Create Thread Postings) integration testing after migration.

## Improve Capture & Transcript (ICT)

### Key Insights

The orchestrator YAML format migration demonstrates several important principles:
- Single source of truth reduces configuration drift
- Explicit type declarations improve clarity
- Convention over configuration simplifies common cases

This article tests CTP's ability to convert technical articles into shareable social media content.
EOF

sleep 3

# Article 2
cat > "2025-10-30 CTP Test B $(date +%H%M%S).md" << 'EOF'
---
title: "CTP Test Article B - Agent Registry Refactoring"
created: 2025-10-30
tags:
  - test
  - refactoring
source: "[[Ingest/Clippings/Test Source]]"
---

## Summary

Testing CTP's processing of refactoring-focused content.

## Improve Capture & Transcript (ICT)

### Refactoring Impact

The agent registry refactoring improved:
- Testability through dependency injection
- Maintainability via clearer abstractions
- Reliability through comprehensive testing

CTP should extract these key points for social sharing.
EOF
```

**3. Monitor and Verify**

```bash
# Check task creation
cd ../_Tasks_
ls -lt | grep "CTP"

# Check output files
cd ../AI/Sharable
ls -lt | head -5

# Verify task status
grep -i "status:" ../_Tasks_/2025-10-30\ CTP*.md
```

#### Success Criteria

✅ **PASS** if:
- CTP tasks created for each article file
- Tasks complete with `PROCESSED` status
- Output files in `AI/Sharable/` directory
- Content formatted for social media (shorter, punchier)

---

### Test 3: Agent Loading Validation

**Purpose**: Verify all agents load correctly with new nodes format.

#### Steps

**1. Stop Orchestrator**

```bash
pkill -f orchestrator_cli
```

**2. Test Agent Loading**

```bash
cd ai4pkm_vault
python -c "
from ai4pkm_cli.orchestrator.agent_registry import AgentRegistry
from ai4pkm_cli.config import Config

config = Config()
registry = AgentRegistry(config)
registry.load_all_agents()

print(f'\nTotal agents loaded: {len(registry.agents)}')
print('\nAgent details:')
for abbr, agent in registry.agents.items():
    print(f'  {abbr}: {agent.name}')
    print(f'    Input: {agent.input_path}')
    print(f'    Output: {agent.output_path}')
    print(f'    Executor: {agent.executor}')
    print()
"
```

**Expected Output**:
```
Total agents loaded: 7

Agent details:
  EIC: Enrich Ingested Content
    Input: Ingest/Clippings
    Output: AI/Articles
    Executor: claude_code

  GDR: Generate Daily Roundup
    Input: []
    Output: AI/Roundup
    Executor: claude_code

  # ... all 7 agents listed
```

#### Success Criteria

✅ **PASS** if:
- 7 agents load successfully (EIC, GDR, PLL, CTP, PPP, GES, ARP)
- No abbreviation extraction errors
- All agents have correct configuration
- HTC (deprecated) is NOT in the list

---

## Observability & Debugging

### Key Log Patterns

**Agent Loading**:
```
INFO: Loading agents from orchestrator.yaml
INFO: Loading {N} agents from orchestrator.yaml
INFO: Loaded agent: {ABBR} ({Full Name})
```

**File Detection**:
```
INFO: File event: created {path}
INFO: Matched agent: {ABBR}
```

**Task Creation**:
```
INFO: Creating task for {ABBR}: {filename}
INFO: Task created: {task_path}
```

**Task Execution**:
```
INFO: Executing task: {task_name}
INFO: Task completed: {task_name}
```

### Common Issues

#### Issue: "Cannot extract abbreviation from: {name}"

**Cause**: Agent name doesn't follow `"Full Name (ABBR)"` format

**Fix**: Edit [orchestrator.yaml](../ai4pkm_vault/orchestrator.yaml):
```yaml
# Wrong:
- type: agent
  name: ARP

# Correct:
- type: agent
  name: Ad-hoc Research within PKM (ARP)
```

#### Issue: "No prompt file found for agent: {ABBR}"

**Cause**: Missing prompt file in `_Settings_/Prompts/`

**Fix**:
```bash
ls ai4pkm_vault/_Settings_/Prompts/{ABBR}*.md
```

Ensure file exists with name containing the abbreviation (e.g., `EIC.md`, `Enrich Ingested Content (EIC).md`)

#### Issue: Tasks stuck in IN_PROGRESS

**Cause**: Agent execution failed or still running

**Debug**:
1. Check orchestrator console for errors
2. Look for log files in task directory
3. Verify executor (claude_code) is available
4. Check timeout settings

#### Issue: No task created for new file

**Cause**: File created too quickly, watchdog missed event

**Fix**: Create files with 3+ second delays:
```bash
cat > file1.md << EOF
...
EOF

sleep 3

cat > file2.md << EOF
...
EOF
```

#### Issue: Multiple tasks for same file

**Cause**: Duplicate event detection or file modified multiple times

**Debug**:
1. Check task directory for duplicates
2. Review orchestrator logs for event patterns
3. Verify file only created once, not modified

---

## Cleanup

### Remove Test Files

```bash
cd ai4pkm_vault

# Remove test clipping files
rm -f Ingest/Clippings/2025-10-30\ Manual\ Test*.md
rm -f Ingest/Clippings/2025-10-30\ Test\ Migration*.md

# Remove test article files
rm -f AI/Articles/2025-10-30\ CTP\ Test*.md
rm -f AI/Articles/2025-10-30\ Manual\ Test*.md

# Remove test task files
rm -f _Tasks_/2025-10-30\ EIC\ -\ Manual\ Test*.md
rm -f _Tasks_/2025-10-30\ EIC\ -\ Test\ Migration*.md
rm -f _Tasks_/2025-10-30\ CTP\ -\ CTP\ Test*.md

# Remove test output files
rm -f AI/Sharable/2025-10-30\ CTP\ Test*.md

# Verify cleanup
find . -name "*Manual Test*" -o -name "*CTP Test*" -o -name "*Test Migration*"
# Should return nothing
```

### Stop Orchestrator

```bash
pkill -f orchestrator_cli

# Verify stopped
ps aux | grep orchestrator_cli
```

---

## Test Summary Template

Use this template to document test results:

```markdown
## Test Run Summary

**Date**: 2025-10-30
**Tester**: {Your Name}
**Branch**: feature/hashtag-handler-migration
**Commit**: {git hash}

### Test 1: EIC Agent
- [ ] Agent loaded successfully
- [ ] 4 tasks created
- [ ] No duplicate tasks
- [ ] All tasks reached PROCESSED status
- [ ] 4 output files generated
- [ ] Concurrency limit (max_parallel=3) respected

**Notes**: {any observations}

### Test 2: CTP Agent
- [ ] Agent loaded successfully
- [ ] Tasks created for article files
- [ ] Output files in AI/Sharable/
- [ ] Content properly formatted

**Notes**: {any observations}

### Test 3: Agent Loading
- [ ] 7 agents loaded
- [ ] No abbreviation errors
- [ ] HTC not present (deprecated)
- [ ] All configurations correct

**Notes**: {any observations}

### Issues Found
1. {Issue description}
   - **Severity**: Critical/Major/Minor
   - **Resolution**: {how fixed or workaround}

### Overall Result
✅ PASS / ❌ FAIL

**Recommendation**: {ready to merge / needs fixes / etc}
```

---

## Key Learnings

### File Creation Timing

**Critical**: When creating multiple test files, **always wait 3+ seconds between each file**.

**Why**: The file system watchdog (polling interval) needs time to detect and process each event separately. Creating files too quickly can cause:
- Events to be batched/missed
- Duplicate task creation
- Race conditions in task processing

**Pattern**:
```bash
# Create file 1
cat > file1.md << EOF
...
EOF

# WAIT - this is critical
sleep 3

# Create file 2
cat > file2.md << EOF
...
EOF
```

### Agent Name Format

All agent names **must** follow the pattern: `"Full Name (ABBR)"`

- Full descriptive name
- Space before parenthesis
- 3-4 uppercase letters in parentheses
- Examples:
  - ✅ `"Enrich Ingested Content (EIC)"`
  - ✅ `"Create Thread Postings (CTP)"`
  - ❌ `"EIC"`
  - ❌ `"Enrich Ingested Content"`

### Single Source of Truth

The migration established `orchestrator.yaml` as the **only** configuration source:

- ✅ All runtime config in `orchestrator.yaml` nodes
- ✅ Only metadata in prompt frontmatter (title, abbreviation, category)
- ❌ No configuration duplication
- ❌ No configuration in frontmatter

### Concurrency Testing

To properly test `max_parallel` limits:
1. Create more files than the limit (e.g., 4 files when max_parallel=3)
2. Monitor console logs for execution patterns
3. Verify no more than `max_parallel` tasks execute simultaneously
4. Confirm remaining tasks queue properly

---

## References

- [orchestrator.yaml](../ai4pkm_vault/orchestrator.yaml) - Main configuration
- [agent_registry.py](../ai4pkm_cli/orchestrator/agent_registry.py) - Agent loading logic
- [test_orchestrator_eic_integration.py](../ai4pkm_cli/tests/test_orchestrator_eic_integration.py) - Automated test example
- README files: [KTG](../README_KTG.md), [KTP](../README_KTP.md), [KTM](../README_KTM.md)

---

**Version History**:
- 1.0 (2025-10-30): Initial version covering EIC, CTP, and agent loading tests
