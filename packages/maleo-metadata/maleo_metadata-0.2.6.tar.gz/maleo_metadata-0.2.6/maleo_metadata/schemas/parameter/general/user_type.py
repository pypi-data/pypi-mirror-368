from maleo_soma.schemas.parameter.general import ReadSingleParameterSchema
from maleo_metadata.enums.user_type import IdentifierType
from maleo_metadata.types.base.user_type import IdentifierValueType


class ReadSingleParameter(
    ReadSingleParameterSchema[IdentifierType, IdentifierValueType]
):
    pass
