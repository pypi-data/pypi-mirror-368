"""Main CLI entry point for LitAI."""

import asyncio
import json
import os
from collections.abc import Callable
from datetime import datetime
from typing import Any

import click
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import CompleteStyle
from prompt_toolkit.styles import Style
from pyfiglet import Figlet
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich.theme import Theme

from litai.config import Config
from litai.database import Database
from litai.extraction import PaperExtractor
from litai.llm import LLMClient
from litai.models import Paper
from litai.nl_handler import NaturalLanguageHandler
from litai.output_formatter import OutputFormatter
from litai.pdf_processor import PDFProcessor
from litai.semantic_scholar import SemanticScholarClient
from litai.synthesis_session import SynthesisSession
from litai.utils.logger import get_logger, setup_logging

# Define a custom theme with colors that work well on both dark and light terminals
custom_theme = Theme(
    {
        "primary": "#1f78b4",  # Medium blue
        "secondary": "#6a3d9a",  # Purple
        "success": "#33a02c",  # Green
        "warning": "#ff7f00",  # Orange
        "error": "#e31a1c",  # Red
        "info": "#a6cee3",  # Light blue
        "accent": "#b2df8a",  # Light green
        "number": "#fb9a99",  # Light red/pink
        "dim_text": "dim",
        "heading": "bold #1f78b4",
        "command": "#1f78b4",
        "command.collection": "#6a3d9a",
        "command.analysis": "#33a02c",
    },
)

console = Console(theme=custom_theme)
logger = get_logger(__name__)
output = OutputFormatter(console)

# Global search results storage (for /add command)
_search_results: list[Paper] = []
# Global synthesis session for interactive mode
_synthesis_session: SynthesisSession | None = None


@click.command()
@click.option("--debug", is_flag=True, help="Enable debug logging")
def main(debug: bool) -> None:
    """LitAI - AI-powered academic paper synthesis tool."""
    setup_logging(debug=debug)

    # Log application start
    logger.info("litai_start", debug=debug)

    # Initialize configuration and database
    config = Config()
    db = Database(config)

    # Generate personalized time-based greeting

    now = datetime.now()
    hour = now.hour

    if hour < 12:
        greeting = "Good morning"
    elif hour < 17:
        greeting = "Good afternoon"
    elif hour < 21:
        greeting = "Good evening"
    else:
        greeting = "Good night"

    # Get research snapshot data
    paper_count = db.count_papers()
    papers = db.list_papers(limit=100) if paper_count > 0 else []

    # Count read papers (those with key_points extraction)
    read_count = 0
    last_read_paper = None
    for paper in papers:
        if db.get_extraction(paper.paper_id, "key_points") is not None:
            read_count += 1
            if last_read_paper is None or (
                paper.added_at and paper.added_at > last_read_paper.added_at
            ):
                last_read_paper = paper

    # Count papers with notes
    notes_count = len(db.list_papers_with_notes())

    # Get last synthesis activity
    last_synthesis = db.get_last_synthesis_time()

    # Build personalized greeting
    from rich.columns import Columns
    from rich.panel import Panel

    # larry3d, isometric1, smkeyboard, epic, slant, ogre, crawford
    fig = Figlet(font="larry3d")
    console.print("\n")
    console.print(fig.renderText("LitAI"), style="bold cyan")

    console.print(f"\n[heading]{greeting}! Welcome back to LitAI[/heading]\n")

    if paper_count > 0:
        # Left column - research snapshot
        snapshot_lines = [
            "[bold]▚ Your research collection:[/bold]",
            f"  • [info]{paper_count}[/info] papers collected",
            f"  • [accent]{read_count}[/accent] papers analyzed",
        ]

        if notes_count > 0:
            snapshot_lines.append(
                f"  • [number]{notes_count}[/number] papers with notes",
            )

        if last_synthesis:
            time_diff = datetime.now() - last_synthesis
            if time_diff.days > 0:
                time_str = (
                    f"{time_diff.days} day{'s' if time_diff.days > 1 else ''} ago"
                )
            elif time_diff.seconds > 3600:
                hours = time_diff.seconds // 3600
                time_str = f"{hours} hour{'s' if hours > 1 else ''} ago"
            else:
                minutes = time_diff.seconds // 60
                time_str = f"{minutes} minute{'s' if minutes > 1 else ''} ago"
            snapshot_lines.append(f"  • Last synthesis: [dim]{time_str}[/dim]")

        if last_read_paper:
            snapshot_lines.append(
                f'  • Recently read: [dim]"{last_read_paper.title[:40]}..."[/dim]',
            )

        # Right column - natural language examples
        commands_lines = [
            "[bold]Continue your research:[/bold]",
            '"Find more papers about transformers"',
            '"What are the key insights from my recent papers?"',
            '"Compare the methods across my collection"',
            '"Show papers where I\'ve added notes"',
        ]

        # Add empty line if needed to match left column height
        if len(snapshot_lines) > len(commands_lines):
            commands_lines.append("")

        # Create columns with minimal spacing
        left_panel = Panel(
            "\n".join(snapshot_lines), border_style="none", padding=(0, 1, 0, 0),
        )
        right_panel = Panel(
            "\n".join(commands_lines), border_style="none", padding=(0, 0, 0, 1),
        )

        columns = Columns(
            [left_panel, right_panel], equal=False, expand=False, padding=(0, 2),
        )
        console.print(columns)

        console.print(
            "\n[dim_text]» Ask questions naturally and let AI handle the commands, or run them yourself[/dim_text]",
        )
        console.print(
            "[dim_text]   Need ideas? Try [command]/questions[/command] for research-unblocking prompts[/dim_text]",
        )
        console.print(
            "[dim_text]   See [command]/help[/command] for all commands or use [command]--help[/command] flag with any command[/dim_text]",
        )

        # Show vi mode status if enabled
        if config.get_vi_mode():
            console.print(
                "[dim_text]   Vi mode is enabled • Press ESC to enter normal mode[/dim_text]",
            )

        console.print()  # Add blank line
    else:
        # For new users, show research workflow with natural language first
        console.print("[bold]Start your research workflow (run these in order):[/bold]")
        console.print(
            '1. "Find papers about attention mechanisms" [dim_text](searches for papers)[/dim_text]',
        )
        console.print(
            "2. \"Add 'Attention Is All You Need' to my collection\" [dim_text](saves found papers)[/dim_text]",
        )
        console.print(
            '3. "What are the key insights from the BERT paper?" [dim_text](analyzes saved papers)[/dim_text]',
        )
        console.print(
            '4. "How do Vision Transformer\'s methods compare to other papers?" [dim_text](synthesizes across collection)[/dim_text]',
        )
        console.print(
            "\n[dim_text]Or use commands directly: [command]/find[/command], [command]/add[/command], [command]/synthesize[/command][/dim_text]",
        )
        console.print(
            "[dim_text]Need help? • [command]/help[/command] shows all commands • Use [command]--help[/command] flag with any command[/dim_text]",
        )

    chat_loop(db)


class CommandCompleter(Completer):
    """Custom completer for LitAI commands."""

    def __init__(self) -> None:
        # Controls autocomplete for commands
        self.commands = {
            "/find": "Search for papers",
            "/add": "Add paper to collection",
            "/papers": "List and manage papers in your collection",
            "/remove": "Remove paper(s) from collection",
            "/synthesize": "Enter interactive synthesis mode for collaborative paper exploration",
            "/questions": "Show research unblocking questions to ask LitAI",
            "/note": "Manage notes for a paper",
            "/agent-note": "Manage agent notes for a paper",
            "/tag": "Manage tags for a paper",
            "/import": "Import papers from BibTeX file",
            "/prompt": "Manage your personal research context and preferences",
            # "/hf-daily": "Browse HF papers",
            "/help": "Show all commands",
            "/clear": "Clear the console",
            "/config": "Manage LLM configuration",
        }

    def get_completions(self, document: Any, complete_event: Any) -> Any:
        """Get completions for the current input."""
        text = document.text_before_cursor
        
        # Commands that support --help flag
        help_enabled_commands = [
            "/find", "/papers", "/add", "/remove", 
            "/synthesize", "/note", "/tag", "/prompt", "/config",
        ]

        # Flag completion for /find command
        if text.startswith("/find "):
            remaining = text[6:].strip()  # Remove "/find "
            if remaining.startswith("-"):
                # Suggest flags
                flags = ["--recent", "--help"]
                for flag in flags:
                    if flag.startswith(remaining):
                        yield Completion(
                            f"/find {flag}",
                            start_position=-len(text),
                            display=flag,
                            display_meta="Show recent results" if flag == "--recent" else "Show help",
                        )
            return

        # Flag completion for /papers command
        if text.startswith("/papers "):
            remaining = text[8:].strip()  # Remove "/papers "
            if remaining.startswith("-"):
                # Suggest flags
                flag_options = [
                    ("--tags", "Show all tags"),
                    ("--notes", "Show papers with notes"),
                    ("--help", "Show help"),
                ]
                for flag, desc in flag_options:
                    if flag.startswith(remaining):
                        yield Completion(
                            f"/papers {flag}",
                            start_position=-len(text),
                            display=flag,
                            display_meta=desc,
                        )
            return
            
        # Generic --help flag completion for other commands
        for cmd in help_enabled_commands:
            if cmd in ["/find", "/papers"]:  # Skip commands with custom handling
                continue
            if text.startswith(f"{cmd} "):
                remaining = text[len(cmd)+1:].strip()
                if remaining.startswith("-"):
                    if "--help".startswith(remaining):
                        yield Completion(
                            f"{cmd} --help",
                            start_position=-len(text),
                            display="--help",
                            display_meta="Show help",
                        )
                return

        # Path completion for /import
        if text.startswith("/import "):
            path = text[8:]  # Remove "/import "
            original_path = path  # Keep original for completion
            path = os.path.expanduser(path)  # Handle ~/
            
            if path and not path.endswith('/'):
                dir_path = os.path.dirname(path) or "."
                prefix = os.path.basename(path)
            else:
                dir_path = path or "."
                prefix = ""
            
            try:
                for name in os.listdir(os.path.expanduser(dir_path)):
                    if name.startswith(prefix):
                        full = os.path.join(dir_path, name)
                        if os.path.isdir(full):
                            name += "/"
                        elif not name.endswith(('.pdf', '.bib')):
                            continue
                        
                        # Build the completion text (without /import prefix)
                        if original_path.endswith('/'):
                            completion = original_path + name
                        else:
                            completion = os.path.join(os.path.dirname(original_path), name) if os.path.dirname(original_path) else name
                        
                        # The key fix: prepend "/import " to the completion
                        full_completion = "/import " + completion
                        
                        yield Completion(
                            full_completion,
                            start_position=-len(text),  # Replace entire text including "/import "
                            display=name,
                        )
            except Exception:
                pass
            return

        # Only complete if user started typing a command
        if not text.startswith("/"):
            return

        # Get matching commands
        for cmd, description in self.commands.items():
            if cmd.startswith(text):
                yield Completion(
                    cmd,
                    start_position=-len(text),
                    display=cmd,
                    display_meta=description,
                )


def chat_loop(db: Database) -> None:
    """Main interactive chat loop."""
    global _search_results
    global _synthesis_session

    # Initialize config once for all commands
    config = Config()

    # Create minimal style for better readability
    style = Style.from_dict(
        {
            # Ensure completion menu has good contrast
            "completion-menu.completion": "",  # Use terminal defaults
            "completion-menu.completion.current": "reverse",  # Invert colors for selection
            "completion-menu.meta.completion": "fg:ansibrightblack",  # Dimmed description
            "completion-menu.meta.completion.current": "reverse",  # Invert for selection
        },
    )

    # Create command completer and prompt session
    completer = CommandCompleter()
    session: PromptSession = PromptSession(
        completer=completer,
        complete_while_typing=False,  # Only show completions on Tab
        mouse_support=True,
        # Ensure completions appear below the input
        reserve_space_for_menu=0,  # Don't reserve space, show inline
        complete_style=CompleteStyle.MULTI_COLUMN,
        style=style,
        vi_mode=config.get_vi_mode(),  # Enable vi mode based on config
    )

    # Create natural language handler with command mappings
    command_handlers: dict[str, Callable[..., Any]] = {
        "find_papers": find_papers,
        "add_paper": add_paper,
        "list_papers": list_papers,
        "remove_paper": remove_paper,
        "show_search_results": show_search_results,
        "handle_tag_command": handle_tag_command,
        "list_tags": list_tags,
    }

    nl_handler = NaturalLanguageHandler(db, command_handlers, _search_results, config)

    try:
        while True:
            try:
                prompt_text = HTML("<ansiblue><b>normal ▸</b></ansiblue> ")

                # Use prompt_toolkit for rich input
                user_input = session.prompt(
                    prompt_text,
                    default="",
                )

                # Skip empty lines
                if not user_input.strip():
                    continue

                # Log user input
                logger.info("user_input", input=user_input)

                if user_input.lower() in ["exit", "quit", "q"]:
                    logger.info("user_exit", method=user_input.lower())
                    console.print("[warning]Goodbye![/warning]")
                    break


                if user_input.startswith("/"):
                    handle_command(user_input, db, config)
                elif user_input.lower() == "clear":
                    console.clear()
                else:
                    # Handle natural language query
                    asyncio.run(nl_handler.handle_query(user_input))

            except KeyboardInterrupt:
                console.print("\n[warning]Tip: Use 'exit' to quit.[/warning]")
            except Exception as e:
                logger.exception("Unexpected error in chat loop")
                from rich.markup import escape

                console.print(f"[error]Error: {escape(str(e))}[/error]")
    finally:
        # Cleanup the NL handler when exiting
        try:
            asyncio.run(nl_handler.close())
        except Exception:
            # Ignore errors during cleanup
            pass

        # Cleanup the Semantic Scholar client
        try:
            from litai.semantic_scholar import SemanticScholarClient

            asyncio.run(SemanticScholarClient.shutdown())
        except Exception:
            # Ignore errors during cleanup
            pass


def handle_command(command: str, db: Database, config: Config | None = None) -> None:
    """Handle slash commands."""
    parts = command.split(maxsplit=1)
    cmd = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""

    # Log command execution
    logger.info("command_executed", command=cmd, args=args)

    if cmd == "/help":
        show_help()
    elif cmd == "/find":
        # Parse flags for /find command
        if args and args.strip() == "--help":
            show_find_help()
            return
        if args and args.strip() == "--recent":
            show_search_results()
            return
        if not args:
            output.error("Please provide a search query. Usage: /find <query> or /find --recent or /find --help")
            return
        asyncio.run(find_papers(args))
    elif cmd == "/add":
        add_paper(args, db)
    elif cmd == "/papers":
        handle_papers_command(args, db)
    elif cmd == "/remove":
        remove_paper(args, db)
    elif cmd == "/synthesize":
        # Check for --help flag
        if args.strip() == "--help":
            show_command_help("synthesize")
            return
        # Always enter interactive synthesis mode
        if config:
            enter_synthesis_mode(db, config)
        else:
            console.print("[red]Configuration not loaded[/red]")
    elif cmd == "/questions":
        show_research_questions()
    elif cmd == "/note" or cmd == "/note":
        asyncio.run(handle_note_command(args, db))
    elif cmd == "/agent-note":
        asyncio.run(handle_agent_note_command(args,db))
    elif cmd == "/tag":
        handle_tag_command(args, db)
    elif cmd == "/import":
        handle_import_command(args, db, config)
    elif cmd == "/clear":
        console.clear()
    elif cmd == "/config":
        if config:
            handle_config_command(args, config)
        else:
            console.print("[red]Configuration not available[/red]")
    elif cmd == "/prompt":
        if config:
            handle_prompt_command(args, config)
        else:
            console.print("[red]Configuration not available[/red]")
    else:
        logger.warning("unknown_command", command=cmd, args=args)
        console.print(f"[error]Unknown command: {cmd}[/error]")
        console.print("Type '/help' for available commands.")


async def find_papers(query: str) -> str:
    """Search for papers using Semantic Scholar.

    Returns:
        A summary string describing the search results for LLM context.
    """
    global _search_results

    try:
        logger.info("find_papers_start", query=query)
        output.search_status(query)

        async with SemanticScholarClient() as client:
            papers = await client.search(query, limit=10)

        if not papers:
            logger.info("find_papers_no_results", query=query)
            output.error(f"No papers found matching '{query}'")
            return f"No papers found matching '{query}'"

        # Store results for /add command
        _search_results = papers
        logger.info("find_papers_success", query=query, result_count=len(papers))

        output.search_complete(len(papers))

        # Create a table for results
        table = Table(show_header=True)
        table.add_column("No.", style="number", width=4)
        table.add_column("Title", style="bold")
        table.add_column(
            "Authors", style="dim_text", width=25,
        )  # Increased width to prevent wrapping
        table.add_column("Year", style="dim_text", width=6)
        table.add_column("Citations", style="dim_text", width=10)

        for i, paper in enumerate(papers, 1):
            # Truncate title if too long
            title = paper.title[:80] + "..." if len(paper.title) > 80 else paper.title

            # Format authors
            if len(paper.authors) > 2:
                authors = f"{paper.authors[0]}, {paper.authors[1]}, et al."
            else:
                authors = ", ".join(paper.authors)

            table.add_row(
                str(i),
                title,
                authors,
                str(paper.year) if paper.year else "N/A",
                str(paper.citation_count),
            )

        console.print(table)
        console.print(
            "\n[warning]⊹ Tip: Use /add <number> to add a paper to your collection[/warning]",
        )

        # Return summary for LLM
        paper_summaries = []
        for i, paper in enumerate(papers, 1):
            authors_str = ", ".join(paper.authors[:2])
            if len(paper.authors) > 2:
                authors_str += " et al."
            paper_summaries.append(
                f'{i}. "{paper.title}" by {authors_str} ({paper.year}, {paper.citation_count} citations)',
            )

        return f"Found {len(papers)} papers matching '{query}':\n" + "\n".join(
            paper_summaries,
        )

    except Exception as e:
        output.error(f"Search failed: {e}")
        logger.exception("Search failed", query=query)
        return f"Search failed: {str(e)}"


def show_search_results() -> None:
    """Show the currently cached search results."""
    global _search_results

    logger.info("show_results_start")

    if not _search_results:
        logger.info("show_results_empty")
        console.print(
            "[warning]Warning: No search results cached. Use [command]/find[/command] to search for papers.[/warning]",
        )
        return

    logger.info("show_results_success", result_count=len(_search_results))

    # Create a table for cached results
    table = Table(title="Cached Search Results", show_header=True)
    table.add_column("No.", style="number", width=4)
    table.add_column("Title", style="bold")
    table.add_column("Authors", style="dim_text", width=25)
    table.add_column("Year", style="dim_text", width=6)
    table.add_column("Citations", style="dim_text", width=10)

    for i, paper in enumerate(_search_results, 1):
        # Truncate title if too long
        title = paper.title[:80] + "..." if len(paper.title) > 80 else paper.title

        # Format authors
        if len(paper.authors) > 2:
            authors = f"{paper.authors[0]}, {paper.authors[1]}, et al."
        else:
            authors = ", ".join(paper.authors)

        table.add_row(
            str(i),
            title,
            authors,
            str(paper.year) if paper.year else "N/A",
            str(paper.citation_count),
        )

    console.print(table)
    console.print(
        "\n[warning]⊹ Tip: Use /add <number> to add a paper to your collection[/warning]",
    )


def remove_paper(args: str, db: Database) -> None:
    """Remove paper(s) from the collection."""
    logger.info("remove_paper_start", args=args)
    
    # Check for --help flag
    if args.strip() == "--help":
        show_command_help("remove")
        return

    papers = db.list_papers()
    if not papers:
        logger.warning("remove_paper_no_papers")
        console.print(
            "[yellow]Warning: No papers in your collection to remove.[/yellow]",
        )
        return

    try:
        if not args.strip():
            # Empty input - remove all papers
            console.print(
                f"[yellow]Remove all {len(papers)} papers from collection?[/yellow]",
            )
            confirm = console.input("[yellow]Type 'yes' to confirm: [/yellow]")
            if confirm.lower() != "yes":
                console.print("[red]Cancelled[/red]")
                return

            paper_indices = list(range(len(papers)))
            skip_second_confirmation = True  # Flag to skip the second confirmation
        else:
            # Parse comma-delimited paper numbers
            paper_indices = []
            skip_second_confirmation = False  # Flag to enable second confirmation
            for num_str in args.split(","):
                num_str = num_str.strip()
                if not num_str:
                    continue
                try:
                    paper_num = int(num_str)
                    if paper_num < 1 or paper_num > len(papers):
                        console.print(
                            f"[red]Invalid paper number: {paper_num}. Must be between 1 and {len(papers)}[/red]",
                        )
                        return
                    paper_indices.append(paper_num - 1)
                except ValueError:
                    console.print(f"[error]Invalid number: '{num_str}'[/error]")
                    return

        # Show papers to be removed and get confirmation (skip if already confirmed)
        if not skip_second_confirmation:
            if len(paper_indices) > 1:
                console.print(
                    f"\n[yellow]Are you sure you want to remove {len(paper_indices)} papers?[/yellow]",
                )
                for idx in paper_indices[:5]:  # Show first 5
                    paper = papers[idx]
                    console.print(f"  • {paper.title[:60]}...")
                if len(paper_indices) > 5:
                    console.print(f"  ... and {len(paper_indices) - 5} more")
            else:
                paper = papers[paper_indices[0]]
                console.print(
                    "\n[yellow]Are you sure you want to remove this paper?[/yellow]",
                )
                console.print(f"Title: {paper.title}")
                console.print(f"Authors: {', '.join(paper.authors[:3])}")
                if len(paper.authors) > 3:
                    console.print(f"... and {len(paper.authors) - 3} more")

            confirmation = Prompt.ask(
                "\nConfirm removal?", choices=["yes", "y", "no", "n"], default="no",
            )

            if confirmation not in ["yes", "y"]:
                console.print("[red]Cancelled[/red]")
                return

        # Proceed with removal
        removed_count = 0
        failed_count = 0

        for idx in paper_indices:
            paper = papers[idx]
            success = db.delete_paper(paper.paper_id)
            if success:
                logger.info(
                    "remove_paper_success", paper_id=paper.paper_id, title=paper.title,
                )
                removed_count += 1
                if len(paper_indices) == 1:
                    console.print(
                        f"[green]✓ Removed from collection: '{paper.title}'[/green]",
                    )
            else:
                logger.error(
                    "remove_paper_failed", paper_id=paper.paper_id, title=paper.title,
                )
                failed_count += 1

        # Summary
        if len(paper_indices) > 1:
            console.print(f"\n[green]✓ Removed {removed_count} papers[/green]")
            if failed_count:
                console.print(f"[red]Failed to remove {failed_count} papers[/red]")

        console.print(
            "\n[yellow]⊹ Tip: Use /papers to see your updated collection[/yellow]",
        )

    except Exception as e:
        console.print(f"[red]Error removing papers: {e}[/red]")
        logger.exception("Failed to remove papers", args=args)


def add_paper(args: str, db: Database) -> None:
    """Add a paper from search results to the collection."""
    global _search_results

    logger.info("add_paper_start", args=args)
    
    # Check for --help flag
    if args.strip() == "--help":
        show_command_help("add")
        return

    if not _search_results:
        logger.warning("add_paper_no_results")
        console.print(
            "[warning]Warning: No search results available. Use [command]/find[/command] first to search for papers.[/warning]",
        )
        return

    # Parse tags if provided with --tags option
    tags_to_add = []
    actual_args = args
    if "--tags" in args:
        parts = args.split("--tags")
        actual_args = parts[0].strip()
        if len(parts) > 1:
            tag_str = parts[1].strip()
            tags_to_add = [t.strip() for t in tag_str.split(",") if t.strip()]

    try:
        if not actual_args:
            # Empty input - add all papers
            console.print(
                f"[yellow]Add all {len(_search_results)} papers to collection?[/yellow]",
            )
            confirm = console.input("[yellow]Type 'yes' to confirm: [/yellow]")
            if confirm.lower() != "yes":
                console.print("[red]Cancelled[/red]")
                return

            paper_indices = list(range(len(_search_results)))
        else:
            # Parse comma-delimited paper numbers
            paper_indices = []
            for num_str in actual_args.split(","):
                num_str = num_str.strip()
                if not num_str:
                    continue
                try:
                    paper_num = int(num_str)
                    if paper_num < 1 or paper_num > len(_search_results):
                        console.print(
                            f"[error]Invalid paper number: {paper_num}. Must be between 1 and {len(_search_results)}[/error]",
                        )
                        return
                    paper_indices.append(paper_num - 1)
                except ValueError:
                    console.print(f"[error]Invalid number: '{num_str}'[/error]")
                    return

        # Add papers
        added_count = 0
        duplicate_count = 0
        
        # Get existing citation keys to avoid duplicates
        existing_papers = db.list_papers(limit=1000)
        existing_keys = {p.citation_key for p in existing_papers if p.citation_key}

        for idx in paper_indices:
            paper = _search_results[idx]
            existing = db.get_paper(paper.paper_id)

            if existing:
                logger.info(
                    "add_paper_duplicate", paper_id=paper.paper_id, title=paper.title,
                )
                duplicate_count += 1
                continue

            # Generate citation key before adding
            paper.citation_key = paper.generate_citation_key(existing_keys)
            existing_keys.add(paper.citation_key)
            
            success = db.add_paper(paper)
            if success:
                logger.info(
                    "add_paper_success", paper_id=paper.paper_id, title=paper.title,
                )
                added_count += 1
                output.success(f"Added: '{paper.title}'")

                # Add tags if provided
                if tags_to_add:
                    db.add_tags_to_paper(paper.paper_id, tags_to_add)
                    console.print(f"  Tagged with: {output.format_tags(tags_to_add)}")
            else:
                logger.error(
                    "add_paper_failed", paper_id=paper.paper_id, title=paper.title,
                )
                output.error(f"Failed to add: '{paper.title}'")

        # Summary
        console.print(f"[success]✓ Added {added_count} papers[/success]")
        if duplicate_count:
            console.print(f"[warning]Skipped {duplicate_count} duplicates[/warning]")

        # Show tip
        if added_count > 0:
            console.print(
                "\n[warning]⊹ Tip: Use /papers to see your collection or /synthesize to analyze papers[/warning]",
            )

    except Exception as e:
        console.print(f"[error]Error adding papers: {e}[/error]")
        logger.exception("Failed to add papers", args=args)


def list_papers(db: Database, page: int = 1, tag_filter: str | None = None) -> str:
    """List all papers in the collection with pagination.

    Args:
        db: Database instance
        page: Page number (1-indexed)
        tag_filter: Optional tag name to filter by

    Returns:
        A summary string describing the papers in the collection for LLM context.
    """
    # Column configuration mapping
    COLUMN_CONFIG: dict[str, dict[str, Any]] = {
        # Core identification
        "no": {"name": "No.", "style": "secondary", "width": 4},
        "title": {"name": "Title", "style": "bold", "ratio": 4},
        # Authors and venue
        "authors": {
            "name": "Authors",
            "style": "dim_text",
            "width": 25,
            "no_wrap": True,
        },
        "venue": {"name": "Venue", "style": "dim_text", "ratio": 2},
        # Temporal and metrics
        "year": {"name": "Year", "style": "dim_text", "width": 6},
        "citations": {"name": "Citations", "style": "dim_text", "width": 6},
        "added_at": {"name": "Added", "style": "dim_text", "width": 10},
        # Status indicators
        "ai_notes": {"name": "AI Notes", "style": "success", "width": 8},
        "notes": {"name": "Notes", "style": "info", "width": 5},
        "tags": {"name": "Tags", "style": "cyan", "ratio": 2},
        # Content fields
        "abstract": {
            "name": "Abstract",
            "style": "dim_text",
            "ratio": 3,
            "truncate": 100,
        },
        "tldr": {"name": "TL;DR", "style": "dim_text", "ratio": 2},
        # Identifiers
        "doi": {"name": "DOI", "style": "dim_text", "width": 15, "no_wrap": True},
        "arxiv_id": {"name": "ArXiv", "style": "dim_text", "width": 12},
        "citation_key": {"name": "Cite Key", "style": "dim_text", "width": 15},
    }

    page_size = 20  # Papers per page
    offset = (page - 1) * page_size

    logger.info("list_papers_start", page=page, offset=offset, tag_filter=tag_filter)

    # If tag filter, we need to get filtered papers
    if tag_filter:
        # Get all papers with the tag (no pagination for tag search)
        all_tagged_papers = db.list_papers(limit=1000, offset=0, tag=tag_filter)
        total_count = len(all_tagged_papers)

        if total_count == 0:
            logger.info("list_papers_empty_tag", tag=tag_filter)
            console.print(
                f"[warning]No papers found with tag '{tag_filter}'. Use [command]/papers --tags[/command] to see available tags.[/warning]",
            )
            return f"No papers found with tag '{tag_filter}'."

        # Calculate total pages for tagged papers
        total_pages = (total_count + page_size - 1) // page_size

        # Validate page number
        if page < 1 or page > total_pages:
            console.print(
                f"[error]Invalid page number. Please choose between 1 and {total_pages}[/error]",
            )
            return f"Invalid page number. Total pages: {total_pages}"

        # Get papers for current page from the filtered list
        start_idx = offset
        end_idx = min(start_idx + page_size, total_count)
        papers = all_tagged_papers[start_idx:end_idx]
    else:
        # Get total count first to check if collection is empty
        total_count = db.count_papers()

        if total_count == 0:
            logger.info("list_papers_empty")
            console.print(
                "[warning]Warning: No papers in your collection yet. Use [command]/find[/command] to search for papers.[/warning]",
            )
            return "Your collection is empty. No papers found."

        # Calculate total pages
        total_pages = (total_count + page_size - 1) // page_size

        # Validate page number
        if page < 1 or page > total_pages:
            console.print(
                f"[error]Invalid page number. Please choose between 1 and {total_pages}[/error]",
            )
            return f"Invalid page number. Total pages: {total_pages}"

        # Get papers for current page
        papers = db.list_papers(limit=page_size, offset=offset)
    logger.info(
        "list_papers_success",
        paper_count=len(papers),
        total_count=total_count,
        page=page,
        total_pages=total_pages,
    )

    # Show section header
    if tag_filter:
        output.section(
            f"Papers tagged #{tag_filter} ({total_count} papers)", "🏷️", "bold cyan",
        )
    else:
        output.section(f"Your Collection ({total_count} papers)", "⧉", "bold secondary")
    if total_pages > 1:
        console.print(f"[dim_text]Page {page} of {total_pages}[/dim_text]\n")

    # Get configured columns
    config = Config()
    configured_columns = config.get_list_columns()

    # Build table with configured columns only
    table = Table(show_header=True, expand=True)
    for col_key in configured_columns:
        if col_key not in COLUMN_CONFIG:
            logger.warning(f"Unknown column configured: {col_key}")
            continue

        col_info = COLUMN_CONFIG[col_key]
        table.add_column(
            col_info["name"],
            style=col_info.get("style", ""),
            width=col_info.get("width"),
            ratio=col_info.get("ratio"),
            no_wrap=col_info.get("no_wrap", False),
        )

    for i, paper in enumerate(papers):
        # Calculate the actual paper number accounting for pagination
        paper_num = offset + i + 1

        # Build row data based on configured columns
        row_data = []
        for col_key in configured_columns:
            if col_key == "no":
                row_data.append(str(paper_num))
            elif col_key == "title":
                title = (
                    paper.title[:120] + "..." if len(paper.title) > 120 else paper.title
                )
                row_data.append(title)
            elif col_key == "authors":
                if len(paper.authors) > 2:
                    authors = f"{paper.authors[0]}, {paper.authors[1]}, et al."
                else:
                    authors = ", ".join(paper.authors)
                row_data.append(authors)
            elif col_key == "year":
                row_data.append(str(paper.year) if paper.year else "N/A")
            elif col_key == "citations":
                row_data.append(str(paper.citation_count))
            elif col_key == "ai_notes":
                has_agent_notes = db.get_agent_note(paper.paper_id) is not None
                row_data.append("✓" if has_agent_notes else "")
            elif col_key == "notes":
                has_notes = db.get_note(paper.paper_id) is not None
                row_data.append("✓" if has_notes else "")
            elif col_key == "tags":
                if paper.tags:
                    tags_display = ", ".join([f"#{tag}" for tag in paper.tags[:3]])
                    if len(paper.tags) > 3:
                        tags_display += f" +{len(paper.tags) - 3}"
                    row_data.append(tags_display)
                else:
                    row_data.append("")
            elif col_key == "venue":
                row_data.append(paper.venue if paper.venue else "N/A")
            elif col_key == "abstract":
                truncate_len = int(COLUMN_CONFIG[col_key].get("truncate", 100))
                abstract = (
                    paper.abstract[:truncate_len] + "..."
                    if paper.abstract and len(paper.abstract) > truncate_len
                    else paper.abstract or ""
                )
                row_data.append(abstract)
            elif col_key == "tldr":
                row_data.append(paper.tldr if paper.tldr else "")
            elif col_key == "doi":
                row_data.append(paper.doi if paper.doi else "")
            elif col_key == "arxiv_id":
                row_data.append(paper.arxiv_id if paper.arxiv_id else "")
            elif col_key == "citation_key":
                row_data.append(paper.citation_key if paper.citation_key else "")
            elif col_key == "added_at":
                row_data.append(paper.added_at.strftime("%Y-%m-%d"))
            else:
                row_data.append("")  # Unknown column

        table.add_row(*row_data)

    console.print(table)

    # Show pagination info
    if total_pages > 1:
        console.print(
            f"\n[dim_text]Page {page} of {total_pages} • Papers {offset + 1}-{offset + len(papers)} of {total_count}[/dim_text]",
        )

        # Show navigation hints
        nav_hints = []
        if page > 1:
            nav_hints.append("/papers 1 (first page)")
            nav_hints.append(f"/papers {page - 1} (previous)")
        if page < total_pages:
            nav_hints.append(f"/papers {page + 1} (next)")
            nav_hints.append(f"/papers {total_pages} (last page)")

        if nav_hints:
            console.print(f"[dim_text]Navigate: {' • '.join(nav_hints)}[/dim_text]")

    output.tip(
        "Use /synthesize to extract key points or analyze across papers",
    )

    # Return summary for LLM
    paper_summaries = []
    for i, paper in enumerate(papers[:10], 1):  # Include top 10 for LLM context
        authors_str = ", ".join(paper.authors[:2])
        if len(paper.authors) > 2:
            authors_str += " et al."
        paper_summaries.append(f'{i}. "{paper.title}" by {authors_str} ({paper.year})')

    result = f"Found {total_count} papers in your collection."
    if paper_summaries:
        result += " Top papers:\n" + "\n".join(paper_summaries)
    return result


def show_papers_help() -> None:
    """Show help for the /papers command."""
    output.section("Papers Command Help", "⧉", "bold secondary")
    
    console.print("[bold]Usage:[/bold] /papers [page_number] [--tags] [--notes] [--help]\n")
    
    console.print("[bold]Description:[/bold]")
    console.print("  List and manage papers in your collection with various filters\n")
    
    console.print("[bold]Options:[/bold]")
    console.print("  [command]page_number[/command]  Page number for pagination (default: 1)")
    console.print("  [command]--tags[/command]        Show all tags with paper counts")
    console.print("  [command]--notes[/command]       Show papers that have notes")
    console.print("  [command]--help[/command]        Show this help message\n")
    
    console.print("[bold]Examples:[/bold]")
    console.print("  [command]/papers[/command]           # List first page of papers")
    console.print("  [command]/papers 2[/command]         # Show page 2 of papers")
    console.print("  [command]/papers --tags[/command]    # Show all tags")
    console.print("  [command]/papers --notes[/command]   # Show papers with notes")


def handle_papers_command(args: str, db: Database) -> None:
    """Handle the /papers command with various flags."""
    if not args:
        # No arguments - show first page
        list_papers(db, page=1)
        return
    
    args = args.strip()
    
    # Check for flags
    if args == "--help":
        show_papers_help()
        return
    if args == "--tags":
        list_tags(db)
        return
    if args == "--notes":
        list_papers_with_notes(db)
        return
    
    # Try to parse as page number
    try:
        page = int(args)
        list_papers(db, page=page)
    except ValueError:
        # Check if it's a tag filter (backward compatibility)
        if args.startswith("--tag "):
            tag_parts = args[6:].strip().split(maxsplit=1)
            if tag_parts:
                tag_filter = tag_parts[0]
                page = 1
                if len(tag_parts) > 1:
                    try:
                        page = int(tag_parts[1])
                    except ValueError:
                        pass
                list_papers(db, page=page, tag_filter=tag_filter)
            else:
                output.error("Please provide a tag name. Usage: /papers --tag <tag_name>")
        else:
            output.error(f"Invalid argument: {args}. Use /papers --help for usage.")



def enter_synthesis_mode(db: Database, config: Config) -> None:
    """Enter interactive synthesis mode with LLM conversation loop."""
    global _synthesis_session
    
    console.print("\n[bold cyan]◈ Entering Synthesis Mode[/bold cyan]")
    console.print("[dim]Chat naturally about your papers. I'll use tools as needed.[/dim]\n")
    
    # Create synthesis-specific completer
    synthesis_completer = SynthesisCompleter()
    
    # Create a new prompt session for synthesis mode
    synthesis_prompt_session: PromptSession = PromptSession(
        completer=synthesis_completer,
        complete_while_typing=False,
        mouse_support=True,
        complete_style=CompleteStyle.MULTI_COLUMN,
        vi_mode=config.get_vi_mode(),
    )
    
    # Initialize conversation handler
    llm_client = None
    conversation = None
    
    try:
        llm_client = LLMClient(config)
        pdf_processor = PDFProcessor(db, config.base_dir)
        extractor = PaperExtractor(db, llm_client, pdf_processor)
        
        from litai.synthesis_tools import SynthesisConversation, SynthesisOrchestrator
        orchestrator = SynthesisOrchestrator(db, llm_client, extractor)
        conversation = SynthesisConversation(db, llm_client, orchestrator, config)
        _synthesis_session = conversation.session
        
        while True:
            try:
                # Build and show status line before prompt
                status_parts = []
                
                # Add paper count if any
                paper_count = len(conversation.session.selected_papers)
                total_papers = db.count_papers()
                if paper_count > 0:
                    status_parts.append(f"{paper_count}/{total_papers} papers")
                else:
                    status_parts.append(f"{total_papers} papers available")
                
                # Add context type
                context_type = conversation.session.context_type
                status_parts.append(f"{context_type}")
                
                # Add model info
                model_name = llm_client.model or "unknown"
                # Shorten model names for display
                if "gpt-4" in model_name:
                    model_display = "GPT-4"
                elif "gpt-3.5" in model_name:
                    model_display = "GPT-3.5"
                elif "claude" in model_name:
                    if "opus" in model_name:
                        model_display = "Claude Opus"
                    elif "sonnet" in model_name:
                        model_display = "Claude Sonnet"
                    else:
                        model_display = "Claude"
                elif "o4" in model_name or "o3" in model_name:
                    model_display = model_name.split("-")[0].upper()
                else:
                    model_display = model_name.split("-")[0]
                status_parts.append(model_display)
                
                # Display status line (commented out but kept for future use)
                # status_line = " | ".join(status_parts)
                # console.print(f"[dim][ {status_line} ][/dim]")
                
                # Get user input
                prompt_text = HTML("<ansicyan><b>synthesis ▸</b></ansicyan> ")
                user_input = synthesis_prompt_session.prompt(prompt_text, default="")
                
                if not user_input.strip():
                    continue
                    
                # Handle exit
                if user_input.lower() in ["exit", "done", "/exit"]:
                    console.print("[yellow]Exiting synthesis mode.[/yellow]")
                    break
                
                # Handle slash commands locally (don't send to LLM)
                if user_input.startswith("/"):
                    if user_input.startswith("/list"):
                        # Show all papers in collection (same as main CLI /list)
                        parts = user_input.split(maxsplit=1)
                        args = parts[1] if len(parts) > 1 else ""
                        
                        tag_filter = None
                        page = 1
                        
                        if args:
                            args_parts = args.strip().split()
                            if args_parts[0] == "--tag" and len(args_parts) >= 2:
                                # Tag filter provided
                                tag_filter = args_parts[1]
                                # Check if page number provided after tag
                                if len(args_parts) >= 3:
                                    try:
                                        page = int(args_parts[2])
                                    except ValueError:
                                        console.print(
                                            "[red]Invalid page number. Usage: /list --tag <tag_name> [page_number][/red]",
                                        )
                                        continue
                            else:
                                # Just page number
                                try:
                                    page = int(args_parts[0])
                                except ValueError:
                                    console.print(
                                        "[red]Invalid argument. Usage: /list [page_number] or /list --tag <tag_name> [page_number][/red]",
                                    )
                                    continue
                        
                        list_papers(db, page, tag_filter)
                        continue
                        
                    if user_input.startswith("/selected"):
                        logger.info(f"Slash command: /selected, papers in session: {len(conversation.session.selected_papers)}")
                        # Show current papers in session
                        if conversation.session.selected_papers:
                            console.print("\n[bold]Selected Papers in Session:[/bold]")
                            for i, paper in enumerate(conversation.session.selected_papers, 1):
                                console.print(f"{i}. {paper.title} ({paper.year})")
                        else:
                            console.print("[yellow]No papers selected yet.[/yellow]")
                        continue
                        
                    if user_input.startswith("/papers"):
                        # Show all papers in collection (normal papers command)
                        parts = user_input.split(maxsplit=1)
                        args = parts[1] if len(parts) > 1 else ""
                        handle_papers_command(args, db)
                        continue
                        
                    if user_input.startswith("/context"):
                        # Change context depth
                        parts = user_input.split(maxsplit=1)
                        logger.info(f"Slash command: /context {parts[1] if len(parts) > 1 else '(show)'}")
                        if len(parts) > 1:
                            context_type = parts[1].strip()
                            if context_type in ["abstracts", "notes", "agent_notes", "sections", "full_text"]:
                                asyncio.run(conversation.session.change_context_depth(context_type))
                                console.print(f"[green]Context depth changed to: {context_type}[/green]")
                            else:
                                console.print("[red]Invalid context type. Use: abstracts, notes, agent_notes, sections, or full_text[/red]")
                        else:
                            console.print("[yellow]Current context: " + conversation.session.context_type + "[/yellow]")
                        continue
                        
                    if user_input.startswith("/clear"):
                        logger.info("Slash command: /clear - clearing session (keeping selected papers)")
                        # Clear session but keep selected papers and context type
                        conversation.session.clear_session()
                        conversation.message_history.clear()
                        console.print("[green]Session cleared (keeping selected papers).[/green]")
                        continue
                        
                    if user_input.startswith("/help"):
                        logger.info("Slash command: /help - showing synthesis mode help")
                        show_synthesis_help()
                        continue
                    console.print("[yellow]Unknown command. Use /papers, /selected, /context, /clear, /help, or /exit[/yellow]")
                    continue
                
                # Send to conversation handler
                response = asyncio.run(conversation.handle_message(user_input))
                
                # Display response
                console.print(f"\n{response}\n")
                
            except KeyboardInterrupt:
                console.print("\n[warning]Use 'exit' to leave synthesis mode.[/warning]")
            except Exception as e:
                logger.exception("Error in synthesis mode")
                console.print(f"[error]Error: {str(e)}[/error]")
                
    finally:
        # Cleanup
        _synthesis_session = None
        if llm_client:
            try:
                asyncio.run(llm_client.close())
            except Exception:
                pass



class SynthesisCompleter(Completer):
    """Completer for synthesis mode."""
    
    def get_completions(self, document: Any, complete_event: Any) -> Any:
        """Get completions for synthesis mode."""
        text = document.text_before_cursor
        
        if text.startswith("/"):
            # Synthesis mode commands
            commands = {
                "/papers": "Show all papers in your collection",
                "/selected": "Show selected papers in current session",
                "/context": "Change context depth (abstracts, notes, agent_notes, sections, full_text)",
                "/clear": "Clear session (keeping selected papers)",
                "/help": "Show synthesis mode help",
                "/exit": "Exit synthesis mode",
            }
            
            for cmd, desc in commands.items():
                if cmd.startswith(text):
                    yield Completion(
                        cmd,
                        start_position=-len(text),
                        display=cmd,
                        display_meta=desc,
                    )
        else:
            # Suggest question starters
            if not text:
                suggestions = [
                    "What are the main findings about",
                    "How do these papers approach",
                    "Compare the methods for",
                    "What evidence supports",
                    "Go deeper on",
                ]
                for suggestion in suggestions:
                    yield Completion(
                        suggestion,
                        start_position=0,
                        display=suggestion,
                        display_meta="Question starter",
                    )




def show_examples(command: str = "") -> None:
    """Show usage examples for different commands."""
    logger.info("show_examples", command=command)

    # If a specific command is provided, show examples for that command
    if command:
        command = command.strip().lower()
        if command.startswith("/"):
            command = command[1:]  # Remove leading slash

        examples = get_command_examples()
        if command in examples:
            console.print(f"\n[bold]Examples for /{command}:[/bold]\n")
            console.print(examples[command])
        else:
            console.print(f"[red]No examples found for '{command}'[/red]")
            console.print("Use '/examples' without arguments to see all examples.")
        return

    # Show all examples
    console.print("\n[bold]Usage Examples:[/bold]\n")

    examples = get_command_examples()
    for cmd, example_text in examples.items():
        console.print(f"[bold cyan]/{cmd}[/bold cyan]")
        console.print(example_text)
        console.print()  # Add spacing between examples


def get_command_examples() -> dict[str, str]:
    """Get example usage for each command."""
    return {
        "config": """[dim]Manage LitAI configuration:[/dim]
  /config show                    [dim]# Display current configuration[/dim]
  
[dim]Display settings:[/dim]
  /config set display.list_columns title,authors,tags,notes
  /config set display.list_columns no,title,year,tldr  
  /config reset display.list_columns   [dim]# Reset to default columns[/dim]

[dim]Synthesis settings:[/dim]
  /config set synthesis.tool_approval true   [dim]# Enable tool approval prompts[/dim]
  /config set synthesis.tool_approval false  [dim]# Auto-approve all tools[/dim]

[dim]Reset configuration:[/dim]
  /config reset                   [dim]# Reset all configuration[/dim]

[dim]Available columns:[/dim]
  no, title, authors, year, citations, ai_notes, notes, tags,
  venue, abstract, tldr, doi, arxiv_id, citation_key, added_at
  
[dim]Default columns:[/dim]
  no,title,authors,year,citations,ai_notes,notes,tags,venue""",
        "find": """[dim]Search for papers on a specific topic:[/dim]
  [blue]/find attention mechanisms[/blue]
  [blue]/find transformer architecture[/blue]
  [blue]/find "deep learning optimization"[/blue]
  [blue]/find COVID-19 wastewater surveillance[/blue]""",
        "add": """[dim]Add paper(s) from search results:[/dim]
  /add            [dim]# Add all papers from search results (prompts for confirmation)[/dim]
  /add 1          [dim]# Add the first paper from search results[/dim]
  /add 3          [dim]# Add the third paper[/dim]
  /add 1,3,5      [dim]# Add multiple papers (comma-delimited)[/dim]
  
[dim]Note: You must use [blue]/find[/blue] first to get search results[/dim]""",
        "list": """[dim]List papers in your collection with pagination:[/dim]
  /list           [dim]# Shows page 1 of your collection (20 papers per page)[/dim]
  /list 2         [dim]# Shows page 2 of your collection[/dim]
  /list 5         [dim]# Shows page 5 of your collection[/dim]""",
        "remove": """[dim]Remove paper(s) from your collection:[/dim]
  /remove         [dim]# Remove all papers from your collection (prompts for confirmation)[/dim]
  /remove 1       [dim]# Remove the first paper from your collection[/dim]
  /remove 5       [dim]# Remove the fifth paper[/dim]
  /remove 1,3,5   [dim]# Remove multiple papers (comma-delimited)[/dim]
  
[dim]Note: Use /list first to see paper numbers[/dim]
[dim]You will be asked to confirm before deletion[/dim]""",
        "synthesize": """[dim]Interactive synthesis mode for collaborative paper exploration:[/dim]
  /synthesize                [dim]# Enter interactive synthesis mode[/dim]

[dim]In synthesis mode, you can:[/dim]
  • Ask questions and I'll select relevant papers
  • Refine answers by asking follow-ups
  • Say "go deeper" for more detail
  • Change context with /context <type>
  • View current papers with /papers
  • Add papers with /add <numbers>
  • Exit with 'exit' or 'done'

[dim]Example session:[/dim]
  /synthesize
  > What are the main optimization techniques?
  [I select papers and synthesize]
  > Go deeper on learning rate schedules
  [I refine with more detail]
  > /context full_text
  > Compare Adam vs SGD approaches
  [I analyze full papers]""",
        "examples": """[dim]Show examples for specific commands:[/dim]
  /examples               [dim]# Show all examples[/dim]
  /examples synthesize    [dim]# Show examples for /synthesize[/dim]
  /examples find          [dim]# Show examples for [blue]/find[/blue][/dim]""",
        "note": """[dim]Manage personal notes for papers:[/dim]
  /note 1                 [dim]# Open note for paper 1 in your editor[/dim]
  /note 1 view           [dim]# Display note in terminal[/dim]
  /note 1 append "TODO: Implement algorithm from section 3"
  /note 1 clear          [dim]# Delete note (asks for confirmation)[/dim]
  
[dim]Tips:[/dim]
  - Notes are written in Markdown format
  - Set your preferred editor with: export EDITOR=vim
  - Use /papers --notes to see all papers with notes""",
        "note": """[dim]Manage notes for a paper:[/dim]
  [cyan]/note 3[/cyan]         [dim]# View or add notes to paper 3[/dim]
  [cyan]/note 5 -r[/cyan]      [dim]# Remove notes from paper 5[/dim]
  
[dim]Output shows:[/dim]
  - Paper number and title
  - Last update timestamp
  - Preview of note content""",
        "prompt": """[dim]Manage your personal research context:[/dim]
  /prompt                [dim]# Edit your research context (opens in editor)[/dim]
  /prompt view          [dim]# Display your current research context[/dim]
  /prompt append "Also interested in hardware-aware NAS"
  /prompt clear         [dim]# Delete your research context (asks for confirmation)[/dim]
  
[dim]Your research context helps LitAI:[/dim]
  - Understand your expertise level
  - Focus on relevant aspects of papers
  - Tailor synthesis to your interests
  - Remember your preferences""",
        "tag": """[dim]Manage tags for papers in your collection:[/dim]
  /tag 1 -a ml,deep-learning    [dim]# Add tags to paper 1[/dim]
  /tag 2 -r outdated            [dim]# Remove tag from paper 2[/dim]
  /tag 3 -l                     [dim]# List tags for paper 3[/dim]
  /tag 1                        [dim]# View tags for paper 1[/dim]
  
[dim]Tips:[/dim]
  - Tags help organize your collection
  - Use /papers --tags to see all tags
  - Tags are case-insensitive and normalized""",
    }


def handle_config_command(args: str, config: Config) -> None:
    """Handle /config commands."""
    # Check for --help flag
    if args.strip() == "--help":
        show_command_help("config")
        return
    
    args_parts = args.strip().split(maxsplit=1)
    subcommand = args_parts[0] if args_parts else "show"

    if subcommand == "show":
        # Show current configuration
        config_data = config.load_config()
        if not config_data:
            console.print("\n[yellow]No configuration file found.[/yellow]")
            console.print("Using auto-detection based on environment variables.\n")

            # Show current runtime config
            try:
                temp_client = LLMClient(config)
                console.print("[bold]Current Runtime Configuration:[/bold]")
                console.print(f"  Provider: {temp_client.provider}")
                console.print(f"  Model: {temp_client.model}")
                console.print(f"  Vi Mode: {config.get_vi_mode()}")
                asyncio.run(temp_client.close())
            except Exception as e:
                console.print(f"[red]Error loading LLM client: {e}[/red]")
                console.print(f"  Vi Mode: {config.get_vi_mode()}")
        else:
            console.print("\n[bold]Current Configuration:[/bold]")
            llm_config = config_data.get("llm", {})
            console.print(f"  Provider: {llm_config.get('provider', 'auto')}")
            console.print(f"  Model: {llm_config.get('model', 'default')}")
            if llm_config.get("api_key_env"):
                console.print(f"  API Key Env: {llm_config['api_key_env']}")
            console.print(f"  Vi Mode: {config.get_vi_mode()}")
            
            # Show synthesis configuration
            synthesis_config = config_data.get("synthesis", {})
            tool_approval = synthesis_config.get("tool_approval", True)
            console.print(f"  Tool Approval: {tool_approval}")
            
            # Show list columns configuration
            display_config = config_data.get("display", {})
            list_columns = display_config.get("list_columns", "")
            if list_columns:
                console.print(f"  List Columns: {list_columns}")
            else:
                console.print("  List Columns: [dim](using defaults)[/dim]")

    elif subcommand == "set":
        # Set configuration value
        if len(args_parts) < 2:
            console.print("[red]Usage: /config set <key> <value>[/red]")
            console.print("\n[bold]LLM Configuration:[/bold]")
            console.print("  /config set llm.provider openai")
            console.print("  /config set llm.model gpt-4o-mini")
            console.print("  /config set llm.provider anthropic")
            console.print("  /config set llm.model claude-3-haiku-20240307")
            console.print("\n[bold]Editor Configuration:[/bold]")
            console.print("  /config set editor.vi_mode true")
            console.print("  /config set editor.vi_mode false")
            console.print("\n[bold]Synthesis Configuration:[/bold]")
            console.print("  /config set synthesis.tool_approval true   [dim]# Enable tool approval prompts[/dim]")
            console.print("  /config set synthesis.tool_approval false  [dim]# Auto-approve all tools[/dim]")
            console.print("\n[bold]Display Configuration:[/bold]")
            console.print("  /config set display.list_columns no,title,authors,year,venue")
            console.print("  /config set display.list_columns title,tldr,tags,notes")
            console.print("\n[cyan]Available columns for list_columns:[/cyan]")
            console.print("  • [bold]no[/bold] - Paper number")
            console.print("  • [bold]title[/bold] - Paper title")
            console.print("  • [bold]authors[/bold] - Author names")
            console.print("  • [bold]year[/bold] - Publication year")
            console.print("  • [bold]citations[/bold] - Citation count")
            console.print("  • [bold]ai_notes[/bold] - Whether paper has AI-generated notes (✓)")
            console.print("  • [bold]notes[/bold] - Whether paper has user notes (✓)")
            console.print("  • [bold]tags[/bold] - Paper tags")
            console.print("  • [bold]venue[/bold] - Publication venue")
            console.print("  • [bold]abstract[/bold] - Paper abstract (truncated)")
            console.print("  • [bold]tldr[/bold] - TL;DR summary")
            console.print("  • [bold]doi[/bold] - DOI identifier")
            console.print("  • [bold]arxiv_id[/bold] - ArXiv ID")
            console.print("  • [bold]citation_key[/bold] - BibTeX citation key")
            console.print("  • [bold]added_at[/bold] - Date added to collection")
            console.print("\n[dim]Default columns: no,title,authors,year,citations,ai_notes,notes,tags,venue[/dim]")
            console.print("[dim]Reset to default: /config reset display.list_columns[/dim]")
            return

        key_value = args_parts[1].split(maxsplit=1)
        if len(key_value) != 2:
            console.print("[red]Usage: /config set <key> <value>[/red]")
            return

        key, value = key_value

        # Validate key
        if not (
            key.startswith("llm.")
            or key.startswith("editor.")
            or key.startswith("display.")
            or key.startswith("synthesis.")
        ):
            console.print(f"[red]Invalid configuration key: {key}[/red]")
            console.print(
                "Supported keys: llm.provider, llm.model, llm.api_key_env, editor.vi_mode, display.list_columns, synthesis.tool_approval",
            )
            return

        # Validate provider
        if key == "llm.provider" and value not in ["openai", "anthropic", "auto"]:
            console.print(f"[red]Invalid provider: {value}[/red]")
            console.print("Supported providers: openai, anthropic, auto")
            return

        # Validate and convert boolean values
        config_value: Any = value
        if key in ["editor.vi_mode", "synthesis.tool_approval"]:
            if value.lower() in ["true", "yes", "1", "on"]:
                config_value = True
            elif value.lower() in ["false", "no", "0", "off"]:
                config_value = False
            else:
                console.print(f"[red]Invalid boolean value: {value}[/red]")
                console.print("Use: true, false, yes, no, 1, 0, on, or off")
                return

        # Update configuration
        config.update_config(key, config_value)
        console.print(f"[green]Configuration updated: {key} = {value}[/green]")
        console.print(
            "\n[yellow]Note: Restart LitAI for changes to take effect.[/yellow]",
        )

    elif subcommand == "reset":
        # Reset configuration - either all or specific key
        if len(args_parts) > 1:
            # Reset specific key
            key = args_parts[1].strip()
            
            # Define defaults for resettable keys
            defaults = {
                "display.list_columns": "no,title,authors,year,citations,ai_notes,notes,tags,venue",
            }
            
            if key in defaults:
                config.update_config(key, defaults[key])
                console.print(f"[green]Reset {key} to default: {defaults[key]}[/green]")
            elif key in ["llm.provider", "llm.model", "llm.api_key_env", "editor.vi_mode"]:
                # Remove these keys to use auto-detection/defaults
                config_data = config.load_config()
                if config_data:
                    keys = key.split(".")
                    if len(keys) == 2 and keys[0] in config_data and keys[1] in config_data[keys[0]]:
                        del config_data[keys[0]][keys[1]]
                        if not config_data[keys[0]]:  # Remove empty section
                            del config_data[keys[0]]
                        config.config_path.write_text(json.dumps(config_data, indent=2))
                        console.print(f"[green]Reset {key} to default[/green]")
                    else:
                        console.print(f"[yellow]Key {key} not currently set[/yellow]")
                else:
                    console.print("[yellow]No configuration to reset[/yellow]")
            else:
                console.print(f"[red]Unknown configuration key: {key}[/red]")
                console.print("Resettable keys: llm.provider, llm.model, editor.vi_mode, display.list_columns")
        else:
            # Reset entire configuration
            config_path = config.config_path
            if config_path.exists():
                console.print("[yellow]This will reset ALL configuration settings to defaults.[/yellow]")
                confirm = console.input("[yellow]Type 'yes' to confirm: [/yellow]")
                if confirm.lower() != "yes":
                    console.print("[red]Cancelled[/red]")
                    return
                
                config_path.unlink()
                console.print("[green]Configuration reset to defaults.[/green]")
                console.print("Will use auto-detection based on environment variables.")
            else:
                console.print("[yellow]No configuration file to reset.[/yellow]")

    else:
        console.print(f"[red]Unknown config subcommand: {subcommand}[/red]")
        console.print("Available subcommands:")
        console.print("  [cyan]show[/cyan] - Display current configuration")
        console.print("  [cyan]set <key> <value>[/cyan] - Set a configuration value")
        console.print("  [cyan]reset [key][/cyan] - Reset all config or specific key to default")
        console.print("\nExamples:")
        console.print("  /config show")
        console.print("  /config set display.list_columns title,authors,tags")
        console.print("  /config reset display.list_columns")
        console.print("  /config reset  [dim]# Reset all configuration[/dim]")


def handle_prompt_command(args: str, config: Config) -> None:
    """Handle /prompt commands for managing user research context."""
    # Check for --help flag
    if args.strip() == "--help":
        show_command_help("prompt")
        return
    
    args_parts = args.strip().split(maxsplit=1)
    subcommand = args_parts[0] if args_parts else "edit"

    if subcommand == "edit":
        edit_user_prompt(config)
    elif subcommand == "view":
        view_user_prompt(config)
    elif subcommand == "append":
        if len(args_parts) < 2:
            console.print("[red]Usage: /prompt append <text>[/red]")
            return
        append_to_user_prompt(args_parts[1], config)
    elif subcommand == "clear":
        clear_user_prompt(config)
    else:
        console.print(f"[red]Unknown subcommand: {subcommand}[/red]")
        console.print("Available subcommands: edit, view, append, clear")


def edit_user_prompt(config: Config) -> None:
    """Open user prompt in external editor."""
    import os
    import shutil
    import subprocess
    import tempfile

    logger.info("edit_user_prompt_start")

    # Get existing prompt
    prompt_path = config.user_prompt_path
    existing_prompt = ""
    if prompt_path.exists():
        try:
            existing_prompt = prompt_path.read_text().strip()
            logger.info("edit_user_prompt_existing", length=len(existing_prompt))
        except Exception as e:
            logger.error("edit_user_prompt_read_error", error=str(e))
            output.error(f"Failed to read existing prompt: {e}")
            return

    # Create temp file with content
    with tempfile.NamedTemporaryFile(
        mode="w", suffix="_user_prompt.md", prefix="litai_", delete=False,
    ) as tmp:
        # Write header and template/existing content
        tmp.write("# LitAI User Prompt\n")
        tmp.write("<!-- This prompt will be added to every conversation -->\n\n")

        if existing_prompt:
            tmp.write(existing_prompt)
        else:
            # Provide template
            tmp.write("## Research Context\n")
            tmp.write("<!-- Describe your research area and current focus -->\n\n")
            tmp.write("## Background & Expertise\n")
            tmp.write(
                "<!-- Your academic/professional background relevant to your research -->\n\n",
            )
            tmp.write("## Specific Interests\n")
            tmp.write(
                "<!-- Particular topics, methods, or problems you're investigating -->\n\n",
            )
            tmp.write("## Preferences\n")
            tmp.write(
                "<!-- How you prefer information to be presented or synthesized -->\n",
            )

        tmp_path = tmp.name

    # Determine editor
    editor = os.environ.get("EDITOR", "nano")
    if shutil.which(editor) is None:
        # Fallback editors
        for fallback in ["vim", "vi", "emacs", "pico"]:
            if shutil.which(fallback):
                editor = fallback
                break
        else:
            # No editor found
            os.unlink(tmp_path)
            logger.error("edit_user_prompt_no_editor")
            output.error(
                "No text editor found. Please set $EDITOR environment variable.",
            )
            return

    logger.info("edit_user_prompt_editor", editor=editor)

    # Open editor
    try:
        result = subprocess.run([editor, tmp_path], check=True)
        logger.info("edit_user_prompt_editor_closed", return_code=result.returncode)
    except subprocess.CalledProcessError as e:
        os.unlink(tmp_path)
        logger.error("edit_user_prompt_editor_error", error=str(e))
        output.error(f"Editor exited with error: {e}")
        return
    except Exception as e:
        os.unlink(tmp_path)
        logger.error("edit_user_prompt_unexpected_error", error=str(e))
        output.error(f"Unexpected error: {e}")
        return

    # Read back the content
    try:
        with open(tmp_path) as f:
            new_content = f.read()

        # Remove header lines
        lines = new_content.split("\n")
        content_lines = []
        skip_next = False
        for line in lines:
            if line.startswith("# LitAI User Prompt"):
                skip_next = True
                continue
            if skip_next and line.startswith("<!--"):
                skip_next = False
                continue
            content_lines.append(line)

        # Join and clean up
        final_content = "\n".join(content_lines).strip()

        if final_content:
            # Save to file
            prompt_path.write_text(final_content)
            logger.info("edit_user_prompt_saved", length=len(final_content))
            console.print("[green]✓ User prompt saved successfully[/green]")
        else:
            logger.info("edit_user_prompt_empty")
            console.print("[yellow]No content saved (file was empty)[/yellow]")

    except Exception as e:
        logger.error("edit_user_prompt_save_error", error=str(e))
        output.error(f"Failed to save prompt: {e}")
    finally:
        # Clean up temp file
        os.unlink(tmp_path)


def view_user_prompt(config: Config) -> None:
    """Display current user prompt."""
    logger.info("view_user_prompt_start")

    prompt_path = config.user_prompt_path
    if not prompt_path.exists():
        console.print(
            "[info]No user prompt set. Use /prompt edit to create one.[/info]",
        )
        return

    try:
        content = prompt_path.read_text().strip()
        if not content:
            console.print("[info]User prompt file is empty.[/info]")
            return

        output.section("Your Research Context", "📝", "bold blue")
        console.print(content)
        console.print("\n[dim]Use /prompt edit to modify[/dim]")

    except Exception as e:
        logger.error("view_user_prompt_error", error=str(e))
        output.error(f"Failed to read user prompt: {e}")


def append_to_user_prompt(text: str, config: Config) -> None:
    """Append text to existing user prompt."""
    logger.info("append_to_user_prompt_start", text_length=len(text))

    prompt_path = config.user_prompt_path

    try:
        # Read existing content
        existing = ""
        if prompt_path.exists():
            existing = prompt_path.read_text()

        # Append new text
        if existing and not existing.endswith("\n"):
            existing += "\n"

        new_content = existing + text + "\n"
        prompt_path.write_text(new_content)

        logger.info("append_to_user_prompt_success")
        console.print("[green]✓ Text appended to user prompt[/green]")

    except Exception as e:
        logger.error("append_to_user_prompt_error", error=str(e))
        output.error(f"Failed to append to prompt: {e}")


def clear_user_prompt(config: Config) -> None:
    """Delete user prompt file."""
    logger.info("clear_user_prompt_start")

    prompt_path = config.user_prompt_path
    if not prompt_path.exists():
        console.print("[info]No user prompt to clear.[/info]")
        return

    # Confirm deletion
    console.print("[yellow]This will permanently delete your user prompt.[/yellow]")
    confirm = console.input("[yellow]Type 'yes' to confirm: [/yellow]")

    if confirm.lower() != "yes":
        console.print("[red]Cancelled[/red]")
        return

    try:
        prompt_path.unlink()
        logger.info("clear_user_prompt_success")
        console.print("[green]✓ User prompt cleared[/green]")
    except Exception as e:
        logger.error("clear_user_prompt_error", error=str(e))
        output.error(f"Failed to clear prompt: {e}")


def show_help() -> None:
    """Display a quick reference of all available commands."""
    logger.info("show_help")

    console.print("\n[bold]Available Commands:[/bold]\n")
    
    # Core commands
    console.print("[bold cyan]Paper Discovery:[/bold cyan]")
    console.print("  [blue]/find[/blue]        Search for papers")
    console.print("  [blue]/papers[/blue]      List papers in collection")
    console.print()
    
    console.print("[bold cyan]Collection Management:[/bold cyan]")
    console.print("  [green]/add[/green]         Add papers from search")
    console.print("  [red]/remove[/red]      Remove papers from collection")
    console.print("  [yellow]/note[/yellow]        Add notes to papers")
    console.print("  [magenta]/tag[/magenta]         Tag papers")
    console.print("  [dim]/import[/dim]      Import from BibTeX")
    console.print()
    
    console.print("[bold cyan]Analysis:[/bold cyan]")
    console.print("  [blue]/synthesize[/blue]  Interactive synthesis mode")
    console.print("  [blue]/questions[/blue]   Research unblocking prompts")
    console.print(
)
    
    console.print("[bold cyan]System:[/bold cyan]")
    console.print("  [dim]/prompt[/dim]      Manage research context")
    console.print("  [dim]/config[/dim]      LLM configuration")  
    console.print("  [dim]/clear[/dim]       Clear console")
    console.print("  [dim]/exit[/dim]        Exit LitAI")
    console.print()
    
    console.print("[dim]💡 Type any command with [bold]--help[/bold] for detailed usage and examples[/dim]")
    console.print("[dim]   Example: [italic]/find --help[/italic][/dim]\n")


def show_command_help(command: str) -> None:
    """Display help information for a specific command."""
    logger.info("show_command_help", command=command)
    
    # Get command examples
    examples = get_command_examples()
    
    # Special case for commands with custom help formatting
    if command == "find":
        show_find_help()
        return
    if command == "papers":
        show_papers_help()
        return
    
    # Generic help display for other commands
    if command in examples:
        console.print(f"\n[bold]/{command} Command Usage[/bold]\n")
        console.print(examples[command])
        console.print()
    else:
        console.print(f"\n[yellow]No help available for /{command}[/yellow]\n")


def show_find_help() -> None:
    """Display help information for the /find command."""
    logger.info("show_find_help")
    
    console.print("\n[bold]/find Command Usage[/bold]\n")
    
    console.print("[blue]/find <query>[/blue] — Search for papers on Semantic Scholar")
    console.print("[blue]/find --recent[/blue] — Show cached results from last search")
    console.print("[blue]/find --help[/blue] — Show this help message\n")
    
    console.print("[bold]Examples:[/bold]")
    console.print("  [dim]/find attention mechanisms[/dim]")
    console.print("  [dim]/find transformer architecture[/dim]")
    console.print("  [dim]/find \"deep learning optimization\"[/dim]")
    console.print("  [dim]/find COVID-19 wastewater surveillance[/dim]\n")
    
    console.print("[bold]Tips:[/bold]")
    console.print("  • Use quotes for exact phrases: /find \"exact phrase\"")
    console.print("  • After searching, use /add <number> to add papers to your collection")
    console.print("  • Use /find --recent to view your last search results again\n")


def show_synthesis_help() -> None:
    """Display help information for synthesis mode commands."""
    logger.info("show_synthesis_help")
    
    console.print("\n[bold cyan]◈ Synthesis Mode Commands[/bold cyan]\n")
    
    console.print("[bold]Slash Commands:[/bold]")
    console.print("  [blue]/papers[/blue]      List all papers in your collection")
    console.print("  [blue]/selected[/blue]    Show papers selected in current session")
    console.print("  [blue]/context[/blue]     Change context depth (abstracts, notes, agent_notes, sections, full_text)")
    console.print("  [blue]/clear[/blue]       Clear session (keeping selected papers)")
    console.print("  [blue]/help[/blue]        Show this help")
    console.print("  [blue]/exit[/blue]        Exit synthesis mode\n")
    
    console.print("[bold]Natural Language Commands:[/bold]")
    console.print("  Just ask questions naturally! Examples:")
    console.print("  • \"What are the main findings about attention mechanisms?\"")
    console.print("  • \"How do these papers approach optimization?\"")
    console.print("  • \"Compare the methods across my papers\"")
    console.print("  • \"Go deeper on the evaluation metrics\"\n")
    
    console.print("[bold]Context Depths:[/bold]")
    console.print("  [green]abstracts[/green]     Quick overview from paper abstracts")
    console.print("  [green]notes[/green]         Your personal notes on papers")
    console.print("  [green]agent_notes[/green]   AI-generated insights about papers")
    console.print("  [green]sections[/green]      Specific sections from papers")
    console.print("  [green]full_text[/green]     Complete paper content (slower)\n")
    
    console.print("[bold]Workflow Tips:[/bold]")
    console.print("  1. Ask a question - I'll find relevant papers automatically")
    console.print("  2. Say \"go deeper\" for more detailed analysis")
    console.print("  3. Use /context to change detail level")
    console.print("  4. Build on previous answers with follow-up questions")
    console.print("  5. Use /selected to see which papers I'm working with\n")


def show_research_questions() -> None:
    """Display research unblocking questions that users can ask with LitAI."""
    logger.info("show_research_questions")

    console.print("\n[bold heading]RESEARCH UNBLOCKING QUESTIONS[/bold heading]")
    console.print("[dim_text]Learn to ask better synthesis questions[/dim_text]\n")

    # Experimental Troubleshooting
    output.section("Debugging Experiments", "🔧", "bold cyan")
    console.print("• Why does this baseline perform differently than reported?")
    console.print("• What hyperparameters do papers actually use vs report?")
    console.print('• Which "standard" preprocessing steps vary wildly across papers?')
    console.print("• What's the actual variance in this metric across the literature?")
    console.print("• Do others see this instability/artifact? How do they handle it?\n")

    # Methods & Analysis
    output.section("Methods & Analysis", "📊", "bold cyan")
    console.print("• What statistical tests does this subfield actually use/trust?")
    console.print("• How do people typically visualize this type of data?")
    console.print("• What's the standard ablation set for this method?")
    console.print("• Which evaluation metrics correlate with downstream performance?")
    console.print("• What dataset splits/versions are people actually using?\n")

    # Contextualizing Results
    output.section("Contextualizing Results", "📈", "bold cyan")
    console.print("• Is my improvement within noise bounds of prior work?")
    console.print("• What explains the gap between my results and theirs?")
    console.print("• Which prior results are suspicious outliers?")
    console.print("• Have others tried and failed at this approach?")
    console.print(
        "• What's the real SOTA when you account for compute/data differences?\n",
    )

    # Technical Details
    output.section("Technical Details", "🎯", "bold cyan")
    console.print("• What batch size/learning rate scaling laws apply here?")
    console.print("• Which optimizer quirks matter for this problem?")
    console.print("• What numerical precision issues arise at this scale?")
    console.print("• How long do people actually train these models?")
    console.print("• What early stopping criteria work in practice?\n")

    # Common Research Questions
    output.section("Common Research Questions", "🔍", "bold cyan")
    console.print("• Has someone done this research already?")
    console.print("• What methods do other people use to analyze this problem?")
    console.print("• What are typical issues people run into?")
    console.print("• How do people typically do these analyses?")
    console.print("• Is our result consistent or contradictory with the literature?")
    console.print("• What are known open problems in the field?")
    console.print("• Any key papers I forgot to cite?\n")


async def handle_note_command(args: str, db: Database) -> None:
    """Handle /note command for managing user notes."""
    logger.info("handle_note_command_start", args=args)
    
    # Check for --help flag
    if args.strip() == "--help":
        show_command_help("note")
        return

    parts = args.strip().split(maxsplit=2)

    if not args.strip():
        logger.warning("handle_note_command_no_args")
        output.error("Usage: /note <paper_number> [view|append|clear]")
        console.print("[dim]Examples:[/dim]")
        console.print("  /note 1         # Edit note for paper 1")
        console.print("  /note 1 view    # View note for paper 1")
        console.print('  /note 1 append "Additional thoughts"')
        console.print("  /note 1 clear   # Delete note for paper 1")
        return

    # Parse paper number
    try:
        paper_num = int(parts[0])
        papers = db.list_papers()
        if paper_num < 1 or paper_num > len(papers):
            logger.warning(
                "handle_note_command_invalid_number",
                paper_num=paper_num,
                max_num=len(papers),
            )
            output.error(f"Invalid paper number. Choose 1-{len(papers)}")
            return
        paper = papers[paper_num - 1]
        logger.info(
            "handle_note_command_paper_selected",
            paper_num=paper_num,
            paper_id=paper.paper_id,
        )
    except ValueError:
        logger.warning("handle_note_command_parse_error", input=parts[0])
        output.error("Invalid paper number")
        return

    # Determine action
    action = parts[1].lower() if len(parts) > 1 else "edit"
    logger.info("handle_note_command_action", action=action)

    # Validate action
    valid_actions = ["edit", "view", "append", "clear"]
    if action not in valid_actions:
        logger.warning("handle_note_command_invalid_action", action=action)
        output.error(f"Invalid action: '{action}'. Valid actions: view, append, clear")
        return

    if action == "edit":
        await edit_note(paper, db)
    elif action == "view":
        view_note(paper, db)
    elif action == "append":
        if len(parts) < 3:
            logger.warning("handle_note_command_append_no_text")
            output.error("Usage: /note <number> append <text>")
            return
        append_to_note(paper, parts[2], db)
    elif action == "clear":
        clear_note(paper, db)


async def edit_note(paper: Paper, db: Database) -> None:
    """Open note in external editor."""
    import os
    import shutil
    import subprocess
    import tempfile

    logger.info("edit_note_start", paper_id=paper.paper_id, title=paper.title)

    # Get existing note
    existing_note = db.get_note(paper.paper_id) or ""
    logger.info(
        "edit_note_existing",
        has_existing=bool(existing_note),
        length=len(existing_note),
    )

    # Create temp file with content
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=f"_{paper.paper_id}.md", prefix="litai_note_", delete=False,
    ) as tmp:
        # Write header and existing content
        tmp.write(f"# Notes: {paper.title}\n")
        tmp.write(f"<!-- Paper: {paper.paper_id} -->\n")
        tmp.write("<!-- Do not edit the above lines -->\n\n")

        if existing_note:
            tmp.write(existing_note)
        else:
            # Provide template
            tmp.write("## Key Insights\n\n")
            tmp.write("## Questions\n\n")
            tmp.write("## Implementation Ideas\n\n")
            tmp.write("## Related Work\n\n")

        tmp_path = tmp.name

    try:
        # Determine editor
        editor = os.environ.get("EDITOR", "vim")
        logger.info(
            "edit_note_editor_check",
            editor=editor,
            from_env=bool(os.environ.get("EDITOR")),
        )

        if not shutil.which(editor):
            # Try fallbacks
            for fallback in ["nano", "vi"]:
                if shutil.which(fallback):
                    editor = fallback
                    logger.info("edit_note_editor_fallback", editor=editor)
                    break
            else:
                logger.error("edit_note_no_editor")
                output.error("No text editor found. Set $EDITOR environment variable.")
                return

        # Open editor
        console.print(f"[info]Opening note in {editor}...[/info]")
        subprocess.run([editor, tmp_path], check=True)

        # Read updated content
        with open(tmp_path) as f:
            content = f.read()

        # Remove header lines
        lines = content.split("\n")
        content_start = 0
        for i, line in enumerate(lines):
            if line.strip() == "<!-- Do not edit the above lines -->":
                content_start = i + 1
                break

        final_content = "\n".join(lines[content_start:]).strip()

        # Save to database
        if final_content:
            success = db.add_note(paper.paper_id, final_content)
            logger.info(
                "edit_note_saved",
                paper_id=paper.paper_id,
                length=len(final_content),
                success=success,
            )
            output.success(f"Notes saved for '{paper.title}'")
        else:
            logger.info("edit_note_empty", paper_id=paper.paper_id)
            console.print("[warning]Empty note not saved[/warning]")

    except subprocess.CalledProcessError as e:
        logger.error("edit_note_editor_error", paper_id=paper.paper_id, error=str(e))
        output.error("Editor closed with error")
    except Exception as e:
        logger.exception("edit_note_failed", paper_id=paper.paper_id)
        output.error(f"Failed to edit note: {e}")
    finally:
        # Cleanup
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


def view_note(paper: Paper, db: Database) -> None:
    """Display note in terminal."""
    logger.info("view_note_start", paper_id=paper.paper_id, title=paper.title)

    note = db.get_note(paper.paper_id)
    if not note:
        logger.info("view_note_not_found", paper_id=paper.paper_id)
        console.print(f"[warning]No notes found for '{paper.title}'[/warning]")
        return

    logger.info("view_note_found", paper_id=paper.paper_id, length=len(note))

    output.section(f"Notes: {paper.title}", "📝", "bold blue")
    from rich.markdown import Markdown

    console.print(Markdown(note))


def append_to_note(paper: Paper, text: str, db: Database) -> None:
    """Append text to an existing note."""
    logger.info("append_note_start", paper_id=paper.paper_id, text_length=len(text))

    existing_note = db.get_note(paper.paper_id) or ""

    # Add newlines if the existing note doesn't end with them
    if existing_note and not existing_note.endswith("\n"):
        existing_note += "\n\n"

    new_content = existing_note + text
    success = db.add_note(paper.paper_id, new_content)
    logger.info(
        "append_note_complete",
        paper_id=paper.paper_id,
        new_length=len(new_content),
        success=success,
    )
    output.success(f"Text appended to notes for '{paper.title}'")


def clear_note(paper: Paper, db: Database) -> None:
    """Delete note with confirmation."""
    logger.info("clear_note_start", paper_id=paper.paper_id)

    if not db.get_note(paper.paper_id):
        logger.info("clear_note_not_found", paper_id=paper.paper_id)
        console.print(f"[warning]No notes found for '{paper.title}'[/warning]")
        return

    confirm = Prompt.ask(
        f"[warning]Are you sure you want to delete notes for '{paper.title}'?[/warning]",
        choices=["yes", "no"],
        default="no",
    )

    if confirm == "yes":
        success = db.delete_note(paper.paper_id)
        logger.info("clear_note_result", paper_id=paper.paper_id, success=success)
        if success:
            output.success(f"Notes deleted for '{paper.title}'")
        else:
            output.error("Failed to delete notes")
    else:
        logger.info("clear_note_cancelled", paper_id=paper.paper_id)


def list_papers_with_notes(db: Database) -> None:
    """List all papers that have notes attached."""
    logger.info("list_notes_start")

    papers_with_notes = db.list_papers_with_notes()
    logger.info("list_notes_found", count=len(papers_with_notes))

    if not papers_with_notes:
        console.print(
            "[info]No papers have notes yet. Use /note <paper_number> to add notes.[/info]",
        )
        return

    output.section(
        f"Papers with Notes ({len(papers_with_notes)} total)", "📚", "bold blue",
    )

    # Get full paper list to find paper numbers
    all_papers = db.list_papers()
    paper_id_to_num = {p.paper_id: i + 1 for i, p in enumerate(all_papers)}

    for paper, preview, updated_at in papers_with_notes:
        paper_num = paper_id_to_num.get(paper.paper_id, "?")
        console.print(
            f"\n[number]{paper_num}[/number]. [primary]{paper.title}[/primary] ({paper.year})",
        )
        console.print(
            f"   [dim_text]Last updated: {updated_at.strftime('%Y-%m-%d %H:%M')}[/dim_text]",
        )
        console.print(f"   [italic]Preview: {preview}[/italic]")

def list_papers_with_agent_notes(db: Database) -> None:
    """List all papers that have agent notes attached."""
    logger.info("list_agent_notes_start")

    papers_with_notes = db.list_papers_with_agent_notes()
    logger.info("list_agent_notes_found", count=len(papers_with_notes))

    if not papers_with_notes:
        console.print(
            "[info]No papers have agent notes yet. Agent notes are created during synthesis mode.[/info]",
        )
        return

    output.section(
        f"Papers with Agent Notes ({len(papers_with_notes)} total)", "🤖", "bold cyan",
    )

    # Get full paper list to find paper numbers
    all_papers = db.list_papers()
    paper_id_to_num = {p.paper_id: i + 1 for i, p in enumerate(all_papers)}

    for paper, preview, updated_at in papers_with_notes:
        paper_num = paper_id_to_num.get(paper.paper_id, "?")
        console.print(
            f"\n[number]{paper_num}[/number]. [primary]{paper.title}[/primary] ({paper.year})",
        )
        console.print(
            f"   [dim_text]Last updated: {updated_at.strftime('%Y-%m-%d %H:%M')}[/dim_text]",
        )
        console.print(f"   [italic]Preview: {preview}[/italic]")

async def handle_agent_note_command(args: str, db: Database) -> None:
    """Handle /agent-note command for viewing agent-generated notes."""
    
    parts = args.strip().split(maxsplit=1)
    
    if not parts:
        # List all papers with agent notes
        list_papers_with_agent_notes(db)
        return
    
    # Handle clear-all command
    if parts[0] == "clear-all":
        # Clear all agent notes with confirmation
        console.print(
            "[yellow]This will clear ALL agent notes for ALL papers.[/yellow]",
        )
        confirm = console.input("[yellow]Type 'yes' to confirm: [/yellow]")
        if confirm.lower() != "yes":
            console.print("[red]Cancelled[/red]")
            return
        
        count = db.clear_all_agent_notes()
        output.success(f"Cleared agent notes from {count} papers")
        return
    
    # Parse paper number
    try:
        paper_num = int(parts[0])
        papers = db.list_papers()
        if paper_num < 1 or paper_num > len(papers):
            logger.warning(
                "handle_note_command_invalid_number",
                paper_num=paper_num,
                max_num=len(papers),
            )
            output.error(f"Invalid paper number. Choose 1-{len(papers)}")
            return
        paper = papers[paper_num - 1]
        logger.info(
            "handle_note_command_paper_selected",
            paper_num=paper_num,
            paper_id=paper.paper_id,
        )
    except ValueError:
        logger.warning("handle_note_command_parse_error", input=parts[0])
        output.error("Invalid paper number")
        return
    
    # Determine action
    action = parts[1].lower() if len(parts) > 1 else "view"
    logger.info("handle_agent_note_command_action", action=action)

    # Validate action
    valid_actions = ["view", "clear"]
    if action not in valid_actions:
        logger.warning("handle_agent_note_command_invalid_action", action=action)
        output.error(f"Invalid action: '{action}'. Valid actions: view, clear")
        return

    if action == "view":
        view_agent_note(paper, db)
    elif action == "clear":
        # Clear agent notes for this paper
        console.print(
            f"[yellow]Clear agent notes for '{paper.title}'?[/yellow]",
        )
        confirm = console.input("[yellow]Type 'yes' to confirm: [/yellow]")
        if confirm.lower() != "yes":
            console.print("[red]Cancelled[/red]")
            return
        
        success = db.clear_agent_notes(paper.paper_id)
        if success:
            output.success(f"Cleared agent notes for '{paper.title}'")
        else:
            output.error(f"No agent notes found for '{paper.title}'")


def view_agent_note(paper: Paper, db: Database) -> None:
    """Display agent note in terminal."""
    logger.info("view_agent_note_start", paper_id=paper.paper_id, title=paper.title)

    note = db.get_agent_note(paper.paper_id)
    if not note:
        logger.info("view_agent_note_not_found", paper_id=paper.paper_id)
        console.print(f"[warning]No agent notes found for '{paper.title}'[/warning]")
        return

    logger.info("view_agent_note_found", paper_id=paper.paper_id, length=len(note))

    output.section(f"Agent Notes: {paper.title}", "🤖", "bold cyan")
    from rich.markdown import Markdown

    console.print(Markdown(note))


def handle_tag_command(args: str, db: Database) -> None:
    """Handle tag management for a paper."""
    # Check for --help flag
    if args.strip() == "--help":
        show_command_help("tag")
        return
    
    parts = args.split(maxsplit=1)
    if not parts:
        output.error(
            "Please provide a paper number. Usage: /tag <paper_number> [-a|-r|-l tags]",
        )
        return

    try:
        paper_num = int(parts[0])
    except ValueError:
        output.error("Invalid paper number. Usage: /tag <paper_number> [-a|-r|-l tags]")
        return

    # Get the paper
    papers = db.list_papers(limit=100)
    if paper_num < 1 or paper_num > len(papers):
        output.error(f"Invalid paper number. Please choose between 1 and {len(papers)}")
        return

    paper = papers[paper_num - 1]
    current_tags = db.get_paper_tags(paper.paper_id)

    # Parse the command options
    if len(parts) == 1:
        # No options provided, show current tags
        if current_tags:
            output.section(f"Tags for paper #{paper_num}", "🏷️", "bold cyan")
            console.print(f"[primary]{paper.title}[/primary]\n")
            console.print("Current tags: " + output.format_tags(current_tags))
            console.print(
                "\n[dim]Use -a to add tags, -r to remove tags, -l to list tags[/dim]",
            )
        else:
            console.print(f"[info]No tags for paper #{paper_num}: {paper.title}[/info]")
            console.print("[dim]Use /tag <number> -a <tags> to add tags[/dim]")
        return

    # Parse the action and tags
    action_and_tags = parts[1].strip()
    if action_and_tags.startswith("-a "):
        # Add tags
        tag_str = action_and_tags[3:].strip()
        if not tag_str:
            output.error(
                "Please provide tags to add. Usage: /tag <number> -a tag1,tag2",
            )
            return

        new_tags = [t.strip() for t in tag_str.split(",") if t.strip()]
        db.add_tags_to_paper(paper.paper_id, new_tags)

        output.success(f"Added {len(new_tags)} tag(s) to paper #{paper_num}")
        updated_tags = db.get_paper_tags(paper.paper_id)
        console.print("Updated tags: " + output.format_tags(updated_tags))

    elif action_and_tags.startswith("-r "):
        # Remove tags
        tag_str = action_and_tags[3:].strip()
        if not tag_str:
            output.error(
                "Please provide tags to remove. Usage: /tag <number> -r tag1,tag2",
            )
            return

        tags_to_remove = [t.strip() for t in tag_str.split(",") if t.strip()]
        removed_count = 0
        for tag in tags_to_remove:
            if db.remove_tag_from_paper(paper.paper_id, tag):
                removed_count += 1

        if removed_count > 0:
            output.success(f"Removed {removed_count} tag(s) from paper #{paper_num}")
            updated_tags = db.get_paper_tags(paper.paper_id)
            if updated_tags:
                console.print("Remaining tags: " + output.format_tags(updated_tags))
            else:
                console.print("[dim]Paper now has no tags[/dim]")
        else:
            output.error("No matching tags found to remove")

    elif action_and_tags == "-l":
        # List all current tags
        if current_tags:
            output.section(f"Tags for paper #{paper_num}", "🏷️", "bold cyan")
            console.print(f"[primary]{paper.title}[/primary]\n")
            for tag in sorted(current_tags):
                console.print(f"  {output.format_tag(tag)}")
        else:
            console.print(f"[info]No tags for paper #{paper_num}[/info]")
    else:
        output.error(
            "Invalid option. Use -a to add tags, -r to remove tags, or -l to list tags",
        )


def list_tags(db: Database) -> None:
    """List all tags in the database with paper counts."""
    tags_with_counts = db.list_all_tags()

    if not tags_with_counts:
        console.print(
            "[info]No tags in the database yet. Use /tag <number> -a <tags> to add tags to papers.[/info]",
        )
        return

    output.section(f"All Tags ({len(tags_with_counts)} total)", "🏷️", "bold cyan")

    # Create a table for tags
    table = Table(show_header=True)
    table.add_column("Tag", style="cyan")
    table.add_column("Papers", style="number", justify="right")
    table.add_column("Created", style="dim_text")

    for tag, count in tags_with_counts:
        table.add_row(
            output.format_tag(tag.name), str(count), tag.created_at.strftime("%Y-%m-%d"),
        )

    console.print(table)
    console.print(
        "\n[dim]Use /papers --tag <tag_name> to see papers with a specific tag[/dim]",
    )


def handle_import_command(args: str, db: Database, config: Config | None) -> None:
    """Handle BibTeX import command."""
    from pathlib import Path

    from litai.importers.bibtex import parse_bibtex_file

    if not args:
        output.error(
            "Please provide a BibTeX file path. Usage: /import <path/to/file.bib> [--dry-run]",
        )
        return

    # Parse arguments
    parts = args.split()
    file_path = Path(parts[0]).expanduser()
    dry_run = "--dry-run" in parts

    # Check if file exists
    if not file_path.exists():
        output.error(f"File not found: {file_path}")
        return

    if file_path.suffix.lower() not in [".bib", ".bibtex"]:
        output.error("File must have .bib or .bibtex extension")
        return

    try:
        # Parse the BibTeX file
        output.section("Importing BibTeX", "📚", "bold cyan")
        console.print(f"[info]Parsing {file_path}...[/info]")

        papers = parse_bibtex_file(file_path)

        if not papers:
            output.error("No valid entries found in BibTeX file")
            return

        console.print(f"[success]Found {len(papers)} valid entries[/success]")

        if dry_run:
            console.print("\n[warning]DRY RUN - No changes will be made[/warning]\n")

        # Process each paper
        imported = 0
        skipped = 0

        for i, paper in enumerate(papers, 1):
            # Check if paper already exists
            existing = None

            # Check by paper_id
            existing = db.get_paper(paper.paper_id)

            # Check by DOI if we have one
            if not existing and paper.doi:
                papers_with_doi = db.list_papers(limit=1000)
                for p in papers_with_doi:
                    if p.doi == paper.doi:
                        existing = p
                        break

            # Check by arXiv ID if we have one
            if not existing and paper.arxiv_id:
                papers_with_arxiv = db.list_papers(limit=1000)
                for p in papers_with_arxiv:
                    if p.arxiv_id == paper.arxiv_id:
                        existing = p
                        break

            if existing:
                skipped += 1
                if existing.citation_key != paper.citation_key and paper.citation_key:
                    # Update citation key if different
                    if not dry_run:
                        # TODO: Add update_paper_citation_key method to database
                        pass
                    console.print(
                        f"[dim][{i}/{len(papers)}] Skipped (exists): {paper.title[:60]}...[/dim]",
                    )
            else:
                if not dry_run:
                    success = db.add_paper(paper)
                    if success:
                        imported += 1
                        console.print(
                            f"[success][{i}/{len(papers)}] Added: {paper.title[:60]}...[/success]",
                        )
                    else:
                        skipped += 1
                        console.print(
                            f"[warning][{i}/{len(papers)}] Failed to add: {paper.title[:60]}...[/warning]",
                        )
                else:
                    imported += 1
                    console.print(
                        f"[info][{i}/{len(papers)}] Would add: {paper.title[:60]}...[/info]",
                    )

        # Summary
        console.print("\n[success]Import complete![/success]")
        console.print(f"  • Imported: {imported} papers")
        console.print(f"  • Skipped: {skipped} papers (duplicates)")

    except Exception as e:
        logger.error("Import failed", error=str(e))
        output.error(f"Import failed: {str(e)}")


if __name__ == "__main__":
    main()
