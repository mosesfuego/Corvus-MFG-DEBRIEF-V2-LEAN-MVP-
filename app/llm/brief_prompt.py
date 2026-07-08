from __future__ import annotations

import json
from typing import Any

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


def build_mes_context_prompt(mes_context: dict[str, Any]) -> str:
    compact_context = json.dumps(mes_context, indent=2, sort_keys=True)
    return "\n".join(
        [
            "You are helping a manufacturing leader prepare a daily production risk brief.",
            "Use the normalized jobs first. Use raw MES tables only as supporting context.",
            "Do not invent jobs, dates, owners, blockers, or customer commitments.",
            "Return concise operational observations and questions for today's standup.",
            "",
            "MES context:",
            compact_context,
        ]
    )
