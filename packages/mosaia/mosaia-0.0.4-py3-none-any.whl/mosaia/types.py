"""
Type definitions for the Mosaia Python SDK.

This module contains all the type definitions, interfaces, and data structures
used throughout the SDK.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class AuthType(str, Enum):
    """Authentication types."""

    API_KEY = "api_key"
    OAUTH2 = "oauth2"


class GrantType(str, Enum):
    """OAuth2 grant types."""

    AUTHORIZATION_CODE = "authorization_code"
    CLIENT_CREDENTIALS = "client_credentials"
    REFRESH_TOKEN = "refresh_token"


@dataclass
class SessionInterface:
    """Session interface for authentication."""

    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    exp: Optional[str] = None
    user_id: Optional[str] = None
    org_id: Optional[str] = None
    auth_type: Optional[str] = None
    sub: Optional[str] = None
    iat: Optional[str] = None
    token_type: Optional[str] = None


@dataclass
class MosaiaConfig:
    """Configuration for the Mosaia SDK."""

    api_key: Optional[str] = None
    api_url: Optional[str] = None
    version: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    verbose: bool = False
    session: Optional[SessionInterface] = None


@dataclass
class UserInterface:
    """User interface."""

    id: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None


@dataclass
class OrganizationInterface:
    """Organization interface."""

    id: Optional[str] = None
    name: Optional[str] = None
    short_description: Optional[str] = None


@dataclass
class AppInterface:
    """Application interface."""

    id: Optional[str] = None
    name: Optional[str] = None
    short_description: Optional[str] = None
    external_app_url: Optional[str] = None


@dataclass
class AgentInterface:
    """Agent interface."""

    id: Optional[str] = None
    name: Optional[str] = None
    short_description: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = None
    system_prompt: Optional[str] = None


@dataclass
class ToolInterface:
    """Tool interface."""

    id: Optional[str] = None
    name: Optional[str] = None
    friendly_name: Optional[str] = None
    short_description: Optional[str] = None
    tool_schema: Optional[str] = None


@dataclass
class QueryParams:
    """Query parameters for API requests."""

    limit: Optional[int] = None
    offset: Optional[int] = None
    search: Optional[str] = None
    sort_by: Optional[str] = None
    sort_order: Optional[str] = None


@dataclass
class PagingInterface:
    """Pagination interface for list responses."""

    offset: Optional[int] = None
    limit: Optional[int] = None
    total: Optional[int] = None
    page: Optional[int] = None
    total_pages: Optional[int] = None


@dataclass
class APIResponse:
    """Standard API response."""

    data: Any = None
    meta: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class BatchAPIResponse:
    """Batch API response."""

    data: List[Any] = field(default_factory=list)
    paging: Optional[PagingInterface] = None


@dataclass
class ErrorResponse:
    """Error response."""

    message: str = ""
    code: str = "UNKNOWN_ERROR"
    status: int = 400
    more_info: Optional[Dict[str, Any]] = None


@dataclass
class OAuthConfig:
    """OAuth configuration interface."""

    redirect_uri: Optional[str] = None
    app_url: Optional[str] = None
    scopes: Optional[List[str]] = None
    client_id: Optional[str] = None
    api_url: Optional[str] = None
    api_version: Optional[str] = None
    state: Optional[str] = None


@dataclass
class OAuthTokenResponse:
    """OAuth token response interface."""

    access_token: str = ""
    refresh_token: Optional[str] = None
    token_type: str = "Bearer"
    expires_in: int = 0
    sub: str = ""
    iat: str = ""
    exp: str = ""


@dataclass
class OAuthErrorResponse:
    """OAuth error response interface."""

    error: str = ""
    error_description: Optional[str] = None
    error_uri: Optional[str] = None


@dataclass
class ChatMessage:
    """Chat message interface."""

    role: Optional[str] = None  # 'system' | 'user' | 'assistant'
    content: Optional[str] = None
    refusal: Optional[str] = None
    annotations: Optional[List[str]] = None


@dataclass
class ChatCompletionRequest:
    """Chat completion request interface."""

    model: Optional[str] = None
    messages: List[ChatMessage] = field(default_factory=list)
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    stream: Optional[bool] = None
    logging: Optional[bool] = None
    log_id: Optional[str] = None


@dataclass
class ChatCompletionResponse:
    """Chat completion response interface."""

    id: str = ""
    object: str = ""
    created: int = 0
    model: str = ""
    choices: List[Dict[str, Any]] = field(default_factory=list)
    usage: Optional[Dict[str, Any]] = None
    service_tier: str = ""
    system_fingerprint: str = ""
