from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import (
    Signature,
    ProtocolJob,
    CorrectionBit
)
from app.dependencies import require_role
from app.schemas.signature import SignatureCreate
from app.services.orchestration_service import run_signature_background
from app.services.qiskit_service import prepare_signature_metadata


router = APIRouter(
    prefix="/signatures",
    tags=["Signatures"]
)


@router.post("")
def create_signature(
    signature_data: SignatureCreate,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(
        require_role("signer")
    ),
    db: Session = Depends(get_db)
):
    signer_user_id = int(current_user["sub"])

    metadata = prepare_signature_metadata(
        signature_data.message
    )

    last_signature = (
        db.query(Signature)
        .filter(
            Signature.signer_user_id == signer_user_id
        )
        .order_by(
            Signature.sequence_no.desc()
        )
        .first()
    )

    if last_signature:
        sequence_no = last_signature.sequence_no + 1
    else:
        sequence_no = 1

    new_signature = Signature(
        signer_user_id=signer_user_id,
        sequence_no=sequence_no,
        message_digest=metadata["message_digest"],
        basis_schedule=metadata["basis_schedule"],
        expected_bits=metadata["expected_bits"]
    )

    db.add(new_signature)
    db.commit()
    db.refresh(new_signature)

    job = ProtocolJob(
        signature_id=new_signature.id,
        status="PENDING"
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    background_tasks.add_task(
        run_signature_background,
        job.id,
        signature_data.message
    )

    return {
        "message": "Signature execution started",
        "signature": {
            "id": new_signature.id,
            "signer_user_id": new_signature.signer_user_id,
            "sequence_no": new_signature.sequence_no,
            "message_digest": new_signature.message_digest,
            "basis_schedule": new_signature.basis_schedule,
            "expected_bits": new_signature.expected_bits
        },
        "job": {
            "id": job.id,
            "status": job.status
        }
    }


@router.get("/{signature_id}")
def get_signature(
    signature_id: int,
    current_user: dict = Depends(
        require_role("verifier")
    ),
    db: Session = Depends(get_db)
):
    signature = (
        db.query(Signature)
        .filter(
            Signature.id == signature_id
        )
        .first()
    )

    if not signature:
        raise HTTPException(
            status_code=404,
            detail="Signature not found"
        )

    return {
        "signature": {
            "id": signature.id,
            "signer_user_id": signature.signer_user_id,
            "sequence_no": signature.sequence_no,
            "message_digest": signature.message_digest,
            "basis_schedule": signature.basis_schedule,
            "expected_bits": signature.expected_bits
        }
    }


@router.get("/{signature_id}/correction-bits")
def get_correction_bits(
    signature_id: int,
    current_user: dict = Depends(
        require_role("verifier")
    ),
    db: Session = Depends(get_db)
):
    signature = (
        db.query(Signature)
        .filter(
            Signature.id == signature_id
        )
        .first()
    )

    if not signature:
        raise HTTPException(
            status_code=404,
            detail="Signature not found"
        )

    correction_bits = (
        db.query(CorrectionBit)
        .filter(
            CorrectionBit.signature_id == signature_id
        )
        .order_by(
            CorrectionBit.trial_no,
            CorrectionBit.qubit_index
        )
        .all()
    )

    return {
        "signature_id": signature_id,
        "correction_bits": [
            {
                "id": item.id,
                "trial_no": item.trial_no,
                "qubit_index": item.qubit_index,
                "m1": item.m1,
                "m2": item.m2,
                "logged_at": item.logged_at
            }
            for item in correction_bits
        ]
    }