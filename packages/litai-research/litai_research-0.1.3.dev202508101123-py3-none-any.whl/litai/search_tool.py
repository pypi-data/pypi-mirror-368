"""Simple CLI-based search tool for searching through paper text files."""

import asyncio
import asyncio.subprocess
from pathlib import Path
from litai.utils.logger import get_logger

logger = get_logger(__name__)


class PaperSearchTool:
    """Simple bash command execution for paper searching."""

    def __init__(self, paper_cache_dir: Path):
        self.paper_cache_dir = paper_cache_dir

    async def execute_search(self, command: str) -> tuple[str, int]:
        """Execute a search command in the papers directory."""
        # Basic safety - must be grep
        if not command.strip().startswith("grep"):
            logger.warning(f"Rejected non-grep command: {command}")
            return "Error: Only grep commands allowed", 1

        logger.info(f"Executing search command: {command}", extra={"cwd": str(self.paper_cache_dir)})
        
        # Execute in papers directory to limit scope
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=self.paper_cache_dir,
        )

        stdout, _ = await proc.communicate()
        returncode = proc.returncode or 0
        
        logger.info(
            "Search command completed",
            extra={
                "command": command,
                "returncode": returncode,
                "output_length": len(stdout),
            }
        )
        
        return stdout.decode(), returncode