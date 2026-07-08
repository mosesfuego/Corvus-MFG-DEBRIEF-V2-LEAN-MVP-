from __future__ import annotations

from app.models.risk import RiskFinding


def build_brief_prompt(findings: list[RiskFinding]) -> str:
    lines = [
        "Write a concise daily manufacturing risk brief.",
        "Audience: production manager, operations lead, or shop owner.",
        "Focus on what needs attention today.",
        "",
        "Findings:",
    ]
    for finding in findings:
        lines.append(f"- {finding.severity.value.upper()} {finding.job_id}: {finding.summary}")
    return "\n".join(lines)
