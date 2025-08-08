from pydantic import BaseModel, Field
from typing import List, Optional
from maleo_soma.mixins.data import DataIdentifier, DataStatus, DataTimestamp
from maleo_soma.mixins.general import Order
from maleo_metadata.enums.system_role import SystemRole
from maleo_metadata.mixins.system_role import Key, Name


class SystemRoleDataSchema(
    Name,
    Key,
    Order,
    DataTimestamp,
    DataStatus,
    DataIdentifier,
):
    pass


class SimpleSystemRole(BaseModel):
    system_role: SystemRole = Field(..., description="Single System Role")


class OptionalSimpleSystemRole(BaseModel):
    system_role: Optional[SystemRole] = Field(
        None, description="Single System Role. (Optional)"
    )


class ListOfSimpleSystemRoles(BaseModel):
    system_roles: List[SystemRole] = Field(..., description="Multiple System Roles")


class OptionalListOfSimpleSystemRoles(BaseModel):
    system_roles: Optional[List[SystemRole]] = Field(
        None, description="Multiple System Roles. (Optional)"
    )


class ExpandedSystemRole(BaseModel):
    system_role: SystemRoleDataSchema = Field(
        ..., description="Single System Role Data"
    )


class OptionalExpandedSystemRole(BaseModel):
    system_role: Optional[SystemRoleDataSchema] = Field(
        None, description="Single System Role Data. (Optional)"
    )


class ListOfExpandedSystemRoles(BaseModel):
    system_roles: List[SystemRoleDataSchema] = Field(
        ..., description="Multiple System Roles Data"
    )


class OptionalListOfExpandedSystemRoles(BaseModel):
    system_roles: Optional[List[SystemRoleDataSchema]] = Field(
        None, description="Multiple System Roles Data. (Optional)"
    )
