from Crypto.PublicKey.RSA import RsaKey
from redis.asyncio.client import Redis
from typing import Optional
from maleo_soma.dtos.configurations.cache.redis import RedisCacheNamespaces
from maleo_soma.dtos.configurations.client.maleo import MaleoClientConfigurationDTO
from maleo_soma.managers.client.maleo import MaleoClientManager
from maleo_soma.managers.credential import CredentialManager
from maleo_soma.schemas.service import ServiceContext
from maleo_soma.utils.logging import SimpleConfig
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
from maleo_metadata.client.controllers import (
    MaleoMetadataBloodTypeControllers,
    MaleoMetadataGenderControllers,
    MaleoMetadataMedicalRoleControllers,
    MaleoMetadataOrganizationTypeControllers,
    MaleoMetadataServiceControllers,
    MaleoMetadataSystemRoleControllers,
    MaleoMetadataUserTypeControllers,
    MaleoMetadataControllers,
)
from maleo_metadata.client.services import (
    MaleoMetadataBloodTypeClientService,
    MaleoMetadataGenderClientService,
    MaleoMetadataMedicalRoleClientService,
    MaleoMetadataOrganizationTypeClientService,
    MaleoMetadataServiceClientService,
    MaleoMetadataSystemRoleClientService,
    MaleoMetadataUserTypeClientService,
    MaleoMetadataServices,
)


class MaleoMetadataClientManager(MaleoClientManager):
    def __init__(
        self,
        configurations: MaleoClientConfigurationDTO,
        log_config: SimpleConfig,
        credential_manager: CredentialManager,
        private_key: RsaKey,
        redis: Redis,
        redis_namespaces: RedisCacheNamespaces,
        service_context: Optional[ServiceContext] = None,
    ):
        assert configurations.key == "maleo-metadata"
        assert configurations.name == "MaleoMetadata"
        super().__init__(
            configurations,
            log_config,
            credential_manager,
            private_key,
            redis,
            redis_namespaces,
            service_context,
        )
        self._initialize_controllers()
        self._initialize_services()
        self._logger.info("Client manager initialized successfully")

    def _initialize_controllers(self):
        super()._initialize_controllers()
        # Blood type controllers
        blood_type_http_controller = MaleoMetadataBloodTypeHTTPController(
            manager=self._controller_managers.http,
            credential_manager=self._credential_manager,
            private_key=self._private_key,
        )
        blood_type_controllers = MaleoMetadataBloodTypeControllers(
            http=blood_type_http_controller
        )
        # Gender controllers
        gender_http_controller = MaleoMetadataGenderHTTPController(
            manager=self._controller_managers.http,
            credential_manager=self._credential_manager,
            private_key=self._private_key,
        )
        gender_controllers = MaleoMetadataGenderControllers(http=gender_http_controller)
        # Medical role controllers
        medical_role_http_controller = MaleoMetadataMedicalRoleHTTPController(
            manager=self._controller_managers.http,
            credential_manager=self._credential_manager,
            private_key=self._private_key,
        )
        medical_role_controllers = MaleoMetadataMedicalRoleControllers(
            http=medical_role_http_controller
        )
        # Organization type controllers
        organization_type_http_controller = MaleoMetadataOrganizationTypeHTTPController(
            manager=self._controller_managers.http,
            credential_manager=self._credential_manager,
            private_key=self._private_key,
        )
        organization_type_controllers = MaleoMetadataOrganizationTypeControllers(
            http=organization_type_http_controller
        )
        # Service controllers
        service_http_controller = MaleoMetadataServiceHTTPController(
            manager=self._controller_managers.http,
            credential_manager=self._credential_manager,
            private_key=self._private_key,
        )
        service_controllers = MaleoMetadataServiceControllers(
            http=service_http_controller
        )
        # System role controllers
        system_role_http_controller = MaleoMetadataSystemRoleHTTPController(
            manager=self._controller_managers.http,
            credential_manager=self._credential_manager,
            private_key=self._private_key,
        )
        system_role_controllers = MaleoMetadataSystemRoleControllers(
            http=system_role_http_controller
        )
        # User type controllers
        user_type_http_controller = MaleoMetadataUserTypeHTTPController(
            manager=self._controller_managers.http,
            credential_manager=self._credential_manager,
            private_key=self._private_key,
        )
        user_type_controllers = MaleoMetadataUserTypeControllers(
            http=user_type_http_controller
        )
        # All controllers
        self._controllers = MaleoMetadataControllers(
            blood_type=blood_type_controllers,
            gender=gender_controllers,
            medical_role=medical_role_controllers,
            organization_type=organization_type_controllers,
            service=service_controllers,
            system_role=system_role_controllers,
            user_type=user_type_controllers,
        )

    @property
    def controllers(self) -> MaleoMetadataControllers:
        return self._controllers

    def _initialize_services(self):
        super()._initialize_services()
        blood_type_service = MaleoMetadataBloodTypeClientService(
            environment=self._environment,
            key=self._key,
            service_context=self._service_context,
            operation_origin=self._operation_origin,
            logger=self._logger,
            redis=self._redis,
            redis_namespaces=self._redis_namespaces,
            controllers=self._controllers.blood_type,
        )
        gender_service = MaleoMetadataGenderClientService(
            environment=self._environment,
            key=self._key,
            service_context=self._service_context,
            operation_origin=self._operation_origin,
            logger=self._logger,
            redis=self._redis,
            redis_namespaces=self._redis_namespaces,
            controllers=self._controllers.gender,
        )
        medical_role = MaleoMetadataMedicalRoleClientService(
            environment=self._environment,
            key=self._key,
            service_context=self._service_context,
            operation_origin=self._operation_origin,
            logger=self._logger,
            redis=self._redis,
            redis_namespaces=self._redis_namespaces,
            controllers=self._controllers.medical_role,
        )
        organization_type_service = MaleoMetadataOrganizationTypeClientService(
            environment=self._environment,
            key=self._key,
            service_context=self._service_context,
            operation_origin=self._operation_origin,
            logger=self._logger,
            redis=self._redis,
            redis_namespaces=self._redis_namespaces,
            controllers=self._controllers.organization_type,
        )
        service_service = MaleoMetadataServiceClientService(
            environment=self._environment,
            key=self._key,
            service_context=self._service_context,
            operation_origin=self._operation_origin,
            logger=self._logger,
            redis=self._redis,
            redis_namespaces=self._redis_namespaces,
            controllers=self._controllers.service,
        )
        system_role_service = MaleoMetadataSystemRoleClientService(
            environment=self._environment,
            key=self._key,
            service_context=self._service_context,
            operation_origin=self._operation_origin,
            logger=self._logger,
            redis=self._redis,
            redis_namespaces=self._redis_namespaces,
            controllers=self._controllers.system_role,
        )
        user_type_service = MaleoMetadataUserTypeClientService(
            environment=self._environment,
            key=self._key,
            service_context=self._service_context,
            operation_origin=self._operation_origin,
            logger=self._logger,
            redis=self._redis,
            redis_namespaces=self._redis_namespaces,
            controllers=self._controllers.user_type,
        )
        self._services = MaleoMetadataServices(
            blood_type=blood_type_service,
            gender=gender_service,
            medical_role=medical_role,
            organization_type=organization_type_service,
            service=service_service,
            system_role=system_role_service,
            user_type=user_type_service,
        )

    @property
    def services(self) -> MaleoMetadataServices:
        return self._services
