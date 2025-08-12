from pydantic import BaseModel, Field
from uuid import UUID
from maleo.soma.enums.service import (
    ServiceType as ServiceTypeEnum,
    Category as CategoryEnum,
)


class ServiceType(BaseModel):
    type: ServiceTypeEnum = Field(..., description="Service's type")


class Category(BaseModel):
    category: CategoryEnum = Field(..., description="Service's category")


class Key(BaseModel):
    key: str = Field(..., max_length=20, description="Service's key")


class Name(BaseModel):
    name: str = Field(..., max_length=20, description="Service's name")


class Secret(BaseModel):
    secret: UUID = Field(..., description="Service's secret")
