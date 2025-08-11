# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from fv import Fv, AsyncFv

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestCard:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_down(self, client: Fv) -> None:
        card = client.lineup.card.down(
            usercard_id=0,
        )
        assert card is None

    @pytest.mark.skip()
    @parametrize
    def test_method_down_with_all_params(self, client: Fv) -> None:
        card = client.lineup.card.down(
            usercard_id=0,
            accept_language="accept-language",
        )
        assert card is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_down(self, client: Fv) -> None:
        response = client.lineup.card.with_raw_response.down(
            usercard_id=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        card = response.parse()
        assert card is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_down(self, client: Fv) -> None:
        with client.lineup.card.with_streaming_response.down(
            usercard_id=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            card = response.parse()
            assert card is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_up(self, client: Fv) -> None:
        card = client.lineup.card.up(
            usercard_id=0,
            position="GOL",
        )
        assert card is None

    @pytest.mark.skip()
    @parametrize
    def test_method_up_with_all_params(self, client: Fv) -> None:
        card = client.lineup.card.up(
            usercard_id=0,
            position="GOL",
            accept_language="accept-language",
        )
        assert card is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_up(self, client: Fv) -> None:
        response = client.lineup.card.with_raw_response.up(
            usercard_id=0,
            position="GOL",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        card = response.parse()
        assert card is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_up(self, client: Fv) -> None:
        with client.lineup.card.with_streaming_response.up(
            usercard_id=0,
            position="GOL",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            card = response.parse()
            assert card is None

        assert cast(Any, response.is_closed) is True


class TestAsyncCard:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_down(self, async_client: AsyncFv) -> None:
        card = await async_client.lineup.card.down(
            usercard_id=0,
        )
        assert card is None

    @pytest.mark.skip()
    @parametrize
    async def test_method_down_with_all_params(self, async_client: AsyncFv) -> None:
        card = await async_client.lineup.card.down(
            usercard_id=0,
            accept_language="accept-language",
        )
        assert card is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_down(self, async_client: AsyncFv) -> None:
        response = await async_client.lineup.card.with_raw_response.down(
            usercard_id=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        card = await response.parse()
        assert card is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_down(self, async_client: AsyncFv) -> None:
        async with async_client.lineup.card.with_streaming_response.down(
            usercard_id=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            card = await response.parse()
            assert card is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_up(self, async_client: AsyncFv) -> None:
        card = await async_client.lineup.card.up(
            usercard_id=0,
            position="GOL",
        )
        assert card is None

    @pytest.mark.skip()
    @parametrize
    async def test_method_up_with_all_params(self, async_client: AsyncFv) -> None:
        card = await async_client.lineup.card.up(
            usercard_id=0,
            position="GOL",
            accept_language="accept-language",
        )
        assert card is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_up(self, async_client: AsyncFv) -> None:
        response = await async_client.lineup.card.with_raw_response.up(
            usercard_id=0,
            position="GOL",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        card = await response.parse()
        assert card is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_up(self, async_client: AsyncFv) -> None:
        async with async_client.lineup.card.with_streaming_response.up(
            usercard_id=0,
            position="GOL",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            card = await response.parse()
            assert card is None

        assert cast(Any, response.is_closed) is True
