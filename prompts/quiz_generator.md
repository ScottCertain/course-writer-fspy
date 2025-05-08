# Quiz Generator Prompt Template

## Task
Create a set of quiz questions based on the expanded lesson content. The questions should assess understanding of key concepts and align with the learning outcomes.

## Expanded Lesson
$expanded_draft

## Learning Outcomes
$learning_outcomes

## Quiz Type
$quiz_type  # This will be "multiple_choice", "fill_in_blank", or "true_false"

## Instructions
1. Generate 5-10 quiz questions of the specified type that assess understanding of the most important concepts from the lesson
2. Ensure questions are aligned with the learning outcomes
3. Cover a range of difficulty levels (use Bloom's taxonomy as a guide)
4. Distribute questions evenly across the entire lesson content
5. Include detailed answer explanations for each question
6. Avoid overly complex or ambiguous wording

## Format Guidelines

### For Multiple Choice
- Include a clear question stem
- Provide 4 options (A, B, C, D)
- Ensure only one option is correct
- Make distractors plausible
- Indicate the correct answer
- Include explanation of why the answer is correct and why others are incorrect

### For Fill in the Blank
- Create sentences with key terms removed
- Put blank lines where words are missing
- Include the correct answer in (parentheses) after each blank
- Provide an explanation for why this is the correct answer

### For True/False
- Create clear, unambiguous statements
- Include a mix of true and false statements
- Indicate whether each statement is TRUE or FALSE
- Provide an explanation for the correct determination

## Output
A well-formatted set of quiz questions with answers and explanations, ready for student assessment.
