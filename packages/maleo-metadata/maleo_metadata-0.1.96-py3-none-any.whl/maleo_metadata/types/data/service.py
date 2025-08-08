from typing import List, Optional
from maleo_metadata.enums.service import Service
from maleo_metadata.schemas.data.service import ServiceDataSchema, FullServiceDataSchema


# Simple service
type SimpleService = Service
type OptionalSimpleService = Optional[SimpleService]
type ListOfSimpleServices = List[SimpleService]
type OptionalListOfSimpleServices = Optional[List[SimpleService]]

# Expanded service
type ExpandedService = ServiceDataSchema
type OptionalExpandedService = Optional[ExpandedService]
type ListOfExpandedServices = List[ExpandedService]
type OptionalListOfExpandedServices = Optional[List[ExpandedService]]

# Expanded full service
type ExpandedFullService = FullServiceDataSchema
type OptionalExpandedFullService = Optional[ExpandedFullService]
type ListOfExpandedFullServices = List[ExpandedFullService]
type OptionalListOfExpandedFullServices = Optional[List[ExpandedFullService]]
