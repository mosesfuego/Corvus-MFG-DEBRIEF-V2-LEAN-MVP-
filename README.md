# Corvus MFG Daily Risk Brief

Corvus MFG is a lean demo that turns manufacturing status data into a daily production risk brief.

The sprint scope is intentionally narrow:

1. Load sample or uploaded CSV production data.
2. Detect late, blocked, stale, changed, and schedule-risk jobs.
3. Generate a daily brief for production leaders.
4. Export markdown, JSON, and mock Slack-style output.

## Repository Layout

```text
.
├── app/                  # Python backend, ingestion, analysis, brief generation, API
│   ├── analysis/         # Deterministic production-risk rules
│   ├── api/              # FastAPI routes and request/response wiring
│   ├── ingest/           # CSV loading and validation
│   ├── llm/              # Prompt templates and brief writer abstraction
│   ├── models/           # Typed domain models
│   └── output/           # Markdown, JSON, and mock Slack exporters
├── docs/                 # Product, architecture, and sprint notes
├── frontend/             # Optional React/Next UI if the demo needs it
├── outputs/              # Local generated reports, ignored except .gitkeep
├── responsibilties/      # Sprint ownership and team task breakdowns
├── samples/              # Demo manufacturing CSV fixtures
├── scripts/              # Developer/demo helper commands
├── tests/                # Unit tests for ingestion and risk logic
└── .github/              # CI, PR template, and issue templates
```

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## Mock MES Ingestion

Place raw mock MES CSV exports in `samples/mock_mes/`, then compile them into an LLM-ready context bundle:

```bash
python scripts/ingest_mock_mes.py samples/mock_mes \
  --output outputs/mock_mes_context.json \
  --prompt-output outputs/mock_mes_prompt.txt
```

The socket currently uses hard-coded filename and header heuristics to classify CSVs as manufacturing logs, work orders, operations, quality, receiving, inventory, or unknown. Work-order-like rows are normalized into Corvus production jobs. Event-log rows are summarized by job and line. Every raw table is still included as supporting context for the LLM.

## Demo Principle

Every feature should help answer: **What needs my attention today?**

Out of scope for this sprint: real ERP/MES/QMS integrations, real Slack bots, auth, multi-tenant data, complex dashboards, and autonomous task assignment.
