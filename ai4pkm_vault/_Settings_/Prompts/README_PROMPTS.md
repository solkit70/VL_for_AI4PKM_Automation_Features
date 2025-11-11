# Prompts Folder - Agent Definition Guidelines

This folder contains canonical agent definitions for the AI4PKM orchestrator system. Each file defines an agent's behavior, input/output specifications, and processing logic.

## File Naming Convention

**Format**: `Full Title (ABBREVIATION).md`

**Examples**:
- `Enrich Ingested Content (EIC).md`
- `Process Life Logs (PLL).md`
- `Ad-hoc Research within PKM (ARP).md`

**Rules**:
- Use descriptive full title (not "EIC Agent" but "Enrich Ingested Content")
- Include 3-letter abbreviation in parentheses
- Use `.md` extension
- Use title case for readability

---

## Configuration Structure

Agent configuration is split into two parts:
1. **Agent Prompt** (`.md` file): Contains agent identity and instructions
2. **Orchestrator Config** (`orchestrator.yaml`): Contains input/output routing

### Agent Frontmatter (Required Fields)

```yaml
---
title: Full Agent Title (ABC)
abbreviation: ABC
category: ingestion|research|publish
---
```

**Note**: Input/output configuration has been moved to `orchestrator.yaml` at vault root.

### Field Descriptions

#### `title` (required)
- **Format**: "Full Title (ABBREVIATION)"
- **Purpose**: Display name including abbreviation
- **Example**: `"Enrich Ingested Content (EIC)"`

#### `abbreviation` (required)
- **Format**: 3 uppercase letters
- **Purpose**: Short identifier for logging, task tracking
- **Example**: `"EIC"`, `"PLL"`, `"ARP"`

#### `category` (required)
- **Values**:
  - `ingestion` - Content capture and initial processing
  - `research` - Deep analysis and synthesis
  - `publish` - Output preparation and distribution
- **Purpose**: Organize agents by workflow stage

---

## Orchestrator Configuration (`orchestrator.yaml`)

Input/output routing is now centralized in `orchestrator.yaml` at the vault root. This file defines where each agent reads from and writes to.

### File Location

```
vault/
├── orchestrator.yaml          # Configuration file
├── ai4pkm_cli.json           # Existing config
└── _Settings_/
    └── Prompts/              # Agent definitions
```

### Structure

```yaml
version: "1.0"

# Global defaults for all agents
defaults:
  executor: claude_code
  timeout_minutes: 30
  max_parallel: 1
  task_create: true
  task_priority: medium
  task_archived: false

# Agent-specific configuration
agents:
  # Key by agent abbreviation
  EIC:
    input_path: Ingest/Clippings
    input_type: new_file
    output_path: AI/Articles
    output_type: new_file

  HTC:
    input_path: ""  # Content pattern triggered
    input_type: updated_file
    output_path: _Settings_/Tasks
    output_type: new_file
```

### Input/Output Configuration

#### `input_path`
- **Format**: String, list, empty string, or null
- **Purpose**: Where the agent looks for input files
- **Examples**:
  ```yaml
  input_path: Ingest/Clippings        # Single path
  input_path:                          # Multiple paths
    - AI/Articles
    - Journal
  input_path: ""                       # Empty (content pattern)
  input_path: null                     # Manual invocation
  ```

#### `input_type`
- **Values**:
  - `new_file` - Trigger on new files
  - `updated_file` - Trigger on modifications
  - `daily_files` - Batch process for a day
  - `manual` - Explicit invocation only
- **Purpose**: Defines trigger behavior

#### `output_path`
- **Format**: String (relative to vault root)
- **Purpose**: Output directory
- **Examples**: `AI/Articles`, `_Settings_/Tasks`

#### `output_type`
- **Values**:
  - `new_file` - Create new file per execution
  - `daily_file` - One file per day
  - `new_files` - Multiple files per execution
- **Purpose**: Output file strategy

### Agent-Level Optional Fields

```yaml
# Output file naming
output_naming: "{title} - {agent}.md"

# Execution settings
executor: claude_code|gemini_cli|codex_cli|cursor_agent|continue_cli|grok_cli
max_parallel: 2
timeout_minutes: 30

# Skills and integrations
skills:
  - skill_name
mcp_servers:
  - server_name

# Post-processing
post_process_action: remove_trigger_content|archive_source

# Task tracking
task_create: true
task_priority: low|medium|high
task_archived: false

# Logging
log_prefix: ABC
log_pattern: "{timestamp}-{agent}.log"
```

---

## Input/Output Patterns

### Pattern 1: New File Processing (Real-Time)

**Use Case**: Process each new file as it arrives

```yaml
input_path: Ingest/Clipping
input_type: new_file
output_path: AI/Clipping
output_type: new_file
output_naming: "{title} - Processed.md"
```

**Behavior**:
- Agent triggers immediately when new file appears in `Ingest/Clipping/`
- Creates new file in `AI/Clipping/` with processed content
- One input → one output

**Example**: EIC (Enrich Ingested Content)

---

### Pattern 2: Daily Batch Processing

**Use Case**: Aggregate and summarize daily content

```yaml
input_path: Ingest/Limitless
input_type: daily_file
output_path: AI/Lifelog
output_type: daily_file
output_naming: "{date} Lifelog - {agent}.md"
```

**Behavior**:
- Agent processes all files for a specific date
- Creates/updates single daily summary file
- Many inputs → one daily output

**Example**: PLL (Process Life Logs)

---

### Pattern 3: Update in Place

**Use Case**: Enhance existing file without creating new file

```yaml
input_path: Journal
input_type: daily_file
output_path: Journal
output_type: update_file
```

**Behavior**:
- Agent reads file from input_path
- Modifies content (adds sections, links, summaries)
- Writes back to same file
- Input file becomes output file

**Example**: Daily journal enrichment

---

### Pattern 4: Multi-Source Aggregation

**Use Case**: Combine content from multiple locations

```yaml
input_path:
  - AI/Clipping
  - AI/Lifelog
  - AI/Research
input_type: daily_file
output_path: AI/Roundup
output_type: daily_file
```

**Behavior**:
- Agent reads from multiple input directories
- Synthesizes content into unified output
- Many sources → one aggregated output

**Example**: GDR (Generate Daily Roundup)

---

### Pattern 5: Image/Binary File Processing

**Use Case**: Process non-markdown files

```yaml
input_path: Ingest/Photolog/Processed
input_type: new_file
input_pattern: "*.{jpg,jpeg,png,yaml}"
output_path: Ingest/Photolog
output_type: daily_file
```

**Behavior**:
- Agent triggers on image files + metadata
- Processes visual content
- Creates markdown output with embedded images

**Example**: PPP (Pick and Process Photos)

---

## Prompt Body Guidelines

The content below frontmatter defines the agent's instructions.

### Structure

```markdown
---
[frontmatter]
---

Brief description of agent purpose (1-2 sentences).

## Input
- List expected input files/formats
- Document any prerequisites
- Mention special requirements (size, structure)

## Output
- Describe output file format
- List sections/properties added
- Note any transformations applied

## Main Process
```
1. STEP ONE
   - Detailed sub-tasks
   - Expected outcomes

2. STEP TWO
   - More sub-tasks
   - Quality checks
```

## Caveats
- Important warnings
- Common failure modes
- Quality verification steps
```

### Best Practices

1. **Be Specific About Input**
   - File location: "Files in `Ingest/Clipping/`"
   - File format: "Markdown with frontmatter"
   - Size limits: "Articles >3000 words need chunking"
   - Required properties: "Must have `title` and `source`"

2. **Define Clear Output**
   - File location: "Creates file in `AI/Clipping/`"
   - Naming convention: "{original-title} - Processed.md"
   - Added sections: "## Summary", "## Key Points"
   - Property updates: "Sets `status: processed`"

3. **Document Process Steps**
   - Use numbered list for main workflow
   - Include quality checks at each step
   - Note any external dependencies (MCP servers, skills)
   - Mention error handling

4. **Include Critical Warnings**
   - Token/context limits
   - Completeness verification
   - Data loss prevention
   - Common mistakes to avoid

---

## Examples

### Example 1: Simple File Processing

```yaml
---
title: Enrich Ingested Content (EIC)
abbreviation: EIC
category: ingestion
input_path: Ingest/Clipping
input_type: new_file
output_path: AI/Clipping
output_type: new_file
---

Improve captured content through transcript correction, summarization, and knowledge linking.

## Input
- Markdown files in `Ingest/Clipping/`
- Must have frontmatter with `title` and `source`
- Long articles may need chunking (>3000 words)

## Output
- Enhanced file in `AI/Clipping/`
- Adds `## Summary` section at top
- Sets `status: processed` property
- Adds topic links and formatting

## Main Process
1. Fix grammar and transcript errors
2. Add structured headings (###)
3. Create summary for sharing
4. Link to related topics
```

---

### Example 2: Daily Aggregation

```yaml
---
title: Generate Daily Roundup (GDR)
abbreviation: GDR
category: research
input_path:
  - AI/Clipping
  - AI/Lifelog
  - Journal
input_type: daily_file
output_path: AI/Roundup
output_type: daily_file
output_naming: "{date} - Daily Roundup.md"
---

Create comprehensive daily summary integrating multiple sources.

## Input
- Target date: YYYY-MM-DD
- All files from specified paths for that date
- Journal entry if exists
- Processed clippings and lifelogs

## Output
- File: `AI/Roundup/{YYYY-MM-DD} - Daily Roundup.md`
- Structured by source type
- Minimum 3-5 memorable quotes
- Links back to source files
```

---

### Example 3: Image Processing

```yaml
---
title: Pick and Process Photos (PPP)
abbreviation: PPP
category: ingestion
input_path: Ingest/Photolog/Processed
input_type: new_file
input_pattern: "*.{jpg,jpeg,png,yaml}"
output_path: Ingest/Photolog
output_type: daily_file
output_naming: "{date} Photolog.md"
---

Process and curate daily photos into organized photologs.

## Input
- Image files in `Ingest/Photolog/Processed/`
- Metadata YAML files with timestamps
- Calendar data via MCP

## Output
- Daily photolog: `{YYYYMMDD} Photolog.md`
- 5-10 curated photos per day
- Inline image format with EXIF timestamps
- Organized by time of day and activity
```

---

## Properties: `input_type` Details

### `new_file`
- **Trigger**: File creation event
- **Frequency**: Real-time (immediate)
- **Use For**: Processing individual items as they arrive
- **Examples**: Clippings, transcripts, photos

### `daily_file`
- **Trigger**: Scheduled (typically end of day)
- **Frequency**: Once per day
- **Use For**: Daily summaries, roundups, batch processing
- **Examples**: Lifelog summaries, daily roundups, photo collections

### `updated_file`
- **Trigger**: File modification event
- **Frequency**: Real-time (on edit)
- **Use For**: Incremental updates, event detection
- **Examples**: Meeting notes updates, hashtag triggers

### `manual`
- **Trigger**: User invocation only
- **Frequency**: On-demand
- **Use For**: Ad-hoc research, special reports, one-time tasks
- **Examples**: Research requests, thread creation, publishing

---

## Properties: `output_type` Details

### `new_file`
- Creates new file for each execution
- Naming controlled by `output_naming` template
- Preserves all outputs (no overwriting)
- **Example**: Each clipping gets its own processed file

### `daily_file`
- One file per day (YYYY-MM-DD pattern)
- Updates/appends if file exists
- Consolidates multiple executions
- **Example**: Single daily lifelog aggregating all entries

### `update_file`
- Modifies input file in place
- No new file created
- Use with caution (original lost unless versioned)
- **Example**: Adding sections to journal entries

---

## Common Patterns

### Pattern: Hashtag-Triggered Processing

```yaml
input_path: "**/*.md"  # Any markdown file
input_type: updated_file
trigger_content_pattern: "%%\\s*#ai\\s*%%"
post_process_action: remove_trigger_content
```

Agent triggers when `%% #ai %%` appears in any file, then removes the trigger.

---

### Pattern: Calendar-Integrated Processing

```yaml
input_path: Ingest/Limitless
input_type: updated_file
mcp_servers:
  - gcal
```

Agent uses Google Calendar MCP to match transcripts with meetings.

---

### Pattern: Multi-Stage Pipeline

```yaml
# Stage 1: EIC
input_path: Ingest/Clipping
output_path: AI/Clipping

# Stage 2: GDR (uses EIC output)
input_path:
  - AI/Clipping
  - AI/Lifelog
output_path: AI/Roundup
```

Chain agents by having one's output be another's input.

---

## Validation Checklist

Before committing a new prompt file:

- [ ] Filename follows "Title (ABC)" format
- [ ] All required frontmatter fields present
- [ ] `input_path` points to valid vault location
- [ ] `input_type` matches expected trigger behavior
- [ ] `output_path` is appropriate for content type
- [ ] `output_type` matches desired file strategy
- [ ] Prompt body has Input/Output/Process sections
- [ ] Caveats document critical warnings
- [ ] Examples illustrate expected behavior
- [ ] No `trigger_pattern` or `trigger_event` properties (orchestrator-specific, not in Prompts)

---

## Orchestrator Integration

**Note**: The orchestrator may derive trigger patterns from `input_path` + `input_type`:

```yaml
# In Prompts folder (clean, canonical)
input_path: Ingest/Clipping
input_type: new_file

# Orchestrator derives (internal use only)
trigger_pattern: "Ingest/Clipping/*.md"
trigger_event: "created"
```

Keep Prompts files clean - no orchestrator-specific trigger properties here.

---

## Version History

- **2025-10-27**: Initial guidelines created
- **Format**: "Title (ABC)" naming, input/output focus
- **Properties**: Removed trigger_*, standardized input_type/output_type

---

*For orchestrator implementation details, see `docs/_specs/2025-10-27 Orchestrator User Guide.md`*
