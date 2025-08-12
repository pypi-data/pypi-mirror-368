#!/usr/bin/env python3
"""
Test script for the Mosaia Python SDK models module.

This script tests the model classes to ensure they work correctly
and maintain parity with the Node.js SDK.
"""

from typing import Any, Dict

import pytest

# Test imports
from mosaia.models import (
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


@pytest.mark.models
class TestBaseModel:
    """Test BaseModel functionality."""

    def test_base_model_creation(self):
        """Test BaseModel can be instantiated."""
        # BaseModel is abstract, so we'll test with a concrete implementation
        user = User({"name": "Test User"})
        assert user is not None
        assert user.data["name"] == "Test User"

    def test_base_model_with_uri(self):
        """Test BaseModel with custom URI."""
        user = User({"name": "Test User"}, "/custom/user")
        assert user.uri == "/custom/user"

    def test_base_model_config_property(self):
        """Test BaseModel config property."""
        user = User({"name": "Test User"})
        config = user.config
        assert config is not None

    def test_base_model_is_active(self):
        """Test BaseModel is_active method."""
        user = User({"name": "Test User", "active": True})
        assert user.is_active() is True

        user_inactive = User({"name": "Test User", "active": False})
        assert user_inactive.is_active() is False

    def test_base_model_to_json(self):
        """Test BaseModel to_json method."""
        user_data = {"name": "Test User", "email": "test@example.com"}
        user = User(user_data)
        json_data = user.to_json()
        assert json_data["name"] == "Test User"
        assert json_data["email"] == "test@example.com"

    def test_base_model_to_api_payload(self):
        """Test BaseModel to_api_payload method."""
        user_data = {"id": "123", "name": "Test User", "email": "test@example.com"}
        user = User(user_data)
        payload = user.to_api_payload()
        assert "id" not in payload  # ID should be removed
        assert payload["name"] == "Test User"
        assert payload["email"] == "test@example.com"

    def test_base_model_update(self):
        """Test BaseModel update method."""
        user = User({"name": "Test User"})
        user.update({"email": "test@example.com", "age": 30})
        assert user.data["name"] == "Test User"
        assert user.data["email"] == "test@example.com"
        assert user.data["age"] == 30

    def test_base_model_has_id(self):
        """Test BaseModel has_id method."""
        user_with_id = User({"id": "123", "name": "Test User"})
        assert user_with_id.has_id() is True

        user_without_id = User({"name": "Test User"})
        assert user_without_id.has_id() is False

    def test_base_model_get_id(self):
        """Test BaseModel get_id method."""
        user = User({"id": "123", "name": "Test User"})
        assert user.get_id() == "123"

        user_without_id = User({"name": "Test User"})
        with pytest.raises(Exception, match="Entity ID is required"):
            user_without_id.get_id()

    def test_base_model_get_uri(self):
        """Test BaseModel get_uri method."""
        user = User({"id": "123", "name": "Test User"}, "/user")
        assert user.get_uri() == "/user/123"

        user_without_id = User({"name": "Test User"})
        # Updated behavior: when no ID is present, return base uri
        assert user_without_id.get_uri() == "/user"


@pytest.mark.models
class TestUser:
    """Test User model functionality."""

    def test_user_creation(self):
        """Test User can be instantiated."""
        user = User(
            {"username": "jsmith", "name": "John Smith", "email": "john@example.com"}
        )
        assert user is not None
        assert user.data["username"] == "jsmith"
        assert user.data["name"] == "John Smith"
        assert user.data["email"] == "john@example.com"

    def test_user_agents_property(self):
        """Test User agents property."""
        user = User({"name": "Test User"})
        agents = user.agents
        assert agents is not None
        assert hasattr(agents, "get")
        assert hasattr(agents, "create")

    def test_user_apps_property(self):
        """Test User apps property."""
        user = User({"name": "Test User"})
        apps = user.apps
        assert apps is not None
        assert hasattr(apps, "get")
        assert hasattr(apps, "create")

    def test_user_clients_property(self):
        """Test User clients property."""
        user = User({"name": "Test User"})
        clients = user.clients
        assert clients is not None
        assert hasattr(clients, "get")
        assert hasattr(clients, "create")

    def test_user_groups_property(self):
        """Test User groups property."""
        user = User({"name": "Test User"})
        groups = user.groups
        assert groups is not None
        assert hasattr(groups, "get")
        assert hasattr(groups, "create")

    def test_user_models_property(self):
        """Test User models property."""
        user = User({"name": "Test User"})
        models = user.models
        assert models is not None
        assert hasattr(models, "get")
        assert hasattr(models, "create")

    def test_user_orgs_property(self):
        """Test User orgs property."""
        user = User({"name": "Test User"})
        orgs = user.orgs
        assert orgs is not None
        assert hasattr(orgs, "get")
        assert hasattr(orgs, "create")

    def test_user_tools_property(self):
        """Test User tools property."""
        user = User({"name": "Test User"})
        tools = user.tools
        assert tools is not None
        assert hasattr(tools, "get")
        assert hasattr(tools, "create")


@pytest.mark.models
class TestAgent:
    """Test Agent model functionality."""

    def test_agent_creation(self):
        """Test Agent can be instantiated."""
        agent = Agent(
            {
                "name": "Support Agent",
                "short_description": "Customer support AI",
                "model": "gpt-4",
                "temperature": 0.7,
            }
        )
        assert agent is not None
        assert agent.data["name"] == "Support Agent"
        assert agent.data["model"] == "gpt-4"
        assert agent.data["temperature"] == 0.7

    def test_agent_chat_property(self):
        """Test Agent chat property."""
        agent = Agent({"name": "Test Agent"})
        chat = agent.chat
        assert chat is not None
        assert hasattr(chat, "completions")


@pytest.mark.models
class TestOrganization:
    """Test Organization model functionality."""

    def test_organization_creation(self):
        """Test Organization can be instantiated."""
        org = Organization(
            {
                "name": "Acme Corp",
                "short_description": "Technology company",
                "metadata": {"industry": "Technology", "size": "100-500"},
            }
        )
        assert org is not None
        assert org.data["name"] == "Acme Corp"
        assert org.data["short_description"] == "Technology company"

    def test_organization_agents_property(self):
        """Test Organization agents property."""
        org = Organization({"name": "Test Org"})
        agents = org.agents
        assert agents is not None
        assert hasattr(agents, "get")
        assert hasattr(agents, "create")

    def test_organization_apps_property(self):
        """Test Organization apps property."""
        org = Organization({"name": "Test Org"})
        apps = org.apps
        assert apps is not None
        assert hasattr(apps, "get")
        assert hasattr(apps, "create")

    def test_organization_users_property(self):
        """Test Organization users property."""
        org = Organization({"name": "Test Org"})
        users = org.users
        assert users is not None
        assert hasattr(users, "get")
        assert hasattr(users, "create")

    def test_organization_tools_property(self):
        """Test Organization tools property."""
        org = Organization({"name": "Test Org"})
        tools = org.tools
        assert tools is not None
        assert hasattr(tools, "get")
        assert hasattr(tools, "create")


@pytest.mark.models
class TestApp:
    """Test App model functionality."""

    def test_app_creation(self):
        """Test App can be instantiated."""
        app = App(
            {
                "name": "Task Manager",
                "short_description": "AI-powered task management",
                "metadata": {"category": "Productivity", "version": "1.0.0"},
            }
        )
        assert app is not None
        assert app.data["name"] == "Task Manager"
        assert app.data["short_description"] == "AI-powered task management"


@pytest.mark.models
class TestSession:
    """Test Session model functionality."""

    def test_session_creation(self):
        """Test Session can be instantiated."""
        session = Session({})
        assert session is not None


@pytest.mark.models
class TestOrgUser:
    """Test OrgUser model functionality."""

    def test_org_user_creation(self):
        """Test OrgUser can be instantiated."""
        org_user = OrgUser(
            {
                "user_id": "user-123",
                "org_id": "org-456",
                "permission": "admin",
                "role": "member",
            }
        )
        assert org_user is not None
        assert org_user.data["user_id"] == "user-123"
        assert org_user.data["org_id"] == "org-456"
        assert org_user.data["permission"] == "admin"


@pytest.mark.models
class TestAppBot:
    """Test AppBot model functionality."""

    def test_app_bot_creation(self):
        """Test AppBot can be instantiated."""
        app_bot = AppBot(
            {
                "app_id": "app-123",
                "bot_id": "bot-456",
                "config": {"enabled": True, "auto_reply": False},
            }
        )
        assert app_bot is not None
        assert app_bot.data["app_id"] == "app-123"
        assert app_bot.data["bot_id"] == "bot-456"


@pytest.mark.models
class TestAgentGroup:
    """Test AgentGroup model functionality."""

    def test_agent_group_creation(self):
        """Test AgentGroup can be instantiated."""
        group = AgentGroup(
            {
                "name": "Support Team",
                "description": "Customer support agents",
                "agents": ["agent-1", "agent-2", "agent-3"],
            }
        )
        assert group is not None
        assert group.data["name"] == "Support Team"
        assert group.data["description"] == "Customer support agents"


@pytest.mark.models
class TestTool:
    """Test Tool model functionality."""

    def test_tool_creation(self):
        """Test Tool can be instantiated."""
        tool = Tool(
            {
                "name": "Weather API",
                "type": "api",
                "config": {
                    "endpoint": "https://api.weather.com",
                    "api_key": "your-api-key",
                },
            }
        )
        assert tool is not None
        assert tool.data["name"] == "Weather API"
        assert tool.data["type"] == "api"


@pytest.mark.models
class TestClient:
    """Test Client model functionality."""

    def test_client_creation(self):
        """Test Client can be instantiated."""
        client = Client(
            {
                "name": "My App",
                "client_id": "client-123",
                "redirect_uri": "https://myapp.com/callback",
                "scopes": ["read", "write"],
            }
        )
        assert client is not None
        assert client.data["name"] == "My App"
        assert client.data["client_id"] == "client-123"


@pytest.mark.models
class TestModel:
    """Test Model model functionality."""

    def test_model_creation(self):
        """Test Model can be instantiated."""
        model = Model(
            {
                "name": "GPT-4",
                "type": "openai",
                "config": {"model": "gpt-4", "temperature": 0.7, "max_tokens": 1000},
            }
        )
        assert model is not None
        assert model.data["name"] == "GPT-4"
        assert model.data["type"] == "openai"


@pytest.mark.models
class TestModelsIntegration:
    """Test models integration."""

    def test_models_import(self):
        """Test that all models can be imported."""
        # Test that all required models exist
        assert User is not None
        assert App is not None
        assert Session is not None
        assert Agent is not None
        assert Organization is not None
        assert OrgUser is not None
        assert AppBot is not None
        assert AgentGroup is not None
        assert Tool is not None
        assert Client is not None
        assert Model is not None

    def test_models_inheritance(self):
        """Test that all models inherit from BaseModel."""
        models = [
            User,
            App,
            Session,
            Agent,
            Organization,
            OrgUser,
            AppBot,
            AgentGroup,
            Tool,
            Client,
            Model,
        ]

        for model_class in models:
            assert issubclass(model_class, BaseModel)

    def test_models_type_annotations(self):
        """Test that models have proper type annotations."""
        import inspect

        models = [
            User,
            App,
            Session,
            Agent,
            Organization,
            OrgUser,
            AppBot,
            AgentGroup,
            Tool,
            Client,
            Model,
        ]

        for model_class in models:
            sig = inspect.signature(model_class.__init__)
            assert "data" in sig.parameters
