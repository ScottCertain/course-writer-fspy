import streamlit as st
import os
import logging
import yaml
from dotenv import load_dotenv

from ui.course_ui import render_course_metadata, load_app_config
from ui.learning_outcomes_ui import render_learning_outcomes
from services.file_service import FileService

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# App title and configuration
st.set_page_config(
    page_title="CourseSmith",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)


def initialize_session_state():
    """Initialize session state variables if they don't exist."""
    if "workflow_step" not in st.session_state:
        st.session_state.workflow_step = "Course Metadata"
    if "course" not in st.session_state:
        st.session_state.course = None
    if "course_dir" not in st.session_state:
        st.session_state.course_dir = None
    if "current_lesson" not in st.session_state:
        st.session_state.current_lesson = None
    if "app_config" not in st.session_state:
        st.session_state.app_config = load_app_config()


def main():
    """Main application entry point."""
    # Initialize session state
    initialize_session_state()

    # App header
    st.title("CourseSmith")
    st.markdown("AI-Powered Course Writing Assistant")

    # Sidebar navigation
    st.sidebar.title("Navigation")

    # Navigation options
    nav_options = [
        "Course Metadata",
        "Learning Outcomes",
        "Generate Content",
    ]

    # Update workflow step based on sidebar selection
    workflow_step = st.sidebar.radio(
        "Workflow", nav_options, index=nav_options.index(st.session_state.workflow_step)
    )
    st.session_state.workflow_step = workflow_step

    # Display appropriate UI based on workflow step
    if workflow_step == "Course Metadata":
        render_course_metadata()
    elif workflow_step == "Learning Outcomes":
        render_learning_outcomes()
    else:  # Generate Content
        # TODO: Implement content generation UI once completed
        st.warning("Content Generation UI not yet implemented")

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**CourseSmith v0.1.0**")
    st.sidebar.markdown("AI-Powered Course Writing Assistant")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        st.error(f"An error occurred: {e}")
