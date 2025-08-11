# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import strip_not_given
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.match_join_ranked_response import MatchJoinRankedResponse

__all__ = ["MatchResource", "AsyncMatchResource"]


class MatchResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> MatchResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/victorgabrieldeon/fv-api#accessing-raw-response-data-eg-headers
        """
        return MatchResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> MatchResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/victorgabrieldeon/fv-api#with_streaming_response
        """
        return MatchResourceWithStreamingResponse(self)

    def join_ranked(
        self,
        *,
        accept_language: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MatchJoinRankedResponse:
        """
        Entra na fila de ranked.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {**strip_not_given({"accept-language": accept_language}), **(extra_headers or {})}
        return self._post(
            "/match/ranked",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MatchJoinRankedResponse,
        )


class AsyncMatchResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncMatchResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/victorgabrieldeon/fv-api#accessing-raw-response-data-eg-headers
        """
        return AsyncMatchResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncMatchResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/victorgabrieldeon/fv-api#with_streaming_response
        """
        return AsyncMatchResourceWithStreamingResponse(self)

    async def join_ranked(
        self,
        *,
        accept_language: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MatchJoinRankedResponse:
        """
        Entra na fila de ranked.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {**strip_not_given({"accept-language": accept_language}), **(extra_headers or {})}
        return await self._post(
            "/match/ranked",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MatchJoinRankedResponse,
        )


class MatchResourceWithRawResponse:
    def __init__(self, match: MatchResource) -> None:
        self._match = match

        self.join_ranked = to_raw_response_wrapper(
            match.join_ranked,
        )


class AsyncMatchResourceWithRawResponse:
    def __init__(self, match: AsyncMatchResource) -> None:
        self._match = match

        self.join_ranked = async_to_raw_response_wrapper(
            match.join_ranked,
        )


class MatchResourceWithStreamingResponse:
    def __init__(self, match: MatchResource) -> None:
        self._match = match

        self.join_ranked = to_streamed_response_wrapper(
            match.join_ranked,
        )


class AsyncMatchResourceWithStreamingResponse:
    def __init__(self, match: AsyncMatchResource) -> None:
        self._match = match

        self.join_ranked = async_to_streamed_response_wrapper(
            match.join_ranked,
        )
