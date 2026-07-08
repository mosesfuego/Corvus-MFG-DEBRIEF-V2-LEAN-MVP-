# Contributing

Keep changes aligned to the core workflow:

```text
manufacturing data -> risk detection -> daily brief -> owner questions
```

## Guidelines

- Prefer small pull requests with one clear product outcome.
- Keep deterministic risk logic in `app/analysis/`.
- Keep generated reports out of git; use `outputs/` locally.
- Add or update tests when changing ingestion, risk rules, or brief structure.
- Do not add real external integrations during the lean sprint.

## Local Checks

```bash
ruff check .
pytest
```
