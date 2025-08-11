from maleo_soma.schemas.parameter.general import ReadSingleParameterSchema
from maleo_metadata.enums.service import IdentifierType
from maleo_metadata.types.base.service import IdentifierValueType


class ReadSingleParameter(
    ReadSingleParameterSchema[IdentifierType, IdentifierValueType]
):
    pass
