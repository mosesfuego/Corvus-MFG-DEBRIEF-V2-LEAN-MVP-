from __future__ import annotations

from app.models.brief import DailyBrief


def render_markdown(brief: DailyBrief) -> str:
    lines = [
        f"# Corvus MFG Daily Brief - {brief.production_date}",
        "",
        f"## Headline",
        "",
        brief.headline,
        "",
        "## Risks",
        "",
    ]

    if not brief.findings:
        lines.append("- No risks detected.")
    else:
        for finding in brief.findings:
            lines.append(
                f"- **{finding.severity.value.upper()}** Job {finding.job_id}: "
                f"{finding.summary} Owner: {finding.owner}."
            )

    lines.extend(["", "## Owner Questions", ""])
    if not brief.owner_questions:
        lines.append("- No owner questions.")
    else:
        for owner, questions in brief.owner_questions.items():
            lines.append(f"### {owner}")
            for question in questions:
                lines.append(f"- {question}")

    return "\n".join(lines).strip() + "\n"
