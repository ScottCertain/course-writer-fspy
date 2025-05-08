# Lesson Shell Prompt Template

## API Parameters
- Model: claude-3-7-sonnet-20250219
- Max Tokens: 20000
- Temperature: 0.1

## User Message Template
You are an expert lesson planner for "Generative AI for Software Developers." I'll provide a lesson title and Learning Outcomes (LOs) with subtopics. Generate a structured lesson shell in Markdown-like format, matching this style: concise LO titles (e.g., "Analyzing LLMs in AI"), specific subheadings tied to subtopics (e.g., "Definition and Significance"), and standard placeholders. Use no Thinking mode and a temperature of 0.1 for precision.

Instructions:
1. Start with `# Lesson: [Provided Title]`.
2. Add `## Introduction` with "[Write a 150–200-word introduction...]" placeholder.
3. Add `## Learning Outcomes`, copying LOs and subtopics verbatim.
4. For each LO, create a section (e.g., `## LO1: [Title]`):
   - Title: Use the LO verb + focus (e.g., "Analyze" → "Analyzing [Topic] in AI", "Evaluate" → "Evaluating the [Topic]").
   - Two subheadings: Map "Key Concepts" and "Dev Concepts" to specific names (e.g., "Definition and Purpose," "Prompting as Function Parameters").
   - `### Key Takeaways` with "[Summarize key takeaways tied to LO#.]" and "[Transition to LO#+1 section.]" (except last LO).
5. End with:
   - `## Conclusion`: "[In 150–200 words, summarize...]"
   - `## Glossary`: "- **[Term]** – [Definition]" with placeholder note.
   - `## Learning Enhancements`: Exercise/Discussion placeholders (under 100 words each).
6. Wrap in `<lesson_shell>` tags, noting "[Target total length: ~{1800–2000 for 3 LOs, 2200–2500 for 4 LOs} words when filled by LC1]."

Input:
- **Title**: {{TITLE}}
- **LOs**:
  {{LOs}}

Generate the lesson shell now.
