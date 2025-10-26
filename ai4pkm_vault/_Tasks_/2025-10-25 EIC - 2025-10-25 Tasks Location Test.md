---
title: "EIC - 2025-10-25 Tasks Location Test"
created: 2025-10-25T20:25:42.582037
archived: false
worker: "claude_code"
status: "PROCESSED"
priority: "medium"
output: "[[Ingest/Clippings/2025-10-25 Tasks Location Test.md]]"
task_type: "EIC"
generation_log: "[[AI/Tasks/Logs/2025-10-25-202542-EIC-gen]]"
---

## Input

Target file: `[[Ingest/Clippings/2025-10-25 Tasks Location Test.md]]`

Created file event triggered Enrich Ingested Content processing.

## Output

Enrich Ingested Content will update this section with output information.

## Instructions

Improve captured content through transcript correction, summarization, and knowledge linking.

## Context
You are processing a newly captured article/clipping. The file was just created in Ingest/Clippings/ and needs enrichment.

## Input
The file path is provided in the trigger context. Read the file to get:
- Original content (may have grammar/transcript errors)
- Frontmatter metadata
- Current status

## Your Task

### 1. IMPROVE CAPTURE & TRANSCRIPT (ICT)
- Fix all grammar or transcript errors
- Translate to Korean for Clippings
- Remove extra/duplicated newlines
- Add chapters using heading3 (###)
- Add formatting (lists, highlights)
- Keep overall length equal to original
- Set status property to `processed`

### 2. ADD SUMMARY FOR THREAD
- Add Summary section at beginning (##)
- Write catchy summaries for Threads sharing
- Use quotes verbatim to convey author's voice
- Don't add highlights in summary

### 3. ENRICH USING TOPICS
- Link related KB topics (existing only)
- Add one-line summary to relevant KB topics
- Link to related summaries (books, etc.)

## Critical Requirements

### Content Completeness - MUST VERIFY
⚠️ **CRITICAL**: ICT section must be COMPLETE - not truncated

**Before marking PROCESSED, verify:**
1. Check article length FIRST before starting
2. If source >3000 words, process in chunks OR request context extension
3. VERIFY ICT ends at natural stopping point (end of paragraph/section, not mid-sentence)
4. Self-check: "Does the last paragraph in ICT feel complete?"
5. ICT section should have multiple ### subsections
6. Last sentence should end with proper punctuation, not "..." or cut-off text
7. Length should be comparable to original source

**If you cannot complete full ICT:**
- Mark task as NEEDS_INPUT explaining length/complexity issue
- DO NOT mark PROCESSED with incomplete work

### File Naming
- Convert curly quotes to straight quotes
- Remove incomplete words
- Remove "Readwise" suffix if present
- Rename file if needed using Edit tool

### Output Format
- Update file INLINE (don't create new file)
- Set status property to `processed`
- Ensure Summary section is at the beginning
- Use heading3 (###) for chapters
- Preserve original structure and length

## File to Process
The file path will be in the trigger_data context. Use Read tool to access it, then Edit tool to update it inline.


## Process Log

## Evaluation Log

