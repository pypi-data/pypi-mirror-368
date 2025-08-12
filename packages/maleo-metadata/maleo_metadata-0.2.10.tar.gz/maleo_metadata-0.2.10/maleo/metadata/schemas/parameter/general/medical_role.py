from maleo.soma.schemas.parameter.general import ReadSingleParameterSchema
from maleo.metadata.enums.medical_role import IdentifierType
from maleo.metadata.types.base.medical_role import IdentifierValueType


class ReadSingleParameter(
    ReadSingleParameterSchema[IdentifierType, IdentifierValueType]
):
    pass
