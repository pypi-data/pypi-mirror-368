"""
Base functions class that provides common functionality for all function classes.

This abstract class serves as the foundation for all API function classes in the SDK.
It provides standardized CRUD operations, configuration management, and error handling
that can be extended by specific function implementations.
"""

import urllib.parse
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, Optional, TypeVar, Union

from ..config import ConfigurationManager
from ..types import MosaiaConfig
from ..utils.api_client import APIClient

# Type variables for generic responses
T = TypeVar("T")
GetPayload = TypeVar("GetPayload")
CreatePayload = TypeVar("CreatePayload")


class BaseFunctions(ABC, Generic[T, GetPayload, CreatePayload]):
    """
    Base functions class that provides common functionality for all function classes.

    This abstract class serves as the foundation for all API function classes in the SDK.
    It provides standardized CRUD operations, configuration management, and error handling
    that can be extended by specific function implementations.

    Examples:
        >>> class Users(BaseFunctions[UserInterface, GetUsersPayload, GetUserPayload]):
        ...     def __init__(self):
        ...         super().__init__('/user')
        ...
        >>> users = Users()
        >>> all_users = await users.get()
        >>> new_user = await users.create({'email': 'john@example.com'})
    """

    def __init__(self, uri: Optional[str] = None):
        """
        Initialize the BaseFunctions.

        Args:
            uri: Optional base URI for the API endpoint

        Examples:
            >>> class Users(BaseFunctions):
            ...     def __init__(self):
            ...         super().__init__('/user')
        """
        self._config_manager = ConfigurationManager.get_instance()
        # Create API client (uses ConfigurationManager internally)
        self._api_client = APIClient()
        self._uri = uri or ""

    @property
    def config(self) -> MosaiaConfig:
        """
        Get the current configuration from the ConfigurationManager.

        This property provides access to the current SDK configuration,
        including API keys, URLs, and other settings.

        Returns:
            The current MosaiaConfig object

        Examples:
            >>> current_config = self.config
            >>> print('API URL:', current_config.api_url)
            >>> print('API Key:', current_config.api_key)
        """
        return self._config_manager.get_config()

    @property
    def uri(self) -> str:
        """
        Get the base URI for this function class.

        This property provides access to the base URI used for API requests.

        Returns:
            The base URI string

        Examples:
            >>> functions = BaseFunctions('/user')
            >>> print('URI:', functions.uri)  # '/user'
        """
        return self._uri

    @property
    def api_client(self) -> APIClient:
        """
        Get the API client instance.

        This property provides access to the internal API client used for
        making HTTP requests.

        Returns:
            The APIClient instance

        Examples:
            >>> functions = BaseFunctions()
            >>> client = functions.api_client
        """
        return self._api_client

    @property
    def config_manager(self) -> ConfigurationManager:
        """
        Get the configuration manager instance.

        This property provides access to the internal configuration manager
        used for managing SDK configuration.

        Returns:
            The ConfigurationManager instance

        Examples:
            >>> functions = BaseFunctions()
            >>> manager = functions.config_manager
        """
        return self._config_manager

    async def get(
        self, params: Optional[Dict[str, Any]] = None, id: Optional[str] = None
    ) -> GetPayload:
        """
        Get entities with optional filtering and pagination.

        This method retrieves entities from the API. When called without an ID,
        it returns a list of entities with optional filtering and pagination.
        When called with an ID, it returns a specific entity.

        Args:
            params: Optional query parameters for filtering and pagination
                - limit: Maximum number of items to return
                - offset: Number of items to skip (for pagination)
                - q: Search query for text-based filtering
                - active: Filter by active status
                - tags: Array of tags to filter by
            id: Optional specific entity ID to retrieve

        Returns:
            Entity data

        Examples:
            # Get all entities
            >>> all_entities = await functions.get()

            # Get entities with filtering
            >>> filtered_entities = await functions.get({
            ...     'limit': 10,
            ...     'offset': 0,
            ...     'q': 'search term',
            ...     'active': True
            ... })

            # Get specific entity by ID
            >>> entity = await functions.get({}, 'entity-id')

        Raises:
            Error: When API request fails
        """
        try:
            uri = self._uri
            if id:
                uri = f"{uri}/{id}"

            return await self._api_client.get(uri, params)
        except Exception as error:
            raise self._handle_error(error)

    async def create(
        self, entity: T, params: Optional[Dict[str, Any]] = None
    ) -> CreatePayload:
        """
        Create a new entity.

        This method creates a new entity in the system. The entity ID will be
        automatically generated by the server.

        Args:
            entity: Entity data for the new entity (ID will be generated)
                - id: Optional ID (will be ignored, server generates ID)
                - active: Whether the entity should be active
                - external_id: External system identifier
                - extensors: Extended properties for custom integrations
            params: Optional query parameters to include in the request

        Returns:
            The created entity

        Examples:
            # Create a new user
            >>> new_user = await users.create({
            ...     'email': 'john@example.com',
            ...     'first_name': 'John',
            ...     'last_name': 'Doe',
            ...     'active': True
            ... })

            # Create with external ID
            >>> new_agent = await agents.create({
            ...     'name': 'My Agent',
            ...     'short_description': 'A helpful AI agent',
            ...     'external_id': 'agent-123',
            ...     'extensors': {
            ...         'custom_field': 'custom value'
            ...     }
            ... })

        Raises:
            Error: When API request fails or validation fails
        """
        try:
            uri = self._uri

            if params:
                query_string = urllib.parse.urlencode(params)
                uri += f"?{query_string}"

            return await self._api_client.post(uri, entity)
        except Exception as error:
            raise self._handle_error(error)

    async def update(
        self, id: str, entity: Dict[str, Any], params: Optional[Dict[str, Any]] = None
    ) -> CreatePayload:
        """
        Update an existing entity.

        This method updates an existing entity in the system. Only the fields
        provided in the entity parameter will be updated.

        Args:
            id: The entity ID to update
            entity: Entity data for the update (only provided fields will be updated)
                - active: Whether the entity should be active
                - external_id: External system identifier
                - extensors: Extended properties for custom integrations
            params: Optional query parameters to include in the request

        Returns:
            The updated entity

        Examples:
            # Update user's email
            >>> updated_user = await users.update('user-id', {
            ...     'email': 'newemail@example.com'
            ... })

            # Update multiple fields
            >>> updated_agent = await agents.update('agent-id', {
            ...     'name': 'Updated Agent Name',
            ...     'short_description': 'Updated description',
            ...     'active': False
            ... })

            # Update with external ID
            >>> updated_org = await organizations.update('org-id', {
            ...     'name': 'New Organization Name',
            ...     'external_id': 'new-external-id'
            ... })

        Raises:
            Error: When API request fails, entity not found, or validation fails
        """
        try:
            uri = f"{self._uri}/{id}"

            if params:
                query_string = urllib.parse.urlencode(params)
                uri += f"?{query_string}"

            return await self._api_client.put(uri, entity)
        except Exception as error:
            raise self._handle_error(error)

    async def delete(self, id: str, params: Optional[Dict[str, Any]] = None) -> None:
        """
        Delete an entity.

        This method permanently deletes an entity from the system. This action
        cannot be undone, so use with caution.

        Args:
            id: The entity ID to delete
            params: Optional query parameters (e.g., force deletion flags)
                - force: Force deletion even if entity has dependencies

        Examples:
            # Delete a user
            >>> await users.delete('user-id')

            # Force delete an organization
            >>> await organizations.delete('org-id', {'force': True})

            # Delete with additional parameters
            >>> await agents.delete('agent-id', {
            ...     'force': True,
            ...     'cascade': True
            ... })

        Raises:
            Error: When API request fails, entity not found, or deletion is not allowed
        """
        try:
            uri = f"{self._uri}/{id}"

            if params:
                query_string = urllib.parse.urlencode(params)
                uri += f"?{query_string}"

            await self._api_client.delete(uri, params)
        except Exception as error:
            raise self._handle_error(error)

    def _handle_error(self, error: Any) -> Exception:
        """
        Handle API errors consistently across all function classes.

        This protected method provides standardized error handling for all
        API operations. It ensures that errors are properly formatted and
        contain meaningful messages.

        Args:
            error: The error to handle (can be any type)

        Returns:
            Standardized Error object with a meaningful message

        Examples:
            >>> try:
            ...     result = await self.api_client.get('/endpoint')
            ...     return result
            ... except Exception as error:
            ...     raise self._handle_error(error)
        """
        if hasattr(error, "message"):
            return Exception(str(error.message))

        if isinstance(error, dict) and "message" in error:
            return Exception(error["message"])

        if isinstance(error, str):
            return Exception(error)

        if hasattr(error, "__str__") and str(error) != repr(error):
            return Exception(str(error))

        return Exception("Unknown error occurred")
