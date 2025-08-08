from typing import List, Optional
from maleo_metadata.enums.system_role import SystemRole
from maleo_metadata.schemas.data.system_role import SystemRoleDataSchema


# Simple system role
type SimpleSystemRole = SystemRole
type OptionalSimpleSystemRole = Optional[SimpleSystemRole]
type ListOfSimpleSystemRoles = List[SimpleSystemRole]
type OptionalListOfSimpleSystemRoles = Optional[List[SimpleSystemRole]]

# Expanded system role
type ExpandedSystemRole = SystemRoleDataSchema
type OptionalExpandedSystemRole = Optional[ExpandedSystemRole]
type ListOfExpandedSystemRoles = List[ExpandedSystemRole]
type OptionalListOfExpandedSystemRoles = Optional[List[ExpandedSystemRole]]
