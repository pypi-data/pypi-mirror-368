# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional

import httpx

from ..types import WaitUntil, download_create_job_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.wait_until import WaitUntil
from ..types.download_create_job_response import DownloadCreateJobResponse
from ..types.download_get_job_status_response import DownloadGetJobStatusResponse

__all__ = ["DownloadResource", "AsyncDownloadResource"]


class DownloadResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> DownloadResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/evrimai/fleet-client#accessing-raw-response-data-eg-headers
        """
        return DownloadResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DownloadResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/evrimai/fleet-client#with_streaming_response
        """
        return DownloadResourceWithStreamingResponse(self)

    def create_job(
        self,
        *,
        download_url: str,
        s3_bucket: str,
        aws_access_key_id: Optional[str] | NotGiven = NOT_GIVEN,
        aws_region: str | NotGiven = NOT_GIVEN,
        aws_secret_access_key: Optional[str] | NotGiven = NOT_GIVEN,
        s3_key: Optional[str] | NotGiven = NOT_GIVEN,
        wait_until: WaitUntil | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DownloadCreateJobResponse:
        """
        Create an async download job and return a job ID immediately.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/download",
            body=maybe_transform(
                {
                    "download_url": download_url,
                    "s3_bucket": s3_bucket,
                    "aws_access_key_id": aws_access_key_id,
                    "aws_region": aws_region,
                    "aws_secret_access_key": aws_secret_access_key,
                    "s3_key": s3_key,
                    "wait_until": wait_until,
                },
                download_create_job_params.DownloadCreateJobParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DownloadCreateJobResponse,
        )

    def get_job_status(
        self,
        job_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DownloadGetJobStatusResponse:
        """
        Get the status and results of an async download job.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not job_id:
            raise ValueError(f"Expected a non-empty value for `job_id` but received {job_id!r}")
        return self._get(
            f"/download/{job_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DownloadGetJobStatusResponse,
        )


class AsyncDownloadResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncDownloadResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/evrimai/fleet-client#accessing-raw-response-data-eg-headers
        """
        return AsyncDownloadResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDownloadResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/evrimai/fleet-client#with_streaming_response
        """
        return AsyncDownloadResourceWithStreamingResponse(self)

    async def create_job(
        self,
        *,
        download_url: str,
        s3_bucket: str,
        aws_access_key_id: Optional[str] | NotGiven = NOT_GIVEN,
        aws_region: str | NotGiven = NOT_GIVEN,
        aws_secret_access_key: Optional[str] | NotGiven = NOT_GIVEN,
        s3_key: Optional[str] | NotGiven = NOT_GIVEN,
        wait_until: WaitUntil | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DownloadCreateJobResponse:
        """
        Create an async download job and return a job ID immediately.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/download",
            body=await async_maybe_transform(
                {
                    "download_url": download_url,
                    "s3_bucket": s3_bucket,
                    "aws_access_key_id": aws_access_key_id,
                    "aws_region": aws_region,
                    "aws_secret_access_key": aws_secret_access_key,
                    "s3_key": s3_key,
                    "wait_until": wait_until,
                },
                download_create_job_params.DownloadCreateJobParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DownloadCreateJobResponse,
        )

    async def get_job_status(
        self,
        job_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DownloadGetJobStatusResponse:
        """
        Get the status and results of an async download job.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not job_id:
            raise ValueError(f"Expected a non-empty value for `job_id` but received {job_id!r}")
        return await self._get(
            f"/download/{job_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DownloadGetJobStatusResponse,
        )


class DownloadResourceWithRawResponse:
    def __init__(self, download: DownloadResource) -> None:
        self._download = download

        self.create_job = to_raw_response_wrapper(
            download.create_job,
        )
        self.get_job_status = to_raw_response_wrapper(
            download.get_job_status,
        )


class AsyncDownloadResourceWithRawResponse:
    def __init__(self, download: AsyncDownloadResource) -> None:
        self._download = download

        self.create_job = async_to_raw_response_wrapper(
            download.create_job,
        )
        self.get_job_status = async_to_raw_response_wrapper(
            download.get_job_status,
        )


class DownloadResourceWithStreamingResponse:
    def __init__(self, download: DownloadResource) -> None:
        self._download = download

        self.create_job = to_streamed_response_wrapper(
            download.create_job,
        )
        self.get_job_status = to_streamed_response_wrapper(
            download.get_job_status,
        )


class AsyncDownloadResourceWithStreamingResponse:
    def __init__(self, download: AsyncDownloadResource) -> None:
        self._download = download

        self.create_job = async_to_streamed_response_wrapper(
            download.create_job,
        )
        self.get_job_status = async_to_streamed_response_wrapper(
            download.get_job_status,
        )
