from abc import ABC, abstractmethod
import dataclasses
from typing import List
from oauthlib.oauth2 import BackendApplicationClient
from oauthlib.oauth2.rfc6749.errors import InvalidScopeError
from requests_oauthlib import OAuth2Session
import logging

logger = logging.getLogger(__name__)


class TokenHandler(ABC):
    @abstractmethod
    def get_endpoint_url(self) -> str:
        """
        Returns a string that will identify the source of the token fetched
        Used by TokenCache for key generation
        """
        raise NotImplementedError()  # pragma: no cover

    @abstractmethod
    def fetch_token(self, scopes: List[str]) -> dict:
        raise NotImplementedError()  # pragma: no cover


@dataclasses.dataclass
class OIDCTokenHandler(TokenHandler):
    oidc_token_endpoint: str
    oidc_client_id: str
    oidc_client_secret: str
    ssl_verify: bool = True
    timeout: float = 5.0

    def get_endpoint_url(self) -> str:
        return self.oidc_token_endpoint

    def fetch_token(self, scopes: List[str]) -> dict:
        client = BackendApplicationClient(client_id=self.oidc_client_id)
        session = OAuth2Session(client=client)
        logger.info(f"Retrieving new OIDC token with scopes: {scopes}")
        # Fetch the token with using the session and params
        try:
            return session.fetch_token(
                token_url=self.oidc_token_endpoint,
                method="POST",
                client_id=self.oidc_client_id,
                client_secret=self.oidc_client_secret,
                timeout=self.timeout,
                verify=self.ssl_verify,
                scope=scopes,
            )
        except InvalidScopeError:
            msg = (
                "Invalid OIDC token scope configuration. "
                "Check the requested scopes match the available scopes in platform."
            )
            raise Exception(msg)
