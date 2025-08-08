from typing import List, Optional
from maleo_metadata.enums.gender import Gender
from maleo_metadata.schemas.data.gender import GenderDataSchema


# Simple gender
SimpleGender = Gender
OptionalSimpleGender = Optional[SimpleGender]
ListOfSimpleGenders = List[SimpleGender]
OptionalListOfSimpleGenders = Optional[List[SimpleGender]]

# Expanded gender
ExpandedGender = GenderDataSchema
OptionalExpandedGender = Optional[ExpandedGender]
ListOfExpandedGenders = List[ExpandedGender]
OptionalListOfExpandedGenders = Optional[List[ExpandedGender]]
