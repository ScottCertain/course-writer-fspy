import os
import asyncio
import logging
import json
import re
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple

from services.llm_service_provider import LLMServiceProvider
from services.prompt_service import PromptService
from services.file_service import FileService
from services.anthropic_service_fix import FixedAnthropicLLMService
from models.course import Course
from models.lesson import Lesson


class DraftPipeline:
    """
    Draft generation pipeline service that runs the first part of lesson creation.
    Executes a series of prompts in sequence to generate content up to the expanded draft.
    """

    def __init__(
        self,
        course_dir: str,
        lesson_id: str,
        llm_provider: Optional[str] = None,
        model: Optional[str] = None,
    ):
        """
        Initialize the draft pipeline.

        Args:
            course_dir: Directory containing the course
            lesson_id: Identifier for the lesson
            llm_provider: LLM provider to use (defaults to course configuration)
            model: Model to use (defaults to course configuration)
        """
        self.logger = logging.getLogger(__name__)
        self.course_dir = course_dir
        self.lesson_id = lesson_id
        self.llm_provider = llm_provider
        self.model = model

        # Initialize services
        self.llm_service_provider = LLMServiceProvider()
        self.prompt_service = PromptService()
        self.file_service = FileService()

        # Set up lesson directory
        self.lesson_dir = os.path.join(course_dir, "lessons")
        os.makedirs(self.lesson_dir, exist_ok=True)

        # Track the current step
        self.current_step = None
        self.progress_callback = None
        self.log_file = os.path.join(course_dir, "pipeline_logs.jsonl")

    def set_progress_callback(self, callback):
        """Set a callback function to report progress."""
        self.progress_callback = callback

    def _update_progress(self, step: str, status: str, message: str = ""):
        """Update progress using the callback if available."""
        self.current_step = step

        # Log the progress
        self._log_step(step, status, message)

        # Call the callback if available
        if self.progress_callback:
            self.progress_callback(step, status, message)

    def _log_step(self, step: str, status: str, message: str = ""):
        """Log pipeline step to a file."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "step": step,
            "status": status,
            "message": message,
        }

        try:
            with open(self.log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            self.logger.error(f"Error writing to log file: {e}")

    async def _call_llm_with_retry(
        self,
        prompt: str,
        model_params: Dict[str, Any],
        max_retries: int = 3,
        initial_delay: float = 1.0,
    ) -> str:
        """Call LLM with exponential backoff retry logic."""

        # Extract parameters
        temperature = model_params.get("temperature", 0.7)
        max_tokens = model_params.get("max_tokens", 2000)
        prompt_type = model_params.get("prompt_type", "standard")

        # Get the LLM service - always use FixedAnthropicLLMService if provider is "anthropic"
        llm_service = None
        if self.llm_provider and self.llm_provider.lower() == "anthropic":
            self.logger.info(f"Using fixed Anthropic service with model: {self.model}")
            llm_service = FixedAnthropicLLMService(model=self.model)
        else:
            # Use the regular service provider for other providers
            llm_service = self.llm_service_provider.get_llm_service(
                provider=self.llm_provider, model=self.model
            )

        # Retry logic
        retries = 0
        last_error = None

        while retries <= max_retries:
            try:
                # Call the appropriate method based on prompt type
                if prompt_type == "with_system" and "system_prompt" in model_params:
                    return await llm_service.generate_with_context(
                        prompt=prompt,
                        context=model_params["system_prompt"],
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                else:
                    return await llm_service.generate_text(
                        prompt=prompt, temperature=temperature, max_tokens=max_tokens
                    )

            except Exception as e:
                last_error = e
                self.logger.warning(
                    f"LLM API error (attempt {retries+1}/{max_retries+1}): {str(e)}"
                )

                # Implement exponential backoff
                delay = initial_delay * (2**retries)
                self.logger.info(f"Retrying in {delay}s")
                await asyncio.sleep(delay)
                retries += 1

        # If we've exhausted retries, log and raise the error
        self.logger.error(
            f"Maximum retries exceeded when calling LLM API: {last_error}"
        )
        raise last_error

    async def _validate_output(
        self, output: str, expected_format: str
    ) -> Tuple[bool, str]:
        """Validate that LLM output meets expected format."""
        validation_message = ""

        if expected_format == "learning_outcomes":
            # Check for LO format
            if not re.search(r"LO \d+:", output) and not re.search(
                r"Learning Outcome \d+:", output
            ):
                validation_message = "Output missing expected Learning Outcomes format"
                return False, validation_message

        elif expected_format == "lesson_shell":
            # Check for lesson shell structure
            if not all(
                x in output
                for x in ["# Lesson:", "## Introduction", "## Learning Outcomes"]
            ):
                validation_message = "Output missing expected lesson shell structure"
                return False, validation_message

        elif expected_format == "rough_draft":
            # Check for rough draft structure
            if not all(
                x in output
                for x in [
                    "# ",
                    "## Introduction",
                    "## Learning Outcomes",
                    "## Conclusion",
                ]
            ):
                validation_message = "Output missing expected rough draft structure"
                return False, validation_message

        elif expected_format == "expanded_draft":
            # Check for expanded draft structure
            if not all(
                x in output
                for x in [
                    "# ",
                    "## Introduction",
                    "## Learning Outcomes",
                    "## Conclusion",
                ]
            ):
                validation_message = "Output missing expected expanded draft structure"
                return False, validation_message

        # Default to success if no specific validation is defined
        return True, "Validation passed"

    async def _generate_learning_outcomes(
        self, module: str, lesson_objective: str, lesson_topics: str
    ) -> str:
        """
        Step 1: Generate Learning Outcomes.

        Args:
            module: The module name
            lesson_objective: The lesson objective
            lesson_topics: The lesson topics

        Returns:
            The generated learning outcomes
        """
        self._update_progress(
            "learning_outcomes", "starting", "Generating learning outcomes"
        )

        try:
            # Get the LO generator prompt template
            template = self.prompt_service.get_prompt("lo_generator")
            if not template:
                raise ValueError("LO generator prompt template not found")

            # Prepare variables for the template
            # Note: The prompt service uses $variable format, but our templates use {{VARIABLE}}
            # We need to convert between the formats
            variables = {
                "MODULE": module,
                "LESSON_OBJECTIVE": lesson_objective,
                "LESSON_TOPICS": lesson_topics,
            }

            # Extract API parameters from the template with safer token limits
            api_params = self._extract_api_params(template)

            # Limit max_tokens to 4000 to work with claude-3-sonnet
            if api_params.get("max_tokens", 0) > 4000:
                api_params["max_tokens"] = 4000
                self.logger.info("Reduced max_tokens to 4000 for compatibility")

            # Extract system prompt from the template
            system_prompt = self._extract_system_prompt(template)
            if system_prompt:
                api_params["prompt_type"] = "with_system"
                api_params["system_prompt"] = system_prompt

            # Prepare the prompt with variable substitution by manually replacing {{VARIABLE}} format
            prompt = template
            for key, value in variables.items():
                prompt = prompt.replace(f"{{{{{key}}}}}", value)

            # Use only the user message part for the API call
            user_message = self._extract_user_message(prompt)
            if not user_message:
                raise ValueError("Failed to extract user message from template")

            # Call the LLM with retry
            self.logger.info("Calling LLM for learning outcomes generation")
            response = await self._call_llm_with_retry(user_message, api_params)

            # Validate the output
            is_valid, message = await self._validate_output(
                response, "learning_outcomes"
            )
            if not is_valid:
                self.logger.warning(f"LO validation failed: {message}")
                self._update_progress(
                    "learning_outcomes", "warning", f"Validation issue: {message}"
                )
                # Continue anyway but log the warning

            # Write the learning outcomes to a file
            los_file = os.path.join(self.lesson_dir, f"{self.lesson_id}_los.md")
            with open(los_file, "w", encoding="utf-8") as f:
                f.write(response)

            self._update_progress(
                "learning_outcomes", "success", "Learning outcomes generated"
            )
            return response

        except Exception as e:
            self.logger.error(f"Error generating learning outcomes: {str(e)}")
            self._update_progress("learning_outcomes", "error", f"Error: {str(e)}")
            raise

    async def _generate_lesson_shell(self, learning_outcomes: str, title: str) -> str:
        """
        Step 2: Generate Lesson Shell.

        Args:
            learning_outcomes: The learning outcomes generated in step 1
            title: The lesson title

        Returns:
            The generated lesson shell
        """
        self._update_progress("lesson_shell", "starting", "Generating lesson shell")

        try:
            # Get the lesson shell prompt template
            template = self.prompt_service.get_prompt("lesson_shell")
            if not template:
                raise ValueError("Lesson shell prompt template not found")

            # Prepare variables for the template
            variables = {"TITLE": title, "LOs": learning_outcomes}

            # Extract API parameters from the template with safer token limits
            api_params = self._extract_api_params(template)

            # Limit max_tokens to 4000 to work with claude-3-sonnet
            if api_params.get("max_tokens", 0) > 4000:
                api_params["max_tokens"] = 4000
                self.logger.info("Reduced max_tokens to 4000 for compatibility")

            # Extract system prompt from the template
            system_prompt = self._extract_system_prompt(template)
            if system_prompt:
                api_params["prompt_type"] = "with_system"
                api_params["system_prompt"] = system_prompt

            # Prepare the prompt with variable substitution by manually replacing {{VARIABLE}} format
            prompt = template
            for key, value in variables.items():
                prompt = prompt.replace(f"{{{{{key}}}}}", value)

            # Use only the user message part for the API call
            user_message = self._extract_user_message(prompt)
            if not user_message:
                raise ValueError("Failed to extract user message from template")

            # Call the LLM with retry
            self.logger.info("Calling LLM for lesson shell generation")
            response = await self._call_llm_with_retry(user_message, api_params)

            # Validate the output
            is_valid, message = await self._validate_output(response, "lesson_shell")
            if not is_valid:
                self.logger.warning(f"Lesson shell validation failed: {message}")
                self._update_progress(
                    "lesson_shell", "warning", f"Validation issue: {message}"
                )
                # Continue anyway but log the warning

            # Write the lesson shell to a file
            shell_file = os.path.join(self.lesson_dir, f"{self.lesson_id}_shell.md")
            with open(shell_file, "w", encoding="utf-8") as f:
                f.write(response)

            self._update_progress("lesson_shell", "success", "Lesson shell generated")
            return response

        except Exception as e:
            self.logger.error(f"Error generating lesson shell: {str(e)}")
            self._update_progress("lesson_shell", "error", f"Error: {str(e)}")
            raise

    async def _generate_rough_draft(self, lesson_shell: str) -> str:
        """
        Step 3: Generate Rough Draft.

        Args:
            lesson_shell: The lesson shell generated in step 2

        Returns:
            The generated rough draft
        """
        self._update_progress("rough_draft", "starting", "Generating rough draft")

        try:
            # Get the rough draft prompt template
            template = self.prompt_service.get_prompt("rough_draft")
            if not template:
                raise ValueError("Rough draft prompt template not found")

            # Prepare variables for the template
            variables = {"LESSON_SHELL": lesson_shell}

            # Extract API parameters from the template with safer token limits
            api_params = self._extract_api_params(template)

            # Limit max_tokens to 4000 to work with claude-3-sonnet
            if api_params.get("max_tokens", 0) > 4000:
                api_params["max_tokens"] = 4000
                self.logger.info("Reduced max_tokens to 4000 for compatibility")

            # Extract system prompt from the template
            system_prompt = self._extract_system_prompt(template)
            if system_prompt:
                api_params["prompt_type"] = "with_system"
                api_params["system_prompt"] = system_prompt

            # Extract the template part from the <template> tags
            template_part_match = re.search(
                r"<template>(.*?)</template>", template, re.DOTALL
            )
            if not template_part_match:
                raise ValueError("Could not find <template> tags in rough draft prompt")

            template_part = template_part_match.group(1).strip()

            # Replace variables in the template part
            for key, value in variables.items():
                template_part = template_part.replace(f"{{{{{key}}}}}", value)

            # Call the LLM with retry
            self.logger.info("Calling LLM for rough draft generation")
            response = await self._call_llm_with_retry(template_part, api_params)

            # Extract content from <lesson_content> tags if present
            content_match = re.search(
                r"<lesson_content>(.*?)</lesson_content>", response, re.DOTALL
            )
            if content_match:
                response = content_match.group(1).strip()

            # Validate the output
            is_valid, message = await self._validate_output(response, "rough_draft")
            if not is_valid:
                self.logger.warning(f"Rough draft validation failed: {message}")
                self._update_progress(
                    "rough_draft", "warning", f"Validation issue: {message}"
                )
                # Continue anyway but log the warning

            # Write the rough draft to a file
            rough_draft_file = os.path.join(
                self.lesson_dir, f"{self.lesson_id}_rough_draft.md"
            )
            with open(rough_draft_file, "w", encoding="utf-8") as f:
                f.write(response)

            self._update_progress("rough_draft", "success", "Rough draft generated")
            return response

        except Exception as e:
            self.logger.error(f"Error generating rough draft: {str(e)}")
            self._update_progress("rough_draft", "error", f"Error: {str(e)}")
            raise

    async def _generate_expanded_draft(self, rough_draft: str) -> str:
        """
        Step 4: Generate Expanded Draft.

        Args:
            rough_draft: The rough draft generated in step 3

        Returns:
            The generated expanded draft
        """
        self._update_progress("expanded_draft", "starting", "Generating expanded draft")

        try:
            # Get the expanded draft prompt template
            template = self.prompt_service.get_prompt("expanded_draft")
            if not template:
                raise ValueError("Expanded draft prompt template not found")

            # Prepare variables for the template
            variables = {"LESSON": rough_draft}

            # Extract API parameters from the template with safer token limits
            api_params = self._extract_api_params(template)

            # Limit max_tokens to 4000 to work with claude-3-sonnet
            if api_params.get("max_tokens", 0) > 4000:
                api_params["max_tokens"] = 4000
                self.logger.info("Reduced max_tokens to 4000 for compatibility")

            # Extract system prompt from the template
            system_prompt = self._extract_system_prompt(template)
            if system_prompt:
                api_params["prompt_type"] = "with_system"
                api_params["system_prompt"] = system_prompt

            # Prepare the prompt with variable substitution by manually replacing {{VARIABLE}} format
            prompt = template
            for key, value in variables.items():
                prompt = prompt.replace(f"{{{{{key}}}}}", value)

            # Use only the user message part for the API call
            user_message = self._extract_user_message(prompt)
            if not user_message:
                raise ValueError("Failed to extract user message from template")

            # Call the LLM with retry
            self.logger.info("Calling LLM for expanded draft generation")
            response = await self._call_llm_with_retry(user_message, api_params)

            # Extract content from <expanded_lesson> tags if present
            content_match = re.search(
                r"<expanded_lesson>(.*?)</expanded_lesson>", response, re.DOTALL
            )
            if content_match:
                response = content_match.group(1).strip()

            # Validate the output
            is_valid, message = await self._validate_output(response, "expanded_draft")
            if not is_valid:
                self.logger.warning(f"Expanded draft validation failed: {message}")
                self._update_progress(
                    "expanded_draft", "warning", f"Validation issue: {message}"
                )
                # Continue anyway but log the warning

            # Write the expanded draft to a file
            expanded_draft_file = os.path.join(
                self.lesson_dir, f"{self.lesson_id}_expanded_draft.md"
            )
            with open(expanded_draft_file, "w", encoding="utf-8") as f:
                f.write(response)

            self._update_progress(
                "expanded_draft", "success", "Expanded draft generated"
            )
            return response

        except Exception as e:
            self.logger.error(f"Error generating expanded draft: {str(e)}")
            self._update_progress("expanded_draft", "error", f"Error: {str(e)}")
            raise

    def _extract_api_params(self, template: str) -> Dict[str, Any]:
        """Extract API parameters from the template."""
        api_params = {"temperature": 0.7, "max_tokens": 2000}

        # Look for API Parameters section
        api_params_match = re.search(
            r"## API Parameters\s*\n(.*?)(?:\n##|\Z)", template, re.DOTALL
        )
        if api_params_match:
            api_params_text = api_params_match.group(1)

            # Extract temperature
            temp_match = re.search(r"Temperature: ([\d\.]+)", api_params_text)
            if temp_match:
                api_params["temperature"] = float(temp_match.group(1))

            # Extract max tokens
            tokens_match = re.search(r"Max Tokens: (\d+)", api_params_text)
            if tokens_match:
                # Cap max tokens at 4000 for safety with Claude 3 Sonnet
                api_params["max_tokens"] = min(int(tokens_match.group(1)), 4000)

            # Extract thinking budget if present
            thinking_match = re.search(
                r"Thinking: Enabled \(budget: (\d+) tokens\)", api_params_text
            )
            if thinking_match:
                api_params["thinking_budget"] = int(thinking_match.group(1))

        return api_params

    def _extract_system_prompt(self, template: str) -> Optional[str]:
        """Extract system prompt from the template."""
        system_prompt_match = re.search(
            r"## System Prompt\s*\n(.*?)(?:\n##|\Z)", template, re.DOTALL
        )
        if system_prompt_match:
            return system_prompt_match.group(1).strip()
        return None

    def _extract_user_message(self, template: str) -> Optional[str]:
        """Extract user message from the template."""
        user_message_match = re.search(
            r"## User Message Template\s*\n(.*?)(?:\n##|\Z)", template, re.DOTALL
        )
        if user_message_match:
            return user_message_match.group(1).strip()
        return None

    async def run_pipeline(
        self,
        module: str,
        lesson_objective: str,
        lesson_topics: str,
        title: str,
        course_context: Dict[str, str],
    ) -> Dict[str, Any]:
        """
        Run the draft generation pipeline.

        Args:
            module: The module name
            lesson_objective: The lesson objective
            lesson_topics: The lesson topics
            title: The lesson title
            course_context: Course context information

        Returns:
            Dictionary with pipeline results
        """
        self.logger.info(
            f"Starting draft generation pipeline for lesson: {self.lesson_id}"
        )

        try:
            # Step 1: Generate Learning Outcomes
            los = await self._generate_learning_outcomes(
                module, lesson_objective, lesson_topics
            )

            # Step 2: Generate Lesson Shell
            shell = await self._generate_lesson_shell(los, title)

            # Step 3: Generate Rough Draft
            rough_draft = await self._generate_rough_draft(shell)

            # Step 4: Generate Expanded Draft
            expanded_draft = await self._generate_expanded_draft(rough_draft)

            self.logger.info(
                f"Draft generation pipeline completed for lesson: {self.lesson_id}"
            )

            return {
                "status": "success",
                "message": "Draft generation complete",
                "files": {
                    "learning_outcomes": f"{self.lesson_id}_los.md",
                    "lesson_shell": f"{self.lesson_id}_shell.md",
                    "rough_draft": f"{self.lesson_id}_rough_draft.md",
                    "expanded_draft": f"{self.lesson_id}_expanded_draft.md",
                },
                "lesson_id": self.lesson_id,
            }
        except Exception as e:
            self.logger.error(f"Pipeline failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Pipeline failed: {str(e)}",
                "step": self.current_step,
                "lesson_id": self.lesson_id,
            }


class PolishingPipeline:
    """
    Polishing pipeline service that takes the human-edited expanded draft
    and generates the final polished content.

    This is a stub for future implementation.
    """

    def __init__(
        self,
        course_dir: str,
        lesson_id: str,
        llm_provider: Optional[str] = None,
        model: Optional[str] = None,
    ):
        """
        Initialize the polishing pipeline.

        Args:
            course_dir: Directory containing the course
            lesson_id: Identifier for the lesson
            llm_provider: LLM provider to use (defaults to course configuration)
            model: Model to use (defaults to course configuration)
        """
        self.logger = logging.getLogger(__name__)
        self.course_dir = course_dir
        self.lesson_id = lesson_id
        self.llm_provider = llm_provider
        self.model = model

        # Initialize services
        self.llm_service_provider = LLMServiceProvider()
        self.prompt_service = PromptService()
        self.file_service = FileService()

        # Set up lesson directory
        self.lesson_dir = os.path.join(course_dir, "lessons")

        # Track the current step
        self.current_step = None
        self.log_file = os.path.join(course_dir, "polish_logs.jsonl")

    async def run_pipeline(
        self,
        expanded_draft_path: str,
        learning_outcomes_path: str,
        course_context: Dict[str, str],
    ) -> Dict[str, Any]:
        """
        Run the polishing pipeline.

        Args:
            expanded_draft_path: Path to the human-edited expanded draft
            learning_outcomes_path: Path to the learning outcomes
            course_context: Course context information

        Returns:
            Dictionary with pipeline results
        """
        self.logger.info(
            f"[STUB] Would run polishing pipeline for lesson: {self.lesson_id}"
        )

        # This is just a stub for future implementation
        return {
            "status": "not_implemented",
            "message": "Polishing pipeline not implemented yet",
            "lesson_id": self.lesson_id,
        }
