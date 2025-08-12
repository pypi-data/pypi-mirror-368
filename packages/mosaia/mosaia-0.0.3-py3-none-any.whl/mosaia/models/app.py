"""
App class for managing AI-powered applications.

This class represents an application in the Mosaia platform, serving as a
container and orchestrator for AI solutions. Apps provide the structure and
configuration for deploying and managing AI capabilities.

Features:
- Application lifecycle management
- External integration configuration
- Security and access control
- Resource organization
- Usage monitoring

Applications are the foundational building blocks for deploying AI solutions.
They provide:
- Centralized configuration management
- Integration points with external systems
- Security boundary definitions
- Resource allocation and monitoring
- Usage analytics and reporting
"""

from typing import Any, Dict, Optional

from .base import BaseModel


class App(BaseModel[Dict[str, Any]]):
    """
    App class for managing AI-powered applications.

    This class represents an application in the Mosaia platform, serving as a
    container and orchestrator for AI solutions. Apps provide the structure and
    configuration for deploying and managing AI capabilities.

    Features:
    - Application lifecycle management
    - External integration configuration
    - Security and access control
    - Resource organization
    - Usage monitoring

    Examples:
        Basic app setup:
        >>> # Create a new application
        >>> support_portal = App({
        ...     'name': 'AI Support Portal',
        ...     'short_description': 'Intelligent customer support',
        ...     'long_description': 'AI-powered support system with multiple specialized agents',
        ...     'external_app_url': 'https://support.example.com'
        ... })
        >>>
        >>> # Save the application
        >>> await support_portal.save()

        External integration:
        >>> # Configure external system integration
        >>> app = App({
        ...     'name': 'Integration App',
        ...     'external_app_url': 'https://api.external-system.com',
        ...     'external_api_key': 'your-api-key',
        ...     'external_headers': {
        ...         'X-Custom-Header': 'value',
        ...         'Authorization': 'Bearer your-token'
        ...     }
        ... })
        >>>
        >>> # Test the connection
        >>> if app.is_active():
        ...     print('Integration configured successfully')
    """

    def __init__(self, data: Dict[str, Any], uri: Optional[str] = None):
        """
        Create a new App instance.

        Initializes an application with the provided configuration data and optional
        URI. The application serves as a container for organizing and managing
        AI-powered solutions.

        Args:
            data: Application configuration data including:
                  - name: Application name
                  - short_description: Brief description
                  - long_description: Detailed description
                  - external_app_url: External system URL
                  - external_api_key: API key for external system
                  - external_headers: Custom headers for external requests
            uri: Optional URI path for the application endpoint. Defaults to '/app'

        Examples:
            Basic configuration:
            >>> app = App({
            ...     'name': 'Customer Portal',
            ...     'short_description': 'AI customer service portal',
            ...     'external_app_url': 'https://portal.example.com'
            ... })

            Full configuration:
            >>> app = App({
            ...     'name': 'Enterprise Solution',
            ...     'short_description': 'AI-powered enterprise tools',
            ...     'long_description': 'Comprehensive suite of AI tools for enterprise use',
            ...     'external_app_url': 'https://enterprise.example.com',
            ...     'external_api_key': 'your-api-key',
            ...     'external_headers': {
            ...         'X-Enterprise-ID': 'ent-123',
            ...         'Authorization': 'Bearer token'
            ...     }
            ... }, '/enterprise/app')
        """
        super().__init__(data, uri or "/app")
