"""Tests for natural language query handling in normal mode."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from litai.config import Config
from litai.database import Database
from litai.models import Paper
from litai.nl_handler import NaturalLanguageHandler


@pytest.fixture
def sample_papers():
    """Create sample papers for testing."""
    return [
        Paper(
            paper_id="attention2017",
            title="Attention Is All You Need",
            authors=["Vaswani", "Shazeer", "Parmar"],
            year=2017,
            abstract="The dominant sequence transduction models are based on complex recurrent or convolutional neural networks...",
            citation_count=50000,
            tags=["transformers", "attention", "NLP"],
        ),
        Paper(
            paper_id="bert2018",
            title="BERT: Pre-training of Deep Bidirectional Transformers",
            authors=["Devlin", "Chang"],
            year=2018,
            abstract="We introduce a new language representation model called BERT...",
            citation_count=40000,
            tags=["BERT", "NLP", "pretraining"],
        ),
        Paper(
            paper_id="gpt3_2020",
            title="Language Models are Few-Shot Learners",
            authors=["Brown", "Mann", "Ryder"],
            year=2020,
            abstract="Recent work has demonstrated substantial gains on many NLP tasks...",
            citation_count=10000,
            tags=["GPT", "few-shot", "language-models"],
        ),
    ]


@pytest.fixture
def mock_db(sample_papers):
    """Create mock database with papers."""
    db = MagicMock(spec=Database)
    db.list_papers.return_value = sample_papers
    db.count_papers.return_value = len(sample_papers)
    db.get_paper.side_effect = lambda pid: next((p for p in sample_papers if p.paper_id == pid), None)
    return db


@pytest.fixture
def mock_config():
    """Create mock configuration."""
    config = MagicMock(spec=Config)
    config.get_api_key.return_value = "test-api-key"
    return config


@pytest.fixture
def mock_llm_response():
    """Factory for creating mock LLM responses."""
    def _create_response(content="", tool_calls=None):
        response = {"content": content}
        if tool_calls:
            response["tool_calls"] = tool_calls
        return response
    return _create_response


class TestNaturalLanguageQueries:
    """Test natural language query understanding and routing."""
    
    @pytest.mark.asyncio
    async def test_search_intent_recognition(self, mock_db, mock_config, mock_llm_response):
        """Test that search queries are properly recognized and routed."""
        # Mock command handlers
        find_papers_handler = AsyncMock(return_value="Found 5 papers on transformers")
        command_handlers = {
            "find_papers": find_papers_handler,
        }
        
        # Create NL handler
        search_results = []
        nl_handler = NaturalLanguageHandler(mock_db, command_handlers, search_results, mock_config)
        
        # Mock LLM to recognize search intent
        tool_call = MagicMock()
        tool_call.id = "call_1"
        tool_call.name = "find_papers"
        tool_call.arguments = {"query": "transformers"}
        
        nl_handler.llm_client.complete = AsyncMock(side_effect=[
            mock_llm_response(content="I'll search for papers about transformers.", tool_calls=[tool_call]),
            mock_llm_response(content="I found 5 papers about transformers in the literature."),
        ])
        
        # Test various search queries
        test_queries = [
            "Find papers about transformers",
            "Search for attention mechanisms",
            "Show me research on BERT",
            "What papers exist on few-shot learning?",
        ]
        
        for query in test_queries:
            await nl_handler.handle_query(query)
            
            # Verify the find_papers tool was called
            assert find_papers_handler.called
            find_papers_handler.reset_mock()
    
    @pytest.mark.asyncio
    async def test_add_paper_intent(self, mock_db, mock_config, mock_llm_response):
        """Test that add paper requests are properly handled."""
        add_paper_handler = MagicMock()
        command_handlers = {
            "add_paper": add_paper_handler,
        }
        
        # Set up search results
        search_results = [
            Paper(paper_id="test1", title="Test Paper 1", authors=["Author 1"], year=2023),
            Paper(paper_id="test2", title="Test Paper 2", authors=["Author 2"], year=2023),
        ]
        
        nl_handler = NaturalLanguageHandler(mock_db, command_handlers, search_results, mock_config)
        
        # Mock LLM to recognize add intent
        tool_call = MagicMock()
        tool_call.id = "call_2"
        tool_call.name = "add_paper"
        tool_call.arguments = {"paper_numbers": "1,2"}
        
        nl_handler.llm_client.complete = AsyncMock(side_effect=[
            mock_llm_response(content="I'll add those papers to your collection.", tool_calls=[tool_call]),
            mock_llm_response(content="Successfully added 2 papers to your collection."),
        ])
        
        # Test add queries
        test_queries = [
            "Add the first two papers to my collection",
            "Save papers 1 and 2",
            "Add 'Attention Is All You Need' to my library",
        ]
        
        for query in test_queries[:1]:  # Test at least one
            await nl_handler.handle_query(query)
            assert add_paper_handler.called
    
    @pytest.mark.asyncio
    async def test_list_papers_intent(self, mock_db, mock_config, mock_llm_response):
        """Test that list papers requests work correctly."""
        list_handler = MagicMock(return_value="Listed 3 papers in collection")
        command_handlers = {
            "list_papers": list_handler,
        }
        
        nl_handler = NaturalLanguageHandler(mock_db, command_handlers, [], mock_config)
        
        # Mock LLM to recognize list intent
        tool_call = MagicMock()
        tool_call.id = "call_3"
        tool_call.name = "list_papers"
        tool_call.arguments = {"page": 1}
        
        nl_handler.llm_client.complete = AsyncMock(side_effect=[
            mock_llm_response(content="Let me show you your paper collection.", tool_calls=[tool_call]),
            mock_llm_response(content="You have 3 papers in your collection."),
        ])
        
        # Test list queries
        test_queries = [
            "Show me my papers",
            "What's in my collection?",
            "List all papers I've saved",
        ]
        
        for query in test_queries[:1]:
            await nl_handler.handle_query(query)
            assert list_handler.called
    
    @pytest.mark.asyncio
    async def test_tag_management_intent(self, mock_db, mock_config, mock_llm_response):
        """Test tag-related natural language queries."""
        tag_handler = MagicMock()
        list_tags_handler = MagicMock()
        command_handlers = {
            "handle_tag_command": tag_handler,
            "list_tags": list_tags_handler,
        }
        
        nl_handler = NaturalLanguageHandler(mock_db, command_handlers, [], mock_config)
        
        # Test adding tags
        tool_call = MagicMock()
        tool_call.id = "call_4"
        tool_call.name = "manage_paper_tags"
        tool_call.arguments = {"paper_number": 1, "add_tags": "deep-learning,transformers"}
        
        nl_handler.llm_client.complete = AsyncMock(side_effect=[
            mock_llm_response(content="I'll add those tags.", tool_calls=[tool_call]),
            mock_llm_response(content="Tags added successfully."),
        ])
        
        await nl_handler.handle_query("Add tags deep-learning and transformers to paper 1")
        assert tag_handler.called
    
    @pytest.mark.asyncio
    async def test_complex_multi_step_query(self, mock_db, mock_config, mock_llm_response):
        """Test handling of complex queries that require multiple steps."""
        find_handler = AsyncMock(return_value="Found 3 papers")
        add_handler = MagicMock()
        command_handlers = {
            "find_papers": find_handler,
            "add_paper": add_handler,
        }
        
        search_results = []
        nl_handler = NaturalLanguageHandler(mock_db, command_handlers, search_results, mock_config)
        
        # First call: search
        search_call = MagicMock()
        search_call.id = "call_5"
        search_call.name = "find_papers"
        search_call.arguments = {"query": "vision transformers"}
        
        # Second call: add
        add_call = MagicMock()
        add_call.id = "call_6"
        add_call.name = "add_paper"
        add_call.arguments = {"paper_numbers": "1,2,3"}
        
        nl_handler.llm_client.complete = AsyncMock(side_effect=[
            mock_llm_response(content="I'll search for vision transformer papers first.", tool_calls=[search_call]),
            mock_llm_response(content="Found 3 papers. Now I'll add them to your collection.", tool_calls=[add_call]),
            mock_llm_response(content="Successfully found and added 3 vision transformer papers."),
        ])
        
        await nl_handler.handle_query("Find papers on vision transformers and add them all to my collection")
        
        assert find_handler.called
        assert add_handler.called
    
    @pytest.mark.asyncio
    async def test_conversation_context_maintenance(self, mock_db, mock_config, mock_llm_response):
        """Test that conversation context is maintained across queries."""
        list_handler = MagicMock(return_value="Listed papers with transformers tag")
        command_handlers = {
            "list_papers": list_handler,
        }
        
        nl_handler = NaturalLanguageHandler(mock_db, command_handlers, [], mock_config)
        
        # First query
        tool_call1 = MagicMock()
        tool_call1.id = "call_7"
        tool_call1.name = "list_papers_by_tag"
        tool_call1.arguments = {"tag": "transformers"}
        
        nl_handler.llm_client.complete = AsyncMock(side_effect=[
            mock_llm_response(content="Showing papers tagged with transformers.", tool_calls=[tool_call1]),
            mock_llm_response(content="Found 2 papers with the transformers tag."),
        ])
        
        await nl_handler.handle_query("Show me papers about transformers")
        
        # Verify conversation has the right messages
        messages = nl_handler.conversation.messages
        assert len(messages) > 0
        assert any("transformers" in str(m) for m in messages)
        
        # Second query referring to previous context
        nl_handler.llm_client.complete = AsyncMock(
            return_value=mock_llm_response(content="The first paper 'Attention Is All You Need' introduced the transformer architecture in 2017.")
        )
        
        await nl_handler.handle_query("Tell me more about the first one")
        
        # Verify context is maintained
        assert len(nl_handler.conversation.messages) > 2
    
    @pytest.mark.asyncio
    async def test_error_handling(self, mock_db, mock_config):
        """Test graceful error handling for various failure scenarios."""
        command_handlers = {}
        nl_handler = NaturalLanguageHandler(mock_db, command_handlers, [], mock_config)
        
        # Test LLM failure
        nl_handler.llm_client.complete = AsyncMock(side_effect=Exception("API Error"))
        
        # Should handle error gracefully
        with patch("litai.nl_handler.output.error") as mock_error:
            await nl_handler.handle_query("Find papers")
            mock_error.assert_called_once()
            assert "Error processing query" in str(mock_error.call_args)
    
    @pytest.mark.asyncio 
    async def test_tool_confirmation_flow(self, mock_db, mock_config, mock_llm_response):
        """Test user confirmation before tool execution."""
        find_handler = AsyncMock(return_value="Found papers")
        command_handlers = {
            "find_papers": find_handler,
        }
        
        nl_handler = NaturalLanguageHandler(mock_db, command_handlers, [], mock_config)
        
        tool_call = MagicMock()
        tool_call.id = "call_8"
        tool_call.name = "find_papers"
        tool_call.arguments = {"query": "test"}
        
        nl_handler.llm_client.complete = AsyncMock(side_effect=[
            mock_llm_response(content="Searching...", tool_calls=[tool_call]),
            mock_llm_response(content="Search complete."),
        ])
        
        # Mock user declining confirmation
        with patch("litai.nl_handler.Prompt.ask", return_value="no"):
            await nl_handler.handle_query("Find papers")
            
            # Handler should not be called if user declines
            assert not find_handler.called
        
        # Mock user accepting confirmation
        with patch("litai.nl_handler.Prompt.ask", return_value="yes"):
            await nl_handler.handle_query("Find papers")
            
            # Handler should be called if user accepts
            assert find_handler.called


class TestQueryPatterns:
    """Test various natural language query patterns."""
    
    @pytest.mark.asyncio
    async def test_ambiguous_queries(self, mock_db, mock_config, mock_llm_response):
        """Test handling of ambiguous queries that need clarification."""
        command_handlers = {}
        nl_handler = NaturalLanguageHandler(mock_db, command_handlers, [], mock_config)
        
        # LLM should ask for clarification
        nl_handler.llm_client.complete = AsyncMock(
            return_value=mock_llm_response(
                content="Could you clarify what you mean by 'the paper'? Are you referring to a specific paper in your collection or search results?"
            )
        )
        
        response = await nl_handler.handle_query("Add the paper")
        
        # Should get clarification request
        messages = nl_handler.conversation.messages
        assert any("clarify" in msg.get("content", "").lower() for msg in messages)
    
    @pytest.mark.asyncio
    async def test_compound_queries(self, mock_db, mock_config, mock_llm_response):
        """Test queries with multiple actions."""
        find_handler = AsyncMock(return_value="Found papers")
        add_handler = MagicMock()
        tag_handler = MagicMock()
        
        command_handlers = {
            "find_papers": find_handler,
            "add_paper": add_handler,
            "handle_tag_command": tag_handler,
        }
        
        nl_handler = NaturalLanguageHandler(mock_db, command_handlers, [], mock_config)
        
        # Multiple tool calls in sequence
        calls = [
            MagicMock(id="1", name="find_papers", arguments={"query": "BERT"}),
            MagicMock(id="2", name="add_paper", arguments={"paper_numbers": "1"}),
            MagicMock(id="3", name="manage_paper_tags", arguments={"paper_number": 1, "add_tags": "important"}),
        ]
        
        nl_handler.llm_client.complete = AsyncMock(side_effect=[
            mock_llm_response(content="I'll find BERT papers, add the first one, and tag it.", tool_calls=calls),
            mock_llm_response(content="Done! Found BERT papers, added the first one, and tagged it as important."),
        ])
        
        with patch("litai.nl_handler.Prompt.ask", return_value="yes"):
            await nl_handler.handle_query("Find BERT papers, add the first one, and tag it as important")
        
        assert find_handler.called
        assert add_handler.called
        assert tag_handler.called
    
    @pytest.mark.asyncio
    async def test_contextual_references(self, mock_db, mock_config, mock_llm_response, sample_papers):
        """Test queries that reference previous context."""
        mock_db.list_papers.return_value = sample_papers[:2]
        
        list_handler = MagicMock(return_value="Listed 2 papers")
        command_handlers = {
            "list_papers": list_handler,
        }
        
        nl_handler = NaturalLanguageHandler(mock_db, command_handlers, [], mock_config)
        
        # First query to establish context
        tool_call = MagicMock(id="1", name="list_papers", arguments={"page": 1})
        nl_handler.llm_client.complete = AsyncMock(side_effect=[
            mock_llm_response(content="Here are your papers.", tool_calls=[tool_call]),
            mock_llm_response(content="You have 2 papers: 'Attention Is All You Need' and 'BERT'."),
        ])
        
        with patch("litai.nl_handler.Prompt.ask", return_value="yes"):
            await nl_handler.handle_query("Show my papers")
        
        # Follow-up query using context
        nl_handler.llm_client.complete = AsyncMock(
            return_value=mock_llm_response(
                content="The BERT paper by Devlin and Chang (2018) has 40,000 citations."
            )
        )
        
        await nl_handler.handle_query("How many citations does the BERT paper have?")
        
        # Should answer using context
        messages = nl_handler.conversation.messages
        assert any("40,000" in str(msg.get("content", "")) or "40000" in str(msg.get("content", "")) for msg in messages)