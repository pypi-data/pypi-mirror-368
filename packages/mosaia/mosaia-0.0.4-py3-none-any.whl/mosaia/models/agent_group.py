"""
AgentGroup class for managing AI agent collections.

This class represents a collection of AI agents in the Mosaia platform.
It manages groups of agents that can work together or be organized
for specific purposes.
"""

from typing import Any, Dict, Optional

from ..functions.chat import Chat
from .base import BaseModel


class AgentGroup(BaseModel[Dict[str, Any]]):
    """
    AgentGroup class for managing AI agent collections.

    This class represents a collection of AI agents in the Mosaia platform.
    It manages groups of agents that can work together or be organized
    for specific purposes.

    Features:
    - Agent grouping
    - Collection management
    - Group coordination
    - Agent organization
    - Collaborative chat capabilities
    - Group branding/image management

    Examples:
        Basic agent group usage:
        >>> # Create agent group
        >>> group = AgentGroup({
        ...     'name': 'Support Team',
        ...     'description': 'Customer support agents',
        ...     'agents': ['agent-1', 'agent-2', 'agent-3']
        ... })
        >>>
        >>> await group.save()

        Using collaborative chat capabilities:
        >>> # Engage with the agent group
        >>> response = await group.chat.completions.create({
        ...     'messages': [
        ...         {'role': 'user', 'content': 'I have a billing question about my subscription.'}
        ...     ],
        ...     'temperature': 0.7
        ... })
        >>>
        >>> print('Team response:', response['choices'][0]['message']['content'])

        Uploading group branding:
        >>> # Upload a group logo
        >>> with open('team-logo.png', 'rb') as f:
        ...     group = await group.upload_image(f)
        ...     print('Group logo uploaded successfully')
    """

    def __init__(self, data: Dict[str, Any], uri: Optional[str] = None):
        """
        Create a new AgentGroup instance.

        Initializes an agent group with the provided data and optional URI.
        The agent group represents a collection of AI agents.

        Args:
            data: AgentGroup data dictionary
            uri: Optional URI path for the agent group endpoint. Defaults to '/group'

        Examples:
            >>> group = AgentGroup({
            ...     'name': 'Support Team',
            ...     'description': 'Customer support agents'
            ... })
        """
        super().__init__(data, uri or "/group")

    async def upload_image(self, file) -> "AgentGroup":
        """
        Upload an image for the agent group.

        Uploads an image file to be associated with the agent group for branding
        and identification purposes.

        Args:
            file: Image file to upload (supports common image formats)

        Returns:
            Updated agent group instance

        Raises:
            Error: When upload fails or network errors occur

        Examples:
            >>> # Upload a group logo
            >>> with open('team-logo.png', 'rb') as f:
            ...     group = await group.upload_image(f)
            ...     print('Group logo uploaded successfully')
        """
        try:
            path = f"{self.get_uri()}/image/upload"
            response = await self.api_client.post_multipart(path, file)

            if isinstance(response, dict):
                data = response.get("data", response)
                if isinstance(data, dict):
                    self.update(data)
            return self
        except Exception as error:
            raise self._handle_error(error)

    @property
    def chat(self) -> Chat:
        """
        Get the chat functionality for this agent group.

        This property provides access to the group's collaborative chat capabilities
        through the Chat class. It enables coordinated responses from multiple
        agents within the group.

        Returns:
            A new Chat instance configured for this agent group

        Examples:
            Basic group chat:
            >>> response = await group.chat.completions.create({
            ...     'messages': [
            ...         {'role': 'user', 'content': 'I need help with a complex issue.'}
            ...     ]
            ... })

            Advanced group chat with context:
            >>> response = await group.chat.completions.create({
            ...     'messages': [
            ...         {
            ...             'role': 'system',
            ...             'content': 'You are a collaborative team of experts.'
            ...         },
            ...         {
            ...             'role': 'user',
            ...             'content': 'This problem requires both technical and billing expertise.'
            ...         }
            ...     ],
            ...     'temperature': 0.7,
            ...     'max_tokens': 200
            ... })
            >>>
            >>> print('Team response:', response['choices'][0]['message']['content'])
        """
        return Chat(self.get_uri())
