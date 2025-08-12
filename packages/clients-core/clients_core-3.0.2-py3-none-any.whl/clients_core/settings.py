from typing import Optional
import logging
from pydantic_settings import BaseSettings

_environment = None


class Environ(BaseSettings):
    """
    Dataclass for holing environment variables with defaults
    """

    # Runtime variables
    DEBUG: bool = False
    LOG_LEVEL: int = logging.INFO
    SSL_VERIFY: bool = True
    REDIS_CONNECTION_URL: str = "redis://localhost:6379/0"

    # E360 configuration variables
    OIDC_CLIENT_ID: str = ""
    OIDC_CLIENT_SECRET: str = ""
    OIDC_TOKEN_ENDPOINT_URL: str = ""


def get_environ(reload: bool = False) -> Optional[Environ]:
    """
    Function for a lazy loading of an Environ instance.
    reload (bool): forces the environment variables to be re-read.
    """
    if _environment is None or reload is True:
        globals()["_environment"] = Environ()
    return _environment
