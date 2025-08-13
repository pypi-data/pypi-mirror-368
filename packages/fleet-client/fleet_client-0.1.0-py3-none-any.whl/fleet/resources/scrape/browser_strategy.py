# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ...types import BrowserSelectionStrategy
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
from ...types.scrape import browser_strategy_update_params
from ...types.browser_selection_strategy import BrowserSelectionStrategy
from ...types.scrape.browser_strategy_response import BrowserStrategyResponse

__all__ = ["BrowserStrategyResource", "AsyncBrowserStrategyResource"]


class BrowserStrategyResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> BrowserStrategyResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/evrimai/fleet-client#accessing-raw-response-data-eg-headers
        """
        return BrowserStrategyResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> BrowserStrategyResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/evrimai/fleet-client#with_streaming_response
        """
        return BrowserStrategyResourceWithStreamingResponse(self)

    def retrieve(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BrowserStrategyResponse:
        """Get the current browser selection strategy for async scraping jobs."""
        return self._get(
            "/scrape/browser-strategy",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BrowserStrategyResponse,
        )

    def update(
        self,
        *,
        strategy: BrowserSelectionStrategy,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BrowserStrategyResponse:
        """
        Set the browser selection strategy for async scraping jobs.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/scrape/browser-strategy",
            body=maybe_transform({"strategy": strategy}, browser_strategy_update_params.BrowserStrategyUpdateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BrowserStrategyResponse,
        )


class AsyncBrowserStrategyResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncBrowserStrategyResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/evrimai/fleet-client#accessing-raw-response-data-eg-headers
        """
        return AsyncBrowserStrategyResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncBrowserStrategyResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/evrimai/fleet-client#with_streaming_response
        """
        return AsyncBrowserStrategyResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BrowserStrategyResponse:
        """Get the current browser selection strategy for async scraping jobs."""
        return await self._get(
            "/scrape/browser-strategy",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BrowserStrategyResponse,
        )

    async def update(
        self,
        *,
        strategy: BrowserSelectionStrategy,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BrowserStrategyResponse:
        """
        Set the browser selection strategy for async scraping jobs.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/scrape/browser-strategy",
            body=await async_maybe_transform(
                {"strategy": strategy}, browser_strategy_update_params.BrowserStrategyUpdateParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BrowserStrategyResponse,
        )


class BrowserStrategyResourceWithRawResponse:
    def __init__(self, browser_strategy: BrowserStrategyResource) -> None:
        self._browser_strategy = browser_strategy

        self.retrieve = to_raw_response_wrapper(
            browser_strategy.retrieve,
        )
        self.update = to_raw_response_wrapper(
            browser_strategy.update,
        )


class AsyncBrowserStrategyResourceWithRawResponse:
    def __init__(self, browser_strategy: AsyncBrowserStrategyResource) -> None:
        self._browser_strategy = browser_strategy

        self.retrieve = async_to_raw_response_wrapper(
            browser_strategy.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            browser_strategy.update,
        )


class BrowserStrategyResourceWithStreamingResponse:
    def __init__(self, browser_strategy: BrowserStrategyResource) -> None:
        self._browser_strategy = browser_strategy

        self.retrieve = to_streamed_response_wrapper(
            browser_strategy.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            browser_strategy.update,
        )


class AsyncBrowserStrategyResourceWithStreamingResponse:
    def __init__(self, browser_strategy: AsyncBrowserStrategyResource) -> None:
        self._browser_strategy = browser_strategy

        self.retrieve = async_to_streamed_response_wrapper(
            browser_strategy.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            browser_strategy.update,
        )
