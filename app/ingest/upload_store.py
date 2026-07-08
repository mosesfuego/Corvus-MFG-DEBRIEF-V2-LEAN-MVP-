from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SavedUpload:
    upload_id: str
    original_filename: str
    stored_path: Path
    context_path: Path
    metadata_path: Path
    received_at: datetime

    def to_dict(self) -> dict[str, str]:
        return {
            "upload_id": self.upload_id,
            "original_filename": self.original_filename,
            "stored_path": str(self.stored_path),
            "context_path": str(self.context_path),
            "metadata_path": str(self.metadata_path),
            "received_at": self.received_at.isoformat(timespec="seconds"),
        }


def save_mes_upload(
    filename: str,
    content: bytes,
    upload_root: str | Path | None = None,
    received_at: datetime | None = None,
) -> SavedUpload:
    if not filename:
        filename = "upload.csv"
    if Path(filename).suffix.lower() != ".csv":
        raise ValueError("Only CSV uploads are supported for the mock MES socket.")
    if not content:
        raise ValueError("Uploaded CSV is empty.")

    received_at = received_at or datetime.now(timezone.utc)
    root = Path(upload_root or os.getenv("CORVUS_UPLOAD_DIR", "uploads/mes"))
    safe_name = _safe_filename(filename)
    upload_id = _unique_upload_id(root, received_at, Path(safe_name).stem)
    upload_dir = root / upload_id
    upload_dir.mkdir(parents=True, exist_ok=False)

    stored_path = upload_dir / safe_name
    context_path = upload_dir / "context.json"
    metadata_path = upload_dir / "metadata.json"

    stored_path.write_bytes(content)
    saved = SavedUpload(
        upload_id=upload_id,
        original_filename=filename,
        stored_path=stored_path,
        context_path=context_path,
        metadata_path=metadata_path,
        received_at=received_at,
    )
    metadata_path.write_text(json.dumps(saved.to_dict(), indent=2), encoding="utf-8")
    return saved


def save_upload_context(saved_upload: SavedUpload, context: dict[str, Any]) -> None:
    saved_upload.context_path.write_text(
        json.dumps(context, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def _safe_filename(filename: str) -> str:
    path_name = Path(filename).name
    stem = re.sub(r"[^a-zA-Z0-9._-]+", "_", Path(path_name).stem).strip("._-")
    suffix = Path(path_name).suffix.lower()
    if not stem:
        stem = "upload"
    return f"{stem}{suffix}"


def _unique_upload_id(root: Path, received_at: datetime, safe_stem: str) -> str:
    timestamp = received_at.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    base = f"{timestamp}-{safe_stem}"
    candidate = base
    counter = 2
    while (root / candidate).exists():
        candidate = f"{base}-{counter}"
        counter += 1
    return candidate
