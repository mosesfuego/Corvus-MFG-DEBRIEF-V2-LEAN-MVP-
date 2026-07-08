# Marcus - Risk Logic Engineer

## Owns

- Deterministic risk rules
- Late job detection
- Blocker detection
- Stale update detection
- Schedule pressure logic
- Recovery pressure framing

## Tasks

- Build and maintain rules in `app/analysis/`.
- Detect jobs that are late, blocked, stale, understaffed, or out of cycle-time buffer.
- Keep risk findings structured and explainable.
- Add evidence and recommended action text for each finding.
- Write tests for every risk rule that affects the daily brief.
- Avoid hiding risk detection inside LLM prompts.

## Done When

- Each risk finding explains what happened, why it matters, and who owns it.
- The same input data produces the same risk findings every time.
- Tests cover the demo scenario and important edge cases.
