import asyncio
import logging
import os
import yaml
import sys
from datetime import datetime
from services.pipeline_service import LessonPipeline
from services.file_service import FileService
from services.anthropic_service import AnthropicLLMService
from services.llm_service_provider import LLMServiceProvider

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for more verbose logging
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("pipeline_test_fixed.log"),
    ],
)
logger = logging.getLogger(__name__)


# Override LLMServiceFactory's create_llm_service to use our fixed version
def fixed_create_llm_service(provider, model, api_key=None, *args, **kwargs):
    """Create a fixed version of the LLM service."""
    if provider.lower() == "anthropic":
        logger.info(f"Using fixed Anthropic service with model: {model}")
        return AnthropicLLMService(api_key=api_key, model=model)
    else:
        # Use the regular factory for other providers
        from services.llm_service import LLMServiceFactory

        return LLMServiceFactory.create_llm_service(
            provider, model, api_key, *args, **kwargs
        )


# Monkey patch the LLMServiceProvider
LLMServiceProvider._orig_get_llm_service = LLMServiceProvider.get_llm_service


def fixed_get_llm_service(self, provider=None, model=None, api_key=None, base_url=None):
    """Get LLM service using the fixed factory."""
    if provider and provider.lower() == "anthropic":
        llm_config = self.config.get("llm", {})
        provider_config = llm_config.get("models", {}).get(provider.lower(), {})

        # Use default model from config if not specified
        if model is None and "default_model" in provider_config:
            model = provider_config.get("default_model")

        # Create and return the fixed Anthropic service
        logger.info(
            f"Creating fixed Anthropic LLM service: {model or 'claude-3-sonnet-20240229'}"
        )
        return AnthropicLLMService(
            api_key=api_key, model=model or "claude-3-sonnet-20240229"
        )
    else:
        # Use the original method for other providers
        return self._orig_get_llm_service(provider, model, api_key, base_url)


# Apply the monkey patch
LLMServiceProvider.get_llm_service = fixed_get_llm_service


# Define progress callback
def progress_callback(step, status, message):
    """Callback function to report pipeline progress."""
    print(f"[{status.upper()}] {step}: {message}")


async def run_test(course_dir, lesson_id):
    """Run a test of the lesson pipeline."""

    # Set up test parameters
    module = "Introduction to Generative AI"
    lesson_objective = "Help software developers understand and implement Retrieval-Augmented Generation for their applications"
    lesson_topics = """
    - Definition and components of RAG systems
    - Benefits of RAG for software applications
    - Implementation strategies for RAG in production
    - Evaluation and optimization of RAG pipelines
    """
    title = "Implementing Retrieval-Augmented Generation (RAG) Systems"

    # Course context
    course_context = {
        "title": "Generative AI for Software Developers",
        "target_audience": "Experienced software developers",
        "skill_level": "Intermediate",
    }

    # Create the pipeline with anthropic provider explicitly specified
    pipeline = LessonPipeline(
        course_dir=course_dir,
        lesson_id=lesson_id,
        llm_provider="anthropic",
        model="claude-3-sonnet-20240229",  # Updated model name
    )

    # Set the progress callback
    pipeline.set_progress_callback(progress_callback)

    # Run the pipeline
    print(f"Starting lesson generation pipeline for lesson: {lesson_id}")
    start_time = datetime.now()

    result = await pipeline.run_pipeline(
        module=module,
        lesson_objective=lesson_objective,
        lesson_topics=lesson_topics,
        title=title,
        course_context=course_context,
    )

    end_time = datetime.now()
    duration = end_time - start_time

    # Report results
    if result["status"] == "success":
        print(f"✅ Pipeline completed successfully in {duration}")
        print("Generated files:")
        for file_type, file_name in result["files"].items():
            file_path = os.path.join(course_dir, "lessons", file_name)
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            print(f"  - {file_type}: {file_name} ({file_size/1024:.1f} KB)")
    else:
        print(f"❌ Pipeline failed at step '{result['step']}': {result['message']}")

    return result


def create_test_course():
    """Create a test course for pipeline testing."""

    # Create file service
    file_service = FileService()

    # Test course details
    course_name = "test_course_fixed"
    course_dir = os.path.join("courses", course_name)

    # Ensure the course directory exists
    os.makedirs(course_dir, exist_ok=True)
    os.makedirs(os.path.join(course_dir, "lessons"), exist_ok=True)

    # Create a simple course config if it doesn't exist
    config_path = os.path.join(course_dir, "course_config.yaml")
    if not os.path.exists(config_path):
        course_config = {
            "title": "Test Course",
            "description": "A test course for pipeline testing",
            "target_audience": "Developers",
            "skill_level": "Intermediate",
            "llm": {
                "provider": "anthropic",
                "model": "claude-3-sonnet-20240229",  # Updated model name
                "temperature": 0.7,
                "max_tokens": 15000,
            },
        }

        # Write the config to file
        with open(config_path, "w") as f:
            yaml.dump(course_config, f, default_flow_style=False)

    return course_dir


# Mini test to verify our fixed service works
async def test_fixed_anthropic_service():
    """Test the fixed Anthropic service directly."""
    print("Testing fixed Anthropic service...")

    # Create a test instance with the updated model name
    service = AnthropicLLMService(model="claude-3-sonnet-20240229")

    try:
        # Simple test prompt
        response = await service.generate_text(
            "Explain what RAG is in one sentence.", temperature=0.7, max_tokens=100
        )
        print(f"Response: {response}")
        print("✅ Fixed Anthropic service test succeeded!")
        return True
    except Exception as e:
        print(f"❌ Fixed Anthropic service test failed: {str(e)}")
        return False


if __name__ == "__main__":
    # Test the fixed Anthropic service first
    if asyncio.run(test_fixed_anthropic_service()):
        # Create a test course
        course_dir = create_test_course()

        # Generate a unique lesson ID based on timestamp
        lesson_id = f"test_lesson_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Run the pipeline test
        asyncio.run(run_test(course_dir, lesson_id))
    else:
        print("Skipping pipeline test due to Anthropic service test failure.")
