from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from app.models.production import ProductionJob


class MesTableType(str, Enum):
    MANUFACTURING_LOG = "manufacturing_log"
    WORK_ORDERS = "work_orders"
    OPERATIONS = "operations"
    QUALITY = "quality"
    RECEIVING = "receiving"
    INVENTORY = "inventory"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class MesEvent:
    timestamp: datetime
    line_id: str
    job_id: str
    customer_tier: str
    work_center: str
    status: str
    error_code: str
    operator_id: str
    part_number: str
    yield_rate: float | None
    comments: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(timespec="minutes"),
            "line_id": self.line_id,
            "job_id": self.job_id,
            "customer_tier": self.customer_tier,
            "work_center": self.work_center,
            "status": self.status,
            "error_code": self.error_code,
            "operator_id": self.operator_id,
            "part_number": self.part_number,
            "yield_rate": self.yield_rate,
            "comments": self.comments,
        }


@dataclass(frozen=True)
class MesTable:
    file_name: str
    table_type: MesTableType
    columns: list[str]
    rows: list[dict[str, str]]

    @property
    def row_count(self) -> int:
        return len(self.rows)

    def sample_rows(self, limit: int = 5) -> list[dict[str, str]]:
        return self.rows[:limit]

    def to_dict(self, sample_limit: int = 25) -> dict[str, Any]:
        return {
            "file_name": self.file_name,
            "table_type": self.table_type.value,
            "columns": self.columns,
            "row_count": self.row_count,
            "sample_rows": self.sample_rows(sample_limit),
        }


@dataclass(frozen=True)
class MesIngestionBundle:
    source: str
    tables: list[MesTable]
    production_jobs: list[ProductionJob]
    manufacturing_events: list[MesEvent] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def table_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for table in self.tables:
            counts[table.table_type.value] = counts.get(table.table_type.value, 0) + 1
        return counts

    def to_llm_context(self, row_limit: int = 25) -> dict[str, Any]:
        return {
            "source": self.source,
            "table_counts": self.table_counts,
            "warnings": self.warnings,
            "normalized_jobs": [production_job_to_dict(job) for job in self.production_jobs],
            "manufacturing_events": [
                event.to_dict() for event in self.manufacturing_events[:row_limit]
            ],
            "manufacturing_event_summary": summarize_manufacturing_events(
                self.manufacturing_events
            ),
            "raw_tables": [table.to_dict(row_limit) for table in self.tables],
        }


def summarize_manufacturing_events(events: list[MesEvent]) -> dict[str, Any]:
    jobs: dict[str, dict[str, Any]] = {}
    lines: dict[str, dict[str, Any]] = {}

    for event in sorted(events, key=lambda item: item.timestamp):
        job_summary = jobs.setdefault(
            event.job_id,
            {
                "latest_timestamp": "",
                "latest_status": "",
                "customer_tier": event.customer_tier,
                "work_centers": [],
                "line_ids": [],
                "statuses": {},
                "error_codes": {},
                "blocked_or_stopped_events": 0,
                "low_yield_events": 0,
                "comments": [],
            },
        )
        _append_unique(job_summary["work_centers"], event.work_center)
        _append_unique(job_summary["line_ids"], event.line_id)
        _increment(job_summary["statuses"], event.status)
        if event.error_code and event.error_code.lower() != "none":
            _increment(job_summary["error_codes"], event.error_code)
        if event.status.lower() in {"blocked", "stopped", "warning", "backlog"}:
            job_summary["blocked_or_stopped_events"] += 1
        if event.yield_rate is not None and event.yield_rate < 0.9:
            job_summary["low_yield_events"] += 1
        if event.comments:
            job_summary["comments"].append(event.comments)
        job_summary["latest_timestamp"] = event.timestamp.isoformat(timespec="minutes")
        job_summary["latest_status"] = event.status

        line_summary = lines.setdefault(
            event.line_id,
            {
                "latest_timestamp": "",
                "latest_job_id": "",
                "latest_status": "",
                "work_centers": [],
                "event_count": 0,
                "blocked_or_stopped_events": 0,
            },
        )
        _append_unique(line_summary["work_centers"], event.work_center)
        line_summary["event_count"] += 1
        if event.status.lower() in {"blocked", "stopped", "warning", "backlog"}:
            line_summary["blocked_or_stopped_events"] += 1
        line_summary["latest_timestamp"] = event.timestamp.isoformat(timespec="minutes")
        line_summary["latest_job_id"] = event.job_id
        line_summary["latest_status"] = event.status

    return {
        "event_count": len(events),
        "job_count": len(jobs),
        "jobs": jobs,
        "lines": lines,
    }


def production_job_to_dict(job: ProductionJob) -> dict[str, Any]:
    return {
        "job_id": job.job_id,
        "part_number": job.part_number,
        "customer": job.customer,
        "build_goal": job.build_goal,
        "due_date": job.due_date.isoformat(),
        "quantity_required": job.quantity_required,
        "quantity_completed": job.quantity_completed,
        "current_step": job.current_step,
        "status": job.status.value,
        "owner": job.owner,
        "blocker_reason": job.blocker_reason,
        "last_updated": job.last_updated.isoformat(),
        "estimated_cycle_time_days": job.estimated_cycle_time_days,
        "trained_technicians_available": job.trained_technicians_available,
        "priority": job.priority.value,
        "previous_step": job.previous_step,
        "previous_status": job.previous_status,
        "promised_ship_date": (
            job.promised_ship_date.isoformat() if job.promised_ship_date else None
        ),
    }


def source_label(path: str | Path) -> str:
    return str(Path(path))


def _append_unique(values: list[str], value: str) -> None:
    if value and value not in values:
        values.append(value)


def _increment(counts: dict[str, int], value: str) -> None:
    if value:
        counts[value] = counts.get(value, 0) + 1
