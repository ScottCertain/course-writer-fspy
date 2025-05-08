from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import os


class Lesson(BaseModel):
    """Lesson data model representing a single lesson within a course."""

    number: int = Field(..., description="Lesson number")
    title: str = Field(..., description="Lesson title")
    learning_outcomes: List[str] = Field(
        ..., description="List of learning outcomes for the lesson"
    )

    # Generation status tracking
    has_shell: bool = Field(
        False, description="Whether the lesson shell has been generated"
    )
    has_rough_draft: bool = Field(
        False, description="Whether the rough draft has been generated"
    )
    has_expanded_draft: bool = Field(
        False, description="Whether the expanded draft has been generated"
    )
    has_quizzes: bool = Field(False, description="Whether quizzes have been generated")
    has_activities: bool = Field(
        False, description="Whether activities have been generated"
    )

    def file_path(self, course_dir: str, file_type: str) -> str:
        """
        Generate the appropriate file path for lesson outputs.

        Args:
            course_dir: Base course directory
            file_type: Type of file (LOs, shell, rough, expanded, quiz1, quiz2, quiz3, activities, solutions)

        Returns:
            Full file path for the requested lesson file
        """
        # Ensure lesson number is zero-padded to 2 digits
        lesson_number = f"{self.number:02d}"

        # Map of file types to file names
        file_name_map = {
            "LOs": f"lesson_{lesson_number}_LOs.md",
            "shell": f"lesson_{lesson_number}_shell.md",
            "rough": f"lesson_{lesson_number}_rough.md",
            "expanded": f"lesson_{lesson_number}_expanded.md",
            "quiz1": f"lesson_{lesson_number}_quiz1.md",
            "quiz2": f"lesson_{lesson_number}_quiz2.md",
            "quiz3": f"lesson_{lesson_number}_quiz3.md",
            "activities": f"lesson_{lesson_number}_activities.md",
            "solutions": f"lesson_{lesson_number}_solutions.md",
        }

        if file_type not in file_name_map:
            raise ValueError(f"Unsupported file type: {file_type}")

        # Construct full path
        return os.path.join(course_dir, "lessons", file_name_map[file_type])

    def to_dict(self) -> Dict[str, Any]:
        """Convert the lesson to a dictionary suitable for YAML serialization."""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Lesson":
        """Create a Lesson instance from a dictionary (loaded from YAML)."""
        return cls(**data)
