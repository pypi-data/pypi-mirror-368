"""
Base API class for the Mosaia Python SDK.

This module provides the base API class that other API classes inherit from.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, Optional, TypeVar

from .types import APIResponse, QueryParams
from .utils.api_client import APIClient

T = TypeVar("T")


class BaseAPI(ABC, Generic[T]):
    """
    Base API class for all API operations.

    This class provides common functionality for all API classes including
    HTTP client management, request handling, and response processing.

    Examples:
        >>> class UsersAPI(BaseAPI[UserInterface]):
        ...     def __init__(self):
        ...         super().__init__()
        ...
        ...     async def get(self, user_id: Optional[str] = None) -> UserInterface:
        ...         if user_id:
        ...             return await self.client.get(f'/users/{user_id}')
        ...         return await self.client.get('/users')
    """

    def __init__(self, client: Optional[APIClient] = None):
        """
        Initialize the BaseAPI.

        Args:
            client: Optional APIClient instance (if not provided, creates a new one)
        """
        self.client = client or APIClient()

    async def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> T:
        """
        Make a GET request.

        Args:
            path: API endpoint path
            params: Optional query parameters

        Returns:
            API response data
        """
        return await self.client.get(path, params)

    async def post(self, path: str, data: Optional[Dict[str, Any]] = None) -> T:
        """
        Make a POST request.

        Args:
            path: API endpoint path
            data: Optional request body data

        Returns:
            API response data
        """
        return await self.client.post(path, data)

    async def put(self, path: str, data: Optional[Dict[str, Any]] = None) -> T:
        """
        Make a PUT request.

        Args:
            path: API endpoint path
            data: Optional request body data

        Returns:
            API response data
        """
        return await self.client.put(path, data)

    async def delete(self, path: str, params: Optional[Dict[str, Any]] = None) -> T:
        """
        Make a DELETE request.

        Args:
            path: API endpoint path
            params: Optional query parameters

        Returns:
            API response data
        """
        return await self.client.delete(path, params)

    async def close(self) -> None:
        """Close the API client."""
        await self.client.close()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
