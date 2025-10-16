# Prompts

All prompts in this system follow a standardized structure defined by the Prompt Template. This template ensures consistency across all workflow prompts with a clear and predictable format.

## Standardized Template Structure

Every prompt follows this four-part structure:

### Structure Components

**Input**
- Required inputs, file paths, data sources, and parameters
- Clearly defines what the prompt needs to work with
- Specifies any optional parameters or configurations

**Output**
- Expected output format and structure
- File naming conventions
- Location where outputs should be saved
- Any side effects or state changes

**Main Process**
- Step-by-step workflow in numbered format
- Sub-bullets for detailed steps within each main step
- Clear, actionable instructions for execution

**Caveats**
- Critical warnings and important considerations
- Processing rules and constraints
- Quality standards and best practices
- Edge cases to be aware of

## Benefits

The standardized prompt template provides several key advantages:

- **Consistent Documentation**: All prompts follow the same structure, making them easier to understand and use
- **Clear Specifications**: Input/output requirements are explicitly defined for each workflow step
- **Easier Maintenance**: Updates and improvements can be made systematically
- **Better Understanding**: Users and AI agents can quickly grasp prompt requirements and constraints
- **Reduced Errors**: Explicit caveats and processing rules prevent common mistakes

## Prompt Directory Structure

All prompts are organized in the vault:

```
_Settings_/
├── Prompts/
│   ├── Generate Daily Roundup (GDR).md
│   ├── Generate Weekly Roundup (GWR).md
│   ├── Process Life Logs (PLL).md
│   ├── Enrich Ingested Content (EIC).md
│   ├── Topic Knowledge Creation (TKC).md
│   ├── Topic Knowledge Improvement (TKI).md
│   ├── Topic Knowledge Addendum (TKA).md
│   ├── Update Folder Notes (UFN).md
│   ├── Knowledge Task Generator (KTG).md
│   ├── Knowledge Task Processor (KTP).md
│   ├── Knowledge Task Evaluator (KTE).md
│   ├── Pick and Process Photos (PPP).md
│   ├── Create Thread Postings (CTP).md
│   ├── Ad-hoc Research within PKM (ARP).md
│   └── Adhoc/
│       └── custom_prompt.md
└── Templates/
    ├── Prompt Template.md
    ├── Journal Template.md
    ├── Topic Template.md
    └── Weekly Roundup Template.md
```

## Key Prompts

### Daily Operations
- **Generate Daily Roundup (GDR)**: Creates daily summaries linking meaningful updates and topics
- **Process Life Logs (PLL)**: Summarizes voice-based life logs with memorable items and emotions
- **Pick and Process Photos (PPP)**: Processes photos into structured photo logs
- **Enrich Ingested Content (EIC)**: Improves captured content structure and adds summaries

### Weekly Operations
- **Generate Weekly Roundup (GWR)**: Generates weekly summaries from daily roundups
- **Weekly Reading Review**: Reviews weekly reading for key learnings

### Topic Management
- **Topic Knowledge Creation (TKC)**: Creates new topic notes from source materials
- **Topic Knowledge Improvement (TKI)**: Improves topic note structure and balance
- **Topic Knowledge Addendum (TKA)**: Updates existing topic notes with new content

### Maintenance
- **Update Folder Notes (UFN)**: Creates and updates folder notes with recent changes
- **Knowledge Task Generator (KTG)**: Generates maintenance and improvement tasks
- **Knowledge Task Processor (KTP)**: Processes and executes knowledge tasks
- **Knowledge Task Evaluator (KTE)**: Evaluates task completion and quality

### Content Creation
- **Create Thread Postings (CTP)**: Generates social media content from knowledge base
- **Ad-hoc Research within PKM (ARP)**: Conducts research within your knowledge base

## Usage

Prompts can be executed in several ways:

1. **Via Claude Code/Cursor**: Directly reference prompts in your vault
2. **Via CLI**: Use the ai4pkm CLI tool with prompt names or inline prompts
3. **Manually**: Follow the prompt steps in the markdown files

Example CLI usage:
```bash
# Execute a named workflow
ai4pkm -p "DIR for today"

# Execute a specific prompt inline
ai4pkm -p "GDR for yesterday"

# Use a specific agent for a prompt
ai4pkm -a gemini -p "EIC on new articles"
```

## See Also

- [Guidelines](AI4PKM/guidelines.md) - PKM overview and principles
- [Workflows](AI4PKM/workflows.md) - How prompts work together in workflows
- [FAQ](AI4PKM/faq.md) - Frequently asked questions

