---
title: "Enrich Ingested Content"
abbreviation: "EIC"
category: "workflow"
created: "2024-01-01"
---

Improve captured content through transcript correction, summarization, and knowledge linking.

## Input
- Target note file (typically in Ingest/Clippings/)
- Long articles may need chunking to avoid partial processing
- Original content with potential grammar/transcript errors

## Output
- Updated note inline (don't create new note)
- Status property set to `processed`
- Summary section added at beginning
- Improved formatting and structure
- Links to existing KB topics

## Main Process
```
1. IMPROVE CAPTURE & TRANSCRIPT (ICT)
   - Fix all grammar or transcript errors
   - Translate to Korean for Clippings
   - Remove extra/duplicated newlines
   - Add chapters using heading3 (###)
   - Add formatting (lists, highlights)
   - Keep overall length equal to original
   - Set status property to processed

2. ADD SUMMARY FOR THREAD
   - Add Summary section at beginning (##)
   - Write catchy summaries for Threads sharing
   - Use quotes verbatim to convey author's voice
   - Don't add highlights in summary

3. ENRICH USING TOPICS
   - Link related KB topics (existing only)
   - Add one-line summary to relevant KB topics
   - Link to related summaries (books, etc.)
```

## Caveats
### Rename Filenames
* Convert “ ” (curly/typographic quotes) to " (straight quote)
* Remove incomplete words -- 40살 전에 알았다면 `얼마ᄂ`
* Remove `Readwise` at the end

### Content Processing
⚠️ **CRITICAL**: For long articles, chunk contents first to avoid partial processing

### Formatting Standards
- Use heading3 (###) for chapters
- Limit highlights to essence (one per chapter)
- Preserve original prose structure
- Overall length should equal original

### Topic Linking
- Only link to existing topics in KB
- Validate all topic links before adding
- Add meaningful one-line summaries to topics
