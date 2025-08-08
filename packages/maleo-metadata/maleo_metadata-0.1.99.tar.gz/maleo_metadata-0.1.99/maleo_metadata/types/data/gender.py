from typing import List, Optional
from maleo_metadata.enums.gender import Gender
from maleo_metadata.schemas.data.gender import GenderDataSchema


# Simple gender
type SimpleGender = Gender
type OptionalSimpleGender = Optional[SimpleGender]
type ListOfSimpleGenders = List[SimpleGender]
type OptionalListOfSimpleGenders = Optional[List[SimpleGender]]

# Expanded gender
type ExpandedGender = GenderDataSchema
type OptionalExpandedGender = Optional[ExpandedGender]
type ListOfExpandedGenders = List[ExpandedGender]
type OptionalListOfExpandedGenders = Optional[List[ExpandedGender]]
