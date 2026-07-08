from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.ingest.csv_loader import load_production_jobs
from app.ingest.mock_mes_socket import load_mock_mes_export
from app.ingest.upload_store import save_mes_upload, save_upload_context

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/sample/jobs")
def sample_jobs() -> dict[str, object]:
    sample_path = Path("samples/production_status.csv")
    jobs = load_production_jobs(sample_path)
    return {
        "count": len(jobs),
        "jobs": [
            {
                "job_id": job.job_id,
                "part_number": job.part_number,
                "customer": job.customer,
                "due_date": job.due_date.isoformat(),
                "status": job.status.value,
                "owner": job.owner,
            }
            for job in jobs
        ],
    }


@router.post("/mes/uploads")
async def upload_mes_csv(file: UploadFile = File(...)) -> dict[str, object]:
    try:
        saved_upload = save_mes_upload(
            filename=file.filename or "upload.csv",
            content=await file.read(),
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    try:
        bundle = load_mock_mes_export(saved_upload.stored_path)
        context = bundle.to_llm_context()
        save_upload_context(saved_upload, context)
    except Exception as error:
        raise HTTPException(
            status_code=422,
            detail=f"Upload was saved, but MES context generation failed: {error}",
        ) from error

    return {
        **saved_upload.to_dict(),
        "table_counts": bundle.table_counts,
        "normalized_job_count": len(bundle.production_jobs),
        "manufacturing_event_count": len(bundle.manufacturing_events),
        "warnings": bundle.warnings,
    }
