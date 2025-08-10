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

## Quick Start

Launch the interactive interface:
```bash
litai
```

## Two Ways to Use LitAI

### → Natural Language Mode (Recommended)
Just ask questions and let AI handle everything. Follow this workflow:
```bash
litai
# Step 1: Find papers (builds search results)
> Find papers about vision transformers

# Step 2: Add papers from search results to your collection
> Add the "Attention Is All You Need" paper to my collection

# Step 3: Analyze papers in your collection
> What are the key findings in the BERT paper?

# Step 4: Synthesize across your collection
> How does ViT compare to CNN methods in my papers?
```

The AI will automatically:
- Search for relevant papers
- Download and read PDFs
- Extract key insights
- Synthesize findings across multiple sources
- Provide citations for all claims

### → Command Mode
For precise control over specific operations:

<details>
<summary>View Command Reference</summary>

```bash
# Search for papers
> /find attention mechanisms for computer vision

# Add papers to your collection (by search result number)
> /add 1 3 5

# List papers in your collection
> /list

# Extract key points from a paper
> /distill 1

# Synthesize multiple papers
> /synthesize Compare transformer and CNN architectures

# Clear the screen
> /clear
```
</details>

## Features

### Paper Discovery
- Natural language search via Semantic Scholar API
- View abstracts and metadata before adding to collection

### Paper Management
- Build a local collection of research papers
- Automatic PDF download from ArXiv
- Duplicate detection and organized storage

### AI-Powered Analysis
- Extract key claims with supporting evidence
- Automatic section references and quotes
- Generate comprehensive literature reviews
- Proper inline citations (Author et al., Year)

### Natural Language Interface
- Chat-based interaction for complex queries
- Context-aware conversations about your research
- Multi-paper analysis and comparison

## Data Storage

LitAI stores all data locally in `~/.litai/`:
- `litai.db` - SQLite database with paper metadata and extractions
- `pdfs/` - Downloaded PDF files
- `logs/` - Application logs for debugging

## Development

<details>
<summary>Project Structure</summary>

```
litai/
├── src/litai/
│   ├── cli.py          # Command-line interface
│   ├── database.py     # Data persistence layer
│   ├── llm.py          # LLM client (OpenAI/Anthropic)
│   ├── papers.py       # Paper search and management
│   ├── pdf.py          # PDF processing
│   ├── synthesis.py    # Literature synthesis
│   └── tools.py        # Extraction tools
├── tests/              # Test suite
├── docs/               # Documentation
└── pyproject.toml      # Project configuration
```
</details>

<details>
<summary>Running Tests</summary>

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=litai

# Run specific test file
pytest tests/test_papers.py
```
</details>

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
