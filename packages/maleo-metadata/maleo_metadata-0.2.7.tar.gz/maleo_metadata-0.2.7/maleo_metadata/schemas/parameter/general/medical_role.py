from maleo_soma.schemas.parameter.general import ReadSingleParameterSchema
from maleo_metadata.enums.medical_role import IdentifierType
from maleo_metadata.types.base.medical_role import IdentifierValueType


class ReadSingleParameter(
    ReadSingleParameterSchema[IdentifierType, IdentifierValueType]
):
    pass
