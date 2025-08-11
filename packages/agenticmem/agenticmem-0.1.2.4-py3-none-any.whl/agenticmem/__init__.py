__app_name__ = "agenticmem"
__version__ = "0.1.1"


from agenticmem.client import AgenticMemClient
from agenticmem_commons.api_schema.service_schemas import (
    UserActionType,
    ProfileTimeToLive,
    InteractionRequest,
    Interaction,
    UserProfile,
    PublishUserInteractionRequest,
    PublishUserInteractionResponse,
    DeleteUserProfileRequest,
    DeleteUserProfileResponse,
    DeleteUserInteractionRequest,
    DeleteUserInteractionResponse,
)
from agenticmem_commons.api_schema.retriever_schema import (
    SearchInteractionRequest,
    SearchUserProfileRequest,
    SearchInteractionResponse,
    SearchUserProfileResponse,
)
from agenticmem_commons.config_schema import (
    StorageConfigTest,
    StorageConfigLocal,
    StorageConfigS3,
    StorageConfigSupabase,
    StorageConfig,
    ProfileExtractorConfig,
    FeedbackAggregatorConfig,
    AgentFeedbackConfig,
    Config,
)

debug = False
log = None  # Set to either 'debug' or 'info', controls console logging


__all__ = [
    "AgenticMemClient",
    "UserActionType",
    "ProfileTimeToLive",
    "InteractionRequest",
    "Interaction",
    "UserProfile",
    "PublishUserInteractionRequest",
    "PublishUserInteractionResponse",
    "DeleteUserProfileRequest",
    "DeleteUserProfileResponse",
    "DeleteUserInteractionRequest",
    "DeleteUserInteractionResponse",
    "SearchInteractionRequest",
    "SearchUserProfileRequest",
    "SearchInteractionResponse",
    "SearchUserProfileResponse",
    "StorageConfigTest",
    "StorageConfigLocal",
    "StorageConfigS3",
    "StorageConfigSupabase",
    "StorageConfig",
    "ProfileExtractorConfig",
    "FeedbackAggregatorConfig",
    "AgentFeedbackConfig",
    "Config",
]
