from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter

from app.ingest.csv_loader import load_production_jobs

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
