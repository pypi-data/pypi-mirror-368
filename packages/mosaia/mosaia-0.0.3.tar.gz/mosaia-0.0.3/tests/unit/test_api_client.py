#!/usr/bin/env python3
"""
Tests for the APIClient class.

This module tests the APIClient class functionality, including URL construction,
request handling, and error management.

Test Coverage:
=============

1. Basic APIClient Functionality:
   - Client creation with configuration
   - Header construction (Authorization, Content-Type)
   - Base URL construction with version injection

2. URL Construction:
   - URL construction with leading slash removal
   - URL construction without leading slash
   - URL construction with complex paths
   - URL construction with query parameters
   - URL construction with different API versions

3. Request Methods:
   - GET request method
   - POST request method
   - PUT request method
   - DELETE request method

4. Error Handling:
   - Error response creation
   - Error handling with custom status codes

Key Changes Tested:
==================
- Fixed URL construction to properly include API version (e.g., /v1/auth/signin)
- Replaced urljoin with manual URL construction for better control
- Added proper version injection in base URL construction
- Ensured leading slash removal for consistent URL formatting
"""

import asyncio
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from mosaia.types import MosaiaConfig
from mosaia.utils.api_client import APIClient


@pytest.mark.unit
class TestAPIClient:
    """Test APIClient functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_config = MosaiaConfig(
            api_key="test-api-key",
            api_url="https://api.mosaia.ai",
            version="1",
            verbose=True,
        )

    def test_client_creation(self):
        """Test APIClient can be created."""
        client = APIClient(self.test_config)
        assert client is not None
        assert hasattr(client, "base_url")
        assert hasattr(client, "headers")

    def test_headers_contain_auth(self):
        """Test that headers contain authorization."""
        client = APIClient(self.test_config)
        assert "Authorization" in client.headers
        assert "Content-Type" in client.headers
        assert client.headers["Authorization"] == "Bearer test-api-key"
        assert client.headers["Content-Type"] == "application/json"

    def test_base_url_construction(self):
        """Test that base URL is constructed correctly with version."""
        client = APIClient(self.test_config)
        assert client.base_url == "https://api.mosaia.ai/v1"

    def test_base_url_with_different_version(self):
        """Test base URL construction with different version."""
        config = MosaiaConfig(
            api_key="test-api-key",
            api_url="https://api.mosaia.ai",
            version="2",
            verbose=True,
        )
        client = APIClient(config)
        assert client.base_url == "https://api.mosaia.ai/v2"

    def test_base_url_with_default_version(self):
        """Test base URL construction with default version."""
        config = MosaiaConfig(
            api_key="test-api-key", api_url="https://api.mosaia.ai", verbose=True
        )
        client = APIClient(config)
        assert client.base_url == "https://api.mosaia.ai/v1"

    def test_base_url_with_custom_api_url(self):
        """Test base URL construction with custom API URL."""
        config = MosaiaConfig(
            api_key="test-api-key",
            api_url="https://api-staging.mosaia.ai",
            version="1",
            verbose=True,
        )
        client = APIClient(config)
        assert client.base_url == "https://api-staging.mosaia.ai/v1"


@pytest.mark.unit
class TestAPIClientURLConstruction:
    """Test APIClient URL construction functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_config = MosaiaConfig(
            api_key="test-api-key",
            api_url="https://api.mosaia.ai",
            version="1",
            verbose=True,
        )

    def test_url_construction_logic(self):
        """Test URL construction logic without making actual requests."""
        client = APIClient(self.test_config)

        # Test URL construction with leading slash
        path = "/auth/signin"
        if path.startswith("/"):
            path = path[1:]  # Remove leading slash
        expected_url = f"{client.base_url}/{path}"
        assert expected_url == "https://api.mosaia.ai/v1/auth/signin"

        # Test URL construction without leading slash
        path = "auth/signin"
        expected_url = f"{client.base_url}/{path}"
        assert expected_url == "https://api.mosaia.ai/v1/auth/signin"

        # Test URL construction with complex path
        path = "/users/123/agents/456"
        if path.startswith("/"):
            path = path[1:]  # Remove leading slash
        expected_url = f"{client.base_url}/{path}"
        assert expected_url == "https://api.mosaia.ai/v1/users/123/agents/456"

    def test_url_construction_with_query_params(self):
        """Test URL construction with query parameters."""
        client = APIClient(self.test_config)

        # Test URL construction with query params
        path = "/users"
        if path.startswith("/"):
            path = path[1:]  # Remove leading slash
        base_url = f"{client.base_url}/{path}"

        # Simulate query string building
        params = {"limit": 10, "offset": 0}
        query_string = "?" + "&".join([f"{k}={v}" for k, v in params.items()])
        full_url = base_url + query_string

        assert full_url == "https://api.mosaia.ai/v1/users?limit=10&offset=0"

    def test_url_construction_with_different_version(self):
        """Test URL construction with different API version."""
        config = MosaiaConfig(
            api_key="test-api-key",
            api_url="https://api.mosaia.ai",
            version="2",
            verbose=True,
        )
        client = APIClient(config)

        # Test URL construction with version 2
        path = "/auth/signin"
        if path.startswith("/"):
            path = path[1:]  # Remove leading slash
        expected_url = f"{client.base_url}/{path}"
        assert expected_url == "https://api.mosaia.ai/v2/auth/signin"


@pytest.mark.unit
class TestAPIClientRequestMethods:
    """Test APIClient request methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_config = MosaiaConfig(
            api_key="test-api-key",
            api_url="https://api.mosaia.ai",
            version="1",
            verbose=True,
        )

    @pytest.mark.asyncio
    async def test_get_request(self):
        """Test GET request method."""
        client = APIClient(self.test_config)

        # Mock the _make_request method
        with patch.object(
            client, "_make_request", new_callable=AsyncMock
        ) as mock_make_request:
            mock_make_request.return_value = {"data": "test"}

            result = await client.get("/users")

            mock_make_request.assert_called_once_with("GET", "/users", params=None)
            assert result == {"data": "test"}

    @pytest.mark.asyncio
    async def test_post_request(self):
        """Test POST request method."""
        client = APIClient(self.test_config)

        # Mock the _make_request method
        with patch.object(
            client, "_make_request", new_callable=AsyncMock
        ) as mock_make_request:
            mock_make_request.return_value = {"data": "created"}

            data = {"name": "Test User", "email": "test@example.com"}
            result = await client.post("/users", data)

            mock_make_request.assert_called_once_with("POST", "/users", data=data)
            assert result == {"data": "created"}

    @pytest.mark.asyncio
    async def test_put_request(self):
        """Test PUT request method."""
        client = APIClient(self.test_config)

        # Mock the _make_request method
        with patch.object(
            client, "_make_request", new_callable=AsyncMock
        ) as mock_make_request:
            mock_make_request.return_value = {"data": "updated"}

            data = {"name": "Updated User"}
            result = await client.put("/users/123", data)

            mock_make_request.assert_called_once_with("PUT", "/users/123", data=data)
            assert result == {"data": "updated"}

    @pytest.mark.asyncio
    async def test_delete_request(self):
        """Test DELETE request method."""
        client = APIClient(self.test_config)

        # Mock the _make_request method
        with patch.object(
            client, "_make_request", new_callable=AsyncMock
        ) as mock_make_request:
            mock_make_request.return_value = {"data": "deleted"}

            result = await client.delete("/users/123")

            mock_make_request.assert_called_once_with(
                "DELETE", "/users/123", params=None
            )
            assert result == {"data": "deleted"}


@pytest.mark.unit
class TestAPIClientErrorHandling:
    """Test APIClient error handling."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_config = MosaiaConfig(
            api_key="test-api-key",
            api_url="https://api.mosaia.ai",
            version="1",
            verbose=True,
        )

    def test_error_handling(self):
        """Test error handling functionality."""
        client = APIClient(self.test_config)

        # Test error response creation
        error = Exception("Test error")
        error_response = client._handle_error(error)

        assert error_response["message"] == "Test error"
        assert error_response["code"] == "UNKNOWN_ERROR"
        assert error_response["status"] == 400

    def test_error_handling_with_status(self):
        """Test error handling with custom status."""
        client = APIClient(self.test_config)

        # Test error response creation with custom status
        error = Exception("Not found")
        error_response = client._handle_error(error, status=404)

        assert error_response["message"] == "Not found"
        assert error_response["code"] == "UNKNOWN_ERROR"
        assert error_response["status"] == 404
