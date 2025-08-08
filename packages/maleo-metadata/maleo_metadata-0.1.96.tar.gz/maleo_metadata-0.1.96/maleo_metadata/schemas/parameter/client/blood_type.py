from pydantic import BaseModel
from maleo_soma.mixins.parameter import (
    OptionalListOfIds,
    OptionalListOfUuids,
    OptionalListOfKeys,
    OptionalListOfNames,
)
from maleo_soma.schemas.parameter.client import (
    ReadUnpaginatedMultipleParameterSchema,
    ReadUnpaginatedMultipleQueryParameterSchema,
)


class ReadMultipleParameter(
    ReadUnpaginatedMultipleParameterSchema,
    OptionalListOfNames,
    OptionalListOfKeys,
    OptionalListOfUuids,
    OptionalListOfIds,
    BaseModel,
):
    pass


class ReadMultipleQueryParameter(
    ReadUnpaginatedMultipleQueryParameterSchema,
    OptionalListOfNames,
    OptionalListOfKeys,
    OptionalListOfUuids,
    OptionalListOfIds,
    BaseModel,
):
    pass
