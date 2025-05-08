import os
import yaml
from typing import Dict, Any, Optional, Union
import logging
from models.course import Course
from models.lesson import Lesson


class FileService:
    """
    Service for managing file operations related to courses and lessons.
    Handles file creation, reading, writing, and directory management.
    """

    def __init__(self, base_dir: str = "courses"):
        """
        Initialize the file service.

        Args:
            base_dir: Base directory for all courses
        """
        self.base_dir = base_dir
        self.logger = logging.getLogger(__name__)

    def create_course_directory(self, course_title: str) -> str:
        """
        Create the course directory structure.

        Args:
            course_title: Title of the course (will be used in directory name)

        Returns:
            Path to the created course directory
        """
        # Sanitize course title for directory name
        dir_name = course_title.lower().replace(" ", "_")
        course_dir = os.path.join(self.base_dir, dir_name)

        # Create main course directory
        os.makedirs(course_dir, exist_ok=True)
        self.logger.info(f"Created course directory: {course_dir}")

        # Create lessons subdirectory
        lessons_dir = os.path.join(course_dir, "lessons")
        os.makedirs(lessons_dir, exist_ok=True)
        self.logger.info(f"Created lessons directory: {lessons_dir}")

        return course_dir

    def save_course_config(
        self, course: Course, course_dir: Optional[str] = None
    ) -> str:
        """
        Save course configuration to YAML.

        Args:
            course: Course model to save
            course_dir: Directory to save to (if None, will be derived from course title)

        Returns:
            Path to the saved config file
        """
        if course_dir is None:
            course_dir = os.path.join(
                self.base_dir, course.title.lower().replace(" ", "_")
            )

        # Create directory if it doesn't exist
        os.makedirs(course_dir, exist_ok=True)

        # Path to config file
        config_path = os.path.join(course_dir, "course_config.yaml")

        # Convert to dict and save as YAML
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(course.to_dict(), f, default_flow_style=False, sort_keys=False)

        self.logger.info(f"Saved course config to: {config_path}")
        return config_path

    def load_course_config(self, config_path: str) -> Course:
        """
        Load course configuration from YAML.

        Args:
            config_path: Path to the course config YAML file

        Returns:
            Loaded Course model
        """
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            course = Course.from_dict(data)
            self.logger.info(f"Loaded course config from: {config_path}")
            return course

        except Exception as e:
            self.logger.error(f"Error loading course config: {e}")
            raise

    def save_markdown(self, content: str, file_path: str) -> str:
        """
        Save markdown content to a file.

        Args:
            content: Markdown content to save
            file_path: Path to save the file

        Returns:
            Path to the saved file
        """
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        self.logger.info(f"Saved markdown to: {file_path}")
        return file_path

    def load_markdown(self, file_path: str) -> str:
        """
        Load markdown content from a file.

        Args:
            file_path: Path to the markdown file

        Returns:
            Content of the markdown file
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            self.logger.info(f"Loaded markdown from: {file_path}")
            return content

        except Exception as e:
            self.logger.error(f"Error loading markdown: {e}")
            raise

    def save_lesson(self, lesson: Lesson, course_dir: str) -> str:
        """
        Save lesson metadata to YAML.

        Args:
            lesson: Lesson model to save
            course_dir: Course directory

        Returns:
            Path to the saved lesson metadata file
        """
        # Ensure lessons directory exists
        lessons_dir = os.path.join(course_dir, "lessons")
        os.makedirs(lessons_dir, exist_ok=True)

        # Path to lesson metadata file
        lesson_number = f"{lesson.number:02d}"
        metadata_path = os.path.join(
            lessons_dir, f"lesson_{lesson_number}_metadata.yaml"
        )

        # Convert to dict and save as YAML
        with open(metadata_path, "w", encoding="utf-8") as f:
            yaml.dump(lesson.to_dict(), f, default_flow_style=False, sort_keys=False)

        self.logger.info(f"Saved lesson metadata to: {metadata_path}")
        return metadata_path

    def load_lesson(self, metadata_path: str) -> Lesson:
        """
        Load lesson metadata from YAML.

        Args:
            metadata_path: Path to the lesson metadata YAML file

        Returns:
            Loaded Lesson model
        """
        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            lesson = Lesson.from_dict(data)
            self.logger.info(f"Loaded lesson metadata from: {metadata_path}")
            return lesson

        except Exception as e:
            self.logger.error(f"Error loading lesson metadata: {e}")
            raise

    def list_courses(self) -> list:
        """
        List all available courses.

        Returns:
            List of course directory names
        """
        if not os.path.exists(self.base_dir):
            return []

        return [
            d
            for d in os.listdir(self.base_dir)
            if os.path.isdir(os.path.join(self.base_dir, d))
        ]

    def list_lessons(self, course_dir: str) -> list:
        """
        List all lessons in a course based on metadata files.

        Args:
            course_dir: Course directory

        Returns:
            List of lesson numbers
        """
        lessons_dir = os.path.join(course_dir, "lessons")
        if not os.path.exists(lessons_dir):
            return []

        # Find all lesson metadata files
        metadata_files = [
            f
            for f in os.listdir(lessons_dir)
            if f.endswith("_metadata.yaml") and f.startswith("lesson_")
        ]

        # Extract lesson numbers
        lesson_numbers = []
        for filename in metadata_files:
            # Extract the lesson number from the filename
            # Format is lesson_XX_metadata.yaml
            try:
                number_str = filename.split("_")[1]
                lesson_numbers.append(int(number_str))
            except (IndexError, ValueError):
                continue

        return sorted(lesson_numbers)
