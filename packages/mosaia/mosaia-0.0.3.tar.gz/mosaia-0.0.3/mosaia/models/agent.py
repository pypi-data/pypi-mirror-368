"""
Agent class for managing AI agent instances in the Mosaia SDK.

This class represents an AI agent that can perform tasks, handle conversations,
and execute workflows. Agents are the core AI entities in the platform,
providing natural language understanding and task automation capabilities.
"""

from typing import Any, Dict, Optional

from ..functions import Chat
from .base import BaseModel


class Agent(BaseModel[Dict[str, Any]]):
    """
    Agent class for managing AI agent instances in the Mosaia SDK.

    This class represents an AI agent that can perform tasks, handle conversations,
    and execute workflows. Agents are the core AI entities in the platform,
    providing natural language understanding and task automation capabilities.

    Features:
    - Agent configuration management
    - Chat and completion operations
    - Image/avatar management
    - Tool integration
    - Model configuration

    Examples:
        Basic agent usage:
        >>> # Create an agent instance
        >>> agent = Agent({
        ...     'name': 'Customer Support Agent',
        ...     'short_description': 'AI agent for customer inquiries',
        ...     'model': 'gpt-4',
        ...     'temperature': 0.7,
        ...     'system_prompt': 'You are a helpful customer support agent.'
        ... })
        >>>
        >>> # Upload an agent avatar
        >>> with open('agent-avatar.png', 'rb') as f:
        ...     await agent.upload_image(f)

        Using chat capabilities:
        >>> # Chat with the agent
        >>> response = await agent.chat.completions.create({
        ...     'messages': [
        ...         {'role': 'user', 'content': 'How can I reset my password?'}
        ...     ],
        ...     'temperature': 0.7,
        ...     'max_tokens': 150
        ... })
        >>>
        >>> print('Agent response:', response['choices'][0]['message']['content'])
    """

    def __init__(self, data: Dict[str, Any], uri: Optional[str] = None):
        """
        Create a new Agent instance.

        Initializes an agent with the provided configuration data and optional URI.
        The agent represents an AI entity that can perform intelligent tasks.

        Args:
            data: Agent configuration data
            uri: Optional URI path for the agent endpoint. Defaults to '/agent'

        Examples:
            >>> agent = Agent({
            ...     'name': 'Support Agent',
            ...     'short_description': 'Customer support AI',
            ...     'model': 'gpt-4',
            ...     'temperature': 0.7
            ... })
        """
        super().__init__(data, uri or "/agent")

    async def upload_image(self, file) -> "Agent":
        """
        Upload an image for the agent.

        Uploads an image file to be associated with the agent for branding
        and identification purposes.

        Args:
            file: Image file to upload (supports common image formats)

        Returns:
            Updated agent instance

        Raises:
            Error: When upload fails or network errors occur

        Examples:
            >>> with open('agent-avatar.png', 'rb') as f:
            ...     agent = await agent.upload_image(f)
            ...     print('Agent image uploaded successfully')
        """
        try:
            path = f"{self.get_uri()}/image/upload"
            response = await self.api_client.post_multipart(path, file)

            # Update with response payload
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
        Get the chat instance for this agent.

        This property provides access to the Chat class, which handles
        chat completion requests to the AI agent.

        Returns:
            Chat instance configured for this agent

        Examples:
            >>> # Chat with the agent
            >>> response = await agent.chat.completions.create({
            ...     'messages': [
            ...         {'role': 'user', 'content': 'What is the weather like?'}
            ...     ],
            ...     'max_tokens': 100,
            ...     'temperature': 0.7
            ... })
            >>>
            >>> print('Agent response:', response['choices'][0]['message']['content'])
        """
        return Chat(self.get_uri())
