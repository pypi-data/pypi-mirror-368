"""
Session class for managing authenticated contexts.

This class represents an authenticated session in the Mosaia platform.
It manages the current context including user identity, organization
membership, client information, and permissions.

Features:
- Identity management
- Context switching
- Permission tracking
- Relationship access
- Client authentication

Sessions provide access to:
- Current user profile
- Active organization
- Organization membership
- OAuth client context
- Permission scopes

The session maintains the active context for:
- API requests
- Resource access
- Permission checks
- Identity verification
"""

from typing import Any, Dict, Optional

from .base import BaseModel
from .client import Client
from .org_user import OrgUser
from .organization import Organization
from .user import User


class Session(BaseModel[Dict[str, Any]]):
    """
    Session class for managing authenticated contexts.

    This class represents an authenticated session in the Mosaia platform.
    It manages the current context including user identity, organization
    membership, client information, and permissions.

    Features:
    - Identity management
    - Context switching
    - Permission tracking
    - Relationship access
    - Client authentication

    Sessions provide access to:
    - Current user profile
    - Active organization
    - Organization membership
    - OAuth client context
    - Permission scopes

    The session maintains the active context for:
    - API requests
    - Resource access
    - Permission checks
    - Identity verification

    Examples:
        Basic session usage:
        >>> # Create authenticated session
        >>> session = Session({
        ...     'user': {
        ...         'id': 'user-123',
        ...         'name': 'John Developer',
        ...         'email': 'john@example.com'
        ...     },
        ...     'org': {
        ...         'id': 'org-456',
        ...         'name': 'Tech Corp'
        ...     }
        ... })
        >>>
        >>> # Access session context
        >>> user = session.user
        >>> org = session.org
        >>> print(f"{user.name} @ {org.name}")

        Permission checking:
        >>> # Check access and permissions
        >>> perms = session.permissions
        >>> if perms and perms.get('can_manage_users'):
        ...     # Add team member
        ...     org_user = session.org_user
        ...     await org_user.orgs.create({
        ...         'user': 'new-user',
        ...         'permission': 'member'
        ...     })
        >>>
        >>> # Switch organization context
        >>> session.org = new_org
        >>> session.org_user = new_org_user
        >>>
        >>> # Verify client
        >>> client = session.client
        >>> if client and client.is_active():
        ...     print('Client authenticated')
        ...     print(f'Scopes: {client.scopes}')
    """

    def __init__(self, data: Dict[str, Any], uri: Optional[str] = None):
        """
        Create a new authenticated session.

        Initializes a session with the provided authentication context. The
        session manages the current user's identity, organization membership,
        and access permissions.

        Args:
            data: Session data including:
                  - user: Current user details
                  - org: Active organization
                  - org_user: Organization membership
                  - client: OAuth client context
                  - permissions: Access permissions
            uri: Optional URI path for the session endpoint. Defaults to '/session'

        Examples:
            Basic user session:
            >>> session = Session({
            ...     'user': {
            ...         'id': 'user-123',
            ...         'name': 'Jane Developer',
            ...         'email': 'jane@example.com'
            ...     }
            ... })

            Full organization context:
            >>> session = Session({
            ...     'user': {
            ...         'id': 'user-123',
            ...         'name': 'Jane Developer'
            ...     },
            ...     'org': {
            ...         'id': 'org-456',
            ...         'name': 'Tech Corp'
            ...     },
            ...     'org_user': {
            ...         'permission': 'admin'
            ...     },
            ...     'client': {
            ...         'id': 'client-789',
            ...         'name': 'Web Dashboard'
            ...     },
            ...     'permissions': {
            ...         'can_manage_users': True,
            ...         'can_manage_apps': True
            ...     }
            ... })
        """
        super().__init__(data, uri or "/session")

    @property
    def user(self) -> Optional[User]:
        """
        Get the current authenticated user.

        This property provides access to the current user's profile and identity
        information. It returns a User instance that can be used to access
        and manage user-specific data.

        Returns:
            User instance for the authenticated user, or None if not available

        Examples:
            Basic user access:
            >>> user = session.user
            >>> if user:
            ...     print(f"Authenticated as: {user.name}")
            ...     print(f"Email: {user.email}")
            ...     print(f"Status: {'Active' if user.is_active() else 'Inactive'}")
            >>> else:
            ...     print('Not authenticated')

            Profile management:
            >>> async def update_user_profile(session):
            ...     user = session.user
            ...     if not user:
            ...         raise ValueError('Not authenticated')
            ...
            ...     # Update profile
            ...     user.update({
            ...         'name': 'Updated Name',
            ...         'metadata': {
            ...             'title': 'Senior Developer',
            ...             'department': 'Engineering'
            ...         }
            ...     })
            ...
            ...     await user.save()
            ...     print('Profile updated successfully')
        """
        if self.data.get("user"):
            return User(self.data["user"])
        return None

    @user.setter
    def user(self, user_data: Dict[str, Any]):
        """
        Set the current authenticated user.

        This setter updates the current user context in the session. It's
        typically used when switching users or updating user information
        after authentication changes.

        Args:
            user_data: Complete user data including:
                      - id: User's unique identifier
                      - name: User's full name
                      - email: User's email address
                      - metadata: Additional user data

        Examples:
            Basic user switch:
            >>> session.user = {
            ...     'id': 'user-123',
            ...     'name': 'New User',
            ...     'email': 'new@example.com'
            ... }

            Detailed user context:
            >>> session.user = {
            ...     'id': 'user-456',
            ...     'name': 'Jane Smith',
            ...     'email': 'jane@example.com',
            ...     'metadata': {
            ...         'title': 'Engineering Manager',
            ...         'department': 'R&D',
            ...         'location': 'San Francisco',
            ...         'timezone': 'America/Los_Angeles'
            ...     }
            ... }
        """
        self.data["user"] = user_data

    @property
    def org(self) -> Optional[Organization]:
        """
        Get the current active organization.

        This property provides access to the current organization context in
        the session. It returns an Organization instance that can be used
        to access and manage organization-specific resources.

        Returns:
            Organization instance for active organization, or None if not available

        Examples:
            Basic organization access:
            >>> org = session.org
            >>> if org:
            ...     print(f"Organization: {org.name}")
            ...     print(f"Description: {org.short_description}")
            ...     print(f"Status: {'Active' if org.is_active() else 'Inactive'}")
            >>> else:
            ...     print('No organization context')

            Resource management:
            >>> async def manage_org_resources(session):
            ...     org = session.org
            ...     if not org:
            ...         raise ValueError('No organization context')
            ...
            ...     # Access organization resources
            ...     agents, apps, models = await asyncio.gather(
            ...         org.agents.get(),
            ...         org.apps.get(),
            ...         org.models.get()
            ...     )
            ...
            ...     print('Organization Resources:')
            ...     print(f'- {len(agents)} AI agents')
            ...     print(f'- {len(apps)} applications')
            ...     print(f'- {len(models)} models')
        """
        if self.data.get("org"):
            return Organization(self.data["org"])
        return None

    @org.setter
    def org(self, org_data: Dict[str, Any]):
        """
        Set the current active organization.

        This setter updates the current organization context in the session.
        It's typically used when switching between organizations or updating
        organization information.

        Args:
            org_data: Complete organization data including:
                     - id: Organization's unique identifier
                     - name: Organization name
                     - short_description: Brief description
                     - metadata: Additional organization data

        Examples:
            Basic organization switch:
            >>> session.org = {
            ...     'id': 'org-123',
            ...     'name': 'New Organization',
            ...     'short_description': 'Updated context'
            ... }

            Detailed organization context:
            >>> session.org = {
            ...     'id': 'org-456',
            ...     'name': 'Enterprise Corp',
            ...     'short_description': 'Global enterprise solutions',
            ...     'long_description': 'Leading provider of enterprise AI solutions',
            ...     'metadata': {
            ...         'industry': 'technology',
            ...         'size': 'enterprise',
            ...         'region': 'global',
            ...         'features': ['agents', 'apps', 'models']
            ...     }
            ... }
        """
        self.data["org"] = org_data

    @property
    def org_user(self) -> Optional[OrgUser]:
        """
        Get the current organization membership.

        This property provides access to the current user's membership and role
        within the active organization. It returns an OrgUser instance that
        manages the relationship between user and organization.

        Returns:
            OrgUser instance for current membership, or None if not available

        Examples:
            Basic membership check:
            >>> membership = session.org_user
            >>> if membership:
            ...     print(f"Role: {membership.permission}")
            ...     print(f"Active: {membership.is_active()}")
            >>> else:
            ...     print('No organization membership')

            Permission management:
            >>> async def check_access(session):
            ...     membership = session.org_user
            ...     if not membership:
            ...         raise ValueError('No organization access')
            ...
            ...     # Check permissions
            ...     perms = session.permissions
            ...     if perms and perms.get('can_manage_users'):
            ...         # Manage team
            ...         team = await membership.orgs.get()
            ...         print('Team Members:')
            ...         for member in team:
            ...             print(f"- {member['user']['name']} ({member['permission']})")
            ...     else:
            ...         print('Insufficient permissions')
        """
        if self.data.get("org_user"):
            return OrgUser(self.data["org_user"])
        return None

    @org_user.setter
    def org_user(self, org_user_data: Dict[str, Any]):
        """
        Set the current organization membership.

        This setter updates the current user's membership and role within
        the active organization. It's typically used when switching roles
        or updating membership details.

        Args:
            org_user_data: Complete membership data including:
                          - org: Organization reference
                          - user: User reference
                          - permission: Access level
                          - metadata: Additional membership data

        Examples:
            Basic role update:
            >>> session.org_user = {
            ...     'org': 'org-123',
            ...     'user': 'user-456',
            ...     'permission': 'admin'
            ... }

            Detailed membership update:
            >>> session.org_user = {
            ...     'org': 'org-123',
            ...     'user': 'user-456',
            ...     'permission': 'member',
            ...     'metadata': {
            ...         'department': 'engineering',
            ...         'title': 'Senior Developer',
            ...         'start_date': '2024-01-01T00:00:00Z',
            ...         'access_level': 'full',
            ...         'teams': ['frontend', 'platform']
            ...     }
            ... }
        """
        self.data["org_user"] = org_user_data

    @property
    def client(self) -> Optional[Client]:
        """
        Get the current OAuth client.

        This property provides access to the current OAuth client context in
        the session. It returns a Client instance that manages authentication
        and authorization for external applications.

        Returns:
            Client instance for current OAuth client, or None if not available

        Examples:
            Basic client access:
            >>> client = session.client
            >>> if client:
            ...     print(f"Client: {client.name}")
            ...     print(f"ID: {client.client_id}")
            ...     print(f"Status: {'Active' if client.is_active() else 'Inactive'}")
            >>> else:
            ...     print('No client context')

            Client verification:
            >>> async def verify_client(session):
            ...     client = session.client
            ...     if not client:
            ...         raise ValueError('No client context')
            ...
            ...     # Check client configuration
            ...     print('Client Configuration:')
            ...     print(f"Name: {client.name}")
            ...     print(f"ID: {client.client_id}")
            ...     print(f"Redirect URIs: {', '.join(client.redirect_uris)}")
            ...     print(f"Scopes: {', '.join(client.scopes)}")
            ...
            ...     if client.metadata and client.metadata.get('type') == 'service-account':
            ...         print('Service Account Details:')
            ...         print(f"Service: {client.metadata['service']}")
            ...         print(f"Environment: {client.metadata['environment']}")
        """
        if self.data.get("client"):
            return Client(self.data["client"])
        return None

    @client.setter
    def client(self, client_data: Dict[str, Any]):
        """
        Set the current OAuth client.

        This setter updates the current OAuth client context in the session.
        It's typically used when switching clients or updating client
        configuration for authentication.

        Args:
            client_data: Complete client data including:
                        - id: Client's unique identifier
                        - name: Client application name
                        - client_id: OAuth client ID
                        - client_secret: OAuth client secret
                        - redirect_uris: Authorized redirect URIs
                        - scopes: Authorized scopes
                        - metadata: Additional client data

        Examples:
            Basic client update:
            >>> session.client = {
            ...     'id': 'client-123',
            ...     'name': 'Web Dashboard',
            ...     'client_id': 'client-id',
            ...     'redirect_uris': ['https://app.example.com/callback']
            ... }

            Service account setup:
            >>> session.client = {
            ...     'id': 'client-456',
            ...     'name': 'Background Service',
            ...     'client_id': 'service-client-id',
            ...     'client_secret': 'service-client-secret',
            ...     'grant_types': ['client_credentials'],
            ...     'scopes': ['service:full'],
            ...     'metadata': {
            ...         'type': 'service-account',
            ...         'service': 'data-processor',
            ...         'environment': 'production',
            ...         'rate_limit': 1000
            ...     }
            ... }
        """
        self.data["client"] = client_data

    @property
    def permissions(self) -> Optional[Dict[str, Any]]:
        """
        Get the current session permissions.

        This property provides access to the current session's permission set.
        It returns a permissions object that defines what actions the current
        user can perform within the active organization context.

        Returns:
            Permission object defining allowed actions, or None if not available

        Examples:
            Basic permission check:
            >>> perms = session.permissions
            >>> if perms:
            ...     print('User Permissions:')
            ...     print(f"- Manage Users: {perms.get('can_manage_users', False)}")
            ...     print(f"- Manage Apps: {perms.get('can_manage_apps', False)}")
            ...     print(f"- Manage Models: {perms.get('can_manage_models', False)}")
            >>> else:
            ...     print('No permission data available')

            Permission-based operations:
            >>> async def perform_admin_task(session):
            ...     perms = session.permissions
            ...     if not perms:
            ...         raise ValueError('No permission data')
            ...
            ...     # Check admin capabilities
            ...     can_manage_team = perms.get('can_manage_users', False)
            ...     can_configure_apps = perms.get('can_manage_apps', False)
            ...     can_deploy_models = perms.get('can_manage_models', False)
            ...
            ...     if can_manage_team and can_configure_apps and can_deploy_models:
            ...         print('Full administrative access')
            ...
            ...         # Perform admin tasks
            ...         org = session.org
            ...         if org:
            ...             users, apps, models = await asyncio.gather(
            ...                 org.orgs.get(),
            ...                 org.apps.get(),
            ...                 org.models.get()
            ...             )
            ...
            ...             print('Resource Summary:')
            ...             print(f'- {len(users)} team members')
            ...             print(f'- {len(apps)} applications')
            ...             print(f'- {len(models)} AI models')
            ...     else:
            ...         print('Limited permissions:')
            ...         print(f'- Team management: {can_manage_team}')
            ...         print(f'- App configuration: {can_configure_apps}')
            ...         print(f'- Model deployment: {can_deploy_models}')
        """
        return self.data.get("permissions")
