"""Tool call approval system for user control over AI actions."""

from dataclasses import dataclass

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from litai.config import Config
from litai.utils.logger import get_logger

logger = get_logger(__name__)
console = Console()


@dataclass
class ToolCall:
    """Represents a pending tool call."""

    id: str
    name: str
    description: str  # Human-readable explanation
    arguments: dict


@dataclass
class ApprovalResponse:
    """User's response to a tool call."""

    approved: bool
    cancel_all: bool = False


class ToolApprovalManager:
    """Manages interactive approval of tool calls during synthesis."""

    def __init__(self, config: Config):
        """Initialize with configuration.
        
        Args:
            config: Configuration instance
        """
        self.config = config
        self.enabled = self._get_approval_setting()

    def _get_approval_setting(self) -> bool:
        """Read tool_approval setting from config.
        
        Returns:
            True if tool approval is enabled (default), False otherwise
        """
        config_data = self.config.load_config()
        synthesis_config = config_data.get("synthesis", {})
        return bool(synthesis_config.get("tool_approval", True))

    async def get_approval(self, tool_calls: list[ToolCall]) -> list[ToolCall]:
        """Get user approval for tool calls.
        
        Args:
            tool_calls: List of pending tool calls
            
        Returns:
            List of approved (possibly modified) tool calls
        """
        if not self.enabled:
            logger.info("Tool approval disabled, auto-approving all tools")
            return tool_calls
        
        return await self.interactive_approval(tool_calls)

    async def interactive_approval(self, tool_calls: list[ToolCall]) -> list[ToolCall]:
        """Show each tool call and get user response.
        
        Args:
            tool_calls: List of pending tool calls
            
        Returns:
            List of approved tool calls
        """
        approved = []
        
        for i, call in enumerate(tool_calls, 1):
            response = await self.show_and_get_response(call, i, len(tool_calls))
            
            if response.cancel_all:
                logger.info("User cancelled all remaining tool calls")
                break
                
            if response.approved:
                approved.append(call)
                logger.info(f"Tool approved: {call.name}")
        
        return approved

    async def show_and_get_response(
        self, call: ToolCall, index: int, total: int,
    ) -> ApprovalResponse:
        """Display tool call and get user input.
        
        Args:
            call: Tool call to display
            index: Current tool index (1-based)
            total: Total number of tools
            
        Returns:
            User's response to the tool call
        """
        # Create the display panel
        panel_content = f"""[bold]Action:[/bold] {call.name}
{call.description}

[dim]Parameters:[/dim]
{self._format_params(call.arguments)}"""

        panel = Panel(
            panel_content,
            title=f"Tool Call Recommended ({index}/{total})",
            border_style="cyan",
        )
        console.print(panel)

        # Show options
        console.print("[green]→[/green] \\[Enter] Approve")
        console.print("[yellow]→[/yellow] \\[q] Cancel (tell the model to do something different)")
        console.print()

        # Get user input
        response = Prompt.ask("> ", default="")

        # Parse response
        if response == "":  # Enter pressed
            return ApprovalResponse(approved=True)
        # Any other input cancels
        return ApprovalResponse(approved=False, cancel_all=True)

    def _format_params(self, params: dict) -> str:
        """Format parameters for display.
        
        Args:
            params: Parameters dictionary
            
        Returns:
            Formatted string for display
        """
        if not params:
            return "  (no parameters)"
            
        lines = []
        for key, value in params.items():
            if isinstance(value, list):
                if len(value) > 3:
                    value_str = f"[{', '.join(str(v) for v in value[:3])}...]"
                else:
                    value_str = str(value)
            elif isinstance(value, dict):
                value_str = "{...}"
            elif isinstance(value, str) and len(value) > 50:
                value_str = f'"{value[:47]}..."'
            else:
                value_str = str(value)
            lines.append(f"  {key}: {value_str}")
        
        return "\n".join(lines)

