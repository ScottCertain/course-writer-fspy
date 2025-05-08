import asyncio
import logging
import os
import yaml
import sys
from datetime import datetime
from services.pipeline_service_fix import FixedLessonPipeline
from services.file_service import FileService
from services.anthropic_service_fix import FixedAnthropicLLMService

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for more verbose logging
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("pipeline_test_fixed2.log"),
    ],
)
logger = logging.getLogger(__name__)


# Define progress callback
def progress_callback(step, status, message):
    """Callback function to report pipeline progress."""
    print(f"[{status.upper()}] {step}: {message}")


async def run_test(course_dir, lesson_id):
    """Run a test of the fixed lesson pipeline."""

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

    # Create the pipeline with explicit fixed Anthropic provider and model
    pipeline = FixedLessonPipeline(
        course_dir=course_dir,
        lesson_id=lesson_id,
        llm_provider="anthropic",
        model="claude-3-sonnet-20240229",
    )

    # Set the progress callback
    pipeline.set_progress_callback(progress_callback)

    # Run the pipeline
    print(f"Starting FIXED lesson generation pipeline for lesson: {lesson_id}")
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
    course_name = "test_course_fixed2"
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
                "max_tokens": 4000,  # Reduced to safe value for claude-3-sonnet
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
    service = FixedAnthropicLLMService(model="claude-3-sonnet-20240229")

    try:
        # Simple test prompt
        response = await service.generate_text(
            "What is Retrieval-Augmented Generation (RAG) in one sentence?",
            temperature=0.7,
            max_tokens=100,
        )
        print(f"Response: {response}")
        print("✅ Fixed Anthropic service test succeeded!")
        return True
    except Exception as e:
        print(f"❌ Fixed Anthropic service test failed: {str(e)}")
        return False


if __name__ == "__main__":
    print("Starting fully fixed pipeline test with token limits...")

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
