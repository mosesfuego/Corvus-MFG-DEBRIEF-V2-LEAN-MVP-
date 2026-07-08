# Architecture

The demo is organized around a single workflow:

```text
CSV/sample data -> typed jobs -> risk findings -> daily brief -> exports/UI
```

## Boundaries

- `app/ingest/` owns file loading and validation.
- `app/ingest/mock_mes_socket.py` owns mock MES CSV classification and normalization.
- `app/models/` owns shared domain types.
- `app/analysis/` owns deterministic risk rules and schedule reasoning.
- `app/llm/` owns prompt construction and brief-writing adapters.
- `app/output/` owns markdown, JSON, and mock Slack formatting.
- `app/api/` owns FastAPI route wiring.

## Design Notes

Risk detection should stay deterministic and testable. LLM output can improve tone and summarization, but it should not be the only place where operational risk is identified.

## Mock MES Socket

The mock MES socket is deliberately simple for the MVP:

1. Read one CSV or a folder of CSV exports.
2. Normalize headers to snake case.
3. Classify each table using hard-coded filename/header hints.
4. Normalize work-order-like rows into `ProductionJob` records.
5. Normalize manufacturing-log rows into timestamped events.
6. Compile event summaries by job and production line.
7. Preserve every raw table as compact context for the LLM.

This keeps the future live-agent path open without building real MES integration infrastructure too early.
