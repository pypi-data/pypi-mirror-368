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
    def test_method_retrieve_image(self, client: Fv) -> None:
        card = client.card.retrieve_image(
            card_id="card_id",
        )
        assert card is None

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_image_with_all_params(self, client: Fv) -> None:
        card = client.card.retrieve_image(
            card_id="card_id",
            accept_language="accept-language",
        )
        assert card is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve_image(self, client: Fv) -> None:
        response = client.card.with_raw_response.retrieve_image(
            card_id="card_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        card = response.parse()
        assert card is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve_image(self, client: Fv) -> None:
        with client.card.with_streaming_response.retrieve_image(
            card_id="card_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            card = response.parse()
            assert card is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve_image(self, client: Fv) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `card_id` but received ''"):
            client.card.with_raw_response.retrieve_image(
                card_id="",
            )


class TestAsyncCard:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_image(self, async_client: AsyncFv) -> None:
        card = await async_client.card.retrieve_image(
            card_id="card_id",
        )
        assert card is None

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_image_with_all_params(self, async_client: AsyncFv) -> None:
        card = await async_client.card.retrieve_image(
            card_id="card_id",
            accept_language="accept-language",
        )
        assert card is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve_image(self, async_client: AsyncFv) -> None:
        response = await async_client.card.with_raw_response.retrieve_image(
            card_id="card_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        card = await response.parse()
        assert card is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve_image(self, async_client: AsyncFv) -> None:
        async with async_client.card.with_streaming_response.retrieve_image(
            card_id="card_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            card = await response.parse()
            assert card is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve_image(self, async_client: AsyncFv) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `card_id` but received ''"):
            await async_client.card.with_raw_response.retrieve_image(
                card_id="",
            )
