from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class RiskType(str, Enum):
    LATE = "late"
    BLOCKED = "blocked"
    SCHEDULE = "schedule"
    STALE_UPDATE = "stale_update"
    STAFFING = "staffing"
    CHANGE = "change"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class RiskFinding:
    job_id: str
    risk_type: RiskType
    severity: Severity
    owner: str
    summary: str
    evidence: str
    recommended_action: str
    days_to_due: int
    impact: str
    questions: list[str] = field(default_factory=list)
