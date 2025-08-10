"""Tool definitions for natural language interface."""

from typing import Any, TypedDict


class ToolParameter(TypedDict):
    """Parameter definition for a tool."""

    type: str
    description: str
    required: bool
    enum: list[str] | None


class ToolDefinition(TypedDict):
    """Definition of a tool that can be called by the LLM."""

    name: str
    description: str
    parameters: dict[str, ToolParameter]


LITAI_TOOLS: list[ToolDefinition] = [
    {
        "name": "find_papers",
        "description": (
            "Search for academic papers on a specific topic using Semantic Scholar, "
            "or show recent search results"
        ),
        "parameters": {
            "query": {
                "type": "string",
                "description": (
                    "The search query or topic to find papers about "
                    "(omit to show recent results)"
                ),
                "required": False,
                "enum": None,
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of papers to return (default: 10)",
                "required": False,
                "enum": None,
            },
            "show_recent": {
                "type": "boolean",
                "description": (
                    "Show cached results from the last search (default: False)"
                ),
                "required": False,
                "enum": None,
            },
        },
    },
    {
        "name": "add_paper",
        "description": (
            "Add paper(s) from search results to the user's collection. "
            "Can add a single paper, multiple papers (comma-delimited), or all papers"
        ),
        "parameters": {
            "paper_numbers": {
                "type": "string",
                "description": (
                    "The paper number(s) to add. Can be: empty string (adds all), "
                    "single number (e.g. '1'), or comma-delimited list (e.g. '1,3,5')"
                ),
                "required": False,
                "enum": None,
            },
        },
    },
    {
        "name": "papers_command",
        "description": (
            "List papers in collection, show all tags, or filter by tags/notes"
        ),
        "parameters": {
            "page": {
                "type": "integer",
                "description": "The page number to display (default: 1)",
                "required": False,
                "enum": None,
            },
            "show_tags": {
                "type": "boolean",
                "description": (
                    "Show all tags in the database with paper counts "
                    "(default: False)"
                ),
                "required": False,
                "enum": None,
            },
            "show_notes": {
                "type": "boolean",
                "description": "Show only papers that have notes (default: False)",
                "required": False,
                "enum": None,
            },
            "tag_filter": {
                "type": "string",
                "description": "Filter papers by specific tag name",
                "required": False,
                "enum": None,
            },
        },
    },
    {
        "name": "remove_paper",
        "description": (
            "Remove paper(s) from the user's collection. Can remove a single "
            "paper, multiple papers (comma-delimited), or all papers"
        ),
        "parameters": {
            "paper_numbers": {
                "type": "string",
                "description": (
                    "The paper number(s) to remove. Can be: empty string "
                    "(removes all), single number (e.g. '1'), or comma-delimited "
                    "list (e.g. '1,3,5')"
                ),
                "required": False,
                "enum": None,
            },
        },
    },
    {
        "name": "manage_paper_tags",
        "description": "Add or remove tags for a specific paper in the collection",
        "parameters": {
            "paper_number": {
                "type": "integer",
                "description": "The paper number to manage tags for",
                "required": True,
                "enum": None,
            },
            "add_tags": {
                "type": "string",
                "description": (
                    "Comma-separated list of tags to add "
                    "(e.g. 'machine-learning,nlp')"
                ),
                "required": False,
                "enum": None,
            },
            "remove_tags": {
                "type": "string",
                "description": "Comma-separated list of tags to remove",
                "required": False,
                "enum": None,
            },
        },
    },
]


def get_openai_tools() -> list[dict[str, Any]]:
    """Convert tool definitions to OpenAI function calling format."""
    openai_tools = []

    for tool in LITAI_TOOLS:
        properties: dict[str, Any] = {}
        required = []

        for param_name, param_def in tool["parameters"].items():
            properties[param_name] = {
                "type": param_def["type"],
                "description": param_def["description"],
            }
            if param_def.get("enum"):
                properties[param_name]["enum"] = param_def["enum"]
            if param_def.get("required", False):
                required.append(param_name)

        openai_tool = {
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }
        openai_tools.append(openai_tool)

    return openai_tools


def get_anthropic_tools() -> list[dict[str, Any]]:
    """Convert tool definitions to Anthropic tool use format."""
    anthropic_tools = []

    for tool in LITAI_TOOLS:
        properties: dict[str, Any] = {}
        required = []

        for param_name, param_def in tool["parameters"].items():
            properties[param_name] = {
                "type": param_def["type"],
                "description": param_def["description"],
            }
            if param_def.get("enum"):
                properties[param_name]["enum"] = param_def["enum"]
            if param_def.get("required", False):
                required.append(param_name)

        anthropic_tool = {
            "name": tool["name"],
            "description": tool["description"],
            "input_schema": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        }
        anthropic_tools.append(anthropic_tool)

    return anthropic_tools
