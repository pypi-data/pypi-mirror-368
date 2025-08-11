# AgenticMem Python Client

A Python client library for interacting with the AgenticMem API. This client provides easy-to-use interfaces for managing user interactions and profiles.

## Installation

```bash
pip install agenticmem
```

## Quick Start

```python
from agenticmem import AgenticMemClient
from agenticmem_commons.api_schema.service_schemas import InteractionRequest
from agenticmem_commons.api_schema.retriever_schema import (
    SearchInteractionRequest,
    SearchUserProfileRequest,
    GetInteractionsRequest,
    GetUserProfilesRequest
)
from datetime import datetime

# Initialize the client
client = AgenticMemClient(api_key="your_api_key")

# Optional: Login with email/password
token = client.login(email="user@example.com", password="password123")

# Publish a user interaction
interaction = InteractionRequest(
    created_at=int(datetime.utcnow().timestamp()),
    content="User clicked on product X",
    user_action="click",
    user_action_description="Clicked on product details button"
)

response = client.publish_interaction(
    user_id="user123",
    request_id="req456",
    interaction_requests=[interaction]
)
print(f"Published interaction: {response.success} - {response.message}")

# Search user profiles
profiles_request = SearchUserProfileRequest(
    user_id="user123",
    search_query="recent interactions",
    top_k=5
)
profiles = client.search_profiles(profiles_request)
for profile in profiles.profiles:
    print(f"Profile {profile.profile_id}: {profile.profile_content}")

# Get user profiles directly
profiles_request = GetUserProfilesRequest(
    user_id="user123"
)
profiles = client.get_profiles(profiles_request)
for profile in profiles.profiles:
    print(f"Profile: {profile}")

# Search interactions
interactions_request = SearchInteractionRequest(
    user_id="user123",
    start_time=int(datetime(2024, 1, 1).timestamp()),
    end_time=int(datetime.utcnow().timestamp())
)
interactions = client.search_interactions(interactions_request)
for interaction in interactions.interactions:
    print(f"Interaction {interaction.interaction_id}: {interaction.content}")

# Get interactions directly
interactions_request = GetInteractionsRequest(
    user_id="user123"
)
interactions = client.get_interactions(interactions_request)
for interaction in interactions.interactions:
    print(f"Interaction: {interaction}")

# Get profile change log
change_log = client.get_profile_change_log()
print(f"Profile changes: {change_log}")
```

## Features

- Authentication
  - API key authentication
  - Email/password login
- User interaction management
  - Publish user interactions
  - Delete specific interactions
  - Search interactions with time range and filters
  - Get direct list of interactions
- User profile management
  - Search user profiles with customizable queries
  - Get direct list of user profiles
  - Delete specific profiles or profiles matching a search query
  - View profile change log history

## API Response Types

All API methods return strongly-typed responses:

- `login()` returns `Token`
- `publish_interaction()` returns `PublishUserInteractionResponse`
- `search_interactions()` returns `SearchInteractionResponse`
- `get_interactions()` returns `GetInteractionsResponse`
- `search_profiles()` returns `SearchUserProfileResponse`
- `get_profiles()` returns `GetUserProfilesResponse`
- `delete_profile()` returns `DeleteUserProfileResponse`
- `delete_interaction()` returns `DeleteUserInteractionResponse`
- `get_profile_change_log()` returns `ProfileChangeLogResponse`

## Documentation

For detailed documentation, please visit [docs link].

## License

MIT License
