# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from fv import Fv, AsyncFv
from fv.types import ProfitCalculateResponse
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestProfit:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_calculate(self, client: Fv) -> None:
        profit = client.profit.calculate()
        assert_matches_type(ProfitCalculateResponse, profit, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_calculate_with_all_params(self, client: Fv) -> None:
        profit = client.profit.calculate(
            accept_language="accept-language",
        )
        assert_matches_type(ProfitCalculateResponse, profit, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_calculate(self, client: Fv) -> None:
        response = client.profit.with_raw_response.calculate()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        profit = response.parse()
        assert_matches_type(ProfitCalculateResponse, profit, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_calculate(self, client: Fv) -> None:
        with client.profit.with_streaming_response.calculate() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            profit = response.parse()
            assert_matches_type(ProfitCalculateResponse, profit, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncProfit:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_calculate(self, async_client: AsyncFv) -> None:
        profit = await async_client.profit.calculate()
        assert_matches_type(ProfitCalculateResponse, profit, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_calculate_with_all_params(self, async_client: AsyncFv) -> None:
        profit = await async_client.profit.calculate(
            accept_language="accept-language",
        )
        assert_matches_type(ProfitCalculateResponse, profit, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_calculate(self, async_client: AsyncFv) -> None:
        response = await async_client.profit.with_raw_response.calculate()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        profit = await response.parse()
        assert_matches_type(ProfitCalculateResponse, profit, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_calculate(self, async_client: AsyncFv) -> None:
        async with async_client.profit.with_streaming_response.calculate() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            profit = await response.parse()
            assert_matches_type(ProfitCalculateResponse, profit, path=["response"])

        assert cast(Any, response.is_closed) is True
