#!/usr/bin/env python3
"""
Basic tests for the Mosaia Python SDK modules.

This script tests that all modules can be imported and basic functionality works.
"""

from typing import Any, Dict

import pytest

# Test imports
from mosaia import (
    AgentInterface,
    APIClient,
    APIResponse,
    AppInterface,
    AuthType,
    BaseAPI,
    BatchAPIResponse,
    ConfigurationManager,
    ErrorResponse,
    GrantType,
    MosaiaConfig,
    OrganizationInterface,
    QueryParams,
    ToolInterface,
    UserInterface,
)


@pytest.mark.unit
class TestConfigurationManager:
    """Test ConfigurationManager functionality."""

    def test_singleton_pattern(self, config_manager):
        """Test that ConfigurationManager follows singleton pattern."""
        instance1 = ConfigurationManager.get_instance()
        instance2 = ConfigurationManager.get_instance()
        assert instance1 is instance2

    def test_initialization(self, config_manager, test_config):
        """Test configuration initialization."""
        config_manager.initialize(test_config)
        config = config_manager.get_config()

        assert config.api_key == "test-api-key"
        assert config.api_url == "https://test-api.mosaia.ai"
        assert config.version == "1"
        assert config.verbose is True

    def test_uninitialized_error(self, config_manager):
        """Test error when accessing uninitialized config."""
        config_manager.reset()
        with pytest.raises(RuntimeError):
            config_manager.get_config()


@pytest.mark.unit
class TestTypes:
    """Test type definitions."""

    def test_user_interface(self, sample_user_data):
        """Test UserInterface creation."""
        user = UserInterface(**sample_user_data)

        assert user.id == "user-123"
        assert user.email == "test@example.com"
        assert user.first_name == "Test"
        assert user.last_name == "User"

    def test_organization_interface(self, sample_organization_data):
        """Test OrganizationInterface creation."""
        org = OrganizationInterface(**sample_organization_data)

        assert org.id == "org-456"
        assert org.name == "Test Organization"
        assert org.short_description == "A test organization"

    def test_agent_interface(self, sample_agent_data):
        """Test AgentInterface creation."""
        agent = AgentInterface(**sample_agent_data)

        assert agent.id == "agent-789"
        assert agent.name == "Test Agent"
        assert agent.model == "gpt-4"
        assert agent.temperature == 0.7

    def test_app_interface(self, sample_app_data):
        """Test AppInterface creation."""
        app = AppInterface(**sample_app_data)

        assert app.id == "app-101"
        assert app.name == "Test App"
        assert app.short_description == "A test application"

    def test_tool_interface(self, sample_tool_data):
        """Test ToolInterface creation."""
        tool = ToolInterface(**sample_tool_data)

        assert tool.id == "tool-202"
        assert tool.name == "Test Tool"
        assert tool.friendly_name == "Test Tool"

    def test_enums(self):
        """Test enum values."""
        assert AuthType.API_KEY == "api_key"
        assert AuthType.OAUTH2 == "oauth2"
        assert GrantType.AUTHORIZATION_CODE == "authorization_code"
        assert GrantType.CLIENT_CREDENTIALS == "client_credentials"
        assert GrantType.REFRESH_TOKEN == "refresh_token"


@pytest.mark.unit
class TestBaseAPI:
    """Test BaseAPI functionality."""

    def test_base_api_creation(self):
        """Test BaseAPI can be instantiated."""

        # Create a concrete implementation for testing
        class TestAPI(BaseAPI):
            pass

        api = TestAPI()
        assert api is not None
        assert hasattr(api, "client")


@pytest.mark.unit
class TestAPIClient:
    """Test APIClient functionality."""

    def test_client_creation(self):
        """Test APIClient can be created."""
        client = APIClient()
        assert client is not None
        assert hasattr(client, "base_url")
        assert hasattr(client, "headers")

    def test_headers_contain_auth(self):
        """Test that headers contain authorization."""
        client = APIClient()
        assert "Authorization" in client.headers
        assert "Content-Type" in client.headers

    def test_base_url_construction(self):
        """Test that base URL is constructed correctly with version."""
        config = MosaiaConfig(
            api_key="test-api-key", api_url="https://api.mosaia.ai", version="1"
        )
        client = APIClient(config)
        assert client.base_url == "https://api.mosaia.ai/v1"

    def test_base_url_with_different_version(self):
        """Test base URL construction with different version."""
        config = MosaiaConfig(
            api_key="test-api-key", api_url="https://api.mosaia.ai", version="2"
        )
        client = APIClient(config)
        assert client.base_url == "https://api.mosaia.ai/v2"

    def test_base_url_with_default_version(self):
        """Test base URL construction with default version."""
        config = MosaiaConfig(api_key="test-api-key", api_url="https://api.mosaia.ai")
        client = APIClient(config)
        assert client.base_url == "https://api.mosaia.ai/v1"
