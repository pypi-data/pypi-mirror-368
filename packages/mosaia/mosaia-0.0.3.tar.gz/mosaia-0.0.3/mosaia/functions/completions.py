"""
Completions functions class for managing chat completion operations.

This class handles chat completion requests to AI models, providing a
standardized interface for generating AI responses. It extends BaseFunctions
to inherit standard CRUD operations while specializing in chat completions.
"""

from typing import Any, Dict, List, Optional

from ..types import ChatCompletionResponse, ChatMessage
from .base_functions import BaseFunctions


class Completions(BaseFunctions[Dict[str, Any], Any, ChatCompletionResponse]):
    """
    Completions functions class for managing chat completion operations.

    This class handles chat completion requests to AI models, providing a
    standardized interface for generating AI responses. It extends BaseFunctions
    to inherit standard CRUD operations while specializing in chat completions.

    The class is typically accessed through the Chat class rather than
    instantiated directly.

    Examples:
        # Access through Chat class (recommended)
        >>> chat = Chat('/agent/123')
        >>> completions = chat.completions

        # Create a chat completion
        >>> response = await completions.create({
        ...     'messages': [
        ...         {'role': 'system', 'content': 'You are a helpful assistant.'},
        ...         {'role': 'user', 'content': 'Hello, how are you?'}
        ...     ],
        ...     'max_tokens': 150,
        ...     'temperature': 0.7,
        ...     'stream': False
        ... })
        >>> print('AI Response:', response['choices'][0]['message']['content'])
    """

    def __init__(self, uri: str = ""):
        """
        Creates a new Completions instance.

        Args:
            uri: Base URI for the completions endpoint (typically set by Chat class)

        Examples:
            # Usually accessed through Chat class
            >>> chat = Chat('/agent/123')
            >>> completions = chat.completions  # This calls the constructor internally

            # Direct instantiation (less common)
            >>> completions = Completions('/agent/123/chat')
        """
        super().__init__(
            f"{uri}/completions"
        )  # Pass the chat endpoint URI to the base class

    async def create(self, request: Dict[str, Any]) -> ChatCompletionResponse:
        """
        Create a chat completion.

        Args:
            request: Chat completion request parameters
                - messages: List of chat messages with role and content
                - max_tokens: Optional maximum tokens to generate
                - temperature: Optional temperature for response randomness
                - stream: Optional flag for streaming responses

        Returns:
            ChatCompletionResponse object containing the model's response

        Examples:
            >>> response = await completions.create({
            ...     'messages': [
            ...         {'role': 'user', 'content': 'Hello!'}
            ...     ]
            ... })
            >>> print(response.choices[0]['message']['content'])
        """
        try:
            response = await super().create(request)

            # Convert raw response to ChatCompletionResponse dataclass
            return ChatCompletionResponse(
                id=response.get("id", ""),
                object=response.get("object", ""),
                created=response.get("created", 0),
                model=response.get("model", ""),
                choices=response.get("choices", []),
                usage=response.get("usage"),
                service_tier=response.get("service_tier", ""),
                system_fingerprint=response.get("system_fingerprint", ""),
            )
        except Exception as error:
            raise self._handle_error(error)
