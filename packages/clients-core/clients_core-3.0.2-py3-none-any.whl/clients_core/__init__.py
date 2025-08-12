__version__ = "3.0.2"

__all__ = [
    "authentication",
    "SimpleRestClient",
    "SecuredRestClient",
    "RestClient",
    "ApiMatchClient",
    "ServiceDirectoryMatchClient",
    "GatewayMatchClient",
    "JsonPatchModel",
    "MetaModel",
]


from clients_core.api_match_client import (
    ApiMatchClient,
    GatewayMatchClient,
    ServiceDirectoryMatchClient,
)
from clients_core.models import JsonPatchModel, MetaModel
from clients_core.rest_client import RestClient
from clients_core.secured_rest_client import SecuredRestClient
from clients_core.simple_rest_client import SimpleRestClient
