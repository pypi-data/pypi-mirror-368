"""
Applications API client for the Mosaia SDK.

Provides CRUD operations for managing applications in the Mosaia platform.
Applications are the primary containers for AI-powered solutions and serve
as entry points for user interactions.
"""

from typing import Any, Dict, Optional

from ..models.app import App
from .base_collection import BaseCollection


class Apps(BaseCollection[Dict[str, Any], App, Any, Any]):
    """
    Applications API client for the Mosaia SDK.

    Provides CRUD operations for managing applications in the Mosaia platform.
    Applications are the primary containers for AI-powered solutions and serve
    as entry points for user interactions.

    Examples:
        >>> from mosaia import Mosaia
        >>>
        >>> mosaia = Mosaia(api_key='your-api-key')
        >>> apps = mosaia.apps
        >>>
        # Get all applications
        >>> all_apps = await apps.get()
        >>>
        # Get a specific application
        >>> app = await apps.get({}, 'app-id')
        >>>
        # Create a new application
        >>> new_app = await apps.create({
        ...     'name': 'Customer Support Portal',
        ...     'short_description': 'AI-powered customer support application',
        ...     'external_app_url': 'https://support.myapp.com',
        ...     'active': True
        ... })
    """

    def __init__(self, uri: str = ""):
        """
        Creates a new Apps API client instance.

        Args:
            uri: Optional base URI path. If provided, the endpoint will be `${uri}/app`.
                  If not provided, defaults to `/app`.
        """
        super().__init__(f"{uri}/app", App)
