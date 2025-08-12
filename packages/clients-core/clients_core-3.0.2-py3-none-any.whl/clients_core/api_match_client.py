from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from clients_core.exceptions import EndpointMatchError
from clients_core.service_list_provider import (
    ServiceListProvider,
    Service,
    Endpoint,
    Version,
)
from clients_core.simple_rest_client import SimpleRestClient
from clients_core.secured_rest_client import SecuredRestClient
from clients_core.authentication.token_handler import TokenHandler
from dataclasses import dataclass


@dataclass
class MatchSpec:
    """
    Used to determine the endpoint that is required by the client
    """

    service_name: str
    endpoint_name: str
    version_major: int
    version_minor: int
    version_patch: int
    scopes: List[str]

    def get_version(self) -> Version:
        return Version(
            major=self.version_major, minor=self.version_minor, patch=self.version_patch
        )

    def __repr__(self) -> str:
        return f"Service: {self.service_name} - {self.endpoint_name}, Version: {self.version_major}.{self.version_minor}.{self.version_patch}"


class ApiMatchClient(ABC):
    _service_provider: ServiceListProvider

    def get_secured_client(
        self,
        match: MatchSpec,
        token_handler: TokenHandler,
        extra_headers: Optional[Dict] = None,
        extra_params: Optional[Dict] = None,
        verify_ssl: bool = True,
    ) -> SecuredRestClient:
        base_path = self.get_endpoint_uri(match)
        if not base_path:
            raise EndpointMatchError(
                f"No endpoint offering found for {str(match)} at {self._service_provider.source}"
            )
        return SecuredRestClient(
            base_path,
            match.scopes,
            token_handler,
            extra_headers,
            extra_params,
            verify_ssl,
        )

    def get_simple_client(
        self,
        match: MatchSpec,
        extra_headers: Optional[Dict] = None,
        extra_params: Optional[Dict] = None,
        verify_ssl: bool = True,
    ) -> SimpleRestClient:
        base_path = self.get_endpoint_uri(match)
        if not base_path:
            raise EndpointMatchError(
                f"No endpoint offering found for {str(match)} at {self._service_provider.source}"
            )
        return SimpleRestClient(base_path, extra_headers, extra_params, verify_ssl)

    def _find_match(self, match: MatchSpec, services: List[Service]) -> Optional[str]:
        matched_services = self._match_services(match, services)
        endpoints = self._match_endpoints(match, matched_services)
        matches = self._match_version(match, endpoints)
        return matches[0].uri if matches else None

    def _match_services(
        self, match: MatchSpec, services: List[Service]
    ) -> List[Service]:
        return [service for service in services if service.name == match.service_name]

    def _match_endpoints(
        self, match: MatchSpec, services: List[Service]
    ) -> List[Endpoint]:
        return [
            endpoint
            for service in services
            for endpoint in service.endpoints
            if endpoint.name == match.endpoint_name
        ]

    def _match_version(
        self, match: MatchSpec, endpoints: List[Endpoint]
    ) -> List[Endpoint]:
        return [
            endpoint
            for endpoint in endpoints
            if Version.is_compatible(match.get_version(), endpoint.version)
        ]

    @abstractmethod
    def get_endpoint_uri(self, match: MatchSpec) -> Optional[str]:
        raise NotImplementedError()  # pragma: no cover


class GatewayMatchClient(ApiMatchClient):
    def __init__(self, service_provider: ServiceListProvider):
        self._service_provider = service_provider

    def get_secured_client(
        self,
        match: MatchSpec,
        token_handler: TokenHandler,
        extra_headers: Optional[Dict] = None,
        extra_params: Optional[Dict] = None,
        verify_ssl: bool = True,
    ) -> SecuredRestClient:
        raise NotImplementedError()  # pragma: no cover

    def get_endpoint_uri(self, match: MatchSpec) -> Optional[str]:
        services = self._service_provider.get_service_list()
        return self._find_match(match, services)


class ServiceDirectoryMatchClient(ApiMatchClient):
    def __init__(self, service_prvider: ServiceListProvider):
        self._service_provider = service_prvider

    def get_endpoint_uri(self, match: MatchSpec) -> Optional[str]:
        data: Dict[Any, Any] = {
            "name": match.service_name,
            "endpoint_name": match.endpoint_name,
            "version_major": match.version_major,
            "version_minor": match.version_minor,
            "version_patch": match.version_patch,
        }
        services = self._service_provider.get_service_list(**data)
        return self._find_match(match, services)
