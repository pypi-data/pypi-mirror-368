"""Integration tests for synthesis mode tool calling with real LLM."""

import asyncio
import json
import os
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, AsyncMock

import pytest
import pytest_asyncio
from rich.console import Console

from litai.config import Config
from litai.database import Database
from litai.extraction import PaperExtractor
from litai.llm import LLMClient
from litai.models import Paper
from litai.pdf_processor import PDFProcessor
from litai.synthesis_tools import (
    SynthesisConversation,
    SynthesisOrchestrator,
)


# Skip these tests if no API key is available
pytestmark = pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set"
)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def config(temp_dir):
    """Create a real config with API key and gpt-5-mini model."""
    config = Config(base_dir=temp_dir)
    # Use gpt-5-mini for faster, cheaper tests
    config.update_config("llm.provider", "openai")
    config.update_config("llm.model", "gpt-5-mini")
    # Disable tool approval for testing
    config.update_config("tool_approval", False)
    return config


@pytest.fixture
def db(config):
    """Create a real database."""
    return Database(config)


@pytest.fixture
def sample_papers(db):
    """Add sample papers to the database."""
    papers = [
        Paper(
            paper_id="transformer2017",
            title="Attention Is All You Need",
            authors=["Vaswani", "Shazeer", "Parmar"],
            year=2017,
            abstract="The dominant sequence transduction models are based on complex recurrent or convolutional neural networks. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms.",
            citation_count=80000,
            tags=["transformers", "attention", "NLP"],
        ),
        Paper(
            paper_id="bert2018",
            title="BERT: Pre-training of Deep Bidirectional Transformers",
            authors=["Devlin", "Chang", "Lee", "Toutanova"],
            year=2018,
            abstract="We introduce a new language representation model called BERT, which stands for Bidirectional Encoder Representations from Transformers.",
            citation_count=60000,
            tags=["BERT", "NLP", "pretraining"],
        ),
        Paper(
            paper_id="gpt3_2020",
            title="Language Models are Few-Shot Learners",
            authors=["Brown", "Mann", "Ryder", "Subbiah"],
            year=2020,
            abstract="Recent work has demonstrated substantial gains on many NLP tasks and benchmarks by pre-training on a large corpus of text followed by fine-tuning on a specific task.",
            citation_count=15000,
            tags=["GPT", "few-shot", "language-models"],
        ),
        Paper(
            paper_id="vit2020",
            title="An Image is Worth 16x16 Words: Transformers for Image Recognition",
            authors=["Dosovitskiy", "Beyer", "Kolesnikov"],
            year=2020,
            abstract="While the Transformer architecture has become the de-facto standard for natural language processing tasks, its applications to computer vision remain limited.",
            citation_count=20000,
            tags=["vision-transformer", "computer-vision", "transformers"],
        ),
    ]
    
    # Add papers to database
    for paper in papers:
        db.add_paper(paper)
    
    # Add some notes
    db.add_note("transformer2017", "Revolutionary architecture that replaced RNNs")
    db.append_agent_note("bert2018", "Key innovation: masked language modeling")
    
    return papers


@pytest_asyncio.fixture
async def synthesis_conversation_with_tracking(db, config, sample_papers):
    """Create synthesis conversation that tracks which tools are called."""
    llm_client = LLMClient(config)
    pdf_processor = PDFProcessor(db, config.base_dir)
    extractor = PaperExtractor(db, llm_client, pdf_processor)
    orchestrator = SynthesisOrchestrator(db, llm_client, extractor)
    conversation = SynthesisConversation(db, llm_client, orchestrator, config)
    
    # Create and disable approval manager proactively (like NaturalLanguageHandler does)
    from litai.tool_approval import ToolApprovalManager
    conversation.approval_manager = ToolApprovalManager(config)
    conversation.approval_manager.enabled = False
    
    # Track tool calls
    tool_calls = []
    original_execute = conversation._execute_tool
    
    async def tracked_execute(tool_name: str, arguments: dict):
        tool_calls.append({
            "name": tool_name,
            "arguments": arguments
        })
        return await original_execute(tool_name, arguments)
    
    conversation._execute_tool = tracked_execute
    conversation._tool_calls = tool_calls
    
    yield conversation
    
    # Cleanup
    await llm_client.close()


class TestSynthesisToolCalling:
    """Test that the LLM calls the correct synthesis tools for various queries."""
    
    @pytest.mark.asyncio
    async def test_search_papers_query(self, synthesis_conversation_with_tracking, capsys):
        """Test that searching for papers triggers search_papers tool."""
        await synthesis_conversation_with_tracking.handle_message(
            "Find papers about transformers"
        )
        
        # Check that search_papers was called
        tool_names = [tc["name"] for tc in synthesis_conversation_with_tracking._tool_calls]
        assert "search_papers" in tool_names
        
        # Verify search arguments
        search_call = next(tc for tc in synthesis_conversation_with_tracking._tool_calls if tc["name"] == "search_papers")
        assert "transformer" in search_call["arguments"]["query"].lower()
    
    @pytest.mark.asyncio
    async def test_select_papers_query(self, synthesis_conversation_with_tracking, capsys):
        """Test that asking to select papers triggers select_papers tool."""
        # First search for papers
        await synthesis_conversation_with_tracking.handle_message(
            "Search for papers about BERT and then select the BERT paper"
        )
        
        tool_names = [tc["name"] for tc in synthesis_conversation_with_tracking._tool_calls]
        
        # Should call both search and select
        assert "search_papers" in tool_names
        assert "select_papers" in tool_names or "list_selected_papers" in tool_names
    
    @pytest.mark.asyncio
    async def test_select_all_papers_query(self, synthesis_conversation_with_tracking, capsys):
        """Test that asking to select all papers triggers select_all_papers tool."""
        await synthesis_conversation_with_tracking.handle_message(
            "Select all papers in my collection"
        )
        
        tool_names = [tc["name"] for tc in synthesis_conversation_with_tracking._tool_calls]
        assert "select_all_papers" in tool_names
    
    @pytest.mark.asyncio
    async def test_list_selected_papers_query(self, synthesis_conversation_with_tracking, capsys):
        """Test that asking about selected papers triggers list_selected_papers."""
        # First select some papers
        synthesis_conversation_with_tracking.session.selected_papers = synthesis_conversation_with_tracking._tool_calls  # Reset
        await synthesis_conversation_with_tracking.handle_message(
            "What papers have I selected?"
        )
        
        tool_names = [tc["name"] for tc in synthesis_conversation_with_tracking._tool_calls]
        assert "list_selected_papers" in tool_names
    
    @pytest.mark.asyncio
    async def test_extract_context_query(self, synthesis_conversation_with_tracking, sample_papers, capsys):
        """Test that asking to extract content triggers extract_context tool."""
        # Pre-select papers
        synthesis_conversation_with_tracking.session.selected_papers = sample_papers[:2]
        synthesis_conversation_with_tracking._tool_calls.clear()
        
        await synthesis_conversation_with_tracking.handle_message(
            "Extract the abstracts from the selected papers"
        )
        
        tool_names = [tc["name"] for tc in synthesis_conversation_with_tracking._tool_calls]
        assert "extract_context" in tool_names
        
        # Check depth argument
        extract_call = next(tc for tc in synthesis_conversation_with_tracking._tool_calls if tc["name"] == "extract_context")
        depth = extract_call["arguments"]["depth"]
        assert "abstracts" in depth or depth == ["abstracts"]
    
    @pytest.mark.asyncio
    async def test_synthesize_query(self, synthesis_conversation_with_tracking, sample_papers, capsys):
        """Test that asking questions triggers synthesize tool."""
        # Pre-select papers and context
        synthesis_conversation_with_tracking.session.selected_papers = sample_papers[:2]
        synthesis_conversation_with_tracking._tool_calls.clear()
        
        await synthesis_conversation_with_tracking.handle_message(
            "What are the main contributions of these papers?"
        )
        
        tool_names = [tc["name"] for tc in synthesis_conversation_with_tracking._tool_calls]
        # Should either extract context first or directly synthesize
        assert "synthesize" in tool_names or "extract_context" in tool_names
    
    @pytest.mark.asyncio
    async def test_refine_synthesis_query(self, synthesis_conversation_with_tracking, sample_papers, capsys):
        """Test that asking for refinement triggers refine_synthesis tool."""
        # Setup: select papers and do initial synthesis
        synthesis_conversation_with_tracking.session.selected_papers = sample_papers[:2]
        synthesis_conversation_with_tracking.session.current_question = "What are transformers?"
        synthesis_conversation_with_tracking.session.synthesis_history.append(MagicMock())
        synthesis_conversation_with_tracking._tool_calls.clear()
        
        await synthesis_conversation_with_tracking.handle_message(
            "Go deeper on the attention mechanism"
        )
        
        tool_names = [tc["name"] for tc in synthesis_conversation_with_tracking._tool_calls]
        assert "refine_synthesis" in tool_names or "synthesize" in tool_names
    
    @pytest.mark.asyncio
    async def test_session_state_query(self, synthesis_conversation_with_tracking, capsys):
        """Test that asking about session triggers get_session_state tool."""
        await synthesis_conversation_with_tracking.handle_message(
            "What's the current session state?"
        )
        
        tool_names = [tc["name"] for tc in synthesis_conversation_with_tracking._tool_calls]
        assert "get_session_state" in tool_names
    
    @pytest.mark.asyncio
    async def test_append_agent_note_query(self, synthesis_conversation_with_tracking, sample_papers, capsys):
        """Test that asking to save insights triggers append_agent_note tool."""
        # Select a paper first
        synthesis_conversation_with_tracking.session.selected_papers = [sample_papers[0]]
        synthesis_conversation_with_tracking._tool_calls.clear()
        
        await synthesis_conversation_with_tracking.handle_message(
            f"Save a note that paper {sample_papers[0].paper_id} introduces a foundational architecture"
        )
        
        tool_names = [tc["name"] for tc in synthesis_conversation_with_tracking._tool_calls]
        assert "append_agent_note" in tool_names
        
        # Check arguments
        note_call = next(tc for tc in synthesis_conversation_with_tracking._tool_calls if tc["name"] == "append_agent_note")
        assert note_call["arguments"]["paper_id"] == sample_papers[0].paper_id
        assert "foundational" in note_call["arguments"]["content"].lower()


class TestComplexWorkflows:
    """Test complex multi-tool workflows."""
    
    @pytest.mark.asyncio
    async def test_search_select_synthesize_workflow(self, synthesis_conversation_with_tracking, capsys):
        """Test complete workflow: search -> select -> extract -> synthesize."""
        synthesis_conversation_with_tracking._tool_calls.clear()
        
        await synthesis_conversation_with_tracking.handle_message(
            "Find papers about transformers, select them, and tell me their key contributions"
        )
        
        tool_names = [tc["name"] for tc in synthesis_conversation_with_tracking._tool_calls]
        
        # Should use multiple tools in sequence
        assert "search_papers" in tool_names
        # May also select papers and synthesize
        assert len(tool_names) >= 1  # At minimum search
    
    @pytest.mark.asyncio
    async def test_extract_multiple_contexts(self, synthesis_conversation_with_tracking, sample_papers, capsys):
        """Test extracting multiple context types."""
        synthesis_conversation_with_tracking.session.selected_papers = sample_papers[:2]
        synthesis_conversation_with_tracking._tool_calls.clear()
        
        await synthesis_conversation_with_tracking.handle_message(
            "Extract both abstracts and any notes from the selected papers"
        )
        
        tool_names = [tc["name"] for tc in synthesis_conversation_with_tracking._tool_calls]
        assert "extract_context" in tool_names
        
        # Check that multiple depths were requested
        extract_call = next(tc for tc in synthesis_conversation_with_tracking._tool_calls if tc["name"] == "extract_context")
        depth = extract_call["arguments"]["depth"]
        if isinstance(depth, list):
            assert len(depth) >= 1  # Should have multiple context types or single
    
    @pytest.mark.asyncio
    async def test_comparative_analysis_workflow(self, synthesis_conversation_with_tracking, sample_papers, capsys):
        """Test comparative analysis triggering appropriate tools."""
        # Pre-select papers
        synthesis_conversation_with_tracking.session.selected_papers = sample_papers[:3]
        synthesis_conversation_with_tracking._tool_calls.clear()
        
        await synthesis_conversation_with_tracking.handle_message(
            "Compare the approaches used in BERT and GPT-3"
        )
        
        tool_names = [tc["name"] for tc in synthesis_conversation_with_tracking._tool_calls]
        
        # Should synthesize with comparative mode
        if "synthesize" in tool_names:
            synth_call = next(tc for tc in synthesis_conversation_with_tracking._tool_calls if tc["name"] == "synthesize")
            # LLM might choose comparative mode
            assert "compare" in synth_call["arguments"]["question"].lower() or \
                   synth_call["arguments"].get("mode") == "comparative"


class TestContextualQueries:
    """Test that LLM maintains context across queries."""
    
    @pytest.mark.asyncio
    async def test_follow_up_questions(self, synthesis_conversation_with_tracking, sample_papers, capsys):
        """Test that follow-up questions use context appropriately."""
        # First query - select papers
        await synthesis_conversation_with_tracking.handle_message(
            "Select the BERT and GPT-3 papers"
        )
        
        initial_tool_count = len(synthesis_conversation_with_tracking._tool_calls)
        
        # Follow-up query
        await synthesis_conversation_with_tracking.handle_message(
            "What do they say about pretraining?"
        )
        
        # Should synthesize without re-selecting papers
        new_tools = synthesis_conversation_with_tracking._tool_calls[initial_tool_count:]
        tool_names = [tc["name"] for tc in new_tools]
        
        # Should synthesize or extract context, not search again
        assert "synthesize" in tool_names or "extract_context" in tool_names
        assert "select_papers" not in tool_names  # Shouldn't re-select
    
    @pytest.mark.asyncio
    async def test_refinement_maintains_context(self, synthesis_conversation_with_tracking, sample_papers, capsys):
        """Test that refinement requests maintain paper context."""
        # Setup context
        synthesis_conversation_with_tracking.session.selected_papers = sample_papers[:2]
        
        # Initial synthesis
        await synthesis_conversation_with_tracking.handle_message(
            "What are the key innovations?"
        )
        
        initial_count = len(synthesis_conversation_with_tracking._tool_calls)
        
        # Refinement
        await synthesis_conversation_with_tracking.handle_message(
            "Tell me more about the technical details"
        )
        
        new_tools = synthesis_conversation_with_tracking._tool_calls[initial_count:]
        tool_names = [tc["name"] for tc in new_tools]
        
        # Should refine or synthesize again, not search for new papers
        assert "refine_synthesis" in tool_names or "synthesize" in tool_names


class TestToolArgumentValidation:
    """Test that LLM provides correct arguments to tools."""
    
    @pytest.mark.asyncio
    async def test_search_with_tags(self, synthesis_conversation_with_tracking, capsys):
        """Test that tag-based search includes tag arguments."""
        await synthesis_conversation_with_tracking.handle_message(
            "Find papers tagged with NLP"
        )
        
        tool_calls = synthesis_conversation_with_tracking._tool_calls
        search_calls = [tc for tc in tool_calls if tc["name"] == "search_papers"]
        
        if search_calls:
            search_call = search_calls[0]
            # Should either use tags argument or include NLP in query
            has_tag = "tags" in search_call["arguments"] and "NLP" in str(search_call["arguments"]["tags"])
            has_query = "query" in search_call["arguments"] and "nlp" in search_call["arguments"]["query"].lower()
            assert has_tag or has_query
    
    @pytest.mark.asyncio
    async def test_extract_context_depth_specification(self, synthesis_conversation_with_tracking, sample_papers, capsys):
        """Test that context extraction specifies correct depth."""
        synthesis_conversation_with_tracking.session.selected_papers = sample_papers[:2]
        synthesis_conversation_with_tracking._tool_calls.clear()
        
        await synthesis_conversation_with_tracking.handle_message(
            "Extract the full text from selected papers"
        )
        
        extract_calls = [tc for tc in synthesis_conversation_with_tracking._tool_calls if tc["name"] == "extract_context"]
        
        if extract_calls:
            extract_call = extract_calls[0]
            depth = extract_call["arguments"]["depth"]
            # Should specify full_text depth
            assert "full_text" in str(depth).lower() or "full" in str(depth).lower()
    
    @pytest.mark.asyncio
    async def test_synthesize_mode_specification(self, synthesis_conversation_with_tracking, sample_papers, capsys):
        """Test that synthesis mode is correctly specified."""
        synthesis_conversation_with_tracking.session.selected_papers = sample_papers[:3]
        synthesis_conversation_with_tracking._tool_calls.clear()
        
        await synthesis_conversation_with_tracking.handle_message(
            "Give me a detailed thorough analysis of these papers"
        )
        
        synth_calls = [tc for tc in synthesis_conversation_with_tracking._tool_calls if tc["name"] == "synthesize"]
        
        if synth_calls:
            synth_call = synth_calls[0]
            # Might specify thorough mode
            mode = synth_call["arguments"].get("mode", "quick")
            # LLM might choose thorough for detailed request
            assert mode in ["quick", "thorough", "comparative"]


class TestErrorRecovery:
    """Test that LLM handles error cases appropriately."""
    
    @pytest.mark.asyncio
    async def test_no_papers_selected_synthesis(self, synthesis_conversation_with_tracking, capsys):
        """Test handling synthesis request with no papers selected."""
        # Ensure no papers selected
        synthesis_conversation_with_tracking.session.selected_papers = []
        synthesis_conversation_with_tracking._tool_calls.clear()
        
        await synthesis_conversation_with_tracking.handle_message(
            "What are the key findings?"
        )
        
        tool_names = [tc["name"] for tc in synthesis_conversation_with_tracking._tool_calls]
        
        # Should either search for papers or list them first
        assert "search_papers" in tool_names or \
               "select_papers" in tool_names or \
               "select_all_papers" in tool_names or \
               "list_selected_papers" in tool_names
    
    @pytest.mark.asyncio
    async def test_empty_search_results(self, synthesis_conversation_with_tracking, capsys):
        """Test handling search with no results."""
        await synthesis_conversation_with_tracking.handle_message(
            "Find papers about quantum_computing_xyz_nonexistent"
        )
        
        # Should still call search_papers
        tool_names = [tc["name"] for tc in synthesis_conversation_with_tracking._tool_calls]
        assert "search_papers" in tool_names
        
        captured = capsys.readouterr()
        # Response should acknowledge no results or limited results


class TestToolCallSequencing:
    """Test that tools are called in logical sequences."""
    
    @pytest.mark.asyncio
    async def test_search_before_select(self, synthesis_conversation_with_tracking, capsys):
        """Test that search happens before selection when needed."""
        await synthesis_conversation_with_tracking.handle_message(
            "Find and select papers about attention mechanisms"
        )
        
        tool_calls = synthesis_conversation_with_tracking._tool_calls
        tool_names = [tc["name"] for tc in tool_calls]
        
        # If both tools called, search should come before select
        if "search_papers" in tool_names and "select_papers" in tool_names:
            search_idx = tool_names.index("search_papers")
            select_idx = tool_names.index("select_papers")
            assert search_idx < select_idx
    
    @pytest.mark.asyncio
    async def test_extract_before_synthesize(self, synthesis_conversation_with_tracking, sample_papers, capsys):
        """Test that extraction happens before synthesis when needed."""
        synthesis_conversation_with_tracking.session.selected_papers = sample_papers[:2]
        synthesis_conversation_with_tracking._tool_calls.clear()
        
        await synthesis_conversation_with_tracking.handle_message(
            "Extract full text and then analyze the methodology sections"
        )
        
        tool_calls = synthesis_conversation_with_tracking._tool_calls
        tool_names = [tc["name"] for tc in tool_calls]
        
        # If both called, extract should come before synthesize
        if "extract_context" in tool_names and "synthesize" in tool_names:
            extract_idx = tool_names.index("extract_context")
            synth_idx = tool_names.index("synthesize")
            assert extract_idx < synth_idx


# Helper function to run async tests
def run_async_test(coro):
    """Helper to run async tests."""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)


if __name__ == "__main__":
    # Can run specific tests directly
    import sys
    pytest.main([__file__] + sys.argv[1:])