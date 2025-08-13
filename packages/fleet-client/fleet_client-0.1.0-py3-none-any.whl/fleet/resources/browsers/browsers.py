# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional

import httpx

from .page import (
    PageResource,
    AsyncPageResource,
    PageResourceWithRawResponse,
    AsyncPageResourceWithRawResponse,
    PageResourceWithStreamingResponse,
    AsyncPageResourceWithStreamingResponse,
)
from ...types import (
    WaitUntil,
    browser_launch_params,
    browser_visit_page_params,
    browser_scrape_page_params,
    browser_download_file_params,
)
from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from .responses import (
    ResponsesResource,
    AsyncResponsesResource,
    ResponsesResourceWithRawResponse,
    AsyncResponsesResourceWithRawResponse,
    ResponsesResourceWithStreamingResponse,
    AsyncResponsesResourceWithStreamingResponse,
)
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.wait_until import WaitUntil
from ...types.browser_launch_response import BrowserLaunchResponse
from ...types.browser_visit_page_response import BrowserVisitPageResponse
from ...types.browser_get_metadata_response import BrowserGetMetadataResponse
from ...types.browser_download_file_response import BrowserDownloadFileResponse

__all__ = ["BrowsersResource", "AsyncBrowsersResource"]


class BrowsersResource(SyncAPIResource):
    @cached_property
    def page(self) -> PageResource:
        return PageResource(self._client)

    @cached_property
    def responses(self) -> ResponsesResource:
        return ResponsesResource(self._client)

    @cached_property
    def with_raw_response(self) -> BrowsersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/evrimai/fleet-client#accessing-raw-response-data-eg-headers
        """
        return BrowsersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> BrowsersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/evrimai/fleet-client#with_streaming_response
        """
        return BrowsersResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """List Browsers"""
        return self._get(
            "/browsers/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def close(
        self,
        browser_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Close Browser

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not browser_id:
            raise ValueError(f"Expected a non-empty value for `browser_id` but received {browser_id!r}")
        return self._delete(
            f"/browsers/{browser_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def download_file(
        self,
        browser_id: str,
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
    ) -> BrowserDownloadFileResponse:
        """
        Download a file via browser and upload it to S3.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not browser_id:
            raise ValueError(f"Expected a non-empty value for `browser_id` but received {browser_id!r}")
        return self._post(
            f"/browsers/{browser_id}/download",
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
                browser_download_file_params.BrowserDownloadFileParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BrowserDownloadFileResponse,
        )

    def get_metadata(
        self,
        browser_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BrowserGetMetadataResponse:
        """
        Get Browser Metadata

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not browser_id:
            raise ValueError(f"Expected a non-empty value for `browser_id` but received {browser_id!r}")
        return self._get(
            f"/browsers/{browser_id}/metadata",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BrowserGetMetadataResponse,
        )

    def launch(
        self,
        *,
        headless: bool | NotGiven = NOT_GIVEN,
        track_all_responses: bool | NotGiven = NOT_GIVEN,
        url: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BrowserLaunchResponse:
        """
        Launch Browser

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/browsers/",
            body=maybe_transform(
                {
                    "headless": headless,
                    "track_all_responses": track_all_responses,
                    "url": url,
                },
                browser_launch_params.BrowserLaunchParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BrowserLaunchResponse,
        )

    def scrape_page(
        self,
        browser_id: str,
        *,
        url: str,
        wait_until: WaitUntil | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Post Scrape Page

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not browser_id:
            raise ValueError(f"Expected a non-empty value for `browser_id` but received {browser_id!r}")
        return self._post(
            f"/browsers/{browser_id}/scrape",
            body=maybe_transform(
                {
                    "url": url,
                    "wait_until": wait_until,
                },
                browser_scrape_page_params.BrowserScrapePageParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def visit_page(
        self,
        browser_id: str,
        *,
        url: str,
        wait_until: WaitUntil | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BrowserVisitPageResponse:
        """
        Post Visit Page

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not browser_id:
            raise ValueError(f"Expected a non-empty value for `browser_id` but received {browser_id!r}")
        return self._post(
            f"/browsers/{browser_id}/visit",
            body=maybe_transform(
                {
                    "url": url,
                    "wait_until": wait_until,
                },
                browser_visit_page_params.BrowserVisitPageParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BrowserVisitPageResponse,
        )


class AsyncBrowsersResource(AsyncAPIResource):
    @cached_property
    def page(self) -> AsyncPageResource:
        return AsyncPageResource(self._client)

    @cached_property
    def responses(self) -> AsyncResponsesResource:
        return AsyncResponsesResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncBrowsersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/evrimai/fleet-client#accessing-raw-response-data-eg-headers
        """
        return AsyncBrowsersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncBrowsersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/evrimai/fleet-client#with_streaming_response
        """
        return AsyncBrowsersResourceWithStreamingResponse(self)

    async def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """List Browsers"""
        return await self._get(
            "/browsers/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def close(
        self,
        browser_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Close Browser

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not browser_id:
            raise ValueError(f"Expected a non-empty value for `browser_id` but received {browser_id!r}")
        return await self._delete(
            f"/browsers/{browser_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def download_file(
        self,
        browser_id: str,
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
    ) -> BrowserDownloadFileResponse:
        """
        Download a file via browser and upload it to S3.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not browser_id:
            raise ValueError(f"Expected a non-empty value for `browser_id` but received {browser_id!r}")
        return await self._post(
            f"/browsers/{browser_id}/download",
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
                browser_download_file_params.BrowserDownloadFileParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BrowserDownloadFileResponse,
        )

    async def get_metadata(
        self,
        browser_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BrowserGetMetadataResponse:
        """
        Get Browser Metadata

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not browser_id:
            raise ValueError(f"Expected a non-empty value for `browser_id` but received {browser_id!r}")
        return await self._get(
            f"/browsers/{browser_id}/metadata",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BrowserGetMetadataResponse,
        )

    async def launch(
        self,
        *,
        headless: bool | NotGiven = NOT_GIVEN,
        track_all_responses: bool | NotGiven = NOT_GIVEN,
        url: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BrowserLaunchResponse:
        """
        Launch Browser

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/browsers/",
            body=await async_maybe_transform(
                {
                    "headless": headless,
                    "track_all_responses": track_all_responses,
                    "url": url,
                },
                browser_launch_params.BrowserLaunchParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BrowserLaunchResponse,
        )

    async def scrape_page(
        self,
        browser_id: str,
        *,
        url: str,
        wait_until: WaitUntil | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Post Scrape Page

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not browser_id:
            raise ValueError(f"Expected a non-empty value for `browser_id` but received {browser_id!r}")
        return await self._post(
            f"/browsers/{browser_id}/scrape",
            body=await async_maybe_transform(
                {
                    "url": url,
                    "wait_until": wait_until,
                },
                browser_scrape_page_params.BrowserScrapePageParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def visit_page(
        self,
        browser_id: str,
        *,
        url: str,
        wait_until: WaitUntil | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BrowserVisitPageResponse:
        """
        Post Visit Page

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not browser_id:
            raise ValueError(f"Expected a non-empty value for `browser_id` but received {browser_id!r}")
        return await self._post(
            f"/browsers/{browser_id}/visit",
            body=await async_maybe_transform(
                {
                    "url": url,
                    "wait_until": wait_until,
                },
                browser_visit_page_params.BrowserVisitPageParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BrowserVisitPageResponse,
        )


class BrowsersResourceWithRawResponse:
    def __init__(self, browsers: BrowsersResource) -> None:
        self._browsers = browsers

        self.list = to_raw_response_wrapper(
            browsers.list,
        )
        self.close = to_raw_response_wrapper(
            browsers.close,
        )
        self.download_file = to_raw_response_wrapper(
            browsers.download_file,
        )
        self.get_metadata = to_raw_response_wrapper(
            browsers.get_metadata,
        )
        self.launch = to_raw_response_wrapper(
            browsers.launch,
        )
        self.scrape_page = to_raw_response_wrapper(
            browsers.scrape_page,
        )
        self.visit_page = to_raw_response_wrapper(
            browsers.visit_page,
        )

    @cached_property
    def page(self) -> PageResourceWithRawResponse:
        return PageResourceWithRawResponse(self._browsers.page)

    @cached_property
    def responses(self) -> ResponsesResourceWithRawResponse:
        return ResponsesResourceWithRawResponse(self._browsers.responses)


class AsyncBrowsersResourceWithRawResponse:
    def __init__(self, browsers: AsyncBrowsersResource) -> None:
        self._browsers = browsers

        self.list = async_to_raw_response_wrapper(
            browsers.list,
        )
        self.close = async_to_raw_response_wrapper(
            browsers.close,
        )
        self.download_file = async_to_raw_response_wrapper(
            browsers.download_file,
        )
        self.get_metadata = async_to_raw_response_wrapper(
            browsers.get_metadata,
        )
        self.launch = async_to_raw_response_wrapper(
            browsers.launch,
        )
        self.scrape_page = async_to_raw_response_wrapper(
            browsers.scrape_page,
        )
        self.visit_page = async_to_raw_response_wrapper(
            browsers.visit_page,
        )

    @cached_property
    def page(self) -> AsyncPageResourceWithRawResponse:
        return AsyncPageResourceWithRawResponse(self._browsers.page)

    @cached_property
    def responses(self) -> AsyncResponsesResourceWithRawResponse:
        return AsyncResponsesResourceWithRawResponse(self._browsers.responses)


class BrowsersResourceWithStreamingResponse:
    def __init__(self, browsers: BrowsersResource) -> None:
        self._browsers = browsers

        self.list = to_streamed_response_wrapper(
            browsers.list,
        )
        self.close = to_streamed_response_wrapper(
            browsers.close,
        )
        self.download_file = to_streamed_response_wrapper(
            browsers.download_file,
        )
        self.get_metadata = to_streamed_response_wrapper(
            browsers.get_metadata,
        )
        self.launch = to_streamed_response_wrapper(
            browsers.launch,
        )
        self.scrape_page = to_streamed_response_wrapper(
            browsers.scrape_page,
        )
        self.visit_page = to_streamed_response_wrapper(
            browsers.visit_page,
        )

    @cached_property
    def page(self) -> PageResourceWithStreamingResponse:
        return PageResourceWithStreamingResponse(self._browsers.page)

    @cached_property
    def responses(self) -> ResponsesResourceWithStreamingResponse:
        return ResponsesResourceWithStreamingResponse(self._browsers.responses)


class AsyncBrowsersResourceWithStreamingResponse:
    def __init__(self, browsers: AsyncBrowsersResource) -> None:
        self._browsers = browsers

        self.list = async_to_streamed_response_wrapper(
            browsers.list,
        )
        self.close = async_to_streamed_response_wrapper(
            browsers.close,
        )
        self.download_file = async_to_streamed_response_wrapper(
            browsers.download_file,
        )
        self.get_metadata = async_to_streamed_response_wrapper(
            browsers.get_metadata,
        )
        self.launch = async_to_streamed_response_wrapper(
            browsers.launch,
        )
        self.scrape_page = async_to_streamed_response_wrapper(
            browsers.scrape_page,
        )
        self.visit_page = async_to_streamed_response_wrapper(
            browsers.visit_page,
        )

    @cached_property
    def page(self) -> AsyncPageResourceWithStreamingResponse:
        return AsyncPageResourceWithStreamingResponse(self._browsers.page)

    @cached_property
    def responses(self) -> AsyncResponsesResourceWithStreamingResponse:
        return AsyncResponsesResourceWithStreamingResponse(self._browsers.responses)
