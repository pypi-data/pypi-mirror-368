import json
import base64
from abc import ABC, abstractmethod
from typing import Dict, TypedDict, ClassVar
from dataclasses import dataclass
from clients_core.simple_rest_client import SimpleRestClient

_CLAIMS_HEADER = "x-ims-claims"
_CORRELATION_HEADER = "x-correlation-id"


class ClientOptions(TypedDict):
    trim_trailing_slash: bool


@dataclass  # type: ignore
class E360ServiceClient(ABC):
    """
    Abstract Service Client dataclass, to be used for building other microservice clients.

    Args:
        client: an instance of a simple or secure rest client
        user_id: the user_id guid
        correlation_id: optional, correlation id when available

    """

    client: SimpleRestClient
    user_id: str
    correlation_id: str = None  # type: ignore
    client_options: ClassVar[ClientOptions] = {"trim_trailing_slash": False}

    extra_headers = {}  # type: Dict[str, str]

    def __post_init__(self) -> None:
        self.client.extra_headers.update(self.extra_headers)
        if self.client_options.get("trim_trailing_slash"):
            self.client.base_path = self.client.base_path.rstrip("/")

    @property
    @abstractmethod
    def service_endpoint(self) -> str:
        """``
        Class proterty holding an endpoint value.

        Examples:
            ```
            class SomeClient(E360ServiceClient):
                service_endpoint = 'services'
            ```

        """
        raise NotImplementedError  # pragma: no cover

    def get_ims_claims(self) -> Dict:
        return self.get_ims_claims_for_user(self.user_id) if self.user_id else {}

    @staticmethod
    def get_ims_claims_for_user(user_id: str) -> Dict:
        """
        Returns a dictionary with the X-Ims-Claims encoded header containing the user_id.
        """
        sub = {"sub": str(user_id)}
        claims = json.dumps(sub, separators=(",", ":")).encode()
        return {_CLAIMS_HEADER: base64.b64encode(claims).decode().rstrip("=")}

    def get_correlation(self) -> Dict:
        if self.correlation_id is not None:
            return {_CORRELATION_HEADER: self.correlation_id}
        return {}

    @property
    def service_headers(self) -> Dict:
        """
        Returns X-IMS-CLAIMS and correlation_id dictionary.
        """
        headers = {**self.get_ims_claims(), **self.get_correlation()}
        return headers
