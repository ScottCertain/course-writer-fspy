import os
import logging
from typing import Dict, Any, List, Optional
import re
import string


class PromptService:
    """
    Service for managing and rendering prompt templates.
    Loads templates from files and renders them with variable substitution.
    """

    def __init__(self, prompts_dir: str = "prompts"):
        """
        Initialize the prompt service.

        Args:
            prompts_dir: Directory containing prompt template files
        """
        self.prompts_dir = prompts_dir
        self.logger = logging.getLogger(__name__)
        self.templates = {}
        self._load_templates()

    def _load_templates(self) -> None:
        """Load all prompt templates from the prompts directory."""
        if not os.path.exists(self.prompts_dir):
            self.logger.warning(f"Prompts directory {self.prompts_dir} does not exist.")
            return

        prompt_files = [f for f in os.listdir(self.prompts_dir) if f.endswith(".md")]

        for filename in prompt_files:
            prompt_name = os.path.splitext(filename)[0]
            path = os.path.join(self.prompts_dir, filename)
            try:
                with open(path, "r", encoding="utf-8") as file:
                    self.templates[prompt_name] = file.read()
                self.logger.info(f"Loaded prompt template: {prompt_name}")
            except Exception as e:
                self.logger.error(f"Error loading prompt template {prompt_name}: {e}")

    def reload_templates(self) -> None:
        """Reload all prompt templates from disk."""
        self.templates = {}
        self._load_templates()

    def get_prompt(self, prompt_name: str) -> Optional[str]:
        """
        Get a prompt template by name.

        Args:
            prompt_name: Name of the prompt template

        Returns:
            The prompt template text, or None if not found
        """
        if prompt_name not in self.templates:
            self.logger.warning(f"Prompt template {prompt_name} not found.")
            return None

        return self.templates[prompt_name]

    def render_prompt(
        self, prompt_name: str, variables: Dict[str, Any]
    ) -> Optional[str]:
        """
        Render a prompt template with variables.

        Args:
            prompt_name: Name of the prompt template
            variables: Dictionary of variables to substitute

        Returns:
            The rendered prompt, or None if the template is not found
        """
        template = self.get_prompt(prompt_name)
        if not template:
            return None

        # Convert all variables to strings
        str_variables = {k: str(v) for k, v in variables.items()}

        # Simple string template substitution
        try:
            # Convert the template to a string.Template
            template_obj = string.Template(template)

            # Render the template with the variables
            rendered = template_obj.safe_substitute(str_variables)
            return rendered
        except Exception as e:
            self.logger.error(f"Error rendering template {prompt_name}: {e}")
            return template

    def chain_prompts(
        self, prompt_names: List[str], variables: Dict[str, Any]
    ) -> Optional[str]:
        """
        Chain multiple prompts together.

        Args:
            prompt_names: List of prompt template names to chain
            variables: Dictionary of variables to substitute

        Returns:
            The combined rendered prompt, or None if any template is not found
        """
        rendered_prompts = []

        for prompt_name in prompt_names:
            rendered = self.render_prompt(prompt_name, variables)
            if rendered is None:
                return None
            rendered_prompts.append(rendered)

        return "\n\n".join(rendered_prompts)

    def add_template(self, prompt_name: str, template_text: str) -> None:
        """
        Add a new template to the service.

        Args:
            prompt_name: Name of the prompt template
            template_text: The template text
        """
        self.templates[prompt_name] = template_text
        self.logger.info(f"Added prompt template: {prompt_name}")

        # Also save to disk
        path = os.path.join(self.prompts_dir, f"{prompt_name}.md")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        try:
            with open(path, "w", encoding="utf-8") as file:
                file.write(template_text)
            self.logger.info(f"Saved prompt template to disk: {prompt_name}")
        except Exception as e:
            self.logger.error(f"Error saving prompt template {prompt_name}: {e}")
