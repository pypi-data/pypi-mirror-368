"""Natural language handler for LitAI."""

from typing import Any, Callable

import structlog
from rich.console import Console
from rich.prompt import Prompt

from litai.llm import LLMClient
from litai.conversation import ConversationManager
from litai.tools import get_openai_tools, get_anthropic_tools
from litai.database import Database
from litai.models import Paper
from litai.output_formatter import OutputFormatter
from litai.config import Config
from litai.synthesis_session import SynthesisSession

logger = structlog.get_logger()
console = Console()
output = OutputFormatter(console)


class NaturalLanguageHandler:
    """Handles natural language queries and tool execution."""
    
    def __init__(
        self, 
        db: Database,
        command_handlers: dict[str, Callable],
        search_results_ref: list[Paper],
        config: Config
    ):
        """Initialize the natural language handler.
        
        Args:
            db: Database instance
            command_handlers: Dictionary mapping tool names to handler functions
            search_results_ref: Reference to the global search results list
            config: Configuration instance
        """
        self.db = db
        self.llm_client = LLMClient(config)
        self.conversation = ConversationManager(config)
        self.command_handlers = command_handlers
        self.search_results_ref = search_results_ref
        # Add synthesis session for conversational flow
        self.synthesis_session = SynthesisSession()
    
    async def close(self) -> None:
        """Close the handler and cleanup resources."""
        await self.llm_client.close()
        
    async def handle_query(self, query: str) -> None:
        """Handle a natural language query.
        
        Args:
            query: The user's natural language query
        """
        logger.info("nl_query_start", query=query)
        
        # Add user message to conversation
        self.conversation.add_message("user", query)
        
        try:
            # Get appropriate tools for the provider
            if self.llm_client.provider == "openai":
                tools = get_openai_tools()
            else:
                tools = get_anthropic_tools()
            
            # Get LLM response with tools
            messages = self.conversation.get_messages_for_llm(self.llm_client.provider)
            
            with console.status("[yellow]Thinking...[/yellow]"):
                response = await self.llm_client.complete(
                    messages,
                    tools=tools,
                    temperature=0.0
                )
            
            # Handle the response
            content = response.get("content", "")
            tool_calls = response.get("tool_calls", [])
            
            # If there are tool calls, execute them
            if tool_calls:
                # Add assistant message with tool calls
                self.conversation.add_message(
                    "assistant", 
                    content,
                    tool_calls=[{
                        "id": tc.id,
                        "name": tc.name,
                        "arguments": tc.arguments
                    } for tc in tool_calls]
                )
                
                # Execute tools and get results
                tool_results = await self._execute_tools(tool_calls)
                
                # Add tool results to conversation
                self.conversation.add_message(
                    "tool",
                    "",
                    tool_results=tool_results
                )
                
                # Get final response from LLM
                messages = self.conversation.get_messages_for_llm(self.llm_client.provider)
                
                with console.status("[yellow]Processing results...[/yellow]"):
                    final_response = await self.llm_client.complete(
                        messages,
                        temperature=0.0
                    )
                
                final_content = final_response.get("content", "")
                self.conversation.add_message("assistant", final_content)
                
                # Display the response
                if final_content:
                    output.ai_response(final_content)
            else:
                # Just display the content
                self.conversation.add_message("assistant", content)
                if content:
                    output.ai_response(content)
                    
            logger.info("nl_query_success", query=query, tool_count=len(tool_calls))
            
        except Exception as e:
            logger.exception("Natural language query failed", query=query)
            output.error(f"Error processing query: {e}")
    
    async def _execute_tools(self, tool_calls: list) -> list[dict[str, Any]]:
        """Execute tool calls and return results.
        
        Args:
            tool_calls: List of tool calls to execute
            
        Returns:
            List of tool results
        """
        results = []
        
        for tool_call in tool_calls:
            try:
                # Ask for user confirmation
                if not await self._get_user_confirmation(tool_call.name, tool_call.arguments):
                    results.append({
                        "tool_call_id": tool_call.id,
                        "content": "Tool execution cancelled by user."
                    })
                    continue
                
                # Execute the tool
                result = await self._execute_single_tool(
                    tool_call.name,
                    tool_call.arguments
                )
                
                results.append({
                    "tool_call_id": tool_call.id,
                    "content": result
                })
                
            except Exception as e:
                logger.exception(
                    "Tool execution failed",
                    tool_name=tool_call.name,
                    arguments=tool_call.arguments
                )
                results.append({
                    "tool_call_id": tool_call.id,
                    "content": f"Error executing {tool_call.name}: {str(e)}"
                })
        
        return results
    
    async def _execute_single_tool(self, tool_name: str, arguments: dict[str, Any]) -> str:
        """Execute a single tool using the provided command handlers.
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Arguments for the tool
            
        Returns:
            String result of the tool execution
        """
        logger.info("tool_execution_start", tool_name=tool_name, arguments=arguments)
        
        # Map tool names to command handlers
        if tool_name == "find_papers":
            handler = self.command_handlers.get("find_papers")
            if handler:
                return await handler(arguments.get("query", ""))
            
        elif tool_name == "add_paper":
            handler = self.command_handlers.get("add_paper")
            if handler:
                handler(str(arguments.get("paper_numbers", "")), self.db)
                return "Paper add operation completed."
            
        elif tool_name == "list_papers":
            handler = self.command_handlers.get("list_papers")
            if handler:
                page = arguments.get("page", 1)
                return handler(self.db, page)
            
        elif tool_name == "remove_paper":
            handler = self.command_handlers.get("remove_paper")
            if handler:
                handler(str(arguments.get("paper_numbers", "")), self.db)
                return "Paper remove operation completed."
            
        elif tool_name == "distill_paper":
            handler = self.command_handlers.get("distill_paper")
            if handler:
                await handler(str(arguments.get("paper_numbers", "")), self.db)
                return "Paper reading completed."
            
        elif tool_name == "synthesize_papers":
            # Synthesis is now only available in interactive mode
            return "Synthesis is now only available in interactive mode. Use /synthesize to enter synthesis mode."
            
        elif tool_name == "ask_paper":
            handler = self.command_handlers.get("ask_paper")
            if handler:
                paper_numbers = str(arguments.get("paper_numbers", ""))
                question = arguments.get("question", "")
                args = f"{paper_numbers} {question}"
                result = await handler(args, self.db)
                return result
            
        elif tool_name == "show_search_results":
            handler = self.command_handlers.get("show_search_results")
            if handler:
                handler()
                return "Search results displayed."
            
        elif tool_name == "fetch_hf_papers":
            handler = self.command_handlers.get("fetch_hf_papers")
            if handler:
                await handler()
                return "HF papers fetched."
            
        elif tool_name == "clear_screen":
            console.clear()
            return "Screen cleared."
            
        elif tool_name == "manage_paper_tags":
            paper_number = arguments.get("paper_number", 0)
            add_tags = arguments.get("add_tags", "")
            remove_tags = arguments.get("remove_tags", "")
            
            # Build the command string
            if add_tags:
                handler = self.command_handlers.get("handle_tag_command")
                if handler:
                    handler(f"{paper_number} -a {add_tags}", self.db)
                    return f"Added tags to paper {paper_number}."
            elif remove_tags:
                handler = self.command_handlers.get("handle_tag_command") 
                if handler:
                    handler(f"{paper_number} -r {remove_tags}", self.db)
                    return f"Removed tags from paper {paper_number}."
            else:
                # Just list tags for the paper
                handler = self.command_handlers.get("handle_tag_command")
                if handler:
                    handler(str(paper_number), self.db)
                    return f"Listed tags for paper {paper_number}."
                    
        elif tool_name == "list_all_tags":
            handler = self.command_handlers.get("list_tags")
            if handler:
                handler(self.db)
                return "Listed all tags."
                
        elif tool_name == "list_papers_by_tag":
            tag = arguments.get("tag", "")
            page = arguments.get("page", 1)
            handler = self.command_handlers.get("list_papers")
            if handler:
                return handler(self.db, page, tag)
            
        else:
            return f"Unknown tool: {tool_name}"
    
    async def _get_user_confirmation(self, tool_name: str, arguments: dict[str, Any]) -> bool:
        """Get user confirmation before executing a tool.
        
        Args:
            tool_name: Name of the tool
            arguments: Tool arguments
            
        Returns:
            True if user confirms, False otherwise
        """
        # Format the tool call for display
        output.section("Tool Execution Request", "🔧", "bold yellow")
        console.print(f"Tool: [cyan]{tool_name}[/cyan]")
        
        if arguments:
            console.print("\nArguments:")
            for key, value in arguments.items():
                console.print(f"  • {key}: {value}")
        
        # Get confirmation
        confirm = Prompt.ask(
            "\nProceed?",
            choices=["yes", "y", "no", "n"],
            default="yes"
        )
        
        return confirm.lower() in ["yes", "y"]