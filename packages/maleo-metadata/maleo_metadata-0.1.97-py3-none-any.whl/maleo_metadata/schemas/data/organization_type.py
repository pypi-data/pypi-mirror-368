from pydantic import BaseModel, Field
from typing import Generic, List, Optional, TypeVar
from maleo_soma.mixins.data import DataIdentifier, DataStatus, DataTimestamp
from maleo_soma.mixins.general import Order
from maleo_metadata.enums.organization_type import OrganizationType
from maleo_metadata.mixins.organization_type import Key, Name


class OrganizationTypeDataSchema(
    Name,
    Key,
    Order,
    DataTimestamp,
    DataStatus,
    DataIdentifier,
):
    pass


T = TypeVar("T")


class OrganizationTypeMixin(BaseModel, Generic[T]):
    organization_type: T = Field(..., description="Organization Type")


class SimpleOrganizationType(OrganizationTypeMixin[OrganizationType]):
    pass


class OptionalSimpleOrganizationType(OrganizationTypeMixin[Optional[OrganizationType]]):
    pass


class ListOfSimpleOrganizationTypes(OrganizationTypeMixin[List[OrganizationType]]):
    pass


class ListOfOptionalSimpleOrganizationTypes(
    OrganizationTypeMixin[Optional[List[OrganizationType]]]
):
    pass


class ExpandedOrganizationType(OrganizationTypeMixin[OrganizationTypeDataSchema]):
    pass


class OptionalExpandedOrganizationType(
    OrganizationTypeMixin[Optional[OrganizationTypeDataSchema]]
):
    pass


class ListOfExpandedOrganizationTypes(
    OrganizationTypeMixin[List[OrganizationTypeDataSchema]]
):
    pass


class ListOfOptionalExpandedOrganizationTypes(
    OrganizationTypeMixin[Optional[List[OrganizationTypeDataSchema]]]
):
    pass
