import asyncio
import logging
import os
from dotenv import load_dotenv

from services.llm_service_provider import LLMServiceProvider

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


async def test_llm_configuration():
    """Test the LLM configuration with different providers and models."""

    logger.info("Testing LLM configuration...")

    # Create LLM service provider
    provider = LLMServiceProvider()

    # Test configurations to try
    test_configs = [
        # Default configuration (from app_config.yaml)
        {"provider": None, "model": None, "description": "Default from config"},
        # Anthropic Claude models
        {
            "provider": "anthropic",
            "model": "claude-3-7-sonnet",
            "description": "Anthropic Claude 3.7 Sonnet",
        },
        {
            "provider": "anthropic",
            "model": "claude-3.5-sonnet-2024-10-22",
            "description": "Anthropic Claude 3.5 Sonnet",
        },
        {
            "provider": "anthropic",
            "model": "claude-3.5-haiku",
            "description": "Anthropic Claude 3.5 Haiku",
        },
        # Ollama models
        {
            "provider": "ollama",
            "model": "gemma3:12b",
            "description": "Ollama with Gemma 3 12B",
        },
        {
            "provider": "ollama",
            "model": "codegemma:7b",
            "description": "Ollama with CodeGemma 7B",
        },
        {
            "provider": "ollama",
            "model": "phi4:latest",
            "description": "Ollama with Phi 4",
        },
        # LMStudio model
        {
            "provider": "lmstudio",
            "model": "gemma-3-12b-it-qat",
            "description": "LM Studio with Gemma 3 12B QAT",
        },
    ]

    # Test each configuration
    for config in test_configs:
        provider_name = config["provider"] or "default"
        model_name = config["model"] or "default"

        logger.info(
            f"\nTesting {config['description']} ({provider_name}/{model_name})..."
        )

        try:
            # Get LLM service
            llm_service = provider.get_llm_service(
                provider=config["provider"], model=config["model"]
            )

            logger.info(
                f"Successfully created LLM service: {type(llm_service).__name__}"
            )
            logger.info(f"Provider: {config['provider'] or 'default'}")
            logger.info(f"Model: {llm_service.model}")

            # Skip actual API calls - we're just testing the configuration
            logger.info(f"Would call the model API here if this wasn't just a test")

        except Exception as e:
            logger.error(f"Error testing {config['description']}: {e}")

    logger.info("\nLLM configuration test complete.")


if __name__ == "__main__":
    asyncio.run(test_llm_configuration())
