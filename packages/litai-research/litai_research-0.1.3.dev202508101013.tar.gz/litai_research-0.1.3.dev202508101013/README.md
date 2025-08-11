# LitAI

AI-powered literature review assistant that understands your research questions and automatically finds papers, extracts insights, and synthesizes findings - all through natural conversation.

## Why LitAI?

LitAI accelerates your research by turning hours of paper reading into minutes of focused insights:

- **Find relevant papers fast**: Natural language search across millions of papers
- **Extract key insights**: AI reads papers and pulls out claims with evidence
- **Synthesize findings**: Ask questions across multiple papers and get cited answers
- **Build your collection**: Manage PDFs locally with automatic downloads from ArXiv

Perfect for:
- Literature reviews for research papers
- Understanding a new field quickly  
- Finding solutions to technical problems
- Discovering contradictions in existing work
- Building comprehensive reading lists

💡 **Tip**: Use the `/questions` command to see research unblocking questions organized by phase - from debugging experiments to contextualizing results.

## Installation

### Prerequisites
- Python 3.11 or higher
- API key for OpenAI or Anthropic

### Install with pip or uv
```bash
# Using pip
pip install litai-research

# Using uv (faster)
uv pip install litai-research
```

### Updates
```bash
# Stable updates
pip install --upgrade litai-research
uv pip install --upgrade litai-research

# Development/pre-release updates  
pip install --upgrade --pre litai-research
uv pip install --upgrade --pre litai-research
```

## Configuration

Set your API key as an environment variable:
```bash
# For OpenAI
export OPENAI_API_KEY=sk-...

# For Anthropic
export ANTHROPIC_API_KEY=sk-ant-...
```

<details>
<summary>Advanced Configuration</summary>

Configure LitAI using the `/config` command:
```bash
# Show current configuration
/config show

# Set provider and model
/config set llm.provider openai
/config set llm.model gpt-4o-mini

# Reset to auto-detection
/config reset
```

Configuration is stored in `~/.litai/config.json` and persists across sessions.
</details>

## Getting Started

### 1. Launch LitAI
```bash
litai
```

### 2. Set Up Your Research Context (Recommended)
Provide context about your research to get more tailored responses:

```bash
/prompt
```

This opens your default editor with a template where you can describe:
- **Research Context**: Your area of study and current focus
- **Background & Expertise**: Your academic/professional background
- **Specific Interests**: Particular topics, methods, or problems you're investigating  
- **Preferences**: How you prefer information to be presented or synthesized

**Example research context:**
```markdown
## Research Context
I'm a PhD student researching efficient transformer architectures for edge deployment. Currently focusing on knowledge distillation and pruning techniques for large language models.

## Background & Expertise
- Strong background in deep learning and PyTorch
- Experience with model compression techniques
- Familiar with transformer architectures and attention mechanisms

## Specific Interests
- Structured pruning methods that maintain model accuracy
- Hardware-aware neural architecture search
- Quantization techniques for transformers

## Preferences
- When synthesizing papers, please highlight actual compression ratios achieved
- I prefer concrete numbers over vague claims
- Interested in both positive and negative results
```

**Why this matters**: This context gets automatically included in every AI conversation, helping LitAI understand your expertise level and tailor responses accordingly. Without it, LitAI treats every user the same way.

### 3. Understanding LitAI's Two Modes

**Normal Mode** - Build your research context:
```bash
normal ▸ "Find papers about attention mechanisms"
normal ▸ "Add the Transformer paper to my collection"  
normal ▸ /papers                    # View your collection
normal ▸ /note 1                    # Add personal notes
normal ▸ /tag 1 -a transformers     # Organize with tags
```

**Synthesis Mode** - Ask questions and analyze:
```bash
normal ▸ /synthesize                # Enter synthesis mode
synthesis ▸ "What are the key findings across my transformer papers?"
synthesis ▸ "How do attention mechanisms work?"
synthesis ▸ "Compare BERT vs GPT architectures" 
synthesis ▸ "Go deeper on the mathematical foundations"
synthesis ▸ exit                    # Return to normal mode
```

**The Workflow:**
1. **Normal Mode**: Search, collect, and organize papers
2. **Synthesis Mode**: Ask research questions and get AI analysis
3. **Switch freely**: `/synthesize` to enter, `exit` to return

### 4. Build Your Research Workflow

**For New Research Areas:**
1. **Normal Mode**: `"Find recent papers about [topic]"` + `"Add the most cited papers"`
2. **Synthesis Mode**: `"What are the main approaches in this field?"` + follow-up questions

**For Literature Reviews:**
1. **Normal Mode**: Build collection, add notes (`/note`), organize with tags (`/tag`)
2. **Synthesis Mode**: `"Compare methodologies across my papers"` + deep analysis questions

**For Keeping Current:**
1. **Normal Mode**: `/questions` → See research-unblocking prompts by phase
2. **Synthesis Mode**: Regular Q&A sessions to connect new papers to existing work

> **Key Insight**: Normal mode = building context, Synthesis mode = asking questions

## Features

### 🔍 Paper Discovery & Management
- **Smart Search**: Natural language queries across millions of papers via Semantic Scholar
- **Intelligent Collection**: Automatic duplicate detection and citation key generation
- **PDF Integration**: Automatic ArXiv downloads with local storage
- **Flexible Organization**: Tags, notes, and configurable paper list views
- **Import Support**: BibTeX file import for existing libraries

### 🤖 AI-Powered Analysis
- **Key Point Extraction**: Automatically extract main claims with evidence
- **Deep Synthesis**: Interactive synthesis mode for collaborative exploration  
- **Context-Aware**: Multiple context depths (abstracts, notes, key points, full text)
- **Agent Notes**: AI-generated insights and summaries for papers
- **Research Context**: Personal research profile for tailored responses

### 💬 Interactive Experience
- **Natural Language Interface**: Chat naturally about your research
- **Command Autocomplete**: Tab completion for all commands and file paths
- **Vi Mode Support**: Optional vi-style keybindings
- **Session Management**: Persistent conversations with paper selections
- **Research Questions**: Built-in prompts to unblock research at any phase

### ⚙️ Advanced Features
- **Configurable Display**: Customize paper list columns and layout
- **Tool Approval System**: Control AI tool usage in synthesis mode
- **Comprehensive Logging**: Debug and track all operations
- **Multi-LLM Support**: OpenAI and Anthropic models with auto-detection

## Command Reference

### Essential Commands
```bash
/find <query>          # Search for papers  
/add <numbers>         # Add papers from search results
/papers [page]         # List your collection (with pagination)
/synthesize            # Enter interactive synthesis mode
/note <number>         # Manage paper notes
/tag <number> -a <tags>  # Add tags to papers
/prompt                # Set up your research context (recommended)
/questions             # Show research-unblocking prompts
/help                  # Show all commands
```

### Papers Command Options
```bash
/papers --tags         # Show all tags with counts
/papers --notes        # Show papers with notes
/papers 2              # Show page 2 of collection
```

### Research Context Commands
```bash
/prompt                # Edit your research context (opens in editor)
/prompt view           # Display your current research context
/prompt append "text"  # Add text to your existing context
/prompt clear          # Delete your research context
```

### Configuration
```bash
/config show           # Display current settings
/config set llm.model gpt-4o-mini
/config set synthesis.tool_approval false
/config set display.list_columns title,authors,tags,notes
```

> **Note**: Configuration changes require restarting LitAI to take effect

### Normal Mode vs Synthesis Mode

**Normal Mode** - Context building and management:
```bash
/find <query>          # Search for papers  
/add <numbers>         # Add papers from search results
/papers [page]         # List your collection
/note <number>         # Add your personal notes
/tag <number> -a <tags>  # Add tags to papers
/synthesize            # Enter synthesis mode
```

**Synthesis Mode** - Question answering and analysis:
```bash
synthesis ▸ "What are the key insights from paper X?"
synthesis ▸ "How do these approaches compare?"
synthesis ▸ "Go deeper on the methodology"
synthesis ▸ "Add AI notes to paper 1"     # Ask AI to generate analysis notes
synthesis ▸ /papers                       # Show full collection
synthesis ▸ /selected                     # Show papers in current session  
synthesis ▸ /context key_points           # Change context depth
synthesis ▸ /clear                        # Clear session (keep selected papers)
synthesis ▸ exit                          # Return to normal mode
```

### Notes System
- **Personal Notes** (`/note` in normal mode): Your own thoughts and observations
- **AI Notes** (request in synthesis mode): Ask AI to generate insights and summaries for papers

## Data Storage

LitAI stores all data locally in `~/.litai/`:
- `litai.db` - SQLite database with paper metadata and extractions
- `pdfs/` - Downloaded PDF files  
- `logs/litai.log` - Application logs for debugging
- `config.json` - User configuration
- `user_prompt.txt` - Personal research context

## FAQ

### Why do paper searches sometimes fail?

Semantic Scholar's public API can experience high load, leading to search failures. If you encounter frequent issues:
- Wait a few minutes and try again
- Consider requesting a free API key for higher rate limits: [Semantic Scholar API Key Form](https://www.semanticscholar.org/product/api#api-key-form)

## License

This project is open source and available under the [MIT License](LICENSE).

## Acknowledgments

- Built with [Semantic Scholar API](https://www.semanticscholar.org/product/api)
- Powered by OpenAI/Anthropic language models

## Support

- Report issues: [GitHub Issues](https://github.com/harmonbhasin/litai/issues)
- Logs for debugging: `~/.litai/logs/litai.log`
