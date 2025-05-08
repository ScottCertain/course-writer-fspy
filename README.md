# CourseSmith: AI-Powered Course Writing Assistant

CourseSmith is a Streamlit-based application that helps course creators generate structured educational content using Large Language Models. It automates the process from course metadata definition to content generation, producing well-structured lessons, quizzes, and learning activities.

## Features

- Course metadata management with YAML-based configuration
- Step-by-step lesson creation workflow
- Multiple LLM provider support (Anthropic Claude, OpenAI, Ollama, LM Studio)
- Generation of lesson outlines, drafts, quizzes, and activities
- Markdown-based output for easy integration with various platforms

## Installation

### Prerequisites

- Python 3.12+
- Pip package manager
- Optional: API keys for Anthropic or OpenAI
- Optional: Ollama or LM Studio for local LLM support

### Setup

1. Clone the repository:
```bash
git clone <repository_url>
cd course-writer-fspy
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
# Create .env file from template
cp .env.template .env

# Edit .env file with your API keys
# ANTHROPIC_API_KEY=your_key_here
# OPENAI_API_KEY=your_key_here
```

## Usage

1. Start the application:
```bash
# For best compatibility, use the python -m prefix
python -m streamlit run app.py
```

2. Open your browser and navigate to http://localhost:8501

3. Follow the workflow:
   - Enter course metadata
   - Define learning outcomes for each lesson
   - Generate lesson shells, drafts, and expanded versions
   - Create quizzes and activities
   - Export the content as Markdown files

## Project Status Tracking

The project includes a `knowledge_transfer.md` file that tracks the current status of the application, implementation progress, known issues and their resolutions, and planned next steps. This file is continually updated throughout development.

## Project Structure

```
course-writer/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Dependencies
├── .env.template          # Environment variables template
├── config/                # Configuration files
│   └── app_config.yaml    # App configuration
├── models/                # Data models
│   ├── course.py          # Course data models
│   └── lesson.py          # Lesson data models
├── services/              # Service layer
│   ├── file_service.py    # File operations
│   ├── llm_service.py     # LLM provider abstraction
│   └── prompt_service.py  # Prompt management
├── ui/                    # UI components
│   └── course_ui.py       # Course metadata UI
├── prompts/               # Prompt templates
│   ├── lesson_shell.md
│   ├── rough_draft.md
│   ├── expanded_draft.md
│   ├── quiz_generator.md
│   └── activity_generator.md
└── courses/               # Generated course content
```

## Configuration

Edit `config/app_config.yaml` to customize application settings:

- Default LLM provider and models
- Temperature and token settings
- UI preferences
- Log levels

### LLM Configuration

CourseSmith supports multiple LLM providers with specific model options:

1. **Anthropic Claude**
   - Default model: `claude-3-7-sonnet`
   - Available models: `claude-3-7-sonnet`, `claude-3-opus`, `claude-3-haiku`
   - Requires `ANTHROPIC_API_KEY` in your `.env` file

2. **OpenAI**
   - Default model: `gpt-4o`
   - Available models: `gpt-4o`, `gpt-4-turbo`, `gpt-3.5-turbo`
   - Requires `OPENAI_API_KEY` in your `.env` file

3. **Ollama (Local)**
   - Default models: `codegemma:7b`, `phi4:latest`
   - Additional options: `llama3`, `mistral`, `llama2`
   - Connects to local Ollama instance at `http://localhost:11434` by default
   - Set custom URL with `OLLAMA_BASE_URL` in your `.env` file

4. **LM Studio (Local)**
   - Default model: `gemma-3-12b-it-qat`
   - Also supports generic `custom` model
   - Connects to LM Studio at `http://127.0.0.1:1234` by default
   - Set custom URL with `LMSTUDIO_BASE_URL` in your `.env` file

To add additional models, update the `config/app_config.yaml` file with your desired configuration.

## Development

### Known Issues and Fixes

- **Streamlit API Change**: The project originally used `st.experimental_rerun()` which has been deprecated in newer Streamlit versions. This has been updated to use `st.rerun()` instead.

### Contributing

To enhance CourseSmith or fix issues:

1. Create an issue describing the enhancement or bug
2. Fork the repository
3. Create a new branch for your feature
4. Submit a PR with your changes

## License

This project is licensed under the MIT License - see the LICENSE file for details.
