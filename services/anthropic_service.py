import os
import logging
import json
import requests
import asyncio
from typing import Dict, Any, Optional, List, Union
from dotenv import load_dotenv
from services.llm_service import LLMService


class AnthropicLLMService(LLMService):
    """LLM service for Anthropic Claude models with proper API compatibility."""

    # Model maximum token map
    MODEL_MAX_TOKENS = {
        "claude-3-sonnet-20240229": 4096,
        "claude-3-haiku-20240307": 4096,
        "claude-3-opus-20240229": 4096,
        "claude-3-7-sonnet-20250219": 4096,
        "claude-2.0": 100000,  # High value as fallback
        "claude-2.1": 100000,  # High value as fallback
    }

    def __init__(
        self, api_key: Optional[str] = None, model: str = "claude-3-7-sonnet-20250219"
    ):
        """
        Initialize Anthropic LLM service.

        Args:
            api_key: Anthropic API key (if None, loads from ANTHROPIC_API_KEY env var)
            model: Anthropic model to use
        """
        super().__init__()
        # Load from environment if not provided
        if api_key is None:
            # Ensure env file is loaded
            load_dotenv(override=True)
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("Anthropic API key not found in environment variables")

        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.anthropic.com/v1/messages"
        self.logger.info(f"Initialized Anthropic LLM service with model: {model}")

    def _check_token_limit(self, max_tokens: int) -> int:
        """Check if the requested max_tokens is within model limits."""
        model_limit = self.MODEL_MAX_TOKENS.get(
            self.model, 4096
        )  # Default to 4096 if model not found

        if max_tokens > model_limit:
            self.logger.warning(
                f"Requested max_tokens ({max_tokens}) exceeds model limit ({model_limit}). "
                f"Using model limit instead."
            )
            return model_limit
        return max_tokens

    async def generate_text(
        self, prompt: str, temperature: float = 0.7, max_tokens: int = 2000
    ) -> str:
        """
        Generate text using Anthropic Claude.

        Args:
            prompt: The prompt text
            temperature: Temperature parameter (0.0 to 1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text
        """
        # Check token limit for the model
        max_tokens = self._check_token_limit(max_tokens)

        # Headers with the proper API version
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "anthropic-beta": "messages-2023-12-15",
        }

        # Payload format per Anthropic API specification
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        try:
            # Print request details for debugging
            self.logger.debug(f"Making request to: {self.base_url}")
            self.logger.debug(f"Headers: {headers}")
            self.logger.debug(f"Data: {json.dumps(data, indent=2)}")

            response = requests.post(self.base_url, headers=headers, json=data)

            # Log response status
            self.logger.debug(f"Response status: {response.status_code}")

            # Full response content for debugging
            self.logger.debug(f"Response content: {response.text}")

            # If non-successful response, print more details
            if response.status_code != 200:
                self.logger.error(
                    f"API Error - Status: {response.status_code}, Response: {response.text}"
                )

            response.raise_for_status()
            result = response.json()

            # Extract content from the response
            if "content" in result and len(result["content"]) > 0:
                return result["content"][0]["text"]
            else:
                self.logger.error(f"Unexpected response format: {result}")
                return ""

        except Exception as e:
            self.logger.error(f"Error generating text with Anthropic: {e}")
            raise

    async def generate_with_context(
        self,
        prompt: str,
        context: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """
        Generate text with additional context using Anthropic Claude.

        Args:
            prompt: The prompt text
            context: Additional context to provide
            temperature: Temperature parameter (0.0 to 1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text
        """
        # Check token limit for the model
        max_tokens = self._check_token_limit(max_tokens)

        # Headers with the proper API version
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "anthropic-beta": "messages-2023-12-15",
        }

        # System goes at the top level, not as a message role
        data = {
            "model": self.model,
            "system": context,  # System prompt goes here at the top level
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        try:
            # Print request details for debugging
            self.logger.debug(f"Making request to: {self.base_url}")
            self.logger.debug(f"Headers: {headers}")
            self.logger.debug(f"Data: {json.dumps(data, indent=2)}")

            response = requests.post(self.base_url, headers=headers, json=data)

            # Log response status
            self.logger.debug(f"Response status: {response.status_code}")

            # Full response content for debugging
            self.logger.debug(f"Response content: {response.text}")

            # If non-successful response, print more details
            if response.status_code != 200:
                self.logger.error(
                    f"API Error - Status: {response.status_code}, Response: {response.text}"
                )

            response.raise_for_status()
            result = response.json()

            # Extract content from the response
            if "content" in result and len(result["content"]) > 0:
                return result["content"][0]["text"]
            else:
                self.logger.error(f"Unexpected response format: {result}")
                return ""

        except Exception as e:
            self.logger.error(f"Error generating text with Anthropic: {e}")
            raise
