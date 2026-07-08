# Lena - Integrations / Output Engineer

## Owns

- Markdown report export
- JSON output shape
- Mock Slack-style output
- Future integration boundaries
- Output consistency across channels

## Tasks

- Maintain output formatters in `app/output/`.
- Keep generated report files in `outputs/`.
- Create markdown output suitable for email or docs.
- Create mock Slack output without building a real Slack bot.
- Define simple adapter boundaries for future integrations.
- Make sure output formats reuse the same `DailyBrief` data.

## Done When

- The same brief can render as markdown, JSON, and mock Slack text.
- Demo outputs are easy to inspect and share.
- No real external integration is required for the MVP.
