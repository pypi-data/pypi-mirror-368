"""
Client class for managing OAuth client applications.

This class represents an OAuth client application that can authenticate with
the Mosaia API through various OAuth flows. It manages client credentials,
redirect URIs, and scopes for secure API access.

Features:
- OAuth client management
- Secure credential handling
- Redirect URI configuration
- Scope management
- Flow configuration

OAuth clients are essential for:
- Third-party application integration
- Secure API access
- User authentication flows
- Resource authorization
- Access token management

The class supports multiple OAuth 2.0 flows:
- Authorization Code (with PKCE)
- Client Credentials
- Resource Owner Password
"""

from typing import Any, Dict, Optional

from .base import BaseModel


class Client(BaseModel[Dict[str, Any]]):
    """
    Client class for managing OAuth client applications.

    This class represents an OAuth client application that can authenticate with
    the Mosaia API through various OAuth flows. It manages client credentials,
    redirect URIs, and scopes for secure API access.

    Features:
    - OAuth client management
    - Secure credential handling
    - Redirect URI configuration
    - Scope management
    - Flow configuration

    Examples:
        Basic client setup:
        >>> # Create an OAuth client for web application
        >>> web_client = Client({
        ...     'name': 'Web Dashboard',
        ...     'client_id': 'your-client-id',
        ...     'client_secret': 'your-client-secret',
        ...     'redirect_uris': ['https://app.example.com/oauth/callback'],
        ...     'scopes': ['read:users', 'write:data']
        ... })
        >>>
        >>> await web_client.save()

        Service account setup:
        >>> # Create a service account client
        >>> service_client = Client({
        ...     'name': 'Background Service',
        ...     'client_id': 'your-service-client-id',
        ...     'client_secret': 'your-service-client-secret',
        ...     'grant_types': ['client_credentials'],
        ...     'scopes': ['service:full'],
        ...     'metadata': {
        ...         'service': 'data-processor',
        ...         'environment': 'production'
        ...     }
        ... })
        >>>
        >>> if service_client.is_active():
        ...     print('Service client ready')
        ...     print('Available scopes:', service_client.scopes)
    """

    def __init__(self, data: Dict[str, Any], uri: Optional[str] = None):
        """
        Create a new OAuth client instance.

        Initializes an OAuth client application with the provided configuration.
        The client manages authentication and authorization for accessing the
        Mosaia API securely.

        Args:
            data: Configuration data including:
                  - name: Client application name
                  - client_id: OAuth client ID
                  - client_secret: OAuth client secret
                  - redirect_uris: Authorized redirect URIs
                  - scopes: Authorized scope list
                  - grant_types: Supported OAuth grant types
                  - metadata: Custom metadata object
            uri: Optional custom URI path for the client endpoint. Defaults to '/client'

        Examples:
            Web application client:
            >>> web_client = Client({
            ...     'name': 'Web App',
            ...     'client_id': 'your-client-id',
            ...     'client_secret': 'your-client-secret',
            ...     'redirect_uris': [
            ...         'https://app.example.com/oauth/callback',
            ...         'http://localhost:3000/callback'  # Development
            ...     ],
            ...     'scopes': ['read:users', 'write:data']
            ... })

            Machine-to-machine client:
            >>> service_client = Client({
            ...     'name': 'API Service',
            ...     'client_id': 'your-service-client-id',
            ...     'client_secret': 'your-service-client-secret',
            ...     'grant_types': ['client_credentials'],
            ...     'scopes': ['service:full'],
            ...     'metadata': {
            ...         'type': 'service-account',
            ...         'owner': 'system'
            ...     }
            ... }, '/service/client')
        """
        super().__init__(data, uri or "/client")
