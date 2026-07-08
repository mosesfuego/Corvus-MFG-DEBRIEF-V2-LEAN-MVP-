from __future__ import annotations

from datetime import date

from app.models.production import ProductionJob, Status
from app.models.risk import RiskFinding, RiskType, Severity


def detect_basic_risks(jobs: list[ProductionJob], today: date) -> list[RiskFinding]:
    findings: list[RiskFinding] = []
    for job in jobs:
        if job.is_complete:
            continue

        days_to_due = (job.due_date - today).days

        if days_to_due < 0 or job.status == Status.LATE:
            findings.append(
                RiskFinding(
                    job_id=job.job_id,
                    risk_type=RiskType.LATE,
                    severity=Severity.CRITICAL,
                    owner=job.owner,
                    summary=f"Job {job.job_id} is late.",
                    evidence=(
                        f"Due {job.due_date.isoformat()} with "
                        f"{job.remaining_quantity} units open."
                    ),
                    recommended_action="Confirm recovery date and customer communication plan.",
                    days_to_due=days_to_due,
                    impact="Missed delivery risk is already active.",
                    questions=[f"What recovery commitment can {job.owner} make today?"],
                )
            )

        if job.status == Status.BLOCKED:
            findings.append(
                RiskFinding(
                    job_id=job.job_id,
                    risk_type=RiskType.BLOCKED,
                    severity=Severity.HIGH if days_to_due > 1 else Severity.CRITICAL,
                    owner=job.owner,
                    summary=f"Job {job.job_id} is blocked at {job.current_step}.",
                    evidence=job.blocker_reason or "No blocker reason provided.",
                    recommended_action=(
                        "Assign an owner to remove the blocker before the next standup."
                    ),
                    days_to_due=days_to_due,
                    impact="Blocked work can consume remaining schedule buffer.",
                    questions=[
                        f"What decision or material does {job.owner} need to unblock this job?"
                    ],
                )
            )

        if job.estimated_cycle_time_days > max(days_to_due, 0):
            findings.append(
                RiskFinding(
                    job_id=job.job_id,
                    risk_type=RiskType.SCHEDULE,
                    severity=Severity.HIGH,
                    owner=job.owner,
                    summary=f"Job {job.job_id} has insufficient cycle-time buffer.",
                    evidence=(
                        f"{job.estimated_cycle_time_days} cycle days estimated with "
                        f"{days_to_due} calendar days to due date."
                    ),
                    recommended_action=(
                        "Review expedite options, overtime, or revised ship promise."
                    ),
                    days_to_due=days_to_due,
                    impact="Work may become late without schedule intervention.",
                    questions=[f"Can {job.owner} reduce cycle time or resequence work today?"],
                )
            )

    return findings
