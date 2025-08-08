from pydantic import BaseModel, Field
from typing import Generic, List, Optional, TypeVar
from maleo_soma.mixins.data import DataIdentifier, DataStatus, DataTimestamp
from maleo_soma.mixins.general import Order
from maleo_metadata.enums.blood_type import BloodType
from maleo_metadata.mixins.blood_type import Key, Name


class BloodTypeDataSchema(
    Name,
    Key,
    Order,
    DataTimestamp,
    DataStatus,
    DataIdentifier,
):
    pass


T = TypeVar("T")


class BloodTypeMixin(BaseModel, Generic[T]):
    blood_type: T = Field(..., description="Blood Type")


class SimpleBloodType(BloodTypeMixin[BloodType]):
    pass


class OptionalSimpleBloodType(BloodTypeMixin[Optional[BloodType]]):
    pass


class ListOfSimpleBloodTypes(BloodTypeMixin[List[BloodType]]):
    pass


class ListOfOptionalSimpleBloodTypes(BloodTypeMixin[Optional[List[BloodType]]]):
    pass


class ExpandedBloodType(BloodTypeMixin[BloodTypeDataSchema]):
    pass


class OptionalExpandedBloodType(BloodTypeMixin[Optional[BloodTypeDataSchema]]):
    pass


class ListOfExpandedBloodTypes(BloodTypeMixin[List[BloodTypeDataSchema]]):
    pass


class ListOfOptionalExpandedBloodTypes(
    BloodTypeMixin[Optional[List[BloodTypeDataSchema]]]
):
    pass
