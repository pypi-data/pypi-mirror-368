from pydantic import BaseModel, Field
from typing import List, Optional
from maleo_soma.mixins.data import DataIdentifier, DataStatus, DataTimestamp
from maleo_soma.mixins.general import Order
from maleo_metadata.enums.medical_role import MedicalRole
from maleo_metadata.mixins.medical_role import ParentId, Code, Key, Name


class MedicalRoleDataSchema(
    Name,
    Key,
    Code,
    Order,
    ParentId,
    DataTimestamp,
    DataStatus,
    DataIdentifier,
):
    pass


class SimpleMedicalRole(BaseModel):
    medical_role: MedicalRole = Field(..., description="Single Medical Role")


class OptionalSimpleMedicalRole(BaseModel):
    medical_role: Optional[MedicalRole] = Field(
        None, description="Single Medical Role. (Optional)"
    )


class ListOfSimpleMedicalRoles(BaseModel):
    medical_roles: List[MedicalRole] = Field(..., description="Multiple Medical Roles")


class OptionalListOfSimpleMedicalRoles(BaseModel):
    medical_roles: Optional[List[MedicalRole]] = Field(
        None, description="Multiple Medical Roles. (Optional)"
    )


class ExpandedMedicalRole(BaseModel):
    medical_role: MedicalRoleDataSchema = Field(
        ..., description="Single Medical Role Data"
    )


class OptionalExpandedMedicalRole(BaseModel):
    medical_role: Optional[MedicalRoleDataSchema] = Field(
        None, description="Single Medical Role Data. (Optional)"
    )


class ListOfExpandedMedicalRoles(BaseModel):
    medical_roles: List[MedicalRoleDataSchema] = Field(
        ..., description="Multiple Medical Roles Data"
    )


class OptionalListOfExpandedMedicalRoles(BaseModel):
    medical_roles: Optional[List[MedicalRoleDataSchema]] = Field(
        None, description="Multiple Medical Roles Data. (Optional)"
    )
