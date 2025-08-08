from pydantic import BaseModel, Field
from typing import List, Optional
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


class SimpleOrganizationType(BaseModel):
    organization_type: OrganizationType = Field(
        ..., description="Single Organization Type"
    )


class OptionalSimpleOrganizationType(BaseModel):
    organization_type: Optional[OrganizationType] = Field(
        None, description="Single Organization Type. (Optional)"
    )


class ListOfSimpleOrganizationTypes(BaseModel):
    organization_types: List[OrganizationType] = Field(
        ..., description="Multiple Organization Types"
    )


class OptionalListOfSimpleOrganizationTypes(BaseModel):
    organization_types: Optional[List[OrganizationType]] = Field(
        None, description="Multiple Organization Types. (Optional)"
    )


class ExpandedOrganizationType(BaseModel):
    organization_type: OrganizationTypeDataSchema = Field(
        ..., description="Single Organization Type Data"
    )


class OptionalExpandedOrganizationType(BaseModel):
    organization_type: Optional[OrganizationTypeDataSchema] = Field(
        None, description="Single Organization Type Data. (Optional)"
    )


class ListOfExpandedOrganizationTypes(BaseModel):
    organization_types: List[OrganizationTypeDataSchema] = Field(
        ..., description="Multiple Organization Types Data"
    )


class OptionalListOfExpandedOrganizationTypes(BaseModel):
    organization_types: Optional[List[OrganizationTypeDataSchema]] = Field(
        None, description="Multiple Organization Types Data. (Optional)"
    )
