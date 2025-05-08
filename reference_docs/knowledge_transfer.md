# CourseSmith: Knowledge Transfer Document

This document tracks the status of the CourseSmith application over time, including development progress, known issues, and planned next steps. It serves as a continuous knowledge transfer resource for the project.

## Current Status (2025-05-08)

### Implementation Progress

The current implementation is based on the phases outlined in the implementation plan:

#### Phase 1: Project Foundations ✅
- Project structure created
- Virtual environment set up with dependencies
- Configuration files implemented
- Data models (Course and Lesson) implemented with Pydantic
- File service for YAML configuration and file management implemented

#### Phase 2: LLM Integration ✅
- LLM service layer implemented with provider abstraction
- Support for multiple providers (Anthropic, OpenAI, Ollama, LM Studio)
- Prompt service implemented with template rendering

#### Phase 3: UI Implementation 🟡
- Main application structure with Streamlit created
- Navigation and session state management implemented
- Course metadata UI fully implemented
- Lesson UI and content generation UI placeholders added

#### Phase 4: Generation Pipeline 🟡
- Prompt templates for generation pipeline completed
- Pipeline architecture designed
- Implementation in progress
- Full integration with UI pending

#### Phase 5: Testing Framework ✅
- Comprehensive unit testing framework implemented
- Integration tests for key components added
- Centralized test logging system configured
- Code coverage reporting implemented

### Prompt Templates Progress

We have successfully implemented all core prompt templates needed for the lesson generation pipeline:

- **LO Generator (Step 1)**: Creates detailed learning outcomes with key concepts and relevant software development parallels
- **Lesson Shell (Step 2)**: Generates structured lesson outlines from learning outcomes
- **Rough Draft (Step 3)**: Transforms lesson shells into initial content with developer-friendly tone
- **Expanded Draft (Step 4)**: Enhances rough drafts with deeper explanations while preserving structure
- **Intro & Conclusion (Step 5)**: Creates engaging bookend sections for the expanded content

Each template uses the Anthropic Claude model with carefully tuned parameters for optimal results. The templates follow a consistent progression, with each step's output becoming the input for the next step.

### Working Features

- **Course Management**
  - Create new courses with complete metadata
  - Save course configurations to YAML files
  - Load existing courses from disk
  - Configure LLM settings (provider, model, temperature, tokens)

- **Infrastructure**
  - File system operations for course storage
  - Prompt template system with variable substitution
  - LLM service abstraction layer
  - Multi-provider support for LLM integration

- **Prompt Templates**
  - Standardized prompt formats for consistent results
  - Model-specific parameter tuning
  - Template variable system for dynamic content

- **Testing Framework**
  - Unit tests for models and services
  - Integration tests for pipeline components
  - Centralized test logs in `test_logs/` directory
  - Coverage reporting for code quality metrics

### Known Issues and Resolutions

| Issue | Status | Resolution |
|-------|--------|------------|
| Streamlit API Change | Resolved | The project originally used `st.experimental_rerun()` which has been deprecated in newer Streamlit versions. Updated to use `st.rerun()` instead. |
| Variable Format Differences | Pending | The prompt templates use `{{VARIABLE}}` format but the PromptService uses `$variable` format. Need to implement conversion or update one approach for consistency. |
| Pipeline Integration Tests | Resolved | Fixed file path and naming convention issues in pipeline integration tests, ensuring proper test execution. |

## Next Steps

### Immediate Priorities

1. **Implement Lesson Pipeline**
   - Create `LessonPipeline` class to orchestrate the generation process
   - Implement step-by-step execution with proper error handling
   - Add file-based persistence between steps
   - Integrate with Streamlit UI

2. **Implement Learning Outcomes UI**
   - Create UI for entering module name, lesson objective, and topics
   - Implement form for submitting learning outcomes
   - Add validation and preview capabilities

3. **Implement Content Generation Workflow**
   - Connect the pipeline to the UI
   - Implement progress tracking and visualization
   - Add file preview and editing capabilities
   - Create error recovery mechanisms

4. **Enhance Test Coverage**
   - Add unit tests for remaining services
   - Create end-to-end tests for the entire generation pipeline
   - Develop UI testing strategy

### Future Enhancements (Post-MVP)

As outlined in the PRD:
- Multi-lesson navigation and editing
- Auto-versioning and backup of lesson drafts
- Vector search over lesson drafts
- VS Code sidebar plugin integration
- RAG-based prompt refinement

## Development Notes

### LLM Error Handling Best Practices

When communicating with LLM APIs, implement these error handling strategies:

1. **Retry Logic with Exponential Backoff**: For transient errors like rate limits or network issues
2. **Output Validation**: Verify that LLM outputs match expected formats and structure
3. **Fallback Mechanisms**: Have backup models or providers if the primary one fails
4. **Timeout Handling**: Set appropriate timeouts to prevent hanging requests
5. **Comprehensive Logging**: Track all LLM interactions for debugging and improvement

### File-Based Pipeline Architecture

The lesson generation pipeline will use a file-based approach:
- Each step writes its output to a markdown file in the lesson directory
- Each subsequent step reads from the previous step's output file
- This provides persistence, inspection capabilities, and restart options

### Streamlit Tips

- Always use `python -m streamlit run app.py` instead of just `streamlit run app.py` for best compatibility
- Streamlit session state is essential for preserving data between reruns
- Avoid using deprecated experimental features (they may be removed in future versions)

### LLM Integration

- Anthropic Claude 3.7 is the default LLM but the application supports multiple providers
- Local LLMs through Ollama or LM Studio can be used without API keys
- Environment variables are used for API key management

### Testing Best Practices

- Always use the pytest fixture system for test setup and teardown
- Mock external services (especially LLM APIs) for reliable testing
- Store all test logs in the centralized `test_logs/` directory
- Run tests with coverage reporting to identify untested code paths
- Use integration tests to verify component interactions

## Update History

### 2025-05-08: Comprehensive Testing Framework Implementation
- Implemented organized testing directory structure:
  - Unit tests for models and services
  - Integration tests for pipeline components
  - Shared fixtures in conftest.py
- Set up centralized test logging in `test_logs/` directory
- Configured code coverage reporting with `.coveragerc`
- Migrated standalone test scripts into organized framework:
  - Pipeline integration tests
  - Draft pipeline tests
  - Lesson pipeline tests
  - LLM configuration tests
- Added detailed test documentation:
  - Step-by-step guide for running tests
  - Coverage reporting instructions
  - Best practices for writing new tests

### 2025-05-08: Prompt Templates and Pipeline Architecture
- Completed all core prompt templates for lesson generation:
  - LO Generator (Step 1)
  - Lesson Shell (Step 2)
  - Rough Draft (Step 3)
  - Expanded Draft (Step 4)
  - Intro & Conclusion (Step 5)
- Designed pipeline architecture for automated lesson generation
- Updated API parameters for optimal results with Claude 3.7
- Standardized template formats for consistency

### 2025-05-07: UI Enhancement with Tabs and Columns (Completed)
- Completely redesigned the LLM configuration UI for a more intuitive experience:
  - Added tabs to separate primary and additional LLM configurations
  - Used columns to place related fields next to each other (Provider + Model, Temperature + Tokens)
  - Moved the model selection directly next to provider selection for clearer relationship
  - Added visual separators between different LLM configurations
  - Implemented a more intuitive flow from top to bottom
- Added new UX improvements:
  - Information message when no additional LLMs are configured
  - Visual indicators for relationships between fields
  - More compact layout that reduces scrolling
  - More logical organization of form elements

### 2025-05-07: UI Fixes for LLM Configuration (Completed)
- Fixed critical Streamlit form errors:
  - Completely restructured UI to avoid the "Missing Submit Button" error 
  - Removed duplicated form elements that were causing conflicts
  - Fixed the model dropdown not updating correctly when changing providers
  - Moved all provider selection outside the form to avoid callback errors
  - Ensured all non-form UI elements are properly placed outside the form context
- Improved UX with additional features:
  - Read-only summary of additional LLMs inside the form
  - Better organization of UI components with clearer section headers
  - Dynamic model selection with proper state management
  - Added proper temperature and token tracking for additional LLMs

### 2025-05-07: Multiple LLM Support (Completed)
- Added support for configuring multiple LLMs for each course:
  - Updated Course model to include a list of additional LLM configurations
  - Added "Add Another LLM" button to the course metadata UI
  - Implemented UI for adding, configuring, and removing additional LLMs
  - Updated course saving logic to store all LLM configurations
- Each additional LLM has its own provider, model, temperature, and token settings

### 2025-05-07: LLM Configuration UI Enhancement (Completed)
- Improved the course creation UX:
  - Added form field clearing when selecting "Create New Course"
  - Implemented session state tracking to reset fields to default values
- Updated the LLM model options for each provider:
  - Anthropic: Claude 3.7 Sonnet, Claude 3.5 Sonnet 2024-10-22, Claude 3.5 Haiku
  - LMStudio: Gemma 3 12B QAT (gemma-3-12b-it-qat)
  - Ollama: Gemma 3 12B (gemma3:12b), CodeGemma (codegemma:7b), Phi 4 (phi4:latest)
- Enhanced provider switching in the UI with proper model selection updates
- Removed unnecessary models and streamlined the configuration

### 2025-05-07: LLM Configuration Enhancement
- Updated LLM configuration to support specific model selection:
  - Claude 3.7 Sonnet
  - Ollama with CodeGemma (codegemma:7b) and Phi 4 (phi4:latest)
  - LM Studio with Gemma 3 12B QAT (gemma-3-12b-it-qat)
- Created a new LLMServiceProvider for simplified LLM service management
- Implemented dynamic loading of LLM models from configuration
- Added test script to verify LLM configuration options
- Updated documentation with detailed LLM configuration instructions

### 2025-05-07: Initial Setup
- Created project structure and implemented core components
- Set up virtual environment and dependencies
- Implemented Course and Lesson models
- Created basic UI with course metadata management
- Fixed issue with deprecated Streamlit API (experimental_rerun)
