Generate knowledge tasks from multiple sources and process them efficiently.

## Main Process

```
0. RUN HELPER SCRIPT
   └─ Execute: python _Settings_/Tools/automation/ktg_helper.py --days 3 --output _Settings_/Tools/ktg_candidates.json --verbose
   └─ Load JSON results from ktg_candidates.json
   └─ Review metadata (scan_date, total_candidates)

1. PROCESS SOURCES (from helper script results)¹
   └─ Unprocessed docs → Create EIC task²
   └─ Tagged docs (#TODO, #TOWRITE, #TOREAD, #TOSEARCH)³
   └─ Limitless PKM requests⁴ → Update Journal or create task
   └─ Recent calendar events → GES⁵ (manual check via MCP)

2. VALIDATE
   └─ Time scope check (already done by helper script)
   └─ Duplicate check in AI/Tasks/YYYY-MM-DD*
   └─ Status consistency⁶

3. PROCESS
   └─ Simple tasks: Execute immediately⁷
   └─ Complex tasks: Create task file⁸

4. CREATE TASK (if complex)
   └─ Use [[Task Template]]
   └─ File: AI/Tasks/YYYY-MM-DD [Description].md
   └─ Properties: Priority, Status, Source
   └─ Structure: Input, Context, Requirements, Inferred

5. CLEANUP
   └─ Update source status
   └─ Remove TODO tags
   └─ Mark completed duplicates
```

## Caveats

### Time Scope Restrictions
⚠️ **CRITICAL**: Only process sources from the **last 3 days** to prevent generating outdated tasks. This applies to all source types and prevents accumulation of stale work.

### Helper Script Integration

**⁰ KTG Helper Script**: Automates source detection and time filtering
- Script location: `_Settings_/Tools/automation/ktg_helper.py`
- Output: `_Settings_/Tools/ktg_candidates.json`
- Documentation: `_Settings_/Tools/KTG_Helper_README.md`
- **Pre-filtered**: All results already respect 3-day time boundary
- **Pre-validated**: YAML frontmatter parsing with error handling

### Source Detection Details

**¹ Process sources from helper script JSON**:
- `sources.unprocessed_docs[]` - Files needing EIC processing
- `sources.tagged_docs[]` - Files with action tags
- `sources.limitless_requests[]` - PKM requests from transcripts

**² Unprocessed docs** (detected by helper script):
- Already filtered to exclude: `status: processed`, `EIC-PROCESSED: true`, Summary+ICT sections
- Contains: file path, created date, source URL, needs_eic flag
- **Action**: Always create EIC task file, never process directly in KTG

**³ Tagged docs patterns** (detected by helper script):
- TODO, TOWRITE → [[Interactive Writing Assistant (IWA)]]
- TOREAD → [[Draft Enhancer]]
- TOSEARCH → [[Ad-hoc Research within PKM (ARP)]]
- Contains: file path, tag, recommended action, created date

**⁴ Limitless PKM requests** (detected by helper script):
- Pattern: `hey pkm` (case insensitive)
- Contains: file path, timestamp, context (500 chars), has_preference flag, line_number
- Preferences detected: "좋겠고", "원해", "필요해", "했으면", "해줘"
- **Action**:
  - Simple insights/reflections → Add to Journal Thoughts section directly
  - Complex requests (research, analysis, multi-step) → Create task file

**⁵ Calendar events**: Manual check via MCP (gcal: Default)
- Not included in helper script (requires MCP API)
- Check recent events, verify completion status with current time

### Status and Validation Rules

**⁶ Status consistency**:
- Use proper statuses: `TBD`, `COMPLETED`, `NEEDS_INPUT`
- Verify due dates are future dates, not past
- Delete or update any outdated pending tasks found

### Processing Categories

**⁷ Simple tasks** (execute immediately):
- Daily goals/todos → Update Journal with `- [ ]` format
- File operations, lookups
- Quick reference tasks
- Limitless insights → Add to Journal Thoughts section

**⁸ Complex tasks** (create task file):
- **ALL unprocessed docs requiring EIC** (always create task, never execute directly)
- Research, analysis, writing
- Multi-step workflows
- Tasks requiring context preservation

### EIC Processing Policy

⚠️ **CRITICAL**: **Never execute EIC directly during KTG**
- Unprocessed docs → Create EIC task file in `AI/Tasks/`
- Reason: Maintain clear separation between task discovery and task execution
- Exception: Simple Limitless insights can be added directly to Journal Thoughts

### Task File Structure Requirements
- **Properties**: Priority (P1 content/P2 workflow), Status, Archived: false, Source link
- **Sections**: Input (full context with blockquotes), Context (time/speaker/type), Requirements (structured preferences), Inferred (input/output/instructions/budget)