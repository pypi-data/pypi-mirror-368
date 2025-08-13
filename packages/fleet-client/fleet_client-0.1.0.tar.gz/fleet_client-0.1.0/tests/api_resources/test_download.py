# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from fleet import Fleet, AsyncFleet
from fleet.types import DownloadCreateJobResponse, DownloadGetJobStatusResponse
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDownload:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_job(self, client: Fleet) -> None:
        download = client.download.create_job(
            download_url="download_url",
            s3_bucket="s3_bucket",
        )
        assert_matches_type(DownloadCreateJobResponse, download, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_job_with_all_params(self, client: Fleet) -> None:
        download = client.download.create_job(
            download_url="download_url",
            s3_bucket="s3_bucket",
            aws_access_key_id="aws_access_key_id",
            aws_region="aws_region",
            aws_secret_access_key="aws_secret_access_key",
            s3_key="s3_key",
            wait_until="load",
        )
        assert_matches_type(DownloadCreateJobResponse, download, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create_job(self, client: Fleet) -> None:
        response = client.download.with_raw_response.create_job(
            download_url="download_url",
            s3_bucket="s3_bucket",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        download = response.parse()
        assert_matches_type(DownloadCreateJobResponse, download, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create_job(self, client: Fleet) -> None:
        with client.download.with_streaming_response.create_job(
            download_url="download_url",
            s3_bucket="s3_bucket",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            download = response.parse()
            assert_matches_type(DownloadCreateJobResponse, download, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_job_status(self, client: Fleet) -> None:
        download = client.download.get_job_status(
            "job_id",
        )
        assert_matches_type(DownloadGetJobStatusResponse, download, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_job_status(self, client: Fleet) -> None:
        response = client.download.with_raw_response.get_job_status(
            "job_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        download = response.parse()
        assert_matches_type(DownloadGetJobStatusResponse, download, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_job_status(self, client: Fleet) -> None:
        with client.download.with_streaming_response.get_job_status(
            "job_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            download = response.parse()
            assert_matches_type(DownloadGetJobStatusResponse, download, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_job_status(self, client: Fleet) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `job_id` but received ''"):
            client.download.with_raw_response.get_job_status(
                "",
            )


class TestAsyncDownload:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_job(self, async_client: AsyncFleet) -> None:
        download = await async_client.download.create_job(
            download_url="download_url",
            s3_bucket="s3_bucket",
        )
        assert_matches_type(DownloadCreateJobResponse, download, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_job_with_all_params(self, async_client: AsyncFleet) -> None:
        download = await async_client.download.create_job(
            download_url="download_url",
            s3_bucket="s3_bucket",
            aws_access_key_id="aws_access_key_id",
            aws_region="aws_region",
            aws_secret_access_key="aws_secret_access_key",
            s3_key="s3_key",
            wait_until="load",
        )
        assert_matches_type(DownloadCreateJobResponse, download, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create_job(self, async_client: AsyncFleet) -> None:
        response = await async_client.download.with_raw_response.create_job(
            download_url="download_url",
            s3_bucket="s3_bucket",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        download = await response.parse()
        assert_matches_type(DownloadCreateJobResponse, download, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create_job(self, async_client: AsyncFleet) -> None:
        async with async_client.download.with_streaming_response.create_job(
            download_url="download_url",
            s3_bucket="s3_bucket",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            download = await response.parse()
            assert_matches_type(DownloadCreateJobResponse, download, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_job_status(self, async_client: AsyncFleet) -> None:
        download = await async_client.download.get_job_status(
            "job_id",
        )
        assert_matches_type(DownloadGetJobStatusResponse, download, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_job_status(self, async_client: AsyncFleet) -> None:
        response = await async_client.download.with_raw_response.get_job_status(
            "job_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        download = await response.parse()
        assert_matches_type(DownloadGetJobStatusResponse, download, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_job_status(self, async_client: AsyncFleet) -> None:
        async with async_client.download.with_streaming_response.get_job_status(
            "job_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            download = await response.parse()
            assert_matches_type(DownloadGetJobStatusResponse, download, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_job_status(self, async_client: AsyncFleet) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `job_id` but received ''"):
            await async_client.download.with_raw_response.get_job_status(
                "",
            )
