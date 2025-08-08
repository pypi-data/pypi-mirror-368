from typing import List, Optional
from maleo_metadata.enums.medical_role import MedicalRole
from maleo_metadata.schemas.data.medical_role import MedicalRoleDataSchema


# Simple medical role
type SimpleMedicalRole = MedicalRole
type OptionalSimpleMedicalRole = Optional[SimpleMedicalRole]
type ListOfSimpleMedicalRoles = List[SimpleMedicalRole]
type OptionalListOfSimpleMedicalRoles = Optional[List[SimpleMedicalRole]]

# Expanded medical role
type ExpandedMedicalRole = MedicalRoleDataSchema
type OptionalExpandedMedicalRole = Optional[ExpandedMedicalRole]
type ListOfExpandedMedicalRoles = List[ExpandedMedicalRole]
type OptionalListOfExpandedMedicalRoles = Optional[List[ExpandedMedicalRole]]
