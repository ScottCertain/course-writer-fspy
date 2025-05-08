"""
Unit tests for the AnthropicLLMService classes.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
import asyncio

from services.anthropic_service_fix import FixedAnthropicLLMService
from services.anthropic_service import AnthropicLLMService


class TestFixedAnthropicLLMService:
    """Tests for the FixedAnthropicLLMService class."""

    def test_init(self):
        """Test initialization with default parameters."""
        service = FixedAnthropicLLMService(api_key="test_key")
        assert service.api_key == "test_key"
        assert service.model == "claude-3-sonnet-20240229"
        assert service.base_url == "https://api.anthropic.com/v1/messages"

    def test_init_with_model(self):
        """Test initialization with a specific model."""
        service = FixedAnthropicLLMService(
            api_key="test_key", model="claude-3-haiku-20240307"
        )
        assert service.api_key == "test_key"
        assert service.model == "claude-3-haiku-20240307"

    def test_check_token_limit(self):
        """Test token limit checking logic."""
        service = FixedAnthropicLLMService(
            api_key="test_key", model="claude-3-sonnet-20240229"
        )

        # Test with token count within limit
        result = service._check_token_limit(3000)
        assert result == 3000

        # Test with token count exceeding limit
        result = service._check_token_limit(5000)
        assert result == 4096  # Should be capped at the model's max tokens

    @patch("requests.post")
    @pytest.mark.asyncio
    async def test_generate_text(self, mock_post):
        """Test the generate_text method with a mocked API response."""
        # Configure the mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "content": [{"text": "This is a test response."}]
        }
        mock_post.return_value = mock_response

        # Create service and call method
        service = FixedAnthropicLLMService(api_key="test_key")
        result = await service.generate_text(
            "Test prompt", temperature=0.5, max_tokens=100
        )

        # Verify the request
        mock_post.assert_called_once()
        # Check that the URL is correct
        assert mock_post.call_args[0][0] == "https://api.anthropic.com/v1/messages"
        # Check that the API key is in the headers
        assert mock_post.call_args[1]["headers"]["x-api-key"] == "test_key"
        # Check that the model is in the payload
        assert mock_post.call_args[1]["json"]["model"] == "claude-3-sonnet-20240229"
        # Check the temperature and max_tokens
        assert mock_post.call_args[1]["json"]["temperature"] == 0.5
        assert mock_post.call_args[1]["json"]["max_tokens"] == 100
        # Check that the prompt is in the messages
        assert mock_post.call_args[1]["json"]["messages"][0]["content"] == "Test prompt"

        # Verify the result
        assert result == "This is a test response."

    @patch("requests.post")
    @pytest.mark.asyncio
    async def test_generate_with_context(self, mock_post):
        """Test the generate_with_context method with a mocked API response."""
        # Configure the mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "content": [{"text": "This is a test response with context."}]
        }
        mock_post.return_value = mock_response

        # Create service and call method
        service = FixedAnthropicLLMService(api_key="test_key")
        result = await service.generate_with_context(
            "Test prompt", "Test context", temperature=0.5, max_tokens=100
        )

        # Verify the request
        mock_post.assert_called_once()
        # Check that the context is in the system parameter at the top level
        assert mock_post.call_args[1]["json"]["system"] == "Test context"
        # Check that the prompt is in the messages
        assert mock_post.call_args[1]["json"]["messages"][0]["content"] == "Test prompt"

        # Verify the result
        assert result == "This is a test response with context."

    @patch("requests.post")
    @pytest.mark.asyncio
    async def test_api_error_handling(self, mock_post):
        """Test handling of API errors."""
        # Configure the mock to raise an exception
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_response.raise_for_status.side_effect = Exception("API Error")
        mock_post.return_value = mock_response

        # Create service and call method, expecting an exception
        service = FixedAnthropicLLMService(api_key="test_key")
        with pytest.raises(Exception, match="API Error"):
            await service.generate_text("Test prompt")


# Optional: Add similar tests for the original AnthropicLLMService if needed
