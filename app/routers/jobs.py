from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import ProtocolJob
from app.dependencies import require_role


router = APIRouter(
    prefix="/jobs",
    tags=["Protocol Jobs"]
)


@router.get("/{job_id}")
def get_job_status(
    job_id: int,
    current_user: dict = Depends(
        require_role("signer")
    ),
    db: Session = Depends(get_db)
):
    job = (
        db.query(ProtocolJob)
        .filter(ProtocolJob.id == job_id)
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Protocol job not found"
        )

    return {
        "job": {
            "id": job.id,
            "signature_id": job.signature_id,
            "status": job.status,
            "error_message": job.error_message,
            "created_at": job.created_at,
            "completed_at": job.completed_at
        }
    }