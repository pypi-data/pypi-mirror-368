from maleo.soma.schemas.parameter.general import ReadSingleParameterSchema
from maleo.metadata.enums.service import IdentifierType
from maleo.metadata.types.base.service import IdentifierValueType


class ReadSingleParameter(
    ReadSingleParameterSchema[IdentifierType, IdentifierValueType]
):
    pass
