from __future__ import annotations

from collections import defaultdict

from app.models.risk import RiskFinding


def group_questions_by_owner(findings: list[RiskFinding]) -> dict[str, list[str]]:
    questions: dict[str, list[str]] = defaultdict(list)
    for finding in findings:
        for question in finding.questions:
            if question not in questions[finding.owner]:
                questions[finding.owner].append(question)
    return dict(questions)
