from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_mes_upload_endpoint_saves_csv_and_returns_context_summary(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("CORVUS_UPLOAD_DIR", str(tmp_path))
    client = TestClient(app)

    response = client.post(
        "/mes/uploads",
        files={
            "file": (
                "manufacturing_log.csv",
                (
                    "Timestamp,Line_ID,Job_ID,Work_Center,Status\n"
                    "2026-03-24 04:05,Line 1,A1,SMT,Running\n"
                ),
                "text/csv",
            )
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["table_counts"] == {"manufacturing_log": 1}
    assert body["manufacturing_event_count"] == 1
    assert body["normalized_job_count"] == 0
