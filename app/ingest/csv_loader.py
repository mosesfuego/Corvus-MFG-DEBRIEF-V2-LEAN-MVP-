from __future__ import annotations

import csv
from pathlib import Path

from app.ingest.validators import validate_columns, validate_quantity
from app.models.production import (
    Priority,
    ProductionJob,
    Status,
    parse_date,
    parse_int,
    parse_optional_date,
)


def load_production_jobs(path: str | Path) -> list[ProductionJob]:
    csv_path = Path(path)
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        validate_columns(set(reader.fieldnames or []))
        return [_row_to_job(row) for row in reader]


def _row_to_job(row: dict[str, str]) -> ProductionJob:
    required = parse_int(row["quantity_required"])
    completed = parse_int(row["quantity_completed"])
    validate_quantity(row["job_id"], required, completed)

    return ProductionJob(
        job_id=row["job_id"].strip(),
        part_number=row["part_number"].strip(),
        customer=row["customer"].strip(),
        build_goal=row["build_goal"].strip(),
        due_date=parse_date(row["due_date"]),
        quantity_required=required,
        quantity_completed=completed,
        current_step=row["current_step"].strip(),
        status=Status(row["status"].strip()),
        owner=row["owner"].strip(),
        blocker_reason=row.get("blocker_reason", "").strip(),
        last_updated=parse_date(row["last_updated"]),
        estimated_cycle_time_days=parse_int(row["estimated_cycle_time_days"], 1),
        trained_technicians_available=parse_int(row["trained_technicians_available"]),
        priority=Priority(row["priority"].strip()),
        previous_step=row.get("previous_step", "").strip(),
        previous_status=row.get("previous_status", "").strip(),
        promised_ship_date=parse_optional_date(row.get("promised_ship_date")),
    )
