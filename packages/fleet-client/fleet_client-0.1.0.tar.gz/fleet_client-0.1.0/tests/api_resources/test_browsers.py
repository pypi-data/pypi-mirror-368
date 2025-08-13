# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from fleet import Fleet, AsyncFleet
from fleet.types import (
    BrowserLaunchResponse,
    BrowserVisitPageResponse,
    BrowserGetMetadataResponse,
    BrowserDownloadFileResponse,
)
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestBrowsers:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Fleet) -> None:
        browser = client.browsers.list()
        assert_matches_type(object, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Fleet) -> None:
        response = client.browsers.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        browser = response.parse()
        assert_matches_type(object, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Fleet) -> None:
        with client.browsers.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            browser = response.parse()
            assert_matches_type(object, browser, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_close(self, client: Fleet) -> None:
        browser = client.browsers.close(
            "browser_id",
        )
        assert_matches_type(object, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_close(self, client: Fleet) -> None:
        response = client.browsers.with_raw_response.close(
            "browser_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        browser = response.parse()
        assert_matches_type(object, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_close(self, client: Fleet) -> None:
        with client.browsers.with_streaming_response.close(
            "browser_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            browser = response.parse()
            assert_matches_type(object, browser, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_close(self, client: Fleet) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `browser_id` but received ''"):
            client.browsers.with_raw_response.close(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_download_file(self, client: Fleet) -> None:
        browser = client.browsers.download_file(
            browser_id="browser_id",
            download_url="download_url",
            s3_bucket="s3_bucket",
        )
        assert_matches_type(BrowserDownloadFileResponse, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_download_file_with_all_params(self, client: Fleet) -> None:
        browser = client.browsers.download_file(
            browser_id="browser_id",
            download_url="download_url",
            s3_bucket="s3_bucket",
            aws_access_key_id="aws_access_key_id",
            aws_region="aws_region",
            aws_secret_access_key="aws_secret_access_key",
            s3_key="s3_key",
            wait_until="load",
        )
        assert_matches_type(BrowserDownloadFileResponse, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_download_file(self, client: Fleet) -> None:
        response = client.browsers.with_raw_response.download_file(
            browser_id="browser_id",
            download_url="download_url",
            s3_bucket="s3_bucket",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        browser = response.parse()
        assert_matches_type(BrowserDownloadFileResponse, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_download_file(self, client: Fleet) -> None:
        with client.browsers.with_streaming_response.download_file(
            browser_id="browser_id",
            download_url="download_url",
            s3_bucket="s3_bucket",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            browser = response.parse()
            assert_matches_type(BrowserDownloadFileResponse, browser, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_download_file(self, client: Fleet) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `browser_id` but received ''"):
            client.browsers.with_raw_response.download_file(
                browser_id="",
                download_url="download_url",
                s3_bucket="s3_bucket",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_metadata(self, client: Fleet) -> None:
        browser = client.browsers.get_metadata(
            "browser_id",
        )
        assert_matches_type(BrowserGetMetadataResponse, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_metadata(self, client: Fleet) -> None:
        response = client.browsers.with_raw_response.get_metadata(
            "browser_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        browser = response.parse()
        assert_matches_type(BrowserGetMetadataResponse, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_metadata(self, client: Fleet) -> None:
        with client.browsers.with_streaming_response.get_metadata(
            "browser_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            browser = response.parse()
            assert_matches_type(BrowserGetMetadataResponse, browser, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_metadata(self, client: Fleet) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `browser_id` but received ''"):
            client.browsers.with_raw_response.get_metadata(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_launch(self, client: Fleet) -> None:
        browser = client.browsers.launch()
        assert_matches_type(BrowserLaunchResponse, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_launch_with_all_params(self, client: Fleet) -> None:
        browser = client.browsers.launch(
            headless=True,
            track_all_responses=True,
            url="url",
        )
        assert_matches_type(BrowserLaunchResponse, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_launch(self, client: Fleet) -> None:
        response = client.browsers.with_raw_response.launch()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        browser = response.parse()
        assert_matches_type(BrowserLaunchResponse, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_launch(self, client: Fleet) -> None:
        with client.browsers.with_streaming_response.launch() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            browser = response.parse()
            assert_matches_type(BrowserLaunchResponse, browser, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_scrape_page(self, client: Fleet) -> None:
        browser = client.browsers.scrape_page(
            browser_id="browser_id",
            url="url",
        )
        assert_matches_type(object, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_scrape_page_with_all_params(self, client: Fleet) -> None:
        browser = client.browsers.scrape_page(
            browser_id="browser_id",
            url="url",
            wait_until="load",
        )
        assert_matches_type(object, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_scrape_page(self, client: Fleet) -> None:
        response = client.browsers.with_raw_response.scrape_page(
            browser_id="browser_id",
            url="url",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        browser = response.parse()
        assert_matches_type(object, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_scrape_page(self, client: Fleet) -> None:
        with client.browsers.with_streaming_response.scrape_page(
            browser_id="browser_id",
            url="url",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            browser = response.parse()
            assert_matches_type(object, browser, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_scrape_page(self, client: Fleet) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `browser_id` but received ''"):
            client.browsers.with_raw_response.scrape_page(
                browser_id="",
                url="url",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_visit_page(self, client: Fleet) -> None:
        browser = client.browsers.visit_page(
            browser_id="browser_id",
            url="url",
        )
        assert_matches_type(BrowserVisitPageResponse, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_visit_page_with_all_params(self, client: Fleet) -> None:
        browser = client.browsers.visit_page(
            browser_id="browser_id",
            url="url",
            wait_until="load",
        )
        assert_matches_type(BrowserVisitPageResponse, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_visit_page(self, client: Fleet) -> None:
        response = client.browsers.with_raw_response.visit_page(
            browser_id="browser_id",
            url="url",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        browser = response.parse()
        assert_matches_type(BrowserVisitPageResponse, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_visit_page(self, client: Fleet) -> None:
        with client.browsers.with_streaming_response.visit_page(
            browser_id="browser_id",
            url="url",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            browser = response.parse()
            assert_matches_type(BrowserVisitPageResponse, browser, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_visit_page(self, client: Fleet) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `browser_id` but received ''"):
            client.browsers.with_raw_response.visit_page(
                browser_id="",
                url="url",
            )


class TestAsyncBrowsers:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncFleet) -> None:
        browser = await async_client.browsers.list()
        assert_matches_type(object, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncFleet) -> None:
        response = await async_client.browsers.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        browser = await response.parse()
        assert_matches_type(object, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncFleet) -> None:
        async with async_client.browsers.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            browser = await response.parse()
            assert_matches_type(object, browser, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_close(self, async_client: AsyncFleet) -> None:
        browser = await async_client.browsers.close(
            "browser_id",
        )
        assert_matches_type(object, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_close(self, async_client: AsyncFleet) -> None:
        response = await async_client.browsers.with_raw_response.close(
            "browser_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        browser = await response.parse()
        assert_matches_type(object, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_close(self, async_client: AsyncFleet) -> None:
        async with async_client.browsers.with_streaming_response.close(
            "browser_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            browser = await response.parse()
            assert_matches_type(object, browser, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_close(self, async_client: AsyncFleet) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `browser_id` but received ''"):
            await async_client.browsers.with_raw_response.close(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_download_file(self, async_client: AsyncFleet) -> None:
        browser = await async_client.browsers.download_file(
            browser_id="browser_id",
            download_url="download_url",
            s3_bucket="s3_bucket",
        )
        assert_matches_type(BrowserDownloadFileResponse, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_download_file_with_all_params(self, async_client: AsyncFleet) -> None:
        browser = await async_client.browsers.download_file(
            browser_id="browser_id",
            download_url="download_url",
            s3_bucket="s3_bucket",
            aws_access_key_id="aws_access_key_id",
            aws_region="aws_region",
            aws_secret_access_key="aws_secret_access_key",
            s3_key="s3_key",
            wait_until="load",
        )
        assert_matches_type(BrowserDownloadFileResponse, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_download_file(self, async_client: AsyncFleet) -> None:
        response = await async_client.browsers.with_raw_response.download_file(
            browser_id="browser_id",
            download_url="download_url",
            s3_bucket="s3_bucket",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        browser = await response.parse()
        assert_matches_type(BrowserDownloadFileResponse, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_download_file(self, async_client: AsyncFleet) -> None:
        async with async_client.browsers.with_streaming_response.download_file(
            browser_id="browser_id",
            download_url="download_url",
            s3_bucket="s3_bucket",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            browser = await response.parse()
            assert_matches_type(BrowserDownloadFileResponse, browser, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_download_file(self, async_client: AsyncFleet) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `browser_id` but received ''"):
            await async_client.browsers.with_raw_response.download_file(
                browser_id="",
                download_url="download_url",
                s3_bucket="s3_bucket",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_metadata(self, async_client: AsyncFleet) -> None:
        browser = await async_client.browsers.get_metadata(
            "browser_id",
        )
        assert_matches_type(BrowserGetMetadataResponse, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_metadata(self, async_client: AsyncFleet) -> None:
        response = await async_client.browsers.with_raw_response.get_metadata(
            "browser_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        browser = await response.parse()
        assert_matches_type(BrowserGetMetadataResponse, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_metadata(self, async_client: AsyncFleet) -> None:
        async with async_client.browsers.with_streaming_response.get_metadata(
            "browser_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            browser = await response.parse()
            assert_matches_type(BrowserGetMetadataResponse, browser, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_metadata(self, async_client: AsyncFleet) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `browser_id` but received ''"):
            await async_client.browsers.with_raw_response.get_metadata(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_launch(self, async_client: AsyncFleet) -> None:
        browser = await async_client.browsers.launch()
        assert_matches_type(BrowserLaunchResponse, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_launch_with_all_params(self, async_client: AsyncFleet) -> None:
        browser = await async_client.browsers.launch(
            headless=True,
            track_all_responses=True,
            url="url",
        )
        assert_matches_type(BrowserLaunchResponse, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_launch(self, async_client: AsyncFleet) -> None:
        response = await async_client.browsers.with_raw_response.launch()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        browser = await response.parse()
        assert_matches_type(BrowserLaunchResponse, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_launch(self, async_client: AsyncFleet) -> None:
        async with async_client.browsers.with_streaming_response.launch() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            browser = await response.parse()
            assert_matches_type(BrowserLaunchResponse, browser, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_scrape_page(self, async_client: AsyncFleet) -> None:
        browser = await async_client.browsers.scrape_page(
            browser_id="browser_id",
            url="url",
        )
        assert_matches_type(object, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_scrape_page_with_all_params(self, async_client: AsyncFleet) -> None:
        browser = await async_client.browsers.scrape_page(
            browser_id="browser_id",
            url="url",
            wait_until="load",
        )
        assert_matches_type(object, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_scrape_page(self, async_client: AsyncFleet) -> None:
        response = await async_client.browsers.with_raw_response.scrape_page(
            browser_id="browser_id",
            url="url",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        browser = await response.parse()
        assert_matches_type(object, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_scrape_page(self, async_client: AsyncFleet) -> None:
        async with async_client.browsers.with_streaming_response.scrape_page(
            browser_id="browser_id",
            url="url",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            browser = await response.parse()
            assert_matches_type(object, browser, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_scrape_page(self, async_client: AsyncFleet) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `browser_id` but received ''"):
            await async_client.browsers.with_raw_response.scrape_page(
                browser_id="",
                url="url",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_visit_page(self, async_client: AsyncFleet) -> None:
        browser = await async_client.browsers.visit_page(
            browser_id="browser_id",
            url="url",
        )
        assert_matches_type(BrowserVisitPageResponse, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_visit_page_with_all_params(self, async_client: AsyncFleet) -> None:
        browser = await async_client.browsers.visit_page(
            browser_id="browser_id",
            url="url",
            wait_until="load",
        )
        assert_matches_type(BrowserVisitPageResponse, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_visit_page(self, async_client: AsyncFleet) -> None:
        response = await async_client.browsers.with_raw_response.visit_page(
            browser_id="browser_id",
            url="url",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        browser = await response.parse()
        assert_matches_type(BrowserVisitPageResponse, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_visit_page(self, async_client: AsyncFleet) -> None:
        async with async_client.browsers.with_streaming_response.visit_page(
            browser_id="browser_id",
            url="url",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            browser = await response.parse()
            assert_matches_type(BrowserVisitPageResponse, browser, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_visit_page(self, async_client: AsyncFleet) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `browser_id` but received ''"):
            await async_client.browsers.with_raw_response.visit_page(
                browser_id="",
                url="url",
            )
