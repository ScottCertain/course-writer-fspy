"""
Integration tests for the LessonPipeline.

These tests verify that components work together correctly.
"""

import os
import pytest
import asyncio
from unittest.mock import patch, MagicMock

from services.pipeline_service_fix import FixedLessonPipeline as LessonPipeline
from services.anthropic_service_fix import FixedAnthropicLLMService
from services.file_service import FileService


@pytest.mark.asyncio
async def test_pipeline_integration_with_mocked_llm(
    mock_llm_service, test_course_dir, tmp_path
):
    """
    Integration test for the lesson pipeline with a mocked LLM service.

    This test verifies that the pipeline correctly orchestrates the different
    components and produces the expected output files.
    """
    # Create a test lesson
    lesson_id = "test_integration_lesson"

    # Setup test parameters
    module = "Test Module"
    lesson_objective = "Test the pipeline integration"
    lesson_topics = """
    - Topic 1
    - Topic 2
    - Topic 3
    """
    title = "Integration Test Lesson"

    # Course context
    course_context = {
        "title": "Test Course",
        "target_audience": "Software Developers",
        "skill_level": "Intermediate",
    }

    # Mock the LLMServiceProvider to return our mock service
    with patch(
        "services.llm_service_provider.LLMServiceProvider.get_llm_service",
        return_value=mock_llm_service,
    ):

        # Create the pipeline
        pipeline = LessonPipeline(course_dir=test_course_dir, lesson_id=lesson_id)

        # Create a simple callback to track progress
        progress_steps = []

        def progress_callback(step, status, message):
            progress_steps.append((step, status))

        # Set the progress callback
        pipeline.set_progress_callback(progress_callback)

        # Run the pipeline
        result = await pipeline.run_pipeline(
            module=module,
            lesson_objective=lesson_objective,
            lesson_topics=lesson_topics,
            title=title,
            course_context=course_context,
        )

        # Check that the pipeline completed successfully
        assert result["status"] == "success"

        # Verify that we got through all the expected steps
        step_names = [step for step, _ in progress_steps]

        # Verify key steps were processed
        assert "lesson_shell" in step_names
        assert "learning_outcomes" in step_names
        assert "rough_draft" in step_names

        # Check that all files were reported as created
        for file_type, file_name in result["files"].items():
            # File paths should be reported correctly
            assert file_type in [
                "learning_outcomes",
                "lesson_shell",
                "rough_draft",
                "expanded_draft",
                "intro_conclusion",
                "final_lesson",
            ]

            # Files should have the correct naming pattern
            assert file_name.startswith(lesson_id)

            # Handle special cases for file naming conventions
            if file_type == "learning_outcomes":
                assert file_name.endswith("_los.md")
            elif file_type == "lesson_shell":
                assert file_name.endswith("_shell.md")
            elif file_type == "final_lesson":
                assert file_name.endswith("_final.md")
            else:
                # For other types, the suffix matches the file_type
                assert file_name.endswith(f"_{file_type}.md")


@pytest.mark.asyncio
async def test_pipeline_error_handling(mock_llm_service, test_course_dir):
    """
    Test pipeline error handling by simulating a failure in the LLM service.
    """
    # Create a test lesson
    lesson_id = "test_error_handling"

    # Configure the mock to raise an exception for a specific method
    mock_llm_service.generate_text.side_effect = Exception("Simulated LLM failure")

    # Setup test parameters
    module = "Test Module"
    lesson_objective = "Test error handling"
    lesson_topics = "Topic 1, Topic 2"
    title = "Error Handling Test"

    # Course context
    course_context = {
        "title": "Test Course",
        "target_audience": "Software Developers",
        "skill_level": "Intermediate",
    }

    # Mock the LLMServiceProvider
    with patch(
        "services.llm_service_provider.LLMServiceProvider.get_llm_service",
        return_value=mock_llm_service,
    ):

        # Create the pipeline
        pipeline = LessonPipeline(course_dir=test_course_dir, lesson_id=lesson_id)

        # Create a simple callback to track progress
        progress_steps = []

        def progress_callback(step, status, message):
            progress_steps.append((step, status))

        # Set the progress callback
        pipeline.set_progress_callback(progress_callback)

        # Run the pipeline, expecting a failure
        result = await pipeline.run_pipeline(
            module=module,
            lesson_objective=lesson_objective,
            lesson_topics=lesson_topics,
            title=title,
            course_context=course_context,
        )

        # Check that the pipeline reports a failure
        assert result["status"] == "error"
        assert "step" in result
        assert "message" in result

        # Verify that we have an error status in our progress steps
        has_error = any(status == "error" for _, status in progress_steps)
        assert has_error
