from datetime import datetime, timezone
from uuid import UUID
from Crypto.PublicKey.RSA import RsaKey
from httpx import Response
from pydantic import ConfigDict, Field
from redis.asyncio.client import Redis
from typing import Optional
from maleo_soma.dtos.configurations.cache.redis import RedisCacheNamespaces
from maleo_soma.dtos.configurations.client.maleo import MaleoClientConfigurationDTO
from maleo_soma.enums.environment import Environment
from maleo_soma.exceptions import from_resource_http_request
from maleo_soma.managers.client.base import (
    ClientManager,
    ClientHTTPControllerManager,
    ClientControllerManagers,
    ClientHTTPController,
    ClientServiceControllers,
    ClientService,
    ClientControllers,
)
from maleo_soma.managers.credential import CredentialManager
from maleo_soma.schemas.authentication import Authentication
from maleo_soma.schemas.operation.context import (
    OperationContextSchema,
    OperationOriginSchema,
)
from maleo_soma.schemas.operation.resource.action import AllResourceOperationAction
from maleo_soma.schemas.operation.timestamp import OperationTimestamp
from maleo_soma.schemas.request import RequestContext
from maleo_soma.schemas.resource import Resource
from maleo_soma.schemas.service import ServiceContext
from maleo_soma.utils.logging import ClientLogger, SimpleConfig


class MaleoClientHTTPController(ClientHTTPController):
    def __init__(
        self,
        manager: ClientHTTPControllerManager,
        credential_manager: CredentialManager,
        private_key: RsaKey,
    ):
        super().__init__(manager)
        self._credential_manager = credential_manager
        self._private_key = private_key


class MaleoClientServiceControllers(ClientServiceControllers):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    http: MaleoClientHTTPController = Field(  # type: ignore
        ..., description="Maleo's HTTP Client Controller"
    )


class MaleoClientService(ClientService):
    def __init__(
        self,
        environment: Environment,
        key: str,
        service_context: ServiceContext,
        operation_origin: OperationOriginSchema,
        logger: ClientLogger,
        redis: Redis,
        redis_namespaces: RedisCacheNamespaces,
    ):
        super().__init__(service_context, operation_origin, logger)
        self._environment = environment
        self._key = key
        self._redis = redis
        self._redis_namespaces = redis_namespaces

    def _raise_resource_http_request_error(
        self,
        response: Response,
        operation_id: UUID,
        operation_context: OperationContextSchema,
        executed_at: datetime,
        operation_action: AllResourceOperationAction,
        request_context: Optional[RequestContext],
        authentication: Optional[Authentication],
        resource: Resource,
    ):
        """Handle HTTP error response and raise appropriate exception"""

        completed_at = datetime.now(tz=timezone.utc)
        timestamp = OperationTimestamp(
            executed_at=executed_at,
            completed_at=completed_at,
            duration=(completed_at - executed_at).total_seconds(),
        )

        error = from_resource_http_request(
            status_code=response.status_code,
            service_context=self._service_context,
            operation_id=operation_id,
            operation_context=operation_context,
            operation_timestamp=timestamp,
            operation_action=operation_action,
            request_context=request_context,
            authentication=authentication,
            resource=resource,
            logger=self._logger,
        )
        raise error


class MaleoClientManager(ClientManager):
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
        super().__init__(
            configurations.key,
            configurations.name,
            log_config,
            service_context,
        )
        self._environment = configurations.environment
        if (
            self._operation_origin.details is not None
            and "identifier" in self._operation_origin.details.keys()
            and isinstance(self._operation_origin.details["identifier"], dict)
        ):
            self._operation_origin.details["identifier"][
                "environment"
            ] = self._environment
        self._url = configurations.url
        self._credential_manager = credential_manager
        self._private_key = private_key
        self._redis = redis
        self._redis_namespaces = redis_namespaces

    @property
    def environment(self) -> Environment:
        return self._environment

    def _initialize_controllers(self) -> None:
        # * Initialize managers
        http_controller_manager = ClientHTTPControllerManager(url=self._url)
        self._controller_managers = ClientControllerManagers(
            http=http_controller_manager
        )
        # * Initialize controllers
        #! This initialied an empty controllers. Extend this function in the actual class to initialize all controllers.
        self._controllers = ClientControllers()

    @property
    def controllers(self) -> ClientControllers:
        return self._controllers
