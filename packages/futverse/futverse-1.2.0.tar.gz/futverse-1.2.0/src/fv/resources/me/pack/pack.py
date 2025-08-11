# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .config import (
    ConfigResource,
    AsyncConfigResource,
    ConfigResourceWithRawResponse,
    AsyncConfigResourceWithRawResponse,
    ConfigResourceWithStreamingResponse,
    AsyncConfigResourceWithStreamingResponse,
)
from ...._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ...._utils import strip_not_given
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.me.pack_buy_response import PackBuyResponse
from ....types.me.pack_open_response import PackOpenResponse

__all__ = ["PackResource", "AsyncPackResource"]


class PackResource(SyncAPIResource):
    @cached_property
    def config(self) -> ConfigResource:
        return ConfigResource(self._client)

    @cached_property
    def with_raw_response(self) -> PackResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/victorgabrieldeon/fv-api#accessing-raw-response-data-eg-headers
        """
        return PackResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PackResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/victorgabrieldeon/fv-api#with_streaming_response
        """
        return PackResourceWithStreamingResponse(self)

    def buy(
        self,
        pack_id: str,
        *,
        accept_language: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PackBuyResponse:
        """
        Compra um pack.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not pack_id:
            raise ValueError(f"Expected a non-empty value for `pack_id` but received {pack_id!r}")
        extra_headers = {**strip_not_given({"accept-language": accept_language}), **(extra_headers or {})}
        return self._post(
            f"/@me/pack/{pack_id}/buy",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PackBuyResponse,
        )

    def open(
        self,
        pack_id: str,
        *,
        accept_language: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PackOpenResponse:
        """
        Abre um pack.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not pack_id:
            raise ValueError(f"Expected a non-empty value for `pack_id` but received {pack_id!r}")
        extra_headers = {**strip_not_given({"accept-language": accept_language}), **(extra_headers or {})}
        return self._post(
            f"/@me/pack/{pack_id}/open",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PackOpenResponse,
        )


class AsyncPackResource(AsyncAPIResource):
    @cached_property
    def config(self) -> AsyncConfigResource:
        return AsyncConfigResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncPackResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/victorgabrieldeon/fv-api#accessing-raw-response-data-eg-headers
        """
        return AsyncPackResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPackResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/victorgabrieldeon/fv-api#with_streaming_response
        """
        return AsyncPackResourceWithStreamingResponse(self)

    async def buy(
        self,
        pack_id: str,
        *,
        accept_language: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PackBuyResponse:
        """
        Compra um pack.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not pack_id:
            raise ValueError(f"Expected a non-empty value for `pack_id` but received {pack_id!r}")
        extra_headers = {**strip_not_given({"accept-language": accept_language}), **(extra_headers or {})}
        return await self._post(
            f"/@me/pack/{pack_id}/buy",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PackBuyResponse,
        )

    async def open(
        self,
        pack_id: str,
        *,
        accept_language: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PackOpenResponse:
        """
        Abre um pack.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not pack_id:
            raise ValueError(f"Expected a non-empty value for `pack_id` but received {pack_id!r}")
        extra_headers = {**strip_not_given({"accept-language": accept_language}), **(extra_headers or {})}
        return await self._post(
            f"/@me/pack/{pack_id}/open",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PackOpenResponse,
        )


class PackResourceWithRawResponse:
    def __init__(self, pack: PackResource) -> None:
        self._pack = pack

        self.buy = to_raw_response_wrapper(
            pack.buy,
        )
        self.open = to_raw_response_wrapper(
            pack.open,
        )

    @cached_property
    def config(self) -> ConfigResourceWithRawResponse:
        return ConfigResourceWithRawResponse(self._pack.config)


class AsyncPackResourceWithRawResponse:
    def __init__(self, pack: AsyncPackResource) -> None:
        self._pack = pack

        self.buy = async_to_raw_response_wrapper(
            pack.buy,
        )
        self.open = async_to_raw_response_wrapper(
            pack.open,
        )

    @cached_property
    def config(self) -> AsyncConfigResourceWithRawResponse:
        return AsyncConfigResourceWithRawResponse(self._pack.config)


class PackResourceWithStreamingResponse:
    def __init__(self, pack: PackResource) -> None:
        self._pack = pack

        self.buy = to_streamed_response_wrapper(
            pack.buy,
        )
        self.open = to_streamed_response_wrapper(
            pack.open,
        )

    @cached_property
    def config(self) -> ConfigResourceWithStreamingResponse:
        return ConfigResourceWithStreamingResponse(self._pack.config)


class AsyncPackResourceWithStreamingResponse:
    def __init__(self, pack: AsyncPackResource) -> None:
        self._pack = pack

        self.buy = async_to_streamed_response_wrapper(
            pack.buy,
        )
        self.open = async_to_streamed_response_wrapper(
            pack.open,
        )

    @cached_property
    def config(self) -> AsyncConfigResourceWithStreamingResponse:
        return AsyncConfigResourceWithStreamingResponse(self._pack.config)
