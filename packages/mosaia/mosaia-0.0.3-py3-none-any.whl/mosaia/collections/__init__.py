"""
Collection client exports for the Mosaia SDK.

This module exports all the collection client classes that can be used to interact
with different resources on the Mosaia platform. Each client provides
methods for CRUD operations and specialized functionality.

## Available Collection Clients

- **Agents**: Manage AI agents for conversation and task execution
- **Apps**: Manage applications and their configurations
- **Auth**: Handle user authentication and session management
- **Users**: Manage user accounts and profiles
- **Organizations**: Manage organizational structures and settings
- **OrgUsers**: Handle user-organization relationships and permissions
- **Tools**: Manage external integrations and utilities
- **Clients**: Manage OAuth client applications
- **Models**: Manage AI model configurations
- **AppBots**: Handle application-bot integrations
- **AgentGroups**: Manage collections of AI agents

Examples:
    >>> from mosaia.collections import Apps, Tools, Agents, Auth

    # Create collection clients
    >>> apps = Apps()
    >>> tools = Tools()
    >>> agents = Agents()
    >>> auth = MosaiaAuth()

    # Use the clients
    >>> all_apps = await apps.get()
    >>> all_tools = await tools.get()
    >>> all_agents = await agents.get()
"""

from .agent_groups import AgentGroups
from .agents import Agents
from .app_bots import AppBots
from .apps import Apps
from .base_collection import BaseCollection
from .clients import Clients
from .models import Models
from .org_users import OrgUsers
from .organizations import Organizations
from .tools import Tools
from .users import Users

__all__ = [
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
