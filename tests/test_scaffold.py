from __future__ import annotations

from datetime import date

from app.analysis.risk_rules import detect_basic_risks
from app.ingest.csv_loader import load_production_jobs


def test_sample_fixture_loads() -> None:
    jobs = load_production_jobs("samples/production_status.csv")

    assert len(jobs) == 3
    assert jobs[0].job_id == "1047"


def test_basic_risk_detection_finds_demo_risks() -> None:
    jobs = load_production_jobs("samples/production_status.csv")
    findings = detect_basic_risks(jobs, date(2026, 7, 7))

    assert len(findings) >= 3
    assert {finding.job_id for finding in findings} >= {"1047", "1052", "1055"}
