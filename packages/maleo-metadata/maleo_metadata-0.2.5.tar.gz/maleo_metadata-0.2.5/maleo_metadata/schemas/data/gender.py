from pydantic import BaseModel, Field
from typing import List, Optional
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


class SimpleGender(BaseModel):
    gender: Gender = Field(..., description="Single Gender")


class OptionalSimpleGender(BaseModel):
    gender: Optional[Gender] = Field(None, description="Single Gender. (Optional)")


class ListOfSimpleGenders(BaseModel):
    genders: List[Gender] = Field(..., description="Multiple Genders")


class OptionalListOfSimpleGenders(BaseModel):
    genders: Optional[List[Gender]] = Field(
        None, description="Multiple Genders. (Optional)"
    )


class ExpandedGender(BaseModel):
    gender: GenderDataSchema = Field(..., description="Single Gender Data")


class OptionalExpandedGender(BaseModel):
    gender: Optional[GenderDataSchema] = Field(
        None, description="Single Gender Data. (Optional)"
    )


class ListOfExpandedGenders(BaseModel):
    genders: List[GenderDataSchema] = Field(..., description="Multiple Genders Data")


class OptionalListOfExpandedGenders(BaseModel):
    genders: Optional[List[GenderDataSchema]] = Field(
        None, description="Multiple Genders Data. (Optional)"
    )
