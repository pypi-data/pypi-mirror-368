# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from fv import Fv, AsyncFv
from fv.types import AuthLoginDiscordResponse
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAuth:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_login_discord(self, client: Fv) -> None:
        auth = client.auth.login_discord(
            code="code",
            origin="origin",
        )
        assert_matches_type(AuthLoginDiscordResponse, auth, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_login_discord_with_all_params(self, client: Fv) -> None:
        auth = client.auth.login_discord(
            code="code",
            origin="origin",
            accept_language="accept-language",
        )
        assert_matches_type(AuthLoginDiscordResponse, auth, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_login_discord(self, client: Fv) -> None:
        response = client.auth.with_raw_response.login_discord(
            code="code",
            origin="origin",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        auth = response.parse()
        assert_matches_type(AuthLoginDiscordResponse, auth, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_login_discord(self, client: Fv) -> None:
        with client.auth.with_streaming_response.login_discord(
            code="code",
            origin="origin",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            auth = response.parse()
            assert_matches_type(AuthLoginDiscordResponse, auth, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncAuth:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_login_discord(self, async_client: AsyncFv) -> None:
        auth = await async_client.auth.login_discord(
            code="code",
            origin="origin",
        )
        assert_matches_type(AuthLoginDiscordResponse, auth, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_login_discord_with_all_params(self, async_client: AsyncFv) -> None:
        auth = await async_client.auth.login_discord(
            code="code",
            origin="origin",
            accept_language="accept-language",
        )
        assert_matches_type(AuthLoginDiscordResponse, auth, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_login_discord(self, async_client: AsyncFv) -> None:
        response = await async_client.auth.with_raw_response.login_discord(
            code="code",
            origin="origin",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        auth = await response.parse()
        assert_matches_type(AuthLoginDiscordResponse, auth, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_login_discord(self, async_client: AsyncFv) -> None:
        async with async_client.auth.with_streaming_response.login_discord(
            code="code",
            origin="origin",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            auth = await response.parse()
            assert_matches_type(AuthLoginDiscordResponse, auth, path=["response"])

        assert cast(Any, response.is_closed) is True
