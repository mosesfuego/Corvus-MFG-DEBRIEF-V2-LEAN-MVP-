from __future__ import annotations

REQUIRED_COLUMNS = {
    "job_id",
    "part_number",
    "customer",
    "build_goal",
    "due_date",
    "quantity_required",
    "quantity_completed",
    "current_step",
    "status",
    "owner",
    "blocker_reason",
    "last_updated",
    "estimated_cycle_time_days",
    "trained_technicians_available",
    "priority",
}


def validate_columns(columns: set[str]) -> None:
    missing = sorted(REQUIRED_COLUMNS - columns)
    if missing:
        raise ValueError(f"Missing required CSV columns: {', '.join(missing)}")


def validate_quantity(job_id: str, required: int, completed: int) -> None:
    if required < 0 or completed < 0:
        raise ValueError(f"Job {job_id} has negative quantity values")
    if completed > required:
        raise ValueError(f"Job {job_id} has completed quantity greater than required")
