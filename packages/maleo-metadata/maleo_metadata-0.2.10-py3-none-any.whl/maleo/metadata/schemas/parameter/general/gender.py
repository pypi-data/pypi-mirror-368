from maleo.soma.schemas.parameter.general import ReadSingleParameterSchema
from maleo.metadata.enums.gender import IdentifierType
from maleo.metadata.types.base.gender import IdentifierValueType


class ReadSingleParameter(
    ReadSingleParameterSchema[IdentifierType, IdentifierValueType]
):
    pass
