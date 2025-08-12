import requests
from contextlib import suppress
from dataclasses import dataclass
from clients_core.exceptions import HttpResponseError


@dataclass
class ResponseErrorHelper:
    """
    Helps handling Http error response exception raising.

    Args:
        response (requests.Response): takes a Response instance as an argument.

    ``self._default_message``: default message when the server does not provide a Json with "message".
    """

    response: requests.Response
    _default_message = "Service did not provide an error message"

    def __post_init__(self) -> None:
        """
        Captures an exception for HttpError, saves as ``self.exception``.
        """
        try:
            self.response.raise_for_status()
        except (requests.HTTPError) as exc:
            self.exception = exc

    def raise_exception(self) -> HttpResponseError:
        """
        Fetches a message from the server and raises an exception with it.

        Raises:
            HttpResponseError
        """
        msg = self._get_server_error_message()
        raise HttpResponseError(msg) from self.exception

    def _get_server_error_message(self) -> str:
        """
        Gets the "message" from Json resonse body, or falls back to ``_default_message``.
        """
        with suppress(ValueError, KeyError, TypeError):
            response = self.response.json()
            details = ", ".join(response.get("details", []))
            message = response.get("message", "")
            complete_message = f"{message}{': ' if details else ''}{details}"
            return complete_message or self._default_message
        return self._default_message
