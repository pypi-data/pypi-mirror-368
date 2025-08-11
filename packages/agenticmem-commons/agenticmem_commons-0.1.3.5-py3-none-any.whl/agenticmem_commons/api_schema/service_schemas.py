import enum
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

# OS-agnostic "never expires" timestamp (January 1, 2100 00:00:00 UTC)
# This is well within the safe range for all systems (32-bit timestamp limit is 2038)
NEVER_EXPIRES_TIMESTAMP = 4102444800


class UserActionType(str, enum.Enum):
    CLICK = "click"
    SCROLL = "scroll"
    TYPE = "type"
    NONE = "none"


class ProfileTimeToLive(str, enum.Enum):
    ONE_DAY = "one_day"
    ONE_WEEK = "one_week"
    ONE_MONTH = "one_month"
    ONE_QUARTER = "one_quarter"
    ONE_YEAR = "one_year"
    INFINITY = "infinity"


# information about the user interaction sent by the client
class Interaction(BaseModel):
    interaction_id: str
    user_id: str
    request_id: str
    created_at: int = int(datetime.utcnow().timestamp())
    role: str = "User"
    content: str = ""
    user_action: UserActionType = UserActionType.NONE
    user_action_description: str = ""
    interacted_image_url: str = ""
    image_encoding: str = ""  # base64 encoded image
    embedding: list[float] = []


# information about the user profile generated from the user interaction
# output of the profile generation service send back to the client
class UserProfile(BaseModel):
    profile_id: str
    user_id: str
    profile_content: str
    last_modified_timestamp: int
    generated_from_request_id: str
    profile_time_to_live: ProfileTimeToLive = ProfileTimeToLive.INFINITY
    # this is the expiration date calculated based on last modified timestamp and profile time to live instead of generated timestamp
    expiration_timestamp: int = NEVER_EXPIRES_TIMESTAMP
    custom_features: Optional[dict] = None
    source: str = ""
    embedding: list[float] = []


# delete user profile request
class DeleteUserProfileRequest(BaseModel):
    user_id: str
    profile_id: str = ""
    search_query: str = ""


# delete user profile response
class DeleteUserProfileResponse(BaseModel):
    success: bool
    message: str = ""


# delete user interaction request
class DeleteUserInteractionRequest(BaseModel):
    user_id: str
    interaction_id: str


# delete user interaction response
class DeleteUserInteractionResponse(BaseModel):
    success: bool
    message: str = ""


# user provided interaction request information
class InteractionRequest(BaseModel):
    created_at: int = int(datetime.utcnow().timestamp())
    role: str = "User"
    content: str = ""
    user_action: UserActionType = UserActionType.NONE
    user_action_description: str = ""
    interacted_image_url: str = ""
    image_encoding: str = ""  # base64 encoded image


# publish user interaction request
class PublishUserInteractionRequest(BaseModel):
    user_id: str
    request_id: str
    interaction_requests: list[InteractionRequest]
    source: str = ""
    agent_version: str = (
        ""  # this is used for aggregating interactions for generating agent feedback
    )


# publish user interaction response
class PublishUserInteractionResponse(BaseModel):
    success: bool
    message: str = ""


class ProfileChangeLog(BaseModel):
    id: int
    user_id: str
    request_id: str
    created_at: int = int(datetime.utcnow().timestamp())
    added_profiles: list[UserProfile]
    removed_profiles: list[UserProfile]
    mentioned_profiles: list[UserProfile]


class ProfileChangeLogResponse(BaseModel):
    success: bool
    profile_change_logs: list[ProfileChangeLog]


# raw feedback for agents
class RawFeedback(BaseModel):
    raw_feedback_id: int = 0
    agent_version: str
    request_id: str
    feedback_name: str = ""
    created_at: int = int(datetime.utcnow().timestamp())
    feedback_content: str = ""
    embedding: list[float] = []


class FeedbackStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Feedback(BaseModel):
    feedback_id: int = 0
    feedback_name: str = ""
    agent_version: str
    created_at: int = int(datetime.utcnow().timestamp())
    feedback_content: str
    feedback_status: FeedbackStatus
    feedback_metadata: str
    embedding: list[float] = []


class RegenerateFeedbacksRequest(BaseModel):
    agent_version: str
    feedback_name: str


class RegenerateFeedbacksResponse(BaseModel):
    success: bool
    message: str = ""
