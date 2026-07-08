from __future__ import annotations

from datetime import date

from app.models.production import ProductionJob


def days_to_due(job: ProductionJob, today: date) -> int:
    return (job.due_date - today).days


def has_cycle_time_buffer(job: ProductionJob, today: date) -> bool:
    return job.estimated_cycle_time_days <= max(days_to_due(job, today), 0)
