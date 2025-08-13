# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from fleet import Fleet, AsyncFleet
from fleet.types import (
    ProfileCaptureResponse,
    ProfileRunAgentResponse,
)
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestProfile:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_capture(self, client: Fleet) -> None:
        profile = client.profile.capture(
            url="url",
        )
        assert_matches_type(ProfileCaptureResponse, profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_capture_with_all_params(self, client: Fleet) -> None:
        profile = client.profile.capture(
            url="url",
            resource_types=["string"],
        )
        assert_matches_type(ProfileCaptureResponse, profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_capture(self, client: Fleet) -> None:
        response = client.profile.with_raw_response.capture(
            url="url",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        profile = response.parse()
        assert_matches_type(ProfileCaptureResponse, profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_capture(self, client: Fleet) -> None:
        with client.profile.with_streaming_response.capture(
            url="url",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            profile = response.parse()
            assert_matches_type(ProfileCaptureResponse, profile, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_run_agent(self, client: Fleet) -> None:
        profile = client.profile.run_agent(
            network_events=[
                {
                    "event": "event",
                    "headers": {"foo": "bar"},
                    "method": "method",
                    "timestamp": 0,
                    "url": "url",
                }
            ],
            user_prompt="user_prompt",
        )
        assert_matches_type(ProfileRunAgentResponse, profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_run_agent(self, client: Fleet) -> None:
        response = client.profile.with_raw_response.run_agent(
            network_events=[
                {
                    "event": "event",
                    "headers": {"foo": "bar"},
                    "method": "method",
                    "timestamp": 0,
                    "url": "url",
                }
            ],
            user_prompt="user_prompt",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        profile = response.parse()
        assert_matches_type(ProfileRunAgentResponse, profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_run_agent(self, client: Fleet) -> None:
        with client.profile.with_streaming_response.run_agent(
            network_events=[
                {
                    "event": "event",
                    "headers": {"foo": "bar"},
                    "method": "method",
                    "timestamp": 0,
                    "url": "url",
                }
            ],
            user_prompt="user_prompt",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            profile = response.parse()
            assert_matches_type(ProfileRunAgentResponse, profile, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncProfile:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_capture(self, async_client: AsyncFleet) -> None:
        profile = await async_client.profile.capture(
            url="url",
        )
        assert_matches_type(ProfileCaptureResponse, profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_capture_with_all_params(self, async_client: AsyncFleet) -> None:
        profile = await async_client.profile.capture(
            url="url",
            resource_types=["string"],
        )
        assert_matches_type(ProfileCaptureResponse, profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_capture(self, async_client: AsyncFleet) -> None:
        response = await async_client.profile.with_raw_response.capture(
            url="url",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        profile = await response.parse()
        assert_matches_type(ProfileCaptureResponse, profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_capture(self, async_client: AsyncFleet) -> None:
        async with async_client.profile.with_streaming_response.capture(
            url="url",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            profile = await response.parse()
            assert_matches_type(ProfileCaptureResponse, profile, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_run_agent(self, async_client: AsyncFleet) -> None:
        profile = await async_client.profile.run_agent(
            network_events=[
                {
                    "event": "event",
                    "headers": {"foo": "bar"},
                    "method": "method",
                    "timestamp": 0,
                    "url": "url",
                }
            ],
            user_prompt="user_prompt",
        )
        assert_matches_type(ProfileRunAgentResponse, profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_run_agent(self, async_client: AsyncFleet) -> None:
        response = await async_client.profile.with_raw_response.run_agent(
            network_events=[
                {
                    "event": "event",
                    "headers": {"foo": "bar"},
                    "method": "method",
                    "timestamp": 0,
                    "url": "url",
                }
            ],
            user_prompt="user_prompt",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        profile = await response.parse()
        assert_matches_type(ProfileRunAgentResponse, profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_run_agent(self, async_client: AsyncFleet) -> None:
        async with async_client.profile.with_streaming_response.run_agent(
            network_events=[
                {
                    "event": "event",
                    "headers": {"foo": "bar"},
                    "method": "method",
                    "timestamp": 0,
                    "url": "url",
                }
            ],
            user_prompt="user_prompt",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            profile = await response.parse()
            assert_matches_type(ProfileRunAgentResponse, profile, path=["response"])

        assert cast(Any, response.is_closed) is True
