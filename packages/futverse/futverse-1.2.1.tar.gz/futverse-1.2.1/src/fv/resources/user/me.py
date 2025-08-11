# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import maybe_transform, strip_not_given, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...types.user import me_update_language_params
from ..._base_client import make_request_options
from ...types.user.user import User

__all__ = ["MeResource", "AsyncMeResource"]


class MeResource(SyncAPIResource):
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

    def retrieve(
        self,
        *,
        accept_language: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> User:
        """
        Obter informações do usuário atual.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {**strip_not_given({"accept-language": accept_language}), **(extra_headers or {})}
        return self._get(
            "/user/@me",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=User,
        )

    def update_language(
        self,
        *,
        language: Literal["pt-BR", "en-US", "es-ES"],
        accept_language: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> User:
        """
        Alterar o idioma do usuário.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {**strip_not_given({"accept-language": accept_language}), **(extra_headers or {})}
        return self._patch(
            "/user/@me/language",
            body=maybe_transform({"language": language}, me_update_language_params.MeUpdateLanguageParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=User,
        )


class AsyncMeResource(AsyncAPIResource):
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

    async def retrieve(
        self,
        *,
        accept_language: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> User:
        """
        Obter informações do usuário atual.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {**strip_not_given({"accept-language": accept_language}), **(extra_headers or {})}
        return await self._get(
            "/user/@me",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=User,
        )

    async def update_language(
        self,
        *,
        language: Literal["pt-BR", "en-US", "es-ES"],
        accept_language: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> User:
        """
        Alterar o idioma do usuário.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {**strip_not_given({"accept-language": accept_language}), **(extra_headers or {})}
        return await self._patch(
            "/user/@me/language",
            body=await async_maybe_transform({"language": language}, me_update_language_params.MeUpdateLanguageParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=User,
        )


class MeResourceWithRawResponse:
    def __init__(self, me: MeResource) -> None:
        self._me = me

        self.retrieve = to_raw_response_wrapper(
            me.retrieve,
        )
        self.update_language = to_raw_response_wrapper(
            me.update_language,
        )


class AsyncMeResourceWithRawResponse:
    def __init__(self, me: AsyncMeResource) -> None:
        self._me = me

        self.retrieve = async_to_raw_response_wrapper(
            me.retrieve,
        )
        self.update_language = async_to_raw_response_wrapper(
            me.update_language,
        )


class MeResourceWithStreamingResponse:
    def __init__(self, me: MeResource) -> None:
        self._me = me

        self.retrieve = to_streamed_response_wrapper(
            me.retrieve,
        )
        self.update_language = to_streamed_response_wrapper(
            me.update_language,
        )


class AsyncMeResourceWithStreamingResponse:
    def __init__(self, me: AsyncMeResource) -> None:
        self._me = me

        self.retrieve = async_to_streamed_response_wrapper(
            me.retrieve,
        )
        self.update_language = async_to_streamed_response_wrapper(
            me.update_language,
        )
