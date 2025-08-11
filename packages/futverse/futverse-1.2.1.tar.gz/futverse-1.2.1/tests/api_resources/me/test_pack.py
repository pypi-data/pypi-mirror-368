# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from fv import Fv, AsyncFv
from fv.types.me import PackBuyResponse, PackOpenResponse
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestPack:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_buy(self, client: Fv) -> None:
        pack = client.me.pack.buy(
            pack_id="pack_id",
        )
        assert_matches_type(PackBuyResponse, pack, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_buy_with_all_params(self, client: Fv) -> None:
        pack = client.me.pack.buy(
            pack_id="pack_id",
            accept_language="accept-language",
        )
        assert_matches_type(PackBuyResponse, pack, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_buy(self, client: Fv) -> None:
        response = client.me.pack.with_raw_response.buy(
            pack_id="pack_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        pack = response.parse()
        assert_matches_type(PackBuyResponse, pack, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_buy(self, client: Fv) -> None:
        with client.me.pack.with_streaming_response.buy(
            pack_id="pack_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            pack = response.parse()
            assert_matches_type(PackBuyResponse, pack, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_buy(self, client: Fv) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `pack_id` but received ''"):
            client.me.pack.with_raw_response.buy(
                pack_id="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_open(self, client: Fv) -> None:
        pack = client.me.pack.open(
            pack_id="pack_id",
        )
        assert_matches_type(PackOpenResponse, pack, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_open_with_all_params(self, client: Fv) -> None:
        pack = client.me.pack.open(
            pack_id="pack_id",
            accept_language="accept-language",
        )
        assert_matches_type(PackOpenResponse, pack, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_open(self, client: Fv) -> None:
        response = client.me.pack.with_raw_response.open(
            pack_id="pack_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        pack = response.parse()
        assert_matches_type(PackOpenResponse, pack, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_open(self, client: Fv) -> None:
        with client.me.pack.with_streaming_response.open(
            pack_id="pack_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            pack = response.parse()
            assert_matches_type(PackOpenResponse, pack, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_open(self, client: Fv) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `pack_id` but received ''"):
            client.me.pack.with_raw_response.open(
                pack_id="",
            )


class TestAsyncPack:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_buy(self, async_client: AsyncFv) -> None:
        pack = await async_client.me.pack.buy(
            pack_id="pack_id",
        )
        assert_matches_type(PackBuyResponse, pack, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_buy_with_all_params(self, async_client: AsyncFv) -> None:
        pack = await async_client.me.pack.buy(
            pack_id="pack_id",
            accept_language="accept-language",
        )
        assert_matches_type(PackBuyResponse, pack, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_buy(self, async_client: AsyncFv) -> None:
        response = await async_client.me.pack.with_raw_response.buy(
            pack_id="pack_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        pack = await response.parse()
        assert_matches_type(PackBuyResponse, pack, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_buy(self, async_client: AsyncFv) -> None:
        async with async_client.me.pack.with_streaming_response.buy(
            pack_id="pack_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            pack = await response.parse()
            assert_matches_type(PackBuyResponse, pack, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_buy(self, async_client: AsyncFv) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `pack_id` but received ''"):
            await async_client.me.pack.with_raw_response.buy(
                pack_id="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_open(self, async_client: AsyncFv) -> None:
        pack = await async_client.me.pack.open(
            pack_id="pack_id",
        )
        assert_matches_type(PackOpenResponse, pack, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_open_with_all_params(self, async_client: AsyncFv) -> None:
        pack = await async_client.me.pack.open(
            pack_id="pack_id",
            accept_language="accept-language",
        )
        assert_matches_type(PackOpenResponse, pack, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_open(self, async_client: AsyncFv) -> None:
        response = await async_client.me.pack.with_raw_response.open(
            pack_id="pack_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        pack = await response.parse()
        assert_matches_type(PackOpenResponse, pack, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_open(self, async_client: AsyncFv) -> None:
        async with async_client.me.pack.with_streaming_response.open(
            pack_id="pack_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            pack = await response.parse()
            assert_matches_type(PackOpenResponse, pack, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_open(self, async_client: AsyncFv) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `pack_id` but received ''"):
            await async_client.me.pack.with_raw_response.open(
                pack_id="",
            )
