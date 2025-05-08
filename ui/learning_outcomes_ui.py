import streamlit as st
import os
import re
import logging
import asyncio
import json
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

from models.course import Course
from models.lesson import Lesson
from services.file_service import FileService
from services.draft_pipeline_service import DraftPipeline
from services.prompt_service import PromptService


def render_learning_outcomes() -> None:
    """
    Render the learning outcomes screen.
    This screen allows users to create, view, edit, and manage learning outcomes for lessons.
    """
    st.header("Learning Outcomes")

    # Initialize services
    file_service = FileService()
    prompt_service = PromptService()

    # Setup logger
    logger = logging.getLogger(__name__)

    # Check if a course is loaded
    if "course" not in st.session_state or st.session_state.course is None:
        st.warning("Please create or load a course first.")
        if st.button("Go to Course Metadata"):
            st.session_state.workflow_step = "Course Metadata"
            st.rerun()
        return

    # Get the course from session state
    course = st.session_state.course
    course_dir = st.session_state.course_dir

    # Display course title
    st.subheader(f"Course: {course.title}")

    # Initialize lessons list in session state if not exists
    if "lessons" not in st.session_state:
        st.session_state.lessons = []
        # Load existing lessons if available
        lesson_numbers = file_service.list_lessons(course_dir)
        if lesson_numbers:
            for num in lesson_numbers:
                lesson_metadata_path = os.path.join(
                    course_dir, "lessons", f"lesson_{num:02d}_metadata.yaml"
                )
                if os.path.exists(lesson_metadata_path):
                    try:
                        lesson = file_service.load_lesson(lesson_metadata_path)
                        st.session_state.lessons.append(lesson)
                    except Exception as e:
                        logger.error(f"Error loading lesson {num}: {e}")

    # SECTION 1: LESSON SELECTION AND CREATION
    with st.container():
        col1, col2 = st.columns([3, 1])

        with col1:
            # Prepare list of lessons for selection
            if st.session_state.lessons:
                lesson_options = [
                    f"Lesson {lesson.number}: {lesson.title}"
                    for lesson in st.session_state.lessons
                ]
                lesson_options.insert(0, "Create New Lesson")

                # Store previous selection
                previous_selection = st.session_state.get(
                    "previous_lesson_selection", "Create New Lesson"
                )

                # Lesson selection dropdown
                selected_option = st.selectbox(
                    "Select or create a lesson",
                    options=lesson_options,
                    index=0,
                    key="lesson_selection",
                )

                # Check if user switched to "Create New Lesson" from another option
                if (
                    selected_option == "Create New Lesson"
                    and previous_selection != "Create New Lesson"
                ):
                    # Clear current lesson from session state
                    if "current_lesson" in st.session_state:
                        st.session_state.current_lesson = None
                    logger.info("Switched to Create New Lesson - resetting form fields")

                # Update previous selection for next render
                st.session_state.previous_lesson_selection = selected_option
            else:
                selected_option = "Create New Lesson"
                st.info("No existing lessons found. Create a new one.")

        with col2:
            if st.button(
                "Load Lesson", disabled=(selected_option == "Create New Lesson")
            ):
                if selected_option != "Create New Lesson":
                    try:
                        # Extract lesson number from selection
                        lesson_num = int(
                            selected_option.split(":")[0].replace("Lesson ", "").strip()
                        )
                        # Find the lesson in session state
                        for lesson in st.session_state.lessons:
                            if lesson.number == lesson_num:
                                st.session_state.current_lesson = lesson
                                logger.info(f"Loaded lesson: {lesson.title}")
                                st.success(
                                    f"Successfully loaded lesson: {lesson.title}"
                                )
                                st.rerun()
                                break
                    except Exception as e:
                        logger.error(f"Error loading lesson: {e}")
                        st.error(f"Error loading lesson: {e}")

    # SECTION 2: LESSON DETAILS FORM
    # If we have a lesson in session state, use it to populate the form
    if (
        "current_lesson" in st.session_state
        and st.session_state.current_lesson is not None
    ):
        lesson = st.session_state.current_lesson
        default_number = lesson.number
        default_title = lesson.title
        default_learning_outcomes = lesson.learning_outcomes

        # Set other default values for existing lesson
        if "lesson_module" in st.session_state:
            default_module = st.session_state.lesson_module
        else:
            default_module = ""

        if "lesson_objective" in st.session_state:
            default_objective = st.session_state.lesson_objective
        else:
            default_objective = ""

        if "lesson_topics" in st.session_state:
            default_topics = st.session_state.lesson_topics
        else:
            default_topics = ""

        is_new_lesson = False
    else:
        # Default values for new lesson
        default_number = len(st.session_state.lessons) + 1
        default_title = ""
        default_learning_outcomes = []
        default_module = ""
        default_objective = ""
        default_topics = ""
        is_new_lesson = True

    # Create form for lesson details
    with st.form("lesson_details_form"):
        st.subheader("Lesson Details")

        # Lesson number and title
        col1, col2 = st.columns(2)
        with col1:
            lesson_number = st.number_input(
                "Lesson Number *", min_value=1, value=default_number, step=1
            )

        with col2:
            lesson_title = st.text_input("Lesson Title *", value=default_title)

        # Module, objective, and topics for LO generation
        st.subheader("Learning Outcomes Generation")
        st.info(
            "The following fields are used to generate learning outcomes. They are not required if you plan to enter learning outcomes manually."
        )

        module = st.text_input(
            "Module",
            value=default_module,
            help="The module or section this lesson belongs to",
            key="lesson_module",
        )

        objective = st.text_area(
            "Lesson Objective",
            value=default_objective,
            help="The main objective or goal of this lesson",
            key="lesson_objective",
        )

        topics = st.text_area(
            "Lesson Topics",
            value=default_topics,
            help="List of topics covered in this lesson (one per line)",
            key="lesson_topics",
        )

        # Submit button
        submitted = st.form_submit_button("Save Lesson Details")

        if submitted:
            # Validate required fields
            if not lesson_title:
                st.error("Please enter a lesson title")
            else:
                try:
                    # Create or update the lesson
                    learning_outcomes = (
                        default_learning_outcomes if not is_new_lesson else []
                    )

                    lesson = Lesson(
                        number=lesson_number,
                        title=lesson_title,
                        learning_outcomes=learning_outcomes,
                    )

                    # Save to session state
                    st.session_state.current_lesson = lesson

                    # Update or add to lessons list
                    lesson_updated = False
                    for i, existing_lesson in enumerate(st.session_state.lessons):
                        if existing_lesson.number == lesson_number:
                            st.session_state.lessons[i] = lesson
                            lesson_updated = True
                            break

                    if not lesson_updated:
                        st.session_state.lessons.append(lesson)

                    # Save to file system
                    file_service.save_lesson(lesson, course_dir)

                    logger.info(f"Saved lesson: {lesson.title}")
                    st.success(f"Successfully saved lesson: {lesson.title}")
                    st.rerun()

                except Exception as e:
                    logger.error(f"Error saving lesson: {e}")
                    st.error(f"Error saving lesson: {e}")

    # SECTION 3: LEARNING OUTCOMES MANAGEMENT
    if (
        "current_lesson" in st.session_state
        and st.session_state.current_lesson is not None
    ):
        lesson = st.session_state.current_lesson

        st.subheader("Learning Outcomes")

        # LO Generation UI
        with st.container():
            st.markdown("#### Generate Learning Outcomes")

            if st.button(
                "Generate Learning Outcomes",
                disabled=not (module and objective and topics),
            ):
                if not (module and objective and topics):
                    st.warning(
                        "Please fill in Module, Objective, and Topics to generate learning outcomes"
                    )
                else:
                    try:
                        with st.spinner("Generating learning outcomes..."):
                            # Create a unique lesson ID for the pipeline
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            temp_lesson_id = f"temp_lesson_{timestamp}"

                            # Create pipeline
                            pipeline = DraftPipeline(
                                course_dir=course_dir,
                                lesson_id=temp_lesson_id,
                                llm_provider=course.llm_config.provider,
                                model=course.llm_config.model,
                            )

                            # Progress indicator
                            progress_placeholder = st.empty()

                            # Define progress callback
                            def progress_callback(step, status, message):
                                progress_placeholder.info(
                                    f"[{status.upper()}] {step}: {message}"
                                )

                            # Set progress callback
                            pipeline.set_progress_callback(progress_callback)

                            # Run just the learning outcomes generation part
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            los = loop.run_until_complete(
                                pipeline._generate_learning_outcomes(
                                    module=module,
                                    lesson_objective=objective,
                                    lesson_topics=topics,
                                )
                            )
                            loop.close()

                            # Parse learning outcomes from the generated text
                            extracted_los = extract_learning_outcomes(los)

                            if extracted_los:
                                # Update lesson with new learning outcomes
                                lesson.learning_outcomes = extracted_los

                                # Save updated lesson
                                file_service.save_lesson(lesson, course_dir)

                                # Save the actual LO file for reference
                                los_file = lesson.file_path(course_dir, "LOs")
                                with open(los_file, "w", encoding="utf-8") as f:
                                    f.write(los)

                                st.session_state.current_lesson = lesson
                                st.success("Learning outcomes generated and saved!")
                                st.rerun()
                            else:
                                st.error(
                                    "Failed to extract learning outcomes from generated text"
                                )

                    except Exception as e:
                        logger.error(f"Error generating learning outcomes: {e}")
                        st.error(f"Error generating learning outcomes: {e}")

        # Display and edit existing learning outcomes
        if lesson.learning_outcomes:
            st.markdown("#### Current Learning Outcomes")

            # Initialize expanded states if not exists
            if "lo_expanded" not in st.session_state:
                st.session_state.lo_expanded = [False] * len(lesson.learning_outcomes)

            # Add more expanded states if needed
            while len(st.session_state.lo_expanded) < len(lesson.learning_outcomes):
                st.session_state.lo_expanded.append(False)

            # Display each learning outcome
            for i, lo in enumerate(lesson.learning_outcomes):
                with st.expander(
                    f"LO {i+1}: {lo.split(':', 1)[1].strip() if ':' in lo else lo}",
                    expanded=st.session_state.lo_expanded[i],
                ):
                    # Edit this learning outcome
                    edited_lo = st.text_area(
                        f"Learning Outcome {i+1}", value=lo, key=f"lo_{i}"
                    )

                    col1, col2 = st.columns([1, 4])

                    with col1:
                        if st.button(f"Update", key=f"update_lo_{i}"):
                            # Update this learning outcome
                            lesson.learning_outcomes[i] = edited_lo
                            file_service.save_lesson(lesson, course_dir)
                            st.success(f"Updated learning outcome {i+1}")
                            st.session_state.lo_expanded[i] = False
                            st.rerun()

                    with col2:
                        if st.button(f"Delete", key=f"delete_lo_{i}"):
                            # Remove this learning outcome
                            lesson.learning_outcomes.pop(i)
                            file_service.save_lesson(lesson, course_dir)
                            st.session_state.lo_expanded.pop(i)
                            st.success(f"Deleted learning outcome {i+1}")
                            st.rerun()

            # Button to manually add a new learning outcome
            if st.button("Add Learning Outcome"):
                lesson.learning_outcomes.append("LO: New learning outcome")
                file_service.save_lesson(lesson, course_dir)
                st.session_state.lo_expanded.append(True)  # Expand the new LO
                st.success("Added new learning outcome")
                st.rerun()
        else:
            st.info(
                "No learning outcomes yet. Generate them using the form above or add them manually."
            )

            if st.button("Add First Learning Outcome"):
                lesson.learning_outcomes.append("LO: New learning outcome")
                file_service.save_lesson(lesson, course_dir)
                if "lo_expanded" not in st.session_state:
                    st.session_state.lo_expanded = [True]
                else:
                    st.session_state.lo_expanded.append(True)
                st.success("Added new learning outcome")
                st.rerun()

        # Button to continue to content generation
        st.markdown("---")
        if st.button(
            "Continue to Content Generation", disabled=not lesson.learning_outcomes
        ):
            if not lesson.learning_outcomes:
                st.warning("Please add at least one learning outcome before proceeding")
            else:
                st.session_state.workflow_step = "Generate Content"
                st.rerun()


def extract_learning_outcomes(text: str) -> List[str]:
    """
    Extract learning outcomes from generated text.

    Args:
        text: The generated text containing learning outcomes

    Returns:
        List of extracted learning outcomes
    """
    los = []

    # Look for patterns like "LO 1:" or "Learning Outcome 1:"
    lo_pattern = re.compile(
        r"(?:LO\s+\d+:|Learning Outcome\s+\d+:)(.*?)(?=(?:LO\s+\d+:|Learning Outcome\s+\d+:)|$)",
        re.DOTALL,
    )

    matches = lo_pattern.findall(text)
    if matches:
        for match in matches:
            lo_text = match.strip()

            # Check if the LO has multiple paragraphs (key concepts, etc.)
            # We'll keep only the first paragraph as the main LO
            paragraphs = [p.strip() for p in lo_text.split("\n\n") if p.strip()]
            main_lo = paragraphs[0] if paragraphs else lo_text

            # Create a formatted LO string
            formatted_lo = f"LO: {main_lo}"
            los.append(formatted_lo)

    # If the standard pattern didn't work, try a more lenient approach
    if not los:
        # Just split by numeric bullets or lines starting with "LO"
        bullet_pattern = re.compile(r"^\s*(?:\d+\.|\*|LO)\s+(.*?)$", re.MULTILINE)
        matches = bullet_pattern.findall(text)
        if matches:
            for match in matches:
                los.append(f"LO: {match.strip()}")

    return los
