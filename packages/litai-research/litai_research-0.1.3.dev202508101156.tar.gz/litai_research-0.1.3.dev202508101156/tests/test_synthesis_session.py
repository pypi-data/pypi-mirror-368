"""Tests for synthesis session management."""

import pytest
from datetime import datetime
from litai.synthesis_session import SynthesisSession, SynthesisSessionState
from litai.models import Paper
from litai.synthesis import SynthesisResult, RelevantPaper


@pytest.fixture
def sample_papers():
    """Create sample papers for testing."""
    return [
        Paper(
            paper_id="paper1",
            title="First Paper",
            authors=["Author A"],
            year=2023,
            abstract="Abstract 1",
            tags=["ml", "nlp"]
        ),
        Paper(
            paper_id="paper2", 
            title="Second Paper",
            authors=["Author B"],
            year=2024,
            abstract="Abstract 2",
            tags=["cv"]
        ),
        Paper(
            paper_id="paper3",
            title="Third Paper",
            authors=["Author C"],
            year=2024,
            abstract="Abstract 3",
            tags=["ml", "rl"]
        )
    ]


@pytest.fixture
def session():
    """Create a fresh synthesis session."""
    return SynthesisSession()


class TestSynthesisSession:
    """Test synthesis session management."""
    
    def test_initial_state(self, session):
        """Test initial session state."""
        assert session.selected_papers == []
        assert session.current_context == {}
        assert session.context_type == "abstracts"
        assert session.synthesis_history == []
        assert session.current_question == ""
        assert isinstance(session.created_at, datetime)
        assert isinstance(session.updated_at, datetime)
    
    @pytest.mark.asyncio
    async def test_update_papers_replace(self, session, sample_papers):
        """Test replacing all papers."""
        result = await session.update_papers(papers=sample_papers[:2])
        
        assert len(result) == 2
        assert session.selected_papers == sample_papers[:2]
        assert session._papers_modified is True
    
    @pytest.mark.asyncio
    async def test_update_papers_add(self, session, sample_papers):
        """Test adding papers to existing selection."""
        # Start with first paper
        await session.update_papers(papers=[sample_papers[0]])
        
        # Add second paper
        result = await session.update_papers(add_papers=[sample_papers[1]])
        
        assert len(result) == 2
        assert sample_papers[0] in session.selected_papers
        assert sample_papers[1] in session.selected_papers
    
    @pytest.mark.asyncio
    async def test_update_papers_avoid_duplicates(self, session, sample_papers):
        """Test that duplicate papers are not added."""
        await session.update_papers(papers=sample_papers[:2])
        
        # Try to add first paper again
        result = await session.update_papers(add_papers=[sample_papers[0]])
        
        assert len(result) == 2  # Should still be 2, not 3
    
    @pytest.mark.asyncio  
    async def test_update_papers_remove(self, session, sample_papers):
        """Test removing papers by ID."""
        await session.update_papers(papers=sample_papers)
        
        # Remove middle paper
        result = await session.update_papers(remove_paper_ids=["paper2"])
        
        assert len(result) == 2
        assert sample_papers[0] in session.selected_papers
        assert sample_papers[1] not in session.selected_papers
        assert sample_papers[2] in session.selected_papers
    
    @pytest.mark.asyncio
    async def test_change_context_depth(self, session):
        """Test changing context extraction depth."""
        result = await session.change_context_depth("key_points")
        
        assert result == "key_points"
        assert session.context_type == "key_points"
        assert session._context_modified is True
    
    @pytest.mark.asyncio
    async def test_change_context_depth_with_sections(self, session):
        """Test changing to sections context with specific sections."""
        result = await session.change_context_depth(
            "sections", 
            sections=["methods", "results"]
        )
        
        assert result == "sections"
        assert session.context_type == "sections"
        assert session._preferred_sections == ["methods", "results"]
    
    @pytest.mark.asyncio
    async def test_refine_synthesis(self, session, sample_papers):
        """Test refining synthesis with feedback."""
        await session.update_papers(papers=sample_papers)
        session.current_question = "What are the key findings?"
        
        # Add a synthesis result to history
        result = SynthesisResult(
            question="What are the key findings?",
            synthesis="Initial synthesis text",
            relevant_papers=[]
        )
        session.add_synthesis_result(result)
        
        # Refine with feedback
        refinement = await session.refine_synthesis(
            feedback="Focus more on methodology",
            new_question="How do the methods compare?"
        )
        
        assert refinement["feedback"] == "Focus more on methodology"
        assert refinement["question"] == "How do the methods compare?"
        assert refinement["papers"] == sample_papers
        assert refinement["previous_synthesis"] == "Initial synthesis text"
        assert session.current_question == "How do the methods compare?"
    
    def test_add_synthesis_result(self, session):
        """Test adding synthesis results to history."""
        result = SynthesisResult(
            question="Test question",
            synthesis="Test synthesis",
            relevant_papers=[]
        )
        
        session.add_synthesis_result(result)
        
        assert len(session.synthesis_history) == 1
        assert session.synthesis_history[0] == result
        assert session.current_question == "Test question"
    
    def test_context_caching(self, session):
        """Test context caching functionality."""
        # Cache some context
        session.cache_context("paper1", "Cached context for paper1")
        
        # Retrieve cached context
        cached = session.get_cached_context("paper1")
        assert cached == "Cached context for paper1"
        
        # Non-existent cache
        assert session.get_cached_context("paper2") is None
        
        # Cache key generation
        key = session.get_context_cache_key("paper1")
        assert key == ("paper1", "abstracts")
    
    def test_needs_context_update(self, session):
        """Test context update detection."""
        assert not session.needs_context_update()
        
        session._papers_modified = True
        assert session.needs_context_update()
        
        session.mark_context_updated()
        assert not session.needs_context_update()
        
        session._context_modified = True
        assert session.needs_context_update()
    
    def test_get_state(self, session, sample_papers):
        """Test getting immutable state snapshot."""
        session.selected_papers = sample_papers
        session.current_question = "Test question"
        
        state = session.get_state()
        
        assert isinstance(state, SynthesisSessionState)
        assert state.selected_papers == sample_papers
        assert state.current_question == "Test question"
        assert state.context_type == "abstracts"
        
        # Verify it's a copy
        state.selected_papers.clear()
        assert len(session.selected_papers) == 3
    
    def test_restore_state(self, session, sample_papers):
        """Test restoring from saved state."""
        # Create a state
        state = SynthesisSessionState(
            selected_papers=sample_papers,
            current_question="Restored question",
            context_type="full_text"
        )
        
        # Restore it
        session.restore_state(state)
        
        assert session.selected_papers == sample_papers
        assert session.current_question == "Restored question"
        assert session.context_type == "full_text"
        assert not session._papers_modified
        assert not session._context_modified
    
    def test_clear_session(self, session, sample_papers):
        """Test clearing session state."""
        # Populate session
        session.selected_papers = sample_papers
        session.current_question = "Test"
        session.context_type = "key_points"
        session._papers_modified = True
        
        # Clear it
        session.clear()
        
        assert session.selected_papers == []
        assert session.current_context == {}
        assert session.context_type == "abstracts"
        assert session.current_question == ""
        assert not session._papers_modified
        assert not session._context_modified
    
    def test_get_summary(self, session, sample_papers):
        """Test getting session summary."""
        session.selected_papers = sample_papers
        session.current_question = "What are the trends?"
        
        # Add some synthesis history
        for i in range(3):
            result = SynthesisResult(
                question=f"Question {i}",
                synthesis=f"Synthesis {i}",
                relevant_papers=[]
            )
            session.add_synthesis_result(result)
        
        summary = session.get_summary()
        
        assert summary["papers_count"] == 3
        assert len(summary["paper_titles"]) == 3
        assert summary["paper_titles"][0] == "First Paper"
        assert summary["context_type"] == "abstracts"
        assert summary["current_question"] == "Question 2"  # Last one added
        assert summary["synthesis_count"] == 3
        assert "session_duration_minutes" in summary
        assert "last_updated" in summary