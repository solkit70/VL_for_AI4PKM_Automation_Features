# Integration Tests Guide

This guide explains how to run the KTG/KTP/KTE integration tests for the AI4PKM system.

## Overview

The integration test suite validates the complete end-to-end workflow of the AI4PKM orchestrator system, including:

1. **EIC (Enrich Ingested Content)** - Tests clipping file processing workflow
2. **Hashtag (#AI)** - Tests hashtag-triggered task creation workflow
3. **Limitless ("Hey PKM")** - Tests voice memo processing workflow

Each test validates:
- File detection and event triggering
- Task request generation
- Task creation by KTG (Knowledge Task Generator)
- Task processing by KTP (Knowledge Task Processor)
- Task evaluation by KTE (Knowledge Task Evaluator)
- No duplicate processing
- Proper status transitions
- Artifact cleanup

## Prerequisites

- AI4PKM installed and configured
- Working directory: `/Users/lifidea/dev/AI4PKM`
- Valid `ai4pkm_cli.json` configuration file in repo root
- **Test vault:** `ai4pkm_vault/` (demo/test-purpose vault)
- Required folders in test vault: `AI/Tasks`, `Ingest/Clippings`, `Ingest/Limitless`, `Projects`, `_Settings_/Prompts`

## Test Vault Location

Integration tests use **`ai4pkm_vault/`** as the test workspace. This is a demo/test-purpose vault that keeps test artifacts separate from any production data.

**Vault structure:**
```
/Users/lifidea/dev/AI4PKM/
├── ai4pkm_cli.json                    # Config file (repo root)
└── ai4pkm_vault/                      # Test vault
    ├── AI/
    │   └── Tasks/                     # Task files created by tests
    ├── Ingest/
    │   ├── Clippings/                 # EIC test files
    │   └── Limitless/                 # Limitless test files
    ├── Projects/                      # Hashtag test files
    └── _Settings_/
        └── Prompts/                   # Agent definitions
```

**Why separate vault?**
- Keeps test artifacts isolated
- Safe for CI/CD without production data
- Can be cleaned up easily
- Pre-configured with demo agents

## Running All Tests

### Quick Start (Default Mode)

Run all three integration tests sequentially with daemon management:

```bash
cd /Users/lifidea/dev/AI4PKM
./ai4pkm_cli/tests/run_all_integration_tests.sh
```

**What happens:**
- Script starts daemon for each test
- Runs EIC test → stops daemon
- Runs Hashtag test → stops daemon
- Runs Limitless test → stops daemon
- Shows summary of all tests

**Total time:** ~10-20 minutes (depending on LLM API speed)

### Using Existing Daemon (Faster for Development)

If you already have a daemon running, skip the start/stop overhead:

```bash
# Terminal 1: Start daemon manually
cd /Users/lifidea/dev/AI4PKM
python -m ai4pkm_cli.orchestrator_cli daemon

# Terminal 2: Run tests using existing daemon
cd /Users/lifidea/dev/AI4PKM
./ai4pkm_cli/tests/run_all_integration_tests.sh --use-existing-daemon
```

**Benefits:**
- Much faster test iterations (~30% faster)
- Single daemon for all tests
- Better for debugging with verbose logging
- See daemon output in real-time

**Total time:** ~7-15 minutes

## Running Individual Tests

### Default Mode (Start/Stop Daemon)

```bash
cd /Users/lifidea/dev/AI4PKM

# Test 1: EIC workflow
python ai4pkm_cli/tests/test_ktg_ktp_eic_integration.py

# Test 2: Hashtag workflow
python ai4pkm_cli/tests/test_ktg_ktp_hashtag_integration.py

# Test 3: Limitless workflow
python ai4pkm_cli/tests/test_ktg_ktp_limitless_integration.py
```

### Using Existing Daemon

```bash
cd /Users/lifidea/dev/AI4PKM

# Test 1: EIC workflow
python ai4pkm_cli/tests/test_ktg_ktp_eic_integration.py --use-existing-daemon

# Test 2: Hashtag workflow
python ai4pkm_cli/tests/test_ktg_ktp_hashtag_integration.py --use-existing-daemon

# Test 3: Limitless workflow
python ai4pkm_cli/tests/test_ktg_ktp_limitless_integration.py --use-existing-daemon
```

## Test Workflow Details

### Test 1: EIC (Enrich Ingested Content)

**Duration:** ~3-5 minutes

**What it tests:**
1. Creates test clipping file in `Ingest/Clippings/`
2. Waits for ClippingFileHandler to detect file
3. Waits for task request JSON in `AI/Tasks/Requests/Clipping/`
4. Waits for KTG to create task in `AI/Tasks/`
5. Monitors task status changes (TBD → IN_PROGRESS → PROCESSED → COMPLETED)
6. Validates no duplicate tasks created
7. Checks for output file

**Test file:** [test_ktg_ktp_eic_integration.py](test_ktg_ktp_eic_integration.py)

**Test template:** [fixtures/test_clipping_template.md](fixtures/test_clipping_template.md)

### Test 2: Hashtag (#AI)

**Duration:** ~5-10 minutes

**What it tests:**
1. Creates test file with `#AI` hashtag in `Projects/`
2. Waits for HashtagFileHandler to detect hashtag
3. Waits for Writing task request in `AI/Tasks/Requests/Hashtag/`
4. Waits for KTG to create Writing task in `AI/Tasks/`
5. Waits for TBDTaskPoller to detect task (30s polling interval)
6. Monitors task processing to completion
7. Validates task execution

**Test file:** [test_ktg_ktp_hashtag_integration.py](test_ktg_ktp_hashtag_integration.py)

**Test template:** [fixtures/test_hashtag_template.md](fixtures/test_hashtag_template.md)

### Test 3: Limitless ("Hey PKM")

**Duration:** ~5-10 minutes

**What it tests:**
1. Creates Limitless conversation file with "hey pkm" trigger in `Ingest/Limitless/`
2. Waits for LimitlessFileHandler to detect trigger phrase
3. Waits for task request in `AI/Tasks/Requests/Limitless/`
4. Validates complete task workflow
5. Checks for proper metadata extraction

**Test file:** [test_ktg_ktp_limitless_integration.py](test_ktg_ktp_limitless_integration.py)

**Test template:** [fixtures/test_limitless_template.md](fixtures/test_limitless_template.md)

## Test Modes Comparison

| Feature | Default Mode | Existing Daemon Mode |
|---------|-------------|---------------------|
| Daemon management | Auto start/stop per test | Use existing |
| Speed | Slower (~10-20 min total) | Faster (~7-15 min total) |
| Debugging | Limited visibility | Full daemon output |
| Setup | Zero (fully automated) | Manual daemon start |
| Best for | CI/CD, one-off runs | Development, iteration |

## Test Artifacts

Tests create temporary files for validation:

### Created Files

Tests create files in the `ai4pkm_vault/` directory:

```
ai4pkm_vault/
├── AI/Tasks/2025-10-17*.md                      # Generated task files
├── AI/Tasks/Requests/
│   ├── Clipping/*.json                          # EIC request files
│   ├── Hashtag/*.json                           # Hashtag request files
│   └── Limitless/*.json                         # Limitless request files
├── Ingest/
│   ├── Clippings/2025-10-17 Test*.md            # Test clipping files
│   └── Limitless/2025-10-17-test*.md            # Test limitless files
└── Projects/2025-10-17 Test*.md                 # Test hashtag files

ai4pkm_cli/tests/
└── watchdog_*.log                               # Daemon output logs
```

### Cleanup

**Automatic:** Test runner cleans up artifacts between tests

**Manual cleanup if needed:**
```bash
cd /Users/lifidea/dev/AI4PKM

# Remove all test artifacts from vault
rm -f ai4pkm_vault/AI/Tasks/2025-10-17*.md
rm -f ai4pkm_vault/AI/Tasks/Requests/Clipping/2025-10-17*.json
rm -f ai4pkm_vault/AI/Tasks/Requests/Hashtag/2025-10-17*.json
rm -f ai4pkm_vault/AI/Tasks/Requests/Limitless/2025-10-17*.json
rm -f ai4pkm_vault/Ingest/Clippings/2025-10-17*.md
rm -f ai4pkm_vault/Projects/2025-10-17*.md
rm -f ai4pkm_vault/Ingest/Limitless/2025-10-17*.md

# Remove daemon logs
rm -f ai4pkm_cli/tests/watchdog_*.log
```

## Test Results

### Console Output

Tests print real-time progress with stage markers:

```
═══════════════════════════════════════════════════════════════════════════
STAGE 0: Starting ai4pkm watchdog
═══════════════════════════════════════════════════════════════════════════
✓ Watchdog started (PID: 12345)

═══════════════════════════════════════════════════════════════════════════
STAGE 1: Creating test clipping file
═══════════════════════════════════════════════════════════════════════════
✓ Created test clipping: /path/to/file.md

... (stages 2-4) ...

═══════════════════════════════════════════════════════════════════════════
TEST RESULTS SUMMARY
═══════════════════════════════════════════════════════════════════════════
Overall Result: ✓ PASSED
```

### Test Reports

Each test generates a markdown report:

```
ai4pkm_cli/tests/KTG_KTP_Integration_Test_Results.md
ai4pkm_cli/tests/KTG_KTP_Hashtag_Integration_Test_Results_<timestamp>.md
ai4pkm_cli/tests/KTG_KTP_Limitless_Integration_Test_Results_<timestamp>.md
```

Reports include:
- Test duration
- Stage-by-stage timing
- Status transitions
- Issues found
- Created file list

## Troubleshooting

### Test hangs at "Waiting for..."

**Cause:** Daemon not processing files or LLM API slow/stuck

**Fix:**
1. Check daemon is running: `ps aux | grep ai4pkm`
2. Check daemon logs: `tail -f ai4pkm_cli/tests/watchdog_*.log`
3. Check LLM API status
4. Increase timeout if needed (edit test file)

### "Watchdog failed to start"

**Cause:** Port conflict, config issue, or missing dependencies

**Fix:**
1. Check no other daemon running: `pkill -f "ai4pkm -t"`
2. Validate config: `cat ai4pkm_cli.json`
3. Check required folders exist
4. Try running daemon manually first

### Duplicate tasks detected

**Cause:** Multiple daemons running or previous test artifacts

**Fix:**
1. Kill all daemons: `pkill -f ai4pkm`
2. Clean up artifacts (see cleanup section above)
3. Run tests one at a time with `--use-existing-daemon`

### "Task did not complete within timeout"

**Cause:** LLM API slow, complex prompt, or agent error

**Fix:**
1. Check task file status manually
2. Review daemon logs for errors
3. Check LLM API logs
4. Increase timeout in test file if consistently slow
5. Simplify test template content

### Tests fail in CI/CD but pass locally

**Cause:** Different environment, timing issues, or missing secrets

**Fix:**
1. Ensure LLM API keys available in CI
2. Increase timeouts for slower CI runners
3. Check file system permissions
4. Validate working directory is correct
5. Use default mode (not `--use-existing-daemon`)

## Development Tips

### Quick iteration during development

```bash
# Terminal 1: Run daemon with verbose logging
cd /Users/lifidea/dev/AI4PKM
python -m ai4pkm_cli.orchestrator_cli daemon

# Terminal 2: Run specific test repeatedly
cd /Users/lifidea/dev/AI4PKM
python ai4pkm_cli/tests/test_ktg_ktp_eic_integration.py --use-existing-daemon

# Clean up between runs
rm -f ai4pkm_vault/AI/Tasks/2025-10-17*.md
rm -f ai4pkm_vault/Ingest/Clippings/2025-10-17*.md
```

### Test specific agent changes

1. Modify agent prompt in `ai4pkm_vault/_Settings_/Prompts/`
2. Restart daemon to reload agents
3. Run corresponding test with `--use-existing-daemon`
4. Check test reports and daemon logs

### Add test for new workflow

1. Create test template in `fixtures/`
2. Copy existing test file as starting point
3. Update file paths, patterns, and validation logic
4. Add to `run_all_integration_tests.sh`
5. Test both modes (default and existing daemon)

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Integration Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -e .
      - name: Run integration tests
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          cd /path/to/AI4PKM
          ./ai4pkm_cli/tests/run_all_integration_tests.sh
        timeout-minutes: 30
```

## Additional Resources

- [Orchestrator README](../orchestrator/README.md) - Orchestrator architecture
- [Test Fixtures README](fixtures/README.md) - Test template documentation
- [Agent Prompts](../../ai4pkm_vault/_Settings_/Prompts/) - Agent definitions
- [Main README](../../README.md) - Overall system documentation

## Support

For issues or questions:
1. Check daemon logs: `ai4pkm_cli/tests/watchdog_*.log`
2. Review test reports: `ai4pkm_cli/tests/KTG_KTP_*_Results.md`
3. Run tests individually with verbose output
4. File issue with logs and test reports attached
