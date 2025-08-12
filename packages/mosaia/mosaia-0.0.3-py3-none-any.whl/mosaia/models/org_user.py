"""
OrgUser class for managing organization-user relationships.

This class represents the relationship between a user and an organization
in the Mosaia platform. It manages permissions, roles, and access control
within organizational contexts, enabling fine-grained control over user
access to organizational resources.

Features:
- Permission management
- Role-based access control
- Session handling
- User-org relationship lifecycle
- Access control enforcement

Organization-user relationships are crucial for:
- Multi-tenant access control
- Team member management
- Resource sharing
- Activity tracking
- Compliance and auditing

The class supports various permission levels:
- Owner: Full control over organization
- Admin: Administrative access
- Member: Standard access
- Guest: Limited access
"""

from typing import TYPE_CHECKING, Any, Dict, Optional

from mosaia.utils.api_client import MosaiaConfig

from .base import BaseModel

if TYPE_CHECKING:
    # These imports are only for type checkers and won't run at runtime,
    # preventing circular import issues
    from .organization import Organization
    from .user import User


class OrgUser(BaseModel[Dict[str, Any]]):
    """
    OrgUser class for managing organization-user relationships.

    This class represents the relationship between a user and an organization
    in the Mosaia platform. It manages permissions, roles, and access control
    within organizational contexts, enabling fine-grained control over user
    access to organizational resources.

    Features:
    - Permission management
    - Role-based access control
    - Session handling
    - User-org relationship lifecycle
    - Access control enforcement

    Examples:
        Basic relationship setup:
        >>> # Create a new team member relationship
        >>> team_member = OrgUser({
        ...     'org': 'acme-org',
        ...     'user': 'john-doe',
        ...     'permission': 'member',
        ...     'metadata': {
        ...         'department': 'engineering',
        ...         'role': 'developer'
        ...     }
        ... })
        >>>
        >>> await team_member.save()

        Managing access and sessions:
        >>> # Get user and organization details
        >>> user = team_member.user
        >>> org = team_member.org
        >>>
        >>> # Create an authenticated session
        >>> config = await team_member.session()
        >>>
        >>> # Check access and permissions
        >>> if team_member.is_active():
        ...     print(f'{user.name} is active in {org.name}')
        ...     print(f'Permission level: {team_member.permission}')
        ... else:
        ...     # Remove access if needed
        ...     await team_member.disable()
        ...     print('Access removed')
    """

    def __init__(self, data: Dict[str, Any], uri: Optional[str] = None):
        """
        Create a new organization-user relationship.

        Initializes a relationship between a user and an organization with
        specified permissions and metadata. This relationship controls the
        user's access and capabilities within the organization.

        Args:
            data: Configuration data including:
                  - org: Organization ID or data
                  - user: User ID or data
                  - permission: Access level ('owner', 'admin', 'member', 'guest')
                  - metadata: Custom metadata object
            uri: Optional custom URI path for the relationship endpoint. Defaults to '/org'

        Examples:
            Basic member setup:
            >>> member = OrgUser({
            ...     'org': 'acme-org',
            ...     'user': 'jane-doe',
            ...     'permission': 'member'
            ... })

            Admin with metadata:
            >>> admin = OrgUser({
            ...     'org': 'tech-corp',
            ...     'user': 'admin-user',
            ...     'permission': 'admin',
            ...     'metadata': {
            ...         'department': 'IT',
            ...         'role': 'system-admin',
            ...         'access_level': 'full',
            ...         'joined_date': '2024-01-01T00:00:00Z'
            ...     }
            ... }, '/enterprise/org-user')
        """
        super().__init__(data, uri or "/org")

    @property
    def user(self):
        """
        Get the associated user details.

        This property provides access to the user's details within the context
        of the organization relationship. When _shallow=True, returns basic user
        data without creating a full User instance to prevent recursion.

        Returns:
            User instance or dict with basic user data when _shallow=True

        Raises:
            Error: When user data is not available in the relationship

        Examples:
            Basic user access:
            >>> user = org_user.user
            >>> print(f'Member: {user.name} ({user.email})')

            Detailed user information:
            >>> try:
            ...     user = org_user.user
            ...     print('User Details:')
            ...     print(f'Name: {user.name}')
            ...     print(f'Email: {user.email}')
            ...     print(f'Status: {"Active" if user.is_active() else "Inactive"}')
            ...     print(f'Last Login: {user.last_login_at}')
            ... except Exception as error:
            ...     print(f'User data not available: {error}')
        """
        if not self.data.get("user"):
            return None

        # Lazy import to avoid circular import at runtime
        from .user import User

        return User(self.data["user"])

    @user.setter
    def user(self, data: Dict[str, Any]) -> None:
        """
        Set the associated user details.

        This setter updates the user details within the organization relationship.
        It's typically used when reassigning the relationship to a different user
        or updating user details in bulk.

        Args:
            data: Complete user data including:
                  - id: User's unique identifier
                  - name: User's full name
                  - email: User's email address
                  - metadata: Additional user data

        Examples:
            Basic user update:
            >>> org_user.user = {
            ...     'id': 'user-123',
            ...     'name': 'Jane Smith',
            ...     'email': 'jane.smith@example.com'
            ... }

            Detailed user update:
            >>> org_user.user = {
            ...     'id': 'user-456',
            ...     'name': 'John Developer',
            ...     'email': 'john@example.com',
            ...     'metadata': {
            ...         'title': 'Senior Developer',
            ...         'skills': ['python', 'django'],
            ...         'start_date': '2024-01-01'
            ...     }
            ... }
            >>>
            >>> # Save changes
            >>> await org_user.save()
        """
        self.update({"user": data})

    @property
    def org(self):
        """
        Get the associated organization details.

        This property provides access to the organization's details within the
        context of the user relationship. It returns an Organization instance
        that can be used to access and manage organization-specific data.

        Returns:
            Organization instance with full organization details

        Raises:
            Error: When organization data is not available in the relationship

        Examples:
            Basic organization access:
            >>> org = org_user.org
            >>> print(f'Organization: {org.name}')
            >>> print(f'Description: {org.short_description}')

            Detailed organization information:
            >>> try:
            ...     org = org_user.org
            ...     print('Organization Details:')
            ...     print(f'Name: {org.name}')
            ...     print(f'Description: {org.short_description}')
            ...     print(f'Status: {"Active" if org.is_active() else "Inactive"}')
            ...     print(f'Members: {org.member_count}')
            ...
            ...     if org.metadata and 'industry' in org.metadata:
            ...         print(f'Industry: {org.metadata["industry"]}')
            ... except Exception as error:
            ...     print(f'Organization data not available: {error}')
        """
        if not self.data.get("org"):
            return None

        # Lazy import to avoid circular import at runtime
        from .organization import Organization

        return Organization(self.data["org"])

    @org.setter
    def org(self, data: Dict[str, Any]) -> None:
        """
        Set the associated organization details.

        This setter updates the organization details within the user relationship.
        It's typically used when reassigning the relationship to a different
        organization or updating organization details in bulk.

        Args:
            data: Complete organization data including:
                  - id: Organization's unique identifier
                  - name: Organization name
                  - short_description: Brief description
                  - metadata: Additional organization data

        Examples:
            Basic organization update:
            >>> org_user.org = {
            ...     'id': 'org-123',
            ...     'name': 'Acme Corporation',
            ...     'short_description': 'Leading tech company'
            ... }

            Detailed organization update:
            >>> org_user.org = {
            ...     'id': 'org-456',
            ...     'name': 'Tech Innovators',
            ...     'short_description': 'AI and ML solutions',
            ...     'long_description': 'Cutting-edge AI/ML solutions for enterprises',
            ...     'metadata': {
            ...         'industry': 'technology',
            ...         'size': 'enterprise',
            ...         'founded': '2020',
            ...         'locations': ['San Francisco', 'London']
            ...     }
            ... }
            >>>
            >>> # Save changes
            >>> await org_user.save()
        """
        self.update({"org": data})

    async def session(self) -> MosaiaConfig:
        """
        Create an authenticated session for the organization user.

        This method creates a new authenticated session for the user within
        the organization context. The session includes access tokens and
        configuration needed to interact with organization resources.

        The method:
        1. Validates the relationship is active
        2. Requests new access tokens
        3. Creates a configured session

        Returns:
            MosaiaConfig with session details

        Raises:
            Error: When session creation fails
            Error: When relationship is inactive
            Error: When network errors occur

        Examples:
            Basic session creation:
            >>> try:
            ...     config = await org_user.session()
            ...     # Use the authenticated session
            ...     print(f'Session created successfully')
            ... except Exception as error:
            ...     print(f'Session failed: {error}')

            Advanced session usage:
            >>> try:
            ...     # Create authenticated session
            ...     config = await org_user.session()
            ...
            ...     # Access organization resources
            ...     print('Session created successfully')
            ...     print(f'Access token: {config.get("apiKey", "N/A")}')
            ... except Exception as error:
            ...     if 'inactive' in str(error):
            ...         print('User access is inactive')
            ...     elif 'unauthorized' in str(error):
            ...         print('Invalid permissions')
            ...     else:
            ...         print(f'Session error: {error}')
        """
        try:
            response = await self.api_client.get(f"{self.get_uri()}/session")

            if isinstance(response, dict) and "error" in response:
                raise Exception(
                    response["error"].get("message", "Session creation failed")
                )

            # Return the session configuration
            session_data = (
                response.get("data", response)
                if isinstance(response, dict)
                else response
            )
            new_session_config = MosaiaConfig(**self.config.__dict__)
            new_session_config.api_key = session_data.get("access_token")
            new_session_config.session = session_data

            return new_session_config

        except Exception as error:
            if hasattr(error, "message"):
                raise self._handle_error(error)
            else:
                raise self._handle_error(error)

    async def disable(self) -> None:
        """
        Disable the organization-user relationship.

        This method deactivates the relationship between the user and organization,
        effectively revoking the user's access to organization resources. This is
        useful for:
        - Removing team members
        - Revoking access temporarily
        - Managing user offboarding

        The method:
        1. Validates the relationship exists
        2. Sends deactivation request
        3. Clears local session data

        Raises:
            Error: When disable operation fails
            Error: When relationship doesn't exist
            Error: When network errors occur

        Examples:
            Basic deactivation:
            >>> try:
            ...     await org_user.disable()
            ...     print('User access revoked successfully')
            ... except Exception as error:
            ...     print(f'Failed to revoke access: {error}')

            Managed offboarding:
            >>> async def offboard_user(org_user):
            ...     try:
            ...         # Get user details for logging
            ...         user = org_user.user
            ...         org = org_user.org
            ...
            ...         # Revoke access
            ...         await org_user.disable()
            ...
            ...         print('User offboarded successfully:')
            ...         print(f'- User: {user.name} ({user.email})')
            ...         print(f'- From: {org.name}')
            ...         print(f'- Time: {datetime.now().isoformat()}')
            ...     except Exception as error:
            ...         print(f'Offboarding failed: {error}')
            ...         raise error  # Re-throw for handling by caller
        """
        try:
            await self.api_client.delete(f"{self.get_uri()}")
        except Exception as error:
            if hasattr(error, "message"):
                raise self._handle_error(error)
            else:
                raise self._handle_error(Exception("Unknown error occurred"))
