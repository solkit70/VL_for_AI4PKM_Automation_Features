---
title: "Orchestrator Integration Test Plan"
created: 2025-10-27
tags:
  - orchestrator
  - testing
  - integration
  - validation
author:
  - "[[Claude]]"
related:
  - "[[2025-10-27 Orchestrator User Guide]]"
  - "[[2025-10-25 Orchestrator Detailed Design]]"
  - "[[2025-10-25 Phase 1 - Parallel Implementation]]"
---

# Orchestrator Integration Test Plan

## Overview

This document outlines the integration testing strategy for validating the orchestrator with real agent executions. We'll test each agent by creating appropriate trigger files and verifying the complete execution flow.

**Test Strategy**: Create minimal test input files → Run orchestrator → Verify outputs

**Status**: Ready to execute (Phase 1 validation)

---

## Test Environment Setup

### Prerequisites

```bash
# 1. Ensure we're on the orchestrator branch
git checkout feature/hashtag-handler-migration

# 2. Install package in development mode
pip install -e . --force-reinstall --no-deps

# 3. Verify tests pass
python -m pytest ai4pkm_cli/tests/unit/orchestrator/ -v
# Expected: 47/47 passing ✅

# 4. Check orchestrator status
python -m ai4pkm_cli.orchestrator_cli status
# Expected: 8 agents loaded
```

### Test Directory Structure

```
ai4pkm_vault/
├── _Settings_/Agents/          # Agent definitions (already exist)
├── TestFiles/                  # NEW: Test input files
│   ├── test-htc-hashtag.md     # HTC trigger test
│   ├── test-eic-clipping.md    # EIC trigger test
│   ├── test-arp-research.md    # ARP trigger test
│   └── ...
├── AI/Tasks/                   # Output: Task tracking files
│   └── Logs/                   # Output: Execution logs
└── AI/                         # Output: Agent-specific outputs
    ├── Clipping/
    ├── Research/
    ├── Sharable/
    └── Roundup/
```

---

## Agent Test Matrix

Based on analysis of agent definitions in `_Settings_/Agents/`:

| # | Agent | Abbreviation | Trigger | Test File | Expected Output |
|---|-------|--------------|---------|-----------|-----------------|
| 1 | **Hashtag Task Creator** | HTC | `%% #ai %%` in any .md | `TestFiles/test-htc.md` | Task in `_Tasks_/` |
| 2 | **Enrich Ingested Content** | EIC | New file in `Ingest/Clipping` | `Ingest/Clipping/test.md` | Enhanced in `AI/Clipping/` |
| 3 | **Ad-hoc Research** | ARP | Manual trigger | Manual | Research in `AI/Research/` |
| 4 | **Create Thread Postings** | CTP | Manual trigger | Manual | Threads in `AI/Sharable/` |
| 5 | **Daily Roundup** | GDR | Manual/scheduled | Manual | Roundup in `AI/Roundup/` |
| 6 | **General Essay Synthesizer** | GES | Manual trigger | Manual | Essay output |
| 7 | **Lifelog Processor** | PLL | Manual trigger | Manual | Processed lifelog |
| 8 | **Publishing Prep** | PPP | Manual trigger | Manual | Publishable content |

**Note**: Agents without `trigger_pattern` in frontmatter are **manual-only** (no automatic file triggers).

---

## Test Cases

### Test 1: HTC - Hashtag Task Creator ✅ READY

**Trigger**: File modified with `%% #ai %%` comment

**Agent Config**:
```yaml
trigger_pattern: "**/*.md"
trigger_event: "modified"
trigger_exclude_pattern: "_Tasks_/*.md"
trigger_content_pattern: "%%\\s*#ai\\s*%%"
post_process_action: "remove_trigger_content"
```

**Test File**: `TestFiles/test-htc-hashtag.md`
```markdown
---
title: Test HTC Hashtag Detection
created: 2025-10-27
---

# Test Note for Hashtag Task Creator

This is a test note to validate the HTC agent.

%% #ai %%

I need this content to be analyzed and processed by the orchestrator.
Please create a task based on this request.

## Background
This is a test of the hashtag-based task creation system.
```

**Steps**:
```bash
# 1. Create test file
mkdir -p TestFiles
cat > TestFiles/test-htc-hashtag.md << 'EOF'
---
title: Test HTC Hashtag Detection
created: 2025-10-27
---

# Test Note

%% #ai %%

Please analyze this content and create a task.
EOF

# 2. Start orchestrator (in separate terminal)
python -m ai4pkm_cli.orchestrator_cli daemon

# 3. Trigger the agent by modifying the file
echo "" >> TestFiles/test-htc-hashtag.md

# 4. Verify outputs
ls -la _Tasks_/              # Should show new task file
ls -la AI/Tasks/Logs/        # Should show HTC log file
```

**Expected Results**:
- ✅ HTC agent detects `%% #ai %%` pattern
- ✅ Task file created: `_Tasks_/2025-10-27 Test HTC Hashtag Detection - HTC.md`
- ✅ Execution log: `AI/Tasks/Logs/2025-10-27-HHMMSS-htc.log`
- ✅ `%% #ai %%` removed from source file (post-processing)
- ✅ Task status: `PENDING`

**Validation**:
```bash
# Check task file exists
test -f "_Tasks_/2025-10-27 Test HTC Hashtag Detection - HTC.md" && echo "✅ Task created" || echo "❌ Task missing"

# Check log file exists
ls AI/Tasks/Logs/*-htc.log &>/dev/null && echo "✅ Log created" || echo "❌ Log missing"

# Check hashtag removed
grep "%% #ai %%" TestFiles/test-htc-hashtag.md && echo "❌ Hashtag not removed" || echo "✅ Hashtag removed"
```

---

### Test 2: EIC - Enrich Ingested Content ✅ READY

**Trigger**: New file in `Ingest/Clipping/`

**Agent Config**:
```yaml
trigger_pattern: "Ingest/Clipping/*.md"
trigger_event: "created"
input_path: "Ingest/Clipping"
output_path: "AI/Clipping"
```

**Test File**: `Ingest/Clipping/test-eic-clipping.md`
```markdown
---
title: Test Article for EIC
source: https://example.com/test
created: 2025-10-27
---

# Test Article Title

This is a test article with some grammar errors and transcript issues.
The agent should fix these issues and add chapters.

First paragraph about interesting topic number one here.

Second paragraph with more details and informations here.
This should be improved by the EIC agent through transcript correction.

Third paragraph with conclusion and final thoughts.
```

**Steps**:
```bash
# 1. Ensure directory exists
mkdir -p Ingest/Clipping

# 2. Create test clipping (triggers EIC)
cat > Ingest/Clipping/test-eic-clipping.md << 'EOF'
---
title: Test Article for EIC
source: https://example.com/test
created: 2025-10-27
---

# Test Article

This article has grammar errors and needs improvement.

First paragraph here with some transcript issue.
Second paragraph with more detail.
Third paragraph with conclusions.
EOF

# 3. Orchestrator should auto-detect and trigger EIC

# 4. Check outputs
ls -la AI/Clipping/          # Should show enriched version
ls -la AI/Tasks/Logs/        # Should show EIC log
```

**Expected Results**:
- ✅ EIC agent detects new file in `Ingest/Clipping/`
- ✅ Enriched file created: `AI/Clipping/test-eic-clipping.md`
- ✅ Execution log: `AI/Tasks/Logs/2025-10-27-HHMMSS-eic.log`
- ✅ Status property set to `processed` in output file
- ✅ Summary section added
- ✅ Grammar/transcript errors corrected
- ✅ Chapters added with `###` headings

**Validation**:
```bash
# Check enriched file exists
test -f "AI/Clipping/test-eic-clipping.md" && echo "✅ Enriched file created" || echo "❌ File missing"

# Check for status property
grep "status: processed" AI/Clipping/test-eic-clipping.md &>/dev/null && echo "✅ Status updated" || echo "❌ Status not set"

# Check for summary section
grep "## Summary" AI/Clipping/test-eic-clipping.md &>/dev/null && echo "✅ Summary added" || echo "❌ Summary missing"
```

---

### Test 3: Manual Agent Triggers (ARP, CTP, GDR, etc.)

**Status**: ⚠️ NEEDS TRIGGER CONFIGURATION

**Issue**: These agents don't have `trigger_pattern` or `trigger_event` in their frontmatter:
- ARP (Ad-hoc Research)
- CTP (Create Thread Postings)
- GDR (Daily Roundup)
- GES (General Essay Synthesizer)
- PLL (Lifelog Processor)
- PPP (Publishing Prep)

**Current State**: These are **manual-only** agents (no file-based triggers configured)

**Options**:
1. **Add trigger patterns** to agent frontmatter (requires updating agent definitions)
2. **Add manual trigger API** to orchestrator (future enhancement)
3. **Skip for Phase 1** - focus on HTC and EIC validation

**Recommendation**: Test HTC and EIC first, then decide if manual agents need trigger configs.

---

## Integration Test Execution

### Full Test Run Script

```bash
#!/bin/bash
# integration-test.sh - Run full orchestrator integration tests

echo "=== Orchestrator Integration Test Suite ==="
echo ""

# Setup
echo "1. Setup test environment..."
mkdir -p TestFiles
mkdir -p Ingest/Clipping
mkdir -p AI/Tasks/Logs

# Clean previous test files
rm -f TestFiles/test-*.md
rm -f Ingest/Clipping/test-*.md

echo "✅ Test environment ready"
echo ""

# Test 1: HTC
echo "2. Test HTC (Hashtag Task Creator)..."
cat > TestFiles/test-htc.md << 'EOF'
---
title: HTC Integration Test
created: 2025-10-27
---

# HTC Test Note

%% #ai %%

Please create a task for processing this note.
EOF

echo "   Created test file: TestFiles/test-htc.md"
echo "   Waiting for HTC agent to process..."
sleep 5

# Trigger by modifying
echo "" >> TestFiles/test-htc.md
sleep 10

# Check results
if test -f "_Tasks_/2025-10-27 HTC Integration Test - HTC.md"; then
    echo "   ✅ HTC task file created"
else
    echo "   ❌ HTC task file NOT created"
fi

if grep "%% #ai %%" TestFiles/test-htc.md &>/dev/null; then
    echo "   ❌ Hashtag NOT removed (post-process failed)"
else
    echo "   ✅ Hashtag removed successfully"
fi

echo ""

# Test 2: EIC
echo "3. Test EIC (Enrich Ingested Content)..."
cat > Ingest/Clipping/test-eic.md << 'EOF'
---
title: EIC Integration Test
source: https://example.com/test
created: 2025-10-27
---

# Test Article

This article needs enrichment and improvement.

Paragraph one with content here.
Paragraph two with more details.
EOF

echo "   Created test file: Ingest/Clipping/test-eic.md"
echo "   Waiting for EIC agent to process..."
sleep 15

# Check results
if test -f "AI/Clipping/test-eic.md"; then
    echo "   ✅ EIC enriched file created"

    if grep "status: processed" AI/Clipping/test-eic.md &>/dev/null; then
        echo "   ✅ Status property updated"
    else
        echo "   ❌ Status property NOT updated"
    fi

    if grep "## Summary" AI/Clipping/test-eic.md &>/dev/null; then
        echo "   ✅ Summary section added"
    else
        echo "   ❌ Summary section NOT added"
    fi
else
    echo "   ❌ EIC enriched file NOT created"
fi

echo ""

# Summary
echo "4. Test Summary"
echo "   Task files: $(ls -1 _Tasks_/*.md 2>/dev/null | wc -l)"
echo "   Log files: $(ls -1 AI/Tasks/Logs/*.log 2>/dev/null | wc -l)"
echo ""
echo "=== Integration Test Complete ==="
```

**Usage**:
```bash
# Terminal 1: Start orchestrator
python -m ai4pkm_cli.orchestrator_cli daemon

# Terminal 2: Run tests
chmod +x integration-test.sh
./integration-test.sh
```

---

## Success Criteria

### Phase 1 Integration Test Goals

**Minimum Requirements**:
- [ ] HTC agent successfully creates task from `%% #ai %%` hashtag
- [ ] HTC post-processing removes hashtag from source file
- [ ] EIC agent successfully enriches clipping file
- [ ] EIC sets status property to `processed`
- [ ] Task tracking files created in `_Tasks_/`
- [ ] Execution logs written to `AI/Tasks/Logs/`
- [ ] No agent execution errors or timeouts
- [ ] Concurrency control works (max 3 concurrent)

**Extended Validation**:
- [ ] Orchestrator handles multiple rapid triggers
- [ ] File monitor detects all file changes
- [ ] Agent registry correctly matches triggers
- [ ] Execution manager properly increments/decrements counters
- [ ] Log files contain full prompt and response
- [ ] Claude CLI path discovery works
- [ ] All file operations complete without errors

---

## Test Results Template

```markdown
## Test Run: 2025-10-27 HH:MM

### Environment
- Branch: feature/hashtag-handler-migration
- Commit: [sha]
- Python: 3.x.x
- Pytest: 47/47 passing

### Test 1: HTC
- Status: ✅ PASS / ❌ FAIL
- Task created: [YES/NO]
- Hashtag removed: [YES/NO]
- Execution time: [X.Xs]
- Issues: [None / Description]
- Log file: [path]

### Test 2: EIC
- Status: ✅ PASS / ❌ FAIL
- File enriched: [YES/NO]
- Status updated: [YES/NO]
- Summary added: [YES/NO]
- Execution time: [X.Xs]
- Issues: [None / Description]
- Log file: [path]

### Overall
- Total agents tested: 2/8
- Pass rate: [X%]
- Total execution time: [Xs]
- Concurrency peak: [X]
- Errors encountered: [count]

### Notes
[Any observations, issues, or insights]
```

---

## Known Issues & Limitations

### Current Limitations

1. **Manual-only agents**: 6 agents (ARP, CTP, GDR, GES, PLL, PPP) don't have file triggers configured
   - **Impact**: Can't test automatically
   - **Workaround**: Add trigger patterns or test manually later

2. **HTC pattern mismatch**: Uses `%%\\s*#ai\\s*%%` regex but expects `%% #ai %%`
   - **Impact**: May not match variations like `%%#ai%%` or `%% #ai%%`
   - **Fix**: Test with exact spacing

3. **No integration test automation**: Tests require manual execution
   - **Impact**: Can't run in CI/CD
   - **Future**: Add pytest integration test

4. **Claude CLI required**: Tests fail if Claude not installed
   - **Impact**: Can't run on fresh systems
   - **Fix**: Mock Claude CLI in tests

---

## Next Steps After Testing

### If Tests Pass ✅

1. **Document results** in test results section
2. **Commit changes**:
   - Test fixes (47/47 passing)
   - User guide
   - Integration test plan
3. **Update PR #29** with test validation
4. **Proceed to Phase 2**: Convert KTM agents (KTG, KTP, KTE)

### If Tests Fail ❌

1. **Debug failures**:
   - Check orchestrator logs
   - Review agent trigger patterns
   - Verify file paths and permissions
   - Test Claude CLI manually

2. **Fix issues**:
   - Update agent configurations
   - Fix execution manager bugs
   - Correct file monitor patterns

3. **Re-run tests** until passing

4. **Document lessons learned**

---

## Appendix: Agent Trigger Summary

### Agents with File Triggers (Testable)

| Agent | Abbreviation | Pattern | Event | Content Pattern |
|-------|--------------|---------|-------|----------------|
| **HTC** | HTC | `**/*.md` | modified | `%%\\s*#ai\\s*%%` |
| **EIC** | EIC | `Ingest/Clipping/*.md` | created | - |

### Agents without File Triggers (Manual Only)

| Agent | Abbreviation | Category | Reason |
|-------|--------------|----------|--------|
| **ARP** | ARP | research | No trigger_pattern defined |
| **CTP** | CTP | publish | No trigger_pattern defined |
| **GDR** | GDR | research | No trigger_pattern defined |
| **GES** | GES | research | No trigger_pattern defined |
| **PLL** | PLL | research | No trigger_pattern defined |
| **PPP** | PPP | publish | No trigger_pattern defined |

**Action Required**: Either:
1. Add trigger patterns to these agents' frontmatter
2. Implement manual trigger API
3. Accept manual-only operation for Phase 1

---

*Last Updated: 2025-10-27*
*Status: Ready for Execution*
*Next: Run integration tests and document results*
