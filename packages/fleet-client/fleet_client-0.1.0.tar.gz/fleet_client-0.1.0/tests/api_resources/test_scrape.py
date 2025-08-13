# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from fleet import Fleet, AsyncFleet
from fleet.types import ScrapeCleanupResponse, ScrapeGetBrowserStatsResponse
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestScrape:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_cleanup(self, client: Fleet) -> None:
        scrape = client.scrape.cleanup()
        assert_matches_type(ScrapeCleanupResponse, scrape, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_cleanup_with_all_params(self, client: Fleet) -> None:
        scrape = client.scrape.cleanup(
            max_age_hours=0,
        )
        assert_matches_type(ScrapeCleanupResponse, scrape, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_cleanup(self, client: Fleet) -> None:
        response = client.scrape.with_raw_response.cleanup()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        scrape = response.parse()
        assert_matches_type(ScrapeCleanupResponse, scrape, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_cleanup(self, client: Fleet) -> None:
        with client.scrape.with_streaming_response.cleanup() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            scrape = response.parse()
            assert_matches_type(ScrapeCleanupResponse, scrape, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_browser_stats(self, client: Fleet) -> None:
        scrape = client.scrape.get_browser_stats()
        assert_matches_type(ScrapeGetBrowserStatsResponse, scrape, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_browser_stats(self, client: Fleet) -> None:
        response = client.scrape.with_raw_response.get_browser_stats()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        scrape = response.parse()
        assert_matches_type(ScrapeGetBrowserStatsResponse, scrape, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_browser_stats(self, client: Fleet) -> None:
        with client.scrape.with_streaming_response.get_browser_stats() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            scrape = response.parse()
            assert_matches_type(ScrapeGetBrowserStatsResponse, scrape, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncScrape:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_cleanup(self, async_client: AsyncFleet) -> None:
        scrape = await async_client.scrape.cleanup()
        assert_matches_type(ScrapeCleanupResponse, scrape, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_cleanup_with_all_params(self, async_client: AsyncFleet) -> None:
        scrape = await async_client.scrape.cleanup(
            max_age_hours=0,
        )
        assert_matches_type(ScrapeCleanupResponse, scrape, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_cleanup(self, async_client: AsyncFleet) -> None:
        response = await async_client.scrape.with_raw_response.cleanup()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        scrape = await response.parse()
        assert_matches_type(ScrapeCleanupResponse, scrape, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_cleanup(self, async_client: AsyncFleet) -> None:
        async with async_client.scrape.with_streaming_response.cleanup() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            scrape = await response.parse()
            assert_matches_type(ScrapeCleanupResponse, scrape, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_browser_stats(self, async_client: AsyncFleet) -> None:
        scrape = await async_client.scrape.get_browser_stats()
        assert_matches_type(ScrapeGetBrowserStatsResponse, scrape, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_browser_stats(self, async_client: AsyncFleet) -> None:
        response = await async_client.scrape.with_raw_response.get_browser_stats()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        scrape = await response.parse()
        assert_matches_type(ScrapeGetBrowserStatsResponse, scrape, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_browser_stats(self, async_client: AsyncFleet) -> None:
        async with async_client.scrape.with_streaming_response.get_browser_stats() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            scrape = await response.parse()
            assert_matches_type(ScrapeGetBrowserStatsResponse, scrape, path=["response"])

        assert cast(Any, response.is_closed) is True
