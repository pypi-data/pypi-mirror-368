"""Tests for the paper search tool."""

import asyncio
from pathlib import Path
import pytest
from litai.search_tool import PaperSearchTool


@pytest.mark.asyncio
async def test_search_tool_allows_grep():
    """Test that grep commands are allowed."""
    tool = PaperSearchTool(Path("."))
    output, returncode = await tool.execute_search("grep test")
    # Should execute (might fail if no files match, but shouldn't be blocked)
    assert "Error: Only grep commands allowed" not in output


@pytest.mark.asyncio
async def test_search_tool_blocks_ripgrep():
    """Test that rg commands are blocked."""
    tool = PaperSearchTool(Path("."))
    output, returncode = await tool.execute_search("rg test")
    assert output == "Error: Only grep commands allowed"
    assert returncode == 1


@pytest.mark.asyncio
async def test_search_tool_blocks_other_commands():
    """Test that non-search commands are blocked."""
    tool = PaperSearchTool(Path("."))
    output, returncode = await tool.execute_search("ls")
    assert output == "Error: Only grep commands allowed"
    assert returncode == 1
    
    output, returncode = await tool.execute_search("cat file.txt")
    assert output == "Error: Only grep commands allowed"
    assert returncode == 1


@pytest.mark.asyncio 
async def test_search_tool_with_real_search(tmp_path):
    """Test search with actual files."""
    # Create test files
    test_dir = tmp_path / "test_papers"
    test_dir.mkdir()
    
    paper1 = test_dir / "paper1.txt"
    paper1.write_text("This paper uses a batch size of 256.")
    
    paper2 = test_dir / "paper2.txt" 
    paper2.write_text("We experiment with learning rates from 0.001 to 0.1")
    
    # Test search
    tool = PaperSearchTool(test_dir)
    output, returncode = await tool.execute_search('grep -i "batch size" paper1.txt')
    
    assert returncode == 0
    assert "batch size of 256" in output
    
    # Test grep with regex
    output, returncode = await tool.execute_search('grep -E "learning rate" paper2.txt')
    assert returncode == 0
    assert "learning rates from 0.001" in output