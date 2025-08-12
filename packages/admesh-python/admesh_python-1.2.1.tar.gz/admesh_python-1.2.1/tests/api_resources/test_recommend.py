# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from admesh import Admesh, AsyncAdmesh
from tests.utils import assert_matches_type
from admesh.types import RecommendGetRecommendationsResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestRecommend:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_get_recommendations(self, client: Admesh) -> None:
        recommend = client.recommend.get_recommendations(
            query="Best CRM for remote teams",
        )
        assert_matches_type(RecommendGetRecommendationsResponse, recommend, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_get_recommendations_with_all_params(self, client: Admesh) -> None:
        recommend = client.recommend.get_recommendations(
            query="Best CRM for remote teams",
            followup_suggestions="followup_suggestions",
            intent_summary="User just had a meeting about OKRs and needs a task management tool.",
            model="mistralai/mistral-7b-instruct",
            previous_query="previous_query",
            session_id="session_id",
            summary="summary",
            user_id="user_id",
        )
        assert_matches_type(RecommendGetRecommendationsResponse, recommend, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_recommendations(self, client: Admesh) -> None:
        response = client.recommend.with_raw_response.get_recommendations(
            query="Best CRM for remote teams",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        recommend = response.parse()
        assert_matches_type(RecommendGetRecommendationsResponse, recommend, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_recommendations(self, client: Admesh) -> None:
        with client.recommend.with_streaming_response.get_recommendations(
            query="Best CRM for remote teams",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            recommend = response.parse()
            assert_matches_type(RecommendGetRecommendationsResponse, recommend, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncRecommend:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_recommendations(self, async_client: AsyncAdmesh) -> None:
        recommend = await async_client.recommend.get_recommendations(
            query="Best CRM for remote teams",
        )
        assert_matches_type(RecommendGetRecommendationsResponse, recommend, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_recommendations_with_all_params(self, async_client: AsyncAdmesh) -> None:
        recommend = await async_client.recommend.get_recommendations(
            query="Best CRM for remote teams",
            followup_suggestions="followup_suggestions",
            intent_summary="User just had a meeting about OKRs and needs a task management tool.",
            model="mistralai/mistral-7b-instruct",
            previous_query="previous_query",
            session_id="session_id",
            summary="summary",
            user_id="user_id",
        )
        assert_matches_type(RecommendGetRecommendationsResponse, recommend, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_recommendations(self, async_client: AsyncAdmesh) -> None:
        response = await async_client.recommend.with_raw_response.get_recommendations(
            query="Best CRM for remote teams",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        recommend = await response.parse()
        assert_matches_type(RecommendGetRecommendationsResponse, recommend, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_recommendations(self, async_client: AsyncAdmesh) -> None:
        async with async_client.recommend.with_streaming_response.get_recommendations(
            query="Best CRM for remote teams",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            recommend = await response.parse()
            assert_matches_type(RecommendGetRecommendationsResponse, recommend, path=["response"])

        assert cast(Any, response.is_closed) is True
