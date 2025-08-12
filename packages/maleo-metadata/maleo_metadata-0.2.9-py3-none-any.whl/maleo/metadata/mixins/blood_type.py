from pydantic import BaseModel, Field


class Key(BaseModel):
    key: str = Field(..., max_length=2, description="Blood type's key")


class Name(BaseModel):
    name: str = Field(..., max_length=2, description="Blood type's name")
