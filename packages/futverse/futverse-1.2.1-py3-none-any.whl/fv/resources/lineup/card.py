# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
from ..._utils import maybe_transform, strip_not_given, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.lineup import card_up_params

__all__ = ["CardResource", "AsyncCardResource"]


class CardResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> CardResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/victorgabrieldeon/fv-api#accessing-raw-response-data-eg-headers
        """
        return CardResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CardResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/victorgabrieldeon/fv-api#with_streaming_response
        """
        return CardResourceWithStreamingResponse(self)

    def down(
        self,
        usercard_id: int,
        *,
        accept_language: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Retira um card do time titular.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        extra_headers = {**strip_not_given({"accept-language": accept_language}), **(extra_headers or {})}
        return self._delete(
            f"/lineup/card/{usercard_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def up(
        self,
        usercard_id: int,
        *,
        position: Literal["GOL", "LD", "LE", "ZAG", "VOL", "MA", "MC", "PD", "PE", "CA"],
        accept_language: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Escala um card do usuário para o time titular.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        extra_headers = {**strip_not_given({"accept-language": accept_language}), **(extra_headers or {})}
        return self._post(
            f"/lineup/card/{usercard_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"position": position}, card_up_params.CardUpParams),
            ),
            cast_to=NoneType,
        )


class AsyncCardResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncCardResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/victorgabrieldeon/fv-api#accessing-raw-response-data-eg-headers
        """
        return AsyncCardResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCardResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/victorgabrieldeon/fv-api#with_streaming_response
        """
        return AsyncCardResourceWithStreamingResponse(self)

    async def down(
        self,
        usercard_id: int,
        *,
        accept_language: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Retira um card do time titular.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        extra_headers = {**strip_not_given({"accept-language": accept_language}), **(extra_headers or {})}
        return await self._delete(
            f"/lineup/card/{usercard_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def up(
        self,
        usercard_id: int,
        *,
        position: Literal["GOL", "LD", "LE", "ZAG", "VOL", "MA", "MC", "PD", "PE", "CA"],
        accept_language: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Escala um card do usuário para o time titular.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        extra_headers = {**strip_not_given({"accept-language": accept_language}), **(extra_headers or {})}
        return await self._post(
            f"/lineup/card/{usercard_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"position": position}, card_up_params.CardUpParams),
            ),
            cast_to=NoneType,
        )


class CardResourceWithRawResponse:
    def __init__(self, card: CardResource) -> None:
        self._card = card

        self.down = to_raw_response_wrapper(
            card.down,
        )
        self.up = to_raw_response_wrapper(
            card.up,
        )


class AsyncCardResourceWithRawResponse:
    def __init__(self, card: AsyncCardResource) -> None:
        self._card = card

        self.down = async_to_raw_response_wrapper(
            card.down,
        )
        self.up = async_to_raw_response_wrapper(
            card.up,
        )


class CardResourceWithStreamingResponse:
    def __init__(self, card: CardResource) -> None:
        self._card = card

        self.down = to_streamed_response_wrapper(
            card.down,
        )
        self.up = to_streamed_response_wrapper(
            card.up,
        )


class AsyncCardResourceWithStreamingResponse:
    def __init__(self, card: AsyncCardResource) -> None:
        self._card = card

        self.down = async_to_streamed_response_wrapper(
            card.down,
        )
        self.up = async_to_streamed_response_wrapper(
            card.up,
        )
