from abc import ABC, abstractmethod
from typing import Dict, Any
from requests import Response


class RestClient(ABC):
    @property
    @abstractmethod
    def base_url(self) -> str:
        raise NotImplementedError()  # pragma: no cover

    @abstractmethod
    def get(self, endpoint_path: str, **kwargs: Any) -> Response:
        raise NotImplementedError()  # pragma: no cover

    @abstractmethod
    def post(self, endpoint_path: str, data: Dict = {}, **kwargs: Any) -> Response:
        raise NotImplementedError()  # pragma: no cover

    @abstractmethod
    def delete(self, endpoint_path: str, **kwargs: Any) -> Response:
        raise NotImplementedError()  # pragma: no cover

    @abstractmethod
    def patch(self, endpoint_path: str, data: Dict = {}, **kwargs: Any) -> Response:
        raise NotImplementedError()  # pragma: no cover

    @abstractmethod
    def put(self, endpoint_path: str, data: Dict = {}, **kwargs: Any) -> Response:
        raise NotImplementedError()  # pragma: no cover

    @abstractmethod
    def head(self, endpoint_path: str, **kwargs: Any) -> Response:
        raise NotImplementedError()  # pragma: no cover
