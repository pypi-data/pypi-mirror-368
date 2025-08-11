# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
from ..._utils import maybe_transform, strip_not_given, async_maybe_transform
from ..._compat import cached_property
from ...types.me import card_hire_params, card_sell_params, card_update_params
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.me.card_hire_response import CardHireResponse
from ...types.me.card_sell_response import CardSellResponse

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

    def update(
        self,
        usercard_id: int,
        *,
        favorite: Optional[bool] | NotGiven = NOT_GIVEN,
        accept_language: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Atualiza um card de um usuário.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        extra_headers = {**strip_not_given({"accept-language": accept_language}), **(extra_headers or {})}
        return self._put(
            f"/@me/card/{usercard_id}",
            body=maybe_transform({"favorite": favorite}, card_update_params.CardUpdateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def hire(
        self,
        *,
        card_id: str,
        accept_language: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CardHireResponse:
        """
        Contrata um card para um usuário.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {**strip_not_given({"accept-language": accept_language}), **(extra_headers or {})}
        return self._post(
            "/@me/card/hire",
            body=maybe_transform({"card_id": card_id}, card_hire_params.CardHireParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CardHireResponse,
        )

    def sell(
        self,
        *,
        cards_ids: Iterable[int],
        accept_language: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CardSellResponse:
        """
        Vende cards de um usuário.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {**strip_not_given({"accept-language": accept_language}), **(extra_headers or {})}
        return self._post(
            "/@me/card/sell",
            body=maybe_transform({"cards_ids": cards_ids}, card_sell_params.CardSellParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CardSellResponse,
        )

    def set_captain(
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
        Atualiza um card de um usuário.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        extra_headers = {**strip_not_given({"accept-language": accept_language}), **(extra_headers or {})}
        return self._patch(
            f"/@me/card/{usercard_id}/captain",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
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

    async def update(
        self,
        usercard_id: int,
        *,
        favorite: Optional[bool] | NotGiven = NOT_GIVEN,
        accept_language: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Atualiza um card de um usuário.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        extra_headers = {**strip_not_given({"accept-language": accept_language}), **(extra_headers or {})}
        return await self._put(
            f"/@me/card/{usercard_id}",
            body=await async_maybe_transform({"favorite": favorite}, card_update_params.CardUpdateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def hire(
        self,
        *,
        card_id: str,
        accept_language: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CardHireResponse:
        """
        Contrata um card para um usuário.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {**strip_not_given({"accept-language": accept_language}), **(extra_headers or {})}
        return await self._post(
            "/@me/card/hire",
            body=await async_maybe_transform({"card_id": card_id}, card_hire_params.CardHireParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CardHireResponse,
        )

    async def sell(
        self,
        *,
        cards_ids: Iterable[int],
        accept_language: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CardSellResponse:
        """
        Vende cards de um usuário.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {**strip_not_given({"accept-language": accept_language}), **(extra_headers or {})}
        return await self._post(
            "/@me/card/sell",
            body=await async_maybe_transform({"cards_ids": cards_ids}, card_sell_params.CardSellParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CardSellResponse,
        )

    async def set_captain(
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
        Atualiza um card de um usuário.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        extra_headers = {**strip_not_given({"accept-language": accept_language}), **(extra_headers or {})}
        return await self._patch(
            f"/@me/card/{usercard_id}/captain",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class CardResourceWithRawResponse:
    def __init__(self, card: CardResource) -> None:
        self._card = card

        self.update = to_raw_response_wrapper(
            card.update,
        )
        self.hire = to_raw_response_wrapper(
            card.hire,
        )
        self.sell = to_raw_response_wrapper(
            card.sell,
        )
        self.set_captain = to_raw_response_wrapper(
            card.set_captain,
        )


class AsyncCardResourceWithRawResponse:
    def __init__(self, card: AsyncCardResource) -> None:
        self._card = card

        self.update = async_to_raw_response_wrapper(
            card.update,
        )
        self.hire = async_to_raw_response_wrapper(
            card.hire,
        )
        self.sell = async_to_raw_response_wrapper(
            card.sell,
        )
        self.set_captain = async_to_raw_response_wrapper(
            card.set_captain,
        )


class CardResourceWithStreamingResponse:
    def __init__(self, card: CardResource) -> None:
        self._card = card

        self.update = to_streamed_response_wrapper(
            card.update,
        )
        self.hire = to_streamed_response_wrapper(
            card.hire,
        )
        self.sell = to_streamed_response_wrapper(
            card.sell,
        )
        self.set_captain = to_streamed_response_wrapper(
            card.set_captain,
        )


class AsyncCardResourceWithStreamingResponse:
    def __init__(self, card: AsyncCardResource) -> None:
        self._card = card

        self.update = async_to_streamed_response_wrapper(
            card.update,
        )
        self.hire = async_to_streamed_response_wrapper(
            card.hire,
        )
        self.sell = async_to_streamed_response_wrapper(
            card.sell,
        )
        self.set_captain = async_to_streamed_response_wrapper(
            card.set_captain,
        )
