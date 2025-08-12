from maleo.soma.schemas.parameter.general import ReadSingleParameterSchema
from maleo.metadata.enums.blood_type import IdentifierType
from maleo.metadata.types.base.blood_type import IdentifierValueType


class ReadSingleParameter(
    ReadSingleParameterSchema[IdentifierType, IdentifierValueType]
):
    pass
