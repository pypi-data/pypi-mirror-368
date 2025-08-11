# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from fv import Fv, AsyncFv
from fv.types import RedeemRedeemCodeResponse
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestRedeem:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_redeem_code(self, client: Fv) -> None:
        redeem = client.redeem.redeem_code(
            code="code",
        )
        assert_matches_type(RedeemRedeemCodeResponse, redeem, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_redeem_code_with_all_params(self, client: Fv) -> None:
        redeem = client.redeem.redeem_code(
            code="code",
            accept_language="accept-language",
        )
        assert_matches_type(RedeemRedeemCodeResponse, redeem, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_redeem_code(self, client: Fv) -> None:
        response = client.redeem.with_raw_response.redeem_code(
            code="code",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        redeem = response.parse()
        assert_matches_type(RedeemRedeemCodeResponse, redeem, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_redeem_code(self, client: Fv) -> None:
        with client.redeem.with_streaming_response.redeem_code(
            code="code",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            redeem = response.parse()
            assert_matches_type(RedeemRedeemCodeResponse, redeem, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncRedeem:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_redeem_code(self, async_client: AsyncFv) -> None:
        redeem = await async_client.redeem.redeem_code(
            code="code",
        )
        assert_matches_type(RedeemRedeemCodeResponse, redeem, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_redeem_code_with_all_params(self, async_client: AsyncFv) -> None:
        redeem = await async_client.redeem.redeem_code(
            code="code",
            accept_language="accept-language",
        )
        assert_matches_type(RedeemRedeemCodeResponse, redeem, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_redeem_code(self, async_client: AsyncFv) -> None:
        response = await async_client.redeem.with_raw_response.redeem_code(
            code="code",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        redeem = await response.parse()
        assert_matches_type(RedeemRedeemCodeResponse, redeem, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_redeem_code(self, async_client: AsyncFv) -> None:
        async with async_client.redeem.with_streaming_response.redeem_code(
            code="code",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            redeem = await response.parse()
            assert_matches_type(RedeemRedeemCodeResponse, redeem, path=["response"])

        assert cast(Any, response.is_closed) is True
