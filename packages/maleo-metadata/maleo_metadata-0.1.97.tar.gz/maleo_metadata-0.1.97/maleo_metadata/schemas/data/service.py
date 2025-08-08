from pydantic import BaseModel, Field
from typing import Generic, List, Optional, TypeVar
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


T = TypeVar("T")


class ServiceMixin(BaseModel, Generic[T]):
    service: T = Field(..., description="Service")


class SimpleService(ServiceMixin[Service]):
    pass


class OptionalSimpleService(ServiceMixin[Optional[Service]]):
    pass


class ListOfSimpleServices(ServiceMixin[List[Service]]):
    pass


class ListOfOptionalSimpleServices(ServiceMixin[Optional[List[Service]]]):
    pass


class ExpandedService(ServiceMixin[ServiceDataSchema]):
    pass


class OptionalExpandedService(ServiceMixin[Optional[ServiceDataSchema]]):
    pass


class ListOfExpandedServices(ServiceMixin[List[ServiceDataSchema]]):
    pass


class ListOfOptionalExpandedServices(ServiceMixin[Optional[List[ServiceDataSchema]]]):
    pass


class ExpandedFullService(ServiceMixin[FullServiceDataSchema]):
    pass


class OptionalExpandedFullService(ServiceMixin[Optional[FullServiceDataSchema]]):
    pass


class ListOfExpandedFullServices(ServiceMixin[List[FullServiceDataSchema]]):
    pass


class ListOfOptionalExpandedFullServices(
    ServiceMixin[Optional[List[FullServiceDataSchema]]]
):
    pass
