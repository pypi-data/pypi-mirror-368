# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from fv import Fv, AsyncFv
from fv.types import MatchJoinRankedResponse
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestMatch:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_join_ranked(self, client: Fv) -> None:
        match = client.match.join_ranked()
        assert_matches_type(MatchJoinRankedResponse, match, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_join_ranked_with_all_params(self, client: Fv) -> None:
        match = client.match.join_ranked(
            accept_language="accept-language",
        )
        assert_matches_type(MatchJoinRankedResponse, match, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_join_ranked(self, client: Fv) -> None:
        response = client.match.with_raw_response.join_ranked()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        match = response.parse()
        assert_matches_type(MatchJoinRankedResponse, match, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_join_ranked(self, client: Fv) -> None:
        with client.match.with_streaming_response.join_ranked() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            match = response.parse()
            assert_matches_type(MatchJoinRankedResponse, match, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncMatch:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_join_ranked(self, async_client: AsyncFv) -> None:
        match = await async_client.match.join_ranked()
        assert_matches_type(MatchJoinRankedResponse, match, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_join_ranked_with_all_params(self, async_client: AsyncFv) -> None:
        match = await async_client.match.join_ranked(
            accept_language="accept-language",
        )
        assert_matches_type(MatchJoinRankedResponse, match, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_join_ranked(self, async_client: AsyncFv) -> None:
        response = await async_client.match.with_raw_response.join_ranked()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        match = await response.parse()
        assert_matches_type(MatchJoinRankedResponse, match, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_join_ranked(self, async_client: AsyncFv) -> None:
        async with async_client.match.with_streaming_response.join_ranked() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            match = await response.parse()
            assert_matches_type(MatchJoinRankedResponse, match, path=["response"])

        assert cast(Any, response.is_closed) is True
