"""
Main Mosaia SDK client class.

Provides access to all Mosaia API endpoints through a unified interface.
Supports authentication, user management, organization management, AI agents,
tools, applications, and more.

The MosaiaClient is the primary entry point for all SDK operations. It manages
configuration, authentication, and provides access to all API collections.
"""

from typing import Any, Dict, Optional

from .auth import MosaiaAuth, OAuth
from .collections import (
    AgentGroups,
    Agents,
    AppBots,
    Apps,
    Clients,
    Models,
    Organizations,
    OrgUsers,
    Tools,
    Users,
)
from .config import ConfigurationManager
from .models import Session
from .types import MosaiaConfig, OAuthConfig, UserInterface
from .utils.api_client import APIClient


class MosaiaClient:
    """
    Main Mosaia SDK client class.

    Provides access to all Mosaia API endpoints through a unified interface.
    Supports authentication, user management, organization management, AI agents,
    tools, applications, and more.

    The MosaiaClient is the primary entry point for all SDK operations. It manages
    configuration, authentication, and provides access to all API collections.

    Examples:
        >>> from mosaia import MosaiaClient

        # Create a new Mosaia SDK instance
        >>> mosaia = MosaiaClient({
        ...     'api_key': 'your-api-key',
        ...     'api_url': 'https://api.mosaia.ai',
        ...     'version': '1'
        ... })

        # Get all users
        >>> users = await mosaia.users.get()

        # Create an OAuth instance
        >>> oauth = mosaia.oauth({
        ...     'redirect_uri': 'https://your-app.com/callback',
        ...     'scopes': ['read', 'write']
        ... })
    """

    def __init__(self, config: MosaiaConfig):
        """
        Creates a new Mosaia SDK instance.

        Initializes the SDK with the provided configuration and sets up
        the internal configuration manager. The configuration is used
        for all subsequent API requests.

        Args:
            config: Configuration object for the SDK
                - api_key: API key for authentication (optional)
                - api_url: Base URL for API requests (defaults to https://api.mosaia.ai)
                - version: API version (defaults to '1')
                - client_id: Client ID for OAuth flows (required for OAuth)
                - client_secret: Client secret for client credentials flow (optional)
                - user: User ID for user-scoped operations (optional)
                - org: Organization ID for org-scoped operations (optional)

        Examples:
            # Minimal configuration with API key
            >>> mosaia = MosaiaClient({
            ...     'api_key': 'your-api-key'
            ... })

            # Full configuration with OAuth support
            >>> mosaia = MosaiaClient({
            ...     'api_key': 'your-api-key',
            ...     'api_url': 'https://api.mosaia.ai',
            ...     'version': '1',
            ...     'client_id': 'your-client-id',
            ...     'client_secret': 'your-client-secret',
            ...     'user': 'user-id',
            ...     'org': 'org-id'
            ... })
        """
        self._config_manager = ConfigurationManager.get_instance()
        self._config_manager.initialize(config)

    @property
    def config(self) -> MosaiaConfig:
        """
        Get the current configuration.

        Returns the current configuration object used by this client instance.

        Returns:
            The current configuration object

        Examples:
            >>> config = mosaia.config
            >>> print(config.api_key)  # 'your-api-key'
            >>> print(config.api_url)  # 'https://api.mosaia.ai'
        """
        return self._config_manager.get_config()

    @config.setter
    def config(self, config: MosaiaConfig) -> None:
        """
        Set the configuration.

        Updates the configuration for this client instance. This will
        affect all subsequent API requests made through this client.

        Args:
            config: The new configuration object

        Examples:
            >>> mosaia.config = {
            ...     'api_key': 'new-api-key',
            ...     'api_url': 'https://api-staging.mosaia.ai'
            ... }
        """
        self._config_manager.initialize(config)

    @property
    def api_key(self) -> Optional[str]:
        """Get the current API key."""
        return self.config.api_key

    @api_key.setter
    def api_key(self, api_key: str) -> None:
        """
        Set the API key for authentication.

        Updates the API key used for authenticating requests to the Mosaia API.
        This can be used to change authentication credentials at runtime.

        Args:
            api_key: The new API key for authentication

        Examples:
            >>> mosaia.api_key = 'new-api-key-123'
            >>> # Now all subsequent requests will use the new API key
            >>> users = await mosaia.users.get()
        """
        self._config_manager.update_config({"api_key": api_key})

    @property
    def version(self) -> Optional[str]:
        """Get the current API version."""
        return self.config.version

    @version.setter
    def version(self, version: str) -> None:
        """
        Set the API version.

        Updates the API version used for requests. This affects the version
        header sent with API requests.

        Args:
            version: The new API version (e.g., '1', '2')

        Examples:
            >>> mosaia.version = '2'
            >>> # Now all subsequent requests will use API v2
            >>> users = await mosaia.users.get()
        """
        self._config_manager.update_config({"version": version})

    @property
    def api_url(self) -> Optional[str]:
        """Get the current API base URL."""
        return self.config.api_url

    @api_url.setter
    def api_url(self, api_url: str) -> None:
        """
        Set the API base URL.

        Updates the base URL used for API requests. This is useful for
        switching between different environments (development, staging, production).

        Args:
            api_url: The new API base URL

        Examples:
            # Switch to staging environment
            >>> mosaia.api_url = 'https://api-staging.mosaia.ai'

            # Switch to production environment
            >>> mosaia.api_url = 'https://api.mosaia.ai'

            # Switch to local development
            >>> mosaia.api_url = 'http://localhost:3000'
        """
        self._config_manager.update_config({"api_url": api_url})

    @property
    def client_id(self) -> Optional[str]:
        """Get the current OAuth client ID."""
        return self.config.client_id

    @client_id.setter
    def client_id(self, client_id: str) -> None:
        """
        Set the OAuth client ID.

        Updates the OAuth client ID used for authentication flows.
        This is required for OAuth-based authentication.

        Args:
            client_id: The new OAuth client ID

        Examples:
            >>> mosaia.client_id = 'new-client-id-123'
            >>> # Create OAuth instance with updated client ID
            >>> oauth = mosaia.oauth({
            ...     'redirect_uri': 'https://myapp.com/callback',
            ...     'scopes': ['read', 'write']
            ... })
        """
        self._config_manager.update_config({"client_id": client_id})

    @property
    def client_secret(self) -> Optional[str]:
        """Get the current OAuth client secret."""
        return self.config.client_secret

    @client_secret.setter
    def client_secret(self, client_secret: str) -> None:
        """
        Set the OAuth client secret.

        Updates the OAuth client secret used for client credentials flow.
        This is used for server-to-server authentication.

        Args:
            client_secret: The new OAuth client secret

        Examples:
            >>> mosaia.client_secret = 'new-client-secret-456'
            >>> # Use client credentials flow with updated secret
            >>> auth = MosaiaAuth(mosaia.config)
            >>> auth_response = await auth.sign_in_with_client(
            ...     mosaia.config.client_id,
            ...     mosaia.config.client_secret
            ... )
        """
        self._config_manager.update_config({"client_secret": client_secret})

    @property
    def auth(self) -> MosaiaAuth:
        """
        Access to Authentication API.

        Handle authentication flows, including sign in, sign out, token refresh, and session management.

        Returns:
            MosaiaAuth: Authentication API client

        Examples:
            # Sign in with password
            >>> auth = await mosaia.auth.sign_in_with_password('user@example.com', 'password', 'client-id')

            # Sign in with client credentials
            >>> auth = await mosaia.auth.sign_in_with_client('client-id', 'client-secret')

            # Refresh token
            >>> new_auth = await mosaia.auth.refresh_token('refresh-token')

            # Sign out
            >>> await mosaia.auth.sign_out()
        """
        return MosaiaAuth()

    @property
    def agents(self) -> Agents:
        """
        Access to Agents API.

        Manage AI agents, including CRUD operations, chat completions, and agent-specific functionality.

        Returns:
            Agents: Agents API client

        Examples:
            # Get all agents
            >>> agents = await mosaia.agents.get()

            # Get specific agent
            >>> agent = await mosaia.agents.get({}, 'agent-id')

            # Create chat completion
            >>> completion = await mosaia.agents.chat_completion('agent-id', {
            ...     'model': 'gpt-4',
            ...     'messages': [{'role': 'user', 'content': 'Hello'}]
            ... })
        """
        return Agents()

    @property
    def apps(self) -> Apps:
        """
        Access to Applications API.

        Manage applications, including CRUD operations and app-specific functionality.

        Returns:
            Apps: Applications API client

        Examples:
            # Get all apps
            >>> apps = await mosaia.apps.get()

            # Get specific app
            >>> app = await mosaia.apps.get({}, 'app-id')

            # Create new app
            >>> new_app = await mosaia.apps.create({
            ...     'name': 'My App',
            ...     'short_description': 'Description'
            ... })
        """
        return Apps()

    @property
    def tools(self) -> Tools:
        """
        Access to Tools API.

        Manage tools and integrations, including CRUD operations and tool-specific functionality.

        Returns:
            Tools: Tools API client

        Examples:
            # Get all tools
            >>> tools = await mosaia.tools.get()

            # Get specific tool
            >>> tool = await mosaia.tools.get({}, 'tool-id')

            # Create new tool
            >>> new_tool = await mosaia.tools.create({
            ...     'name': 'My Tool',
            ...     'short_description': 'Description',
            ...     'tool_schema': '{}'
            ... })
        """
        return Tools()

    @property
    def users(self) -> Users:
        """
        Access to Users API.

        Manage users, including CRUD operations, authentication, and user-specific functionality.

        Returns:
            Users: Users API client

        Examples:
            # Get all users
            >>> users = await mosaia.users.get()

            # Get specific user
            >>> user = await mosaia.users.get({}, 'user-id')

            # Create new user
            >>> new_user = await mosaia.users.create({
            ...     'email': 'user@example.com',
            ...     'first_name': 'John',
            ...     'last_name': 'Doe'
            ... })
        """
        return Users()

    @property
    def organizations(self) -> Organizations:
        """
        Access to Organizations API.

        Manage organizations, including CRUD operations and organization-specific functionality.

        Returns:
            Organizations: Organizations API client

        Examples:
            # Get all organizations
            >>> orgs = await mosaia.organizations.get()

            # Get specific organization
            >>> org = await mosaia.organizations.get({}, 'org-id')

            # Create new organization
            >>> new_org = await mosaia.organizations.create({
            ...     'name': 'My Organization',
            ...     'short_description': 'Description'
            ... })
        """
        return Organizations()

    @property
    def agent_groups(self) -> AgentGroups:
        """
        Access to Agent Groups API.

        Manage agent groups for multi-agent collaboration, including CRUD operations and group-specific functionality.

        Returns:
            AgentGroups: Agent Groups API client

        Examples:
            # Get all agent groups
            >>> groups = await mosaia.agent_groups.get()

            # Get specific agent group
            >>> group = await mosaia.agent_groups.get({}, 'group-id')

            # Create chat completion with group
            >>> completion = await mosaia.agent_groups.chat_completion('group-id', {
            ...     'model': 'gpt-4',
            ...     'messages': [{'role': 'user', 'content': 'Hello'}]
            ... })
        """
        return AgentGroups()

    @property
    def models(self) -> Models:
        """
        Access to Models API.

        Manage AI models, including CRUD operations and model-specific functionality.

        Returns:
            Models: Models API client

        Examples:
            # Get all models
            >>> models = await mosaia.models.get()

            # Get specific model
            >>> model = await mosaia.models.get({}, 'model-id')

            # Create new model
            >>> new_model = await mosaia.models.create({
            ...     'name': 'My Model',
            ...     'provider': 'openai',
            ...     'model_id': 'gpt-4'
            ... })
        """
        return Models()

    async def session(self) -> Session:
        """
        Get the current user session.

        Retrieves information about the currently authenticated user,
        including user details, organization information, and permissions.

        Returns:
            Session: Session object containing user and organization information

        Raises:
            Error: When authentication fails or session is invalid

        Examples:
            >>> try:
            ...     session = await mosaia.session()
            ...     print('User:', session.user.email)
            ...     print('Organization:', session.org.name)
            ... except Exception as error:
            ...     print('Session error:', error.message)
        """
        try:
            if not self.config:
                raise Exception("Mosaia is not initialized")

            # Use APIClient as a context manager to auto-close resources
            async with APIClient() as client:
                response = await client.get("/self")

            if "error" in response:
                raise Exception(response["error"]["message"])

            return Session(response.get("data", {}))
        except Exception as error:
            # Preserve the actual error message for easier debugging
            raise Exception(str(error))

    def oauth(self, oauth_config: OAuthConfig) -> OAuth:
        """
        Creates a new OAuth instance for handling OAuth2 Authorization Code flow with PKCE.

        This method creates an OAuth client that supports the PKCE (Proof Key for Code Exchange)
        flow for secure authentication, even for public clients.

        Args:
            oauth_config: OAuth configuration object
                - redirect_uri: The redirect URI for the OAuth flow (must match registered client)
                - scopes: Optional array of scopes to request (e.g., ['read', 'write'])

        Returns:
            OAuth: OAuth instance for handling the authentication flow

        Raises:
            Error: When client_id is not provided in SDK configuration

        Examples:
            # Initialize OAuth
            >>> oauth = mosaia.oauth({
            ...     'redirect_uri': 'https://your-app.com/callback',
            ...     'scopes': ['read', 'write']
            ... })

            # Get authorization URL and code verifier
            >>> auth_data = oauth.get_authorization_url_and_code_verifier()
            >>> url = auth_data['url']
            >>> code_verifier = auth_data['code_verifier']

            # Redirect user to the authorization URL
            # After user authorizes, you'll receive a code in your callback

            # Exchange code for new authenticated config (requires the code verifier)
            >>> new_config = await oauth.authenticate_with_code_and_verifier(code, code_verifier)

            # Create new instance with authenticated config
            >>> new_mosaia_instance = MosaiaClient(new_config)
        """
        return OAuth(oauth_config)
