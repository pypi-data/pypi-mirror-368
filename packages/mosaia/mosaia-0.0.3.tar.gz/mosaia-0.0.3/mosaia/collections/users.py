"""
Users API client for the Mosaia SDK.

Provides CRUD operations for managing user accounts in the Mosaia platform.
Users represent individual accounts that can access the platform, manage
resources, and interact with AI agents and applications.
"""

from typing import Any, Dict, Optional

from ..models.user import User
from .base_collection import BaseCollection


class Users(BaseCollection[Dict[str, Any], User, Any, Any]):
    """
    Users API client for the Mosaia SDK.

    Provides CRUD operations for managing user accounts in the Mosaia platform.
    Users represent individual accounts that can access the platform, manage
    resources, and interact with AI agents and applications.

    This class inherits from BaseCollection and provides the following functionality:
    - Retrieve users with filtering and pagination
    - Create new user accounts
    - Update existing user profiles and settings
    - Delete user accounts
    - Manage user metadata and preferences
    - Handle user-specific configurations and permissions

    Examples:
        >>> from mosaia import Mosaia
        >>>
        >>> mosaia = Mosaia(api_key='your-api-key')
        >>> users = mosaia.users
        >>>
        # Get all users
        >>> all_users = await users.get()
        >>>
        # Get a specific user
        >>> user = await users.get({}, 'user-id')
        >>>
        # Create a new user
        >>> new_user = await users.create({
        ...     'username': 'john_doe',
        ...     'name': 'John Doe',
        ...     'email': 'john@example.com',
        ...     'description': 'Software developer'
        ... })
    """

    def __init__(self, uri: str = ""):
        """
        Creates a new Users API client instance.

        Initializes the users client with the appropriate endpoint URI
        and model class for handling user operations.

        The constructor sets up the API endpoint to `/user` (or `${uri}/user` if a base URI is provided),
        which corresponds to the Mosaia API's users endpoint.

        Args:
            uri: Optional base URI path. If provided, the endpoint will be `${uri}/user`.
                  If not provided, defaults to `/user`.

        Examples:
            # Create with default endpoint (/user)
            >>> users = Users()
            >>>
            # Create with custom base URI
            >>> users = Users('/api/v1')
            >>> # This will use endpoint: /api/v1/user
        """
        super().__init__(f"{uri}/user", User)
