# Architecture

The demo is organized around a single workflow:

```text
CSV/sample data -> typed jobs -> risk findings -> daily brief -> exports/UI
```

## Boundaries

- `app/ingest/` owns file loading and validation.
- `app/models/` owns shared domain types.
- `app/analysis/` owns deterministic risk rules and schedule reasoning.
- `app/llm/` owns prompt construction and brief-writing adapters.
- `app/output/` owns markdown, JSON, and mock Slack formatting.
- `app/api/` owns FastAPI route wiring.

## Design Notes

Risk detection should stay deterministic and testable. LLM output can improve tone and summarization, but it should not be the only place where operational risk is identified.
