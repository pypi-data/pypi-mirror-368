from pydantic import BaseModel
from maleo_soma.mixins.general import IsRoot, IsParent, IsChild, IsLeaf
from maleo_soma.mixins.parameter import (
    OptionalListOfIds,
    OptionalListOfParentIds,
    OptionalListOfUuids,
    OptionalListOfCodes,
    OptionalListOfKeys,
    OptionalListOfNames,
)
from maleo_soma.schemas.parameter.client import (
    ReadPaginatedMultipleParameterSchema,
    ReadPaginatedMultipleQueryParameterSchema,
)
from maleo_metadata.mixins.medical_role import MedicalRoleId


class ReadMultipleParameter(
    ReadPaginatedMultipleParameterSchema,
    OptionalListOfNames,
    OptionalListOfKeys,
    OptionalListOfCodes,
    IsLeaf,
    IsChild,
    IsParent,
    IsRoot,
    OptionalListOfParentIds,
    OptionalListOfUuids,
    OptionalListOfIds,
    BaseModel,
):
    pass


class ReadMultipleRootSpecializationsParameter(
    ReadPaginatedMultipleParameterSchema,
    OptionalListOfNames,
    OptionalListOfKeys,
    OptionalListOfCodes,
    OptionalListOfUuids,
    OptionalListOfIds,
    BaseModel,
):
    pass


class ReadMultipleSpecializationsParameter(
    ReadMultipleRootSpecializationsParameter,
    MedicalRoleId,
    BaseModel,
):
    pass


class ReadMultipleQueryParameter(
    ReadPaginatedMultipleQueryParameterSchema,
    OptionalListOfNames,
    OptionalListOfKeys,
    OptionalListOfCodes,
    IsLeaf,
    IsChild,
    IsParent,
    IsRoot,
    OptionalListOfParentIds,
    OptionalListOfUuids,
    OptionalListOfIds,
    BaseModel,
):
    pass


class ReadMultipleSpecializationsQueryParameter(
    ReadPaginatedMultipleQueryParameterSchema,
    OptionalListOfNames,
    OptionalListOfKeys,
    OptionalListOfCodes,
    OptionalListOfUuids,
    OptionalListOfIds,
    BaseModel,
):
    pass
