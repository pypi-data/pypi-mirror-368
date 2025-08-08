from typing import List, Optional
from maleo_metadata.enums.organization_type import OrganizationType
from maleo_metadata.schemas.data.organization_type import OrganizationTypeDataSchema


# Simple organization type
type SimpleOrganizationType = OrganizationType
type OptionalSimpleOrganizationType = Optional[SimpleOrganizationType]
type ListOfSimpleOrganizationTypes = List[SimpleOrganizationType]
type OptionalListOfSimpleOrganizationTypes = Optional[List[SimpleOrganizationType]]

# Expanded organization type
type ExpandedOrganizationType = OrganizationTypeDataSchema
type OptionalExpandedOrganizationType = Optional[ExpandedOrganizationType]
type ListOfExpandedOrganizationTypes = List[ExpandedOrganizationType]
type OptionalListOfExpandedOrganizationTypes = Optional[List[ExpandedOrganizationType]]
