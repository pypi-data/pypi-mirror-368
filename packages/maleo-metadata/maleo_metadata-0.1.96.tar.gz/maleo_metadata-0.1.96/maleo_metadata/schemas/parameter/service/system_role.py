from pydantic import BaseModel
from maleo_soma.mixins.parameter import (
    OptionalListOfIds,
    OptionalListOfUuids,
    OptionalListOfKeys,
    OptionalListOfNames,
)
from maleo_soma.schemas.parameter.service import (
    ReadUnpaginatedMultipleQueryParameterSchema,
    ReadUnpaginatedMultipleParameterSchema,
)


class ReadMultipleQueryParameter(
    ReadUnpaginatedMultipleQueryParameterSchema,
    OptionalListOfNames,
    OptionalListOfKeys,
    OptionalListOfUuids,
    OptionalListOfIds,
    BaseModel,
):
    pass


class ReadMultipleParameter(
    ReadUnpaginatedMultipleParameterSchema,
    OptionalListOfNames,
    OptionalListOfKeys,
    OptionalListOfUuids,
    OptionalListOfIds,
    BaseModel,
):
    pass
