from pydantic import BaseModel, Field


class QKDSessionCreate(BaseModel):
    receiver_user_id: int = Field(gt=0)