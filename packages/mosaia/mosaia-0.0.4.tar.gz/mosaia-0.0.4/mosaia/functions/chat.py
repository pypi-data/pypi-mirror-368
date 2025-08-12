"""
Chat functions class for managing chat-related operations.

This class provides functionality for chat operations, including access to
chat completions. It extends BaseFunctions to inherit standard CRUD operations
while adding chat-specific functionality.
"""

from typing import Any, Dict, Optional

from .base_functions import BaseFunctions
from .completions import Completions


class Chat(BaseFunctions[Dict[str, Any], Any, Dict[str, Any]]):
    """
    Chat functions class for managing chat-related operations.

    This class provides functionality for chat operations, including access to
    chat completions. It extends BaseFunctions to inherit standard CRUD operations
    while adding chat-specific functionality.

    Examples:
        # Create a chat instance
        >>> chat = Chat('/agent/123')

        # Access completions
        >>> completions = chat.completions

        # Create a chat completion
        >>> response = await completions.create({
        ...     'messages': [
        ...         {'role': 'user', 'content': 'Hello, how are you?'}
        ...     ],
        ...     'max_tokens': 100,
        ...     'temperature': 0.7
        ... })
    """

    def __init__(self, uri: str = ""):
        """
        Creates a new Chat instance.

        Args:
            uri: Base URI for the chat endpoint (e.g., '/agent/123')

        Examples:
            # For agent chat
            >>> agent_chat = Chat('/agent/agent-id')

            # For model chat
            >>> model_chat = Chat('/model/model-id')

            # For agent group chat
            >>> group_chat = Chat('/agent-group/group-id')
        """
        super().__init__(f"{uri}/chat")  # Pass the chat endpoint URI to the base class

    @property
    def completions(self) -> Completions:
        """
        Get the completions instance for this chat.

        This property provides access to the Completions class, which handles
        chat completion requests to AI models.

        Returns:
            A new Completions instance configured for this chat endpoint

        Examples:
            >>> chat = Chat('/agent/123')
            >>> completions = chat.completions

            # Use completions to generate responses
            >>> response = await completions.create({
            ...     'messages': [
            ...         {'role': 'user', 'content': 'What is the weather like?'}
            ...     ]
            ... })
        """
        return Completions(self._uri)
