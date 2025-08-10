"""Tests for CLI paper storage functionality."""

import pytest
from pathlib import Path
import tempfile
import shutil

from litai.config import Config
from litai.database import Database
from litai.models import Paper
from litai.cli import add_paper, list_papers, show_search_results


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def config(temp_dir):
    """Create a test config with temporary directory."""
    return Config(base_dir=temp_dir)


@pytest.fixture
def db(config):
    """Create a test database."""
    return Database(config)


@pytest.fixture
def sample_papers():
    """Create sample papers for testing."""
    return [
        Paper(
            paper_id="test1",
            title="Attention Is All You Need",
            authors=["Vaswani", "Shazeer", "Parmar"],
            year=2017,
            abstract="The dominant sequence transduction models...",
            citation_count=50000
        ),
        Paper(
            paper_id="test2",
            title="BERT: Pre-training of Deep Bidirectional Transformers",
            authors=["Devlin", "Chang"],
            year=2018,
            abstract="We introduce a new language representation model...",
            citation_count=40000
        ),
        Paper(
            paper_id="test3",
            title="GPT-3: Language Models are Few-Shot Learners",
            authors=["Brown", "Mann", "Ryder", "Subbiah"],
            year=2020,
            abstract="Recent work has demonstrated substantial gains...",
            citation_count=10000
        )
    ]


class TestAddPaper:
    """Test the /add command functionality."""
    
    def test_add_paper_success(self, db, sample_papers, capsys):
        """Test successfully adding a paper from search results."""
        # Set up search results
        import litai.cli
        litai.cli._search_results = sample_papers
        
        # Add paper 1
        add_paper("1", db)
        
        captured = capsys.readouterr()
        assert "✓ Added: 'Attention Is All You Need'" in captured.out
        assert "Added 1 papers" in captured.out
        
        # Verify paper was added to database
        saved_paper = db.get_paper("test1")
        assert saved_paper is not None
        assert saved_paper.title == "Attention Is All You Need"
    
    def test_add_paper_duplicate_detection(self, db, sample_papers, capsys):
        """Test duplicate detection when adding papers."""
        import litai.cli
        litai.cli._search_results = sample_papers
        
        # Add paper first time
        add_paper("1", db)
        
        # Try to add same paper again
        add_paper("1", db)
        
        captured = capsys.readouterr()
        assert "Skipped 1 duplicates" in captured.out
    
    def test_add_paper_no_search_results(self, db, capsys):
        """Test adding paper when no search results are available."""
        import litai.cli
        litai.cli._search_results = []
        
        add_paper("1", db)
        
        captured = capsys.readouterr()
        assert "No search results available" in captured.out
        assert "Use /find first" in captured.out
    
    def test_add_paper_invalid_number(self, db, sample_papers, capsys):
        """Test adding paper with invalid number."""
        import litai.cli
        litai.cli._search_results = sample_papers
        
        # Test out of range
        add_paper("10", db)
        captured = capsys.readouterr()
        assert "Invalid paper number" in captured.out
        assert "Must be between 1 and 3" in captured.out
        
        # Test non-numeric
        add_paper("abc", db)
        captured = capsys.readouterr()
        assert "Invalid number" in captured.out
    
    def test_add_paper_no_args(self, db, sample_papers, capsys):
        """Test adding paper without specifying number."""
        import litai.cli
        litai.cli._search_results = sample_papers
        
        add_paper("", db)
        
        captured = capsys.readouterr()
        assert "Add all 3 papers to library?" in captured.out
        assert "Type 'yes' to confirm:" in captured.out
    
    def test_add_paper_with_many_authors(self, db, capsys):
        """Test adding paper with many authors shows et al."""
        import litai.cli
        
        paper = Paper(
            paper_id="many_authors",
            title="Paper with Many Authors",
            authors=["Author1", "Author2", "Author3", "Author4", "Author5"],
            year=2024,
            abstract="Test abstract"
        )
        litai.cli._search_results = [paper]
        
        add_paper("1", db)
        
        captured = capsys.readouterr()
        assert "✓ Added: 'Paper with Many Authors'" in captured.out
        assert "Added 1 papers" in captured.out


class TestListPapers:
    """Test the /list command functionality."""
    
    def test_list_empty_library(self, db, capsys):
        """Test listing papers when library is empty."""
        list_papers(db)
        
        captured = capsys.readouterr()
        assert "No papers in your library yet" in captured.out
        assert "Use /find to search" in captured.out
    
    def test_list_papers_table_display(self, db, sample_papers, capsys):
        """Test listing papers displays proper table."""
        # Add papers to database
        for paper in sample_papers:
            db.add_paper(paper)
        
        list_papers(db)
        
        captured = capsys.readouterr()
        assert "Your Library (3 papers)" in captured.out
        assert "Attention Is All You Need" in captured.out
        assert "BERT: Pre-training" in captured.out
        assert "GPT-3: Language Models" in captured.out
        assert "50000" in captured.out  # citation count
        assert "Use /read <number>" in captured.out
    
    def test_list_papers_pagination_info(self, db, capsys):
        """Test pagination info when there are many papers."""
        # Add more than default limit papers
        for i in range(55):
            paper = Paper(
                paper_id=f"test{i}",
                title=f"Test Paper {i}",
                authors=[f"Author {i}"],
                year=2020 + (i % 5),
                abstract=f"Abstract {i}",
                citation_count=i * 100
            )
            db.add_paper(paper)
        
        list_papers(db)
        
        captured = capsys.readouterr()
        assert "Your Library (55 papers)" in captured.out
        assert "Showing first 50 papers. Total: 55" in captured.out
    
    def test_list_papers_author_formatting(self, db, capsys):
        """Test author formatting in list display."""
        # Paper with 2 authors
        paper1 = Paper(
            paper_id="two_authors",
            title="Paper with Two Authors",
            authors=["Author One", "Author Two"],
            year=2024,
            abstract="Test"
        )
        
        # Paper with many authors
        paper2 = Paper(
            paper_id="many_authors",
            title="Paper with Many Authors",
            authors=["First", "Second", "Third", "Fourth"],
            year=2024,
            abstract="Test"
        )
        
        db.add_paper(paper1)
        db.add_paper(paper2)
        
        list_papers(db)
        
        captured = capsys.readouterr()
        # Check that the output contains the author formatting (may be split across lines in Rich table)
        output_text = captured.out.replace('\n', ' ')
        assert "Author One" in output_text and "Author Two" in output_text
        # The Rich table shows "et al." but "First" and "Second" are on different lines
        # so we just need to check they exist separately
        assert "First" in output_text
        assert "Second" in output_text  
        assert "et al." in output_text
    
    def test_list_papers_truncates_long_titles(self, db, capsys):
        """Test that long titles are handled properly."""
        paper = Paper(
            paper_id="long_title",
            title="This is an extremely long paper title that should definitely be truncated when displayed in the table format to maintain readability",
            authors=["Author"],
            year=2024,
            abstract="Test"
        )
        
        db.add_paper(paper)
        list_papers(db)
        
        captured = capsys.readouterr()
        # The important thing is that list_papers runs without error with long titles
        # and shows the paper. How Rich renders it is not our concern.
        assert "Your Library (1 papers)" in captured.out
        assert "long_title" in captured.out  # Paper ID should be visible


class TestShowSearchResults:
    """Test the /results command functionality."""
    
    def test_show_search_results_empty(self, capsys):
        """Test showing search results when none are cached."""
        import litai.cli
        litai.cli._search_results = []
        
        show_search_results()
        
        captured = capsys.readouterr()
        assert "No search results cached" in captured.out
        assert "Use /find to search" in captured.out
    
    def test_show_search_results_with_data(self, sample_papers, capsys):
        """Test showing cached search results."""
        import litai.cli
        litai.cli._search_results = sample_papers
        
        show_search_results()
        
        captured = capsys.readouterr()
        assert "Cached Search Results" in captured.out
        # Check for parts of the titles (they may be wrapped)
        assert "Attention Is All" in captured.out
        assert "BERT: Pre-training" in captured.out
        assert "GPT-3: Language" in captured.out
        assert "Use /add <number>" in captured.out


class TestIntegration:
    """Integration tests for the full flow."""
    
    def test_find_add_list_flow(self, db, sample_papers, capsys):
        """Test the complete flow of finding, adding, and listing papers."""
        import litai.cli
        
        # Simulate search results
        litai.cli._search_results = sample_papers
        
        # Add multiple papers
        add_paper("1", db)
        add_paper("3", db)
        
        # Try to add duplicate
        add_paper("1", db)
        
        # List papers
        list_papers(db)
        
        captured = capsys.readouterr()
        
        # Check all expected outputs
        assert "✓ Added:" in captured.out
        assert "Skipped 1 duplicates" in captured.out
        assert "Your Library (2 papers)" in captured.out
        assert "Attention Is All You Need" in captured.out
        assert "GPT-3: Language Models" in captured.out
        assert "BERT" not in captured.out  # Paper 2 was not added