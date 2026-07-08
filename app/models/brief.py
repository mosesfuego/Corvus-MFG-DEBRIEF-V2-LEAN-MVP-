from __future__ import annotations

from dataclasses import dataclass, field

from app.models.production import ProductionJob
from app.models.risk import RiskFinding, RiskType, Severity


@dataclass(frozen=True)
class DailyBrief:
    production_date: str
    headline: str
    jobs: list[ProductionJob]
    findings: list[RiskFinding]
    changed_jobs: list[ProductionJob] = field(default_factory=list)
    owner_questions: dict[str, list[str]] = field(default_factory=dict)

    @property
    def blocked_count(self) -> int:
        return sum(1 for finding in self.findings if finding.risk_type == RiskType.BLOCKED)

    @property
    def critical_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == Severity.CRITICAL)
