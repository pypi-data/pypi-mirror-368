"""
Model class for managing AI model configurations and operations.

This class represents an AI model in the Mosaia platform. It manages
model configurations, settings, and operations for AI models.
"""

from typing import Any, Dict, Optional

from ..functions.chat import Chat
from .base import BaseModel


class Model(BaseModel[Dict[str, Any]]):
    """
    Model class for managing AI model configurations and operations.

    This class represents an AI model in the Mosaia platform. It manages
    model configurations, settings, and operations for AI models.

    Features:
    - Model configuration
    - AI model management
    - Model settings
    - Model operations
    - Chat capabilities

    Examples:
        Basic model usage:
        >>> # Create AI model
        >>> model = Model({
        ...     'name': 'GPT-4',
        ...     'type': 'openai',
        ...     'config': {
        ...         'model': 'gpt-4',
        ...         'temperature': 0.7,
        ...         'max_tokens': 1000
        ...     }
        ... })
        >>>
        >>> await model.save()

        Using chat capabilities:
        >>> # Interact with the model
        >>> response = await model.chat.completions.create({
        ...     'messages': [
        ...         {'role': 'user', 'content': 'Explain quantum computing'}
        ...     ],
        ...     'temperature': 0.5,
        ...     'max_tokens': 500
        ... })
        >>>
        >>> print('Model response:', response['choices'][0]['message']['content'])
    """

    def __init__(self, data: Dict[str, Any], uri: Optional[str] = None):
        """
        Create a new Model instance.

        Initializes a model with the provided data and optional URI.
        The model represents an AI model configuration.

        Args:
            data: Model data dictionary
            uri: Optional URI path for the model endpoint. Defaults to '/model'

        Examples:
            >>> model = Model({
            ...     'name': 'GPT-4',
            ...     'type': 'openai',
            ...     'config': {'model': 'gpt-4', 'temperature': 0.7}
            ... })
        """
        super().__init__(data, uri or "/model")

    @property
    def chat(self) -> Chat:
        """
        Get the chat functionality for this model.

        This property provides access to the model's chat capabilities through
        the Chat class. It enables direct interaction with the model for
        text generation and completion tasks.

        Returns:
            A new Chat instance configured for this model

        Examples:
            Basic chat:
            >>> response = await model.chat.completions.create({
            ...     'messages': [
            ...         {'role': 'user', 'content': 'What is machine learning?'}
            ...     ]
            ... })

            Advanced chat with system prompt:
            >>> response = await model.chat.completions.create({
            ...     'messages': [
            ...         {
            ...             'role': 'system',
            ...             'content': 'You are an expert in artificial intelligence.'
            ...         },
            ...         {
            ...             'role': 'user',
            ...             'content': 'Explain neural networks to a beginner.'
            ...         }
            ...     ],
            ...     'temperature': 0.3,
            ...     'max_tokens': 1000,
            ...     'stream': False
            ... })
            >>>
            >>> print('Model explanation:', response['choices'][0]['message']['content'])
        """
        return Chat(self.get_uri())
