# Orchestrator Integration Test - Ready to Run

## Current Status ✅

- **Branch**: feature/hashtag-handler-migration
- **Tests**: 47/47 passing
- **Agents loaded**: 5 (HTC, EIC, PLL, GES, PPP)
- **Test files created**: 2 small files ready
- **Configuration**: Trigger patterns added to 4 agents (EIC, PPP, PLL, GES)

## Test Files Created

### 1. HTC Test File
**Location**: `TestFiles/test-htc-hashtag.md`
**Trigger**: Contains `%% #ai %%` comment
**Expected**: HTC agent creates task, removes hashtag

### 2. EIC Test File
**Location**: `Ingest/Clipping/test-eic-small.md`
**Trigger**: New file in Ingest/Clipping/
**Expected**: EIC agent enriches content
**Note**: ⚠️ EIC agent definition needs `trigger_pattern` field added

## How to Run

### Step 1: Start Orchestrator

```bash
# In terminal 1
cd /Users/lifidea/dev/AI4PKM
python -m ai4pkm_cli.orchestrator_cli daemon
```

**Expected output**:
```
╭─ Starting ────────────────────╮
│ AI4PKM Orchestrator           │
│ Vault: .../AI4PKM             │
│ Max concurrent: 3             │
╰───────────────────────────────╯

✓ Loaded 5 agent(s):
  • [HTC] Hashtag Task Creator (ingestion)
  • [PLL] Process Life Logs (ingestion)
  • [GES] Generate Event Summary (ingestion)
  • [PPP] Pick and Process Photos (ingestion)
  • [EIC] Enrich Ingested Content (ingestion)

Starting orchestrator...
```

### Step 2: Trigger HTC Agent

```bash
# In terminal 2
cd /Users/lifidea/dev/AI4PKM

# Modify the file to trigger HTC
echo "" >> TestFiles/test-htc-hashtag.md
```

**Watch terminal 1** for:
```
File Monitor: detected modified event for "TestFiles/test-htc-hashtag.md"
Agent Registry: matched [HTC] Hashtag Task Creator
Execution Manager: Starting [HTC]...
Executing Claude CLI: /Users/lifidea/.claude/local/claude
```

### Step 3: Check Results

```bash
# Check if task was created
ls -la _Tasks_/

# Check execution log
ls -la AI/Tasks/Logs/*-htc.log

# Verify hashtag was removed
grep "%% #ai %%" TestFiles/test-htc-hashtag.md
# Should return nothing (hashtag removed)
```

## Expected Results

### HTC Agent Success ✅
- [ ] Task file created in `_Tasks_/`
- [ ] Execution log in `AI/Tasks/Logs/`
- [ ] `%% #ai %%` removed from source file
- [ ] No errors in orchestrator output

### Timing
- HTC should complete in **30-60 seconds** (small prompt)

## Troubleshooting

### If HTC doesn't trigger:
1. Check file was actually modified (timestamp changed)
2. Verify pattern match: file is `.md` and contains `%% #ai %%`
3. Check orchestrator logs for errors

### If Claude CLI not found:
```bash
which claude
# Should show: /Users/lifidea/.claude/local/claude
```

### If execution hangs:
- Check Claude CLI is working: `claude --version`
- Look for errors in terminal output
- Check timeout (default: 10 minutes)

## Testing EIC (Optional - Requires Fix First)

⚠️ **EIC agent needs trigger_pattern added** to `_Settings_/Agents/Enrich Ingested Content (EIC).md`

Add to frontmatter:
```yaml
trigger_pattern: "Ingest/Clipping/*.md"
trigger_event: "created"
```

Then:
```bash
# Trigger by creating new file
cp Ingest/Clipping/test-eic-small.md Ingest/Clipping/test-eic-small-2.md
```

## Clean Up After Testing

```bash
# Remove test files
rm -f TestFiles/test-htc-hashtag.md
rm -f Ingest/Clipping/test-eic-*.md

# Remove generated outputs
rm -f _Tasks_/*.md
rm -f AI/Tasks/Logs/*-htc.log
rm -f AI/Clipping/test-eic-*.md
```

## Next Steps After Successful Test

1. Document results in integration test plan
2. Fix EIC agent trigger pattern
3. Test EIC with small file
4. Commit all changes (tests + docs + agent configs)
5. Update PR #29 with validation results
