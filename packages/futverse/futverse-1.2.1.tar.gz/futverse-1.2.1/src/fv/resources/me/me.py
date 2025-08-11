# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .card import (
    CardResource,
    AsyncCardResource,
    CardResourceWithRawResponse,
    AsyncCardResourceWithRawResponse,
    CardResourceWithStreamingResponse,
    AsyncCardResourceWithStreamingResponse,
)
from ..._compat import cached_property
from .pack.pack import (
    PackResource,
    AsyncPackResource,
    PackResourceWithRawResponse,
    AsyncPackResourceWithRawResponse,
    PackResourceWithStreamingResponse,
    AsyncPackResourceWithStreamingResponse,
)
from ..._resource import SyncAPIResource, AsyncAPIResource

__all__ = ["MeResource", "AsyncMeResource"]


class MeResource(SyncAPIResource):
    @cached_property
    def card(self) -> CardResource:
        return CardResource(self._client)

    @cached_property
    def pack(self) -> PackResource:
        return PackResource(self._client)

    @cached_property
    def with_raw_response(self) -> MeResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/victorgabrieldeon/fv-api#accessing-raw-response-data-eg-headers
        """
        return MeResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> MeResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/victorgabrieldeon/fv-api#with_streaming_response
        """
        return MeResourceWithStreamingResponse(self)


class AsyncMeResource(AsyncAPIResource):
    @cached_property
    def card(self) -> AsyncCardResource:
        return AsyncCardResource(self._client)

    @cached_property
    def pack(self) -> AsyncPackResource:
        return AsyncPackResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncMeResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/victorgabrieldeon/fv-api#accessing-raw-response-data-eg-headers
        """
        return AsyncMeResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncMeResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/victorgabrieldeon/fv-api#with_streaming_response
        """
        return AsyncMeResourceWithStreamingResponse(self)


class MeResourceWithRawResponse:
    def __init__(self, me: MeResource) -> None:
        self._me = me

    @cached_property
    def card(self) -> CardResourceWithRawResponse:
        return CardResourceWithRawResponse(self._me.card)

    @cached_property
    def pack(self) -> PackResourceWithRawResponse:
        return PackResourceWithRawResponse(self._me.pack)


class AsyncMeResourceWithRawResponse:
    def __init__(self, me: AsyncMeResource) -> None:
        self._me = me

    @cached_property
    def card(self) -> AsyncCardResourceWithRawResponse:
        return AsyncCardResourceWithRawResponse(self._me.card)

    @cached_property
    def pack(self) -> AsyncPackResourceWithRawResponse:
        return AsyncPackResourceWithRawResponse(self._me.pack)


class MeResourceWithStreamingResponse:
    def __init__(self, me: MeResource) -> None:
        self._me = me

    @cached_property
    def card(self) -> CardResourceWithStreamingResponse:
        return CardResourceWithStreamingResponse(self._me.card)

    @cached_property
    def pack(self) -> PackResourceWithStreamingResponse:
        return PackResourceWithStreamingResponse(self._me.pack)


class AsyncMeResourceWithStreamingResponse:
    def __init__(self, me: AsyncMeResource) -> None:
        self._me = me

    @cached_property
    def card(self) -> AsyncCardResourceWithStreamingResponse:
        return AsyncCardResourceWithStreamingResponse(self._me.card)

    @cached_property
    def pack(self) -> AsyncPackResourceWithStreamingResponse:
        return AsyncPackResourceWithStreamingResponse(self._me.pack)
