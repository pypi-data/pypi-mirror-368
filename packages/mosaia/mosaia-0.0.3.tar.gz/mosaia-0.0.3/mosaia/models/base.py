"""
Base model class that provides common functionality for all models.

This abstract class serves as the foundation for all model classes in the SDK.
It provides standardized data management, CRUD operations, and serialization
capabilities that are inherited by all specific model implementations.
"""

import json
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, Optional, TypeVar, Union

from ..config import ConfigurationManager
from ..types import MosaiaConfig
from ..utils.api_client import APIClient

# Type variable for generic responses
T = TypeVar("T")


class BaseModel(ABC, Generic[T]):
    """
    Base model class that provides common functionality for all models.

    This abstract class serves as the foundation for all model classes in the SDK.
    It provides standardized data management, CRUD operations, and serialization
    capabilities that are inherited by all specific model implementations.

    Features:
    - Automatic property mapping from data
    - CRUD operations (save, delete)
    - Configuration management
    - Data validation and type safety
    - JSON serialization
    - API payload generation
    - Error handling

    Examples:
        Basic model implementation:
        >>> class User(BaseModel[UserInterface]):
        ...     def __init__(self, data: Dict[str, Any]):
        ...         super().__init__(data, '/user')
        ...
        ...     # Add custom methods
        ...     async def update_email(self, email: str) -> None:
        ...         await self.save({'email': email})

        Using model instances:
        >>> # Create a new user instance
        >>> user = User({
        ...     'email': 'user@example.com',
        ...     'first_name': 'John'
        ... })
        >>>
        >>> # Update properties
        >>> user.update({'last_name': 'Doe'})
        >>>
        >>> # Save changes
        >>> await user.save()
        >>>
        >>> # Convert to JSON
        >>> data = user.to_json()
    """

    def __init__(self, data: Dict[str, Any], uri: Optional[str] = None):
        """
        Initialize the BaseModel.

        Args:
            data: Model data dictionary
            uri: Optional URI path for the model endpoint

        Examples:
            >>> class User(BaseModel):
            ...     def __init__(self, data):
            ...         super().__init__(data, '/user')
        """
        self.data = data or {}
        self.uri = uri or ""
        self.config_manager = ConfigurationManager.get_instance()

        # Map data properties to instance attributes without triggering property getters
        reserved_keys = ["config", "api_client", "data", "uri", "config_manager"]
        for key, value in self.data.items():
            if key in reserved_keys:
                continue
            # Inspect class attributes to avoid evaluating property getters on the instance
            class_attr = getattr(self.__class__, key, None)
            # Skip if there is a property or a callable defined on the class with this name
            if isinstance(class_attr, property) or callable(class_attr):
                continue
            # Skip if already set explicitly
            if key in self.__dict__:
                continue
            setattr(self, key, value)

        # Create API client (uses ConfigurationManager internally)
        self.api_client = APIClient()

    @property
    def config(self) -> MosaiaConfig:
        """
        Get the current configuration from the ConfigurationManager.

        This protected property provides access to the current SDK configuration,
        including API keys, URLs, and other settings.

        Returns:
            The current MosaiaConfig object

        Examples:
            >>> def some_method(self):
            ...     config = self.config
            ...     print('Using API URL:', config.api_url)
        """
        try:
            return self.config_manager.get_config()
        except RuntimeError:
            # Configuration not initialized, return a default config
            from ..types import MosaiaConfig

            return MosaiaConfig()

    def is_active(self) -> bool:
        """
        Check if the entity is active.

        This method checks the active status of the entity. Most entities in the
        system can be active or inactive, which affects their availability and
        usability in the platform.

        Returns:
            True if the entity is active, false otherwise

        Examples:
            >>> user = User(user_data)
            >>> if user.is_active():
            ...     # Perform operations with active user
            ...     pass
            >>> else:
            ...     print('User is inactive')
        """
        return self.data.get("active", False) is True

    def to_json(self) -> Dict[str, Any]:
        """
        Convert model instance to interface data.

        This method serializes the model instance to a plain object that matches
        the interface type. This is useful for:
        - Sending data to the API
        - Storing data in a database
        - Passing data between components
        - Debugging model state

        Returns:
            The model data as a plain object matching the interface type

        Examples:
            >>> user = User({
            ...     'email': 'user@example.com',
            ...     'first_name': 'John'
            ... })
            >>>
            >>> data = user.to_json()
            >>> print(data)  # {'email': '...', 'first_name': '...'}
            >>>
            >>> # Use with JSON.stringify
            >>> json_str = json.dumps(user.to_json())
        """
        return self.data.copy()

    def to_api_payload(self) -> Dict[str, Any]:
        """
        Convert model instance to API payload.

        This method creates a payload suitable for API requests by:
        - Converting the model to a plain object
        - Removing read-only fields (like 'id')
        - Ensuring proper data format for the API

        Returns:
            A clean object suitable for API requests

        Examples:
            >>> user = User({
            ...     'id': '123',           # Will be removed from payload
            ...     'email': 'new@example.com',
            ...     'first_name': 'John'
            ... })
            >>>
            >>> payload = user.to_api_payload()
            >>> # payload = {'email': '...', 'first_name': '...'}
            >>> # Note: 'id' is removed as it's read-only
            >>>
            >>> await api_client.post('/users', payload)
        """
        data = self.data.copy()
        # Remove read-only fields
        data.pop("id", None)
        return data

    def update(self, updates: Dict[str, Any]) -> None:
        """
        Update model data with new values.

        This method updates the model's data and instance properties with new values.
        It performs a shallow merge of the updates with existing data, allowing for
        partial updates of the model's properties.

        Args:
            updates: Object containing properties to update

        Examples:
            >>> user = User({
            ...     'email': 'old@example.com',
            ...     'first_name': 'John'
            ... })
            >>>
            >>> # Update multiple properties
            >>> user.update({
            ...     'email': 'new@example.com',
            ...     'last_name': 'Doe'
            ... })
            >>>
            >>> # Save changes to API
            >>> await user.save()

        Note:
            This method only updates the local model instance. To persist changes
            to the API, call save() after updating.
        """
        self.data.update(updates)
        # Update instance properties
        for key, value in updates.items():
            setattr(self, key, value)

    async def save(self) -> Dict[str, Any]:
        """
        Save the model instance to the API.

        This method persists the current state of the model to the API using a PUT
        request. It requires the model to have an ID (existing instance). For new
        instances, use the collection's create method instead.

        The method:
        1. Validates the model has an ID
        2. Sends current data to the API
        3. Updates local instance with API response

        Returns:
            The updated model data

        Raises:
            Error: When model has no ID
            Error: When API request fails

        Examples:
            >>> user = User({
            ...     'id': '123',
            ...     'email': 'user@example.com'
            ... })
            >>>
            >>> # Update and save
            >>> user.update({'first_name': 'John'})
            >>> await user.save()

            Error handling:
            >>> try:
            ...     await user.save()
            ... except Exception as error:
            ...     if 'ID is required' in str(error):
            ...         # Handle missing ID error
            ...         pass
            ...     else:
            ...         # Handle API errors
            ...         pass
        """
        try:
            if not self.has_id():
                raise Exception("Entity ID is required for update")

            response = await self.api_client.put(
                f"{self.uri}/{self.get_id()}", self.to_json()
            )

            # Update the model's data with the response
            if isinstance(response, dict):
                self.update(response)
                return response
            else:
                # Handle case where response might be wrapped
                data = (
                    response.get("data", response)
                    if hasattr(response, "get")
                    else response
                )
                self.update(data)
                return data
        except Exception as error:
            raise self._handle_error(error)

    async def delete(self) -> None:
        """
        Delete the model instance from the API.

        This method permanently deletes the model instance from the API and clears
        the local data. This operation cannot be undone.

        The method:
        1. Validates the model has an ID
        2. Sends DELETE request to the API
        3. Clears local instance data on success

        Raises:
            Error: When model has no ID
            Error: When API request fails

        Examples:
            Basic deletion:
            >>> user = await users.get({}, 'user-id')
            >>> if user:
            ...     await user.delete()
            ...     # User is now deleted and instance is cleared

            Error handling:
            >>> try:
            ...     await user.delete()
            ...     print('User deleted successfully')
            ... except Exception as error:
            ...     if 'ID is required' in str(error):
            ...         print('Cannot delete - no ID')
            ...     else:
            ...         print(f'Deletion failed: {error}')
        """
        try:
            if not self.has_id():
                raise Exception("Entity ID is required for deletion")

            await self.api_client.delete(f"{self.uri}/{self.get_id()}")
            # Clear the model's data after deletion
            self._clear_data()
        except Exception as error:
            raise self._handle_error(error)

    def _clear_data(self) -> None:
        """
        Clear all model data.

        This protected method clears all data from the model instance while
        preserving essential internal properties. It's used after deletion
        or when resetting a model instance.

        The method:
        - Clears the data object
        - Removes instance properties
        - Preserves protected internal properties

        Examples:
            >>> def reset(self):
            ...     self._clear_data()
            ...     # Instance is now empty except for internal properties
        """
        self.data = {}
        # Clear instance properties except protected ones
        protected_keys = ["config", "api_client", "data", "uri", "config_manager"]
        for key in list(self.__dict__.keys()):
            if key not in protected_keys:
                delattr(self, key)

    def has_id(self) -> bool:
        """
        Check if the model has an ID.

        This protected method checks if the model instance has a valid ID.
        It's used internally to validate operations that require an ID.

        Returns:
            True if the model has an ID, false otherwise

        Examples:
            >>> def validate_update(self):
            ...     if not self.has_id():
            ...         raise Exception('Cannot update without ID')
            ...     # Continue with update
        """
        return bool(self.data.get("id"))

    def get_id(self) -> str:
        """
        Get the model's ID.

        This protected method safely retrieves the model's ID, throwing an error
        if the ID is not available. It's used internally by methods that require
        an ID to operate.

        Returns:
            The model's ID

        Raises:
            Error: When the model has no ID

        Examples:
            >>> def fetch_details(self):
            ...     try:
            ...         id = self.get_id()
            ...         details = await self.api_client.get(f'/details/{id}')
            ...         self.update(details)
            ...     except Exception as error:
            ...         # Handle missing ID or API errors
            ...         pass
        """
        if not self.has_id():
            raise Exception("Entity ID is required")
        return self.data["id"]

    def get_uri(self) -> str:
        """
        Get the model's complete API URI.

        This protected method constructs the complete URI for API requests by
        combining the base URI with the model's ID. It ensures the model has
        an ID before constructing the URI.

        Returns:
            The complete API URI for this model instance

        Raises:
            Error: When the model has no ID

        Examples:
            >>> def fetch_related(self):
            ...     try:
            ...         uri = self.get_uri()
            ...         related = await self.api_client.get(f'{uri}/related')
            ...         return related
            ...     except Exception as error:
            ...         # Handle missing ID or API errors
            ...         pass
        """
        if not self.has_id():
            return self.uri
        return f"{self.uri}/{self.get_id()}"

    def _handle_error(self, error: Any) -> Exception:
        """
        Handle API errors consistently.

        This protected method provides standardized error handling for all
        API operations. It ensures that errors are properly formatted and
        contain meaningful messages.

        The method handles:
        - Error objects with messages
        - Plain objects with message properties
        - Unknown error types

        Args:
            error: The error to handle (can be any type)

        Returns:
            Standardized Error object

        Examples:
            >>> def custom_operation(self):
            ...     try:
            ...         await self.api_client.post('/endpoint', data)
            ...     except Exception as error:
            ...         raise self._handle_error(error)
        """
        if hasattr(error, "message"):
            return Exception(str(error.message))

        if isinstance(error, dict) and "message" in error:
            return Exception(error["message"])

        if isinstance(error, str):
            return Exception(error)

        if hasattr(error, "__str__"):
            return Exception(str(error))

        return Exception("Unknown error occurred")

    def __str__(self) -> str:
        """
        String representation of the model.

        Returns a human-readable string representation of the model,
        typically including the model type and ID if available.

        Returns:
            String representation of the model

        Examples:
            >>> user = User({'id': '123', 'email': 'john@example.com'})
            >>> print(user)  # User(id=123, email=john@example.com)
        """
        model_name = self.__class__.__name__
        if self.has_id():
            return f"{model_name}(id={self.get_id()})"
        return f"{model_name}()"

    def __repr__(self) -> str:
        """
        Detailed string representation of the model.

        Returns a detailed string representation useful for debugging,
        including all model data.

        Returns:
            Detailed string representation of the model

        Examples:
            >>> user = User({'id': '123', 'email': 'john@example.com'})
            >>> repr(user)  # User({'id': '123', 'email': 'john@example.com'})
        """
        model_name = self.__class__.__name__
        return f"{model_name}({self.data})"

    def __eq__(self, other: Any) -> bool:
        """
        Check if this model equals another model.

        Two models are considered equal if they have the same type and ID.

        Args:
            other: Another model to compare with

        Returns:
            True if models are equal, false otherwise

        Examples:
            >>> user1 = User({'id': '123', 'email': 'john@example.com'})
            >>> user2 = User({'id': '123', 'email': 'jane@example.com'})
            >>> user1 == user2  # True (same ID)
        """
        if not isinstance(other, self.__class__):
            return False

        if not self.has_id() or not other.has_id():
            return False

        return self.get_id() == other.get_id()

    def __hash__(self) -> int:
        """
        Get hash value for the model.

        Returns a hash value based on the model type and ID.
        This allows models to be used as dictionary keys or in sets.

        Returns:
            Hash value for the model

        Examples:
            >>> user = User({'id': '123', 'email': 'john@example.com'})
            >>> hash(user)  # Hash value based on type and ID
        """
        if self.has_id():
            return hash((self.__class__, self.get_id()))
        return hash(self.__class__)
