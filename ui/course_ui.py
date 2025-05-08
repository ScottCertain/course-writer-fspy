import streamlit as st
import os
import yaml
from typing import Optional, Dict, Any, List
import logging

from models.course import Course, LLMConfig
from services.file_service import FileService


def load_app_config() -> Dict[str, Any]:
    """
    Load the application configuration from YAML file.

    Returns:
        Dict containing the application configuration
    """
    config_path = os.path.join("config", "app_config.yaml")
    try:
        with open(config_path, "r") as file:
            return yaml.safe_load(file)
    except Exception as e:
        st.error(f"Error loading application configuration: {e}")
        return {}


def render_course_metadata() -> None:
    """
    Render the course metadata input form.
    Allows users to create or load a course.
    """
    st.header("Course Metadata")

    # Initialize services
    file_service = FileService()

    # Setup logger
    logger = logging.getLogger(__name__)

    # Load application configuration
    app_config = load_app_config()
    llm_config = app_config.get("llm", {})

    # Check if there are existing courses to load
    existing_courses = file_service.list_courses()

    # Add option to create a new course
    col1, col2 = st.columns([3, 1])

    with col1:
        if existing_courses:
            course_options = ["Create New Course"] + existing_courses

            # Store previous selection to detect changes
            previous_selection = st.session_state.get(
                "previous_course_selection", "Create New Course"
            )

            selected_option = st.selectbox(
                "Select or create a course",
                options=course_options,
                index=0,
                key="course_selection",
            )

            # Check if user switched to "Create New Course" from another option
            if (
                selected_option == "Create New Course"
                and previous_selection != "Create New Course"
            ):
                # Clear course from session state to reset form fields
                if "course" in st.session_state:
                    st.session_state.course = None
                if "course_dir" in st.session_state:
                    st.session_state.course_dir = None
                logger.info("Switched to Create New Course - resetting form fields")

            # Update previous selection for next render
            st.session_state.previous_course_selection = selected_option
        else:
            selected_option = "Create New Course"
            st.info("No existing courses found. Create a new one.")

    with col2:
        if st.button("Load Course", disabled=(selected_option == "Create New Course")):
            if selected_option != "Create New Course":
                try:
                    course_dir = os.path.join("courses", selected_option)
                    config_path = os.path.join(course_dir, "course_config.yaml")
                    course = file_service.load_course_config(config_path)
                    st.session_state.course = course
                    st.session_state.course_dir = course_dir
                    logger.info(f"Loaded course: {course.title}")
                    st.success(f"Successfully loaded course: {course.title}")
                    st.rerun()
                except Exception as e:
                    logger.error(f"Error loading course: {e}")
                    st.error(f"Error loading course: {e}")

    # If we have a course in session state, use it to populate the form
    if "course" in st.session_state and st.session_state.course is not None:
        course = st.session_state.course
        default_title = course.title
        default_description = course.description
        default_audience = course.target_audience
        default_language = course.language
        default_version = course.version
        default_author = course.author
        default_skill = course.skill_level
        default_prereq = course.prerequisites
        default_duration = course.estimated_duration
        default_provider = course.llm_config.provider
        default_model = course.llm_config.model
        default_temp = course.llm_config.temperature
        default_tokens = course.llm_config.max_tokens
    else:
        # Default values for new course
        default_title = ""
        default_description = ""
        default_audience = ""
        default_language = "English"
        default_version = "1.0"
        default_author = ""
        default_skill = ""
        default_prereq = ""
        default_duration = ""
        default_provider = "anthropic"
        default_model = "claude-3-7-sonnet"
        default_temp = 0.7
        default_tokens = 4000

    # Function to get model options for a given provider
    def get_model_options_for_provider(provider_name):
        # Get from config first
        provider_config = llm_config.get("models", {}).get(provider_name, {})
        model_opts = provider_config.get("available_models", [])

        # Fallback if config doesn't have models
        if not model_opts:
            if provider_name == "anthropic":
                model_opts = [
                    "claude-3-7-sonnet",
                    "claude-3.5-sonnet-2024-10-22",
                    "claude-3.5-haiku",
                ]
            elif provider_name == "openai":
                model_opts = ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
            elif provider_name == "ollama":
                model_opts = [
                    "gemma3:12b",
                    "codegemma:7b",
                    "phi4:latest",
                ]
            else:  # lmstudio
                model_opts = ["gemma-3-12b-it-qat"]
        return model_opts

    # Initialize additional LLM configurations in session state if not exist
    if "additional_llm_configs" not in st.session_state:
        st.session_state.additional_llm_configs = []

    # Initialize provider session state to manage model dropdown updates
    if "current_provider" not in st.session_state:
        st.session_state.current_provider = default_provider

    # Get available providers from config
    available_providers = list(llm_config.get("models", {}).keys())
    if not available_providers:
        available_providers = ["anthropic", "openai", "ollama", "lmstudio"]

    # LLM CONFIGURATION SECTION
    st.subheader("LLM Configuration")

    # Create tabs for primary and additional LLMs for better organization
    primary_tab, additional_tab = st.tabs(["Primary LLM", "Additional LLMs"])

    with primary_tab:
        # SECTION 1: PRIMARY LLM CONFIGURATION - Group provider and model together
        with st.container():
            # Callback to update model options when provider changes
            def on_provider_change():
                new_provider = st.session_state.primary_provider_select
                st.session_state.current_provider = new_provider
                # Update default model for this provider
                model_options = get_model_options_for_provider(new_provider)
                if model_options:
                    st.session_state.primary_model_select = model_options[0]

            # Create a two-column layout for provider and model
            col1, col2 = st.columns(2)

            with col1:
                # Provider selection
                provider = st.selectbox(
                    "LLM Provider *",
                    options=available_providers,
                    index=(
                        available_providers.index(default_provider)
                        if default_provider in available_providers
                        else 0
                    ),
                    key="primary_provider_select",
                    on_change=on_provider_change,
                )

            # Store model options in session state
            if "primary_model_select" not in st.session_state:
                model_options = get_model_options_for_provider(provider)
                if model_options:
                    if default_model in model_options:
                        st.session_state.primary_model_select = default_model
                    else:
                        st.session_state.primary_model_select = model_options[0]

            # Get the current model options based on selected provider
            model_options = get_model_options_for_provider(provider)

            with col2:
                # Model selection dropdown right next to provider
                model = st.selectbox(
                    "Model *", options=model_options, key="primary_model_select"
                )

            # Temperature and tokens in separate columns for compact layout
            col3, col4 = st.columns(2)

            with col3:
                temperature = st.slider(
                    "Temperature",
                    min_value=0.0,
                    max_value=1.0,
                    value=default_temp,
                    step=0.1,
                    help="Controls the randomness of the output (0 = deterministic, 1 = creative)",
                    key="primary_llm_temperature",
                )

            with col4:
                max_tokens = st.number_input(
                    "Max Tokens",
                    min_value=100,
                    max_value=10000,
                    value=default_tokens,
                    step=100,
                    help="Maximum number of tokens to generate",
                    key="primary_llm_max_tokens",
                )

    # SECTION 2: ADDITIONAL LLM CONFIGURATIONS
    with additional_tab:
        # Function to add a new LLM configuration
        def add_llm_config():
            st.session_state.additional_llm_configs.append(
                {
                    "provider": "anthropic",
                    "model": "claude-3-7-sonnet",
                    "temperature": 0.7,
                    "max_tokens": 4000,
                }
            )

        # Display all additional LLM configs
        if not st.session_state.additional_llm_configs:
            st.info(
                "No additional LLMs configured. Click 'Add Another LLM' to add one."
            )

        for i, additional_config in enumerate(st.session_state.additional_llm_configs):
            with st.container():
                st.markdown(f"#### Additional LLM #{i+1}")

                # Create columns for provider and model
                col1, col2 = st.columns(2)

                # Provider selection
                def on_additional_provider_change(idx):
                    def _callback():
                        new_provider = st.session_state[f"additional_provider_{idx}"]
                        # Update model list for this provider
                        model_options = get_model_options_for_provider(new_provider)
                        if model_options:
                            st.session_state[f"additional_model_{idx}"] = model_options[
                                0
                            ]
                        # Update in the additional_llm_configs
                        st.session_state.additional_llm_configs[idx][
                            "provider"
                        ] = new_provider
                        if model_options:
                            st.session_state.additional_llm_configs[idx]["model"] = (
                                model_options[0]
                            )

                    return _callback

                with col1:
                    add_provider = st.selectbox(
                        "LLM Provider",
                        options=available_providers,
                        index=(
                            available_providers.index(additional_config["provider"])
                            if additional_config["provider"] in available_providers
                            else 0
                        ),
                        key=f"additional_provider_{i}",
                        on_change=on_additional_provider_change(i),
                    )

                # Get model options for this provider
                add_provider = st.session_state[f"additional_provider_{i}"]
                add_model_options = get_model_options_for_provider(add_provider)

                # Handle model selection state
                if f"additional_model_{i}" not in st.session_state:
                    if additional_config["model"] in add_model_options:
                        st.session_state[f"additional_model_{i}"] = additional_config[
                            "model"
                        ]
                    elif add_model_options:
                        st.session_state[f"additional_model_{i}"] = add_model_options[0]

                # Model selection
                with col2:
                    add_model = st.selectbox(
                        "Model", options=add_model_options, key=f"additional_model_{i}"
                    )

                # Update the config with the current values
                st.session_state.additional_llm_configs[i]["model"] = add_model

                # Temperature and token settings in columns
                col3, col4 = st.columns(2)

                with col3:
                    add_temperature = st.slider(
                        "Temperature",
                        min_value=0.0,
                        max_value=1.0,
                        value=additional_config["temperature"],
                        step=0.1,
                        key=f"additional_temperature_{i}",
                    )
                    # Update temperature
                    st.session_state.additional_llm_configs[i][
                        "temperature"
                    ] = add_temperature

                with col4:
                    add_max_tokens = st.number_input(
                        "Max Tokens",
                        min_value=100,
                        max_value=10000,
                        value=additional_config["max_tokens"],
                        step=100,
                        key=f"additional_max_tokens_{i}",
                    )
                    # Update tokens
                    st.session_state.additional_llm_configs[i][
                        "max_tokens"
                    ] = add_max_tokens

                # Remove button
                st.button(
                    f"Remove LLM #{i+1}",
                    key=f"remove_llm_{i}",
                    on_click=lambda i=i: st.session_state.additional_llm_configs.pop(i)
                    or st.rerun(),
                )

                # Visual separator between configs
                st.markdown("---")

        # Add LLM button at the bottom
        if st.button("Add Another LLM", key="add_llm_button"):
            add_llm_config()
            st.rerun()

    # SECTION 3: COURSE DETAILS FORM
    st.subheader("Course Details")

    # Now create the actual form
    with st.form("course_metadata_form"):
        # Required fields
        title = st.text_input("Course Title *", value=default_title)
        description = st.text_area("Course Description *", value=default_description)
        target_audience = st.text_input("Target Audience *", value=default_audience)
        language = st.text_input("Language", value=default_language)
        version = st.text_input("Version", value=default_version)
        author = st.text_input("Author *", value=default_author)

        # Optional fields (in expander)
        with st.expander("Additional Information (Optional)"):
            skill_level = st.selectbox(
                "Skill Level",
                options=["", "Beginner", "Intermediate", "Advanced"],
                index=(
                    0
                    if not default_skill
                    else ["", "Beginner", "Intermediate", "Advanced"].index(
                        default_skill
                    )
                ),
            )
            prerequisites = st.text_area("Prerequisites", value=default_prereq)
            estimated_duration = st.text_input(
                "Estimated Duration", value=default_duration
            )

        # Display settings for all LLMs (read-only summary)
        st.markdown("### LLM Configuration Summary")

        # Display primary LLM summary
        st.markdown(
            f"**Primary LLM**: {provider} - {model} (Temperature: {temperature}, Max Tokens: {max_tokens})"
        )

        # Display additional LLMs summary
        if st.session_state.additional_llm_configs:
            for i, cfg in enumerate(st.session_state.additional_llm_configs):
                st.markdown(
                    f"**Additional LLM #{i+1}**: {cfg['provider']} - {cfg['model']} (Temperature: {cfg['temperature']}, Max Tokens: {cfg['max_tokens']})"
                )

        # Submit button
        submitted = st.form_submit_button("Save Course")

        if submitted:
            # Validate required fields
            if not title or not description or not target_audience or not author:
                st.error("Please fill in all required fields marked with *")
            else:
                try:
                    # Create LLM config
                    llm_config = LLMConfig(
                        provider=provider,
                        model=model,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )

                    # Store selected provider and model in session state for later use
                    if "app_config" not in st.session_state:
                        st.session_state.app_config = app_config

                    if "selected_llm" not in st.session_state:
                        st.session_state.selected_llm = {
                            "provider": provider,
                            "model": model,
                        }
                    else:
                        st.session_state.selected_llm["provider"] = provider
                        st.session_state.selected_llm["model"] = model

                    # Create additional LLM configs from the session state
                    additional_llm_configs = []
                    for config_data in st.session_state.additional_llm_configs:
                        additional_llm_configs.append(
                            LLMConfig(
                                provider=config_data["provider"],
                                model=config_data["model"],
                                temperature=config_data["temperature"],
                                max_tokens=config_data["max_tokens"],
                            )
                        )

                    # Create course object with primary and additional LLM configs
                    course = Course(
                        title=title,
                        description=description,
                        target_audience=target_audience,
                        language=language,
                        version=version,
                        author=author,
                        skill_level=skill_level if skill_level else None,
                        prerequisites=prerequisites if prerequisites else None,
                        estimated_duration=(
                            estimated_duration if estimated_duration else None
                        ),
                        llm_config=llm_config,
                        additional_llm_configs=additional_llm_configs,
                    )

                    # Save to session state
                    st.session_state.course = course

                    # Create course directory and save config
                    course_dir = file_service.create_course_directory(course.title)
                    st.session_state.course_dir = course_dir
                    file_service.save_course_config(course, course_dir)

                    # Success message
                    logger.info(f"Saved course: {course.title}")
                    st.success(f"Successfully saved course: {course.title}")

                    # Move to next step
                    st.session_state.workflow_step = "Learning Outcomes"

                except Exception as e:
                    logger.error(f"Error saving course: {e}")
                    st.error(f"Error saving course: {e}")
