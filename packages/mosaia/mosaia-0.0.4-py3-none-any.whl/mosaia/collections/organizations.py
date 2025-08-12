"""
Organizations API client for the Mosaia SDK.

Provides CRUD operations for managing organizations in the Mosaia platform.
Organizations are containers for grouping users, applications, and resources
to enable team collaboration.
"""

from typing import Any, Dict, Optional

from ..models.organization import Organization
from .base_collection import BaseCollection


class Organizations(BaseCollection[Dict[str, Any], Organization, Any, Any]):
    """
    Organizations API client for the Mosaia SDK.

    Provides CRUD operations for managing organizations in the Mosaia platform.
    Organizations are containers for grouping users, applications, and resources
    to enable team collaboration.

    Examples:
        >>> from mosaia import Mosaia
        >>>
        >>> mosaia = Mosaia(api_key='your-api-key')
        >>> organizations = mosaia.organizations
        >>>
        # Get all organizations
        >>> all_orgs = await organizations.get()
        >>>
        # Get a specific organization
        >>> org = await organizations.get({}, 'org-id')
        >>>
        # Create a new organization
        >>> new_org = await organizations.create({
        ...     'name': 'Acme Corp',
        ...     'short_description': 'Technology company'
        ... })
    """

    def __init__(self, uri: str = ""):
        """
        Creates a new Organizations API client instance.

        Args:
            uri: Optional base URI path. If provided, the endpoint will be `${uri}/org`.
                  If not provided, defaults to `/org`.
        """
        super().__init__(f"{uri}/org", Organization)
