# Integration Tests for AI4PKM Knowledge Task Workflow

## Why Integration Tests?

The AI4PKM system implements a sophisticated knowledge task workflow with multiple components that must work together seamlessly:

```
Input Source → Handler → Request → KTG → Task (TBD) → Poller → KTP → KTE → Completed
```

**The Problem**: Each component works independently, but failures can occur at integration points:
- File system events might not trigger handlers (macOS FSEvents subprocess issue)
- Task status mismatches prevent processing (e.g., `status: "pending"` vs `"TBD"`)
- Agents might create malformed task files
- Race conditions in concurrent processing

**The Solution**: End-to-end integration tests that validate the entire workflow automatically, from file creation to task completion, catching issues that unit tests miss.

### Real Issues Discovered

These integration tests have identified and validated fixes for:

1. **macOS FSEvents Subprocess Bug** - Files created by Claude Code agent (KTG subprocess) weren't detected by file observers
   - **Solution**: Implemented TBDTaskPoller with 30-second polling interval
   - **Validation**: Tests confirm tasks are detected within 30-60 seconds

2. **Status Mismatch Bug** - KTG created tasks with `status: "pending"` but KTP only processes `status: "TBD"`
   - **Solution**: Updated prompts and templates to enforce `"TBD"` status
   - **Validation**: Tests verify all tasks are created with correct status

3. **Request Deletion Timing** - Request files deleted before KTG could process them
   - **Solution**: KTG now deletes requests after processing
   - **Validation**: Tests monitor request lifecycle

## What We Test

### Three Complete Workflows

#### 1. EIC (Enrich Ingested Content) Workflow
**Trigger**: New clipping file in `Ingest/Clippings/`
**Handler**: ClippingFileHandler
**Task Type**: EIC (enrichment of web article clippings)

```
Clipping.md → ClippingFileHandler → Request JSON →
KTG creates EIC task → TBDTaskPoller detects → KTP enriches → KTE validates → COMPLETED
```

**Validates**:
- Clipping file detection
- Request JSON generation with metadata
- EIC task creation with proper frontmatter
- Content enrichment execution
- Completion criteria evaluation

#### 2. Hashtag (#AI) Workflow
**Trigger**: `#AI` hashtag in any markdown file
**Handler**: HashtagFileHandler
**Task Type**: Writing (article/document creation)

```
file.md with #AI → HashtagFileHandler → Request JSON →
KTG creates Writing task → TBDTaskPoller detects → KTP writes → KTE validates → COMPLETED
```

**Validates**:
- Hashtag detection across all markdown files
- Hashtag removal from source file after processing
- Writing task generation
- Content creation workflow
- Output file generation

#### 3. Limitless ("Hey PKM") Workflow
**Trigger**: "hey pkm" phrase in Limitless conversation
**Handler**: LimitlessFileHandler
**Task Type**: Various (determined by request content)

```
Limitless conversation → LimitlessFileHandler (detects "hey pkm") →
Request JSON with context → KTG creates task → TBDTaskPoller → KTP executes → COMPLETED
```

**Validates**:
- Natural language trigger detection (case-insensitive)
- Context extraction (±5 conversation entries)
- Preference keyword detection (Korean: 좋겠고, 원해, 필요해)
- Conversation-to-task translation
- Complete workflow execution

### Test Stages

Each test validates 6-7 stages:

1. **Watchdog Startup** - ai4pkm -t subprocess starts successfully
2. **File Creation** - Test input file created from fixture
3. **Request Generation** - Handler detects file and creates JSON request
4. **Task Creation** - KTG agent processes request and creates task file
5. **Task Detection** - TBDTaskPoller finds task within 30-60 seconds
6. **Task Processing** - KTP executes task through all phases
7. **Task Completion** - KTE evaluates and marks as COMPLETED

## How to Run Tests

### Prerequisites

- AI4PKM installed and configured
- `ai4pkm` command available in PATH
- Claude Code agent configured
- All required directories exist (AI/Tasks, Ingest/, etc.)

### Quick Start

```bash
# Run all tests (recommended)
./ai4pkm_cli/tests/run_all_integration_tests.sh

# Run individual test
python ai4pkm_cli/tests/test_ktg_ktp_eic_integration.py
python ai4pkm_cli/tests/test_ktg_ktp_hashtag_integration.py
python ai4pkm_cli/tests/test_ktg_ktp_limitless_integration.py
```

### Expected Output

```
╔════════════════════════════════════════════════════════════════╗
║        KTG/KTP/KTE Integration Test Suite                     ║
╚════════════════════════════════════════════════════════════════╝

═══════════════════════════════════════════════════════════════
  TEST 1/3: EIC (Enrich Ingested Content) Workflow
═══════════════════════════════════════════════════════════════
🧹 Cleaning up old test artifacts...
   ✅ Cleanup complete

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Running: EIC Test
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Stages progress with timestamps...]

   ✅ EIC Test PASSED

[Similar output for Hashtag and Limitless tests...]

╔════════════════════════════════════════════════════════════════╗
║                   TEST SUITE SUMMARY                           ║
╚════════════════════════════════════════════════════════════════╝

  Total Tests:  3
  Passed:       3
  Failed:       0

  🎉 All tests passed!
```

### Test Duration

| Test | Typical | Max Acceptable |
|------|---------|----------------|
| EIC | 2-3 min | 4 min |
| Hashtag | 2-3 min | 4 min |
| Limitless | 2-3 min | 4 min |
| **Total** | **6-9 min** | **12 min** |

### Test Reports

Each test generates a detailed markdown report:

- `KTG_KTP_Integration_Test_Results.md` (EIC)
- `KTG_KTP_Hashtag_Integration_Test_Results_{timestamp}.md`
- `KTG_KTP_Limitless_Integration_Test_Results_{timestamp}.md`

Reports include:
- Test duration and timestamp
- Stage-by-stage results with timings
- Issues found during execution
- Created files and artifacts
- Pass/Fail status

## How Tests Work

### Architecture

```python
class KTGKTPIntegrationTest:
    """Self-contained integration test with full workflow simulation."""

    def start_watchdog(self):
        """Launch ai4pkm -t subprocess with logging"""
        # Creates process group for clean shutdown
        # Redirects output to watchdog_output.log
        # Waits 10s for initialization

    def create_test_file(self):
        """Create test input from editable fixture"""
        # Reads template from fixtures/ folder
        # Generates timestamped filename
        # Tracks created files for cleanup

    def wait_for_request_generation(self, timeout=60):
        """Monitor AI/Tasks/Requests/{source}/ for JSON"""
        # Polls directory every 2 seconds
        # Validates JSON structure
        # Returns request file path

    def wait_for_task_creation(self, timeout=120):
        """Monitor AI/Tasks/ for new task file"""
        # Filters by timestamp (after test start)
        # Excludes self-created files
        # Validates frontmatter status

    def wait_for_task_detection(self, timeout=60):
        """Check watchdog logs for polling detection"""
        # Reads watchdog_output.log incrementally
        # Searches for "🔄 Polling detected TBD task"
        # Confirms TBDTaskPoller is working

    def wait_for_task_processing(self, timeout=300):
        """Monitor task status transitions"""
        # Polls task file every 5 seconds
        # Tracks: TBD → IN_PROGRESS → PROCESSED

    def wait_for_task_completion(self, timeout=600):
        """Wait for COMPLETED status"""
        # Monitors final evaluation
        # Validates output files exist
        # Confirms KTE approval

    def stop_watchdog(self):
        """Graceful watchdog shutdown"""
        # Sends SIGTERM to process group
        # Waits 15s for graceful exit
        # Force kills if necessary

    def generate_report(self):
        """Create markdown test results"""
        # Summarizes all stages
        # Lists issues found
        # Records timing data
```

### Key Design Decisions

1. **Self-Contained**: Each test manages its own watchdog process
   - No dependency on manual setup
   - Clean start/stop for each run
   - Isolated from system state

2. **Timestamp Filtering**: Only detects files created after test start
   - Prevents false positives from old files
   - Handles concurrent test runs
   - Tracks file creation accurately

3. **Incremental Log Reading**: Monitors watchdog logs without re-reading
   - Efficient for long-running tests
   - Detects specific log messages (polling events)
   - Validates asynchronous operations

4. **Editable Fixtures**: Test data in separate markdown files
   - Easy to modify scenarios
   - Realistic content for testing
   - No hardcoded test data in code

5. **Cleanup Policy**: Disabled by default
   - Preserves artifacts for debugging
   - Manual cleanup via script before each run
   - Helps diagnose failures

### Critical Component: TBDTaskPoller

**Background**: macOS FSEvents doesn't reliably detect files created by subprocesses (Claude Code agent).

**Symptoms**:
- Manual file creation → Detected instantly ✅
- KTG subprocess file creation → Never detected ❌

**Solution**: Hybrid approach
- **FSEvents Observer**: Fast detection for parent process files
- **TBDTaskPoller**: Periodic scanning (30s interval) for subprocess files

**Implementation**:
```python
class TBDTaskPoller:
    """Scans AI/Tasks/*.md for status: "TBD" every 30 seconds."""

    def _scan_for_tbd_tasks(self):
        # Read first 500 chars of each task file (frontmatter)
        # Check for status: "TBD"
        # Trigger TaskProcessor if found
        # Cache processed files to avoid duplicates
```

**Configuration**:
```json
{
  "task_management": {
    "polling_interval": 30  // seconds
  }
}
```

**Test Validation**:
- All tests confirm TBD tasks detected within 30-60 seconds
- Watchdog logs show: `🔄 Polling detected TBD task: {filename}`
- Processing starts immediately after detection

## Test Fixtures

Location: [fixtures/](fixtures/)

### 1. EIC Fixture
**File**: `test_clipping_template.md`
**Format**: Article clipping with frontmatter

```markdown
---
title: "Test Integration Article"
source: "https://example.com/test-article"
author:
  - "Test Author"
created: 2025-10-17
tags:
  - clippings
  - test
---

# Test Article Content

> Important quote from article

Key insights and analysis...
```

### 2. Hashtag Fixture
**File**: `test_hashtag_template.md`
**Format**: Project file with #AI hashtag

```markdown
---
title: "Test Writing Task with AI Hashtag"
created: 2025-10-17
tags:
  - test
  - projects
---

# Content Outline

#AI - Please help me write about:
- Topic 1
- Topic 2
- Topic 3
```

### 3. Limitless Fixture
**File**: `test_limitless_template.md`
**Format**: Conversation transcript

```markdown
# PKM 시스템 개선 논의
## 자동화 개선 방안 대화
- You (10/17/25 10:30 AM): 오늘 PKM 시스템 개선 방안을 논의해볼까?
- Unknown (10/17/25 10:32 AM): Hey PKM, 통합 테스트 시스템을 구축하는 태스크를 만들어줘.
  전체 워크플로우가 end-to-end로 테스트되면 좋겠고...
```

**To customize tests**: Edit these fixtures before running tests.

## Troubleshooting

### Test hangs at "Waiting for task detection"

**Cause**: TBDTaskPoller not running or interval too long

**Fix**:
```bash
# 1. Check config has polling enabled
grep polling_interval ai4pkm_cli.json

# 2. Verify watchdog log shows poller starting
grep "Starting TBD task poller" ai4pkm_cli/tests/watchdog_output.log

# 3. Wait at least 60 seconds for first poll
```

### Test finds wrong task file

**Cause**: Old task files from previous runs

**Fix**:
```bash
# Clean up before running
rm -f AI/Tasks/2025-10-17*.md
./ai4pkm_cli/tests/run_all_integration_tests.sh
```

### Watchdog won't stop

**Cause**: Process group not killed

**Fix**:
```bash
# Force kill
pkill -f "ai4pkm -t"

# Verify
ps aux | grep ai4pkm
```

### Status mismatch errors

**Cause**: Outdated KTG prompt

**Fix**: Ensure `ai4pkm_cli/prompts/task_generation.md` has:
```markdown
status: "TBD" (CRITICAL: Must be exactly "TBD" in quotes)
NEVER use "pending" or other values
```

### Request file not created

**Cause**: Handler not triggering

**Check**:
```bash
# View watchdog logs
tail -50 ai4pkm_cli/tests/watchdog_output.log | grep -i clipping
```

**Common issues**:
- File in excluded directory (ai4pkm_cli/, .git/)
- Handler pattern doesn't match file path
- Permission errors

## Performance Benchmarks

Target latencies per stage:

| Stage | Target | Acceptable | Notes |
|-------|--------|------------|-------|
| Request Generation | <1s | <5s | Handler triggers instantly |
| Task Creation (KTG) | 20-40s | <90s | Claude Code subprocess |
| Task Detection | 0-30s | <60s | TBDTaskPoller interval |
| Task Processing (KTP) | 60-120s | <300s | Task complexity dependent |
| Task Evaluation (KTE) | 10-30s | <60s | Validation logic |
| **End-to-End** | **2-3 min** | **<5 min** | Total workflow time |

**Optimization Opportunities**:
1. Reduce polling interval to 10s for faster detection (tradeoff: CPU usage)
2. Parallel task processing (currently sequential with semaphore)
3. Cached agent responses for similar tasks

## Files Reference

**Test Scripts**:
- [test_ktg_ktp_eic_integration.py](test_ktg_ktp_eic_integration.py) - EIC workflow test
- [test_ktg_ktp_hashtag_integration.py](test_ktg_ktp_hashtag_integration.py) - Hashtag workflow test
- [test_ktg_ktp_limitless_integration.py](test_ktg_ktp_limitless_integration.py) - Limitless workflow test
- [run_all_integration_tests.sh](run_all_integration_tests.sh) - Test suite runner

**Test Fixtures**:
- [fixtures/test_clipping_template.md](fixtures/test_clipping_template.md)
- [fixtures/test_hashtag_template.md](fixtures/test_hashtag_template.md)
- [fixtures/test_limitless_template.md](fixtures/test_limitless_template.md)

**System Components**:
- [../watchdog/tbd_poller.py](../watchdog/tbd_poller.py) - TBD task polling
- [../watchdog/handlers/](../watchdog/handlers/) - All file handlers
- [../prompts/task_generation.md](../prompts/task_generation.md) - KTG system prompt

## Test Automation

### CI/CD Integration

Add integration tests to your CI/CD pipeline:

**GitHub Actions** (`.github/workflows/integration-tests.yml`):
```yaml
name: Integration Tests
on: [pull_request, push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: ./ai4pkm_cli/tests/run_all_integration_tests.sh
```

**Pre-commit Hook** (`.git/hooks/pre-commit`):
```bash
#!/bin/bash
./ai4pkm_cli/tests/run_all_integration_tests.sh || exit 1
```

**Makefile**:
```makefile
test-integration:
	./ai4pkm_cli/tests/run_all_integration_tests.sh
```

### Scheduled Testing

**Cron (daily at 2 AM)**:
```bash
0 2 * * * cd /path/to/AI4PKM && ./ai4pkm_cli/tests/run_all_integration_tests.sh
```

---

**Last Updated**: 2025-10-17
**Test Coverage**: 3 workflows, 18+ stages
**Status**: ✅ Production Ready
