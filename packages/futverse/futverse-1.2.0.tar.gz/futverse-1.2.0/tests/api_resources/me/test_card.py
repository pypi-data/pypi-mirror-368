# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from fv import Fv, AsyncFv
from fv.types.me import CardHireResponse, CardSellResponse
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestCard:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update(self, client: Fv) -> None:
        card = client.me.card.update(
            usercard_id=0,
        )
        assert card is None

    @pytest.mark.skip()
    @parametrize
    def test_method_update_with_all_params(self, client: Fv) -> None:
        card = client.me.card.update(
            usercard_id=0,
            favorite=True,
            accept_language="accept-language",
        )
        assert card is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update(self, client: Fv) -> None:
        response = client.me.card.with_raw_response.update(
            usercard_id=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        card = response.parse()
        assert card is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update(self, client: Fv) -> None:
        with client.me.card.with_streaming_response.update(
            usercard_id=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            card = response.parse()
            assert card is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_hire(self, client: Fv) -> None:
        card = client.me.card.hire(
            card_id="card_id",
        )
        assert_matches_type(CardHireResponse, card, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_hire_with_all_params(self, client: Fv) -> None:
        card = client.me.card.hire(
            card_id="card_id",
            accept_language="accept-language",
        )
        assert_matches_type(CardHireResponse, card, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_hire(self, client: Fv) -> None:
        response = client.me.card.with_raw_response.hire(
            card_id="card_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        card = response.parse()
        assert_matches_type(CardHireResponse, card, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_hire(self, client: Fv) -> None:
        with client.me.card.with_streaming_response.hire(
            card_id="card_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            card = response.parse()
            assert_matches_type(CardHireResponse, card, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_sell(self, client: Fv) -> None:
        card = client.me.card.sell(
            cards_ids=[0],
        )
        assert_matches_type(CardSellResponse, card, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_sell_with_all_params(self, client: Fv) -> None:
        card = client.me.card.sell(
            cards_ids=[0],
            accept_language="accept-language",
        )
        assert_matches_type(CardSellResponse, card, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_sell(self, client: Fv) -> None:
        response = client.me.card.with_raw_response.sell(
            cards_ids=[0],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        card = response.parse()
        assert_matches_type(CardSellResponse, card, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_sell(self, client: Fv) -> None:
        with client.me.card.with_streaming_response.sell(
            cards_ids=[0],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            card = response.parse()
            assert_matches_type(CardSellResponse, card, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_set_captain(self, client: Fv) -> None:
        card = client.me.card.set_captain(
            usercard_id=0,
        )
        assert card is None

    @pytest.mark.skip()
    @parametrize
    def test_method_set_captain_with_all_params(self, client: Fv) -> None:
        card = client.me.card.set_captain(
            usercard_id=0,
            accept_language="accept-language",
        )
        assert card is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_set_captain(self, client: Fv) -> None:
        response = client.me.card.with_raw_response.set_captain(
            usercard_id=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        card = response.parse()
        assert card is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_set_captain(self, client: Fv) -> None:
        with client.me.card.with_streaming_response.set_captain(
            usercard_id=0,
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
    async def test_method_update(self, async_client: AsyncFv) -> None:
        card = await async_client.me.card.update(
            usercard_id=0,
        )
        assert card is None

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncFv) -> None:
        card = await async_client.me.card.update(
            usercard_id=0,
            favorite=True,
            accept_language="accept-language",
        )
        assert card is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncFv) -> None:
        response = await async_client.me.card.with_raw_response.update(
            usercard_id=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        card = await response.parse()
        assert card is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncFv) -> None:
        async with async_client.me.card.with_streaming_response.update(
            usercard_id=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            card = await response.parse()
            assert card is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_hire(self, async_client: AsyncFv) -> None:
        card = await async_client.me.card.hire(
            card_id="card_id",
        )
        assert_matches_type(CardHireResponse, card, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_hire_with_all_params(self, async_client: AsyncFv) -> None:
        card = await async_client.me.card.hire(
            card_id="card_id",
            accept_language="accept-language",
        )
        assert_matches_type(CardHireResponse, card, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_hire(self, async_client: AsyncFv) -> None:
        response = await async_client.me.card.with_raw_response.hire(
            card_id="card_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        card = await response.parse()
        assert_matches_type(CardHireResponse, card, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_hire(self, async_client: AsyncFv) -> None:
        async with async_client.me.card.with_streaming_response.hire(
            card_id="card_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            card = await response.parse()
            assert_matches_type(CardHireResponse, card, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_sell(self, async_client: AsyncFv) -> None:
        card = await async_client.me.card.sell(
            cards_ids=[0],
        )
        assert_matches_type(CardSellResponse, card, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_sell_with_all_params(self, async_client: AsyncFv) -> None:
        card = await async_client.me.card.sell(
            cards_ids=[0],
            accept_language="accept-language",
        )
        assert_matches_type(CardSellResponse, card, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_sell(self, async_client: AsyncFv) -> None:
        response = await async_client.me.card.with_raw_response.sell(
            cards_ids=[0],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        card = await response.parse()
        assert_matches_type(CardSellResponse, card, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_sell(self, async_client: AsyncFv) -> None:
        async with async_client.me.card.with_streaming_response.sell(
            cards_ids=[0],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            card = await response.parse()
            assert_matches_type(CardSellResponse, card, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_set_captain(self, async_client: AsyncFv) -> None:
        card = await async_client.me.card.set_captain(
            usercard_id=0,
        )
        assert card is None

    @pytest.mark.skip()
    @parametrize
    async def test_method_set_captain_with_all_params(self, async_client: AsyncFv) -> None:
        card = await async_client.me.card.set_captain(
            usercard_id=0,
            accept_language="accept-language",
        )
        assert card is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_set_captain(self, async_client: AsyncFv) -> None:
        response = await async_client.me.card.with_raw_response.set_captain(
            usercard_id=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        card = await response.parse()
        assert card is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_set_captain(self, async_client: AsyncFv) -> None:
        async with async_client.me.card.with_streaming_response.set_captain(
            usercard_id=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            card = await response.parse()
            assert card is None

        assert cast(Any, response.is_closed) is True
