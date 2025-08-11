from enum import IntEnum
from pydantic import BaseModel
from typing import Optional


class StorageConfigTest(IntEnum):
    UNKNOWN = 0
    INCOMPLETE = 1
    FAILED = 2
    SUCCEEDED = 3


class StorageConfigLocal(BaseModel):
    dir_path: str


class StorageConfigS3(BaseModel):
    s3_region: str
    s3_path: str
    s3_access_key: str
    s3_secret_key: str


class StorageConfigSupabase(BaseModel):
    url: str
    key: str
    db_url: str


StorageConfig = StorageConfigLocal | StorageConfigS3 | StorageConfigSupabase


class ProfileExtractorConfig(BaseModel):
    profile_content_definition_prompt: str
    context_prompt: Optional[str] = None
    metadata_definition_prompt: Optional[str] = None
    should_extract_profile_prompt_override: Optional[str] = None


class FeedbackAggregatorConfig(BaseModel):
    min_feedback_threshold: int = 2


class AgentFeedbackConfig(BaseModel):
    feedback_name: str
    feedback_definition_prompt: str
    feedback_context_prompt: Optional[str] = None
    metadata_definition_prompt: Optional[str] = None
    feedback_aggregator_config: Optional[FeedbackAggregatorConfig] = None


class Config(BaseModel):
    storage_config: StorageConfig
    storage_config_test: Optional[StorageConfigTest] = StorageConfigTest.UNKNOWN
    agent_context_prompt: Optional[str] = None
    # user level memory
    profile_extractor_configs: Optional[list[ProfileExtractorConfig]] = None
    # agent level feedback
    agent_feedback_configs: Optional[list[AgentFeedbackConfig]] = None
