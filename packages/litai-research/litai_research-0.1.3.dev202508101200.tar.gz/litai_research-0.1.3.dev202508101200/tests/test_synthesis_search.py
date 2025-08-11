"""Tests for synthesis with search integration."""

import asyncio
from pathlib import Path
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from litai.synthesis import PaperSynthesizer, SynthesisResult, RelevantPaper
from litai.models import Paper
from litai.search_tool import PaperSearchTool


@pytest.mark.asyncio
async def test_synthesis_with_search_no_tool():
    """Test that synthesis works without search tool."""
    # Mock dependencies
    db = MagicMock()
    llm = AsyncMock()
    extractor = AsyncMock()
    
    synthesizer = PaperSynthesizer(db, llm, extractor, search_tool=None)
    
    # Mock the regular synthesis method
    test_result = SynthesisResult(
        question="test question",
        synthesis="test synthesis",
        relevant_papers=[]
    )
    synthesizer.synthesize = AsyncMock(return_value=test_result)
    
    # Should return regular synthesis result
    result = await synthesizer.synthesize_with_search("test question")
    assert result == test_result


@pytest.mark.asyncio
async def test_synthesis_with_search_no_search_needed():
    """Test when LLM decides no search is needed."""
    # Mock dependencies
    db = MagicMock()
    llm = AsyncMock()
    extractor = AsyncMock()
    search_tool = AsyncMock()
    
    synthesizer = PaperSynthesizer(db, llm, extractor, search_tool)
    
    # Mock synthesis result
    test_paper = Paper(
        paper_id="test123",
        title="Test Paper",
        authors=["Author 1"],
        year=2024,
        abstract="Test abstract",
        venue="Test venue",
        citation_count=10
    )
    test_result = SynthesisResult(
        question="test question", 
        synthesis="test synthesis",
        relevant_papers=[RelevantPaper(paper=test_paper, relevance_score=0.9, relevance_reason="Test reason")]
    )
    synthesizer.synthesize = AsyncMock(return_value=test_result)
    
    # LLM responds with NO_SEARCH
    llm.complete.return_value = {"content": "NO_SEARCH - synthesis is complete"}
    
    # Should return original synthesis without searching
    result = await synthesizer.synthesize_with_search("test question")
    assert result == test_result
    search_tool.execute_search.assert_not_called()


@pytest.mark.asyncio
async def test_synthesis_with_search_executes_commands():
    """Test that search commands are executed and synthesis updated."""
    # Mock dependencies
    db = MagicMock()
    llm = AsyncMock()
    extractor = AsyncMock()
    search_tool = AsyncMock()
    
    synthesizer = PaperSynthesizer(db, llm, extractor, search_tool)
    
    # Mock synthesis result
    test_paper = Paper(
        paper_id="test123",
        title="Test Paper", 
        authors=["Author 1"],
        year=2024,
        abstract="Test abstract",
        venue="Test venue",
        citation_count=10
    )
    test_result = SynthesisResult(
        question="What batch sizes are used?",
        synthesis="Papers use various batch sizes.",
        relevant_papers=[RelevantPaper(paper=test_paper, relevance_score=0.9, relevance_reason="Test reason")]
    )
    synthesizer.synthesize = AsyncMock(return_value=test_result)
    
    # LLM provides search commands
    llm.complete.side_effect = [
        {"content": '```bash\ngrep -i "batch size" test123.txt\n```'},
        {"content": "Papers use batch sizes ranging from 256 to 2048. Specifically, test123.txt mentions using a batch size of 256 for training."}
    ]
    
    # Search returns results
    search_tool.execute_search.return_value = ("test123.txt: We use a batch size of 256", 0)
    
    # Execute synthesis with search
    result = await synthesizer.synthesize_with_search("What batch sizes are used?")
    
    # Check search was executed
    search_tool.execute_search.assert_called_once_with('grep -i "batch size" test123.txt')
    
    # Check synthesis was updated
    assert "256" in result.synthesis
    assert "2048" in result.synthesis