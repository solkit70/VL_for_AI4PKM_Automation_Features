# FAQ

[← Back to Home](AI4PKM/index.md)

## Frequently Asked Questions

### General Questions

**Q: What is AI4PKM?**  
A: AI4PKM is a Personal Knowledge Management system designed for the AI era, combining human curation with AI-powered automation to build and maintain your knowledge base.

**Q: What tools do I need?**  
A: At minimum, you need:
- Obsidian (for the vault interface)
- One of the AI CLI tools (Claude Code, Gemini CLI, or Codex CLI)
- Python 3.8+ (if using the automation CLI)

**Q: Can I use this without the CLI tool?**  
A: Yes! You can manually run prompts through Claude Code in Cursor or directly in your AI tool of choice. The CLI is optional but recommended for automation.

**Q: Which AI agent should I use?**  
A: Each has strengths:
- **Claude Code**: Best for general analysis and writing
- **Gemini CLI**: Best for multilingual content and large files
- **Codex CLI**: Best for code-related tasks

You can switch between them freely with `ai4pkm -a [agent]`.

### Setup & Configuration

**Q: How do I get started?**  
A: Follow the [Getting Started](AI4PKM/index.md#getting-started) guide on the homepage. Key steps:
1. Clone the repo
2. Open in Obsidian
3. Install CLI (optional)
4. Run your first workflow

**Q: Where are the configuration files?**  
A: 
- AI agent config: `_Settings_/ai4pkm_config.json`
- Cron schedules: `cron.json` (root directory)
- Prompts: `_Settings_/Prompts/`
- Templates: `_Settings_/Templates/`

**Q: How do I configure cron jobs?**  
A: Edit `cron.json` in the root directory. See [Workflow Automation](workflows.md#workflow-automation) for examples.

### Using Workflows

**Q: What's the difference between DIR, WRP, and CKU?**  
A: 
- **DIR**: Daily processing of new content
- **WRP**: Weekly review and planning
- **CKU**: Continuous hourly maintenance

See [Workflows](AI4PKM/workflows.md) for detailed explanations.

**Q: Can I run workflows manually?**  
A: Yes! Use commands like:
```bash
ai4pkm -p "DIR for today"
ai4pkm -p "WRP for this week"
ai4pkm -p "CKU for hourly run"
```

**Q: How often should I run each workflow?**  
A: Recommended schedule:
- CKU: Every hour
- DIR: Once daily (evening)
- WRP: Once weekly (Sunday)

### Troubleshooting

**Q: EIC is timing out on large files**  
A: 
1. Try using Gemini or Claude instead of your current agent
2. For files >50KB, consider manual processing following the EIC prompt
3. Gemini provides content but can't directly modify files - apply changes manually

**Q: My agent isn't working**  
A: 
1. Check agent availability: `ai4pkm --list-agents`
2. Verify installation of the CLI tool (claude, gemini, codex)
3. Check your API keys and authentication
4. Try switching to a different agent: `ai4pkm -a [agent]`

**Q: Broken wiki links in my vault**  
A: The CKU workflow includes link fixing. Run:
```bash
ai4pkm -p "CKU for hourly run"
```

**Q: Where are my generated files?**  
A: 
- Daily/Weekly roundups: `AI/Roundup/`
- Research outputs: `AI/Research/`
- Photo logs: `Ingest/Photolog/Snap/`
- Life logs: `Ingest/Limitless/`

**Q: Can I customize prompts?**  
A: Yes! All prompts are in `_Settings_/Prompts/` as markdown files. Edit them to suit your needs. Follow the standard [Prompt Template](AI4PKM/prompts.md#standardized-template-structure) structure.

### Advanced Usage

**Q: Can I add custom workflows?**  
A: Yes! Create new prompt files in `_Settings_/Prompts/Adhoc/` following the template structure, then reference them in commands or cron jobs.

**Q: How do I integrate new data sources?**  
A: Add new ingestion steps to the DIR workflow, or create custom prompts for processing specific sources.

**Q: Can I use this for team knowledge management?**  
A: The current system is designed for personal use. Team usage would require additional setup for shared vaults and coordination.

**Q: How do I backup my knowledge base?**  
A: The vault is a git repository. Regular commits and pushes to a remote (GitHub/GitLab) provide version control and backup.

## Still Have Questions?

- Check the [Guidelines](AI4PKM/guidelines.md) for system architecture
- Review [Prompts](AI4PKM/prompts.md) for detailed prompt documentation
- See [Workflows](AI4PKM/workflows.md) for workflow specifics
- Read the [CLI Documentation](../README_CLI.md) for command reference
- Open an issue on GitHub for technical problems

## Contributing

Found a bug or have a suggestion? Contributions are welcome! Please:
1. Check existing issues first
2. Create a detailed issue or pull request
3. Follow the existing code and documentation patterns

