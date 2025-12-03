## Overview
In addition to [[Daily Ingestion and Roundup (DIR)|daily]] and [[Weekly Roundup and Planning (WRP)|weekly]] roundup, this process runs hourly to keep various index pages up-to-date, which allows AI agents to find contents more easily.
### Process
Run tasks for keeping knowledge base clean
(Run only if there's any updates in PKM since last update)
- Apply `EIC` for all newly ingested `Books`, `Articles` and `Clippings` notes
	- Don't process `Limitless` files
	- **Gemini via ai4pkm**: Use `ai4pkm -a gemini -p "Run EIC on [filepath]"`
		- For large files (>50KB), consider manual EIC application if timeout occurs
		- Gemini provides content but cannot directly modify files - apply changes manually
		- Alternative agents: `-a claude` or `-a codex` if Gemini unavailable
- Apply `UFN` for all folders with 1) updated notes and 2) existing folder notes
- Apply `TKI` for all updated `Topics` notes
Find ways to improve notes
- Fix broken links
- Add source attribution
### Guidelines
- Don't repeat job for files already processed
	- Use commit history / timestamp / contents to make judgments

### EIC Execution Details
#### Using ai4pkm with Gemini
```bash
ai4pkm -a gemini -p "Run EIC on [full-file-path]"
```

#### Troubleshooting Common Issues
1. **Timeout Errors**: Large files (>50KB) may timeout
   - **Solution**: Apply EIC manually following the prompt structure
   - Use Gemini to generate content, then manually update the file

2. **File Modification**: Gemini cannot directly edit files
   - **Process**: Gemini provides improved content → manually apply to file
   - Ensure proper YAML frontmatter updates (status: processed)

3. **Alternative Agents**: If Gemini unavailable
   - Claude: `ai4pkm -a claude -p "Run EIC on [filepath]"`
   - Codex: `ai4pkm -a codex -p "Run EIC on [filepath]"`

#### Manual EIC Application Steps
When ai4pkm times out:
1. Read the EIC prompt: `_Settings_/Prompts/Enrich Ingested Content (EIC).md`
2. Apply ICT improvements: grammar, Korean translation, structure with H3
3. Add comprehensive Summary section with quotes
4. Update YAML: add tags, topics, set `status: processed`
5. Ensure wiki links use complete filenames: `[[YYYY-MM-DD Title]]` 

## Prompts
![[_Settings_/Prompts/Enrich Ingested Content (EIC)]]

![[Update Folder Notes (UFN)]]

![[Topic Knowledge Improvement (TKI)]]
