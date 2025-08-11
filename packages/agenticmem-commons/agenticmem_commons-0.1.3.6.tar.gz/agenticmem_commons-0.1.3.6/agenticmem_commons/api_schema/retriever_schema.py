from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from agenticmem_commons.api_schema.service_schemas import (
    Interaction,
    UserProfile,
    RawFeedback,
    Feedback,
)


class SearchInteractionRequest(BaseModel):
    user_id: str
    request_id: Optional[str] = None
    query: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    top_k: Optional[int] = None
    most_recent_k: Optional[int] = None


class SearchUserProfileRequest(BaseModel):
    user_id: str
    generated_from_request_id: Optional[str] = None
    query: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    top_k: Optional[int] = 10
    source: Optional[str] = None
    custom_feature: Optional[str] = None
    threshold: Optional[float] = 0.7


class SearchInteractionResponse(BaseModel):
    success: bool
    interactions: list[Interaction]
    msg: Optional[str] = None


class SearchUserProfileResponse(BaseModel):
    success: bool
    user_profiles: list[UserProfile]
    msg: Optional[str] = None


class GetInteractionsRequest(BaseModel):
    user_id: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    top_k: Optional[int] = 30


class GetInteractionsResponse(BaseModel):
    success: bool
    interactions: list[Interaction]
    msg: Optional[str] = None


class GetUserProfilesRequest(BaseModel):
    user_id: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    top_k: Optional[int] = 30


class GetUserProfilesResponse(BaseModel):
    success: bool
    user_profiles: list[UserProfile]
    msg: Optional[str] = None


class SetConfigResponse(BaseModel):
    success: bool
    msg: Optional[str] = None


class GetRawFeedbacksRequest(BaseModel):
    limit: Optional[int] = 100
    feedback_name: Optional[str] = None


class GetRawFeedbacksResponse(BaseModel):
    success: bool
    raw_feedbacks: list[RawFeedback]
    msg: Optional[str] = None


class GetFeedbacksRequest(BaseModel):
    limit: Optional[int] = 100
    feedback_name: Optional[str] = None


class GetFeedbacksResponse(BaseModel):
    success: bool
    feedbacks: list[Feedback]
    msg: Optional[str] = None
