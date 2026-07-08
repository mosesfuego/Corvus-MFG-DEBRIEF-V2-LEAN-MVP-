from __future__ import annotations

from datetime import date

from app.analysis.owner_questions import group_questions_by_owner
from app.analysis.risk_rules import detect_basic_risks
from app.models.brief import DailyBrief
from app.models.production import ProductionJob


def write_mock_brief(jobs: list[ProductionJob], today: date) -> DailyBrief:
    findings = detect_basic_risks(jobs, today)
    headline = (
        f"{len(findings)} production risks need review today."
        if findings
        else "No immediate production risks detected today."
    )
    changed_jobs = [
        job for job in jobs if job.previous_status and job.previous_status != job.status.value
    ]
    return DailyBrief(
        production_date=today.isoformat(),
        headline=headline,
        jobs=jobs,
        findings=findings,
        changed_jobs=changed_jobs,
        owner_questions=group_questions_by_owner(findings),
    )
