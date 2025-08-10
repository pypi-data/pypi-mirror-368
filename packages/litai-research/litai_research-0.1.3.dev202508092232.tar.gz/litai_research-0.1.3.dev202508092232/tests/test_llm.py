"""Tests for LLM client functionality."""

import os
import pytest
from unittest.mock import patch
import tempfile
from pathlib import Path

from litai.llm import LLMClient
from litai.config import Config


class TestLLMClient:
    """Test the LLMClient class."""
    
    def test_no_api_key_raises_error(self):
        """Test that missing API keys raise an error."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="No API key found"):
                LLMClient()
    
    def test_openai_provider_detection(self):
        """Test OpenAI provider is detected when API key is set."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            with patch("litai.llm.AsyncOpenAI"):
                client = LLMClient()
                assert client.provider == "openai"
                assert client.model == "gpt-4.1-nano-2025-04-14"
    
    def test_anthropic_provider_detection(self):
        """Test Anthropic provider is detected when API key is set."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}, clear=True):
            with patch("litai.llm.AsyncAnthropic"):
                client = LLMClient()
                assert client.provider == "anthropic"
                assert client.model == "claude-3-sonnet-20240229"
    
    def test_openai_preferred_when_both_keys_present(self):
        """Test OpenAI is preferred when both API keys are present."""
        with patch.dict(os.environ, {
            "OPENAI_API_KEY": "openai-key",
            "ANTHROPIC_API_KEY": "anthropic-key"
        }):
            with patch("litai.llm.AsyncOpenAI"):
                client = LLMClient()
                assert client.provider == "openai"
    
    def test_token_counting(self):
        """Test token counting produces reasonable results."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            with patch("litai.llm.AsyncOpenAI"):
                client = LLMClient()
                
                # Test various text lengths
                assert client._count_tokens("") == 0
                assert client._count_tokens("Hello") > 0
                assert client._count_tokens("Hello") < client._count_tokens("Hello, world!")
                
                # A typical sentence should be roughly 10-20 tokens
                sentence = "The quick brown fox jumps over the lazy dog."
                token_count = client._count_tokens(sentence)
                assert 5 < token_count < 20
                
                # Longer text should have proportionally more tokens
                long_text = sentence * 10
                long_count = client._count_tokens(long_text)
                assert long_count > token_count * 9  # Should be close to 10x
                assert long_count < token_count * 11
    
    def test_cost_estimation_math(self):
        """Test that cost calculations are correct."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            with patch("litai.llm.AsyncOpenAI"):
                with patch("litai.llm.LLMClient._count_tokens") as mock_count:
                    mock_count.side_effect = [1000, 500]  # prompt, completion
                    
                    client = LLMClient()
                    usage = client.estimate_cost("prompt", "response")
                    
                    # OpenAI: $0.01 per 1K prompt, $0.03 per 1K completion
                    expected_cost = (1000 * 0.01 + 500 * 0.03) / 1000
                    assert abs(usage.estimated_cost - expected_cost) < 0.0001
                    assert usage.estimated_cost == 0.025
    
    def test_config_based_init_openai(self):
        """Test initialization with OpenAI config."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = Config(base_dir=Path(temp_dir))
            config.save_config({
                "llm": {
                    "provider": "openai",
                    "model": "gpt-4o-mini"
                }
            })
            
            with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
                with patch("litai.llm.AsyncOpenAI"):
                    client = LLMClient(config)
                    assert client.provider == "openai"
                    assert client.model == "gpt-4o-mini"
    
    def test_config_based_init_anthropic(self):
        """Test initialization with Anthropic config."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = Config(base_dir=Path(temp_dir))
            config.save_config({
                "llm": {
                    "provider": "anthropic",
                    "model": "claude-3-haiku-20240307"
                }
            })
            
            with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
                with patch("litai.llm.AsyncAnthropic"):
                    client = LLMClient(config)
                    assert client.provider == "anthropic"
                    assert client.model == "claude-3-haiku-20240307"
    
    def test_config_auto_detection_fallback(self):
        """Test that auto detection works when config says auto."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = Config(base_dir=Path(temp_dir))
            config.save_config({
                "llm": {
                    "provider": "auto"
                }
            })
            
            with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}, clear=True):
                with patch("litai.llm.AsyncAnthropic"):
                    client = LLMClient(config)
                    assert client.provider == "anthropic"
    
    def test_config_custom_api_key_env(self):
        """Test using custom API key environment variable."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = Config(base_dir=Path(temp_dir))
            config.save_config({
                "llm": {
                    "provider": "openai",
                    "api_key_env": "MY_CUSTOM_API_KEY"
                }
            })
            
            with patch.dict(os.environ, {"MY_CUSTOM_API_KEY": "custom-key"}):
                with patch("litai.llm.AsyncOpenAI") as mock_openai:
                    client = LLMClient(config)
                    assert client.provider == "openai"
                    # Check that the custom API key was used
                    mock_openai.assert_called_once_with(api_key="custom-key")


@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"),
    reason="No API keys available for integration testing"
)
class TestLLMIntegration:
    """Integration tests that require real API keys."""
    
    @pytest.mark.asyncio
    async def test_real_api_connection(self):
        """Test actual API connection and response."""
        client = LLMClient()
        response_text, usage = await client.test_connection()
        
        # Should get a response containing our expected text
        assert "Hello from LitAI" in response_text
        assert usage.prompt_tokens > 0
        assert usage.completion_tokens > 0
        assert usage.estimated_cost > 0
        assert usage.estimated_cost < 0.01  # Should be very cheap
    
    @pytest.mark.asyncio
    async def test_real_completion(self):
        """Test a real completion request."""
        client = LLMClient()
        result = await client.complete(
            "What is 2+2? Reply with just the number.",
            max_tokens=10,
            temperature=0
        )
        
        assert "4" in result["content"]
        assert result["usage"].total_tokens > 0
        assert result["usage"].estimated_cost < 0.01
