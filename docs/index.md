## Front Page

### Why AI4PKM?

AI4PKM is a comprehensive Personal Knowledge Management (PKM) system designed for the AI era, where both humans and AI agents work together to build and maintain your knowledge base.

**Definitions:**
- **PKM**[^1]: The whole practice of managing personal information and knowledge
- **(P)KB**[^2] / Repo / Vault: Information and knowledge stored in a PKM system

**Guiding Principles:**

**PKM is for both Human and AI**
This guideline is meant for both human users and AI assistants/agents:
- AI-created contents are kept separately from human-written notes
- Notes that can be modified by both human and AI are put in VCS for safety

**Tool-agnostic Approach**
Assume that multiple tools can and will process the contents of PKM. As of Aug. 2025, the following applications are used, each with different purposes:
- `Obsidian` is used as a main front-end for human user
	- Primarily as a markdown editor that can manage cross-note links[^3]
- `Cursor` is used as a tool for human-AI collaborative editing
- `Claude Code` is used for agentic processing of PKM prompts and workflows

**Accommodate Multiple AI Tools**
Need to constantly experiment with multiple AI tools and models:
- For that reason, AI-created contents should have clear label on who created it & why

### Resources
![](https://youtu.be/2BMOOMVTdPw)

## Guidelines

### PKM Overview

1. Contents are ingested from various sources, and then get processed for quality (e.g. remove transcription error) and richness.
2. Processed contents are then indexed by topic and time period (day/week) that constitute your knowledge base.
3. Contents in KB are then used in various `Projects` or shared in messages and social media.

![[PKM Workflow.excalidraw.svg]]
%%[[PKM Workflow.excalidraw|🖋 Edit in Excalidraw]]%%

### PKM System Architecture

AI is used extensively for PKM practices. These workflows ensure your KB is kept up-to-date. These workflows can be run with simple prompts like `DIR for 9/10-14` or `DIR for past week (backfill as needed)`.

![[PKM System Architecture.excalidraw.svg]]
%%[[PKM System Architecture.excalidraw|🖋 Edit in Excalidraw]]%%

### PKM Automations

While most workflows can be run with single command, we provide a CLI tool for further automating the execution. The tool allows batch execution (based on cron) or single test run of any workflows configured. Also, the tool supports all of major CLI Agents -- `Gemini CLI`, `Claude Code` and `Codex CLI` so that each agent can be used interchangeably.

### PKM Applications

**Ad-hoc Research**
![[Ad-hoc Research within PKM (ARP)]]

**Contents Creation**
AI also powers writing and various types of contents creation.
![[PKM Writing Workflow.excalidraw.svg]]

![[Interactive Writing Assistant (IWA)]]

![[Create Thread Postings (CTP)]]

### Prompts

All prompts in this system follow a standardized structure defined by [[Prompt Template]]. This template ensures consistency across all workflow prompts with the following format:

**Structure:**
- **Input**: Required inputs, file paths, data sources, and parameters
- **Output**: Expected output format, file naming conventions, and side effects
- **Main Process**: Step-by-step workflow in numbered format with sub-bullets
- **Caveats**: Critical warnings, processing rules, and quality standards

**Benefits:**
- Consistent documentation across all prompts
- Clear input/output specifications for each workflow step
- Easier maintenance and updates
- Better understanding of prompt requirements and constraints

All regular prompts have been updated to follow this template structure for improved organization and usability.

The following prompts and templates are extensively used within workflows to represent individual steps and input/output notes:
- `_Settings_/Prompts` - All prompts follow the standardized [[Prompt Template]] structure
- `_Settings_/Templates` - Including the [[Prompt Template]] that ensures consistent Input/Output/Main Process/Caveats format across all workflow prompts

For detailed prompt information, see [[PKM Prompts]].

### Workflows

AI4PKM provides three main workflows that work together to maintain your knowledge base:

**[[Daily Ingestion and Roundup (DIR)]]**
Daily content processing into episodic memory for your PKM. This workflow:
1. [[Pick and Process Photos (PPP)]] - Photos from each day are processed into photo log (ingested from iCloud Photos via Applescript)
2. [[Process Life Logs (PLL)]] - Voice-based life log (from Limitless.AI) is processed
3. [[Enrich Ingested Content (EIC)]] - Ingested from [Readwise Reader](https://read.readwise.io/new) and [Obsidian Web Clipper](https://obsidian.md/clipper)
4. [[Generate Daily Roundup (GDR)]] - Build episodic knowledge for day
5. [[Topic Knowledge Addendum (TKA)]] - Add updates to topic knowledge
6. [[Create Thread Postings (CTP)]] - Generate ideas for social media posting

`DIR` can be run multiple times per day, in which case only updated contents will be added to existing notes.

![[Daily Roundup 2025-07-20 17.29.29.excalidraw.svg]]
%%[[Daily Roundup 2025-07-20 17.29.29.excalidraw.md|🖋 Edit in Excalidraw]]%%

**[[Weekly Roundup and Planning (WRP)]]**
Weekly knowledge review and planning. This workflow:
- [[Generate Weekly Roundup (GWR)]] - Generates weekly roundups highlighting key content from daily roundups

`GWR` can be run multiple times per day, in which case only updated contents will be added to existing notes.

**[[Continuous Knowledge Upkeep (CKU)]]**
In addition to daily and weekly roundup, this process runs hourly to keep various index pages up-to-date, which allows AI agents to find contents more easily. This workflow:
- Apply `EIC` for all newly ingested `Books`, `Articles` and `Clippings` notes (don't process `Limitless` files)
- Apply `UFN` ([[Update Folder Notes (UFN)]]) for all folders with 1) updated notes and 2) existing folder notes
- Apply `TKI` ([[Topic Knowledge Improvement (TKI)]]) for all updated `Topics` notes
- Fix broken links
- Add source attribution

The process only runs if there are updates in PKM since last update, and doesn't repeat jobs for files already processed.

## FAQ
TBD

[^1]: Personal Knowledge Management
[^2]: (Personal) Knowledge Base
[^3]: And show pretty graphs of KB contents