import json
from copy import copy
from datetime import datetime, timezone
from redis.asyncio.client import Redis
from typing import Dict, List, Optional
from uuid import UUID
from maleo_soma.dtos.configurations.cache.redis import RedisCacheNamespaces
from maleo_soma.enums.environment import Environment
from maleo_soma.enums.expiration import Expiration
from maleo_soma.enums.logging import LogLevel
from maleo_soma.enums.operation import OperationTarget
from maleo_soma.exceptions import NotImplemented as MaleoNotImplemented
from maleo_soma.managers.client.maleo import MaleoClientService
from maleo_soma.schemas.authentication import Authentication
from maleo_soma.schemas.authorization import Authorization
from maleo_soma.schemas.data import DataPair
from maleo_soma.schemas.operation.context import (
    OperationContextSchema,
    OperationOriginSchema,
    OperationLayerSchema,
    OperationTargetSchema,
)
from maleo_soma.schemas.operation.resource import (
    ReadSingleResourceOperationSchema,
    ReadMultipleResourceOperationSchema,
)
from maleo_soma.schemas.operation.resource.action import ReadResourceOperationAction
from maleo_soma.schemas.operation.resource.result import (
    ReadSingleResourceOperationResult,
    ReadMultipleResourceOperationResult,
)
from maleo_soma.schemas.operation.timestamp import OperationTimestamp
from maleo_soma.schemas.pagination import StrictPagination
from maleo_soma.schemas.request import RequestContext
from maleo_soma.schemas.response import (
    SingleDataResponseSchema,
    MultipleDataResponseSchema,
)
from maleo_soma.schemas.service import ServiceContext
from maleo_soma.utils.cache import build_key
from maleo_soma.utils.logging import ClientLogger
from maleo_metadata.client.controllers import MaleoMetadataServiceControllers
from maleo_metadata.enums.general import ClientControllerType
from maleo_metadata.constants.service import RESOURCE
from maleo_metadata.schemas.data.service import ServiceDataSchema
from maleo_metadata.schemas.parameter.client.service import ReadMultipleParameter
from maleo_metadata.schemas.parameter.general.service import ReadSingleParameter


class MaleoMetadataServiceClientService(MaleoClientService):
    _resource = RESOURCE

    def __init__(
        self,
        environment: Environment,
        key: str,
        service_context: ServiceContext,
        operation_origin: OperationOriginSchema,
        logger: ClientLogger,
        redis: Redis,
        redis_namespaces: RedisCacheNamespaces,
        controllers: MaleoMetadataServiceControllers,
    ):
        super().__init__(
            environment,
            key,
            service_context,
            operation_origin,
            logger,
            redis,
            redis_namespaces,
        )
        self._controllers = controllers
        self._namespace = self._redis_namespaces.create(
            self._key,
            self._resource.aggregate(),
            origin=self._CACHE_ORIGIN,
            layer=self._CACHE_LAYER,
        )
        self._default_operation_context = OperationContextSchema(
            origin=self._operation_origin,
            layer=OperationLayerSchema(type=self._OPERATION_LAYER_TYPE, details=None),
            target=OperationTargetSchema(
                type=self._OPERATION_TARGET_TYPE, details=None
            ),
        )

    async def read_services(
        self,
        operation_id: UUID,
        request_context: RequestContext,
        authentication: Authentication,
        parameters: ReadMultipleParameter,
        controller_type: ClientControllerType = ClientControllerType.HTTP,
        authorization: Optional[Authorization] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> ReadMultipleResourceOperationResult[ServiceDataSchema, StrictPagination, None]:
        """Retrieve services from MaleoMetadata"""
        operation_context = copy(self._default_operation_context)
        operation_action = ReadResourceOperationAction()
        executed_at = datetime.now(tz=timezone.utc)

        operation_context.target.type = OperationTarget.CACHE

        # Get function identifier
        func = self.__class__
        module, qualname = func.__module__, func.__qualname__

        # Define arguments being used in this function
        positional_arguments = []
        keyword_arguments = {
            "authentication": authentication.model_dump(
                mode="json",
                exclude={
                    "credentials": {
                        "token": {
                            "payload": {
                                "iat_dt",
                                "iat",
                                "exp_dt",
                                "exp",
                            }
                        }
                    }
                },
            ),
            "parameters": parameters.model_dump(mode="json"),
        }

        # Define full function string
        function = f"{qualname}({json.dumps(positional_arguments)}|{json.dumps(keyword_arguments)})"

        # Define full cache cache_key
        cache_key = build_key(module, function, namespace=self._namespace)

        # Check redis for data
        result_str = await self._redis.get(cache_key)

        if result_str is not None:
            completed_at = datetime.now(tz=timezone.utc)
            result = ReadMultipleResourceOperationResult[
                ServiceDataSchema, StrictPagination, None
            ].model_validate(json.loads(result_str))
            ReadMultipleResourceOperationSchema[
                ServiceDataSchema, StrictPagination, None
            ](
                service_context=self._service_context,
                id=operation_id,
                context=operation_context,
                timestamp=OperationTimestamp(
                    executed_at=executed_at,
                    completed_at=completed_at,
                    duration=(completed_at - executed_at).total_seconds(),
                ),
                summary="Successfully retrieved multiple services",
                request_context=request_context,
                authentication=authentication,
                action=operation_action,
                resource=self._resource,
                result=result,
            ).log(
                self._logger, level=LogLevel.INFO
            )
            return result

        operation_context.target.type = OperationTarget.CONTROLLER

        # Retrieve services using chosen controller
        if controller_type is ClientControllerType.HTTP:
            response = await self._controllers.http.read_services(
                operation_id=operation_id,
                authentication=authentication,
                parameters=parameters,
                authorization=authorization,
                headers=headers,
            )
            if response.is_success:
                completed_at = datetime.now(tz=timezone.utc)
                validated_response = MultipleDataResponseSchema[
                    ServiceDataSchema, StrictPagination, None
                ].model_validate(response.json())
                data = DataPair[List[ServiceDataSchema], None](
                    old=validated_response.data,
                    new=None,
                )
                result = ReadMultipleResourceOperationResult[
                    ServiceDataSchema, StrictPagination, None
                ](
                    data=data,
                    pagination=validated_response.pagination,
                    metadata=None,
                    other=None,
                )
                ReadMultipleResourceOperationSchema[
                    ServiceDataSchema, StrictPagination, None
                ](
                    service_context=self._service_context,
                    id=operation_id,
                    context=operation_context,
                    timestamp=OperationTimestamp(
                        executed_at=executed_at,
                        completed_at=completed_at,
                        duration=(completed_at - executed_at).total_seconds(),
                    ),
                    summary="Successfully retrieved multiple services",
                    request_context=request_context,
                    authentication=authentication,
                    action=operation_action,
                    resource=self._resource,
                    result=result,
                ).log(
                    self._logger, level=LogLevel.INFO
                )
                await self._redis.set(
                    cache_key, result.model_dump_json(), Expiration.EXP_1WK
                )
                return result

            self._raise_resource_http_request_error(
                response=response,
                operation_id=operation_id,
                operation_context=operation_context,
                executed_at=executed_at,
                operation_action=operation_action,
                request_context=request_context,
                authentication=authentication,
                resource=self._resource,
            )
        else:
            completed_at = datetime.now(tz=timezone.utc)
            error = MaleoNotImplemented(
                service_context=self._service_context,
                operation_id=operation_id,
                operation_context=operation_context,
                operation_timestamp=OperationTimestamp(
                    executed_at=executed_at,
                    completed_at=completed_at,
                    duration=(completed_at - executed_at).total_seconds(),
                ),
                operation_summary=f"The provided controller type '{controller_type}' did not exists",
                operation_action=operation_action,
                request_context=request_context,
                authentication=authentication,
                resource=self._resource,
            )
            error.operation_schema.log(self._logger, LogLevel.CRITICAL)
            raise error

    async def read_service(
        self,
        operation_id: UUID,
        request_context: RequestContext,
        authentication: Authentication,
        parameters: ReadSingleParameter,
        controller_type: ClientControllerType = ClientControllerType.HTTP,
        authorization: Optional[Authorization] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> ReadSingleResourceOperationResult[ServiceDataSchema, None]:
        """Retrieve service from MaleoMetadata"""

        operation_context = copy(self._default_operation_context)
        operation_action = ReadResourceOperationAction()
        executed_at = datetime.now(tz=timezone.utc)

        operation_context.target.type = OperationTarget.CACHE

        # Get function identifier
        func = self.__class__
        module, qualname = func.__module__, func.__qualname__

        # Define arguments being used in this function
        positional_arguments = []
        keyword_arguments = {
            "authentication": authentication.model_dump(
                mode="json",
                exclude={
                    "credentials": {
                        "token": {
                            "payload": {
                                "iat_dt",
                                "iat",
                                "exp_dt",
                                "exp",
                            }
                        }
                    }
                },
            ),
            "parameters": parameters.model_dump(mode="json"),
        }

        # Define full function string
        function = f"{qualname}({json.dumps(positional_arguments)}|{json.dumps(keyword_arguments)})"

        # Define full cache cache_key
        cache_key = build_key(module, function, namespace=self._namespace)

        # Check redis for data
        result_str = await self._redis.get(cache_key)

        if result_str is not None:
            completed_at = datetime.now(tz=timezone.utc)
            result = ReadSingleResourceOperationResult[
                ServiceDataSchema, None
            ].model_validate(json.loads(result_str))
            ReadSingleResourceOperationSchema[ServiceDataSchema, None](
                service_context=self._service_context,
                id=operation_id,
                context=operation_context,
                timestamp=OperationTimestamp(
                    executed_at=executed_at,
                    completed_at=completed_at,
                    duration=(completed_at - executed_at).total_seconds(),
                ),
                summary="Successfully retrieved single service",
                request_context=request_context,
                authentication=authentication,
                action=operation_action,
                resource=self._resource,
                result=result,
            ).log(self._logger, level=LogLevel.INFO)
            return result

        operation_context.target.type = OperationTarget.CONTROLLER

        # Retrieve services using chosen controller
        if controller_type is ClientControllerType.HTTP:
            response = await self._controllers.http.read_service(
                operation_id=operation_id,
                authentication=authentication,
                parameters=parameters,
                authorization=authorization,
                headers=headers,
            )
            if response.is_success:
                completed_at = datetime.now(tz=timezone.utc)
                validated_response = SingleDataResponseSchema[
                    ServiceDataSchema, None
                ].model_validate(response.json())
                data = DataPair[ServiceDataSchema, None](
                    old=validated_response.data,
                    new=None,
                )
                result = ReadSingleResourceOperationResult[ServiceDataSchema, None](
                    data=data,
                    pagination=validated_response.pagination,
                    metadata=None,
                    other=None,
                )
                ReadSingleResourceOperationSchema[ServiceDataSchema, None](
                    service_context=self._service_context,
                    id=operation_id,
                    context=operation_context,
                    timestamp=OperationTimestamp(
                        executed_at=executed_at,
                        completed_at=completed_at,
                        duration=(completed_at - executed_at).total_seconds(),
                    ),
                    summary="Successfully retrieved single services",
                    request_context=request_context,
                    authentication=authentication,
                    action=operation_action,
                    resource=self._resource,
                    result=result,
                ).log(self._logger, level=LogLevel.INFO)
                await self._redis.set(
                    cache_key, result.model_dump_json(), Expiration.EXP_1WK
                )
                return result

            self._raise_resource_http_request_error(
                response=response,
                operation_id=operation_id,
                operation_context=operation_context,
                executed_at=executed_at,
                operation_action=operation_action,
                request_context=request_context,
                authentication=authentication,
                resource=self._resource,
            )
        else:
            completed_at = datetime.now(tz=timezone.utc)
            error = MaleoNotImplemented(
                service_context=self._service_context,
                operation_id=operation_id,
                operation_context=operation_context,
                operation_timestamp=OperationTimestamp(
                    executed_at=executed_at,
                    completed_at=completed_at,
                    duration=(completed_at - executed_at).total_seconds(),
                ),
                operation_summary=f"The provided controller type '{controller_type}' did not exists",
                operation_action=operation_action,
                request_context=request_context,
                resource=self._resource,
                authentication=authentication,
            )
            error.operation_schema.log(self._logger, LogLevel.CRITICAL)
            raise error
