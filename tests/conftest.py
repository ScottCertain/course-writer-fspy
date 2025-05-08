"""
Configuration file for pytest containing shared fixtures and setup/teardown functions.
"""

import os
import pytest
import yaml
from unittest.mock import MagicMock

from services.llm_service import LLMService


@pytest.fixture
def mock_llm_service():
    """
    Fixture that provides a mock LLM service for testing.

    This allows tests to run without making actual API calls to LLM providers.
    """
    mock_service = MagicMock(spec=LLMService)

    # Set up the generate_text method to return a predefined response
    async def mock_generate_text(prompt, temperature=0.7, max_tokens=2000):
        return f"Mock response for: {prompt[:30]}..."

    # Set up the generate_with_context method to return a predefined response
    async def mock_generate_with_context(
        prompt, context, temperature=0.7, max_tokens=2000
    ):
        return f"Mock response with context for: {prompt[:30]}..."

    # Assign the mock methods
    mock_service.generate_text.side_effect = mock_generate_text
    mock_service.generate_with_context.side_effect = mock_generate_with_context

    return mock_service


@pytest.fixture
def test_course_dir():
    """
    Fixture that provides a path to a test course directory.
    """
    return os.path.join("courses", "test_course_fixed")


@pytest.fixture
def test_config():
    """
    Fixture that provides a test configuration.
    """
    return {
        "title": "Test Course",
        "description": "A test course for unit testing",
        "target_audience": "Developers",
        "skill_level": "Intermediate",
        "llm": {
            "provider": "anthropic",
            "model": "claude-3-sonnet-20240229",
            "temperature": 0.7,
            "max_tokens": 4000,
        },
    }
