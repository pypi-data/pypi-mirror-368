from pydantic import BaseModel, Field


class Key(BaseModel):
    key: str = Field(..., max_length=20, description="Organization type's key")


class Name(BaseModel):
    name: str = Field(..., max_length=20, description="Organization type's name")
