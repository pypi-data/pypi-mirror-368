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
from ..types.profit_calculate_response import ProfitCalculateResponse

__all__ = ["ProfitResource", "AsyncProfitResource"]


class ProfitResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ProfitResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/victorgabrieldeon/fv-api#accessing-raw-response-data-eg-headers
        """
        return ProfitResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ProfitResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/victorgabrieldeon/fv-api#with_streaming_response
        """
        return ProfitResourceWithStreamingResponse(self)

    def calculate(
        self,
        *,
        accept_language: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ProfitCalculateResponse:
        """
        Retorna o lucro do usuário.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {**strip_not_given({"accept-language": accept_language}), **(extra_headers or {})}
        return self._post(
            "/profit",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ProfitCalculateResponse,
        )


class AsyncProfitResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncProfitResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/victorgabrieldeon/fv-api#accessing-raw-response-data-eg-headers
        """
        return AsyncProfitResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncProfitResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/victorgabrieldeon/fv-api#with_streaming_response
        """
        return AsyncProfitResourceWithStreamingResponse(self)

    async def calculate(
        self,
        *,
        accept_language: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ProfitCalculateResponse:
        """
        Retorna o lucro do usuário.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {**strip_not_given({"accept-language": accept_language}), **(extra_headers or {})}
        return await self._post(
            "/profit",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ProfitCalculateResponse,
        )


class ProfitResourceWithRawResponse:
    def __init__(self, profit: ProfitResource) -> None:
        self._profit = profit

        self.calculate = to_raw_response_wrapper(
            profit.calculate,
        )


class AsyncProfitResourceWithRawResponse:
    def __init__(self, profit: AsyncProfitResource) -> None:
        self._profit = profit

        self.calculate = async_to_raw_response_wrapper(
            profit.calculate,
        )


class ProfitResourceWithStreamingResponse:
    def __init__(self, profit: ProfitResource) -> None:
        self._profit = profit

        self.calculate = to_streamed_response_wrapper(
            profit.calculate,
        )


class AsyncProfitResourceWithStreamingResponse:
    def __init__(self, profit: AsyncProfitResource) -> None:
        self._profit = profit

        self.calculate = async_to_streamed_response_wrapper(
            profit.calculate,
        )
