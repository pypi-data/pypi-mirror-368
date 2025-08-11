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
from ..types.userinventory_redeem_response import UserinventoryRedeemResponse

__all__ = ["UserinventoryResource", "AsyncUserinventoryResource"]


class UserinventoryResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> UserinventoryResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/victorgabrieldeon/fv-api#accessing-raw-response-data-eg-headers
        """
        return UserinventoryResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> UserinventoryResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/victorgabrieldeon/fv-api#with_streaming_response
        """
        return UserinventoryResourceWithStreamingResponse(self)

    def redeem(
        self,
        userinventory_id: int,
        *,
        accept_language: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UserinventoryRedeemResponse:
        """
        Resgata um item do inventário do usuário.

            - **userinventory_id**: ID do item do inventário do usuário.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {**strip_not_given({"accept-language": accept_language}), **(extra_headers or {})}
        return self._post(
            f"/userinventory/redeem/{userinventory_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserinventoryRedeemResponse,
        )


class AsyncUserinventoryResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncUserinventoryResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/victorgabrieldeon/fv-api#accessing-raw-response-data-eg-headers
        """
        return AsyncUserinventoryResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncUserinventoryResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/victorgabrieldeon/fv-api#with_streaming_response
        """
        return AsyncUserinventoryResourceWithStreamingResponse(self)

    async def redeem(
        self,
        userinventory_id: int,
        *,
        accept_language: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UserinventoryRedeemResponse:
        """
        Resgata um item do inventário do usuário.

            - **userinventory_id**: ID do item do inventário do usuário.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {**strip_not_given({"accept-language": accept_language}), **(extra_headers or {})}
        return await self._post(
            f"/userinventory/redeem/{userinventory_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserinventoryRedeemResponse,
        )


class UserinventoryResourceWithRawResponse:
    def __init__(self, userinventory: UserinventoryResource) -> None:
        self._userinventory = userinventory

        self.redeem = to_raw_response_wrapper(
            userinventory.redeem,
        )


class AsyncUserinventoryResourceWithRawResponse:
    def __init__(self, userinventory: AsyncUserinventoryResource) -> None:
        self._userinventory = userinventory

        self.redeem = async_to_raw_response_wrapper(
            userinventory.redeem,
        )


class UserinventoryResourceWithStreamingResponse:
    def __init__(self, userinventory: UserinventoryResource) -> None:
        self._userinventory = userinventory

        self.redeem = to_streamed_response_wrapper(
            userinventory.redeem,
        )


class AsyncUserinventoryResourceWithStreamingResponse:
    def __init__(self, userinventory: AsyncUserinventoryResource) -> None:
        self._userinventory = userinventory

        self.redeem = async_to_streamed_response_wrapper(
            userinventory.redeem,
        )
