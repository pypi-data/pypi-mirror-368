"""
Tests for the main MosaiaClient class.

This module tests the main MosaiaClient class and its methods,
ensuring proper initialization, configuration management, and API access.
"""

from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from mosaia import ConfigurationManager, MosaiaClient, MosaiaConfig, SessionInterface


class TestMosaiaClient:
    """Test MosaiaClient class."""

    def setup_method(self):
        """Reset the singleton instance before each test."""
        # Reset the singleton instance
        ConfigurationManager._instance = None
        ConfigurationManager._config = None

    def test_constructor_should_initialize_with_provided_configuration(self):
        """Test that constructor initializes with provided configuration."""
        with patch("mosaia.client.ConfigurationManager") as mock_config_manager:
            mock_instance = Mock()
            mock_config_manager.get_instance.return_value = mock_instance

            config = MosaiaConfig(
                api_key="test-api-key", api_url="https://api.mosaia.ai"
            )
            client = MosaiaClient(config)

            mock_config_manager.get_instance.assert_called_once()
            mock_instance.initialize.assert_called_once_with(config)

    def test_constructor_should_initialize_with_minimal_configuration(self):
        """Test that constructor initializes with minimal configuration."""
        with patch("mosaia.client.ConfigurationManager") as mock_config_manager:
            mock_instance = Mock()
            mock_config_manager.get_instance.return_value = mock_instance

            minimal_config = MosaiaConfig(api_key="minimal-key")
            client = MosaiaClient(minimal_config)

            mock_instance.initialize.assert_called_once_with(minimal_config)

    def test_constructor_should_initialize_with_full_configuration(self):
        """Test that constructor initializes with full configuration."""
        with patch("mosaia.client.ConfigurationManager") as mock_config_manager:
            mock_instance = Mock()
            mock_config_manager.get_instance.return_value = mock_instance

            full_config = MosaiaConfig(
                api_key="full-key",
                version="2",
                api_url="https://custom-api.mosaia.ai",
                client_id="full-client-id",
                client_secret="full-client-secret",
                verbose=True,
                session=SessionInterface(
                    access_token="full-key",
                    refresh_token="refresh-token",
                    auth_type="oauth",
                    sub="user-123",
                    iat="1640995200",
                    exp="1640998800",
                ),
            )

            client = MosaiaClient(full_config)
            mock_instance.initialize.assert_called_once_with(full_config)

    def test_config_getter_should_return_current_configuration(self):
        """Test that config getter returns current configuration."""
        with patch("mosaia.client.ConfigurationManager") as mock_config_manager:
            mock_instance = Mock()
            mock_config_manager.get_instance.return_value = mock_instance

            expected_config = MosaiaConfig(api_key="test-key")
            mock_instance.get_config.return_value = expected_config

            client = MosaiaClient(MosaiaConfig(api_key="test-key"))
            config = client.config

            assert config == expected_config
            mock_instance.get_config.assert_called_once()

    def test_config_setter_should_update_configuration(self):
        """Test that config setter updates configuration."""
        with patch("mosaia.client.ConfigurationManager") as mock_config_manager:
            mock_instance = Mock()
            mock_config_manager.get_instance.return_value = mock_instance

            client = MosaiaClient(MosaiaConfig(api_key="test-key"))
            new_config = MosaiaConfig(api_key="new-key")
            client.config = new_config

            mock_instance.initialize.assert_called_with(new_config)

    def test_api_key_setter_should_update_api_key(self):
        """Test that api_key setter updates API key."""
        with patch("mosaia.client.ConfigurationManager") as mock_config_manager:
            mock_instance = Mock()
            mock_config_manager.get_instance.return_value = mock_instance

            client = MosaiaClient(MosaiaConfig(api_key="test-key"))
            client.api_key = "new-api-key"

            mock_instance.update_config.assert_called_with({"api_key": "new-api-key"})

    def test_version_setter_should_update_version(self):
        """Test that version setter updates version."""
        with patch("mosaia.client.ConfigurationManager") as mock_config_manager:
            mock_instance = Mock()
            mock_config_manager.get_instance.return_value = mock_instance

            client = MosaiaClient(MosaiaConfig(api_key="test-key"))
            client.version = "2"

            mock_instance.update_config.assert_called_with({"version": "2"})

    def test_api_url_setter_should_update_api_url(self):
        """Test that api_url setter updates API URL."""
        with patch("mosaia.client.ConfigurationManager") as mock_config_manager:
            mock_instance = Mock()
            mock_config_manager.get_instance.return_value = mock_instance

            client = MosaiaClient(MosaiaConfig(api_key="test-key"))
            client.api_url = "https://new-api.mosaia.ai"

            mock_instance.update_config.assert_called_with(
                {"api_url": "https://new-api.mosaia.ai"}
            )

    def test_client_id_setter_should_update_client_id(self):
        """Test that client_id setter updates client ID."""
        with patch("mosaia.client.ConfigurationManager") as mock_config_manager:
            mock_instance = Mock()
            mock_config_manager.get_instance.return_value = mock_instance

            client = MosaiaClient(MosaiaConfig(api_key="test-key"))
            client.client_id = "new-client-id"

            mock_instance.update_config.assert_called_with(
                {"client_id": "new-client-id"}
            )

    def test_client_secret_setter_should_update_client_secret(self):
        """Test that client_secret setter updates client secret."""
        with patch("mosaia.client.ConfigurationManager") as mock_config_manager:
            mock_instance = Mock()
            mock_config_manager.get_instance.return_value = mock_instance

            client = MosaiaClient(MosaiaConfig(api_key="test-key"))
            client.client_secret = "new-client-secret"

            mock_instance.update_config.assert_called_with(
                {"client_secret": "new-client-secret"}
            )

    def test_auth_property_should_return_mosaia_auth_instance(self):
        """Test that auth property returns MosaiaAuth instance."""
        with patch("mosaia.client.ConfigurationManager"):
            with patch("mosaia.client.MosaiaAuth") as mock_auth:
                client = MosaiaClient(MosaiaConfig(api_key="test-key"))
                auth = client.auth

                mock_auth.assert_called_once()
                assert auth == mock_auth.return_value

    def test_agents_property_should_return_agents_instance(self):
        """Test that agents property returns Agents instance."""
        with patch("mosaia.client.ConfigurationManager"):
            with patch("mosaia.client.Agents") as mock_agents:
                client = MosaiaClient(MosaiaConfig(api_key="test-key"))
                agents = client.agents

                mock_agents.assert_called_once()
                assert agents == mock_agents.return_value

    def test_apps_property_should_return_apps_instance(self):
        """Test that apps property returns Apps instance."""
        with patch("mosaia.client.ConfigurationManager"):
            with patch("mosaia.client.Apps") as mock_apps:
                client = MosaiaClient(MosaiaConfig(api_key="test-key"))
                apps = client.apps

                mock_apps.assert_called_once()
                assert apps == mock_apps.return_value

    def test_tools_property_should_return_tools_instance(self):
        """Test that tools property returns Tools instance."""
        with patch("mosaia.client.ConfigurationManager"):
            with patch("mosaia.client.Tools") as mock_tools:
                client = MosaiaClient(MosaiaConfig(api_key="test-key"))
                tools = client.tools

                mock_tools.assert_called_once()
                assert tools == mock_tools.return_value

    def test_users_property_should_return_users_instance(self):
        """Test that users property returns Users instance."""
        with patch("mosaia.client.ConfigurationManager"):
            with patch("mosaia.client.Users") as mock_users:
                client = MosaiaClient(MosaiaConfig(api_key="test-key"))
                users = client.users

                mock_users.assert_called_once()
                assert users == mock_users.return_value

    def test_organizations_property_should_return_organizations_instance(self):
        """Test that organizations property returns Organizations instance."""
        with patch("mosaia.client.ConfigurationManager"):
            with patch("mosaia.client.Organizations") as mock_organizations:
                client = MosaiaClient(MosaiaConfig(api_key="test-key"))
                organizations = client.organizations

                mock_organizations.assert_called_once()
                assert organizations == mock_organizations.return_value

    def test_agent_groups_property_should_return_agent_groups_instance(self):
        """Test that agent_groups property returns AgentGroups instance."""
        with patch("mosaia.client.ConfigurationManager"):
            with patch("mosaia.client.AgentGroups") as mock_agent_groups:
                client = MosaiaClient(MosaiaConfig(api_key="test-key"))
                agent_groups = client.agent_groups

                mock_agent_groups.assert_called_once()
                assert agent_groups == mock_agent_groups.return_value

    def test_models_property_should_return_models_instance(self):
        """Test that models property returns Models instance."""
        with patch("mosaia.client.ConfigurationManager"):
            with patch("mosaia.client.Models") as mock_models:
                client = MosaiaClient(MosaiaConfig(api_key="test-key"))
                models = client.models

                mock_models.assert_called_once()
                assert models == mock_models.return_value

    @pytest.mark.asyncio
    async def test_session_should_return_session_instance(self):
        """Test that session method returns Session instance."""
        with patch("mosaia.client.ConfigurationManager"):
            with patch("mosaia.client.APIClient") as mock_api_client:
                # Configure async context manager behavior
                mock_client_instance = AsyncMock()
                mock_api_client.return_value.__aenter__.return_value = (
                    mock_client_instance
                )
                mock_api_client.return_value.__aexit__ = AsyncMock()

                mock_response = {
                    "data": {"id": "user-123", "email": "test@example.com"}
                }
                mock_client_instance.get.return_value = mock_response

                with patch("mosaia.client.Session") as mock_session:
                    client = MosaiaClient(MosaiaConfig(api_key="test-key"))
                    session = await client.session()

                    mock_client_instance.get.assert_called_once_with("/self")
                    mock_session.assert_called_once_with(mock_response["data"])
                    assert session == mock_session.return_value

    @pytest.mark.asyncio
    async def test_session_should_handle_error_response(self):
        """Test that session method handles error responses."""
        with patch("mosaia.client.ConfigurationManager"):
            with patch("mosaia.client.APIClient") as mock_api_client:
                # Configure async context manager behavior
                mock_client_instance = AsyncMock()
                mock_api_client.return_value.__aenter__.return_value = (
                    mock_client_instance
                )
                mock_api_client.return_value.__aexit__ = AsyncMock()

                mock_response = {"error": {"message": "Authentication failed"}}
                mock_client_instance.get.return_value = mock_response

                client = MosaiaClient(MosaiaConfig(api_key="test-key"))

                # Now errors surface with their actual message
                with pytest.raises(Exception, match="Authentication failed"):
                    await client.session()

    @pytest.mark.asyncio
    async def test_session_should_handle_missing_configuration(self):
        """Test that session method handles missing configuration."""
        with patch("mosaia.client.ConfigurationManager") as mock_config_manager:
            mock_instance = Mock()
            mock_instance.get_config.return_value = None
            mock_config_manager.get_instance.return_value = mock_instance

            client = MosaiaClient(MosaiaConfig(api_key="test-key"))

            # Now raises a clear initialization message
            with pytest.raises(Exception, match="Mosaia is not initialized"):
                await client.session()

    def test_oauth_should_return_oauth_instance(self):
        """Test that oauth method returns OAuth instance."""
        with patch("mosaia.client.ConfigurationManager"):
            with patch("mosaia.client.OAuth") as mock_oauth:
                client = MosaiaClient(MosaiaConfig(api_key="test-key"))
                oauth_config = {"redirect_uri": "https://myapp.com/callback"}

                oauth = client.oauth(oauth_config)

                mock_oauth.assert_called_once_with(oauth_config)
                assert oauth == mock_oauth.return_value

    def test_oauth_should_handle_oauth_config(self):
        """Test that oauth method handles OAuth configuration."""
        with patch("mosaia.client.ConfigurationManager"):
            with patch("mosaia.client.OAuth") as mock_oauth:
                client = MosaiaClient(MosaiaConfig(api_key="test-key"))
                oauth_config = {
                    "redirect_uri": "https://myapp.com/callback",
                    "scopes": ["read", "write"],
                    "client_id": "client-id",
                }

                client.oauth(oauth_config)

                mock_oauth.assert_called_once_with(oauth_config)

    def test_oauth_should_handle_minimal_oauth_config(self):
        """Test that oauth method handles minimal OAuth configuration."""
        with patch("mosaia.client.ConfigurationManager"):
            with patch("mosaia.client.OAuth") as mock_oauth:
                client = MosaiaClient(MosaiaConfig(api_key="test-key"))
                oauth_config = {"redirect_uri": "https://myapp.com/callback"}

                client.oauth(oauth_config)

                mock_oauth.assert_called_once_with(oauth_config)

    def test_oauth_should_handle_full_oauth_config(self):
        """Test that oauth method handles full OAuth configuration."""
        with patch("mosaia.client.ConfigurationManager"):
            with patch("mosaia.client.OAuth") as mock_oauth:
                client = MosaiaClient(MosaiaConfig(api_key="test-key"))
                oauth_config = {
                    "redirect_uri": "https://myapp.com/callback",
                    "app_url": "https://mosaia.ai",
                    "scopes": ["read", "write", "admin"],
                    "client_id": "custom-client-id",
                    "api_url": "https://custom-api.mosaia.ai",
                    "api_version": "2",
                    "state": "csrf-protection-token",
                }

                client.oauth(oauth_config)

                mock_oauth.assert_called_once_with(oauth_config)
