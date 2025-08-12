from abc import ABC, abstractmethod
from typing import Dict, List, Any
from dataclasses import dataclass
import semver


@dataclass
class Version:
    major: int
    minor: int
    patch: int
    prerelease: str = ""
    build: str = ""

    @staticmethod
    def from_string(version: str) -> "Version":
        return Version(**semver.parse(version))

    @staticmethod
    def from_endpoint(endpoint: Dict) -> "Version":
        return Version(
            major=endpoint["version"]["major"],
            minor=endpoint["version"]["minor"],
            patch=endpoint["version"]["patch"],
        )

    @staticmethod
    def is_compatible(requested: "Version", available: "Version") -> bool:
        return (
            requested.major == available.major
            and requested.minor <= available.minor
            and (
                requested.patch <= available.patch or requested.minor < available.minor
            )
        )


@dataclass
class Endpoint:
    name: str
    version: Version
    uri: str

    @staticmethod
    def from_endpoint(endpoint: Dict) -> "Endpoint":
        return Endpoint(
            name=endpoint["name"],
            version=Version.from_endpoint(endpoint),
            uri=endpoint["properties"]["uri"],
        )


@dataclass
class Service:
    name: str
    endpoints: List[Endpoint]

    @staticmethod
    def from_service(service: Dict) -> "Service":
        return Service(
            name=service["name"],
            endpoints=[
                Endpoint.from_endpoint(endpoint) for endpoint in service["endpoints"]
            ],
        )


class ServiceListProvider(ABC):
    @property
    @abstractmethod
    def source(self) -> str:
        raise NotImplementedError()  # pragma: no cover

    @abstractmethod
    def get_service_list(self, **kwargs: Any) -> List[Service]:
        raise NotImplementedError()  # pragma: no cover
