from maleo.soma.schemas.parameter.general import ReadSingleParameterSchema
from maleo.metadata.enums.user_type import IdentifierType
from maleo.metadata.types.base.user_type import IdentifierValueType


class ReadSingleParameter(
    ReadSingleParameterSchema[IdentifierType, IdentifierValueType]
):
    pass
