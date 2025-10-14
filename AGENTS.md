---
description:
globs:
alwaysApply: true
---

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation or README files. 

# Generic AI Agent Rules

*These rules apply to all AI agents (Claude Code, Gemini, Codex) working in this PKM vault.*

## Core Mission & Principles
- **Your mission is to enhance and organize user's knowledge**
	- Don't add your internal knowledge unless explicitly asked to do so
- Most commands are based on existing prompts and workflows (locations below)
	- But note that default settings (e.g. input/output) can be overridden for each run
- You're expected to run autonomously for most prompts & workflow runs
	- Use your judgment to complete the task unless asked otherwise

## Prompts & Workflows
- Prompts can be found in `_Settings_/Prompts`
- Workflows (of prompts) in `_Settings_/Workflows`
- Templates (of md docs) in `_Settings/Templates`
- Knowledge Tasks in `AI/Tasks` (only when requested) 
- Each command can be called using abbreviations
- Check this first for new command (especially if it's abbreviations)

## Search over files
- For searching over topic or dates, start from `Topics` or `Roundup` folder
- Follow markdown link to find related files (use `find` to find exact location)
* **파일 검색 시 `.gitignore` 고려**: 파일 목록을 찾거나 내용을 검색할 때, `.gitignore`에 의해 제외될 수 있는 경우 `respect_git_ignore=False` 옵션을 사용하여 모든 관련 파일을 포함한다.

## 📝 Content Creation Requirements
### General Guidelines
- **Include original quotes** in blockquote format
- **Add detailed analysis** explaining significance
- Structure by themes with clear categories
- **Use wiki links with full filenames**: `[[YYYY-MM-DD Filename]]`
- **Tags use plain text in YAML frontmatter**: `tag` not `#tag` in YAML
  - Example:
```yaml
tags:
  - journal
  - daily
```

### Link Format Standards
- Use Link Format below for page properties:
```yaml
  - "[[Page Title]]"
```
- For files in AI folder, omit "AI/" prefix for brevity
- Example: `[[Roundup/2025-08-03 - Claude Code]]` not `[[AI/Roundup/2025-08-03 - Claude Code]]`

### 📁 Output File Management
- Create analysis files in `AI/*/` folder unless instructed otherwise
- Naming: `YYYY-MM-DD [Project Name] by [Agent Name].md`
- Include source attribution for every insight

### Properties & Frontmatter Standards
- Use a single YAML block at top (`---` … `---`). Leave one blank line after it.
- Keys are lowercase and consistent: `title`, `source` (URL), `author` (list), `created` (YYYY-MM-DD), `tags` (list)
- Avoid duplicates like `date` vs `created`
- Tags are plain text (no `#`) and indented list; authors may be wiki links wrapped in quotes
- Quote values that contain colons, hashes, or look numeric to avoid YAML casting
- After frontmatter, start with a section heading — no loose text or embeds before the first heading

## 🔄 Additional Principles

### Update over duplicated creation
- 해당 날짜에 기존 파일이 존재하면 업데이트 (새로 만들지 말 것)
  - 이때 그냥 추가된 내용을 덧붙이지 말고 전체적인 일관성을 고려해여 수정할 것 (중복은 죄악)

### Language Preferences
- Use Korean as default language (English is fine, say, to quote original note)

### 🔗 Critical: Wiki Links Must Be Valid
- **All wiki links must point to existing files**
- Use complete filename: `[[2025-04-09 세컨드 브레인]]` not `[[세컨드 브레인]]`
  - If possible add section links too (using `#` suffix)
- Verify file existence before linking
  - Fix broken links immediately
- **Link to original sources, not topic indices**
  - Topic files (e.g., `Topics/Business & Career/Career.md`) are indices/aggregations
  - Always link to the original article, clipping, or document where content first appeared
  - Example: Link to `[[Ingest/Articles/2025-08-15 역스킬 현상]]` not `[[Topics/Business & Career/Career#역스킬]]`
  - This maintains proper source attribution and traceability

## Source/Prompt-specific Guidelines
### Limitless Link Format
- **Correct path**: `[[Limitless/YYYY-MM-DD#section]]` (no Ingest prefix)
- **Always verify section exists**: Check exact header text in source file
- **Section headers are usually Korean**: Match them exactly as written
- **If unsure about section**: Link to file only `[[Limitless/YYYY-MM-DD]]`

### Heading Structure Guidelines
- Clippings (EIC/ICT): begin with `## Summary`, then `## Improve Capture & Transcript (ICT)`, then transcript
- ICT means improve the transcript (correct grammar, translate to Korean, structure with h3), not summarize. Keep length comparable to source; summaries live only under `## Summary`
- Lifelog: use H1 `# YYYY-MM-DD Lifelog - <Assistant>` then H2 sections (Monologues, Conversations, etc.)
- Topics/Projects: start with H2 summary; avoid duplicating title as H1

## Quality Standards
- Validate all wiki links resolve to existing files/sections; fix broken links immediately
- Focus on meaningful content over metadata files
- Don't ask permission for any non-file-changing operations (search/list/echo etc)
- Always use local time (usually in Seattle area) for processing requests

---
*For agent-specific rules, refer to individual agent configuration files: CLAUDE.md, GEMINI.md, AGENTS.md*