# CourseSmith Implementation Plan

## Overview

This document outlines the technical approach for implementing the CourseSmith application, an AI-powered course writing assistant that helps course developers generate structured content using Large Language Models (LLMs).

## Project Setup

### 1. Virtual Environment Setup

```bash
# Create a virtual environment using Python 3.12
python3.12 -m venv venv

# Activate the virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Dependencies (requirements.txt)

```
# Core dependencies
langchain>=0.1.0
streamlit>=1.31.0
pydantic>=2.5.0
pyyaml>=6.0.1
python-dotenv>=1.0.0

# LLM providers
anthropic>=0.8.0
openai>=1.10.0
requests>=2.31.0

# Testing
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-mock>=3.11.1

# Utilities
streamlit-markdown-editor>=0.2.0
rich>=13.5.0
loguru>=0.7.0
```

### 3. Environment Configuration (.env.template)

```
# Anthropic API Key
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# OpenAI API Key (optional)
OPENAI_API_KEY=your_openai_api_key_here

# Local LLM Settings (if using Ollama)
OLLAMA_BASE_URL=http://localhost:11434

# LM Studio Settings (if using LM Studio)
LMSTUDIO_BASE_URL=http://localhost:1234/v1

# Log Level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO
```

## Project Structure

```
course-writer/
├── app.py                 # Main Streamlit application entry point
├── requirements.txt       # Project dependencies
├── .env.template          # Template for environment variables
├── README.md              # Project documentation
├── config/                # Configuration files
│   └── app_config.yaml    # App configuration
├── models/                # Data models
│   ├── __init__.py
│   ├── course.py          # Course data models
│   └── lesson.py          # Lesson data models
├── services/              # Service layer
│   ├── __init__.py
│   ├── llm_service.py     # LLM provider abstraction
│   ├── file_service.py    # File operations
│   └── prompt_service.py  # Prompt management
├── ui/                    # UI components
│   ├── __init__.py
│   ├── course_ui.py       # Course metadata UI
│   ├── lesson_ui.py       # Lesson creation UI
│   └── preview_ui.py      # Markdown preview UI
├── utils/                 # Utility functions
│   ├── __init__.py
│   ├── logger.py          # Logging utilities
│   └── markdown_utils.py  # Markdown processing
├── prompts/               # Prompt templates
│   ├── lesson_shell.md
│   ├── rough_draft.md
│   ├── expanded_draft.md
│   ├── quiz_generator.md
│   └── activity_generator.md
└── tests/                 # Test suite
    ├── __init__.py
    ├── conftest.py        # Test fixtures
    ├── test_models/       # Model tests
    ├── test_services/     # Service tests
    └── test_ui/           # UI tests
```

## Implementation Phases

### Phase 1: Project Foundations (Week 1)

#### Core Setup
- Initialize project structure
- Create virtual environment
- Set up configuration files
- Implement logging

#### Data Models
- Implement Course model (Pydantic)
- Implement Lesson model (Pydantic)
- Create YAML serialization/deserialization

#### Basic File Service
- Implement file system operations
- Create course directory structure
- Add YAML file management

### Phase 2: LLM Integration (Week 2)

#### LLM Service Layer
- Implement LLM provider factory
- Add Anthropic Claude 3.7 integration
- Implement Ollama support
- Add LM Studio integration
- Create token tracking and management

#### Prompt Service
- Create prompt template system
- Implement prompt formatting
- Add variable substitution
- Create prompt chaining mechanism

#### Testing Framework
- Set up pytest configuration
- Implement mock LLM responses
- Create test fixtures

### Phase 3: UI Implementation (Week 3)

#### Streamlit App Structure
- Create main application flow
- Implement navigation
- Add session state management

#### Core UI Components
- Implement course metadata form
- Create lesson input screens
- Add markdown preview component
- Implement generation controls

#### Workflow States
- Create workflow state management
- Implement progress tracking
- Add error handling and recovery

### Phase 4: Generation Pipeline (Week 4)

#### Generation Workflows
- Implement lesson shell generation
- Add rough draft generation
- Create expanded draft generation
- Implement quiz generation
- Add activity generation

#### Output Management
- Create file naming conventions
- Implement output saving
- Add export capabilities

#### Testing & Refinement
- Conduct integration testing
- Optimize performance
- Refine error handling

## Component Specifications

### 1. Data Models

#### Course Model
```python
class Course(BaseModel):
    title: str
    description: str
    target_audience: str
    language: str = "English"
    version: str = "1.0"
    author: str
    
    # Optional fields
    skill_level: Optional[str] = None
    prerequisites: Optional[str] = None
    estimated_duration: Optional[str] = None
    
    # LLM Configuration
    llm_config: LLMConfig
    
    # Methods for YAML serialization/deserialization
```

#### Lesson Model
```python
class Lesson(BaseModel):
    number: int
    title: str
    learning_outcomes: List[str]
    
    # Track generation status
    has_shell: bool = False
    has_rough_draft: bool = False
    has_expanded_draft: bool = False
    has_quizzes: bool = False
    has_activities: bool = False
    
    # Methods for file path construction
```

### 2. LLM Service

The LLM service will provide a unified interface to different LLM providers:

```python
class LLMService:
    def __init__(self, provider: str, config: dict):
        """Initialize the appropriate LLM client based on provider"""
        
    async def generate_text(self, 
                    prompt: str, 
                    temperature: float = 0.7, 
                    max_tokens: int = 2000) -> str:
        """Generate text from the LLM with standard parameters"""
        
    async def generate_with_context(self, 
                            prompt: str, 
                            context: str,
                            temperature: float = 0.7, 
                            max_tokens: int = 2000) -> str:
        """Generate text with additional context"""
```

Provider-specific implementations:
- `AnthropicLLMService`: Uses Claude 3.7 models
- `OllamaLLMService`: Connects to local Ollama instance
- `LMStudioService`: Connects to LM Studio local API

### 3. File Service

The file service will handle all file operations:

```python
class FileService:
    def create_course_directory(self, course_title: str) -> str:
        """Create the course directory structure and return the path"""
        
    def save_course_config(self, course: Course, path: str) -> None:
        """Save course configuration to YAML"""
        
    def save_markdown(self, content: str, path: str) -> None:
        """Save markdown content to a file"""
        
    def load_course_config(self, path: str) -> Course:
        """Load course configuration from YAML"""
        
    def load_markdown(self, path: str) -> str:
        """Load markdown content from a file"""
```

### 4. Prompt Service

The prompt service will manage prompt templates and their rendering:

```python
class PromptService:
    def __init__(self, prompts_dir: str):
        """Load prompt templates from directory"""
        
    def get_prompt(self, prompt_name: str) -> str:
        """Get a prompt template by name"""
        
    def render_prompt(self, prompt_name: str, variables: dict) -> str:
        """Render a prompt template with variables"""
        
    def chain_prompts(self, 
                     prompt_names: List[str], 
                     variables: dict) -> str:
        """Chain multiple prompts together"""
```

### 5. Main Application (app.py)

The Streamlit application structure:

```python
import streamlit as st
from ui.course_ui import render_course_metadata
from ui.lesson_ui import render_lesson_ui
from ui.preview_ui import render_preview

# Initialize session state
if 'course' not in st.session_state:
    st.session_state.course = None
if 'current_lesson' not in st.session_state:
    st.session_state.current_lesson = None
if 'workflow_step' not in st.session_state:
    st.session_state.workflow_step = 'course_metadata'

# Main application flow
def main():
    st.title("CourseSmith")
    st.sidebar.title("Navigation")
    
    # Navigation
    workflow_step = st.sidebar.radio(
        "Workflow",
        ["Course Metadata", "Learning Outcomes", "Generate Content"]
    )
    
    # Render appropriate UI based on workflow step
    if workflow_step == "Course Metadata":
        render_course_metadata()
    elif workflow_step == "Learning Outcomes":
        render_lesson_ui()
    else:
        render_preview()

if __name__ == "__main__":
    main()
```

## Testing Strategy

We'll use pytest for testing with the following approach:

### 1. Unit Tests

- Test each component in isolation
- Mock external dependencies
- Verify core logic functions correctly

Example unit test for the LLM service:

```python
def test_anthropic_llm_service(mocker):
    # Mock Anthropic API response
    mock_completion = mocker.patch('anthropic.Anthropic.completions.create')
    mock_completion.return_value.completion = "Generated text"
    
    # Initialize service
    service = AnthropicLLMService(api_key="test_key")
    
    # Call the service
    result = service.generate_text("Test prompt")
    
    # Assert the result
    assert result == "Generated text"
    mock_completion.assert_called_once()
```

### 2. Integration Tests

- Test interactions between components
- Verify data flows correctly through the system
- Test error handling and recovery

### 3. Functional Tests

- Test complete workflows
- Verify UI interactions
- Test end-to-end generation pipelines

## Deployment Considerations

### Environment Variables

API keys and configuration will be managed through environment variables for security. The `.env.template` file will provide documentation, but actual keys should never be committed to version control.

### Local LLM Support

For local LLM support (Ollama and LM Studio), the application will:
1. Check if the local service is running
2. Provide clear error messages if not available
3. Fall back to cloud providers if configured

### Error Handling

The application will implement robust error handling:
1. Graceful degradation for API failures
2. Automatic retries with exponential backoff
3. Clear error messages for users
4. Comprehensive logging for debugging

## Conclusion

This implementation plan outlines the technical approach for building the CourseSmith application according to the PRD requirements. The modular architecture and phased approach will enable incremental development and testing, with a focus on creating a robust, user-friendly tool for course developers.
