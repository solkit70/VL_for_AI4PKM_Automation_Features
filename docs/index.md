# AI4PKM

## Why AI4PKM?

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

## Learn More

- [Guidelines](guidelines.md) - PKM overview, architecture, and applications
- [Prompts](prompts.md) - Standardized prompt system documentation
- [Workflows](workflows.md) - Daily, weekly, and continuous maintenance workflows
- [FAQ](faq.md) - Frequently asked questions and troubleshooting

## Getting Started

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/AI4PKM.git
   cd AI4PKM
   ```

2. **Set Up Obsidian**
   - Open the vault in Obsidian
   - Explore community plugins in settings
   - Review templates in `_Settings_/Templates/`

3. **Install CLI Tool** (Optional)
   ```bash
   pip install -e .
   ```
   See [CLI Documentation](../README_CLI.md) for details.

4. **Start Using Workflows**
   - Begin with `DIR for today` for daily roundup
   - Use `CKU for hourly run` for maintenance
   - See [Workflows](workflows.md) for complete details

## Resources

- [PKM in AI Era](https://publish.obsidian.md/lifidea/Publish/PKM+in+AI+Era/0.+Why+PKM+now%3F) tutorial series
- Video Introduction: ![](https://youtu.be/2BMOOMVTdPw)

[^1]: Personal Knowledge Management
[^2]: (Personal) Knowledge Base
[^3]: And show pretty graphs of KB contents