from typing import Dict, Any, Optional
from posixpath import join as urljoin
from requests import request, Response
from clients_core.utils import ResponseErrorHelper
from clients_core.rest_client import RestClient

"""
Simple API Client provides interface for HTTP requests
"""


class SimpleRestClient(RestClient):
    base_path: str
    extra_headers: Dict
    extra_params: Dict

    def __init__(
        self,
        base_path: str,
        extra_headers: Optional[Dict] = None,
        extra_params: Optional[Dict] = None,
        verify_ssl: bool = True,
    ):
        self.base_path = base_path
        if extra_headers is None:
            extra_headers = {}
        if extra_params is None:
            extra_params = {}
        self.extra_params = extra_params
        self.extra_headers = extra_headers
        self.verify_ssl = verify_ssl

    def _update_headers(self, **kwargs: Any) -> Dict:
        headers = kwargs.get("headers", {})
        headers.update(self.extra_headers)
        kwargs["headers"] = headers
        return kwargs

    def _update_params(self, **kwargs: Any) -> Dict:
        params = kwargs.get("params", {})
        params.update(self.extra_params)
        kwargs["params"] = params
        return kwargs

    def _request(
        self, method: str, endpoint_path: str, raises: bool = False, **kwargs: Any
    ) -> Response:
        kwargs = self._update_headers(**kwargs)
        kwargs = self._update_params(**kwargs)
        service_path = self._get_service_path(endpoint_path)
        response = request(method, service_path, verify=self.verify_ssl, **kwargs)
        if raises and not response.ok:
            ResponseErrorHelper(response).raise_exception()
        return response

    def _get_service_path(self, endpoint_path: str) -> str:
        endpoint = endpoint_path.lstrip("/")
        if endpoint:
            return urljoin(self.base_path, endpoint)
        return self.base_path

    @property
    def base_url(self) -> str:
        return self.base_path

    def get(self, endpoint_path: str, **kwargs: Any) -> Response:
        return self._request("get", endpoint_path, **kwargs)

    def post(self, endpoint_path: str, data: Dict = {}, **kwargs: Any) -> Response:
        return self._request("post", endpoint_path, data=data, **kwargs)

    def patch(self, endpoint_path: str, data: Dict = {}, **kwargs: Any) -> Response:
        return self._request("patch", endpoint_path, data=data, **kwargs)

    def put(self, endpoint_path: str, data: Dict = {}, **kwargs: Any) -> Response:
        return self._request("put", endpoint_path, data=data, **kwargs)

    def delete(self, endpoint_path: str, **kwargs: Any) -> Response:
        return self._request("delete", endpoint_path, **kwargs)

    def head(self, endpoint_path: str, **kwargs: Any) -> Response:
        return self._request("head", endpoint_path, **kwargs)
