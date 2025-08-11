# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from fv import Fv, AsyncFv
from fv.types import UserinventoryRedeemResponse
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestUserinventory:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_redeem(self, client: Fv) -> None:
        userinventory = client.userinventory.redeem(
            userinventory_id=0,
        )
        assert_matches_type(UserinventoryRedeemResponse, userinventory, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_redeem_with_all_params(self, client: Fv) -> None:
        userinventory = client.userinventory.redeem(
            userinventory_id=0,
            accept_language="accept-language",
        )
        assert_matches_type(UserinventoryRedeemResponse, userinventory, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_redeem(self, client: Fv) -> None:
        response = client.userinventory.with_raw_response.redeem(
            userinventory_id=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        userinventory = response.parse()
        assert_matches_type(UserinventoryRedeemResponse, userinventory, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_redeem(self, client: Fv) -> None:
        with client.userinventory.with_streaming_response.redeem(
            userinventory_id=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            userinventory = response.parse()
            assert_matches_type(UserinventoryRedeemResponse, userinventory, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncUserinventory:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_redeem(self, async_client: AsyncFv) -> None:
        userinventory = await async_client.userinventory.redeem(
            userinventory_id=0,
        )
        assert_matches_type(UserinventoryRedeemResponse, userinventory, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_redeem_with_all_params(self, async_client: AsyncFv) -> None:
        userinventory = await async_client.userinventory.redeem(
            userinventory_id=0,
            accept_language="accept-language",
        )
        assert_matches_type(UserinventoryRedeemResponse, userinventory, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_redeem(self, async_client: AsyncFv) -> None:
        response = await async_client.userinventory.with_raw_response.redeem(
            userinventory_id=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        userinventory = await response.parse()
        assert_matches_type(UserinventoryRedeemResponse, userinventory, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_redeem(self, async_client: AsyncFv) -> None:
        async with async_client.userinventory.with_streaming_response.redeem(
            userinventory_id=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            userinventory = await response.parse()
            assert_matches_type(UserinventoryRedeemResponse, userinventory, path=["response"])

        assert cast(Any, response.is_closed) is True
