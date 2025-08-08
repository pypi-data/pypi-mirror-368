from typing import List, Optional
from maleo_metadata.enums.blood_type import BloodType
from maleo_metadata.schemas.data.blood_type import BloodTypeDataSchema


# Simple blood type
type SimpleBloodType = BloodType
type OptionalSimpleBloodType = Optional[SimpleBloodType]
type ListOfSimpleBloodTypes = List[SimpleBloodType]
type OptionalListOfSimpleBloodTypes = Optional[List[SimpleBloodType]]

# Expanded blood type
type ExpandedBloodType = BloodTypeDataSchema
type OptionalExpandedBloodType = Optional[ExpandedBloodType]
type ListOfExpandedBloodTypes = List[ExpandedBloodType]
type OptionalListOfExpandedBloodTypes = Optional[List[ExpandedBloodType]]
