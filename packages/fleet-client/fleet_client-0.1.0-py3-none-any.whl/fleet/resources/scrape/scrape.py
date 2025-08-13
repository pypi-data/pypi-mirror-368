# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .async_ import (
    AsyncResource,
    AsyncAsyncResource,
    AsyncResourceWithRawResponse,
    AsyncAsyncResourceWithRawResponse,
    AsyncResourceWithStreamingResponse,
    AsyncAsyncResourceWithStreamingResponse,
)
from ...types import scrape_cleanup_params
from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from .browser_strategy import (
    BrowserStrategyResource,
    AsyncBrowserStrategyResource,
    BrowserStrategyResourceWithRawResponse,
    AsyncBrowserStrategyResourceWithRawResponse,
    BrowserStrategyResourceWithStreamingResponse,
    AsyncBrowserStrategyResourceWithStreamingResponse,
)
from ...types.scrape_cleanup_response import ScrapeCleanupResponse
from ...types.scrape_get_browser_stats_response import ScrapeGetBrowserStatsResponse

__all__ = ["ScrapeResource", "AsyncScrapeResource"]


class ScrapeResource(SyncAPIResource):
    @cached_property
    def async_(self) -> AsyncResource:
        return AsyncResource(self._client)

    @cached_property
    def browser_strategy(self) -> BrowserStrategyResource:
        return BrowserStrategyResource(self._client)

    @cached_property
    def with_raw_response(self) -> ScrapeResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/evrimai/fleet-client#accessing-raw-response-data-eg-headers
        """
        return ScrapeResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ScrapeResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/evrimai/fleet-client#with_streaming_response
        """
        return ScrapeResourceWithStreamingResponse(self)

    def cleanup(
        self,
        *,
        max_age_hours: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ScrapeCleanupResponse:
        """
        Clean up completed jobs older than the specified age.

        Args:
          max_age_hours: Maximum age in hours for completed jobs

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/scrape/cleanup",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"max_age_hours": max_age_hours}, scrape_cleanup_params.ScrapeCleanupParams),
            ),
            cast_to=ScrapeCleanupResponse,
        )

    def get_browser_stats(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ScrapeGetBrowserStatsResponse:
        """Get browser usage statistics for async scraping jobs."""
        return self._get(
            "/scrape/browser-stats",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ScrapeGetBrowserStatsResponse,
        )


class AsyncScrapeResource(AsyncAPIResource):
    @cached_property
    def async_(self) -> AsyncAsyncResource:
        return AsyncAsyncResource(self._client)

    @cached_property
    def browser_strategy(self) -> AsyncBrowserStrategyResource:
        return AsyncBrowserStrategyResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncScrapeResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/evrimai/fleet-client#accessing-raw-response-data-eg-headers
        """
        return AsyncScrapeResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncScrapeResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/evrimai/fleet-client#with_streaming_response
        """
        return AsyncScrapeResourceWithStreamingResponse(self)

    async def cleanup(
        self,
        *,
        max_age_hours: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ScrapeCleanupResponse:
        """
        Clean up completed jobs older than the specified age.

        Args:
          max_age_hours: Maximum age in hours for completed jobs

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/scrape/cleanup",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"max_age_hours": max_age_hours}, scrape_cleanup_params.ScrapeCleanupParams
                ),
            ),
            cast_to=ScrapeCleanupResponse,
        )

    async def get_browser_stats(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ScrapeGetBrowserStatsResponse:
        """Get browser usage statistics for async scraping jobs."""
        return await self._get(
            "/scrape/browser-stats",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ScrapeGetBrowserStatsResponse,
        )


class ScrapeResourceWithRawResponse:
    def __init__(self, scrape: ScrapeResource) -> None:
        self._scrape = scrape

        self.cleanup = to_raw_response_wrapper(
            scrape.cleanup,
        )
        self.get_browser_stats = to_raw_response_wrapper(
            scrape.get_browser_stats,
        )

    @cached_property
    def async_(self) -> AsyncResourceWithRawResponse:
        return AsyncResourceWithRawResponse(self._scrape.async_)

    @cached_property
    def browser_strategy(self) -> BrowserStrategyResourceWithRawResponse:
        return BrowserStrategyResourceWithRawResponse(self._scrape.browser_strategy)


class AsyncScrapeResourceWithRawResponse:
    def __init__(self, scrape: AsyncScrapeResource) -> None:
        self._scrape = scrape

        self.cleanup = async_to_raw_response_wrapper(
            scrape.cleanup,
        )
        self.get_browser_stats = async_to_raw_response_wrapper(
            scrape.get_browser_stats,
        )

    @cached_property
    def async_(self) -> AsyncAsyncResourceWithRawResponse:
        return AsyncAsyncResourceWithRawResponse(self._scrape.async_)

    @cached_property
    def browser_strategy(self) -> AsyncBrowserStrategyResourceWithRawResponse:
        return AsyncBrowserStrategyResourceWithRawResponse(self._scrape.browser_strategy)


class ScrapeResourceWithStreamingResponse:
    def __init__(self, scrape: ScrapeResource) -> None:
        self._scrape = scrape

        self.cleanup = to_streamed_response_wrapper(
            scrape.cleanup,
        )
        self.get_browser_stats = to_streamed_response_wrapper(
            scrape.get_browser_stats,
        )

    @cached_property
    def async_(self) -> AsyncResourceWithStreamingResponse:
        return AsyncResourceWithStreamingResponse(self._scrape.async_)

    @cached_property
    def browser_strategy(self) -> BrowserStrategyResourceWithStreamingResponse:
        return BrowserStrategyResourceWithStreamingResponse(self._scrape.browser_strategy)


class AsyncScrapeResourceWithStreamingResponse:
    def __init__(self, scrape: AsyncScrapeResource) -> None:
        self._scrape = scrape

        self.cleanup = async_to_streamed_response_wrapper(
            scrape.cleanup,
        )
        self.get_browser_stats = async_to_streamed_response_wrapper(
            scrape.get_browser_stats,
        )

    @cached_property
    def async_(self) -> AsyncAsyncResourceWithStreamingResponse:
        return AsyncAsyncResourceWithStreamingResponse(self._scrape.async_)

    @cached_property
    def browser_strategy(self) -> AsyncBrowserStrategyResourceWithStreamingResponse:
        return AsyncBrowserStrategyResourceWithStreamingResponse(self._scrape.browser_strategy)
