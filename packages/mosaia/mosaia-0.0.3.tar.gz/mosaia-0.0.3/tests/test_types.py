"""
Tests for type definitions and interfaces.

This module tests all TypeScript interfaces and types defined in the SDK,
ensuring proper type validation and compatibility.
"""

from typing import Any, Dict, List

import pytest

from mosaia import (
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


class TestMosaiaConfig:
    """Test MosaiaConfig interface."""

    def test_should_allow_all_optional_properties(self):
        """Test that MosaiaConfig allows all optional properties."""
        config = MosaiaConfig(
            api_key="test-key",
            version="1",
            api_url="https://api.mosaia.ai",
            client_id="client-id",
            client_secret="client-secret",
            verbose=True,
            session=SessionInterface(
                access_token="test-key",
                refresh_token="refresh-token",
                auth_type="oauth",
                sub="user-123",
                iat="1640995200",
                exp="1640998800",
            ),
        )

        assert config.api_key == "test-key"
        assert config.session.auth_type == "oauth"

    def test_should_allow_partial_configuration(self):
        """Test that MosaiaConfig allows partial configuration."""
        partial_config = MosaiaConfig(api_key="test-key")

        assert partial_config.api_key == "test-key"
        assert partial_config.api_url is None


class TestUserInterface:
    """Test UserInterface interface."""

    def test_should_support_all_user_properties(self):
        """Test that UserInterface supports all user properties."""
        user = UserInterface(
            id="user-123",
            email="user@example.com",
            first_name="John",
            last_name="Doe",
            username="johndoe",
            name="John Doe",
            description="Software Engineer",
        )

        assert user.id == "user-123"
        assert user.email == "user@example.com"
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.username == "johndoe"
        assert user.name == "John Doe"
        assert user.description == "Software Engineer"


class TestOrganizationInterface:
    """Test OrganizationInterface interface."""

    def test_should_support_all_organization_properties(self):
        """Test that OrganizationInterface supports all organization properties."""
        org = OrganizationInterface(
            id="org-123",
            name="Acme Corp",
            short_description="Leading technology company",
        )

        assert org.id == "org-123"
        assert org.name == "Acme Corp"
        assert org.short_description == "Leading technology company"


class TestAppInterface:
    """Test AppInterface interface."""

    def test_should_support_all_app_properties(self):
        """Test that AppInterface supports all app properties."""
        app = AppInterface(
            id="app-123",
            name="My AI Assistant",
            short_description="AI-powered customer support assistant",
            external_app_url="https://myapp.com",
        )

        assert app.id == "app-123"
        assert app.name == "My AI Assistant"
        assert app.short_description == "AI-powered customer support assistant"
        assert app.external_app_url == "https://myapp.com"


class TestAgentInterface:
    """Test AgentInterface interface."""

    def test_should_support_all_agent_properties(self):
        """Test that AgentInterface supports all agent properties."""
        agent = AgentInterface(
            id="agent-123",
            name="Customer Support Agent",
            short_description="AI agent for handling customer inquiries",
            model="gpt-4",
            temperature=0.7,
            system_prompt="You are a helpful customer support agent.",
        )

        assert agent.id == "agent-123"
        assert agent.name == "Customer Support Agent"
        assert agent.short_description == "AI agent for handling customer inquiries"
        assert agent.model == "gpt-4"
        assert agent.temperature == 0.7
        assert agent.system_prompt == "You are a helpful customer support agent."


class TestToolInterface:
    """Test ToolInterface interface."""

    def test_should_support_all_tool_properties(self):
        """Test that ToolInterface supports all tool properties."""
        tool = ToolInterface(
            id="tool-123",
            name="Weather API",
            friendly_name="Weather Information",
            short_description="Get weather information for any location",
            tool_schema='{"type": "object", "properties": {"location": {"type": "string"}}}',
        )

        assert tool.id == "tool-123"
        assert tool.name == "Weather API"
        assert tool.friendly_name == "Weather Information"
        assert tool.short_description == "Get weather information for any location"
        assert (
            tool.tool_schema
            == '{"type": "object", "properties": {"location": {"type": "string"}}}'
        )


class TestQueryParams:
    """Test QueryParams interface."""

    def test_should_support_all_query_parameters(self):
        """Test that QueryParams supports all query parameters."""
        params = QueryParams(
            limit=10,
            offset=0,
            search="ai assistant",
            sort_by="created_at",
            sort_order="desc",
        )

        assert params.limit == 10
        assert params.offset == 0
        assert params.search == "ai assistant"
        assert params.sort_by == "created_at"
        assert params.sort_order == "desc"


class TestAPIResponse:
    """Test APIResponse interface."""

    def test_should_support_api_response_structure(self):
        """Test that APIResponse supports the correct structure."""
        response = APIResponse(
            data={"id": "test-123", "name": "Test"}, meta={"total": 1}, error=None
        )

        assert response.data == {"id": "test-123", "name": "Test"}
        assert response.meta == {"total": 1}
        assert response.error is None


class TestBatchAPIResponse:
    """Test BatchAPIResponse interface."""

    def test_should_support_batch_response_structure(self):
        """Test that BatchAPIResponse supports the correct structure."""
        response = BatchAPIResponse(
            data=[{"id": "test-1"}, {"id": "test-2"}],
            paging=PagingInterface(offset=0, limit=10, total=2, page=1, total_pages=1),
        )

        assert len(response.data) == 2
        assert response.data[0]["id"] == "test-1"
        assert response.data[1]["id"] == "test-2"
        assert response.paging.total == 2


class TestErrorResponse:
    """Test ErrorResponse interface."""

    def test_should_support_error_response_structure(self):
        """Test that ErrorResponse supports the correct structure."""
        error = ErrorResponse(
            message="Invalid API key provided",
            code="INVALID_API_KEY",
            status=401,
            more_info={"field": "api_key"},
        )

        assert error.message == "Invalid API key provided"
        assert error.code == "INVALID_API_KEY"
        assert error.status == 401
        assert error.more_info == {"field": "api_key"}


class TestPagingInterface:
    """Test PagingInterface interface."""

    def test_should_support_pagination_structure(self):
        """Test that PagingInterface supports the correct structure."""
        paging = PagingInterface(offset=20, limit=10, total=100, page=3, total_pages=10)

        assert paging.offset == 20
        assert paging.limit == 10
        assert paging.total == 100
        assert paging.page == 3
        assert paging.total_pages == 10


class TestSessionInterface:
    """Test SessionInterface interface."""

    def test_should_support_session_structure(self):
        """Test that SessionInterface supports the correct structure."""
        session = SessionInterface(
            access_token="test-access-token",
            refresh_token="test-refresh-token",
            exp="1640998800",
            user_id="user-123",
            org_id="org-456",
        )

        assert session.access_token == "test-access-token"
        assert session.refresh_token == "test-refresh-token"
        assert session.exp == "1640998800"
        assert session.user_id == "user-123"
        assert session.org_id == "org-456"


class TestOAuthConfig:
    """Test OAuthConfig interface."""

    def test_should_support_oauth_config_structure(self):
        """Test that OAuthConfig supports the correct structure."""
        oauth_config = OAuthConfig(
            redirect_uri="https://myapp.com/callback",
            app_url="https://mosaia.ai",
            scopes=["read", "write"],
            client_id="client-id",
            api_url="https://api.mosaia.ai",
            api_version="1",
            state="random-state",
        )

        assert oauth_config.redirect_uri == "https://myapp.com/callback"
        assert oauth_config.app_url == "https://mosaia.ai"
        assert oauth_config.scopes == ["read", "write"]
        assert oauth_config.client_id == "client-id"
        assert oauth_config.api_url == "https://api.mosaia.ai"
        assert oauth_config.api_version == "1"
        assert oauth_config.state == "random-state"


class TestOAuthTokenResponse:
    """Test OAuthTokenResponse interface."""

    def test_should_support_oauth_token_response_structure(self):
        """Test that OAuthTokenResponse supports the correct structure."""
        token_response = OAuthTokenResponse(
            access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            refresh_token="refresh-token-here",
            token_type="Bearer",
            expires_in=3600,
            sub="user-123",
            iat="1640995200",
            exp="1640998800",
        )

        assert token_response.access_token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        assert token_response.refresh_token == "refresh-token-here"
        assert token_response.token_type == "Bearer"
        assert token_response.expires_in == 3600
        assert token_response.sub == "user-123"
        assert token_response.iat == "1640995200"
        assert token_response.exp == "1640998800"


class TestOAuthErrorResponse:
    """Test OAuthErrorResponse interface."""

    def test_should_support_oauth_error_response_structure(self):
        """Test that OAuthErrorResponse supports the correct structure."""
        error_response = OAuthErrorResponse(
            error="invalid_grant",
            error_description="The authorization code has expired",
            error_uri="https://docs.mosaia.ai/oauth/errors",
        )

        assert error_response.error == "invalid_grant"
        assert error_response.error_description == "The authorization code has expired"
        assert error_response.error_uri == "https://docs.mosaia.ai/oauth/errors"


class TestChatMessage:
    """Test ChatMessage interface."""

    def test_should_support_chat_message_structure(self):
        """Test that ChatMessage supports the correct structure."""
        message = ChatMessage(
            role="user",
            content="Hello, how are you?",
            refusal=None,
            annotations=["annotation1", "annotation2"],
        )

        assert message.role == "user"
        assert message.content == "Hello, how are you?"
        assert message.refusal is None
        assert message.annotations == ["annotation1", "annotation2"]


class TestChatCompletionRequest:
    """Test ChatCompletionRequest interface."""

    def test_should_support_chat_completion_request_structure(self):
        """Test that ChatCompletionRequest supports the correct structure."""
        request = ChatCompletionRequest(
            model="gpt-4",
            messages=[
                ChatMessage(role="system", content="You are a helpful assistant."),
                ChatMessage(role="user", content="Hello, how are you?"),
            ],
            max_tokens=150,
            temperature=0.7,
            stream=False,
            logging=True,
            log_id="log-123",
        )

        assert request.model == "gpt-4"
        assert len(request.messages) == 2
        assert request.messages[0].role == "system"
        assert request.messages[1].role == "user"
        assert request.max_tokens == 150
        assert request.temperature == 0.7
        assert request.stream is False
        assert request.logging is True
        assert request.log_id == "log-123"


class TestChatCompletionResponse:
    """Test ChatCompletionResponse interface."""

    def test_should_support_chat_completion_response_structure(self):
        """Test that ChatCompletionResponse supports the correct structure."""
        response = ChatCompletionResponse(
            id="chatcmpl-123",
            object="chat.completion",
            created=1640995200,
            model="gpt-4",
            choices=[
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "Hello! I am doing well, thank you for asking.",
                    },
                    "finish_reason": "stop",
                }
            ],
            usage={"prompt_tokens": 10, "completion_tokens": 15, "total_tokens": 25},
            service_tier="standard",
            system_fingerprint="fp_123",
        )

        assert response.id == "chatcmpl-123"
        assert response.object == "chat.completion"
        assert response.created == 1640995200
        assert response.model == "gpt-4"
        assert len(response.choices) == 1
        assert response.choices[0]["index"] == 0
        assert response.service_tier == "standard"
        assert response.system_fingerprint == "fp_123"


class TestAuthType:
    """Test AuthType enum."""

    def test_should_support_all_auth_types(self):
        """Test that AuthType supports all authentication types."""
        assert AuthType.API_KEY == "api_key"
        assert AuthType.OAUTH2 == "oauth2"


class TestGrantType:
    """Test GrantType enum."""

    def test_should_support_all_grant_types(self):
        """Test that GrantType supports all grant types."""
        assert GrantType.AUTHORIZATION_CODE == "authorization_code"
        assert GrantType.CLIENT_CREDENTIALS == "client_credentials"
        assert GrantType.REFRESH_TOKEN == "refresh_token"
