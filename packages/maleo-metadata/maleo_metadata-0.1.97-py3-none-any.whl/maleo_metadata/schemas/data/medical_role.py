from pydantic import BaseModel, Field
from typing import Generic, List, Optional, TypeVar
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


T = TypeVar("T")


class MedicalRoleMixin(BaseModel, Generic[T]):
    medical_role: T = Field(..., description="Medical Role")


class SimpleMedicalRole(MedicalRoleMixin[MedicalRole]):
    pass


class OptionalSimpleMedicalRole(MedicalRoleMixin[Optional[MedicalRole]]):
    pass


class ListOfSimpleMedicalRoles(MedicalRoleMixin[List[MedicalRole]]):
    pass


class ListOfOptionalSimpleMedicalRoles(MedicalRoleMixin[Optional[List[MedicalRole]]]):
    pass


class ExpandedMedicalRole(MedicalRoleMixin[MedicalRoleDataSchema]):
    pass


class OptionalExpandedMedicalRole(MedicalRoleMixin[Optional[MedicalRoleDataSchema]]):
    pass


class ListOfExpandedMedicalRoles(MedicalRoleMixin[List[MedicalRoleDataSchema]]):
    pass


class ListOfOptionalExpandedMedicalRoles(
    MedicalRoleMixin[Optional[List[MedicalRoleDataSchema]]]
):
    pass
