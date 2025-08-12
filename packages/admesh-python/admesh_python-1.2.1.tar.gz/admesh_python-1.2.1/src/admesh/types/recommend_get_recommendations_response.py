# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["RecommendGetRecommendationsResponse", "Intent", "Response", "ResponseRecommendation", "FollowupSuggestion"]


# No decision factors needed


class Intent(BaseModel):
    categories: Optional[List[str]] = None

    goal: Optional[str] = None

    llm_intent_confidence_score: Optional[float] = None

    known_mentions: Optional[List[str]] = None

    intent_type: Optional[str] = None

    intent_group: Optional[str] = None

    keywords: Optional[List[str]] = None

    # New dynamic intent detection fields
    is_ecommerce_query: Optional[bool] = None

    product_type: Optional[str] = None

    purchase_intent: Optional[str] = None

    tags: Optional[List[str]] = None


class ResponseRecommendation(BaseModel):
    # Core required fields
    ad_id: str
    admesh_link: str
    audience_segment: str
    availability: str
    brand: str
    brand_trust_score: float
    categories: List[str]
    description: str
    discount_percentage: float
    external_id: str
    image_url: str
    intent_match_score: float
    keywords: List[str]
    layout_type: str
    match_reason: str
    offer_trust_score: float
    price: float
    product_id: str
    rating: float
    reason: str
    recommendation_source: str
    source: str
    title: str
    trial_days: int
    url: str

    # Optional fields
    content_variations: Optional[dict] = None

    # Source information
    conversationText: Optional[str] = None
    badges: Optional[List[str]] = None

    # Legacy/compatibility fields (deprecated but maintained for backward compatibility)
    company_name: Optional[str] = None
    logo_url: Optional[str] = None
    trust_score: Optional[float] = None
    features: Optional[List[str]] = None
    has_free_tier: Optional[bool] = None
    integrations: Optional[List[str]] = None
    pricing: Optional[str] = None
    redirect_url: Optional[str] = None
    reviews_summary: Optional[str] = None
    reward_note: Optional[str] = None
    security: Optional[List[str]] = None
    slug: Optional[str] = None
    support: Optional[List[str]] = None


class FollowupSuggestion(BaseModel):
    label: Optional[str] = None

    query: Optional[str] = None

    product_mentions: Optional[List[str]] = None

    admesh_links: Optional[dict] = None

    session_id: Optional[str] = None


class Response(BaseModel):
    summary: Optional[str] = None

    recommendations: Optional[List[ResponseRecommendation]] = None

    followup_suggestions: Optional[List[FollowupSuggestion]] = None

    is_fallback: Optional[bool] = None

    recommendation_source: Optional[str] = None


class RecommendGetRecommendationsResponse(BaseModel):
    intent: Optional[Intent] = None

    response: Optional[Response] = None

    tokens_used: Optional[int] = None

    api_model_used: Optional[str] = FieldInfo(alias="model_used", default=None)

    recommendation_id: Optional[str] = None

    session_id: Optional[str] = None

    end_of_session: Optional[bool] = None
