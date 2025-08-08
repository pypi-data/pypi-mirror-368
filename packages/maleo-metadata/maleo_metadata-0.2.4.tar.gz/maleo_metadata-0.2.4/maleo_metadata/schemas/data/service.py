from pydantic import BaseModel, Field
from typing import List, Optional
from maleo_soma.mixins.data import DataIdentifier, DataStatus, DataTimestamp
from maleo_soma.mixins.general import Order
from maleo_metadata.enums.service import Service
from maleo_metadata.mixins.service import ServiceType, Category, Key, Name, Secret


class ServiceDataSchema(
    Name,
    Key,
    ServiceType,
    Category,
    Order,
    DataTimestamp,
    DataStatus,
    DataIdentifier,
):
    pass


class FullServiceDataSchema(Secret, ServiceDataSchema):
    pass


class SimpleService(BaseModel):
    service: Service = Field(..., description="Single Service")


class OptionalSimpleService(BaseModel):
    service: Optional[Service] = Field(None, description="Single Service. (Optional)")


class ListOfSimpleServices(BaseModel):
    services: List[Service] = Field(..., description="Multiple Services")


class OptionalListOfSimpleServices(BaseModel):
    services: Optional[List[Service]] = Field(
        None, description="Multiple Services. (Optional)"
    )


class ExpandedService(BaseModel):
    service: ServiceDataSchema = Field(..., description="Single Service Data")


class OptionalExpandedService(BaseModel):
    service: Optional[ServiceDataSchema] = Field(
        None, description="Single Service Data. (Optional)"
    )


class ListOfExpandedServices(BaseModel):
    services: List[ServiceDataSchema] = Field(..., description="Multiple Services Data")


class OptionalListOfExpandedServices(BaseModel):
    services: Optional[List[ServiceDataSchema]] = Field(
        None, description="Multiple Services Data. (Optional)"
    )


class ExpandedFullService(BaseModel):
    full_service: FullServiceDataSchema = Field(
        ..., description="Single Full Service Data"
    )


class OptionalExpandedFullService(BaseModel):
    full_service: Optional[FullServiceDataSchema] = Field(
        None, description="Single Full Service Data. (Optional)"
    )


class ListOfExpandedFullServices(BaseModel):
    full_services: List[FullServiceDataSchema] = Field(
        ..., description="Multiple Full Services Data"
    )


class OptionalListOfExpandedFullServices(BaseModel):
    full_services: Optional[List[FullServiceDataSchema]] = Field(
        None, description="Multiple Full Services Data. (Optional)"
    )
