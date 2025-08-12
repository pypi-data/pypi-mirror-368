from pydantic import BaseModel, Field


class Code(BaseModel):
    code: str = Field(..., max_length=20, description="Medical role's code")


class Key(BaseModel):
    key: str = Field(..., max_length=255, description="Medical role's key")


class Name(BaseModel):
    name: str = Field(..., max_length=255, description="Medical role's name")


class MedicalRoleId(BaseModel):
    medical_role_id: int = Field(..., ge=1, description="Medical role's id")
