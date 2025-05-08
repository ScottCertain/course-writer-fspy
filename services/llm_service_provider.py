import os
import logging
import yaml
from typing import Optional, Dict, Any

from services.llm_service import LLMServiceFactory, LLMService


class LLMServiceProvider:
    """
    Service for providing LLM service instances based on configuration.
    """

    def __init__(self):
        """Initialize the LLM service provider."""
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """
        Load the application configuration from YAML file.

        Returns:
            Dict containing the application configuration
        """
        config_path = os.path.join("config", "app_config.yaml")
        try:
            with open(config_path, "r") as file:
                return yaml.safe_load(file)

        except Exception as e:
            self.logger.error(f"Error loading application configuration: {e}")
            return {}

    def get_llm_service(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> LLMService:
        """
        Get an LLM service instance based on configuration.

        Args:
            provider: LLM provider name (anthropic, openai, ollama, lmstudio)
                     If None, uses the default provider from config
            model: Model name (optional, provider-specific default used if None)
            api_key: API key (optional, loaded from env vars if None)
            base_url: Base URL for API (optional, used for local models)

        Returns:
            LLM service instance
        """
        llm_config = self.config.get("llm", {})

        # Use default provider from config if not specified
        if provider is None:
            provider = llm_config.get("default_provider", "anthropic")

        # Get provider-specific configuration
        provider_config = llm_config.get("models", {}).get(provider.lower(), {})

        # Use default model from config if not specified
        if model is None and "default_model" in provider_config:
            model = provider_config.get("default_model")

        # Get base_url from config if specified there
        if base_url is None and "base_url" in provider_config:
            base_url = provider_config.get("base_url")

        # Create and return the LLM service
        self.logger.info(
            f"Creating LLM service for provider: {provider}, model: {model}"
        )
        return LLMServiceFactory.create_llm_service(
            provider=provider,
            model=model,
            api_key=api_key,
            base_url=base_url,
            config=llm_config,
        )
