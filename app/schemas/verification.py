from pydantic import BaseModel, Field


class VerificationCreate(BaseModel):
    signature_id: int = Field(gt=0)