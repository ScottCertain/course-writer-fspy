# PRD: AI-Powered Course Writing Assistant (Prototype)

## Product Name
**CourseSmith** (Working Title)

## Purpose
This tool assists course developers in generating structured course content using LLMs via API. It automates the process from metadata definition to draft generation and learning asset creation (quizzes, activities, etc.), saving all outputs to local Markdown files.

---

## Target Tech Stack

| Component              | Technology                        |
|------------------------|------------------------------------|
| Language               | Python 3.12                        |
| LLM Framework          | LangChain                          |
| UI Framework           | Streamlit                          |
| Local LLM Interface    | Ollama + LM Studio (local APIs)    |
| Cloud LLM Interface    | Anthropic API (Claude 3.7), OpenAI API |
| File Format            | Markdown (`.md`)                   |
| Config Format          | YAML                               |
| Storage                | Local file system (folder-based)   |

---

## Core Workflow UI

### 1. Course Metadata Input
- Fields: Course title, description, target audience, language, version, author
- Save metadata to: `course_config.yaml`
- Optional tags: skill level, prerequisites, estimated duration

### 2. Lesson Learning Outcomes (LOs)
- Input screen for detailed LOs
- Save LOs to: `lessons/lesson_<number>_LOs.md`

### 3. Generate Lesson Shell
- Use LOs to generate a Lesson Shell (using pre-written prompt)
- Output: `lessons/lesson_<number>_shell.md`

### 4. Generate Rough Draft
- Expand Lesson Shell using a second prompt
- Output: `lessons/lesson_<number>_rough.md`

### 5. Generate Expanded Draft
- Expand Rough Draft using a third prompt
- Output: `lessons/lesson_<number>_expanded.md`

### 6. Generate Quiz Sets
- Input: Expanded Draft
- Generate:
  - Quiz Set 1: Multiple Choice
  - Quiz Set 2: Fill-in-the-Blank
  - Quiz Set 3: True/False
- Output files:
  - `lessons/lesson_<number>_quiz1.md`
  - `lessons/lesson_<number>_quiz2.md`
  - `lessons/lesson_<number>_quiz3.md`

### 7. Generate Student Activities
- Input: Expanded Draft
- Generate:
  - 3 Discussion/Research Activities
  - 1 Code-Along
  - 1 Coding Challenge
  - Solutions for all
- Output files:
  - `lessons/lesson_<number>_activities.md`
  - `lessons/lesson_<number>_solutions.md`

---

## Functional Requirements

- ✅ Support for selecting LLM source (OpenAI, Ollama, LM Studio)
- ✅ Configurable model temperature and token limits
- ✅ Logging of each step's API calls and outputs
- ✅ Markdown preview in UI for outputs
- ✅ YAML/JSON-based project structure for course persistence
- ✅ Lesson navigation and file management

---

## Non-Functional Requirements

- Modular and extendable codebase
- Clean UI suitable for creative writing tasks
- Ability to run entirely offline if using local LLMs
- Support for future plugin/agent-based feature enhancements

---

## Folder Structure Example

```
/courses/
  course_title/
    course_config.yaml
    lessons/
      lesson_01_LOs.md
      lesson_01_shell.md
      lesson_01_rough.md
      lesson_01_expanded.md
      lesson_01_quiz1.md
      lesson_01_quiz2.md
      lesson_01_quiz3.md
      lesson_01_activities.md
      lesson_01_solutions.md
```

---

## Prompts Used (Summary Only)

- **Prompt 01: Lesson Shell**: Converts detailed LOs into a scaffolded lesson outline.
- **Prompt 02: Rough Draft**: Converts the shell into a prose draft with placeholders.
- **Prompt 03: Expanded Draft**: Fills out the prose, adds examples and instructor notes.
- **Prompt 04: Quiz**: Generates quizzes aligned to Bloom's levels.
- **Prompt 05: Activity**: Crafts activities and coding tasks with guided answers.

> Full prompt texts are stored in `prompts/` folder and referenced by name in code.

---

## MVP Goals

- Input course config
- Enter LOs
- Generate shell → rough → expanded
- Generate quizzes and activities
- Save all content as markdown
- Support OpenAI + Ollama as backends

---

## Future Enhancements (Post-MVP)

- Support for multi-lesson navigation and editing
- Auto-versioning and backup of lesson drafts
- Vector search over lesson drafts
- Embedding in VS Code as a sidebar plugin
- RAG-based prompt refinement using previous lessons

---

## Notes for Developers

- Use LangChain for model abstraction and chaining steps
- Use Streamlit `st.session_state` for stateful workflows
- Use Pydantic for schema validation of YAML configurations
- Implement retry logic and error logging for API calls
- Store API keys in environment variables
- Use pytest for testing (unit, integration, and functional tests)
