from maleo_soma.schemas.parameter.general import ReadSingleParameterSchema
from maleo_metadata.enums.gender import IdentifierType
from maleo_metadata.types.base.gender import IdentifierValueType


class ReadSingleParameter(
    ReadSingleParameterSchema[IdentifierType, IdentifierValueType]
):
    pass
