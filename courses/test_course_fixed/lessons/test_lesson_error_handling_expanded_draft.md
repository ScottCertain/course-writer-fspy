Learning Outcomes (LOs)
- Understand the role of error handling for LLMs
- Learn techniques for testing LLM outputs for errors
- Appreciate limitations and failure modes of LLMs

Errors happen, especially with the current generation of language models that can hallucinate wildly inaccurate information. Testing outputs from LLMs is crucial before shipping to production. Naive acceptance of their responses could mean spreading misinformation or breaking software.

## Why care about errors?

LLMs lack robust internal consistency checks. They are great at producing fluent text adhering to language patterns but don't truly understand the subject matter. Nonsensical outputs are common.

## Detecting errors

Look for factual inaccuracies, logical contradictions, coded biases, and departures from prompts. Use techniques like:

- Prompt filtering: Ask LLM to identify its own potential errors
- External validation: Cross-reference outputs against trusted sources
- Human review: Manual inspection by subject matter experts
- Unit tests: Write deterministic test cases for the LLM

## Error failure modes

LLMs can fail by omitting critical information or going off on irrelevant tangents. Their outputs may contradict themselves or show social biases. LLMs have no common sense for grounding.

</lesson_passage>

Glossary:
- LLM: Large Language Model