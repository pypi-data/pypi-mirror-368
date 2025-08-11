"""Tests for configuration management."""

import pytest
from pathlib import Path
import tempfile
import shutil

from litai.config import Config


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


class TestConfig:
    """Test configuration management."""
    
    def test_default_base_dir(self):
        """Test that default base directory is ~/.litai."""
        config = Config()
        assert config.base_dir == Path.home() / ".litai"
    
    def test_custom_base_dir(self, temp_dir):
        """Test using a custom base directory."""
        config = Config(base_dir=temp_dir)
        assert config.base_dir == temp_dir
    
    def test_directories_created(self, temp_dir):
        """Test that all required directories are created."""
        config = Config(base_dir=temp_dir)
        
        # Check all directories exist
        assert config.base_dir.exists()
        assert config.pdfs_dir.exists()
        assert config.db_dir.exists()
        
        # Check they are directories
        assert config.base_dir.is_dir()
        assert config.pdfs_dir.is_dir()
        assert config.db_dir.is_dir()
    
    def test_pdfs_dir_path(self, temp_dir):
        """Test PDFs directory path."""
        config = Config(base_dir=temp_dir)
        assert config.pdfs_dir == temp_dir / "pdfs"
    
    def test_db_dir_path(self, temp_dir):
        """Test database directory path."""
        config = Config(base_dir=temp_dir)
        assert config.db_dir == temp_dir / "db"
    
    def test_db_path(self, temp_dir):
        """Test database file path."""
        config = Config(base_dir=temp_dir)
        assert config.db_path == temp_dir / "db" / "litai.db"
    
    def test_pdf_path(self, temp_dir):
        """Test PDF path generation."""
        config = Config(base_dir=temp_dir)
        
        paper_id = "test123"
        pdf_path = config.pdf_path(paper_id)
        
        assert pdf_path == temp_dir / "pdfs" / "test123.pdf"
        assert pdf_path.parent.exists()  # Directory should exist
    
    def test_config_path(self, temp_dir):
        """Test configuration file path."""
        config = Config(base_dir=temp_dir)
        assert config.config_path == temp_dir / "config.json"
    
    def test_load_config_empty(self, temp_dir):
        """Test loading config when file doesn't exist."""
        config = Config(base_dir=temp_dir)
        loaded = config.load_config()
        assert loaded == {}
    
    def test_save_and_load_config(self, temp_dir):
        """Test saving and loading configuration."""
        config = Config(base_dir=temp_dir)
        
        test_config = {
            "llm": {
                "provider": "openai",
                "model": "gpt-4",
                "api_key_env": "MY_API_KEY"
            }
        }
        
        config.save_config(test_config)
        loaded = config.load_config()
        
        assert loaded == test_config
        assert config.config_path.exists()
    
    def test_update_config(self, temp_dir):
        """Test updating configuration values."""
        config = Config(base_dir=temp_dir)
        
        # Set initial value
        config.update_config("llm.provider", "openai")
        loaded = config.load_config()
        assert loaded["llm"]["provider"] == "openai"
        
        # Update existing value
        config.update_config("llm.provider", "anthropic")
        loaded = config.load_config()
        assert loaded["llm"]["provider"] == "anthropic"
        
        # Add nested value
        config.update_config("llm.model", "claude-3")
        loaded = config.load_config()
        assert loaded["llm"]["model"] == "claude-3"
        assert loaded["llm"]["provider"] == "anthropic"
    
    def test_update_config_nested_creation(self, temp_dir):
        """Test that update_config creates nested structures."""
        config = Config(base_dir=temp_dir)
        
        # Update deeply nested value on empty config
        config.update_config("app.features.enabled", True)
        loaded = config.load_config()
        
        assert loaded["app"]["features"]["enabled"] is True
    
    def test_get_vi_mode_default(self, temp_dir):
        """Test get_vi_mode returns False by default."""
        config = Config(base_dir=temp_dir)
        assert config.get_vi_mode() is False
    
    def test_get_vi_mode_set_true(self, temp_dir):
        """Test get_vi_mode returns True when set."""
        config = Config(base_dir=temp_dir)
        config.update_config("editor.vi_mode", True)
        assert config.get_vi_mode() is True
    
    def test_get_vi_mode_set_false(self, temp_dir):
        """Test get_vi_mode returns False when explicitly set."""
        config = Config(base_dir=temp_dir)
        config.update_config("editor.vi_mode", False)
        assert config.get_vi_mode() is False
    
    def test_user_prompt_path(self, temp_dir):
        """Test user prompt file path."""
        config = Config(base_dir=temp_dir)
        assert config.user_prompt_path == temp_dir / "user_prompt.txt"