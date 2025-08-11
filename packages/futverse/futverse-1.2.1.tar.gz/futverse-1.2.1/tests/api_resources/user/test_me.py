# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from fv import Fv, AsyncFv
from tests.utils import assert_matches_type
from fv.types.user import User

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestMe:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: Fv) -> None:
        me = client.user.me.retrieve()
        assert_matches_type(User, me, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_with_all_params(self, client: Fv) -> None:
        me = client.user.me.retrieve(
            accept_language="accept-language",
        )
        assert_matches_type(User, me, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: Fv) -> None:
        response = client.user.me.with_raw_response.retrieve()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        me = response.parse()
        assert_matches_type(User, me, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: Fv) -> None:
        with client.user.me.with_streaming_response.retrieve() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            me = response.parse()
            assert_matches_type(User, me, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_update_language(self, client: Fv) -> None:
        me = client.user.me.update_language(
            language="pt-BR",
        )
        assert_matches_type(User, me, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update_language_with_all_params(self, client: Fv) -> None:
        me = client.user.me.update_language(
            language="pt-BR",
            accept_language="accept-language",
        )
        assert_matches_type(User, me, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update_language(self, client: Fv) -> None:
        response = client.user.me.with_raw_response.update_language(
            language="pt-BR",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        me = response.parse()
        assert_matches_type(User, me, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update_language(self, client: Fv) -> None:
        with client.user.me.with_streaming_response.update_language(
            language="pt-BR",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            me = response.parse()
            assert_matches_type(User, me, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncMe:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncFv) -> None:
        me = await async_client.user.me.retrieve()
        assert_matches_type(User, me, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncFv) -> None:
        me = await async_client.user.me.retrieve(
            accept_language="accept-language",
        )
        assert_matches_type(User, me, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncFv) -> None:
        response = await async_client.user.me.with_raw_response.retrieve()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        me = await response.parse()
        assert_matches_type(User, me, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncFv) -> None:
        async with async_client.user.me.with_streaming_response.retrieve() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            me = await response.parse()
            assert_matches_type(User, me, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_language(self, async_client: AsyncFv) -> None:
        me = await async_client.user.me.update_language(
            language="pt-BR",
        )
        assert_matches_type(User, me, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_language_with_all_params(self, async_client: AsyncFv) -> None:
        me = await async_client.user.me.update_language(
            language="pt-BR",
            accept_language="accept-language",
        )
        assert_matches_type(User, me, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update_language(self, async_client: AsyncFv) -> None:
        response = await async_client.user.me.with_raw_response.update_language(
            language="pt-BR",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        me = await response.parse()
        assert_matches_type(User, me, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update_language(self, async_client: AsyncFv) -> None:
        async with async_client.user.me.with_streaming_response.update_language(
            language="pt-BR",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            me = await response.parse()
            assert_matches_type(User, me, path=["response"])

        assert cast(Any, response.is_closed) is True
