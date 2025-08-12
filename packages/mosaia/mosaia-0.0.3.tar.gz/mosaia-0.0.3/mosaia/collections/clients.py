"""
Clients API client for the Mosaia SDK.

Provides CRUD operations for managing OAuth client applications in the Mosaia platform.
Clients are OAuth applications that can authenticate with the Mosaia API through
various authentication flows.
"""

from typing import Any, Dict, Optional

from ..models.client import Client
from .base_collection import BaseCollection


class Clients(BaseCollection[Dict[str, Any], Client, Any, Any]):
    """
    Clients API client for the Mosaia SDK.

    Provides CRUD operations for managing OAuth client applications in the Mosaia platform.
    Clients are OAuth applications that can authenticate with the Mosaia API through
    various authentication flows.

    Examples:
        >>> from mosaia import Mosaia
        >>>
        >>> mosaia = Mosaia(api_key='your-api-key')
        >>> clients = mosaia.clients
        >>>
        # Get all clients
        >>> all_clients = await clients.get()
        >>>
        # Get a specific client
        >>> client = await clients.get({}, 'client-id')
        >>>
        # Create a new client
        >>> new_client = await clients.create({
        ...     'name': 'My App',
        ...     'client_id': 'my-app-client',
        ...     'redirect_uris': ['https://myapp.com/callback'],
        ...     'scopes': ['read', 'write']
        ... })
    """

    def __init__(self, uri: str = ""):
        """
        Creates a new Clients API client instance.

        Args:
            uri: Optional base URI path. If provided, the endpoint will be `${uri}/client`.
                  If not provided, defaults to `/client`.
        """
        super().__init__(f"{uri}/client", Client)
