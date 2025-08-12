from maleo.soma.schemas.parameter.general import ReadSingleParameterSchema
from maleo.metadata.enums.organization_type import IdentifierType
from maleo.metadata.types.base.organization_type import IdentifierValueType


class ReadSingleParameter(
    ReadSingleParameterSchema[IdentifierType, IdentifierValueType]
):
    pass
