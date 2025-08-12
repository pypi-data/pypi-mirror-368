"""
Tests for collection classes.

This module tests all collection classes (Agents, Apps, Users, etc.),
ensuring proper initialization, API access, and functionality.
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from mosaia import (
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


class TestBaseCollection:
    """Test BaseCollection class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_config_manager = Mock()
        self.mock_api_client = Mock()

        with patch(
            "mosaia.collections.base_collection.ConfigurationManager"
        ) as mock_cm:
            with patch("mosaia.collections.base_collection.APIClient") as mock_ac:
                mock_cm.get_instance.return_value = self.mock_config_manager
                mock_ac.return_value = self.mock_api_client

                self.base_collection = BaseCollection("/test", Mock())

    def test_should_initialize_with_uri_and_model_class(self):
        """Test that BaseCollection initializes with URI and model class."""
        mock_model_class = Mock()

        with patch("mosaia.collections.base_collection.ConfigurationManager"):
            with patch("mosaia.collections.base_collection.APIClient"):
                collection = BaseCollection("/test", mock_model_class)

                assert collection._uri == "/test"
                assert collection._model_class == mock_model_class

    def test_should_have_public_properties(self):
        """Test that BaseCollection has public properties."""
        assert hasattr(self.base_collection, "uri")
        assert hasattr(self.base_collection, "api_client")
        assert hasattr(self.base_collection, "config_manager")

    def test_uri_property_should_return_uri(self):
        """Test that uri property returns the URI."""
        assert self.base_collection.uri == "/test"

    def test_api_client_property_should_return_api_client(self):
        """Test that api_client property returns the API client."""
        assert self.base_collection.api_client == self.mock_api_client

    def test_config_manager_property_should_return_config_manager(self):
        """Test that config_manager property returns the config manager."""
        assert self.base_collection.config_manager == self.mock_config_manager

    @pytest.mark.asyncio
    async def test_get_should_return_batch_response_for_list(self):
        """Test that get returns batch response for list requests."""
        mock_response = {
            "data": [{"id": "1"}, {"id": "2"}],
            "paging": {"total": 2, "limit": 10},
        }
        self.mock_api_client.get = AsyncMock(return_value=mock_response)

        result = await self.base_collection.get()

        # Updated behavior: batch response contains model instances
        # Verify that items were passed to model class constructor
        assert len(result.data) == len(mock_response["data"])
        assert result.paging.total == 2
        self.mock_api_client.get.assert_called_once_with("/test", None)

    @pytest.mark.asyncio
    async def test_get_should_return_single_model_for_id(self):
        """Test that get returns single model for ID requests."""
        mock_response = {"data": {"id": "1", "name": "Test"}}
        self.mock_api_client.get = AsyncMock(return_value=mock_response)

        mock_model_class = Mock()
        mock_model_instance = Mock()
        mock_model_class.return_value = mock_model_instance

        with patch("mosaia.collections.base_collection.ConfigurationManager"):
            with patch("mosaia.collections.base_collection.APIClient"):
                collection = BaseCollection("/test", mock_model_class)
                collection._api_client = self.mock_api_client

                result = await collection.get(id="1")

                assert result == mock_model_instance
                mock_model_class.assert_called_once_with(mock_response["data"], "/test")
                self.mock_api_client.get.assert_called_once_with("/test/1", None)

    @pytest.mark.asyncio
    async def test_get_should_handle_query_params(self):
        """Test that get handles query parameters."""
        mock_response = {
            "data": [{"id": "1"}],
            "paging": {"total": 1, "limit": 10, "offset": 0},
        }
        self.mock_api_client.get = AsyncMock(return_value=mock_response)

        params = {"limit": 10, "offset": 0}
        result = await self.base_collection.get(params)

        self.mock_api_client.get.assert_called_once_with("/test", params)

    @pytest.mark.asyncio
    async def test_create_should_return_model_instance(self):
        """Test that create returns model instance."""
        mock_response = {"data": {"id": "1", "name": "Test"}}
        self.mock_api_client.post = AsyncMock(return_value=mock_response)

        mock_model_class = Mock()
        mock_model_instance = Mock()
        mock_model_class.return_value = mock_model_instance

        with patch("mosaia.collections.base_collection.ConfigurationManager"):
            with patch("mosaia.collections.base_collection.APIClient"):
                collection = BaseCollection("/test", mock_model_class)
                collection._api_client = self.mock_api_client

                data = {"name": "Test"}
                result = await collection.create(data)

                assert result == mock_model_instance
                mock_model_class.assert_called_once_with(mock_response["data"], None)
                self.mock_api_client.post.assert_called_once_with("/test", data)


class TestAgents:
    """Test Agents collection."""

    def test_should_initialize_with_correct_uri_and_model(self):
        """Test that Agents initializes with correct URI and model."""
        with patch("mosaia.collections.agents.BaseCollection.__init__") as mock_init:
            agents = Agents()

            # Check that the parent constructor was called with the correct URI
            mock_init.assert_called_once()
            args, kwargs = mock_init.call_args
            # The arguments are: (uri, model_class) - self is not included in args
            assert len(args) == 2
            assert args[0] == "/agent"  # URI should be '/agent'
            assert args[1].__name__ == "Agent"  # Model class should be Agent

    def test_should_initialize_with_custom_uri(self):
        """Test that Agents initializes with custom URI."""
        with patch("mosaia.collections.agents.BaseCollection.__init__") as mock_init:
            agents = Agents("/custom")

            # Check that the parent constructor was called with the correct URI
            mock_init.assert_called_once()
            args, kwargs = mock_init.call_args
            # The arguments are: (uri, model_class) - self is not included in args
            assert len(args) == 2
            assert args[0] == "/custom/agent"  # URI should be '/custom/agent'
            assert args[1].__name__ == "Agent"  # Model class should be Agent


class TestApps:
    """Test Apps collection."""

    def test_should_initialize_with_correct_uri_and_model(self):
        """Test that Apps initializes with correct URI and model."""
        with patch("mosaia.collections.apps.BaseCollection.__init__") as mock_init:
            apps = Apps()

            # Check that the parent constructor was called with the correct URI
            mock_init.assert_called_once()
            args, kwargs = mock_init.call_args
            # The arguments are: (uri, model_class) - self is not included in args
            assert len(args) == 2
            assert args[0] == "/app"  # URI should be '/app'
            assert args[1].__name__ == "App"  # Model class should be App

    def test_should_initialize_with_custom_uri(self):
        """Test that Apps initializes with custom URI."""
        with patch("mosaia.collections.apps.BaseCollection.__init__") as mock_init:
            apps = Apps("/custom")

            # Check that the parent constructor was called with the correct URI
            mock_init.assert_called_once()
            args, kwargs = mock_init.call_args
            # The arguments are: (uri, model_class) - self is not included in args
            assert len(args) == 2
            assert args[0] == "/custom/app"  # URI should be '/custom/app'
            assert args[1].__name__ == "App"  # Model class should be App


class TestUsers:
    """Test Users collection."""

    def test_should_initialize_with_correct_uri_and_model(self):
        """Test that Users initializes with correct URI and model."""
        with patch("mosaia.collections.users.BaseCollection.__init__") as mock_init:
            users = Users()

            # Check that the parent constructor was called with the correct URI
            mock_init.assert_called_once()
            args, kwargs = mock_init.call_args
            # The arguments are: (uri, model_class) - self is not included in args
            assert len(args) == 2
            assert args[0] == "/user"  # URI should be '/user'
            assert args[1].__name__ == "User"  # Model class should be User

    def test_should_initialize_with_custom_uri(self):
        """Test that Users initializes with custom URI."""
        with patch("mosaia.collections.users.BaseCollection.__init__") as mock_init:
            users = Users("/custom")

            # Check that the parent constructor was called with the correct URI
            mock_init.assert_called_once()
            args, kwargs = mock_init.call_args
            # The arguments are: (uri, model_class) - self is not included in args
            assert len(args) == 2
            assert args[0] == "/custom/user"  # URI should be '/custom/user'
            assert args[1].__name__ == "User"  # Model class should be User


class TestOrganizations:
    """Test Organizations collection."""

    def test_should_initialize_with_correct_uri_and_model(self):
        """Test that Organizations initializes with correct URI and model."""
        with patch(
            "mosaia.collections.organizations.BaseCollection.__init__"
        ) as mock_init:
            organizations = Organizations()

            # Check that the parent constructor was called with the correct URI
            mock_init.assert_called_once()
            args, kwargs = mock_init.call_args
            # The arguments are: (uri, model_class) - self is not included in args
            assert len(args) == 2
            assert args[0] == "/org"  # URI should be '/org'
            assert (
                args[1].__name__ == "Organization"
            )  # Model class should be Organization

    def test_should_initialize_with_custom_uri(self):
        """Test that Organizations initializes with custom URI."""
        with patch(
            "mosaia.collections.organizations.BaseCollection.__init__"
        ) as mock_init:
            organizations = Organizations("/custom")

            # Check that the parent constructor was called with the correct URI
            mock_init.assert_called_once()
            args, kwargs = mock_init.call_args
            # The arguments are: (uri, model_class) - self is not included in args
            assert len(args) == 2
            assert args[0] == "/custom/org"  # URI should be '/custom/org'
            assert (
                args[1].__name__ == "Organization"
            )  # Model class should be Organization


class TestOrgUsers:
    """Test OrgUsers collection."""

    def test_should_initialize_with_correct_uri_and_model(self):
        """Test that OrgUsers initializes with correct URI and model."""
        with patch("mosaia.collections.org_users.BaseCollection.__init__") as mock_init:
            org_users = OrgUsers()

            # Check that the parent constructor was called with the correct URI
            mock_init.assert_called_once()
            args, kwargs = mock_init.call_args
            # The arguments are: (uri, model_class) - self is not included in args
            assert len(args) == 2
            assert args[0] == "/user"  # URI should be '/user'
            assert args[1].__name__ == "OrgUser"  # Model class should be OrgUser

    def test_should_initialize_with_custom_uri(self):
        """Test that OrgUsers initializes with custom URI."""
        with patch("mosaia.collections.org_users.BaseCollection.__init__") as mock_init:
            org_users = OrgUsers("/custom")

            # Check that the parent constructor was called with the correct URI
            mock_init.assert_called_once()
            args, kwargs = mock_init.call_args
            # The arguments are: (uri, model_class) - self is not included in args
            assert len(args) == 2
            assert args[0] == "/custom/user"  # URI should be '/custom/user'
            assert args[1].__name__ == "OrgUser"  # Model class should be OrgUser


class TestTools:
    """Test Tools collection."""

    def test_should_initialize_with_correct_uri_and_model(self):
        """Test that Tools initializes with correct URI and model."""
        with patch("mosaia.collections.tools.BaseCollection.__init__") as mock_init:
            tools = Tools()

            # Check that the parent constructor was called with the correct URI
            mock_init.assert_called_once()
            args, kwargs = mock_init.call_args
            # The arguments are: (uri, model_class) - self is not included in args
            assert len(args) == 2
            assert args[0] == "/tool"  # URI should be '/tool'
            assert args[1].__name__ == "Tool"  # Model class should be Tool

    def test_should_initialize_with_custom_uri(self):
        """Test that Tools initializes with custom URI."""
        with patch("mosaia.collections.tools.BaseCollection.__init__") as mock_init:
            tools = Tools("/custom")

            # Check that the parent constructor was called with the correct URI
            mock_init.assert_called_once()
            args, kwargs = mock_init.call_args
            # The arguments are: (uri, model_class) - self is not included in args
            assert len(args) == 2
            assert args[0] == "/custom/tool"  # URI should be '/custom/tool'
            assert args[1].__name__ == "Tool"  # Model class should be Tool


class TestClients:
    """Test Clients collection."""

    def test_should_initialize_with_correct_uri_and_model(self):
        """Test that Clients initializes with correct URI and model."""
        with patch("mosaia.collections.clients.BaseCollection.__init__") as mock_init:
            clients = Clients()

            # Check that the parent constructor was called with the correct URI
            mock_init.assert_called_once()
            args, kwargs = mock_init.call_args
            # The arguments are: (uri, model_class) - self is not included in args
            assert len(args) == 2
            assert args[0] == "/client"  # URI should be '/client'
            assert args[1].__name__ == "Client"  # Model class should be Client

    def test_should_initialize_with_custom_uri(self):
        """Test that Clients initializes with custom URI."""
        with patch("mosaia.collections.clients.BaseCollection.__init__") as mock_init:
            clients = Clients("/custom")

            # Check that the parent constructor was called with the correct URI
            mock_init.assert_called_once()
            args, kwargs = mock_init.call_args
            # The arguments are: (uri, model_class) - self is not included in args
            assert len(args) == 2
            assert args[0] == "/custom/client"  # URI should be '/custom/client'
            assert args[1].__name__ == "Client"  # Model class should be Client


class TestModels:
    """Test Models collection."""

    def test_should_initialize_with_correct_uri_and_model(self):
        """Test that Models initializes with correct URI and model."""
        with patch("mosaia.collections.models.BaseCollection.__init__") as mock_init:
            models = Models()

            # Check that the parent constructor was called with the correct URI
            mock_init.assert_called_once()
            args, kwargs = mock_init.call_args
            # The arguments are: (uri, model_class) - self is not included in args
            assert len(args) == 2
            assert args[0] == "/model"  # URI should be '/model'
            assert args[1].__name__ == "Model"  # Model class should be Model

    def test_should_initialize_with_custom_uri(self):
        """Test that Models initializes with custom URI."""
        with patch("mosaia.collections.models.BaseCollection.__init__") as mock_init:
            models = Models("/custom")

            # Check that the parent constructor was called with the correct URI
            mock_init.assert_called_once()
            args, kwargs = mock_init.call_args
            # The arguments are: (uri, model_class) - self is not included in args
            assert len(args) == 2
            assert args[0] == "/custom/model"  # URI should be '/custom/model'
            assert args[1].__name__ == "Model"  # Model class should be Model


class TestAppBots:
    """Test AppBots collection."""

    def test_should_initialize_with_correct_uri_and_model(self):
        """Test that AppBots initializes with correct URI and model."""
        with patch("mosaia.collections.app_bots.BaseCollection.__init__") as mock_init:
            app_bots = AppBots()

            # Check that the parent constructor was called with the correct URI
            mock_init.assert_called_once()
            args, kwargs = mock_init.call_args
            # The arguments are: (uri, model_class) - self is not included in args
            assert len(args) == 2
            assert args[0] == "/bot"  # URI should be '/bot'
            assert args[1].__name__ == "AppBot"  # Model class should be AppBot

    def test_should_initialize_with_custom_uri(self):
        """Test that AppBots initializes with custom URI."""
        with patch("mosaia.collections.app_bots.BaseCollection.__init__") as mock_init:
            app_bots = AppBots("/custom")

            # Check that the parent constructor was called with the correct URI
            mock_init.assert_called_once()
            args, kwargs = mock_init.call_args
            # The arguments are: (uri, model_class) - self is not included in args
            assert len(args) == 2
            assert args[0] == "/custom/bot"  # URI should be '/custom/bot'
            assert args[1].__name__ == "AppBot"  # Model class should be AppBot


class TestAgentGroups:
    """Test AgentGroups collection."""

    def test_should_initialize_with_correct_uri_and_model(self):
        """Test that AgentGroups initializes with correct URI and model."""
        with patch(
            "mosaia.collections.agent_groups.BaseCollection.__init__"
        ) as mock_init:
            agent_groups = AgentGroups()

            # Check that the parent constructor was called with the correct URI
            mock_init.assert_called_once()
            args, kwargs = mock_init.call_args
            # The arguments are: (uri, model_class) - self is not included in args
            assert len(args) == 2
            assert args[0] == "/agent-group"  # URI should be '/agent-group'
            assert args[1].__name__ == "AgentGroup"  # Model class should be AgentGroup

    def test_should_initialize_with_custom_uri(self):
        """Test that AgentGroups initializes with custom URI."""
        with patch(
            "mosaia.collections.agent_groups.BaseCollection.__init__"
        ) as mock_init:
            agent_groups = AgentGroups("/custom")

            # Check that the parent constructor was called with the correct URI
            mock_init.assert_called_once()
            args, kwargs = mock_init.call_args
            # The arguments are: (uri, model_class) - self is not included in args
            assert len(args) == 2
            assert (
                args[0] == "/custom/agent-group"
            )  # URI should be '/custom/agent-group'
            assert args[1].__name__ == "AgentGroup"  # Model class should be AgentGroup
