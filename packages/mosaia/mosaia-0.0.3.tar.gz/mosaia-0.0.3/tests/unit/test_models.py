#!/usr/bin/env python3
"""
Test script for all the models to verify functionality and parity.
"""

from typing import Any, Dict

import pytest

# Import what we can, skip what doesn't exist yet
from mosaia import ConfigurationManager


@pytest.mark.unit
class TestModels:
    """Test model functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        # Initialize configuration for testing
        config_manager = ConfigurationManager.get_instance()
        config_manager.initialize(
            {
                "api_key": "test-key",
                "api_url": "https://api.mosaia.ai",
                "version": "1",
                "client_id": "test-client-id",
            }
        )

    def test_configuration_manager(self):
        """Test that ConfigurationManager works correctly."""
        config_manager = ConfigurationManager.get_instance()
        config = config_manager.get_config()

        assert config.api_key == "test-key"
        assert config.api_url == "https://api.mosaia.ai"
        assert config.version == "1"
        assert config.client_id == "test-client-id"

    def test_basic_types(
        self,
        sample_user_data,
        sample_organization_data,
        sample_agent_data,
        sample_app_data,
        sample_tool_data,
    ):
        """Test basic type creation."""
        from mosaia import (
            AgentInterface,
            AppInterface,
            OrganizationInterface,
            ToolInterface,
            UserInterface,
        )

        # Test User
        user = UserInterface(**sample_user_data)
        assert user.id == "user-123"
        assert user.email == "test@example.com"
        assert user.name == "Test User"

        # Test Organization
        org = OrganizationInterface(**sample_organization_data)
        assert org.id == "org-456"
        assert org.name == "Test Organization"

        # Test Agent
        agent = AgentInterface(**sample_agent_data)
        assert agent.id == "agent-789"
        assert agent.name == "Test Agent"
        assert agent.model == "gpt-4"

        # Test App
        app = AppInterface(**sample_app_data)
        assert app.id == "app-101"
        assert app.name == "Test App"

        # Test Tool
        tool = ToolInterface(**sample_tool_data)
        assert tool.id == "tool-202"
        assert tool.name == "Test Tool"

    def test_enum_types(self):
        """Test enum types."""
        from mosaia import AuthType, GrantType

        assert AuthType.API_KEY == "api_key"
        assert AuthType.OAUTH2 == "oauth2"
        assert GrantType.AUTHORIZATION_CODE == "authorization_code"
        assert GrantType.CLIENT_CREDENTIALS == "client_credentials"
        assert GrantType.REFRESH_TOKEN == "refresh_token"

    def test_response_types(self):
        """Test response type creation."""
        from mosaia import APIResponse, BatchAPIResponse, ErrorResponse, PagingInterface

        # Test APIResponse
        api_response = APIResponse(
            data={"id": "123", "name": "Test"}, meta={"total": 1}, error=None
        )
        assert api_response.data["id"] == "123"
        assert api_response.meta["total"] == 1
        assert api_response.error is None

        # Test BatchAPIResponse
        paging = PagingInterface(total=2, limit=10, offset=0)
        batch_response = BatchAPIResponse(
            data=[{"id": "1"}, {"id": "2"}], paging=paging
        )
        assert len(batch_response.data) == 2
        assert batch_response.paging.total == 2

        # Test ErrorResponse
        error_response = ErrorResponse(
            message="Test error",
            code="TEST_ERROR",
            status=400,
            more_info={"details": "test"},
        )
        assert error_response.message == "Test error"
        assert error_response.code == "TEST_ERROR"
        assert error_response.status == 400

    def test_query_params(self):
        """Test QueryParams creation."""
        from mosaia import QueryParams

        params = QueryParams(
            limit=10, offset=0, search="test", sort_by="created_at", sort_order="desc"
        )

        assert params.limit == 10
        assert params.offset == 0
        assert params.search == "test"
        assert params.sort_by == "created_at"
        assert params.sort_order == "desc"

    def test_session_interface(self):
        """Test SessionInterface creation."""
        from mosaia.types import SessionInterface

        session = SessionInterface(
            access_token="test-token",
            refresh_token="refresh-token",
            exp="1754078962511",
            user_id="user-123",
            org_id="org-456",
        )

        assert session.access_token == "test-token"
        assert session.refresh_token == "refresh-token"
        assert session.exp == "1754078962511"
        assert session.user_id == "user-123"
        assert session.org_id == "org-456"

    def test_mosaia_config(self, test_config):
        """Test MosaiaConfig creation."""
        from mosaia import MosaiaConfig

        config = MosaiaConfig(**test_config)

        assert config.api_key == "test-api-key"
        assert config.api_url == "https://test-api.mosaia.ai"
        assert config.version == "1"
        assert config.client_id == "test-client-id"
        assert config.client_secret == "test-client-secret"
        assert config.verbose is True
