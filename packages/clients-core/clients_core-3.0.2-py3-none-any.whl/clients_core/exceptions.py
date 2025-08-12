class ClientException(Exception):
    """
    Base level exception for all errors specific to e360 python clients
    """

    pass


class EndpointMatchError(ClientException):
    pass


class ClientValueError(ClientException):
    """Error for when the response is provided, but does not match expected value/format/content."""

    pass


class HttpResponseError(ClientException):
    """Error used when the Microservice returns a non-2XX response"""

    pass
