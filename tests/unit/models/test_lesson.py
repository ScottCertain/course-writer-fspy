"""
Unit tests for the Lesson model class.
"""

import os
import pytest
from datetime import datetime

from models.lesson import Lesson


class TestLesson:
    """Tests for the Lesson class."""

    def test_init(self):
        """Test initialization with required parameters."""
        lesson = Lesson(number=1, title="Test Lesson", learning_outcomes=["Outcome 1"])

        assert lesson.number == 1
        assert lesson.title == "Test Lesson"
        assert lesson.learning_outcomes == ["Outcome 1"]
        assert lesson.has_shell is False
        assert lesson.has_rough_draft is False

    def test_init_with_optional_params(self):
        """Test initialization with all parameters."""
        learning_outcomes = ["Outcome 1", "Outcome 2"]

        lesson = Lesson(
            number=1,
            title="Test Lesson",
            learning_outcomes=learning_outcomes,
            has_shell=True,
            has_rough_draft=True,
            has_expanded_draft=True,
            has_quizzes=True,
            has_activities=True,
        )

        assert lesson.number == 1
        assert lesson.title == "Test Lesson"
        assert lesson.learning_outcomes == learning_outcomes
        assert lesson.has_shell is True
        assert lesson.has_rough_draft is True
        assert lesson.has_expanded_draft is True
        assert lesson.has_quizzes is True
        assert lesson.has_activities is True

    def test_to_dict(self):
        """Test converting Lesson object to dictionary."""
        learning_outcomes = ["Outcome 1", "Outcome 2"]

        lesson = Lesson(
            number=1,
            title="Test Lesson",
            learning_outcomes=learning_outcomes,
            has_shell=True,
            has_rough_draft=True,
        )

        lesson_dict = lesson.to_dict()

        assert lesson_dict["number"] == 1
        assert lesson_dict["title"] == "Test Lesson"
        assert lesson_dict["learning_outcomes"] == learning_outcomes
        assert lesson_dict["has_shell"] is True
        assert lesson_dict["has_rough_draft"] is True

    def test_from_dict(self):
        """Test creating Lesson object from dictionary."""
        learning_outcomes = ["Outcome 1", "Outcome 2"]

        lesson_dict = {
            "number": 1,
            "title": "Test Lesson",
            "learning_outcomes": learning_outcomes,
            "has_shell": True,
            "has_rough_draft": True,
        }

        lesson = Lesson.from_dict(lesson_dict)

        assert lesson.number == 1
        assert lesson.title == "Test Lesson"
        assert lesson.learning_outcomes == learning_outcomes
        assert lesson.has_shell is True
        assert lesson.has_rough_draft is True

    def test_from_dict_minimal(self):
        """Test creating Lesson object from dictionary with minimal fields."""
        lesson_dict = {
            "number": 1,
            "title": "Test Lesson",
            "learning_outcomes": ["Learn X"],
        }

        lesson = Lesson.from_dict(lesson_dict)

        assert lesson.number == 1
        assert lesson.title == "Test Lesson"
        assert lesson.learning_outcomes == ["Learn X"]
        assert lesson.has_shell is False
        assert lesson.has_rough_draft is False

    def test_file_path(self):
        """Test generating file paths for different file types."""
        lesson = Lesson(
            number=1,
            title="Test Lesson",
            learning_outcomes=["Learn X"],
        )

        course_dir = "courses/test_course"

        # Test shell file path
        assert lesson.file_path(course_dir, "shell").endswith("lesson_01_shell.md")
        assert "lessons" in lesson.file_path(course_dir, "shell")

        # Test rough draft file path
        assert lesson.file_path(course_dir, "rough").endswith("lesson_01_rough.md")

        # Test expanded draft file path
        assert lesson.file_path(course_dir, "expanded").endswith(
            "lesson_01_expanded.md"
        )

        # Test quiz file path
        assert lesson.file_path(course_dir, "quiz1").endswith("lesson_01_quiz1.md")
