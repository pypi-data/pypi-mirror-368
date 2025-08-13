# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from fleet import Fleet, AsyncFleet
from tests.utils import assert_matches_type
from fleet.types.scrape import BrowserStrategyResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestBrowserStrategy:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: Fleet) -> None:
        browser_strategy = client.scrape.browser_strategy.retrieve()
        assert_matches_type(BrowserStrategyResponse, browser_strategy, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: Fleet) -> None:
        response = client.scrape.browser_strategy.with_raw_response.retrieve()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        browser_strategy = response.parse()
        assert_matches_type(BrowserStrategyResponse, browser_strategy, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: Fleet) -> None:
        with client.scrape.browser_strategy.with_streaming_response.retrieve() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            browser_strategy = response.parse()
            assert_matches_type(BrowserStrategyResponse, browser_strategy, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: Fleet) -> None:
        browser_strategy = client.scrape.browser_strategy.update(
            strategy="round_robin",
        )
        assert_matches_type(BrowserStrategyResponse, browser_strategy, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: Fleet) -> None:
        response = client.scrape.browser_strategy.with_raw_response.update(
            strategy="round_robin",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        browser_strategy = response.parse()
        assert_matches_type(BrowserStrategyResponse, browser_strategy, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: Fleet) -> None:
        with client.scrape.browser_strategy.with_streaming_response.update(
            strategy="round_robin",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            browser_strategy = response.parse()
            assert_matches_type(BrowserStrategyResponse, browser_strategy, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncBrowserStrategy:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncFleet) -> None:
        browser_strategy = await async_client.scrape.browser_strategy.retrieve()
        assert_matches_type(BrowserStrategyResponse, browser_strategy, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncFleet) -> None:
        response = await async_client.scrape.browser_strategy.with_raw_response.retrieve()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        browser_strategy = await response.parse()
        assert_matches_type(BrowserStrategyResponse, browser_strategy, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncFleet) -> None:
        async with async_client.scrape.browser_strategy.with_streaming_response.retrieve() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            browser_strategy = await response.parse()
            assert_matches_type(BrowserStrategyResponse, browser_strategy, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncFleet) -> None:
        browser_strategy = await async_client.scrape.browser_strategy.update(
            strategy="round_robin",
        )
        assert_matches_type(BrowserStrategyResponse, browser_strategy, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncFleet) -> None:
        response = await async_client.scrape.browser_strategy.with_raw_response.update(
            strategy="round_robin",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        browser_strategy = await response.parse()
        assert_matches_type(BrowserStrategyResponse, browser_strategy, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncFleet) -> None:
        async with async_client.scrape.browser_strategy.with_streaming_response.update(
            strategy="round_robin",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            browser_strategy = await response.parse()
            assert_matches_type(BrowserStrategyResponse, browser_strategy, path=["response"])

        assert cast(Any, response.is_closed) is True
