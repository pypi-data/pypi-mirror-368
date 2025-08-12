# Custom OAuth token provider for the Termina Python SDK

import typing
import jwt
from datetime import datetime, timedelta, UTC

from ..auth.client import AuthClient
from .client_wrapper import SyncClientWrapper


class OAuthTokenProvider:
    BUFFER_IN_MINUTES = 2

    def __init__(self, *, api_key: str, client_wrapper: SyncClientWrapper):
        self._api_key = api_key
        self._access_token: typing.Optional[str] = None
        self._expires_at: datetime = datetime.now(UTC)
        self._auth_client = AuthClient(client_wrapper=client_wrapper)

    def get_token(self) -> str:
        if self._access_token and not self.expired:
            return self._access_token
        return self._refresh()

    def _refresh(self) -> str:
        token_response = self._auth_client.get_token(api_key=self._api_key)
        self._access_token = token_response.access_token
        exp = jwt.decode(self._access_token, options={"verify_signature": False})["exp"]
        self._expires_at = datetime.fromtimestamp(exp, UTC) - timedelta(
            minutes=self.BUFFER_IN_MINUTES
        )
        return self._access_token

    @property
    def expired(self) -> bool:
        return self._expires_at < datetime.now(UTC)
