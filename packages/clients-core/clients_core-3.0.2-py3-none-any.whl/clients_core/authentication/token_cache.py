import json
import time
from clients_core.authentication.cache import Cache
from clients_core.authentication.token_handler import TokenHandler
from typing import List
import logging


logger = logging.getLogger(__name__)


class TokenCache(TokenHandler):
    def __init__(self, cache: Cache, token_handler: TokenHandler):
        self.token_handler = token_handler
        self.cache = cache

    def get_endpoint_url(self) -> str:
        return self.token_handler.get_endpoint_url()

    def _new_token(self, scopes: List[str]) -> dict:
        token = self.token_handler.fetch_token(scopes)
        self.cache.set(self._token_key(scopes), json.dumps(token))
        return token

    def _token_key(self, scopes: List[str]) -> str:
        return f"{self.token_handler.get_endpoint_url()} -- {scopes}"

    def fetch_token(self, scopes: List[str]) -> dict:
        cached_value = self.cache.get(self._token_key(scopes))
        token = json.loads(cached_value) if cached_value else None
        utc_timestamp = time.time()
        skew_seconds = (
            60  # A safety buffer, protects against clock disparities and other delays
        )
        if token is None or int(token["expires_at"] - skew_seconds) <= int(
            utc_timestamp
        ):
            token = self._new_token(scopes)

        return token
