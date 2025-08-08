from typing import List, Optional
from maleo_metadata.enums.user_type import UserType
from maleo_metadata.schemas.data.user_type import UserTypeDataSchema


# Simple user type
type SimpleUserType = UserType
type OptionalSimpleUserType = Optional[SimpleUserType]
type ListOfSimpleUserTypes = List[SimpleUserType]
type OptionalListOfSimpleUserTypes = Optional[List[SimpleUserType]]

# Expanded user type
type ExpandedUserType = UserTypeDataSchema
type OptionalExpandedUserType = Optional[ExpandedUserType]
type ListOfExpandedUserTypes = List[ExpandedUserType]
type OptionalListOfExpandedUserTypes = Optional[List[ExpandedUserType]]
