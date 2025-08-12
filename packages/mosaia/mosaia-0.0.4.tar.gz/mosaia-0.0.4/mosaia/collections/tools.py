"""
Tools API client for the Mosaia SDK.

Provides CRUD operations for managing external integrations in the Mosaia platform.
Tools are external integrations and utilities that agents can use to perform
specific tasks.
"""

from typing import Any, Dict, Optional

from ..models.tool import Tool
from .base_collection import BaseCollection


class Tools(BaseCollection[Dict[str, Any], Tool, Any, Any]):
    """
    Tools API client for the Mosaia SDK.

    Provides CRUD operations for managing external integrations in the Mosaia platform.
    Tools are external integrations and utilities that agents can use to perform
    specific tasks.

    Examples:
        >>> from mosaia import Mosaia
        >>>
        >>> mosaia = Mosaia(api_key='your-api-key')
        >>> tools = mosaia.tools
        >>>
        # Get all tools
        >>> all_tools = await tools.get()
        >>>
        # Get a specific tool
        >>> tool = await tools.get({}, 'tool-id')
        >>>
        # Create a new tool
        >>> new_tool = await tools.create({
        ...     'name': 'Weather API',
        ...     'friendly_name': 'Weather Information',
        ...     'short_description': 'Get weather information for any location',
        ...     'tool_schema': '{"type": "object", "properties": {"location": {"type": "string"}}}'
        ... })
    """

    def __init__(self, uri: str = ""):
        """
        Creates a new Tools API client instance.

        Args:
            uri: Optional base URI path. If provided, the endpoint will be `${uri}/tool`.
                  If not provided, defaults to `/tool`.
        """
        super().__init__(f"{uri}/tool", Tool)
