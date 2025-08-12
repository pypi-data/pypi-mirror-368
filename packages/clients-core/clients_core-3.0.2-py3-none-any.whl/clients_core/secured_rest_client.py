from typing import Dict, List, Any, Optional
from clients_core.simple_rest_client import SimpleRestClient
from clients_core.authentication.token_handler import TokenHandler


class SecuredRestClient(SimpleRestClient):
    """
    Secured API Client provides interface for HTTP requests, applies claims and token
    """

    token_handler: TokenHandler

    def __init__(
        self,
        base_path: str,
        scopes: List[str],
        token_handler: TokenHandler,
        extra_headers: Optional[Dict] = None,
        extra_params: Optional[Dict] = None,
        verify_ssl: bool = True,
    ):
        super().__init__(base_path, extra_headers, extra_params, verify_ssl=verify_ssl)
        self.token_handler = token_handler
        self.scopes = scopes

    def _create_auth(self) -> Dict:
        bearer_token = self.token_handler.fetch_token(self.scopes)["access_token"]
        return {"authorization": f"Bearer {bearer_token}"}

    def _update_headers(self, **kwargs: Any) -> Dict:
        kwargs = super()._update_headers(**kwargs)
        headers = kwargs.get("headers", {})
        headers.update(self._create_auth())
        kwargs["headers"] = headers
        return kwargs
