# Workflows

AI4PKM provides three main workflows that work together to maintain your knowledge base. These workflows ensure your KB is kept up-to-date with automated processing and organization.

## Daily Ingestion and Roundup (DIR)

**Purpose**: Daily content processing into episodic memory for your PKM.

**Process Steps**:

1. **Pick and Process Photos (PPP)**
   - Photos from each day are processed into photo log
   - Ingested from iCloud Photos via Applescript
   - EXIF metadata extracted and preserved
   - Images saved to `Ingest/Photolog/Snap/` with markdown metadata

2. **Process Life Logs (PLL)**
   - Voice-based life log from Limitless.AI is processed
   - Requires triggering sync with Limitless.AI first
   - Extracts memorable moments, emotions, and lessons learned
   - Creates structured markdown in lifelog format

3. **Enrich Ingested Content (EIC)**
   - Processes content from [Readwise Reader](https://read.readwise.io/new) and [Obsidian Web Clipper](https://obsidian.md/clipper)
   - Improves structure and grammar
   - Adds comprehensive summaries with key quotes
   - Adds topic tags and cross-links
   - Skip files already processed within CKU workflow

4. **Generate Daily Roundup (GDR)**
   - Builds episodic knowledge for the day
   - Links meaningful updates and activities
   - Connects to relevant topics
   - Creates daily summary in `AI/Roundup/` folder

5. **Topic Knowledge Addendum (TKA)**
   - Updates relevant topic notes with new insights
   - Links daily roundup content to topic pages
   - Maintains knowledge graph connections

6. **Create Thread Postings (CTP)**
   - Generates ideas for social media posting
   - Creates threaded content from daily insights
   - Suggests shareable knowledge snippets

**Usage Notes**:
- `DIR` can be run multiple times per day
- Only updated contents will be added to existing notes on subsequent runs
- Can be triggered manually or via cron schedule

**Example Commands**:
```bash
# Run for today
ai4pkm -p "DIR for today"

# Run for specific date range
ai4pkm -p "DIR for 9/10-14"

# Backfill past week
ai4pkm -p "DIR for past week (backfill as needed)"
```

_Note: Daily roundup workflow diagram is available in the vault at `_Settings_/Prompts/_files_/Daily Roundup 2025-07-20 17.29.29.excalidraw.svg`_

## Weekly Roundup and Planning (WRP)

**Purpose**: Weekly knowledge review and planning.

**Process Steps**:

1. **Generate Weekly Roundup (GWR)**
   - Reviews all daily roundups from the week
   - Highlights key content and patterns
   - Identifies themes and insights
   - Creates weekly summary in `AI/Roundup/` folder
   - Sets context for planning next week

**Usage Notes**:
- `GWR` can be run multiple times per day if needed
- Only updated contents will be added to existing notes on subsequent runs
- Typically scheduled for Sunday

**Example Commands**:
```bash
# Run for this week
ai4pkm -p "WRP for this week"

# Run for specific week
ai4pkm -p "WRP for week of 9/10"
```

## Continuous Knowledge Upkeep (CKU)

**Purpose**: Hourly maintenance to keep various index pages up-to-date, allowing AI agents to find contents more easily.

**Process Steps**:

1. **Apply EIC to New Content**
   - Processes all newly ingested content in `Books`, `Articles`, and `Clippings`
   - Does NOT process `Limitless` files (handled by PLL in DIR)
   - Improves structure and adds enrichment
   - Can be executed via different agents:
     - Gemini: `ai4pkm -a gemini -p "Run EIC on [filepath]"`
     - Claude: `ai4pkm -a claude -p "Run EIC on [filepath]"`
     - Codex: `ai4pkm -a codex -p "Run EIC on [filepath]"`

2. **Update Folder Notes (UFN)**
   - Applies to all folders with:
     - Updated notes since last run
     - Existing folder notes
   - Maintains folder index pages
   - Summarizes recent changes

3. **Apply Topic Knowledge Improvement (TKI)**
   - Reviews all updated `Topics` notes
   - Improves structure and balance
   - Adds relevant source attribution
   - Enhances cross-linking

4. **Fix Broken Links**
   - Scans for broken wiki links
   - Attempts to resolve or flag for review
   - Maintains knowledge graph integrity

5. **Add Source Attribution**
   - Ensures all insights have proper source references
   - Adds missing citations
   - Maintains traceability

**Usage Notes**:
- Only runs if there are updates in PKM since last update
- Doesn't repeat jobs for files already processed
- Uses commit history/timestamp/contents to make judgments
- Typically runs hourly via cron

**Example Commands**:
```bash
# Run hourly maintenance
ai4pkm -p "CKU for hourly run"

# Run on-demand
ai4pkm -p "CKU check and process"
```

**Troubleshooting**:

For large files (>50KB), EIC may timeout with Gemini:
1. Read the EIC prompt: `_Settings_/Prompts/Enrich Ingested Content (EIC).md`
2. Apply ICT improvements manually: grammar, Korean translation, structure with H3
3. Add comprehensive Summary section with quotes
4. Update YAML: add tags, topics, set `status: processed`
5. Ensure wiki links use complete filenames: `[[YYYY-MM-DD Title]]`

Alternative: Use Claude or Codex agent which can directly modify files.

## On-demand Task Processing

In addition to the three scheduled workflows above, AI4PKM provides an on-demand task processing system for real-time knowledge work.

**Key Difference from Batch Workflows:**
- **Batch workflows** (DIR, WRP, CKU) run on schedule and process multiple items
- **On-demand processing** responds immediately to individual triggers as they occur

**How it works:**

The system monitors the filesystem for trigger events and automatically processes them through a three-phase pipeline:

1. **KTG (Knowledge Task Generator)** - Creates structured task from trigger
2. **KTP (Knowledge Task Processor)** - Routes to appropriate agent and executes
3. **KTE (Knowledge Task Evaluator)** - Validates outputs and marks completion

**Task Triggers:**
- **Web Clippings**: Content from [Obsidian Web Clipper](https://obsidian.md/clipper) triggers EIC workflow
- **#AI Hashtag**: Add `#AI` to any note to generate a knowledge task
- **Voice Commands**: Limitless pendant with wake words `Hey PKM` creates tasks

**Agent Routing:**
Tasks are automatically routed to the best agent for the job:
- EIC (content enrichment) → Claude Code
- Research tasks → Gemini
- Analysis tasks → Gemini
- Other tasks → Default agent

**Start Task Management:**
```bash
ai4pkm -t
# or
ai4pkm --task-management
```

**Use Cases:**
- Real-time content enrichment as you clip articles
- Immediate processing of voice-captured ideas
- On-the-fly research and analysis tasks
- Writing assistance triggered from any note

**Learn More:**
- [On-demand Knowledge Task Processing](blog/2025-10-20-on-demand-knowledge-task.html) - Implementation blog post
- [README_KTM.md](https://github.com/jykim/AI4PKM/blob/main/README_KTM.md) - Technical details
- [CLI Tool](cli_tool.html#6-task-management-mode) - Usage reference

## Workflow Automation

All workflows can be automated using the CLI cron scheduler. Configure schedules in `cron.json`:

```json
[
  {
    "inline_prompt": "CKU for hourly run",
    "cron": "0 * * * *",
    "description": "Hourly maintenance"
  },
  {
    "inline_prompt": "DIR for today",
    "cron": "0 21 * * *",
    "description": "Daily roundup at 9 PM"
  },
  {
    "inline_prompt": "WRP for this week",
    "cron": "0 12 * * 0",
    "description": "Weekly review on Sunday at noon"
  }
]
```

Start the scheduler with:
```bash
ai4pkm --cron
```

## See Also

- [Guidelines](guidelines.html) - PKM overview and architecture
- [Prompts](prompts.html) - Individual prompt details
- [CLI Tool](cli_tool.html) - Full CLI reference
- [FAQ](faq.html) - Frequently asked questions and troubleshooting

