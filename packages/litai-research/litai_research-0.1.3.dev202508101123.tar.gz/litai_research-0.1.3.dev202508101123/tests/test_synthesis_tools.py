"""Tests for synthesis tools."""

import pytest
from litai.synthesis_tools import (
    PaperSelector,
    ContextExtractor,
    QuestionAnswerer,
    SynthesisOrchestrator,
    ExtractedContext,
    SynthesisConversation
)
from litai.models import Paper
from litai.extraction import KeyPoint
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def sample_papers():
    """Create sample papers for testing."""
    return [
        Paper(
            paper_id="paper1",
            title="Deep Learning for NLP",
            authors=["John Doe", "Jane Smith"],
            year=2023,
            abstract="This paper explores deep learning techniques for natural language processing...",
            tags=["NLP", "deep-learning"]
        ),
        Paper(
            paper_id="paper2",
            title="Reinforcement Learning Survey",
            authors=["Alice Brown"],
            year=2022,
            abstract="A comprehensive survey of reinforcement learning methods...",
            tags=["RL", "survey"]
        ),
        Paper(
            paper_id="paper3",
            title="Transformer Architecture",
            authors=["Bob Wilson"],
            year=2024,
            abstract="Improvements to the transformer architecture for better performance...",
            tags=["transformers", "NLP"]
        )
    ]


@pytest.fixture
def mock_db(sample_papers):
    """Create mock database."""
    db = MagicMock()
    db.list_papers.return_value = sample_papers
    db.get_notes.return_value = "Test notes for the paper"
    return db


@pytest.fixture
def mock_llm():
    """Create mock LLM client."""
    llm = MagicMock()
    llm.complete = AsyncMock()
    return llm


@pytest.fixture
def mock_extractor():
    """Create mock paper extractor."""
    extractor = MagicMock()
    extractor.extract_key_points = AsyncMock(return_value=[
        KeyPoint(
            claim="Test claim 1",
            evidence="Test evidence 1",
            section="Introduction"
        ),
        KeyPoint(
            claim="Test claim 2",
            evidence="Test evidence 2",
            section="Methods"
        )
    ])
    extractor._read_paper_text = MagicMock(return_value="Full paper text content...")
    return extractor


class TestPaperSelector:
    """Tests for PaperSelector."""
    
    @pytest.mark.asyncio
    async def test_select_by_tags(self, mock_db, mock_llm, sample_papers):
        """Test selecting papers by tags."""
        selector = PaperSelector(mock_db, mock_llm)
        
        # Select papers with NLP tag
        papers = await selector.select_papers(tags=["NLP"])
        
        assert len(papers) == 2
        assert all("NLP" in p.tags for p in papers)
        
    @pytest.mark.asyncio
    async def test_select_by_paper_ids(self, mock_db, mock_llm, sample_papers):
        """Test selecting specific papers by ID."""
        selector = PaperSelector(mock_db, mock_llm)
        
        # Select specific papers
        papers = await selector.select_papers(paper_ids=["paper1", "paper3"])
        
        assert len(papers) == 2
        assert papers[0].paper_id == "paper1"
        assert papers[1].paper_id == "paper3"
        
    @pytest.mark.asyncio
    async def test_select_with_limit(self, mock_db, mock_llm, sample_papers):
        """Test limiting number of selected papers."""
        selector = PaperSelector(mock_db, mock_llm)
        
        # Select with limit
        papers = await selector.select_papers(limit=2)
        
        assert len(papers) == 2
        
    @pytest.mark.asyncio
    async def test_semantic_selection(self, mock_db, mock_llm, sample_papers):
        """Test semantic paper selection with query."""
        # Mock LLM response for semantic selection
        mock_llm.complete.return_value = {"content": "[1, 3]"}
        
        selector = PaperSelector(mock_db, mock_llm)
        
        papers = await selector.select_papers(query="transformer architectures")
        
        assert len(papers) == 2
        assert papers[0].title == "Deep Learning for NLP"
        assert papers[1].title == "Transformer Architecture"
        mock_llm.complete.assert_called_once()


class TestContextExtractor:
    """Tests for ContextExtractor."""
    
    @pytest.mark.asyncio
    async def test_extract_abstracts(self, mock_db, mock_extractor, sample_papers):
        """Test extracting abstracts as context."""
        extractor = ContextExtractor(mock_db, mock_extractor)
        
        contexts = await extractor.extract_context(
            sample_papers[:2],
            context_types="abstracts"
        )
        
        assert len(contexts) == 2
        assert contexts["paper1"].context_type == "abstracts"
        assert "deep learning techniques" in contexts["paper1"].content
        
    @pytest.mark.asyncio
    async def test_extract_notes(self, mock_db, mock_extractor, sample_papers):
        """Test extracting user notes as context."""
        extractor = ContextExtractor(mock_db, mock_extractor)
        
        contexts = await extractor.extract_context(
            [sample_papers[0]],
            context_types="notes"
        )
        
        assert len(contexts) == 1
        assert contexts["paper1"].context_type == "notes"
        assert contexts["paper1"].content == "Test notes for the paper"
        
    @pytest.mark.asyncio
    async def test_extract_key_points(self, mock_db, mock_extractor, sample_papers):
        """Test extracting key points as context."""
        extractor = ContextExtractor(mock_db, mock_extractor)
        
        contexts = await extractor.extract_context(
            [sample_papers[0]],
            context_types="agent_notes"
        )
        
        assert len(contexts) == 1
        assert contexts["paper1"].context_type == "key_points"
        assert "Test claim 1" in contexts["paper1"].content
        assert "Test evidence 1" in contexts["paper1"].content
        
    @pytest.mark.asyncio
    async def test_extract_full_text(self, mock_db, mock_extractor, sample_papers):
        """Test extracting full text as context."""
        extractor = ContextExtractor(mock_db, mock_extractor)
        
        contexts = await extractor.extract_context(
            [sample_papers[0]],
            context_types="full_text"
        )
        
        assert len(contexts) == 1
        assert contexts["paper1"].context_type == "full_text"
        assert contexts["paper1"].content == "Full paper text content..."
        
    @pytest.mark.asyncio
    async def test_extract_sections(self, mock_db, mock_extractor, sample_papers):
        """Test extracting specific sections."""
        # Mock full text with sections
        mock_extractor._read_paper_text.return_value = """
        ## Introduction
        This is the introduction section.
        
        ## Methods
        This is the methods section.
        
        ## Results
        This is the results section.
        
        ## Conclusion
        This is the conclusion.
        """
        
        extractor = ContextExtractor(mock_db, mock_extractor)
        
        contexts = await extractor.extract_context(
            [sample_papers[0]],
            context_types="sections",
            sections=["methods", "results"]
        )
        
        assert len(contexts) == 1
        content = contexts["paper1"].content
        assert "METHODS" in content
        assert "methods section" in content
        assert "RESULTS" in content
        assert "results section" in content


class TestQuestionAnswerer:
    """Tests for QuestionAnswerer."""
    
    @pytest.mark.asyncio
    async def test_quick_answer(self, mock_llm, sample_papers):
        """Test generating quick answer."""
        mock_llm.complete.return_value = {"content": "Quick answer based on abstracts."}
        
        answerer = QuestionAnswerer(mock_llm)
        
        context = {
            "paper1": ExtractedContext(
                paper_id="paper1",
                context_types="abstracts",
                content="Abstract content...",
                metadata={"title": "Test Paper", "year": "2023"}
            )
        }
        
        answer = await answerer.answer(
            "What is the main contribution?",
            context,
            sample_papers[:1],
            depth="quick"
        )
        
        assert answer == "Quick answer based on abstracts."
        mock_llm.complete.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_thorough_answer(self, mock_llm, sample_papers):
        """Test generating thorough answer."""
        mock_llm.complete.return_value = {"content": "Detailed comprehensive analysis..."}
        
        answerer = QuestionAnswerer(mock_llm)
        
        context = {
            "paper1": ExtractedContext(
                paper_id="paper1",
                context_types="agent_notes",
                content="Key points content...",
                metadata={"title": "Test Paper", "year": "2023"}
            )
        }
        
        answer = await answerer.answer(
            "Analyze the methodology",
            context,
            sample_papers[:1],
            depth="thorough"
        )
        
        assert answer == "Detailed comprehensive analysis..."
        # Check that max_tokens was set for thorough analysis
        call_args = mock_llm.complete.call_args
        assert call_args[1]["max_tokens"] == 1500
        
    @pytest.mark.asyncio
    async def test_comparative_answer(self, mock_llm, sample_papers):
        """Test generating comparative answer."""
        mock_llm.complete.return_value = {"content": "Comparison between papers..."}
        
        answerer = QuestionAnswerer(mock_llm)
        
        context = {
            "paper1": ExtractedContext(
                paper_id="paper1",
                context_types="abstracts",
                content="Paper 1 content",
                metadata={"title": "Paper 1", "year": "2023"}
            ),
            "paper2": ExtractedContext(
                paper_id="paper2",
                context_types="abstracts",
                content="Paper 2 content",
                metadata={"title": "Paper 2", "year": "2022"}
            )
        }
        
        answer = await answerer.answer(
            "Compare the approaches",
            context,
            sample_papers[:2],
            depth="comparative"
        )
        
        assert answer == "Comparison between papers..."
        # Check that comparative prompt was used
        call_args = mock_llm.complete.call_args
        assert "Compare and contrast" in call_args[0][0]


class TestSynthesisOrchestrator:
    """Tests for SynthesisOrchestrator."""
    
    @pytest.mark.asyncio
    async def test_basic_synthesis(self, mock_db, mock_llm, mock_extractor, sample_papers):
        """Test basic synthesis flow."""
        # Mock LLM responses
        mock_llm.complete.return_value = {"content": "Synthesis answer"}
        
        orchestrator = SynthesisOrchestrator(mock_db, mock_llm, mock_extractor)
        
        result = await orchestrator.synthesize(
            question="What are the main contributions?",
            context_types="abstracts",
            depth="quick"
        )
        
        assert result["answer"] == "Synthesis answer"
        assert len(result["papers"]) > 0
        assert result["context_type"] == "abstracts"
        
    @pytest.mark.asyncio
    async def test_synthesis_with_tags(self, mock_db, mock_llm, mock_extractor, sample_papers):
        """Test synthesis with tag filtering."""
        mock_llm.complete.return_value = {"content": "NLP-focused synthesis"}
        
        orchestrator = SynthesisOrchestrator(mock_db, mock_llm, mock_extractor)
        
        result = await orchestrator.synthesize(
            question="What are the NLP techniques?",
            tags=["NLP"],
            context_types="abstracts"
        )
        
        # Should only select papers with NLP tag
        assert all("NLP" in p.tags for p in result["papers"])
        
    @pytest.mark.asyncio
    async def test_refine_synthesis(self, mock_db, mock_llm, mock_extractor, sample_papers):
        """Test refining an existing synthesis."""
        # Initial synthesis
        mock_llm.complete.return_value = {"content": "Initial answer"}
        
        orchestrator = SynthesisOrchestrator(mock_db, mock_llm, mock_extractor)
        
        await orchestrator.synthesize("Initial question")
        
        # Refine with new focus
        mock_llm.complete.return_value = {"content": "Refined answer"}
        
        result = await orchestrator.refine(
            "Focus on the implementation details",
            depth="thorough"
        )
        
        assert result["answer"] == "Refined answer"
        assert len(orchestrator.current_papers) > 0  # Papers should be preserved
        
    @pytest.mark.asyncio
    async def test_add_papers_to_session(self, mock_db, mock_llm, mock_extractor, sample_papers):
        """Test adding papers to existing session."""
        orchestrator = SynthesisOrchestrator(mock_db, mock_llm, mock_extractor)
        
        # Start with one paper
        orchestrator.current_papers = [sample_papers[0]]
        
        # Add another paper
        await orchestrator.add_papers(["paper2"])
        
        assert len(orchestrator.current_papers) == 2
        assert orchestrator.current_papers[1].paper_id == "paper2"
        
    @pytest.mark.asyncio
    async def test_change_context_depth(self, mock_db, mock_llm, mock_extractor, sample_papers):
        """Test changing context extraction depth."""
        orchestrator = SynthesisOrchestrator(mock_db, mock_llm, mock_extractor)
        
        # Set initial papers
        orchestrator.current_papers = sample_papers[:2]
        
        # Change from abstracts to key_points
        await orchestrator.change_context_depth("key_points")
        
        assert len(orchestrator.current_context) == 2
        # Verify extract_key_points was called
        assert mock_extractor.extract_key_points.called
        
    @pytest.mark.asyncio
    async def test_empty_library(self, mock_llm, mock_extractor):
        """Test synthesis with empty library."""
        # Mock empty database
        empty_db = MagicMock()
        empty_db.list_papers.return_value = []
        
        orchestrator = SynthesisOrchestrator(empty_db, mock_llm, mock_extractor)
        
        result = await orchestrator.synthesize("Any question")
        
        assert result["answer"] == "No relevant papers found in your library."
        assert result["papers"] == []


class TestSynthesisConversation:
    """Test SynthesisConversation class."""
    
    @pytest.mark.asyncio
    async def test_search_papers_no_autoselect(self, mock_db, mock_extractor, sample_papers):
        """Test that search_papers doesn't automatically select papers."""
        # Setup database to return papers
        mock_db.list_papers.return_value = sample_papers
        
        # Create mock LLM that returns valid JSON for semantic selection
        mock_llm = AsyncMock()
        mock_llm.complete.return_value = {"content": "[1, 3]"}  # Select papers 1 and 3
        
        # Create mock config
        mock_config = MagicMock()
        mock_config.user_prompt_path.exists.return_value = False
        
        # Create orchestrator and conversation
        orchestrator = SynthesisOrchestrator(mock_db, mock_llm, mock_extractor)
        conversation = SynthesisConversation(mock_db, mock_llm, orchestrator, mock_config)
        
        # Initially session should have no papers
        assert len(conversation.session.selected_papers) == 0
        
        # Search for papers
        result = await conversation._search_papers("transformers")
        
        # Verify papers were found but NOT auto-selected
        assert result["found"] > 0  # Papers should be found
        assert result["auto_selected"] is False  # Should not be auto-selected
        assert len(conversation.session.selected_papers) == 0  # Session should still be empty
        
    @pytest.mark.asyncio
    async def test_explicit_paper_selection(self, mock_db, mock_llm, mock_extractor, sample_papers):
        """Test that explicit paper selection still works."""
        # Setup database
        mock_db.list_papers.return_value = sample_papers
        mock_db.get_paper.side_effect = lambda pid: next((p for p in sample_papers if p.paper_id == pid), None)
        
        # Create mock config
        mock_config = MagicMock()
        mock_config.user_prompt_path.exists.return_value = False
        
        # Create orchestrator and conversation
        orchestrator = SynthesisOrchestrator(mock_db, mock_llm, mock_extractor)
        conversation = SynthesisConversation(mock_db, mock_llm, orchestrator, mock_config)
        
        # Initially session should have no papers
        assert len(conversation.session.selected_papers) == 0
        
        # Explicitly select papers
        result = await conversation._select_papers(["paper1", "paper2"], operation="set")
        
        # Verify papers were selected
        assert result["selected_count"] == 2
        assert len(conversation.session.selected_papers) == 2

    def test_get_tool_description_select_papers_with_titles(self, mock_db, mock_llm, mock_extractor, sample_papers):
        """Test that _get_tool_description shows paper titles for select_papers."""
        # Setup database
        mock_db.get_paper.side_effect = lambda pid: next((p for p in sample_papers if p.paper_id == pid), None)
        
        # Create mock config
        mock_config = MagicMock()
        mock_config.user_prompt_path.exists.return_value = False
        
        # Create orchestrator and conversation
        orchestrator = SynthesisOrchestrator(mock_db, mock_llm, mock_extractor)
        conversation = SynthesisConversation(mock_db, mock_llm, orchestrator, mock_config)
        
        # Test set operation with single paper
        description = conversation._get_tool_description(
            "select_papers", 
            {"paper_ids": ["paper1"], "operation": "set"}
        )
        assert "Deep Learning for NLP" in description
        assert "Set selection to 1 paper(s):" in description
        
        # Test add operation with multiple papers  
        description = conversation._get_tool_description(
            "select_papers", 
            {"paper_ids": ["paper1", "paper2"], "operation": "add"}
        )
        assert "Deep Learning for NLP" in description
        assert "Reinforcement Learning Survey" in description
        assert "Add 2 paper(s) to selection:" in description
        
        # Test remove operation
        description = conversation._get_tool_description(
            "select_papers", 
            {"paper_ids": ["paper3"], "operation": "remove"}
        )
        assert "Transformer Architecture" in description
        assert "Remove 1 paper(s) from selection:" in description
        
        # Test with more than 3 papers (should truncate and show "and X more")
        description = conversation._get_tool_description(
            "select_papers", 
            {"paper_ids": ["paper1", "paper2", "paper3", "paper1"], "operation": "set"}
        )
        assert "and 1 more" in description
        
        # Test with non-existent paper ID
        description = conversation._get_tool_description(
            "select_papers", 
            {"paper_ids": ["nonexistent"], "operation": "set"}
        )
        assert "ID:nonexist..." in description
