from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum


class Priority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class Status(str, Enum):
    ON_TRACK = "On Track"
    AT_RISK = "At Risk"
    BLOCKED = "Blocked"
    LATE = "Late"
    COMPLETE = "Complete"


@dataclass(frozen=True)
class ProductionJob:
    job_id: str
    part_number: str
    customer: str
    build_goal: str
    due_date: date
    quantity_required: int
    quantity_completed: int
    current_step: str
    status: Status
    owner: str
    blocker_reason: str
    last_updated: date
    estimated_cycle_time_days: int
    trained_technicians_available: int
    priority: Priority
    previous_step: str = ""
    previous_status: str = ""
    promised_ship_date: date | None = None

    @property
    def remaining_quantity(self) -> int:
        return max(self.quantity_required - self.quantity_completed, 0)

    @property
    def completion_ratio(self) -> float:
        if self.quantity_required <= 0:
            return 1.0
        return min(self.quantity_completed / self.quantity_required, 1.0)

    @property
    def is_complete(self) -> bool:
        return self.remaining_quantity == 0 or self.status == Status.COMPLETE


def parse_date(value: str) -> date:
    return datetime.strptime(value.strip(), "%Y-%m-%d").date()


def parse_int(value: str, default: int = 0) -> int:
    if value is None or value == "":
        return default
    return int(value)


def parse_optional_date(value: str | None) -> date | None:
    if not value:
        return None
    return parse_date(value)
