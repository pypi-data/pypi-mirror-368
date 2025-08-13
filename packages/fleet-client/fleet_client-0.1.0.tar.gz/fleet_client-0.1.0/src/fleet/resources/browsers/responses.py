# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

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
from ...types.browsers import response_get_filtered_params, response_toggle_tracking_params
from ...types.browsers.response_clear_response import ResponseClearResponse
from ...types.browsers.response_get_all_response import ResponseGetAllResponse
from ...types.browsers.response_get_latest_response import ResponseGetLatestResponse
from ...types.browsers.response_get_summary_response import ResponseGetSummaryResponse
from ...types.browsers.response_get_filtered_response import ResponseGetFilteredResponse
from ...types.browsers.response_toggle_tracking_response import ResponseToggleTrackingResponse

__all__ = ["ResponsesResource", "AsyncResponsesResource"]


class ResponsesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ResponsesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/evrimai/fleet-client#accessing-raw-response-data-eg-headers
        """
        return ResponsesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ResponsesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/evrimai/fleet-client#with_streaming_response
        """
        return ResponsesResourceWithStreamingResponse(self)

    def clear(
        self,
        browser_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ResponseClearResponse:
        """
        Clear Browser Responses

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not browser_id:
            raise ValueError(f"Expected a non-empty value for `browser_id` but received {browser_id!r}")
        return self._delete(
            f"/browsers/{browser_id}/responses",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ResponseClearResponse,
        )

    def get_all(
        self,
        browser_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ResponseGetAllResponse:
        """
        Get Browser Responses

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not browser_id:
            raise ValueError(f"Expected a non-empty value for `browser_id` but received {browser_id!r}")
        return self._get(
            f"/browsers/{browser_id}/responses",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ResponseGetAllResponse,
        )

    def get_filtered(
        self,
        browser_id: str,
        *,
        status_code: int | NotGiven = NOT_GIVEN,
        url_pattern: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ResponseGetFilteredResponse:
        """
        Get Browser Responses Filtered

        Args:
          status_code: Filter by status code

          url_pattern: Filter by URL pattern

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not browser_id:
            raise ValueError(f"Expected a non-empty value for `browser_id` but received {browser_id!r}")
        return self._get(
            f"/browsers/{browser_id}/responses/filter",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "status_code": status_code,
                        "url_pattern": url_pattern,
                    },
                    response_get_filtered_params.ResponseGetFilteredParams,
                ),
            ),
            cast_to=ResponseGetFilteredResponse,
        )

    def get_latest(
        self,
        browser_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ResponseGetLatestResponse:
        """
        Get Browser Latest Response

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not browser_id:
            raise ValueError(f"Expected a non-empty value for `browser_id` but received {browser_id!r}")
        return self._get(
            f"/browsers/{browser_id}/responses/latest",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ResponseGetLatestResponse,
        )

    def get_summary(
        self,
        browser_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ResponseGetSummaryResponse:
        """
        Get Browser Response Summary

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not browser_id:
            raise ValueError(f"Expected a non-empty value for `browser_id` but received {browser_id!r}")
        return self._get(
            f"/browsers/{browser_id}/responses/summary",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ResponseGetSummaryResponse,
        )

    def toggle_tracking(
        self,
        browser_id: str,
        *,
        enable: bool,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ResponseToggleTrackingResponse:
        """
        Toggle Response Tracking

        Args:
          enable: Enable or disable tracking

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not browser_id:
            raise ValueError(f"Expected a non-empty value for `browser_id` but received {browser_id!r}")
        return self._post(
            f"/browsers/{browser_id}/responses/toggle",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"enable": enable}, response_toggle_tracking_params.ResponseToggleTrackingParams),
            ),
            cast_to=ResponseToggleTrackingResponse,
        )


class AsyncResponsesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncResponsesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/evrimai/fleet-client#accessing-raw-response-data-eg-headers
        """
        return AsyncResponsesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncResponsesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/evrimai/fleet-client#with_streaming_response
        """
        return AsyncResponsesResourceWithStreamingResponse(self)

    async def clear(
        self,
        browser_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ResponseClearResponse:
        """
        Clear Browser Responses

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not browser_id:
            raise ValueError(f"Expected a non-empty value for `browser_id` but received {browser_id!r}")
        return await self._delete(
            f"/browsers/{browser_id}/responses",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ResponseClearResponse,
        )

    async def get_all(
        self,
        browser_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ResponseGetAllResponse:
        """
        Get Browser Responses

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not browser_id:
            raise ValueError(f"Expected a non-empty value for `browser_id` but received {browser_id!r}")
        return await self._get(
            f"/browsers/{browser_id}/responses",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ResponseGetAllResponse,
        )

    async def get_filtered(
        self,
        browser_id: str,
        *,
        status_code: int | NotGiven = NOT_GIVEN,
        url_pattern: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ResponseGetFilteredResponse:
        """
        Get Browser Responses Filtered

        Args:
          status_code: Filter by status code

          url_pattern: Filter by URL pattern

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not browser_id:
            raise ValueError(f"Expected a non-empty value for `browser_id` but received {browser_id!r}")
        return await self._get(
            f"/browsers/{browser_id}/responses/filter",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "status_code": status_code,
                        "url_pattern": url_pattern,
                    },
                    response_get_filtered_params.ResponseGetFilteredParams,
                ),
            ),
            cast_to=ResponseGetFilteredResponse,
        )

    async def get_latest(
        self,
        browser_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ResponseGetLatestResponse:
        """
        Get Browser Latest Response

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not browser_id:
            raise ValueError(f"Expected a non-empty value for `browser_id` but received {browser_id!r}")
        return await self._get(
            f"/browsers/{browser_id}/responses/latest",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ResponseGetLatestResponse,
        )

    async def get_summary(
        self,
        browser_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ResponseGetSummaryResponse:
        """
        Get Browser Response Summary

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not browser_id:
            raise ValueError(f"Expected a non-empty value for `browser_id` but received {browser_id!r}")
        return await self._get(
            f"/browsers/{browser_id}/responses/summary",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ResponseGetSummaryResponse,
        )

    async def toggle_tracking(
        self,
        browser_id: str,
        *,
        enable: bool,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ResponseToggleTrackingResponse:
        """
        Toggle Response Tracking

        Args:
          enable: Enable or disable tracking

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not browser_id:
            raise ValueError(f"Expected a non-empty value for `browser_id` but received {browser_id!r}")
        return await self._post(
            f"/browsers/{browser_id}/responses/toggle",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"enable": enable}, response_toggle_tracking_params.ResponseToggleTrackingParams
                ),
            ),
            cast_to=ResponseToggleTrackingResponse,
        )


class ResponsesResourceWithRawResponse:
    def __init__(self, responses: ResponsesResource) -> None:
        self._responses = responses

        self.clear = to_raw_response_wrapper(
            responses.clear,
        )
        self.get_all = to_raw_response_wrapper(
            responses.get_all,
        )
        self.get_filtered = to_raw_response_wrapper(
            responses.get_filtered,
        )
        self.get_latest = to_raw_response_wrapper(
            responses.get_latest,
        )
        self.get_summary = to_raw_response_wrapper(
            responses.get_summary,
        )
        self.toggle_tracking = to_raw_response_wrapper(
            responses.toggle_tracking,
        )


class AsyncResponsesResourceWithRawResponse:
    def __init__(self, responses: AsyncResponsesResource) -> None:
        self._responses = responses

        self.clear = async_to_raw_response_wrapper(
            responses.clear,
        )
        self.get_all = async_to_raw_response_wrapper(
            responses.get_all,
        )
        self.get_filtered = async_to_raw_response_wrapper(
            responses.get_filtered,
        )
        self.get_latest = async_to_raw_response_wrapper(
            responses.get_latest,
        )
        self.get_summary = async_to_raw_response_wrapper(
            responses.get_summary,
        )
        self.toggle_tracking = async_to_raw_response_wrapper(
            responses.toggle_tracking,
        )


class ResponsesResourceWithStreamingResponse:
    def __init__(self, responses: ResponsesResource) -> None:
        self._responses = responses

        self.clear = to_streamed_response_wrapper(
            responses.clear,
        )
        self.get_all = to_streamed_response_wrapper(
            responses.get_all,
        )
        self.get_filtered = to_streamed_response_wrapper(
            responses.get_filtered,
        )
        self.get_latest = to_streamed_response_wrapper(
            responses.get_latest,
        )
        self.get_summary = to_streamed_response_wrapper(
            responses.get_summary,
        )
        self.toggle_tracking = to_streamed_response_wrapper(
            responses.toggle_tracking,
        )


class AsyncResponsesResourceWithStreamingResponse:
    def __init__(self, responses: AsyncResponsesResource) -> None:
        self._responses = responses

        self.clear = async_to_streamed_response_wrapper(
            responses.clear,
        )
        self.get_all = async_to_streamed_response_wrapper(
            responses.get_all,
        )
        self.get_filtered = async_to_streamed_response_wrapper(
            responses.get_filtered,
        )
        self.get_latest = async_to_streamed_response_wrapper(
            responses.get_latest,
        )
        self.get_summary = async_to_streamed_response_wrapper(
            responses.get_summary,
        )
        self.toggle_tracking = async_to_streamed_response_wrapper(
            responses.toggle_tracking,
        )
