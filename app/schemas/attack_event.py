from pydantic import BaseModel


class AttackEventCreate(BaseModel):
    module2_scenario: str
    target_signature_id: int | None = None
    detected: bool = False
    notes: str | None = None