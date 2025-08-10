from pydantic import BaseModel, Field
from typing import List, Optional
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


class SimpleBloodType(BaseModel):
    blood_type: BloodType = Field(..., description="Single Blood Type")


class OptionalSimpleBloodType(BaseModel):
    blood_type: Optional[BloodType] = Field(
        None, description="Single Blood Type. (Optional)"
    )


class ListOfSimpleBloodTypes(BaseModel):
    blood_types: List[BloodType] = Field(..., description="Multiple Blood Types")


class OptionalListOfSimpleBloodTypes(BaseModel):
    blood_types: Optional[List[BloodType]] = Field(
        None, description="Multiple Blood Types. (Optional)"
    )


class ExpandedBloodType(BaseModel):
    blood_type: BloodTypeDataSchema = Field(..., description="Single Blood Type Data")


class OptionalExpandedBloodType(BaseModel):
    blood_type: Optional[BloodTypeDataSchema] = Field(
        None, description="Single Blood Type Data. (Optional)"
    )


class ListOfExpandedBloodTypes(BaseModel):
    blood_types: List[BloodTypeDataSchema] = Field(
        ..., description="Multiple Blood Types Data"
    )


class OptionalListOfExpandedBloodTypes(BaseModel):
    blood_types: Optional[List[BloodTypeDataSchema]] = Field(
        None, description="Multiple Blood Types Data. (Optional)"
    )
