"""
Mosaia Python SDK

A comprehensive Python SDK for the Mosaia AI platform.

This module provides the primary interface for interacting with the Mosaia API.
It exports the main MosaiaClient class, all collection classes for API operations,
model classes for data structures, authentication utilities, and configuration
management tools.

The SDK supports both API key and OAuth2 authentication methods, and provides
comprehensive access to all Mosaia platform features including user management,
organization management, AI agents, tools, applications, and more.

Examples:
    >>> from mosaia import MosaiaClient

    # Create a new Mosaia SDK instance
    >>> mosaia = MosaiaClient({
    ...     'api_key': 'your-api-key',
    ...     'api_url': 'https://api.mosaia.ai',
    ...     'version': '1'
    ... })

    # Get all users
    >>> users = await mosaia.users.get()

    # Create an OAuth instance
    >>> oauth = mosaia.oauth({
    ...     'redirect_uri': 'https://your-app.com/callback',
    ...     'scopes': ['read', 'write']
    ... })
"""

__version__ = "0.0.3"
__author__ = "Mosaia Team"
__email__ = "support@mosaia.ai"

from .api_client import APIClient

# Import auth
from .auth import MosaiaAuth, OAuth
from .base_api import BaseAPI

# Import main client class
from .client import MosaiaClient

# Import collections
from .collections import (
    AgentGroups,
    Agents,
    AppBots,
    Apps,
    BaseCollection,
    Clients,
    Models,
    Organizations,
    OrgUsers,
    Tools,
    Users,
)

# Import main components
from .config import DEFAULT_CONFIG, ConfigurationManager

# Import functions
from .functions import BaseFunctions, Chat, Completions

# Import models
from .models import (
    Agent,
    AgentGroup,
    App,
    AppBot,
    BaseModel,
    Client,
    Model,
    Organization,
    OrgUser,
    Session,
    Tool,
    User,
)
from .types import (
    AgentInterface,
    APIResponse,
    AppInterface,
    AuthType,
    BatchAPIResponse,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatMessage,
    ErrorResponse,
    GrantType,
    MosaiaConfig,
    OAuthConfig,
    OAuthErrorResponse,
    OAuthTokenResponse,
    OrganizationInterface,
    PagingInterface,
    QueryParams,
    SessionInterface,
    ToolInterface,
    UserInterface,
)

# Import utils
from .utils import (
    failure,
    is_sdk_error,
    is_timestamp_expired,
    is_valid_object_id,
    parse_error,
    query_generator,
    server_error_to_string,
    success,
)

__all__ = [
    # Main client
    "MosaiaClient",
    # Configuration
    "ConfigurationManager",
    "DEFAULT_CONFIG",
    # API components
    "APIClient",
    "BaseAPI",
    # Types
    "MosaiaConfig",
    "UserInterface",
    "OrganizationInterface",
    "AppInterface",
    "AgentInterface",
    "ToolInterface",
    "QueryParams",
    "APIResponse",
    "BatchAPIResponse",
    "ErrorResponse",
    "AuthType",
    "GrantType",
    "SessionInterface",
    "PagingInterface",
    "OAuthConfig",
    "OAuthTokenResponse",
    "OAuthErrorResponse",
    "ChatMessage",
    "ChatCompletionRequest",
    "ChatCompletionResponse",
    # Utils
    "is_valid_object_id",
    "parse_error",
    "query_generator",
    "is_timestamp_expired",
    "failure",
    "success",
    "server_error_to_string",
    "is_sdk_error",
    # Functions
    "BaseFunctions",
    "Chat",
    "Completions",
    # Auth
    "MosaiaAuth",
    "OAuth",
    # Models
    "BaseModel",
    "User",
    "App",
    "Session",
    "Agent",
    "Organization",
    "OrgUser",
    "AppBot",
    "AgentGroup",
    "Tool",
    "Client",
    "Model",
    # Collections
    "BaseCollection",
    "Agents",
    "Apps",
    "Users",
    "Organizations",
    "OrgUsers",
    "Tools",
    "Clients",
    "Models",
    "AppBots",
    "AgentGroups",
]

# Default export for single primary class pattern
__default__ = MosaiaClient
