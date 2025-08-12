# Custom client for the Termina Python SDK

import typing

import httpx

from .base_client import AsyncBaseClient, BaseClient
from .core.client_wrapper import SyncClientWrapper
from .core.oauth_token_provider import OAuthTokenProvider
from .environment import TerminaEnvironment


class Termina(BaseClient):
    def __init__(
        self,
        *,
        api_key: str,
        base_url: typing.Optional[str] = None,
        environment: TerminaEnvironment = TerminaEnvironment.DEFAULT,
        timeout: typing.Optional[float] = None,
        follow_redirects: typing.Optional[bool] = True,
        httpx_client: typing.Optional[httpx.Client] = None,
    ):
        _defaulted_timeout = (
            timeout if timeout is not None else 60 if httpx_client is None else None
        )
        oauth_token_provider = OAuthTokenProvider(
            api_key=api_key,
            client_wrapper=SyncClientWrapper(
                base_url=_get_base_url(base_url=base_url, environment=environment),
                httpx_client=(
                    httpx.Client(
                        timeout=_defaulted_timeout, follow_redirects=follow_redirects
                    )
                    if follow_redirects is not None
                    else httpx.Client(timeout=_defaulted_timeout)
                ),
                timeout=_defaulted_timeout,
            ),
        )

        super().__init__(
            base_url=base_url,
            environment=environment,
            token=oauth_token_provider.get_token,
            timeout=timeout,
            follow_redirects=follow_redirects,
            httpx_client=httpx_client,
        )


class AsyncTermina(AsyncBaseClient):
    def __init__(
        self,
        *,
        api_key: str,
        base_url: typing.Optional[str] = None,
        environment: TerminaEnvironment = TerminaEnvironment.DEFAULT,
        timeout: typing.Optional[float] = None,
        follow_redirects: typing.Optional[bool] = True,
        httpx_client: typing.Optional[httpx.AsyncClient] = None,
    ):
        _defaulted_timeout = (
            timeout if timeout is not None else 60 if httpx_client is None else None
        )
        oauth_token_provider = OAuthTokenProvider(
            api_key=api_key,
            client_wrapper=SyncClientWrapper(
                base_url=_get_base_url(base_url=base_url, environment=environment),
                httpx_client=(
                    httpx.Client(
                        timeout=_defaulted_timeout, follow_redirects=follow_redirects
                    )
                    if follow_redirects is not None
                    else httpx.Client(timeout=_defaulted_timeout)
                ),
                timeout=_defaulted_timeout,
            ),
        )

        super().__init__(
            base_url=base_url,
            environment=environment,
            token=oauth_token_provider.get_token,
            timeout=timeout,
            follow_redirects=follow_redirects,
            httpx_client=httpx_client,
        )


def _get_base_url(
    *, base_url: typing.Optional[str] = None, environment: TerminaEnvironment
) -> str:
    if base_url is not None:
        return base_url
    elif environment is not None:
        return environment.value
    else:
        raise Exception(
            "Please pass in either base_url or environment to construct the client"
        )
