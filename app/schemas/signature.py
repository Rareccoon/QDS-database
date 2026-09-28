from pydantic import BaseModel, Field


class SignatureCreate(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=10000
    )