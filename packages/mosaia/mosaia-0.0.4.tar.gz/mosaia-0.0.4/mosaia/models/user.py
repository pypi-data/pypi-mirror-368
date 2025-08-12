"""
User class for managing platform users.

This class represents a user account in the Mosaia platform. Users are
the primary actors who can create and manage AI resources, interact with
agents, and collaborate within organizations.

Features:
- Profile management
- Resource ownership
- Organization membership
- Access control
- Resource management

Users can manage:
- AI agents and groups
- Applications
- Models and tools
- Organization memberships
- OAuth clients

Available resources:
- Personal agents
- Custom applications
- Model configurations
- Integration tools
- Organization access
"""

from typing import Any, Dict, List, Optional

from .base import BaseModel


class User(BaseModel[Dict[str, Any]]):
    """
    User class for managing platform users.

    This class represents a user account in the Mosaia platform. Users are
    the primary actors who can create and manage AI resources, interact with
    agents, and collaborate within organizations.

    Features:
    - Profile management
    - Resource ownership
    - Organization membership
    - Access control
    - Resource management

    Users can manage:
    - AI agents and groups
    - Applications
    - Models and tools
    - Organization memberships
    - OAuth clients

    Available resources:
    - Personal agents
    - Custom applications
    - Model configurations
    - Integration tools
    - Organization access

    Examples:
        Basic user setup:
        >>> # Create user profile
        >>> user = User({
        ...     'username': 'jsmith',
        ...     'name': 'John Smith',
        ...     'email': 'john@example.com',
        ...     'metadata': {
        ...         'title': 'Senior Developer',
        ...         'department': 'Engineering',
        ...         'location': 'San Francisco'
        ...     }
        ... })
        >>>
        >>> await user.save()
        >>>
        >>> # Add profile image
        >>> with open('avatar.jpg', 'rb') as f:
        ...     await user.upload_profile_image(f)

        Resource management:
        >>> # Access user's resources
        >>> agents, apps, models = await asyncio.gather(
        ...     user.agents.get(),
        ...     user.apps.get(),
        ...     user.models.get()
        ... )
        >>>
        >>> print('User Resources:')
        >>> print(f'- {len(agents)} AI agents')
        >>> print(f'- {len(apps)} applications')
        >>> print(f'- {len(models)} models')
        >>>
        >>> # Create new agent
        >>> agent = await user.agents.create({
        ...     'name': 'Personal Assistant',
        ...     'model': 'gpt-4',
        ...     'temperature': 0.7,
        ...     'system_prompt': 'You are a helpful assistant.'
        ... })
        >>>
        >>> # Create application
        >>> app = await user.apps.create({
        ...     'name': 'Task Manager',
        ...     'short_description': 'AI-powered task management'
        ... })
        >>>
        >>> # Check organization memberships
        >>> orgs = await user.orgs.get()
        >>> for org in orgs:
        ...     print(f"{org['org']['name']}: {org['permission']}")
    """

    def __init__(self, data: Dict[str, Any], uri: Optional[str] = None):
        """
        Create a new user profile.

        Initializes a user account with the provided profile information.
        Users are the primary actors in the platform who can create and
        manage AI resources.

        Args:
            data: Profile data including:
                  - username: Unique identifier
                  - name: Display name
                  - email: Contact email
                  - description: Bio or description
                  - metadata: Additional profile data
            uri: Optional custom URI path for the user endpoint. Defaults to '/user'

        Examples:
            Basic profile:
            >>> user = User({
            ...     'username': 'jdoe',
            ...     'name': 'Jane Doe',
            ...     'email': 'jane@example.com',
            ...     'description': 'AI Developer'
            ... })

            Detailed profile:
            >>> user = User({
            ...     'username': 'jsmith',
            ...     'name': 'John Smith',
            ...     'email': 'john@example.com',
            ...     'description': 'Senior AI Engineer',
            ...     'metadata': {
            ...         'title': 'Engineering Lead',
            ...         'department': 'AI Research',
            ...         'location': 'New York',
            ...         'skills': ['machine-learning', 'nlp', 'python'],
            ...         'joined_date': '2024-01-01T00:00:00Z',
            ...         'preferences': {
            ...             'theme': 'dark',
            ...             'notifications': True,
            ...             'language': 'en-US'
            ...         }
            ...     }
            ... }, '/enterprise/user')
        """
        super().__init__(data, uri or "/user")

    @property
    def agents(self):
        """
        Get the user's AI agents.

        This property provides access to the user's AI agents through the
        Agents collection. It enables management of personal agents and
        their configurations.

        Returns:
            Agents collection for managing AI agents

        Examples:
            List agents:
            >>> agents = await user.agents.get()
            >>> for agent in agents:
            ...     print(f"Agent: {agent.name}")
            ...     print(f"Model: {agent.model}")

            Create agent:
            >>> agent = await user.agents.create({
            ...     'name': 'Code Assistant',
            ...     'model': 'gpt-4',
            ...     'temperature': 0.7,
            ...     'system_prompt': 'You are an expert programmer.',
            ...     'metadata': {
            ...         'purpose': 'code-review',
            ...         'languages': ['typescript', 'python', 'go']
            ...     }
            ... })
        """
        # Lazy import to avoid circular dependencies at import time
        from mosaia.collections import Agents

        return Agents(self.get_uri())

    @property
    def apps(self):
        """
        Get the user's applications.

        This property provides access to the user's applications through the
        Apps collection. It enables management of personal applications and
        their configurations.

        Returns:
            Apps collection for managing applications

        Examples:
            List applications:
            >>> apps = await user.apps.get()
            >>> for app in apps:
            ...     print(f"App: {app.name}")
            ...     print(f"URL: {app.external_app_url}")

            Create application:
            >>> app = await user.apps.create({
            ...     'name': 'AI Dashboard',
            ...     'short_description': 'Personal AI management',
            ...     'external_app_url': 'https://dashboard.example.com',
            ...     'metadata': {
            ...         'type': 'web-application',
            ...         'features': ['agent-management', 'analytics'],
            ...         'version': '1.0'
            ...     }
            ... })
        """
        from mosaia.collections import Apps

        return Apps(self.get_uri())

    @property
    def clients(self):
        """
        Get the user's OAuth clients.

        This property provides access to the user's OAuth clients through the
        Clients collection. It enables management of authentication and
        authorization for external applications.

        Returns:
            Clients collection for managing OAuth clients

        Examples:
            List clients:
            >>> clients = await user.clients.get()
            >>> for client in clients:
            ...     print(f"Client: {client.name}")
            ...     print(f"ID: {client.client_id}")

            Create OAuth client:
            >>> client = await user.clients.create({
            ...     'name': 'Mobile App',
            ...     'redirect_uris': ['com.example.app://oauth/callback'],
            ...     'scopes': ['read:agents', 'write:apps'],
            ...     'metadata': {
            ...         'platform': 'ios',
            ...         'version': '2.0',
            ...         'environment': 'production'
            ...     }
            ... })
            >>>
            >>> print('Client credentials:')
            >>> print(f"ID: {client.client_id}")
            >>> print(f"Secret: {client.client_secret}")
        """
        from mosaia.collections import Clients

        return Clients(self.get_uri())

    @property
    def groups(self):
        """
        Get the user's agent groups.

        This property provides access to the user's agent groups through the
        AgentGroups collection. It enables management of collaborative
        agent teams and specialized configurations.

        Returns:
            AgentGroups collection for managing agent groups

        Examples:
            List groups:
            >>> groups = await user.groups.get()
            >>> for group in groups:
            ...     print(f"Group: {group.name}")
            ...     print(f"Agents: {len(group.agents)}")

            Create specialized team:
            >>> support_team = await user.groups.create({
            ...     'name': 'Support Team',
            ...     'short_description': 'Customer support specialists',
            ...     'agents': ['billing-expert', 'tech-support', 'general-help'],
            ...     'metadata': {
            ...         'type': 'customer-support',
            ...         'specialties': ['billing', 'technical', 'general'],
            ...         'availability': '24/7',
            ...         'routing': {
            ...             'strategy': 'round-robin',
            ...             'fallback': 'general-help'
            ...         }
            ...     }
            ... })
        """
        from mosaia.collections import AgentGroups

        return AgentGroups(self.get_uri())

    @property
    def models(self):
        """
        Get the user's AI models.

        This property provides access to the user's AI models through the
        Models collection. It enables management of model configurations
        and customizations.

        Returns:
            Models collection for managing AI models

        Examples:
            List models:
            >>> models = await user.models.get()
            >>> for model in models:
            ...     print(f"Model: {model.name}")
            ...     print(f"Provider: {model.provider}")
            ...     print(f"ID: {model.model_id}")

            Create custom model:
            >>> model = await user.models.create({
            ...     'name': 'Enhanced GPT-4',
            ...     'provider': 'openai',
            ...     'model_id': 'gpt-4',
            ...     'temperature': 0.7,
            ...     'max_tokens': 2000,
            ...     'metadata': {
            ...         'purpose': 'code-generation',
            ...         'training': 'fine-tuned',
            ...         'version': '1.0',
            ...         'specialties': ['typescript', 'python'],
            ...         'performance': {
            ...             'avg_latency': 500,
            ...             'max_concurrent': 10
            ...         }
            ...     }
            ... })
        """
        from mosaia.collections import Models

        return Models(self.get_uri())

    @property
    def orgs(self):
        """
        Get the user's organization memberships.

        This property provides access to the user's organization memberships
        through the OrgUsers collection. It enables management of team
        memberships and organization access.

        Returns:
            OrgUsers collection for managing organization memberships

        Examples:
            List memberships:
            >>> memberships = await user.orgs.get()
            >>> for membership in memberships:
            ...     print(f"Organization: {membership['org']['name']}")
            ...     print(f"Role: {membership['permission']}")
            ...     print(f"Active: {membership['is_active']}")

            Manage memberships:
            >>> # Join organization
            >>> membership = await user.orgs.create({
            ...     'org': 'org-123',
            ...     'permission': 'member',
            ...     'metadata': {
            ...         'department': 'engineering',
            ...         'title': 'Senior Developer',
            ...         'start_date': '2024-01-01T00:00:00Z'
            ...     }
            ... })
            >>>
            >>> # Get authenticated session
            >>> config = await membership.session()
            >>> mosaia = Mosaia(config)
            >>>
            >>> # Access organization resources
            >>> org_agents = await mosaia.agents.get()
            >>> print(f"Organization has {len(org_agents)} agents")
        """
        from mosaia.collections import OrgUsers

        return OrgUsers(uri=self.get_uri(), endpoint="/org")

    @property
    def tools(self):
        """
        Get the user's integration tools.

        This property provides access to the user's integration tools through
        the Tools collection. It enables management of external service
        integrations and custom tools.

        Returns:
            Tools collection for managing integrations

        Examples:
            List tools:
            >>> tools = await user.tools.get()
            >>> for tool in tools:
            ...     print(f"Tool: {tool.name}")
            ...     print(f"Type: {tool.type}")
            ...     print(f"Schema: {tool.tool_schema}")

            Create integration:
            >>> tool = await user.tools.create({
            ...     'name': 'jira-integration',
            ...     'friendly_name': 'Jira Service',
            ...     'short_description': 'Create and manage Jira issues',
            ...     'tool_schema': json.dumps({
            ...         'type': 'object',
            ...         'properties': {
            ...             'project': {
            ...                 'type': 'string',
            ...                 'description': 'Jira project key'
            ...             },
            ...             'type': {
            ...                 'type': 'string',
            ...                 'enum': ['bug', 'task', 'story'],
            ...                 'default': 'task'
            ...             },
            ...             'title': {
            ...                 'type': 'string',
            ...                 'minLength': 1
            ...             },
            ...             'description': {
            ...                 'type': 'string'
            ...             },
            ...             'priority': {
            ...                 'type': 'string',
            ...                 'enum': ['high', 'medium', 'low'],
            ...                 'default': 'medium'
            ...             }
            ...         },
            ...         'required': ['project', 'title']
            ...     }),
            ...     'required_environment_variables': [
            ...         'JIRA_HOST',
            ...         'JIRA_EMAIL',
            ...         'JIRA_API_TOKEN'
            ...     ],
            ...     'source_url': 'https://your-domain.atlassian.net',
            ...     'metadata': {
            ...         'type': 'issue-tracker',
            ...         'provider': 'atlassian',
            ...         'version': '1.0',
            ...         'capabilities': ['create', 'read', 'update']
            ...     }
            ... })
        """
        from mosaia.collections import Tools

        return Tools(self.get_uri())

    async def upload_profile_image(self, file) -> "User":
        """
        Upload a profile image.

        This method uploads and sets a profile image for the user. The image
        will be used to represent the user across the platform in various
        UI elements.

        Args:
            file: Image file to upload (supports common formats)

        Returns:
            Updated user instance

        Raises:
            Error: When upload fails
            Error: When file format is invalid
            Error: When network errors occur

        Examples:
            Basic upload:
            >>> with open('avatar.jpg', 'rb') as f:
            ...     await user.upload_profile_image(f)
            ...     print('Profile image updated successfully')

            Upload with validation:
            >>> async def update_profile_image(user, file_path):
            ...     try:
            ...         # Validate file
            ...         if not file_path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            ...             raise ValueError('Invalid file type')
            ...
            ...         file_size = os.path.getsize(file_path)
            ...         if file_size > 5 * 1024 * 1024:
            ...             raise ValueError('File too large (max 5MB)')
            ...
            ...         # Upload and update
            ...         with open(file_path, 'rb') as f:
            ...             updated = await user.upload_profile_image(f)
            ...
            ...         print('Profile updated successfully')
            ...         print(f"Size: {file_size} bytes")
            ...
            ...         return updated
            ...     except Exception as error:
            ...         print(f'Profile update failed: {error}')
            ...         raise error
        """
        try:
            path = f"{self.get_uri()}/profile/image/upload"
            response = await self.api_client.post_multipart(path, file)

            if isinstance(response, dict):
                data = response.get("data", response)
                if isinstance(data, dict):
                    self.update(data)
            return self
        except Exception as error:
            raise self._handle_error(error)
