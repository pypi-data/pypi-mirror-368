"""
Agent Groups API client for the Mosaia SDK.

Provides CRUD operations for managing agent collections in the Mosaia platform.
Agent Groups allow organizing and managing multiple AI agents together for
coordinated workflows.
"""

from typing import Any, Dict, Optional

from ..models.agent_group import AgentGroup
from .base_collection import BaseCollection


class AgentGroups(BaseCollection[Dict[str, Any], AgentGroup, Any, Any]):
    """
    Agent Groups API client for the Mosaia SDK.

    Provides CRUD operations for managing agent collections in the Mosaia platform.
    Agent Groups allow organizing and managing multiple AI agents together for
    coordinated workflows.

    Examples:
        >>> from mosaia import Mosaia
        >>>
        >>> mosaia = Mosaia(api_key='your-api-key')
        >>> agent_groups = mosaia.agent_groups
        >>>
        # Get all agent groups
        >>> all_agent_groups = await agent_groups.get()
        >>>
        # Get a specific agent group
        >>> agent_group = await agent_groups.get({}, 'agent-group-id')
        >>>
        # Create a new agent group
        >>> new_agent_group = await agent_groups.create({
        ...     'name': 'Support Team',
        ...     'short_description': 'Customer support agents',
        ...     'agents': ['agent-1', 'agent-2'],
        ...     'active': True
        ... })
    """

    def __init__(self, uri: str = ""):
        """
        Creates a new AgentGroups API client instance.

        Args:
            uri: Optional base URI path. If provided, the endpoint will be `${uri}/agent-group`.
                  If not provided, defaults to `/agent-group`.
        """
        super().__init__(f"{uri}/agent-group", AgentGroup)
