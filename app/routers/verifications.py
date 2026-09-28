from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import (
    Signature,
    Verification,
    ReceiverMeasurement
)
from app.dependencies import require_role
from app.schemas.verification import VerificationCreate
from app.services.statistics_service import (
    calculate_hoeffding_bound
)

router = APIRouter(
    prefix="/verifications",
    tags=["Verifications"]
)


def calculate_qber(
    db: Session,
    signature_id: int
):
    measurements = (
        db.query(ReceiverMeasurement)
        .filter(
            ReceiverMeasurement.signature_id == signature_id
        )
        .order_by(
            ReceiverMeasurement.trial_no
        )
        .all()
    )

    if not measurements:
        raise HTTPException(
            status_code=400,
            detail="No receiver measurements found"
        )

    m_trials = len(measurements)

    k_mismatches = sum(
        1
        for measurement in measurements
        if measurement.expected_bit
        != measurement.receiver_bit
    )

    observed_qber = (
        k_mismatches / m_trials
    )

    return (
        m_trials,
        k_mismatches,
        observed_qber
    )


@router.post("")
def create_verification(
    verification_data: VerificationCreate,
    current_user: dict = Depends(
        require_role("verifier")
    ),
    db: Session = Depends(get_db)
):
    verifier_user_id = int(current_user["sub"])

    signature = (
        db.query(Signature)
        .filter(
            Signature.id == verification_data.signature_id
        )
        .first()
    )

    if not signature:
        raise HTTPException(
            status_code=404,
            detail="Signature not found"
        )

    # Calculate verification values
    m_trials, k_mismatches, observed_qber = (
        calculate_qber(
            db,
            signature.id
        )
    )

    # Temporary threshold values.
    # The statistical calculation will be improved
    # in the next step.
    hoeffding_bound = calculate_hoeffding_bound(
    m_trials
)
    threshold_used = 0.15

    if observed_qber + hoeffding_bound <= threshold_used:
        verdict = "VERIFIED"
    else:
        verdict = "REJECTED"

    verification = Verification(
        signature_id=signature.id,
        verifier_user_id=verifier_user_id,
        observed_qber=str(observed_qber),
        m_trials=m_trials,
        k_mismatches=k_mismatches,
        hoeffding_bound=str(hoeffding_bound),
        threshold_used=str(threshold_used),
        verdict=verdict
    )

    db.add(verification)
    db.commit()
    db.refresh(verification)

    return {
        "message": "Verification completed",
        "verification": {
            "id": verification.id,
            "signature_id": verification.signature_id,
            "verifier_user_id": verification.verifier_user_id,
            "observed_qber": verification.observed_qber,
            "m_trials": verification.m_trials,
            "k_mismatches": verification.k_mismatches,
            "hoeffding_bound": verification.hoeffding_bound,
            "threshold_used": verification.threshold_used,
            "verdict": verification.verdict
        }
    }


@router.get("/{verification_id}")
def get_verification(
    verification_id: int,
    current_user: dict = Depends(
        require_role("verifier")
    ),
    db: Session = Depends(get_db)
):
    verification = (
        db.query(Verification)
        .filter(
            Verification.id == verification_id
        )
        .first()
    )

    if not verification:
        raise HTTPException(
            status_code=404,
            detail="Verification not found"
        )

    return {
        "verification": {
            "id": verification.id,
            "signature_id": verification.signature_id,
            "verifier_user_id": verification.verifier_user_id,
            "observed_qber": verification.observed_qber,
            "m_trials": verification.m_trials,
            "k_mismatches": verification.k_mismatches,
            "hoeffding_bound": verification.hoeffding_bound,
            "threshold_used": verification.threshold_used,
            "verdict": verification.verdict
        }
    }