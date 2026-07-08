from __future__ import annotations

from app.models.brief import DailyBrief


def render_slack_mock(brief: DailyBrief) -> str:
    lines = [f"*Corvus MFG Daily Brief - {brief.production_date}*", brief.headline]
    for finding in brief.findings[:5]:
        lines.append(f"- {finding.severity.value.upper()} Job {finding.job_id}: {finding.summary}")
    return "\n".join(lines)
