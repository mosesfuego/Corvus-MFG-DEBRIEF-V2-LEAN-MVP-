from __future__ import annotations

from app.ingest.mock_mes_socket import classify_mes_csv, load_mock_mes_export
from app.models.mes import MesTableType
from app.models.production import Priority, Status


def test_classifies_work_order_csv_from_headers() -> None:
    table_type = classify_mes_csv(
        "export.csv",
        ["Work Order", "Part", "Customer", "Need Date", "Order Qty"],
    )

    assert table_type == MesTableType.WORK_ORDERS


def test_load_mock_mes_export_normalizes_work_orders() -> None:
    bundle = load_mock_mes_export("samples/mock_mes")

    assert bundle.table_counts["work_orders"] == 1
    assert bundle.table_counts["manufacturing_log"] == 1
    assert bundle.table_counts["quality"] == 1
    assert len(bundle.production_jobs) == 3
    assert len(bundle.manufacturing_events) == 12
    assert bundle.production_jobs[0].job_id == "WO-1047"
    assert bundle.production_jobs[0].status == Status.BLOCKED
    assert bundle.production_jobs[1].priority == Priority.CRITICAL


def test_mock_mes_bundle_produces_llm_context() -> None:
    bundle = load_mock_mes_export("samples/mock_mes")
    context = bundle.to_llm_context(row_limit=2)

    assert context["normalized_jobs"][0]["job_id"] == "WO-1047"
    assert context["manufacturing_event_summary"]["jobs"]["ACS-2241"]["latest_status"] == "Stopped"
    assert context["manufacturing_event_summary"]["jobs"]["ACS-2241"]["error_codes"] == {
        "ERR_FEED_MISMATCH": 2,
        "ERR_CERT_EXPIRED": 1,
    }
    assert context["raw_tables"][0]["row_count"] >= 1
    assert len(context["raw_tables"][0]["sample_rows"]) <= 2


def test_uploaded_manufacturing_log_file_loads_as_events() -> None:
    bundle = load_mock_mes_export("samples/mock_mes/manufacturing_log.csv")
    context = bundle.to_llm_context()

    assert bundle.table_counts == {"manufacturing_log": 1}
    assert len(bundle.production_jobs) == 0
    assert len(bundle.manufacturing_events) == 12
    assert context["manufacturing_event_summary"]["jobs"]["ACS-2198"]["latest_status"] == "Blocked"
