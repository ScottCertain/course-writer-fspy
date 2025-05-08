"""
Unit tests for the LLM service provider and configuration.

Migrated from the standalone test_llm_configuration.py script.
"""

import os
import pytest
from unittest.mock import patch, MagicMock

from services.llm_service_provider import LLMServiceProvider
from services.llm_service import LLMService


class TestLLMConfiguration:
    """Tests for LLM configuration and service provider."""

    def test_service_provider_instantiation(self):
        """Test creating the LLM service provider instance."""
        provider = LLMServiceProvider()
        assert provider is not None
        assert hasattr(provider, "get_llm_service")

    @patch("services.llm_service_provider.LLMServiceFactory.create_llm_service")
    def test_get_llm_service_default(self, mock_create_llm_service):
        """Test getting an LLM service with default parameters."""
        # Create mock service
        mock_service = MagicMock(spec=LLMService)
        mock_service.model = "default-model"
        mock_create_llm_service.return_value = mock_service

        # Create provider and get service
        provider = LLMServiceProvider()
        service = provider.get_llm_service()

        # Verify the service was created correctly
        assert service is not None
        assert service.model == "default-model"
        mock_create_llm_service.assert_called_once()

    @patch("services.llm_service_provider.LLMServiceFactory.create_llm_service")
    def test_get_llm_service_anthropic(self, mock_create_llm_service):
        """Test getting an Anthropic LLM service."""
        # Create mock service
        mock_service = MagicMock(spec=LLMService)
        mock_service.model = "claude-3-sonnet-20240229"
        mock_create_llm_service.return_value = mock_service

        # Create provider and get service
        provider = LLMServiceProvider()
        service = provider.get_llm_service(
            provider="anthropic", model="claude-3-sonnet-20240229"
        )

        # Verify the service was created correctly
        assert service is not None
        assert service.model == "claude-3-sonnet-20240229"
        mock_create_llm_service.assert_called_once_with(
            "anthropic", "claude-3-sonnet-20240229", None, None
        )

    @patch("services.llm_service_provider.LLMServiceFactory.create_llm_service")
    def test_get_llm_service_with_api_key(self, mock_create_llm_service):
        """Test getting an LLM service with a custom API key."""
        # Create mock service
        mock_service = MagicMock(spec=LLMService)
        mock_service.model = "test-model"
        mock_create_llm_service.return_value = mock_service

        # Create provider and get service
        provider = LLMServiceProvider()
        api_key = "test-api-key"
        service = provider.get_llm_service(
            provider="test", model="test-model", api_key=api_key
        )

        # Verify the service was created with the API key
        assert service is not None
        mock_create_llm_service.assert_called_once_with(
            "test", "test-model", api_key, None
        )

    @patch("services.llm_service_provider.LLMServiceFactory.create_llm_service")
    def test_get_llm_service_with_base_url(self, mock_create_llm_service):
        """Test getting an LLM service with a custom base URL."""
        # Create mock service
        mock_service = MagicMock(spec=LLMService)
        mock_service.model = "test-model"
        mock_create_llm_service.return_value = mock_service

        # Create provider and get service
        provider = LLMServiceProvider()
        base_url = "http://localhost:8000/v1"
        service = provider.get_llm_service(
            provider="test", model="test-model", base_url=base_url
        )

        # Verify the service was created with the base URL
        assert service is not None
        mock_create_llm_service.assert_called_once_with(
            "test", "test-model", None, base_url
        )

    def test_provider_supports_multiple_models(self):
        """Test that the provider supports configuration for multiple models."""
        # This test simulates the original test_llm_configuration.py's
        # checking of multiple provider/model combinations

        provider = LLMServiceProvider()

        # Define test configurations
        test_configs = [
            # Anthropic models
            {"provider": "anthropic", "model": "claude-3-sonnet-20240229"},
            {"provider": "anthropic", "model": "claude-3-haiku-20240307"},
            # Other providers could be added here
        ]

        # Instead of actually creating the services, we'll mock the factory
        with patch(
            "services.llm_service_provider.LLMServiceFactory.create_llm_service"
        ) as mock_create:
            # Setup the mock to return a new mock for each call
            mock_create.side_effect = lambda p, m, *args: MagicMock(
                spec=LLMService, model=m
            )

            # Test each configuration
            for config in test_configs:
                # Get LLM service
                service = provider.get_llm_service(
                    provider=config["provider"], model=config["model"]
                )

                # Verify correct model was passed to factory
                assert service.model == config["model"]

                # Verify factory was called with correct provider
                mock_create.assert_any_call(
                    config["provider"], config["model"], None, None
                )
