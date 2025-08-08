from pydantic import BaseModel, Field
from typing import Generic, List, Optional, TypeVar
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


T = TypeVar("T")


class SystemRoleMixin(BaseModel, Generic[T]):
    system_role: T = Field(..., description="System Role")


class SimpleSystemRole(SystemRoleMixin[SystemRole]):
    pass


class OptionalSimpleSystemRole(SystemRoleMixin[Optional[SystemRole]]):
    pass


class ListOfSimpleSystemRoles(SystemRoleMixin[List[SystemRole]]):
    pass


class ListOfOptionalSimpleSystemRoles(SystemRoleMixin[Optional[List[SystemRole]]]):
    pass


class ExpandedSystemRole(SystemRoleMixin[SystemRoleDataSchema]):
    pass


class OptionalExpandedSystemRole(SystemRoleMixin[Optional[SystemRoleDataSchema]]):
    pass


class ListOfExpandedSystemRoles(SystemRoleMixin[List[SystemRoleDataSchema]]):
    pass


class ListOfOptionalExpandedSystemRoles(
    SystemRoleMixin[Optional[List[SystemRoleDataSchema]]]
):
    pass
