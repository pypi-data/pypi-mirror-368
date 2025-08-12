# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

__all__ = ["RecommendGetRecommendationsParams"]


class RecommendGetRecommendationsParams(TypedDict, total=False):
    query: Required[str]

    format: Optional[str]

    previous_query: Optional[str]

    previous_summary: Optional[str]

    session_id: Optional[str]
