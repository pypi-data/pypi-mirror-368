"""Natural language handler for LitAI."""

from collections.abc import Callable
from typing import Any

import structlog
from rich.console import Console

from litai.config import Config
from litai.conversation import ConversationManager
from litai.database import Database
from litai.llm import LLMClient
from litai.models import Paper
from litai.output_formatter import OutputFormatter
from litai.synthesis_session import SynthesisSession
from litai.tool_approval import ToolApprovalManager, ToolCall
from litai.tools import get_anthropic_tools, get_openai_tools

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
        config: Config,
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
        # Add tool approval manager
        self.approval_manager = ToolApprovalManager(config)
    
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
            provider = self.llm_client.provider or "openai"  # Default to openai if None
            messages = self.conversation.get_messages_for_llm(provider)
            
            with console.status("[yellow]Thinking...[/yellow]"):
                response = await self.llm_client.complete(
                    messages,
                    tools=tools,
                    temperature=0.0,
                )
            
            # Handle the response
            content = response.get("content", "")
            tool_calls = response.get("tool_calls", [])
            
            # If there are tool calls, execute them
            if tool_calls:
                # Convert to ToolCall objects for approval
                pending_calls = [
                    ToolCall(
                        id=tc.id,
                        name=tc.name,
                        description=self._get_tool_description(tc.name, tc.arguments),
                        arguments=tc.arguments,
                    )
                    for tc in tool_calls
                ]
                
                # Get user approval for tool calls
                approved_calls = await self.approval_manager.get_approval(pending_calls)
                
                # If no tools approved, explain to user
                if not approved_calls:
                    console.print("[yellow]Tool execution cancelled by user.[/yellow]")
                    return
                
                # Add assistant message with approved tool calls
                self.conversation.add_message(
                    "assistant", 
                    content,
                    tool_calls=[{
                        "id": tc.id,
                        "name": tc.name,
                        "arguments": tc.arguments,
                    } for tc in approved_calls],
                )
                
                # Execute approved tools and get results
                tool_results = await self._execute_tools(approved_calls)
                
                # Add tool results to conversation
                self.conversation.add_message(
                    "tool",
                    "",
                    tool_results=tool_results,
                )
                
                # Get final response from LLM
                provider = self.llm_client.provider or "openai"  # Default to openai if None
                messages = self.conversation.get_messages_for_llm(provider)
                
                with console.status("[yellow]Processing results...[/yellow]"):
                    final_response = await self.llm_client.complete(
                        messages,
                        temperature=0.0,
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
    
    async def _execute_tools(self, tool_calls: list[ToolCall]) -> list[dict[str, Any]]:
        """Execute tool calls and return results.
        
        Args:
            tool_calls: List of approved ToolCall objects to execute
            
        Returns:
            List of tool results
        """
        results = []
        
        for tool_call in tool_calls:
            try:
                # Execute the tool (already approved)
                result = await self._execute_single_tool(
                    tool_call.name,
                    tool_call.arguments,
                )
                
                results.append({
                    "tool_call_id": tool_call.id,
                    "content": result,
                })
                
            except Exception as e:
                logger.exception(
                    "Tool execution failed",
                    tool_name=tool_call.name,
                    arguments=tool_call.arguments,
                )
                results.append({
                    "tool_call_id": tool_call.id,
                    "content": f"Error executing {tool_call.name}: {str(e)}",
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
                result = await handler(arguments.get("query", ""))
                return str(result)
            
        elif tool_name == "add_paper":
            handler = self.command_handlers.get("add_paper")
            if handler:
                handler(str(arguments.get("paper_numbers", "")), self.db)
                return "Paper add operation completed."
            
        elif tool_name == "list_papers":
            handler = self.command_handlers.get("list_papers")
            if handler:
                page = arguments.get("page", 1)
                result = handler(self.db, page)
                return str(result)
            
        elif tool_name == "remove_paper":
            handler = self.command_handlers.get("remove_paper")
            if handler:
                handler(str(arguments.get("paper_numbers", "")), self.db)
                return "Paper remove operation completed."
            
        elif tool_name == "show_search_results":
            handler = self.command_handlers.get("show_search_results")
            if handler:
                handler()
                return "Search results displayed."
            
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
                result = handler(self.db, page, tag)
                return str(result)
            
        else:
            return f"Unknown tool: {tool_name}"
        
        # Should not reach here, but adding for completeness
        return f"Tool {tool_name} not executed"
    
    def _get_tool_description(self, tool_name: str, arguments: dict[str, Any]) -> str:
        """Get a human-readable description of what a tool will do.
        
        Args:
            tool_name: Name of the tool
            arguments: Tool arguments
            
        Returns:
            Human-readable description
        """
        if tool_name == "find_papers":
            query = arguments.get("query", "")
            return f"Search for papers matching: {query}"
        if tool_name == "add_paper":
            numbers = arguments.get("paper_numbers", "")
            return f"Add paper(s) {numbers} to your collection"
        if tool_name == "list_papers":
            page = arguments.get("page", 1)
            return f"List papers in your collection (page {page})"
        if tool_name == "remove_paper":
            numbers = arguments.get("paper_numbers", "")
            return f"Remove paper(s) {numbers} from your collection"
        if tool_name == "show_search_results":
            return "Display recent search results"
        if tool_name == "clear_screen":
            return "Clear the terminal screen"
        if tool_name == "manage_paper_tags":
            paper_num = arguments.get("paper_number", 0)
            add_tags = arguments.get("add_tags", "")
            remove_tags = arguments.get("remove_tags", "")
            if add_tags:
                return f"Add tags '{add_tags}' to paper {paper_num}"
            if remove_tags:
                return f"Remove tags '{remove_tags}' from paper {paper_num}"
            return f"List tags for paper {paper_num}"
        return f"Execute {tool_name} with provided parameters"
