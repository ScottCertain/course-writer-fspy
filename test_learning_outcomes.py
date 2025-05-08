import asyncio
import logging
import os
import sys
from datetime import datetime
from services.file_service import FileService
from services.draft_pipeline_service import DraftPipeline
from ui.learning_outcomes_ui import extract_learning_outcomes
from models.course import Course, LLMConfig
from models.lesson import Lesson

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("learning_outcomes_test.log"),
    ],
)
logger = logging.getLogger(__name__)


# Define progress callback
def progress_callback(step, status, message):
    """Callback function to report pipeline progress."""
    print(f"[{status.upper()}] {step}: {message}")


async def run_test():
    """Run a test of the learning outcomes functionality."""
    print("Testing Learning Outcomes functionality...")

    # Create file service
    file_service = FileService()

    # Create a test course
    course_name = "test_learning_outcomes"
    course_dir = os.path.join("courses", course_name)

    # Ensure the course directory exists
    os.makedirs(course_dir, exist_ok=True)
    os.makedirs(os.path.join(course_dir, "lessons"), exist_ok=True)

    # Create a course configuration
    llm_config = LLMConfig(
        provider="anthropic",
        model="claude-3-7-sonnet-20250219",  # Make sure this matches the model name in your configuration
        temperature=0.7,
        max_tokens=4000,
    )

    course = Course(
        title="Test Learning Outcomes Course",
        description="A test course for learning outcomes functionality",
        target_audience="Software developers interested in AI",
        author="Test Author",
        llm_config=llm_config,
    )

    # Save the course configuration
    file_service.save_course_config(course, course_dir)
    print(f"Created test course: {course.title}")

    # Create a test lesson
    lesson = Lesson(number=1, title="Introduction to RAG Systems", learning_outcomes=[])

    # Save the lesson
    file_service.save_lesson(lesson, course_dir)
    print(f"Created test lesson: {lesson.title}")

    # Test the learning outcomes generation
    try:
        # Set up test parameters
        module = "Retrieval-Augmented Generation"
        lesson_objective = "Help software developers understand and implement Retrieval-Augmented Generation for their applications"
        lesson_topics = """
        - Definition and components of RAG systems
        - Benefits of RAG for software applications
        - Implementation strategies for RAG in production
        - Evaluation and optimization of RAG pipelines
        """

        # Generate a unique lesson ID based on timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        lesson_id = f"test_lesson_{timestamp}"

        # Create the pipeline
        pipeline = DraftPipeline(
            course_dir=course_dir,
            lesson_id=lesson_id,
            llm_provider="anthropic",
            model="claude-3-7-sonnet-20250219",
        )

        # Set the progress callback
        pipeline.set_progress_callback(progress_callback)

        print("Generating learning outcomes...")
        start_time = datetime.now()

        # Generate learning outcomes
        los = await pipeline._generate_learning_outcomes(
            module=module,
            lesson_objective=lesson_objective,
            lesson_topics=lesson_topics,
        )

        end_time = datetime.now()
        duration = end_time - start_time
        print(f"Generation completed in {duration}")

        # Test the extraction functionality
        print("\nTesting learning outcomes extraction...")
        extracted_los = extract_learning_outcomes(los)

        print(f"Extracted {len(extracted_los)} learning outcomes:")
        for i, lo in enumerate(extracted_los):
            print(f"{i+1}. {lo}")

        # Update the lesson with the learning outcomes
        lesson.learning_outcomes = extracted_los
        file_service.save_lesson(lesson, course_dir)
        print("\nUpdated lesson with extracted learning outcomes")

        # Write the raw learning outcomes to a file for inspection
        los_path = os.path.join(course_dir, "lessons", f"{lesson_id}_los.md")
        with open(los_path, "w", encoding="utf-8") as f:
            f.write(los)
        print(f"Raw learning outcomes written to: {los_path}")

        print("\nTest completed successfully!")
        return True

    except Exception as e:
        logger.error(f"Error in learning outcomes test: {e}", exc_info=True)
        print(f"Test failed with error: {e}")
        return False


if __name__ == "__main__":
    print("===== Learning Outcomes Test =====")
    asyncio.run(run_test())
