"""
Models API client for the Mosaia SDK.

Provides CRUD operations for managing AI model configurations in the Mosaia platform.
Models are AI models that can be used by agents for various tasks such as
text generation and analysis.
"""

from typing import Any, Dict, Optional

from ..models.model import Model
from .base_collection import BaseCollection


class Models(BaseCollection[Dict[str, Any], Model, Any, Any]):
    """
    Models API client for the Mosaia SDK.

    Provides CRUD operations for managing AI model configurations in the Mosaia platform.
    Models are AI models that can be used by agents for various tasks such as
    text generation and analysis.

    Examples:
        >>> from mosaia import Mosaia
        >>>
        >>> mosaia = Mosaia(api_key='your-api-key')
        >>> models = mosaia.models
        >>>
        # Get all models
        >>> all_models = await models.get()
        >>>
        # Get a specific model
        >>> model = await models.get({}, 'model-id')
        >>>
        # Create a new model
        >>> new_model = await models.create({
        ...     'name': 'GPT-4',
        ...     'short_description': 'Advanced language model',
        ...     'provider': 'openai',
        ...     'model_id': 'gpt-4',
        ...     'max_tokens': 4096,
        ...     'temperature': 0.7
        ... })
    """

    def __init__(self, uri: str = ""):
        """
        Creates a new Models API client instance.

        Args:
            uri: Optional base URI path. If provided, the endpoint will be `${uri}/model`.
                  If not provided, defaults to `/model`.
        """
        super().__init__(f"{uri}/model", Model)
