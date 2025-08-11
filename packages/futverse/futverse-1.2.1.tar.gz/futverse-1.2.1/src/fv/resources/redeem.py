# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import redeem_redeem_code_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import maybe_transform, strip_not_given, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.redeem_redeem_code_response import RedeemRedeemCodeResponse

__all__ = ["RedeemResource", "AsyncRedeemResource"]


class RedeemResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> RedeemResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/victorgabrieldeon/fv-api#accessing-raw-response-data-eg-headers
        """
        return RedeemResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RedeemResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/victorgabrieldeon/fv-api#with_streaming_response
        """
        return RedeemResourceWithStreamingResponse(self)

    def redeem_code(
        self,
        *,
        code: str,
        accept_language: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RedeemRedeemCodeResponse:
        """
        Resgata um código.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {**strip_not_given({"accept-language": accept_language}), **(extra_headers or {})}
        return self._post(
            "/redeem",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"code": code}, redeem_redeem_code_params.RedeemRedeemCodeParams),
            ),
            cast_to=RedeemRedeemCodeResponse,
        )


class AsyncRedeemResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncRedeemResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/victorgabrieldeon/fv-api#accessing-raw-response-data-eg-headers
        """
        return AsyncRedeemResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRedeemResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/victorgabrieldeon/fv-api#with_streaming_response
        """
        return AsyncRedeemResourceWithStreamingResponse(self)

    async def redeem_code(
        self,
        *,
        code: str,
        accept_language: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RedeemRedeemCodeResponse:
        """
        Resgata um código.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {**strip_not_given({"accept-language": accept_language}), **(extra_headers or {})}
        return await self._post(
            "/redeem",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"code": code}, redeem_redeem_code_params.RedeemRedeemCodeParams),
            ),
            cast_to=RedeemRedeemCodeResponse,
        )


class RedeemResourceWithRawResponse:
    def __init__(self, redeem: RedeemResource) -> None:
        self._redeem = redeem

        self.redeem_code = to_raw_response_wrapper(
            redeem.redeem_code,
        )


class AsyncRedeemResourceWithRawResponse:
    def __init__(self, redeem: AsyncRedeemResource) -> None:
        self._redeem = redeem

        self.redeem_code = async_to_raw_response_wrapper(
            redeem.redeem_code,
        )


class RedeemResourceWithStreamingResponse:
    def __init__(self, redeem: RedeemResource) -> None:
        self._redeem = redeem

        self.redeem_code = to_streamed_response_wrapper(
            redeem.redeem_code,
        )


class AsyncRedeemResourceWithStreamingResponse:
    def __init__(self, redeem: AsyncRedeemResource) -> None:
        self._redeem = redeem

        self.redeem_code = async_to_streamed_response_wrapper(
            redeem.redeem_code,
        )
