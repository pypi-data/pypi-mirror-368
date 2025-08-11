# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, Union, Mapping
from typing_extensions import Self, override

import httpx

from . import _exceptions
from ._qs import Querystring
from ._types import (
    NOT_GIVEN,
    Omit,
    Timeout,
    NotGiven,
    Transport,
    ProxiesTypes,
    RequestOptions,
)
from ._utils import is_given, get_async_library
from ._version import __version__
from .resources import auth, card, pack, match, profit, redeem, userinventory
from ._streaming import Stream as Stream, AsyncStream as AsyncStream
from ._exceptions import FvError, APIStatusError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
)
from .resources.me import me
from .resources.user import user
from .resources.lineup import lineup

__all__ = ["Timeout", "Transport", "ProxiesTypes", "RequestOptions", "Fv", "AsyncFv", "Client", "AsyncClient"]


class Fv(SyncAPIClient):
    profit: profit.ProfitResource
    pack: pack.PackResource
    me: me.MeResource
    redeem: redeem.RedeemResource
    lineup: lineup.LineupResource
    user: user.UserResource
    card: card.CardResource
    match: match.MatchResource
    userinventory: userinventory.UserinventoryResource
    auth: auth.AuthResource
    with_raw_response: FvWithRawResponse
    with_streaming_response: FvWithStreamedResponse

    # client options
    api_key: str

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#client) for more details.
        http_client: httpx.Client | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new synchronous Fv client instance.

        This automatically infers the `api_key` argument from the `FV_API_KEY` environment variable if it is not provided.
        """
        if api_key is None:
            api_key = os.environ.get("FV_API_KEY")
        if api_key is None:
            raise FvError(
                "The api_key client option must be set either by passing api_key to the client or by setting the FV_API_KEY environment variable"
            )
        self.api_key = api_key

        if base_url is None:
            base_url = os.environ.get("FV_BASE_URL")
        if base_url is None:
            base_url = f"https://api.example.com"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.profit = profit.ProfitResource(self)
        self.pack = pack.PackResource(self)
        self.me = me.MeResource(self)
        self.redeem = redeem.RedeemResource(self)
        self.lineup = lineup.LineupResource(self)
        self.user = user.UserResource(self)
        self.card = card.CardResource(self)
        self.match = match.MatchResource(self)
        self.userinventory = userinventory.UserinventoryResource(self)
        self.auth = auth.AuthResource(self)
        self.with_raw_response = FvWithRawResponse(self)
        self.with_streaming_response = FvWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        api_key = self.api_key
        return {"Authorization": api_key}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": "false",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.Client | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            api_key=api_key or self.api_key,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class AsyncFv(AsyncAPIClient):
    profit: profit.AsyncProfitResource
    pack: pack.AsyncPackResource
    me: me.AsyncMeResource
    redeem: redeem.AsyncRedeemResource
    lineup: lineup.AsyncLineupResource
    user: user.AsyncUserResource
    card: card.AsyncCardResource
    match: match.AsyncMatchResource
    userinventory: userinventory.AsyncUserinventoryResource
    auth: auth.AsyncAuthResource
    with_raw_response: AsyncFvWithRawResponse
    with_streaming_response: AsyncFvWithStreamedResponse

    # client options
    api_key: str

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultAsyncHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#asyncclient) for more details.
        http_client: httpx.AsyncClient | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new async AsyncFv client instance.

        This automatically infers the `api_key` argument from the `FV_API_KEY` environment variable if it is not provided.
        """
        if api_key is None:
            api_key = os.environ.get("FV_API_KEY")
        if api_key is None:
            raise FvError(
                "The api_key client option must be set either by passing api_key to the client or by setting the FV_API_KEY environment variable"
            )
        self.api_key = api_key

        if base_url is None:
            base_url = os.environ.get("FV_BASE_URL")
        if base_url is None:
            base_url = f"https://api.example.com"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.profit = profit.AsyncProfitResource(self)
        self.pack = pack.AsyncPackResource(self)
        self.me = me.AsyncMeResource(self)
        self.redeem = redeem.AsyncRedeemResource(self)
        self.lineup = lineup.AsyncLineupResource(self)
        self.user = user.AsyncUserResource(self)
        self.card = card.AsyncCardResource(self)
        self.match = match.AsyncMatchResource(self)
        self.userinventory = userinventory.AsyncUserinventoryResource(self)
        self.auth = auth.AsyncAuthResource(self)
        self.with_raw_response = AsyncFvWithRawResponse(self)
        self.with_streaming_response = AsyncFvWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        api_key = self.api_key
        return {"Authorization": api_key}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": f"async:{get_async_library()}",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.AsyncClient | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            api_key=api_key or self.api_key,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class FvWithRawResponse:
    def __init__(self, client: Fv) -> None:
        self.profit = profit.ProfitResourceWithRawResponse(client.profit)
        self.pack = pack.PackResourceWithRawResponse(client.pack)
        self.me = me.MeResourceWithRawResponse(client.me)
        self.redeem = redeem.RedeemResourceWithRawResponse(client.redeem)
        self.lineup = lineup.LineupResourceWithRawResponse(client.lineup)
        self.user = user.UserResourceWithRawResponse(client.user)
        self.card = card.CardResourceWithRawResponse(client.card)
        self.match = match.MatchResourceWithRawResponse(client.match)
        self.userinventory = userinventory.UserinventoryResourceWithRawResponse(client.userinventory)
        self.auth = auth.AuthResourceWithRawResponse(client.auth)


class AsyncFvWithRawResponse:
    def __init__(self, client: AsyncFv) -> None:
        self.profit = profit.AsyncProfitResourceWithRawResponse(client.profit)
        self.pack = pack.AsyncPackResourceWithRawResponse(client.pack)
        self.me = me.AsyncMeResourceWithRawResponse(client.me)
        self.redeem = redeem.AsyncRedeemResourceWithRawResponse(client.redeem)
        self.lineup = lineup.AsyncLineupResourceWithRawResponse(client.lineup)
        self.user = user.AsyncUserResourceWithRawResponse(client.user)
        self.card = card.AsyncCardResourceWithRawResponse(client.card)
        self.match = match.AsyncMatchResourceWithRawResponse(client.match)
        self.userinventory = userinventory.AsyncUserinventoryResourceWithRawResponse(client.userinventory)
        self.auth = auth.AsyncAuthResourceWithRawResponse(client.auth)


class FvWithStreamedResponse:
    def __init__(self, client: Fv) -> None:
        self.profit = profit.ProfitResourceWithStreamingResponse(client.profit)
        self.pack = pack.PackResourceWithStreamingResponse(client.pack)
        self.me = me.MeResourceWithStreamingResponse(client.me)
        self.redeem = redeem.RedeemResourceWithStreamingResponse(client.redeem)
        self.lineup = lineup.LineupResourceWithStreamingResponse(client.lineup)
        self.user = user.UserResourceWithStreamingResponse(client.user)
        self.card = card.CardResourceWithStreamingResponse(client.card)
        self.match = match.MatchResourceWithStreamingResponse(client.match)
        self.userinventory = userinventory.UserinventoryResourceWithStreamingResponse(client.userinventory)
        self.auth = auth.AuthResourceWithStreamingResponse(client.auth)


class AsyncFvWithStreamedResponse:
    def __init__(self, client: AsyncFv) -> None:
        self.profit = profit.AsyncProfitResourceWithStreamingResponse(client.profit)
        self.pack = pack.AsyncPackResourceWithStreamingResponse(client.pack)
        self.me = me.AsyncMeResourceWithStreamingResponse(client.me)
        self.redeem = redeem.AsyncRedeemResourceWithStreamingResponse(client.redeem)
        self.lineup = lineup.AsyncLineupResourceWithStreamingResponse(client.lineup)
        self.user = user.AsyncUserResourceWithStreamingResponse(client.user)
        self.card = card.AsyncCardResourceWithStreamingResponse(client.card)
        self.match = match.AsyncMatchResourceWithStreamingResponse(client.match)
        self.userinventory = userinventory.AsyncUserinventoryResourceWithStreamingResponse(client.userinventory)
        self.auth = auth.AsyncAuthResourceWithStreamingResponse(client.auth)


Client = Fv

AsyncClient = AsyncFv
