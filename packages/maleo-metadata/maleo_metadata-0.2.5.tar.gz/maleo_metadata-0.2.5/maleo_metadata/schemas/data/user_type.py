from pydantic import BaseModel, Field
from typing import List, Optional
from maleo_soma.mixins.data import DataIdentifier, DataStatus, DataTimestamp
from maleo_soma.mixins.general import Order
from maleo_metadata.enums.user_type import UserType
from maleo_metadata.mixins.user_type import Key, Name


class UserTypeDataSchema(
    Name,
    Key,
    Order,
    DataTimestamp,
    DataStatus,
    DataIdentifier,
):
    pass


class SimpleUserType(BaseModel):
    user_type: UserType = Field(..., description="Single User Type")


class OptionalSimpleUserType(BaseModel):
    user_type: Optional[UserType] = Field(
        None, description="Single User Type. (Optional)"
    )


class ListOfSimpleUserTypes(BaseModel):
    user_types: List[UserType] = Field(..., description="Multiple User Types")


class OptionalListOfSimpleUserTypes(BaseModel):
    user_types: Optional[List[UserType]] = Field(
        None, description="Multiple User Types. (Optional)"
    )


class ExpandedUserType(BaseModel):
    user_type: UserTypeDataSchema = Field(..., description="Single User Type Data")


class OptionalExpandedUserType(BaseModel):
    user_type: Optional[UserTypeDataSchema] = Field(
        None, description="Single User Type Data. (Optional)"
    )


class ListOfExpandedUserTypes(BaseModel):
    user_types: List[UserTypeDataSchema] = Field(
        ..., description="Multiple User Types Data"
    )


class OptionalListOfExpandedUserTypes(BaseModel):
    user_types: Optional[List[UserTypeDataSchema]] = Field(
        None, description="Multiple User Types Data. (Optional)"
    )
