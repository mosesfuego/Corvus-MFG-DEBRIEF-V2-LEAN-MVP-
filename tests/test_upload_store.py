from __future__ import annotations

import json
from datetime import datetime, timezone

from app.ingest.mock_mes_socket import load_mock_mes_export
from app.ingest.upload_store import save_mes_upload, save_upload_context


def test_save_mes_upload_persists_csv_and_context(tmp_path) -> None:
    source = "Timestamp,Line_ID,Job_ID,Work_Center,Status\n2026-03-24 04:05,Line 1,A1,SMT,Running\n"
    saved = save_mes_upload(
        filename="manufacturing log (1).csv",
        content=source.encode("utf-8"),
        upload_root=tmp_path,
        received_at=datetime(2026, 3, 24, 8, 0, tzinfo=timezone.utc),
    )

    bundle = load_mock_mes_export(saved.stored_path)
    context = bundle.to_llm_context()
    save_upload_context(saved, context)

    assert saved.upload_id == "20260324T080000Z-manufacturing_log_1"
    assert saved.stored_path.exists()
    assert saved.context_path.exists()
    assert json.loads(saved.context_path.read_text())["table_counts"] == {
        "manufacturing_log": 1
    }


def test_save_mes_upload_rejects_non_csv(tmp_path) -> None:
    try:
        save_mes_upload("mes.xlsx", b"data", upload_root=tmp_path)
    except ValueError as error:
        assert "CSV" in str(error)
    else:
        raise AssertionError("Expected non-CSV upload to be rejected")
