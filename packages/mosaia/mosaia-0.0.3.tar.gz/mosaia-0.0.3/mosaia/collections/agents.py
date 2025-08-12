"""
Agents API client for managing AI agents in the Mosaia platform.

This class provides comprehensive functionality for managing AI agents,
which are intelligent entities that can perform tasks, handle conversations,
and execute workflows based on their configuration and assigned tools.

Features:
- Create and configure AI agents
- Manage agent settings and properties
- Handle agent tools and capabilities
- Support for chat and completion operations
- Integration with models and tools
"""

from typing import Any, Dict, Optional

from ..models.agent import Agent
from .base_collection import BaseCollection


class Agents(BaseCollection[Dict[str, Any], Agent, Any, Any]):
    """
    Agents API client for managing AI agents in the Mosaia platform.

    This class provides comprehensive functionality for managing AI agents,
    which are intelligent entities that can perform tasks, handle conversations,
    and execute workflows based on their configuration and assigned tools.

    Features:
    - Create and configure AI agents
    - Manage agent settings and properties
    - Handle agent tools and capabilities
    - Support for chat and completion operations
    - Integration with models and tools

    Examples:
        # Basic agent operations
        >>> from mosaia import Mosaia
        >>>
        >>> mosaia = Mosaia(api_key='your-api-key')
        >>> agents = mosaia.agents
        >>>
        # List all agents with filtering
        >>> all_agents = await agents.get({
        ...     'limit': 10,
        ...     'q': 'support',
        ...     'active': True
        ... })
        >>>
        # Get a specific agent
        >>> agent = await agents.get({}, 'agent-id')
        >>>
        # Create a new agent
        >>> new_agent = await agents.create({
        ...     'name': 'Customer Support Agent',
        ...     'short_description': 'AI agent for handling customer inquiries',
        ...     'model': 'gpt-4',
        ...     'temperature': 0.7,
        ...     'max_tokens': 1000,
        ...     'system_prompt': 'You are a helpful customer support agent.'
        ... })

        # Using agent chat capabilities
        >>> agent = await agents.get({}, 'agent-id')
        >>> if agent:
        ...     # Use the new chat completions API
        ...     response = await agent.chat.completions.create({
        ...         'messages': [
        ...             {'role': 'user', 'content': 'How can I reset my password?'}
        ...         ],
        ...         'temperature': 0.7,
        ...         'max_tokens': 150
        ...     })
        ...     print('Agent response:', response['choices'][0]['message']['content'])
    """

    def __init__(self, uri: str = ""):
        """
        Creates a new Agents API client instance.

        Initializes an Agents collection for managing AI agents through the API.
        The collection provides methods for creating, retrieving, and managing
        agent configurations.

        Args:
            uri: Optional base URI path (e.g., '/org/123' for org-scoped agents)

        Examples:
            # Default initialization
            >>> # Uses /agent endpoint
            >>> agents = Agents()
            >>>
            # Create a new agent
            >>> agent = await agents.create({
            ...     'name': 'Support Bot',
            ...     'short_description': 'Customer support agent'
            ... })

            # Organization-scoped agents
            >>> # Uses /org/123/agent endpoint
            >>> org_agents = Agents('/org/123')
            >>>
            # List org's agents
            >>> agents = await org_agents.get({
            ...     'active': True,
            ...     'limit': 10
            ... })
        """
        super().__init__(f"{uri}/agent", Agent)
