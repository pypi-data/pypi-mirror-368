from pydantic import BaseModel, Field
from typing import Generic, List, Optional, TypeVar
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


T = TypeVar("T")


class UserTypeMixin(BaseModel, Generic[T]):
    organization_type: T = Field(..., description="User Type")


class SimpleUserType(UserTypeMixin[UserType]):
    pass


class OptionalSimpleUserType(UserTypeMixin[Optional[UserType]]):
    pass


class ListOfSimpleUserTypes(UserTypeMixin[List[UserType]]):
    pass


class ListOfOptionalSimpleUserTypes(UserTypeMixin[Optional[List[UserType]]]):
    pass


class ExpandedUserType(UserTypeMixin[UserTypeDataSchema]):
    pass


class OptionalExpandedUserType(UserTypeMixin[Optional[UserTypeDataSchema]]):
    pass


class ListOfExpandedUserTypes(UserTypeMixin[List[UserTypeDataSchema]]):
    pass


class ListOfOptionalExpandedUserTypes(
    UserTypeMixin[Optional[List[UserTypeDataSchema]]]
):
    pass
