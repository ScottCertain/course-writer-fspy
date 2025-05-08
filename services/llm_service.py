import os
import logging
from typing import Dict, Any, Optional, List, Union
from abc import ABC, abstractmethod
import time
import json
import requests
from dotenv import load_dotenv


class LLMService(ABC):
    """Abstract base class for LLM service providers."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @abstractmethod
    async def generate_text(
        self, prompt: str, temperature: float = 0.7, max_tokens: int = 2000
    ) -> str:
        """Generate text from the LLM with standard parameters."""
        pass

    @abstractmethod
    async def generate_with_context(
        self,
        prompt: str,
        context: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """Generate text with additional context."""
        pass


class AnthropicLLMService(LLMService):
    """LLM service for Anthropic Claude models."""

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-7-sonnet"):
        """
        Initialize Anthropic LLM service.

        Args:
            api_key: Anthropic API key (if None, loads from ANTHROPIC_API_KEY env var)
            model: Anthropic model to use
        """
        super().__init__()
        # Load from environment if not provided
        if api_key is None:
            load_dotenv()
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("Anthropic API key not found in environment variables")

        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.anthropic.com/v1/messages"
        self.logger.info(f"Initialized Anthropic LLM service with model: {model}")

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
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
        }

        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        try:
            response = requests.post(self.base_url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            self.logger.debug(f"Anthropic response: {result}")

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
        combined_prompt = f"Context:\n{context}\n\nPrompt:\n{prompt}"
        return await self.generate_text(combined_prompt, temperature, max_tokens)


class OpenAILLMService(LLMService):
    """LLM service for OpenAI models."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        """
        Initialize OpenAI LLM service.

        Args:
            api_key: OpenAI API key (if None, loads from OPENAI_API_KEY env var)
            model: OpenAI model to use
        """
        super().__init__()
        # Load from environment if not provided
        if api_key is None:
            load_dotenv()
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API key not found in environment variables")

        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.openai.com/v1/chat/completions"
        self.logger.info(f"Initialized OpenAI LLM service with model: {model}")

    async def generate_text(
        self, prompt: str, temperature: float = 0.7, max_tokens: int = 2000
    ) -> str:
        """
        Generate text using OpenAI GPT.

        Args:
            prompt: The prompt text
            temperature: Temperature parameter (0.0 to 1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        try:
            response = requests.post(self.base_url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            self.logger.debug(f"OpenAI response: {result}")

            # Extract content from the response
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                self.logger.error(f"Unexpected response format: {result}")
                return ""

        except Exception as e:
            self.logger.error(f"Error generating text with OpenAI: {e}")
            raise

    async def generate_with_context(
        self,
        prompt: str,
        context: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """
        Generate text with additional context using OpenAI GPT.

        Args:
            prompt: The prompt text
            context: Additional context to provide
            temperature: Temperature parameter (0.0 to 1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": context},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        try:
            response = requests.post(self.base_url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()

            # Extract content from the response
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                self.logger.error(f"Unexpected response format: {result}")
                return ""

        except Exception as e:
            self.logger.error(f"Error generating text with OpenAI: {e}")
            raise


class OllamaLLMService(LLMService):
    """LLM service for Ollama models."""

    def __init__(self, base_url: Optional[str] = None, model: str = "llama3"):
        """
        Initialize Ollama LLM service.

        Args:
            base_url: Base URL for Ollama API (if None, loads from OLLAMA_BASE_URL env var)
            model: Ollama model to use
        """
        super().__init__()
        # Load from environment if not provided
        if base_url is None:
            load_dotenv()
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

        self.base_url = base_url
        self.model = model
        self.logger.info(f"Initialized Ollama LLM service with model: {model}")

    async def generate_text(
        self, prompt: str, temperature: float = 0.7, max_tokens: int = 2000
    ) -> str:
        """
        Generate text using Ollama.

        Args:
            prompt: The prompt text
            temperature: Temperature parameter (0.0 to 1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text
        """
        api_url = f"{self.base_url}/api/generate"

        data = {
            "model": self.model,
            "prompt": prompt,
            "temperature": temperature,
            "num_predict": max_tokens,
        }

        try:
            response = requests.post(api_url, json=data)
            response.raise_for_status()
            result = response.text

            # Ollama returns each token as a separate line of JSON
            # We need to join them together to get the full response
            lines = result.strip().split("\n")
            response_text = ""

            for line in lines:
                try:
                    chunk = json.loads(line)
                    if "response" in chunk:
                        response_text += chunk["response"]
                except json.JSONDecodeError:
                    continue

            return response_text

        except Exception as e:
            self.logger.error(f"Error generating text with Ollama: {e}")
            raise

    async def generate_with_context(
        self,
        prompt: str,
        context: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """
        Generate text with additional context using Ollama.

        Args:
            prompt: The prompt text
            context: Additional context to provide
            temperature: Temperature parameter (0.0 to 1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text
        """
        combined_prompt = f"Context:\n{context}\n\nPrompt:\n{prompt}"
        return await self.generate_text(combined_prompt, temperature, max_tokens)


class LMStudioService(LLMService):
    """LLM service for LM Studio local models."""

    def __init__(self, base_url: Optional[str] = None, model: str = "custom"):
        """
        Initialize LM Studio service.

        Args:
            base_url: Base URL for LM Studio API (if None, loads from LMSTUDIO_BASE_URL env var)
            model: Model name (usually just "custom" for local models)
        """
        super().__init__()
        # Load from environment if not provided
        if base_url is None:
            load_dotenv()
            base_url = os.getenv("LMSTUDIO_BASE_URL", "http://localhost:1234/v1")

        self.base_url = base_url
        self.model = model
        self.logger.info(f"Initialized LM Studio service with model: {model}")

    async def generate_text(
        self, prompt: str, temperature: float = 0.7, max_tokens: int = 2000
    ) -> str:
        """
        Generate text using LM Studio.

        Args:
            prompt: The prompt text
            temperature: Temperature parameter (0.0 to 1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text
        """
        api_url = f"{self.base_url}/chat/completions"

        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            response = requests.post(api_url, json=data)
            response.raise_for_status()
            result = response.json()

            # Extract content from the response
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                self.logger.error(f"Unexpected response format: {result}")
                return ""

        except Exception as e:
            self.logger.error(f"Error generating text with LM Studio: {e}")
            raise

    async def generate_with_context(
        self,
        prompt: str,
        context: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """
        Generate text with additional context using LM Studio.

        Args:
            prompt: The prompt text
            context: Additional context to provide
            temperature: Temperature parameter (0.0 to 1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text
        """
        api_url = f"{self.base_url}/chat/completions"

        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": context},
                {"role": "user", "content": prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            response = requests.post(api_url, json=data)
            response.raise_for_status()
            result = response.json()

            # Extract content from the response
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                self.logger.error(f"Unexpected response format: {result}")
                return ""

        except Exception as e:
            self.logger.error(f"Error generating text with LM Studio: {e}")
            raise


class LLMServiceFactory:
    """Factory for creating LLM service instances."""

    @staticmethod
    def create_llm_service(
        provider: str,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> LLMService:
        """
        Create an LLM service instance based on provider.

        Args:
            provider: LLM provider name (anthropic, openai, ollama, lmstudio)
            model: Model name (optional, provider-specific default used if None)
            api_key: API key (optional, loaded from env vars if None)
            base_url: Base URL for API (optional, used for local models)
            config: Additional configuration dictionary from app_config.yaml

        Returns:
            LLM service instance
        """
        logger = logging.getLogger(__name__)
        logger.info(f"Creating LLM service for provider: {provider}")

        # Default values
        default_models = {
            "anthropic": "claude-3-7-sonnet",
            "openai": "gpt-4o",
            "ollama": "codegemma:7b",
            "lmstudio": "gemma-3-12b-it-qat",
        }

        # Get provider specific configurations from config if available
        provider_config = {}
        if config and "models" in config and provider.lower() in config["models"]:
            provider_config = config["models"][provider.lower()]

            # Update default model from config if available
            if "default_model" in provider_config:
                default_models[provider.lower()] = provider_config["default_model"]

            # Get base_url from config for local models if available
            if base_url is None and "base_url" in provider_config:
                base_url = provider_config["base_url"]

        # Create appropriate service based on provider
        if provider.lower() == "anthropic":
            return AnthropicLLMService(
                api_key=api_key, model=model or default_models["anthropic"]
            )
        elif provider.lower() == "openai":
            return OpenAILLMService(
                api_key=api_key, model=model or default_models["openai"]
            )
        elif provider.lower() == "ollama":
            # Default Ollama base URL
            if base_url is None:
                base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            return OllamaLLMService(
                base_url=base_url, model=model or default_models["ollama"]
            )
        elif provider.lower() == "lmstudio":
            # Default LM Studio base URL
            if base_url is None:
                base_url = os.getenv("LMSTUDIO_BASE_URL", "http://localhost:1234/v1")
            return LMStudioService(
                base_url=base_url, model=model or default_models["lmstudio"]
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
