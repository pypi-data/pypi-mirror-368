# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from fv import Fv, AsyncFv
from tests.utils import assert_matches_type
from fv.types.me.pack import ConfigRetrieveResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestConfig:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: Fv) -> None:
        config = client.me.pack.config.retrieve()
        assert_matches_type(ConfigRetrieveResponse, config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_with_all_params(self, client: Fv) -> None:
        config = client.me.pack.config.retrieve(
            accept_language="accept-language",
        )
        assert_matches_type(ConfigRetrieveResponse, config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: Fv) -> None:
        response = client.me.pack.config.with_raw_response.retrieve()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        config = response.parse()
        assert_matches_type(ConfigRetrieveResponse, config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: Fv) -> None:
        with client.me.pack.config.with_streaming_response.retrieve() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            config = response.parse()
            assert_matches_type(ConfigRetrieveResponse, config, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_update(self, client: Fv) -> None:
        config = client.me.pack.config.update()
        assert config is None

    @pytest.mark.skip()
    @parametrize
    def test_method_update_with_all_params(self, client: Fv) -> None:
        config = client.me.pack.config.update(
            auto_sell_cards_repeated=True,
            auto_sell_less_than=0,
            accept_language="accept-language",
        )
        assert config is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update(self, client: Fv) -> None:
        response = client.me.pack.config.with_raw_response.update()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        config = response.parse()
        assert config is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update(self, client: Fv) -> None:
        with client.me.pack.config.with_streaming_response.update() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            config = response.parse()
            assert config is None

        assert cast(Any, response.is_closed) is True


class TestAsyncConfig:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncFv) -> None:
        config = await async_client.me.pack.config.retrieve()
        assert_matches_type(ConfigRetrieveResponse, config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncFv) -> None:
        config = await async_client.me.pack.config.retrieve(
            accept_language="accept-language",
        )
        assert_matches_type(ConfigRetrieveResponse, config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncFv) -> None:
        response = await async_client.me.pack.config.with_raw_response.retrieve()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        config = await response.parse()
        assert_matches_type(ConfigRetrieveResponse, config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncFv) -> None:
        async with async_client.me.pack.config.with_streaming_response.retrieve() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            config = await response.parse()
            assert_matches_type(ConfigRetrieveResponse, config, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_update(self, async_client: AsyncFv) -> None:
        config = await async_client.me.pack.config.update()
        assert config is None

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncFv) -> None:
        config = await async_client.me.pack.config.update(
            auto_sell_cards_repeated=True,
            auto_sell_less_than=0,
            accept_language="accept-language",
        )
        assert config is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncFv) -> None:
        response = await async_client.me.pack.config.with_raw_response.update()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        config = await response.parse()
        assert config is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncFv) -> None:
        async with async_client.me.pack.config.with_streaming_response.update() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            config = await response.parse()
            assert config is None

        assert cast(Any, response.is_closed) is True
