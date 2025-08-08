from pydantic import BaseModel, Field
from typing import Generic, List, Optional, TypeVar
from maleo_soma.mixins.data import DataIdentifier, DataStatus, DataTimestamp
from maleo_soma.mixins.general import Order
from maleo_metadata.enums.gender import Gender
from maleo_metadata.mixins.gender import Key, Name


class GenderDataSchema(
    Name,
    Key,
    Order,
    DataTimestamp,
    DataStatus,
    DataIdentifier,
):
    pass


T = TypeVar("T")


class GenderMixin(BaseModel, Generic[T]):
    gender: T = Field(..., description="Gender")


class SimpleGender(GenderMixin[Gender]):
    pass


class OptionalSimpleGender(GenderMixin[Optional[Gender]]):
    pass


class ListOfSimpleGenders(GenderMixin[List[Gender]]):
    pass


class ListOfOptionalSimpleGenders(GenderMixin[Optional[List[Gender]]]):
    pass


class ExpandedGender(GenderMixin[GenderDataSchema]):
    pass


class OptionalExpandedGender(GenderMixin[Optional[GenderDataSchema]]):
    pass


class ListOfExpandedGenders(GenderMixin[List[GenderDataSchema]]):
    pass


class ListOfOptionalExpandedGenders(GenderMixin[Optional[List[GenderDataSchema]]]):
    pass
