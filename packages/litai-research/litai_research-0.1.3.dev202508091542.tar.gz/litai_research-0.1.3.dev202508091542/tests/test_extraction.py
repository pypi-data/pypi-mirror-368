"""Tests for the extraction module."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from litai.extraction import PaperExtractor, KeyPoint
from litai.models import Extraction


@pytest.fixture
def mock_db():
    """Create a mock database."""
    db = MagicMock()
    db.get_extraction.return_value = None
    db.add_extraction.return_value = True
    return db


@pytest.fixture
def mock_llm():
    """Create a mock LLM client."""
    llm = MagicMock()
    llm.complete = AsyncMock()
    return llm


@pytest.fixture
def mock_pdf_processor():
    """Create a mock PDF processor."""
    pdf_processor = MagicMock()
    pdf_processor.process_paper = AsyncMock()
    return pdf_processor


@pytest.fixture
def extractor(mock_db, mock_llm, mock_pdf_processor):
    """Create a PaperExtractor instance with mocked dependencies."""
    return PaperExtractor(mock_db, mock_llm, mock_pdf_processor)


def test_chunk_text(extractor):
    """Test that text chunking works correctly."""
    # Test with short text that fits in one chunk
    short_text = "This is a short paragraph."
    chunks = extractor.chunk_text(short_text, max_tokens=100)
    assert len(chunks) == 1
    assert chunks[0] == short_text
    
    # Test with longer text that needs multiple chunks
    # Create text with clear paragraph boundaries
    long_text = "\n\n".join([f"Paragraph {i}. " * 50 for i in range(10)])
    chunks = extractor.chunk_text(long_text, max_tokens=100)
    assert len(chunks) > 1
    
    # Verify chunks don't exceed approximate word limit
    max_words = int(100 * 0.75)  # 75 words for 100 tokens
    for chunk in chunks:
        word_count = len(chunk.split())
        # Allow some margin for the chunking algorithm
        assert word_count <= max_words * 1.5


def test_parse_extraction_response(extractor):
    """Test parsing of LLM responses."""
    # Valid JSON response
    valid_response = '''Some preamble text
    [
        {
            "claim": "Test claim 1",
            "evidence": "Evidence for claim 1",
            "section": "Section 1"
        },
        {
            "claim": "Test claim 2",
            "evidence": "Evidence for claim 2",
            "section": "Section 2"
        }
    ]
    Some postamble text'''
    
    points = extractor._parse_extraction_response(valid_response)
    assert len(points) == 2
    assert points[0].claim == "Test claim 1"
    assert points[0].evidence == "Evidence for claim 1"
    assert points[0].section == "Section 1"
    
    # Invalid JSON
    invalid_response = "This is not JSON"
    points = extractor._parse_extraction_response(invalid_response)
    assert len(points) == 0
    
    # Missing required fields
    incomplete_response = '[{"claim": "Only claim"}]'
    points = extractor._parse_extraction_response(incomplete_response)
    assert len(points) == 0


def test_select_best_points(extractor):
    """Test deduplication and selection of best points."""
    # Create points with some duplicates
    points = [
        KeyPoint("Transformers are better than RNNs", "Evidence 1", "Section 1"),
        KeyPoint("Transformers outperform RNNs significantly", "Evidence 2", "Section 2"),
        KeyPoint("Self-attention enables parallelization", "Evidence 3", "Section 3"),
        KeyPoint("The model achieves state-of-the-art results", "Evidence 4", "Section 4"),
        KeyPoint("Training is more efficient", "Evidence 5", "Section 5"),
        KeyPoint("The model achieves SOTA performance", "Evidence 6", "Section 6"),
    ]
    
    # Select top 5
    selected = extractor._select_best_points(points, n=5)
    assert len(selected) <= 5
    
    # Should have deduplicated similar claims about transformers/RNNs and SOTA
    claim_texts = [p.claim for p in selected]
    assert len(set(claim_texts)) == len(claim_texts)  # All unique


@pytest.mark.asyncio
async def test_extract_key_points_cached(extractor, mock_db):
    """Test extraction when results are cached."""
    # Set up cached extraction
    cached_content = {
        "points": [
            {
                "claim": "Cached claim",
                "evidence": "Cached evidence",
                "section": "Cached section"
            }
        ]
    }
    cached_extraction = Extraction(
        paper_id="test123",
        extraction_type="key_points",
        content=cached_content,
        created_at=datetime.now()
    )
    mock_db.get_extraction.return_value = cached_extraction
    
    # Extract key points
    points = await extractor.extract_key_points("test123")
    
    # Should return cached results without calling LLM
    assert len(points) == 1
    assert points[0].claim == "Cached claim"
    extractor.llm.complete.assert_not_called()
    extractor.pdf_processor.process_paper.assert_not_called()


@pytest.mark.asyncio
async def test_extract_key_points_fresh(extractor, mock_db, mock_llm, mock_pdf_processor):
    """Test extraction when no cache exists."""
    # Set up mocks
    mock_db.get_extraction.return_value = None
    mock_pdf_processor.process_paper.return_value = "This is the paper text. It contains important findings."
    
    # Mock LLM response
    mock_llm.complete.return_value = {
        "content": '''[
            {
                "claim": "Important finding 1",
                "evidence": "Direct quote from paper",
                "section": "Results"
            }
        ]''',
        "usage": MagicMock()
    }
    
    # Extract key points
    points = await extractor.extract_key_points("test123")
    
    # Verify extraction flow
    assert len(points) == 1
    assert points[0].claim == "Important finding 1"
    
    # Verify components were called
    mock_pdf_processor.process_paper.assert_called_once_with("test123")
    mock_llm.complete.assert_called()
    mock_db.add_extraction.assert_called_once()
    
    # Verify extraction was cached
    saved_extraction = mock_db.add_extraction.call_args[0][0]
    assert saved_extraction.paper_id == "test123"
    assert saved_extraction.extraction_type == "key_points"
    assert len(saved_extraction.content["points"]) == 1


@pytest.mark.asyncio
async def test_extract_key_points_no_pdf(extractor, mock_db, mock_pdf_processor):
    """Test extraction when PDF processing fails."""
    # Set up mocks
    mock_db.get_extraction.return_value = None
    mock_pdf_processor.process_paper.return_value = None  # Failed to get PDF
    
    # Should raise ValueError
    with pytest.raises(ValueError, match="Could not extract text"):
        await extractor.extract_key_points("test123")


def test_create_extraction_prompt(extractor):
    """Test prompt creation."""
    text = "This is a sample paper text."
    prompt = extractor._create_extraction_prompt(text)
    
    # Verify prompt contains the text and instructions
    assert text in prompt
    assert "Extract" in prompt
    assert "JSON" in prompt
    assert "claim" in prompt
    assert "evidence" in prompt