# Priya - LLM / Prompt Engineer

## Owns

- Brief-generation prompts
- LLM output structure
- Tone and readability of the daily debrief
- Structured summary formats
- Mock writer fallback behavior

## Tasks

- Maintain prompt templates in `app/llm/`.
- Keep the brief concise, direct, and useful for a production leader.
- Make the LLM summarize findings, not invent them.
- Preserve deterministic findings from `app/analysis/`.
- Define a mock writer so the demo works without an API key.
- Ensure the brief answers what is late, blocked, at risk, changed, and who needs to act.

## Done When

- The daily brief sounds like an operations meeting artifact, not a generic AI summary.
- The app can generate a usable brief with or without live LLM access.
- Prompt output is structured enough for markdown, JSON, and UI rendering.
