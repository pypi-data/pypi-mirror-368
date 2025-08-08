from httpx import Response
from typing import Dict, Optional
from uuid import UUID
from maleo_soma.managers.client.base import BearerAuth
from maleo_soma.managers.client.maleo import MaleoClientHTTPController
from maleo_soma.schemas.authentication import Authentication
from maleo_soma.schemas.authorization import Authorization
from maleo_soma.schemas.parameter.general import ReadSingleQueryParameterSchema
from maleo_soma.utils.merger import merge_dicts
from maleo_soma.utils.token import reencode
from maleo_metadata.schemas.parameter.general.medical_role import (
    ReadSingleParameter,
)
from maleo_metadata.schemas.parameter.client.medical_role import (
    ReadMultipleParameter,
    ReadMultipleRootSpecializationsParameter,
    ReadMultipleSpecializationsParameter,
    ReadMultipleQueryParameter,
    ReadMultipleSpecializationsQueryParameter,
)


class MaleoMetadataMedicalRoleHTTPController(MaleoClientHTTPController):
    async def read_medical_roles(
        self,
        operation_id: UUID,
        authentication: Authentication,
        parameters: ReadMultipleParameter,
        authorization: Optional[Authorization] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Response:
        """Fetch medical roles from MaleoMetadata"""
        async with self._manager.get_client() as client:
            # Define URL
            url = f"{self._manager.url}/v1/medical-roles/"

            # Parse parameters to query params
            params = ReadMultipleQueryParameter.model_validate(
                parameters.model_dump()
            ).model_dump(exclude={"sort_columns", "date_filters"}, exclude_none=True)

            # Create headers
            base_headers = {
                "Content-Type": "application/json",
                "X-Operation_Id": str(operation_id),
            }
            if headers is not None:
                headers = merge_dicts(base_headers, headers)
            else:
                headers = base_headers

            # Create auth
            token = None
            if authentication.credentials.token is not None:
                try:
                    token = reencode(
                        payload=authentication.credentials.token.payload,
                        key=self._private_key,
                    )
                except Exception:
                    pass

            if (
                token is None
                and authorization is not None
                and authorization.scheme == "Bearer"
            ):
                token = authorization.credentials

            if token is None:
                token = self._credential_manager.token

            auth = BearerAuth(token) if token is not None else None

            # Send request and wait for response
            return await client.get(url=url, params=params, headers=headers, auth=auth)

    async def read_medical_roles_specializations(
        self,
        operation_id: UUID,
        authentication: Authentication,
        parameters: ReadMultipleRootSpecializationsParameter,
        authorization: Optional[Authorization] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Response:
        """Fetch medical roles specializations from MaleoMetadata"""
        async with self._manager.get_client() as client:
            # Define URL
            url = f"{self._manager.url}/v1/medical-roles/specializations"

            # Parse parameters to query params
            params = ReadMultipleSpecializationsQueryParameter.model_validate(
                parameters.model_dump()
            ).model_dump(exclude={"sort_columns", "date_filters"}, exclude_none=True)

            # Create headers
            base_headers = {
                "Content-Type": "application/json",
                "X-Operation_Id": str(operation_id),
            }
            if headers is not None:
                headers = merge_dicts(base_headers, headers)
            else:
                headers = base_headers

            # Create auth
            token = None
            if authentication.credentials.token is not None:
                try:
                    token = reencode(
                        payload=authentication.credentials.token.payload,
                        key=self._private_key,
                    )
                except Exception:
                    pass

            if (
                token is None
                and authorization is not None
                and authorization.scheme == "Bearer"
            ):
                token = authorization.credentials

            if token is None:
                token = self._credential_manager.token

            auth = BearerAuth(token) if token is not None else None

            # Send request and wait for response
            response = await client.get(
                url=url, params=params, headers=headers, auth=auth
            )
            return Response(response=response)  #  type: ignore

    async def read_medical_role(
        self,
        operation_id: UUID,
        authentication: Authentication,
        parameters: ReadSingleParameter,
        authorization: Optional[Authorization] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Response:
        """Fetch medical role from MaleoMetadata"""
        async with self._manager.get_client() as client:
            # Define URL
            url = f"{self._manager.url}/v1/medical-roles/{parameters.identifier}/{parameters.value}"

            # Parse parameters to query params
            params = ReadSingleQueryParameterSchema.model_validate(
                parameters.model_dump()
            ).model_dump(exclude_none=True)

            # Create headers
            base_headers = {
                "Content-Type": "application/json",
                "X-Operation_Id": str(operation_id),
            }
            if headers is not None:
                headers = merge_dicts(base_headers, headers)
            else:
                headers = base_headers

            # Create auth
            token = None
            if authentication.credentials.token is not None:
                try:
                    token = reencode(
                        payload=authentication.credentials.token.payload,
                        key=self._private_key,
                    )
                except Exception:
                    pass

            if (
                token is None
                and authorization is not None
                and authorization.scheme == "Bearer"
            ):
                token = authorization.credentials

            if token is None:
                token = self._credential_manager.token

            auth = BearerAuth(token) if token is not None else None

            # Send request and wait for response
            return await client.get(url=url, params=params, headers=headers, auth=auth)

    async def read_medical_role_specializations(
        self,
        operation_id: UUID,
        authentication: Authentication,
        parameters: ReadMultipleSpecializationsParameter,
        authorization: Optional[Authorization] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Response:
        """Fetch medical role's specializations from MaleoMetadata"""
        async with self._manager.get_client() as client:
            # Define URL
            url = f"{self._manager.url}/v1/medical-roles/{parameters.medical_role_id}/specializations"

            # Parse parameters to query params
            params = ReadMultipleSpecializationsQueryParameter.model_validate(
                parameters.model_dump()
            ).model_dump(exclude_none=True)

            # Create headers
            base_headers = {
                "Content-Type": "application/json",
                "X-Operation_Id": str(operation_id),
            }
            if headers is not None:
                headers = merge_dicts(base_headers, headers)
            else:
                headers = base_headers

            # Create auth
            token = None
            if authentication.credentials.token is not None:
                try:
                    token = reencode(
                        payload=authentication.credentials.token.payload,
                        key=self._private_key,
                    )
                except Exception:
                    pass

            if (
                token is None
                and authorization is not None
                and authorization.scheme == "Bearer"
            ):
                token = authorization.credentials

            if token is None:
                token = self._credential_manager.token

            auth = BearerAuth(token) if token is not None else None

            # Send request and wait for response
            return await client.get(url=url, params=params, headers=headers, auth=auth)
