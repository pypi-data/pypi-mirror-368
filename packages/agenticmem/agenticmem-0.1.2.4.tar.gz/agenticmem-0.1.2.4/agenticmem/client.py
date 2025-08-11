from agenticmem_commons import IS_TEST_ENV
import aiohttp
from urllib.parse import urljoin
import requests
from typing import Optional, Union
from agenticmem_commons.api_schema.retriever_schema import (
    SearchInteractionRequest,
    SearchInteractionResponse,
    SearchUserProfileRequest,
    SearchUserProfileResponse,
    GetInteractionsRequest,
    GetInteractionsResponse,
    GetUserProfilesRequest,
    GetUserProfilesResponse,
    GetRawFeedbacksRequest,
    GetRawFeedbacksResponse,
    GetFeedbacksRequest,
    GetFeedbacksResponse,
)

if IS_TEST_ENV:
    BACKEND_URL = "http://127.0.0.1:8000"  # Local server for testing
else:
    BACKEND_URL = "http://agenticmem-test.us-west-2.elasticbeanstalk.com:8081"  # Elastic Beanstalk server url

from agenticmem_commons.api_schema.service_schemas import (
    InteractionRequest,
    ProfileChangeLogResponse,
    PublishUserInteractionRequest,
    PublishUserInteractionResponse,
    DeleteUserProfileRequest,
    DeleteUserProfileResponse,
    DeleteUserInteractionRequest,
    DeleteUserInteractionResponse,
)
from agenticmem_commons.api_schema.login_schema import Token
from agenticmem_commons.config_schema import Config


class AgenticMemClient:
    """Client for interacting with the AgenticMem API."""

    def __init__(self, api_key: str = "", url_endpoint: str = ""):
        """Initialize the AgenticMem client.

        Args:
            api_key (str): Your API key for authentication
        """
        self.api_key = api_key
        self.base_url = url_endpoint if url_endpoint else BACKEND_URL
        self.session = requests.Session()

    async def _make_async_request(
        self, method: str, endpoint: str, headers: Optional[dict] = None, **kwargs
    ):
        """Make an async HTTP request to the API."""
        url = urljoin(self.base_url, endpoint)

        headers = headers or {}
        if self.api_key:
            headers.update(
                {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
            )

        async with aiohttp.ClientSession() as async_session:
            response = await async_session.request(
                method, url, headers=headers, **kwargs
            )
            response.raise_for_status()
            return await response.json()

    def _make_request(
        self, method: str, endpoint: str, headers: Optional[dict] = None, **kwargs
    ):
        """Make an HTTP request to the API.

        Args:
            method (str): HTTP method (GET, POST, DELETE)
            endpoint (str): API endpoint
            headers (dict, optional): Additional headers to include in the request
            **kwargs: Additional arguments to pass to requests

        Returns:
            dict: API response
        """
        url = urljoin(self.base_url, endpoint)
        if self.api_key:
            self.session.headers.update(
                {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
            )
        if headers:
            self.session.headers.update(headers)
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()

    async def login(self, email: str, password: str) -> Token:
        """Async login to the AgenticMem API."""
        response = await self._make_async_request(
            "POST",
            "/token",
            data={"username": email, "password": password},
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "accept": "application/json",
            },
        )
        return Token(**response)

    async def publish_interaction(
        self,
        request_id: str,
        user_id: str,
        interaction_requests: list[Union[InteractionRequest, dict]],
        source: str = "",
        agent_version: str = "",
    ) -> PublishUserInteractionResponse:
        """Publish user interactions.

        Args:
            request_id (str): The request ID
            user_id (str): The user ID
            interaction_requests (List[InteractionRequest]): List of interaction requests
            source (str, optional): The source of the interaction
        Returns:
            PublishUserInteractionResponse: Response containing success status and message
        """
        interaction_requests = [
            (
                InteractionRequest(**interaction_request)
                if isinstance(interaction_request, dict)
                else interaction_request
            )
            for interaction_request in interaction_requests
        ]
        request = PublishUserInteractionRequest(
            request_id=request_id,
            user_id=user_id,
            interaction_requests=interaction_requests,
            source=source,
            agent_version=agent_version,
        )
        response = await self._make_async_request(
            "POST",
            "/api/publish_interaction",
            json=request.model_dump(),
        )
        return PublishUserInteractionResponse(**response)

    async def search_interactions(
        self,
        request: Union[SearchInteractionRequest, dict],
    ) -> SearchInteractionResponse:
        """Search for user interactions.

        Args:
            request (SearchInteractionRequest): The search request

        Returns:
            SearchInteractionResponse: Response containing matching interactions
        """
        if isinstance(request, dict):
            request = SearchInteractionRequest(**request)
        response = await self._make_async_request(
            "POST",
            "/api/search_interactions",
            json=request.model_dump(),
        )
        return SearchInteractionResponse(**response)

    async def search_profiles(
        self,
        request: Union[SearchUserProfileRequest, dict],
    ) -> SearchUserProfileResponse:
        """Search for user profiles.

        Args:
            request (SearchUserProfileRequest): The search request

        Returns:
            SearchUserProfileResponse: Response containing matching profiles
        """
        if isinstance(request, dict):
            request = SearchUserProfileRequest(**request)
        response = await self._make_async_request(
            "POST", "/api/search_profiles", json=request.model_dump()
        )
        return SearchUserProfileResponse(**response)

    async def delete_profile(
        self, user_id: str, profile_id: str = "", search_query: str = ""
    ) -> DeleteUserProfileResponse:
        """Delete user profiles.

        Args:
            user_id (str): The user ID
            profile_id (str, optional): Specific profile ID to delete
            search_query (str, optional): Query to match profiles for deletion

        Returns:
            DeleteUserProfileResponse: Response containing success status and message
        """
        request = DeleteUserProfileRequest(
            user_id=user_id,
            profile_id=profile_id,
            search_query=search_query,
        )
        response = await self._make_async_request(
            "DELETE", "/api/delete_profile", json=request.model_dump()
        )
        return DeleteUserProfileResponse(**response)

    async def delete_interaction(
        self, user_id: str, interaction_id: str
    ) -> DeleteUserInteractionResponse:
        """Delete a user interaction.

        Args:
            user_id (str): The user ID
            interaction_id (str): The interaction ID to delete

        Returns:
            DeleteUserInteractionResponse: Response containing success status and message
        """
        request = DeleteUserInteractionRequest(
            user_id=user_id, interaction_id=interaction_id
        )
        response = await self._make_async_request(
            "DELETE", "/api/delete_interaction", json=request.model_dump()
        )
        return DeleteUserInteractionResponse(**response)

    async def get_profile_change_log(self) -> ProfileChangeLogResponse:
        response = await self._make_async_request("GET", "/api/profile_change_log")
        return ProfileChangeLogResponse(**response)

    async def get_interactions(
        self,
        request: Union[GetInteractionsRequest, dict],
    ) -> GetInteractionsResponse:
        """Get user interactions.

        Args:
            request (GetInteractionsRequest): The list request

        Returns:
            GetInteractionsResponse: Response containing list of interactions
        """
        if isinstance(request, dict):
            request = GetInteractionsRequest(**request)
        response = await self._make_async_request(
            "POST",
            "/api/get_interactions",
            json=request.model_dump(),
        )
        return GetInteractionsResponse(**response)

    async def get_profiles(
        self,
        request: Union[GetUserProfilesRequest, dict],
    ) -> GetUserProfilesResponse:
        """Get user profiles.

        Args:
            request (GetUserProfilesRequest): The list request

        Returns:
            GetUserProfilesResponse: Response containing list of profiles
        """
        if isinstance(request, dict):
            request = GetUserProfilesRequest(**request)
        response = await self._make_async_request(
            "POST",
            "/api/get_profiles",
            json=request.model_dump(),
        )
        return GetUserProfilesResponse(**response)

    async def set_config(self, config: Union[Config, dict]) -> dict:
        """Set configuration for the organization.

        Args:
            config (Union[Config, dict]): The configuration to set

        Returns:
            dict: Response containing success status and message
        """
        if isinstance(config, dict):
            config = Config(**config)
        response = await self._make_async_request(
            "POST",
            "/api/set_config",
            json=config.model_dump(),
        )
        return response

    async def get_config(self) -> Config:
        """Get configuration for the organization.

        Returns:
            Config: The current configuration
        """
        response = await self._make_async_request(
            "GET",
            "/api/get_config",
        )
        return Config(**response)

    async def get_raw_feedbacks(
        self,
        request: Optional[Union[GetRawFeedbacksRequest, dict]] = None,
    ) -> GetRawFeedbacksResponse:
        """Get raw feedbacks.

        Args:
            request (Optional[Union[GetRawFeedbacksRequest, dict]]): The get request, defaults to empty request if None

        Returns:
            GetRawFeedbacksResponse: Response containing raw feedbacks
        """
        if request is None:
            request = GetRawFeedbacksRequest()
        elif isinstance(request, dict):
            request = GetRawFeedbacksRequest(**request)
        response = await self._make_async_request(
            "POST",
            "/api/get_raw_feedbacks",
            json=request.model_dump(),
        )
        return GetRawFeedbacksResponse(**response)

    async def get_feedbacks(
        self,
        request: Optional[Union[GetFeedbacksRequest, dict]] = None,
    ) -> GetFeedbacksResponse:
        """Get feedbacks.

        Args:
            request (Optional[Union[GetFeedbacksRequest, dict]]): The get request, defaults to empty request if None

        Returns:
            GetFeedbacksResponse: Response containing feedbacks
        """
        if request is None:
            request = GetFeedbacksRequest()
        elif isinstance(request, dict):
            request = GetFeedbacksRequest(**request)
        response = await self._make_async_request(
            "POST",
            "/api/get_feedbacks",
            json=request.model_dump(),
        )
        return GetFeedbacksResponse(**response)
