from pydantic import Field
from maleo_soma.managers.client.base import (
    ClientServiceControllers,
    ClientControllers,
)

from maleo_metadata.client.controllers.http.blood_type import (
    MaleoMetadataBloodTypeHTTPController,
)

from maleo_metadata.client.controllers.http.gender import (
    MaleoMetadataGenderHTTPController,
)

from maleo_metadata.client.controllers.http.medical_role import (
    MaleoMetadataMedicalRoleHTTPController,
)

from maleo_metadata.client.controllers.http.organization_type import (
    MaleoMetadataOrganizationTypeHTTPController,
)

from maleo_metadata.client.controllers.http.service import (
    MaleoMetadataServiceHTTPController,
)

from maleo_metadata.client.controllers.http.system_role import (
    MaleoMetadataSystemRoleHTTPController,
)

from maleo_metadata.client.controllers.http.user_type import (
    MaleoMetadataUserTypeHTTPController,
)


class MaleoMetadataBloodTypeControllers(ClientServiceControllers):
    http: MaleoMetadataBloodTypeHTTPController = Field(  # type: ignore
        ..., description="Blood type's http controller"
    )


class MaleoMetadataGenderControllers(ClientServiceControllers):
    http: MaleoMetadataGenderHTTPController = Field(  # type: ignore
        ..., description="Gender's http controller"
    )


class MaleoMetadataMedicalRoleControllers(ClientServiceControllers):
    http: MaleoMetadataMedicalRoleHTTPController = Field(  # type: ignore
        ..., description="Medical role's http controller"
    )


class MaleoMetadataOrganizationTypeControllers(ClientServiceControllers):
    http: MaleoMetadataOrganizationTypeHTTPController = Field(  # type: ignore
        ..., description="Organization type's http controller"
    )


class MaleoMetadataServiceControllers(ClientServiceControllers):
    http: MaleoMetadataServiceHTTPController = Field(  # type: ignore
        ..., description="Service's http controller"
    )


class MaleoMetadataSystemRoleControllers(ClientServiceControllers):
    http: MaleoMetadataSystemRoleHTTPController = Field(  # type: ignore
        ..., description="System role's http controller"
    )


class MaleoMetadataUserTypeControllers(ClientServiceControllers):
    http: MaleoMetadataUserTypeHTTPController = Field(  # type: ignore
        ..., description="User type's http controller"
    )


class MaleoMetadataControllers(ClientControllers):
    blood_type: MaleoMetadataBloodTypeControllers = Field(
        ..., description="Blood type's controllers"
    )
    gender: MaleoMetadataGenderControllers = Field(
        ..., description="Gender's controllers"
    )
    medical_role: MaleoMetadataMedicalRoleControllers = Field(
        ..., description="Medical role's controllers"
    )
    organization_type: MaleoMetadataOrganizationTypeControllers = Field(
        ..., description="Organization type's controllers"
    )
    service: MaleoMetadataServiceControllers = Field(
        ..., description="Service's controllers"
    )
    system_role: MaleoMetadataSystemRoleControllers = Field(
        ..., description="System role's controllers"
    )
    user_type: MaleoMetadataUserTypeControllers = Field(
        ..., description="User type's controllers"
    )
