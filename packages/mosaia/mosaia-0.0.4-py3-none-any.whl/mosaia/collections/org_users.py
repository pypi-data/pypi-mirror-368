"""
Organization Users API client for the Mosaia SDK.

Provides CRUD operations for managing org-user relationships in the Mosaia platform.
OrgUsers handle the relationships between users and organizations, including
permissions and access control.
"""

from typing import Any, Dict, Optional

from ..models.org_user import OrgUser
from .base_collection import BaseCollection


class OrgUsers(BaseCollection[Dict[str, Any], OrgUser, Any, Any]):
    """
    Organization Users API client for the Mosaia SDK.

    Provides CRUD operations for managing org-user relationships in the Mosaia platform.
    OrgUsers handle the relationships between users and organizations, including
    permissions and access control.

    Examples:
        >>> from mosaia import Mosaia
        >>>
        >>> mosaia = Mosaia(api_key='your-api-key')
        >>> org_users = mosaia.org_users
        >>>
        # Get all org users
        >>> all_org_users = await org_users.get()
        >>>
        # Get a specific org user
        >>> org_user = await org_users.get({}, 'org-user-id')
        >>>
        # Create a new org user
        >>> new_org_user = await org_users.create({
        ...     'org': 'org-id',
        ...     'user': 'user-id',
        ...     'permission': 'admin'
        ... })
    """

    def __init__(self, uri: str = "", endpoint: str = "/user"):
        """
        Creates a new OrgUsers API client instance.

        Args:
            uri: Optional base URI path. If provided, the endpoint will be `${uri}/user`.
                  If not provided, defaults to `/user`.
        """
        super().__init__(f"{uri}{endpoint}", OrgUser)

    # Use default model creation from BaseCollection
