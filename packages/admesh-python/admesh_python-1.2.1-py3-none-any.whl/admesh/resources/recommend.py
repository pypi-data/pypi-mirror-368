# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional

import httpx

from ..types import recommend_get_recommendations_params
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
from .._exceptions import NoRecommendationsError
from ..types.recommend_get_recommendations_response import RecommendGetRecommendationsResponse

__all__ = ["RecommendResource", "AsyncRecommendResource"]


class RecommendResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> RecommendResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GouniManikumar12/admesh-python#accessing-raw-response-data-eg-headers
        """
        return RecommendResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RecommendResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GouniManikumar12/admesh-python#with_streaming_response
        """
        return RecommendResourceWithStreamingResponse(self)

    def get_recommendations(
        self,
        *,
        query: str,
        format: Optional[str] | NotGiven = NOT_GIVEN,
        previous_query: Optional[str] | NotGiven = NOT_GIVEN,
        previous_summary: Optional[str] | NotGiven = NOT_GIVEN,
        session_id: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        raise_on_empty_recommendations: bool = True,
    ) -> RecommendGetRecommendationsResponse:
        """
        Get monetized product/tool recommendations

        Args:
          query: The user's query

          format: The format of the response (default: "auto")

          previous_query: The user's previous query

          previous_summary: Summary of the previous recommendation

          session_id: The session ID

          raise_on_empty_recommendations: Whether to raise a NoRecommendationsError when no recommendations are available (default: True)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        response = self._post(
            "/agent/recommend",
            body=maybe_transform(
                {
                    "query": query,
                    "format": format,
                    "previous_query": previous_query,
                    "previous_summary": previous_summary,
                    "session_id": session_id,
                },
                recommend_get_recommendations_params.RecommendGetRecommendationsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RecommendGetRecommendationsResponse,
        )

        # Check if recommendations are empty or null
        if (raise_on_empty_recommendations and
            (not response.response or
             not response.response.recommendations or
             len(response.response.recommendations) == 0)):
            raise NoRecommendationsError(f"No recommendations available for query: {query}")

        return response


class AsyncRecommendResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncRecommendResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/GouniManikumar12/admesh-python#accessing-raw-response-data-eg-headers
        """
        return AsyncRecommendResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRecommendResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/GouniManikumar12/admesh-python#with_streaming_response
        """
        return AsyncRecommendResourceWithStreamingResponse(self)

    async def get_recommendations(
        self,
        *,
        query: str,
        format: Optional[str] | NotGiven = NOT_GIVEN,
        previous_query: Optional[str] | NotGiven = NOT_GIVEN,
        previous_summary: Optional[str] | NotGiven = NOT_GIVEN,
        session_id: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        raise_on_empty_recommendations: bool = True,
    ) -> RecommendGetRecommendationsResponse:
        """
        Get monetized product/tool recommendations

        Args:
          query: The user's query

          format: The format of the response (default: "auto")

          previous_query: The user's previous query

          previous_summary: Summary of the previous recommendation

          session_id: The session ID

          raise_on_empty_recommendations: Whether to raise a NoRecommendationsError when no recommendations are available (default: True)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        response = await self._post(
            "/agent/recommend",
            body=await async_maybe_transform(
                {
                    "query": query,
                    "format": format,
                    "previous_query": previous_query,
                    "previous_summary": previous_summary,
                    "session_id": session_id,
                },
                recommend_get_recommendations_params.RecommendGetRecommendationsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RecommendGetRecommendationsResponse,
        )

        # Check if recommendations are empty or null
        if (raise_on_empty_recommendations and
            (not response.response or
             not response.response.recommendations or
             len(response.response.recommendations) == 0)):
            raise NoRecommendationsError(f"No recommendations available for query: {query}")

        return response


class RecommendResourceWithRawResponse:
    def __init__(self, recommend: RecommendResource) -> None:
        self._recommend = recommend

        self.get_recommendations = to_raw_response_wrapper(
            recommend.get_recommendations,
        )


class AsyncRecommendResourceWithRawResponse:
    def __init__(self, recommend: AsyncRecommendResource) -> None:
        self._recommend = recommend

        self.get_recommendations = async_to_raw_response_wrapper(
            recommend.get_recommendations,
        )


class RecommendResourceWithStreamingResponse:
    def __init__(self, recommend: RecommendResource) -> None:
        self._recommend = recommend

        self.get_recommendations = to_streamed_response_wrapper(
            recommend.get_recommendations,
        )


class AsyncRecommendResourceWithStreamingResponse:
    def __init__(self, recommend: AsyncRecommendResource) -> None:
        self._recommend = recommend

        self.get_recommendations = async_to_streamed_response_wrapper(
            recommend.get_recommendations,
        )
