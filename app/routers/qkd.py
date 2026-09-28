from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import QKDSession
from app.dependencies import require_role
from app.schemas.qkd import QKDSessionCreate


router = APIRouter(
    prefix="/qkd",
    tags=["QKD"]
)


@router.post("/sessions")
def create_qkd_session(
    session_data: QKDSessionCreate,
    current_user: dict = Depends(
        require_role("signer")
    ),
    db: Session = Depends(get_db)
):
    initiator_user_id = int(current_user["sub"])

    if initiator_user_id == session_data.receiver_user_id:
        raise HTTPException(
            status_code=400,
            detail="Initiator and receiver must be different users"
        )

    # Temporary values.
    # These will later come from the actual
    # QKD/Module 1 execution.
    basis_log = "10100110"
    estimated_qber = "0.0"
    accepted = True

    qkd_session = QKDSession(
        initiator_user_id=initiator_user_id,
        receiver_user_id=session_data.receiver_user_id,
        basis_log=basis_log,
        estimated_qber=estimated_qber,
        accepted=accepted
    )

    db.add(qkd_session)
    db.commit()
    db.refresh(qkd_session)

    return {
        "message": "QKD session created successfully",
        "qkd_session": {
            "id": qkd_session.id,
            "initiator_user_id": qkd_session.initiator_user_id,
            "receiver_user_id": qkd_session.receiver_user_id,
            "basis_log": qkd_session.basis_log,
            "estimated_qber": qkd_session.estimated_qber,
            "accepted": qkd_session.accepted,
            "timestamp": qkd_session.timestamp
        }
    }