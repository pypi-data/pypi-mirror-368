# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from fleet import Fleet, AsyncFleet
from tests.utils import assert_matches_type
from fleet.types.browsers import (
    ResponseClearResponse,
    ResponseGetAllResponse,
    ResponseGetLatestResponse,
    ResponseGetSummaryResponse,
    ResponseGetFilteredResponse,
    ResponseToggleTrackingResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestResponses:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_clear(self, client: Fleet) -> None:
        response = client.browsers.responses.clear(
            "browser_id",
        )
        assert_matches_type(ResponseClearResponse, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_clear(self, client: Fleet) -> None:
        http_response = client.browsers.responses.with_raw_response.clear(
            "browser_id",
        )

        assert http_response.is_closed is True
        assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"
        response = http_response.parse()
        assert_matches_type(ResponseClearResponse, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_clear(self, client: Fleet) -> None:
        with client.browsers.responses.with_streaming_response.clear(
            "browser_id",
        ) as http_response:
            assert not http_response.is_closed
            assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"

            response = http_response.parse()
            assert_matches_type(ResponseClearResponse, response, path=["response"])

        assert cast(Any, http_response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_clear(self, client: Fleet) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `browser_id` but received ''"):
            client.browsers.responses.with_raw_response.clear(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_all(self, client: Fleet) -> None:
        response = client.browsers.responses.get_all(
            "browser_id",
        )
        assert_matches_type(ResponseGetAllResponse, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_all(self, client: Fleet) -> None:
        http_response = client.browsers.responses.with_raw_response.get_all(
            "browser_id",
        )

        assert http_response.is_closed is True
        assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"
        response = http_response.parse()
        assert_matches_type(ResponseGetAllResponse, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_all(self, client: Fleet) -> None:
        with client.browsers.responses.with_streaming_response.get_all(
            "browser_id",
        ) as http_response:
            assert not http_response.is_closed
            assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"

            response = http_response.parse()
            assert_matches_type(ResponseGetAllResponse, response, path=["response"])

        assert cast(Any, http_response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_all(self, client: Fleet) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `browser_id` but received ''"):
            client.browsers.responses.with_raw_response.get_all(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_filtered(self, client: Fleet) -> None:
        response = client.browsers.responses.get_filtered(
            browser_id="browser_id",
        )
        assert_matches_type(ResponseGetFilteredResponse, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_filtered_with_all_params(self, client: Fleet) -> None:
        response = client.browsers.responses.get_filtered(
            browser_id="browser_id",
            status_code=0,
            url_pattern="url_pattern",
        )
        assert_matches_type(ResponseGetFilteredResponse, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_filtered(self, client: Fleet) -> None:
        http_response = client.browsers.responses.with_raw_response.get_filtered(
            browser_id="browser_id",
        )

        assert http_response.is_closed is True
        assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"
        response = http_response.parse()
        assert_matches_type(ResponseGetFilteredResponse, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_filtered(self, client: Fleet) -> None:
        with client.browsers.responses.with_streaming_response.get_filtered(
            browser_id="browser_id",
        ) as http_response:
            assert not http_response.is_closed
            assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"

            response = http_response.parse()
            assert_matches_type(ResponseGetFilteredResponse, response, path=["response"])

        assert cast(Any, http_response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_filtered(self, client: Fleet) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `browser_id` but received ''"):
            client.browsers.responses.with_raw_response.get_filtered(
                browser_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_latest(self, client: Fleet) -> None:
        response = client.browsers.responses.get_latest(
            "browser_id",
        )
        assert_matches_type(ResponseGetLatestResponse, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_latest(self, client: Fleet) -> None:
        http_response = client.browsers.responses.with_raw_response.get_latest(
            "browser_id",
        )

        assert http_response.is_closed is True
        assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"
        response = http_response.parse()
        assert_matches_type(ResponseGetLatestResponse, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_latest(self, client: Fleet) -> None:
        with client.browsers.responses.with_streaming_response.get_latest(
            "browser_id",
        ) as http_response:
            assert not http_response.is_closed
            assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"

            response = http_response.parse()
            assert_matches_type(ResponseGetLatestResponse, response, path=["response"])

        assert cast(Any, http_response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_latest(self, client: Fleet) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `browser_id` but received ''"):
            client.browsers.responses.with_raw_response.get_latest(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_summary(self, client: Fleet) -> None:
        response = client.browsers.responses.get_summary(
            "browser_id",
        )
        assert_matches_type(ResponseGetSummaryResponse, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_summary(self, client: Fleet) -> None:
        http_response = client.browsers.responses.with_raw_response.get_summary(
            "browser_id",
        )

        assert http_response.is_closed is True
        assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"
        response = http_response.parse()
        assert_matches_type(ResponseGetSummaryResponse, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_summary(self, client: Fleet) -> None:
        with client.browsers.responses.with_streaming_response.get_summary(
            "browser_id",
        ) as http_response:
            assert not http_response.is_closed
            assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"

            response = http_response.parse()
            assert_matches_type(ResponseGetSummaryResponse, response, path=["response"])

        assert cast(Any, http_response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_summary(self, client: Fleet) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `browser_id` but received ''"):
            client.browsers.responses.with_raw_response.get_summary(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_toggle_tracking(self, client: Fleet) -> None:
        response = client.browsers.responses.toggle_tracking(
            browser_id="browser_id",
            enable=True,
        )
        assert_matches_type(ResponseToggleTrackingResponse, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_toggle_tracking(self, client: Fleet) -> None:
        http_response = client.browsers.responses.with_raw_response.toggle_tracking(
            browser_id="browser_id",
            enable=True,
        )

        assert http_response.is_closed is True
        assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"
        response = http_response.parse()
        assert_matches_type(ResponseToggleTrackingResponse, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_toggle_tracking(self, client: Fleet) -> None:
        with client.browsers.responses.with_streaming_response.toggle_tracking(
            browser_id="browser_id",
            enable=True,
        ) as http_response:
            assert not http_response.is_closed
            assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"

            response = http_response.parse()
            assert_matches_type(ResponseToggleTrackingResponse, response, path=["response"])

        assert cast(Any, http_response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_toggle_tracking(self, client: Fleet) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `browser_id` but received ''"):
            client.browsers.responses.with_raw_response.toggle_tracking(
                browser_id="",
                enable=True,
            )


class TestAsyncResponses:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_clear(self, async_client: AsyncFleet) -> None:
        response = await async_client.browsers.responses.clear(
            "browser_id",
        )
        assert_matches_type(ResponseClearResponse, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_clear(self, async_client: AsyncFleet) -> None:
        http_response = await async_client.browsers.responses.with_raw_response.clear(
            "browser_id",
        )

        assert http_response.is_closed is True
        assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"
        response = await http_response.parse()
        assert_matches_type(ResponseClearResponse, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_clear(self, async_client: AsyncFleet) -> None:
        async with async_client.browsers.responses.with_streaming_response.clear(
            "browser_id",
        ) as http_response:
            assert not http_response.is_closed
            assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"

            response = await http_response.parse()
            assert_matches_type(ResponseClearResponse, response, path=["response"])

        assert cast(Any, http_response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_clear(self, async_client: AsyncFleet) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `browser_id` but received ''"):
            await async_client.browsers.responses.with_raw_response.clear(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_all(self, async_client: AsyncFleet) -> None:
        response = await async_client.browsers.responses.get_all(
            "browser_id",
        )
        assert_matches_type(ResponseGetAllResponse, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_all(self, async_client: AsyncFleet) -> None:
        http_response = await async_client.browsers.responses.with_raw_response.get_all(
            "browser_id",
        )

        assert http_response.is_closed is True
        assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"
        response = await http_response.parse()
        assert_matches_type(ResponseGetAllResponse, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_all(self, async_client: AsyncFleet) -> None:
        async with async_client.browsers.responses.with_streaming_response.get_all(
            "browser_id",
        ) as http_response:
            assert not http_response.is_closed
            assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"

            response = await http_response.parse()
            assert_matches_type(ResponseGetAllResponse, response, path=["response"])

        assert cast(Any, http_response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_all(self, async_client: AsyncFleet) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `browser_id` but received ''"):
            await async_client.browsers.responses.with_raw_response.get_all(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_filtered(self, async_client: AsyncFleet) -> None:
        response = await async_client.browsers.responses.get_filtered(
            browser_id="browser_id",
        )
        assert_matches_type(ResponseGetFilteredResponse, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_filtered_with_all_params(self, async_client: AsyncFleet) -> None:
        response = await async_client.browsers.responses.get_filtered(
            browser_id="browser_id",
            status_code=0,
            url_pattern="url_pattern",
        )
        assert_matches_type(ResponseGetFilteredResponse, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_filtered(self, async_client: AsyncFleet) -> None:
        http_response = await async_client.browsers.responses.with_raw_response.get_filtered(
            browser_id="browser_id",
        )

        assert http_response.is_closed is True
        assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"
        response = await http_response.parse()
        assert_matches_type(ResponseGetFilteredResponse, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_filtered(self, async_client: AsyncFleet) -> None:
        async with async_client.browsers.responses.with_streaming_response.get_filtered(
            browser_id="browser_id",
        ) as http_response:
            assert not http_response.is_closed
            assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"

            response = await http_response.parse()
            assert_matches_type(ResponseGetFilteredResponse, response, path=["response"])

        assert cast(Any, http_response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_filtered(self, async_client: AsyncFleet) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `browser_id` but received ''"):
            await async_client.browsers.responses.with_raw_response.get_filtered(
                browser_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_latest(self, async_client: AsyncFleet) -> None:
        response = await async_client.browsers.responses.get_latest(
            "browser_id",
        )
        assert_matches_type(ResponseGetLatestResponse, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_latest(self, async_client: AsyncFleet) -> None:
        http_response = await async_client.browsers.responses.with_raw_response.get_latest(
            "browser_id",
        )

        assert http_response.is_closed is True
        assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"
        response = await http_response.parse()
        assert_matches_type(ResponseGetLatestResponse, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_latest(self, async_client: AsyncFleet) -> None:
        async with async_client.browsers.responses.with_streaming_response.get_latest(
            "browser_id",
        ) as http_response:
            assert not http_response.is_closed
            assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"

            response = await http_response.parse()
            assert_matches_type(ResponseGetLatestResponse, response, path=["response"])

        assert cast(Any, http_response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_latest(self, async_client: AsyncFleet) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `browser_id` but received ''"):
            await async_client.browsers.responses.with_raw_response.get_latest(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_summary(self, async_client: AsyncFleet) -> None:
        response = await async_client.browsers.responses.get_summary(
            "browser_id",
        )
        assert_matches_type(ResponseGetSummaryResponse, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_summary(self, async_client: AsyncFleet) -> None:
        http_response = await async_client.browsers.responses.with_raw_response.get_summary(
            "browser_id",
        )

        assert http_response.is_closed is True
        assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"
        response = await http_response.parse()
        assert_matches_type(ResponseGetSummaryResponse, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_summary(self, async_client: AsyncFleet) -> None:
        async with async_client.browsers.responses.with_streaming_response.get_summary(
            "browser_id",
        ) as http_response:
            assert not http_response.is_closed
            assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"

            response = await http_response.parse()
            assert_matches_type(ResponseGetSummaryResponse, response, path=["response"])

        assert cast(Any, http_response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_summary(self, async_client: AsyncFleet) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `browser_id` but received ''"):
            await async_client.browsers.responses.with_raw_response.get_summary(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_toggle_tracking(self, async_client: AsyncFleet) -> None:
        response = await async_client.browsers.responses.toggle_tracking(
            browser_id="browser_id",
            enable=True,
        )
        assert_matches_type(ResponseToggleTrackingResponse, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_toggle_tracking(self, async_client: AsyncFleet) -> None:
        http_response = await async_client.browsers.responses.with_raw_response.toggle_tracking(
            browser_id="browser_id",
            enable=True,
        )

        assert http_response.is_closed is True
        assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"
        response = await http_response.parse()
        assert_matches_type(ResponseToggleTrackingResponse, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_toggle_tracking(self, async_client: AsyncFleet) -> None:
        async with async_client.browsers.responses.with_streaming_response.toggle_tracking(
            browser_id="browser_id",
            enable=True,
        ) as http_response:
            assert not http_response.is_closed
            assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"

            response = await http_response.parse()
            assert_matches_type(ResponseToggleTrackingResponse, response, path=["response"])

        assert cast(Any, http_response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_toggle_tracking(self, async_client: AsyncFleet) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `browser_id` but received ''"):
            await async_client.browsers.responses.with_raw_response.toggle_tracking(
                browser_id="",
                enable=True,
            )
