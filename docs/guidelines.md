## Guidelines

The AI4PKM system follows a three-stage process:

1. **Ingest**: Contents are ingested from various sources, and then get processed for quality (e.g. remove transcription error) and richness.
2. **Index**: Processed contents are then indexed by topic and time period (day/week) that constitute your knowledge base.
3. **Use**: Contents in KB are then used in various `Projects` or shared in messages and social media.

_Note: PKM workflow diagrams are available in the vault at `_Settings_/Guidelines/_files_/PKM Workflow.excalidraw.svg`_

## PKM System Architecture

AI is used extensively for PKM practices. These workflows ensure your KB is kept up-to-date. These workflows can be run with simple prompts like `DIR for 9/10-14` or `DIR for past week (backfill as needed)`.

The system architecture includes:
- **Automated Ingestion**: From various sources (Readwise, Web Clipper, Limitless.AI, Photos)
- **AI Processing**: Using Claude Code, Gemini CLI, or Codex CLI
- **Knowledge Organization**: Topic-based and temporal indexing
- **Output Generation**: Social media, projects, and publications

_Note: Architecture diagrams are available in the vault at `_Settings_/Guidelines/_files_/PKM System Architecture.excalidraw.svg`_

## PKM Automations

While most workflows can be run with single command, we provide a CLI tool for further automating the execution. The tool allows:

- **Batch Execution**: Based on cron schedules for automated processing
- **Single Test Run**: For any configured workflow
- **Multi-Agent Support**: All major CLI Agents are supported:
  - `Gemini CLI`
  - `Claude Code`
  - `Codex CLI`
  
Each agent can be used interchangeably depending on the task requirements.

See [CLI Tool](cli_tool.html) for installation and usage details.

## PKM Applications

### Ad-hoc Research within PKM (ARP)

The system supports ad-hoc research capabilities, allowing you to:
- Query your knowledge base for specific topics
- Discover connections between concepts
- Generate research summaries from accumulated knowledge

See the `_Settings_/Prompts/Ad-hoc Research within PKM (ARP).md` prompt for details.

### Contents Creation

AI also powers writing and various types of contents creation:

**Interactive Writing Assistant (IWA)**
- Collaborative writing with AI assistance
- Content refinement and editing
- Structure and organization suggestions

See `_Settings_/Workflows/Interactive Writing Assistant (IWA).md` for the full workflow.

**Create Thread Postings (CTP)**
- Generate social media content from your knowledge base
- Create threaded posts for Twitter/X
- Repurpose insights for different platforms

See `_Settings_/Prompts/Create Thread Postings (CTP).md` for details.

_Note: Content creation workflow diagrams are available in the vault at `_Settings_/Guidelines/_files_/PKM Writing Workflow.excalidraw.svg`_

## Properties & Tags

### Properties
Default properties for notes include:
- `links`: List of linked notes
- `tags`: List of tags

```yaml
---
tags: 
links: 
---
```

### Tags
Tags complement the main hierarchical organization:

Common tags include:
- **Tasks**: `#TODO`, `#TOREAD`, `#followup`
- **Topics**: `#PKM`
- **Other**: Custom tags as needed

## See Also

- [Prompts](prompts.html) - Standardized prompt system
- [Workflows](workflows.html) - Daily, weekly, and continuous workflows
- [FAQ](faq.html) - Frequently asked questions

