# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .card import (
    CardResource,
    AsyncCardResource,
    CardResourceWithRawResponse,
    AsyncCardResourceWithRawResponse,
    CardResourceWithStreamingResponse,
    AsyncCardResourceWithStreamingResponse,
)
from .image import (
    ImageResource,
    AsyncImageResource,
    ImageResourceWithRawResponse,
    AsyncImageResourceWithRawResponse,
    ImageResourceWithStreamingResponse,
    AsyncImageResourceWithStreamingResponse,
)
from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import strip_not_given
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.lineup_set_config_response import LineupSetConfigResponse

__all__ = ["LineupResource", "AsyncLineupResource"]


class LineupResource(SyncAPIResource):
    @cached_property
    def card(self) -> CardResource:
        return CardResource(self._client)

    @cached_property
    def image(self) -> ImageResource:
        return ImageResource(self._client)

    @cached_property
    def with_raw_response(self) -> LineupResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/victorgabrieldeon/fv-api#accessing-raw-response-data-eg-headers
        """
        return LineupResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> LineupResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/victorgabrieldeon/fv-api#with_streaming_response
        """
        return LineupResourceWithStreamingResponse(self)

    def set_config(
        self,
        formation_id: str,
        *,
        accept_language: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LineupSetConfigResponse:
        """
        Seta a formação do time titular.

        Se o usuário já tiver uma formação configurada, ela será atualizada.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not formation_id:
            raise ValueError(f"Expected a non-empty value for `formation_id` but received {formation_id!r}")
        extra_headers = {**strip_not_given({"accept-language": accept_language}), **(extra_headers or {})}
        return self._post(
            f"/lineup/formation/{formation_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LineupSetConfigResponse,
        )


class AsyncLineupResource(AsyncAPIResource):
    @cached_property
    def card(self) -> AsyncCardResource:
        return AsyncCardResource(self._client)

    @cached_property
    def image(self) -> AsyncImageResource:
        return AsyncImageResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncLineupResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/victorgabrieldeon/fv-api#accessing-raw-response-data-eg-headers
        """
        return AsyncLineupResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncLineupResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/victorgabrieldeon/fv-api#with_streaming_response
        """
        return AsyncLineupResourceWithStreamingResponse(self)

    async def set_config(
        self,
        formation_id: str,
        *,
        accept_language: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LineupSetConfigResponse:
        """
        Seta a formação do time titular.

        Se o usuário já tiver uma formação configurada, ela será atualizada.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not formation_id:
            raise ValueError(f"Expected a non-empty value for `formation_id` but received {formation_id!r}")
        extra_headers = {**strip_not_given({"accept-language": accept_language}), **(extra_headers or {})}
        return await self._post(
            f"/lineup/formation/{formation_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LineupSetConfigResponse,
        )


class LineupResourceWithRawResponse:
    def __init__(self, lineup: LineupResource) -> None:
        self._lineup = lineup

        self.set_config = to_raw_response_wrapper(
            lineup.set_config,
        )

    @cached_property
    def card(self) -> CardResourceWithRawResponse:
        return CardResourceWithRawResponse(self._lineup.card)

    @cached_property
    def image(self) -> ImageResourceWithRawResponse:
        return ImageResourceWithRawResponse(self._lineup.image)


class AsyncLineupResourceWithRawResponse:
    def __init__(self, lineup: AsyncLineupResource) -> None:
        self._lineup = lineup

        self.set_config = async_to_raw_response_wrapper(
            lineup.set_config,
        )

    @cached_property
    def card(self) -> AsyncCardResourceWithRawResponse:
        return AsyncCardResourceWithRawResponse(self._lineup.card)

    @cached_property
    def image(self) -> AsyncImageResourceWithRawResponse:
        return AsyncImageResourceWithRawResponse(self._lineup.image)


class LineupResourceWithStreamingResponse:
    def __init__(self, lineup: LineupResource) -> None:
        self._lineup = lineup

        self.set_config = to_streamed_response_wrapper(
            lineup.set_config,
        )

    @cached_property
    def card(self) -> CardResourceWithStreamingResponse:
        return CardResourceWithStreamingResponse(self._lineup.card)

    @cached_property
    def image(self) -> ImageResourceWithStreamingResponse:
        return ImageResourceWithStreamingResponse(self._lineup.image)


class AsyncLineupResourceWithStreamingResponse:
    def __init__(self, lineup: AsyncLineupResource) -> None:
        self._lineup = lineup

        self.set_config = async_to_streamed_response_wrapper(
            lineup.set_config,
        )

    @cached_property
    def card(self) -> AsyncCardResourceWithStreamingResponse:
        return AsyncCardResourceWithStreamingResponse(self._lineup.card)

    @cached_property
    def image(self) -> AsyncImageResourceWithStreamingResponse:
        return AsyncImageResourceWithStreamingResponse(self._lineup.image)
