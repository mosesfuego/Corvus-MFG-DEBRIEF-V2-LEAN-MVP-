from __future__ import annotations

import csv
import re
from datetime import date, datetime
from pathlib import Path

from app.models.mes import MesEvent, MesIngestionBundle, MesTable, MesTableType, source_label
from app.models.production import Priority, ProductionJob, Status

TABLE_HINTS: dict[MesTableType, set[str]] = {
    MesTableType.MANUFACTURING_LOG: {
        "timestamp",
        "line",
        "line_id",
        "job",
        "job_id",
        "work_center",
        "status",
        "error",
        "error_code",
        "operator",
        "operator_id",
        "yield",
        "yield_rate",
        "comments",
    },
    MesTableType.WORK_ORDERS: {
        "job",
        "job_id",
        "work_order",
        "wo",
        "order",
        "part",
        "part_number",
        "due",
        "due_date",
        "qty",
        "quantity",
    },
    MesTableType.OPERATIONS: {
        "operation",
        "op",
        "step",
        "work_center",
        "routing",
        "machine",
        "queue",
    },
    MesTableType.QUALITY: {
        "quality",
        "inspection",
        "defect",
        "hold",
        "ncr",
        "disposition",
    },
    MesTableType.RECEIVING: {
        "receiving",
        "receiver",
        "receipt",
        "supplier",
        "po",
        "dock",
        "material",
    },
    MesTableType.INVENTORY: {
        "inventory",
        "stock",
        "on_hand",
        "shortage",
        "bin",
        "warehouse",
    },
}

ALIASES: dict[str, tuple[str, ...]] = {
    "job_id": ("job_id", "job", "work_order", "work_order_id", "wo", "wo_number", "order"),
    "part_number": ("part_number", "part", "item", "item_number", "sku"),
    "customer": ("customer", "customer_name", "account"),
    "build_goal": ("build_goal", "description", "job_description", "order_description"),
    "due_date": ("due_date", "due", "need_date", "promise_date", "ship_date"),
    "quantity_required": ("quantity_required", "qty_required", "required_qty", "order_qty", "qty"),
    "quantity_completed": ("quantity_completed", "qty_completed", "completed_qty", "good_qty"),
    "current_step": ("current_step", "step", "operation", "op_name", "work_center", "routing_step"),
    "status": ("status", "job_status", "order_status", "state"),
    "owner": ("owner", "responsible", "department", "team", "work_center_owner"),
    "blocker_reason": ("blocker_reason", "blocker", "hold_reason", "issue", "constraint"),
    "last_updated": ("last_updated", "updated_at", "last_activity", "status_date"),
    "estimated_cycle_time_days": ("estimated_cycle_time_days", "cycle_days", "remaining_days"),
    "trained_technicians_available": (
        "trained_technicians_available",
        "techs_available",
        "operators",
    ),
    "priority": ("priority", "rank", "expedite"),
    "previous_step": ("previous_step", "prior_step"),
    "previous_status": ("previous_status", "prior_status"),
    "promised_ship_date": ("promised_ship_date", "promise_date", "ship_date"),
}


def load_mock_mes_export(path: str | Path) -> MesIngestionBundle:
    source_path = Path(path)
    csv_paths = _csv_paths(source_path)
    warnings: list[str] = []
    tables: list[MesTable] = []

    for csv_path in csv_paths:
        table = _read_mes_table(csv_path)
        tables.append(table)
        if table.table_type == MesTableType.UNKNOWN:
            warnings.append(f"Could not classify {csv_path.name}; included as raw context only.")

    production_jobs = _normalize_production_jobs(tables, warnings)
    manufacturing_events = _normalize_manufacturing_events(tables, warnings)
    return MesIngestionBundle(
        source=source_label(source_path),
        tables=tables,
        production_jobs=production_jobs,
        manufacturing_events=manufacturing_events,
        warnings=warnings,
    )


def classify_mes_csv(file_name: str, columns: list[str]) -> MesTableType:
    tokens = set(_tokenize(file_name))
    for column in columns:
        tokens.update(_tokenize(column))

    scores = {
        table_type: len(tokens & hints)
        for table_type, hints in TABLE_HINTS.items()
    }
    best_type = max(scores, key=scores.get)
    return best_type if scores[best_type] >= 2 else MesTableType.UNKNOWN


def _csv_paths(path: Path) -> list[Path]:
    if path.is_file():
        if path.suffix.lower() != ".csv":
            raise ValueError(f"Expected a CSV file, got: {path}")
        return [path]

    if not path.exists():
        raise FileNotFoundError(path)

    return sorted(child for child in path.iterdir() if child.suffix.lower() == ".csv")


def _read_mes_table(path: Path) -> MesTable:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        columns = [_normalize_header(column) for column in reader.fieldnames or []]
        rows = [
            {_normalize_header(key): (value or "").strip() for key, value in row.items()}
            for row in reader
        ]

    return MesTable(
        file_name=path.name,
        table_type=classify_mes_csv(path.name, columns),
        columns=columns,
        rows=rows,
    )


def _normalize_production_jobs(
    tables: list[MesTable],
    warnings: list[str],
) -> list[ProductionJob]:
    jobs: list[ProductionJob] = []
    for table in tables:
        if table.table_type != MesTableType.WORK_ORDERS:
            continue

        for index, row in enumerate(table.rows, start=2):
            try:
                jobs.append(_row_to_production_job(row))
            except ValueError as error:
                warnings.append(
                    f"{table.file_name}:{index} skipped during job normalization: {error}"
                )

    return jobs


def _normalize_manufacturing_events(
    tables: list[MesTable],
    warnings: list[str],
) -> list[MesEvent]:
    events: list[MesEvent] = []
    for table in tables:
        if table.table_type != MesTableType.MANUFACTURING_LOG:
            continue

        for index, row in enumerate(table.rows, start=2):
            try:
                events.append(_row_to_mes_event(row))
            except ValueError as error:
                warnings.append(
                    f"{table.file_name}:{index} skipped during event normalization: {error}"
                )

    return sorted(events, key=lambda event: event.timestamp)


def _row_to_mes_event(row: dict[str, str]) -> MesEvent:
    return MesEvent(
        timestamp=_datetime_value(_required_event(row, "timestamp")),
        line_id=_event_value(row, "line_id"),
        job_id=_required_event(row, "job_id"),
        customer_tier=_event_value(row, "customer_tier"),
        work_center=_event_value(row, "work_center"),
        status=_event_value(row, "status") or "Unknown",
        error_code=_event_value(row, "error_code"),
        operator_id=_event_value(row, "operator_id"),
        part_number=_event_value(row, "part_number"),
        yield_rate=_float_value(_event_value(row, "yield_rate")),
        comments=_event_value(row, "comments"),
    )


def _row_to_production_job(row: dict[str, str]) -> ProductionJob:
    job_id = _required(row, "job_id")
    quantity_required = _int_value(_value(row, "quantity_required"), default=1)
    quantity_completed = _int_value(_value(row, "quantity_completed"), default=0)

    return ProductionJob(
        job_id=job_id,
        part_number=_value(row, "part_number") or "Unknown",
        customer=_value(row, "customer") or "Unknown",
        build_goal=_value(row, "build_goal") or f"Complete job {job_id}",
        due_date=_date_value(_required(row, "due_date")),
        quantity_required=quantity_required,
        quantity_completed=min(quantity_completed, quantity_required),
        current_step=_value(row, "current_step") or "Unknown",
        status=_status_value(_value(row, "status")),
        owner=_value(row, "owner") or "Unassigned",
        blocker_reason=_value(row, "blocker_reason"),
        last_updated=_date_value(_value(row, "last_updated"), default=date.today()),
        estimated_cycle_time_days=_int_value(_value(row, "estimated_cycle_time_days"), default=1),
        trained_technicians_available=_int_value(
            _value(row, "trained_technicians_available"),
            default=0,
        ),
        priority=_priority_value(_value(row, "priority")),
        previous_step=_value(row, "previous_step"),
        previous_status=_value(row, "previous_status"),
        promised_ship_date=_optional_date_value(_value(row, "promised_ship_date")),
    )


def _normalize_header(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")


def _tokenize(value: str) -> list[str]:
    normalized = _normalize_header(value)
    return [token for token in normalized.split("_") if token]


def _value(row: dict[str, str], canonical_key: str) -> str:
    for key in ALIASES[canonical_key]:
        if key in row and row[key]:
            return row[key].strip()
    return ""


def _required(row: dict[str, str], canonical_key: str) -> str:
    value = _value(row, canonical_key)
    if not value:
        raise ValueError(f"missing {canonical_key}")
    return value


def _int_value(value: str, default: int) -> int:
    if not value:
        return default
    cleaned = value.replace(",", "").strip()
    if cleaned.lower() in {"yes", "true"}:
        return 1
    if cleaned.lower() in {"no", "false"}:
        return 0
    return int(float(cleaned))


def _date_value(value: str, default: date | None = None) -> date:
    parsed = _optional_date_value(value)
    if parsed:
        return parsed
    if default:
        return default
    raise ValueError(f"invalid date: {value!r}")


def _optional_date_value(value: str) -> date | None:
    if not value:
        return None

    for date_format in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y", "%Y/%m/%d"):
        try:
            return datetime.strptime(value.strip(), date_format).date()
        except ValueError:
            pass
    return None


def _datetime_value(value: str) -> datetime:
    for date_format in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S", "%m/%d/%Y %H:%M"):
        try:
            return datetime.strptime(value.strip(), date_format)
        except ValueError:
            pass

    parsed_date = _optional_date_value(value)
    if parsed_date:
        return datetime.combine(parsed_date, datetime.min.time())
    raise ValueError(f"invalid timestamp: {value!r}")


def _float_value(value: str) -> float | None:
    if not value or value.lower() == "none":
        return None
    return float(value)


def _event_value(row: dict[str, str], canonical_key: str) -> str:
    aliases = {
        "timestamp": ("timestamp", "time", "event_time"),
        "line_id": ("line_id", "line", "production_line"),
        "job_id": ("job_id", "job", "work_order", "wo"),
        "customer_tier": ("customer_tier", "customer_priority", "tier"),
        "work_center": ("work_center", "station", "machine", "operation"),
        "status": ("status", "state", "event_status"),
        "error_code": ("error_code", "error", "fault_code"),
        "operator_id": ("operator_id", "operator", "employee_id"),
        "part_number": ("part_number", "part", "item"),
        "yield_rate": ("yield_rate", "yield", "first_pass_yield", "fpy"),
        "comments": ("comments", "comment", "notes"),
    }
    for key in aliases[canonical_key]:
        if key in row and row[key]:
            return row[key].strip()
    return ""


def _required_event(row: dict[str, str], canonical_key: str) -> str:
    value = _event_value(row, canonical_key)
    if not value:
        raise ValueError(f"missing {canonical_key}")
    return value


def _status_value(value: str) -> Status:
    normalized = _normalize_header(value)
    if normalized in {"complete", "completed", "closed", "done"}:
        return Status.COMPLETE
    if normalized in {"blocked", "hold", "on_hold", "quality_hold", "material_hold"}:
        return Status.BLOCKED
    if normalized in {"late", "past_due", "overdue"}:
        return Status.LATE
    if normalized in {"risk", "at_risk", "expedite", "hot"}:
        return Status.AT_RISK
    return Status.ON_TRACK


def _priority_value(value: str) -> Priority:
    normalized = _normalize_header(value)
    if normalized in {"critical", "hot", "expedite", "1", "p1"}:
        return Priority.CRITICAL
    if normalized in {"high", "2", "p2"}:
        return Priority.HIGH
    if normalized in {"low", "4", "p4"}:
        return Priority.LOW
    return Priority.MEDIUM
