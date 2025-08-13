# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ...types import WaitUntil
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
from ...types.scrape import async_create_params
from ...types.wait_until import WaitUntil
from ...types.scrape.async_list_response import AsyncListResponse
from ...types.scrape.async_create_response import AsyncCreateResponse
from ...types.scrape.async_delete_response import AsyncDeleteResponse
from ...types.scrape.async_retrieve_response import AsyncRetrieveResponse

__all__ = ["AsyncResource", "AsyncAsyncResource"]


class AsyncResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/evrimai/fleet-client#accessing-raw-response-data-eg-headers
        """
        return AsyncResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/evrimai/fleet-client#with_streaming_response
        """
        return AsyncResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        url: str,
        wait_until: WaitUntil | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncCreateResponse:
        """
        Create an async scraping job and return a job ID immediately.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/scrape/async",
            body=maybe_transform(
                {
                    "url": url,
                    "wait_until": wait_until,
                },
                async_create_params.AsyncCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AsyncCreateResponse,
        )

    def retrieve(
        self,
        job_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncRetrieveResponse:
        """
        Get the status and results of an async scraping job.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not job_id:
            raise ValueError(f"Expected a non-empty value for `job_id` but received {job_id!r}")
        return self._get(
            f"/scrape/async/{job_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AsyncRetrieveResponse,
        )

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncListResponse:
        """List all async scraping jobs with their statuses."""
        return self._get(
            "/scrape/async",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AsyncListResponse,
        )

    def delete(
        self,
        job_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncDeleteResponse:
        """
        Delete a specific async scraping job.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not job_id:
            raise ValueError(f"Expected a non-empty value for `job_id` but received {job_id!r}")
        return self._delete(
            f"/scrape/async/{job_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AsyncDeleteResponse,
        )


class AsyncAsyncResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAsyncResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/evrimai/fleet-client#accessing-raw-response-data-eg-headers
        """
        return AsyncAsyncResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAsyncResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/evrimai/fleet-client#with_streaming_response
        """
        return AsyncAsyncResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        url: str,
        wait_until: WaitUntil | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncCreateResponse:
        """
        Create an async scraping job and return a job ID immediately.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/scrape/async",
            body=await async_maybe_transform(
                {
                    "url": url,
                    "wait_until": wait_until,
                },
                async_create_params.AsyncCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AsyncCreateResponse,
        )

    async def retrieve(
        self,
        job_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncRetrieveResponse:
        """
        Get the status and results of an async scraping job.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not job_id:
            raise ValueError(f"Expected a non-empty value for `job_id` but received {job_id!r}")
        return await self._get(
            f"/scrape/async/{job_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AsyncRetrieveResponse,
        )

    async def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncListResponse:
        """List all async scraping jobs with their statuses."""
        return await self._get(
            "/scrape/async",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AsyncListResponse,
        )

    async def delete(
        self,
        job_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncDeleteResponse:
        """
        Delete a specific async scraping job.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not job_id:
            raise ValueError(f"Expected a non-empty value for `job_id` but received {job_id!r}")
        return await self._delete(
            f"/scrape/async/{job_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AsyncDeleteResponse,
        )


class AsyncResourceWithRawResponse:
    def __init__(self, async_: AsyncResource) -> None:
        self._async_ = async_

        self.create = to_raw_response_wrapper(
            async_.create,
        )
        self.retrieve = to_raw_response_wrapper(
            async_.retrieve,
        )
        self.list = to_raw_response_wrapper(
            async_.list,
        )
        self.delete = to_raw_response_wrapper(
            async_.delete,
        )


class AsyncAsyncResourceWithRawResponse:
    def __init__(self, async_: AsyncAsyncResource) -> None:
        self._async_ = async_

        self.create = async_to_raw_response_wrapper(
            async_.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            async_.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            async_.list,
        )
        self.delete = async_to_raw_response_wrapper(
            async_.delete,
        )


class AsyncResourceWithStreamingResponse:
    def __init__(self, async_: AsyncResource) -> None:
        self._async_ = async_

        self.create = to_streamed_response_wrapper(
            async_.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            async_.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            async_.list,
        )
        self.delete = to_streamed_response_wrapper(
            async_.delete,
        )


class AsyncAsyncResourceWithStreamingResponse:
    def __init__(self, async_: AsyncAsyncResource) -> None:
        self._async_ = async_

        self.create = async_to_streamed_response_wrapper(
            async_.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            async_.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            async_.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            async_.delete,
        )
