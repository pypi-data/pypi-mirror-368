# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from fv import Fv, AsyncFv
from fv.types import LineupSetConfigResponse
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestLineup:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_set_config(self, client: Fv) -> None:
        lineup = client.lineup.set_config(
            formation_id="formation_id",
        )
        assert_matches_type(LineupSetConfigResponse, lineup, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_set_config_with_all_params(self, client: Fv) -> None:
        lineup = client.lineup.set_config(
            formation_id="formation_id",
            accept_language="accept-language",
        )
        assert_matches_type(LineupSetConfigResponse, lineup, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_set_config(self, client: Fv) -> None:
        response = client.lineup.with_raw_response.set_config(
            formation_id="formation_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        lineup = response.parse()
        assert_matches_type(LineupSetConfigResponse, lineup, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_set_config(self, client: Fv) -> None:
        with client.lineup.with_streaming_response.set_config(
            formation_id="formation_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            lineup = response.parse()
            assert_matches_type(LineupSetConfigResponse, lineup, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_set_config(self, client: Fv) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `formation_id` but received ''"):
            client.lineup.with_raw_response.set_config(
                formation_id="",
            )


class TestAsyncLineup:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_set_config(self, async_client: AsyncFv) -> None:
        lineup = await async_client.lineup.set_config(
            formation_id="formation_id",
        )
        assert_matches_type(LineupSetConfigResponse, lineup, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_set_config_with_all_params(self, async_client: AsyncFv) -> None:
        lineup = await async_client.lineup.set_config(
            formation_id="formation_id",
            accept_language="accept-language",
        )
        assert_matches_type(LineupSetConfigResponse, lineup, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_set_config(self, async_client: AsyncFv) -> None:
        response = await async_client.lineup.with_raw_response.set_config(
            formation_id="formation_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        lineup = await response.parse()
        assert_matches_type(LineupSetConfigResponse, lineup, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_set_config(self, async_client: AsyncFv) -> None:
        async with async_client.lineup.with_streaming_response.set_config(
            formation_id="formation_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            lineup = await response.parse()
            assert_matches_type(LineupSetConfigResponse, lineup, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_set_config(self, async_client: AsyncFv) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `formation_id` but received ''"):
            await async_client.lineup.with_raw_response.set_config(
                formation_id="",
            )
