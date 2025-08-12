from maleo.soma.schemas.parameter.general import ReadSingleParameterSchema
from maleo.metadata.enums.system_role import IdentifierType
from maleo.metadata.types.base.system_role import IdentifierValueType


class ReadSingleParameter(
    ReadSingleParameterSchema[IdentifierType, IdentifierValueType]
):
    pass
