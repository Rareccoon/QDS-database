from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import AttackEvent
from app.dependencies import require_role
from app.schemas.attack_event import AttackEventCreate


router = APIRouter(
    prefix="/audit/attack-events",
    tags=["Attack Events"]
)


@router.post("")
def create_attack_event(
    attack_data: AttackEventCreate,
    current_user: dict = Depends(
        require_role("admin")
    ),
    db: Session = Depends(get_db)
):
    injected_by = int(current_user["sub"])

    attack_event = AttackEvent(
        module2_scenario=attack_data.module2_scenario,
        target_signature_id=attack_data.target_signature_id,
        injected_by=injected_by,
        detected=attack_data.detected,
        notes=attack_data.notes
    )

    db.add(attack_event)
    db.commit()
    db.refresh(attack_event)

    return {
        "message": "Attack event recorded",
        "attack_event": {
            "id": attack_event.id,
            "module2_scenario": attack_event.module2_scenario,
            "target_signature_id": attack_event.target_signature_id,
            "injected_by": attack_event.injected_by,
            "detected": attack_event.detected,
            "notes": attack_event.notes,
            "created_at": attack_event.created_at
        }
    }


@router.get("")
def get_attack_events(
    current_user: dict = Depends(
        require_role("admin")
    ),
    db: Session = Depends(get_db)
):
    attack_events = (
        db.query(AttackEvent)
        .order_by(
            AttackEvent.created_at.desc()
        )
        .all()
    )

    return {
        "attack_events": [
            {
                "id": event.id,
                "module2_scenario": event.module2_scenario,
                "target_signature_id": event.target_signature_id,
                "injected_by": event.injected_by,
                "detected": event.detected,
                "notes": event.notes,
                "created_at": event.created_at
            }
            for event in attack_events
        ]
    }