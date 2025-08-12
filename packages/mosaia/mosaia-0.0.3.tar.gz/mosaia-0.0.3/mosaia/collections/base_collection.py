"""
Base Collection class that provides common functionality for all collection clients.

This abstract class serves as the foundation for all collection classes in the SDK.
It provides standardized CRUD operations, configuration management, error handling,
and model instantiation capabilities.

Features:
- Standardized CRUD operations (GET, POST)
- Automatic configuration management
- Consistent error handling
- Response processing and type safety
- Model instantiation and hydration
- Pagination support
- Query parameter handling
"""

import urllib.parse
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from ..config import ConfigurationManager
from ..types import BatchAPIResponse, MosaiaConfig, PagingInterface, QueryParams
from ..utils.api_client import APIClient

# Type variables for generic responses
T = TypeVar("T")
M = TypeVar("M")
GetPayload = TypeVar("GetPayload")
CreatePayload = TypeVar("CreatePayload")


class BaseCollection(ABC, Generic[T, M, GetPayload, CreatePayload]):
    """
    Base Collection class that provides common functionality for all collection clients.

    This abstract class serves as the foundation for all collection classes in the SDK.
    It provides standardized CRUD operations, configuration management, error handling,
    and model instantiation capabilities.

    Examples:
        >>> class Users(BaseCollection[UserInterface, User, GetUsersPayload, GetUserPayload]):
        ...     def __init__(self):
        ...         super().__init__('/user', User)
        ...
        >>> users = Users()
        >>> all_users = await users.get()
        >>> new_user = await users.create({'email': 'john@example.com'})
    """

    def __init__(self, uri: str, model_class: Type[M]):
        """
        Creates a new Base Collection instance.

        Initializes a collection with the specified API endpoint and model class.
        The collection will use these to handle CRUD operations and instantiate
        model objects from API responses.

        Args:
            uri: The API endpoint path (e.g., '/user', '/agent')
            model_class: The model class constructor for creating instances

        Examples:
            >>> class Users(BaseCollection[UserInterface, User]):
            ...     def __init__(self):
            ...         # Initialize with /user endpoint and User model
            ...         super().__init__('/user', User)
        """
        self._config_manager = ConfigurationManager.get_instance()
        self._api_client = APIClient()
        self._uri = uri
        self._model_class = model_class

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
        Get the base URI for this collection.

        This property provides access to the base URI used for API requests.

        Returns:
            The base URI string

        Examples:
            >>> functions = BaseCollection('/user', User)
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
            >>> functions = BaseCollection('/user', User)
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
            >>> functions = BaseCollection('/user', User)
            >>> manager = functions.config_manager
        """
        return self._config_manager

    async def get(
        self, params: Optional[Dict[str, Any]] = None, id: Optional[str] = None
    ) -> Union[BatchAPIResponse, M, None]:
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
            Entity data - either a list of entities (BatchAPIResponse) or a single entity

        Examples:
            # Get multiple entities with filtering
            >>> result = await collection.get({
            ...     'limit': 10,
            ...     'offset': 0,
            ...     'q': 'search term',
            ...     'active': True,
            ...     'tags': ['tag1', 'tag2']
            ... })
            >>> print('Items:', result.data)
            >>> print('Total:', result.paging.total)

            # Get single entity by ID
            >>> entity = await collection.get({}, 'entity-id')
            >>> if entity:
            ...     print('Found:', entity.id)
            ... else:
            ...     print('Entity not found')

        Raises:
            Error: When API request fails or response is invalid
        """
        try:
            uri = self._uri
            if id:
                uri = f"{uri}/{id}"

            response = await self._api_client.get(uri, params)

            # No response
            if response is None:
                return None

            # List retrieval without ID must include paging; raw lists are invalid
            if isinstance(response, list):
                raise Exception("Invalid response from API")

            if isinstance(response, dict):
                data = response.get("data")
                paging = response.get("paging")
                if isinstance(data, list):
                    # Require paging metadata for batch responses
                    if paging is None:
                        raise Exception("Invalid response from API")
                    paging_obj = paging
                    if isinstance(paging, dict):
                        paging_obj = PagingInterface(
                            **{
                                k: v
                                for k, v in paging.items()
                                if k
                                in ["offset", "limit", "total", "page", "total_pages"]
                            }
                        )
                    # Convert raw data items to model instances
                    model_instances = [
                        self._create_model(item, self.uri) for item in data
                    ]
                    return BatchAPIResponse(data=model_instances, paging=paging_obj)
                if isinstance(data, dict):
                    return self._create_model(data, self.uri)
                # Unknown dict shape
                raise Exception("Invalid response from API")

            # Unknown response type
            raise Exception("Invalid response from API")
        except Exception as error:
            # Preserve original error message for easier debugging
            raise Exception(str(error))

    async def create(self, entity: Dict[str, Any]) -> M:
        """
        Create a new entity.

        This method creates a new entity in the system. The entity ID will be
        automatically generated by the server. The method returns a new model
        instance initialized with the created entity's data.

        Args:
            entity: Entity data for the new entity (without ID)
                - id: Optional ID (will be ignored, server generates ID)
                - active: Whether the entity should be active
                - external_id: External system identifier
                - extensors: Extended properties for custom integrations

        Returns:
            A new model instance

        Examples:
            # Create a new user
            >>> new_user = await users.create({
            ...     'email': 'user@example.com',
            ...     'first_name': 'John',
            ...     'last_name': 'Doe',
            ...     'active': True
            ... })
            >>> print('Created user:', new_user.id)

            # Create with external ID
            >>> new_agent = await agents.create({
            ...     'name': 'Customer Support',
            ...     'short_description': 'AI agent for support',
            ...     'external_id': 'agent-123',
            ...     'extensors': {
            ...         'custom_field': 'value'
            ...     }
            ... })

        Raises:
            Error: When API request fails or response is invalid
            Error: When required fields are missing
        """
        try:
            response = await self._api_client.post(self._uri, entity)

            # Handle the case where response might be undefined or null
            if response is None:
                raise Exception("Invalid response from API")

            if isinstance(response, dict) and "data" in response:
                return self._create_model(response.get("data"))

            # Treat a plain dict as the created entity payload
            if isinstance(response, dict):
                return self._create_model(response)

            raise Exception("Invalid response from API")
        except Exception as error:
            # Preserve original error message for easier debugging
            raise Exception(str(error))

    def _create_model(self, data: Dict[str, Any], uri: Optional[str] = None) -> M:
        """
        Create a model instance from raw data.

        This method can be overridden by subclasses to customize model instantiation.
        By default, it creates a model instance directly using the model class.

        Args:
            data: Raw data to create the model from

        Returns:
            Model instance
        """
        return self._model_class(data, uri)

    def _handle_error(self, error: Any) -> Exception:
        """
        Handle API errors consistently across all collection classes.

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
        if isinstance(error, dict) and "message" in error:
            return Exception(error["message"])

        if isinstance(error, str):
            return Exception(error)

        if hasattr(error, "__str__") and str(error) != repr(error):
            return Exception(str(error))

        return Exception("Unknown error occurred")
