"""
Internal API client for making HTTP requests to the Mosaia API.

This module provides a centralized HTTP client for all API communication
with the Mosaia platform. It handles authentication, request formatting,
response processing, and error handling in a consistent manner.

Features:
- Automatic authentication header management
- Token refresh handling
- Request/response standardization
- Error handling and formatting
- Query parameter building
- Content type management
- Async/await support
"""

import json
import logging
import mimetypes
from dataclasses import dataclass
from typing import Any, Dict, Generic, Optional, TypeVar, Union
from urllib.parse import urlencode, urljoin

import aiohttp

# Try to import from parent modules, with fallbacks
try:
    from ..config import DEFAULT_CONFIG, ConfigurationManager
    from ..types import APIResponse, ErrorResponse, MosaiaConfig
except ImportError:
    # Fallback for when parent modules don't exist yet
    DEFAULT_CONFIG = {
        "API": {
            "BASE_URL": "https://api.mosaia.ai",
            "VERSION": "1",
            "CONTENT_TYPE": "application/json",
        },
        "AUTH": {"TOKEN_PREFIX": "Bearer"},
        "ERRORS": {
            "UNKNOWN_ERROR": "An unknown error occurred",
            "DEFAULT_STATUS_CODE": 400,
        },
    }

    # Define basic types if they don't exist
    from typing import TypedDict

    class MosaiaConfig:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    class APIResponse:
        pass

    class ErrorResponse(TypedDict):
        message: str
        code: str
        status: int

    class ConfigurationManager:
        @classmethod
        def get_instance(cls):
            return cls()

        def get_config(self):
            return MosaiaConfig()

        def set_config(self, config):
            pass


from .helpers import is_timestamp_expired, query_generator

# Type variable for generic responses
T = TypeVar("T")

logger = logging.getLogger(__name__)


@dataclass
class RequestOptions:
    """Options for HTTP requests."""

    method: str = "GET"
    headers: Optional[Dict[str, str]] = None
    params: Optional[Dict[str, Any]] = None
    data: Optional[Dict[str, Any]] = None
    timeout: int = 30


class APIClient:
    """
    Internal API client for making HTTP requests to the Mosaia API.

    This class provides a centralized HTTP client for all API communication
    with the Mosaia platform. It handles authentication, request formatting,
    response processing, and error handling in a consistent manner.

    Features:
    - Automatic authentication header management
    - Token refresh handling
    - Request/response standardization
    - Error handling and formatting
    - Query parameter building
    - Content type management
    - Async/await support

    Examples:
        Basic usage:
        >>> client = APIClient()

        # GET request
        >>> users = await client.get('/user')

        # POST request
        >>> new_user = await client.post('/user', {
        ...     'name': 'John Doe',
        ...     'email': 'john@example.com'
        ... })

        # PUT request
        >>> updated_user = await client.put('/user/123', {
        ...     'name': 'John Smith'
        ... })

        # DELETE request
        >>> await client.delete('/user/123')

        With query parameters:
        >>> filtered_users = await client.get('/user', {
        ...     'limit': 10,
        ...     'offset': 0,
        ...     'search': 'john',
        ...     'active': True
        ... })
    """

    def __init__(
        self, config: Optional[MosaiaConfig] = None, skip_token_refresh: bool = False
    ):
        """
        Creates a new API client instance.

        Initializes the API client with configuration from the ConfigurationManager.
        The client automatically handles authentication and token refresh.

        Args:
            config: Optional configuration object (if not provided, uses ConfigurationManager)
            skip_token_refresh: Skip token refresh check to prevent circular dependencies

        Examples:
            Basic initialization:
            >>> client = APIClient()

            With custom config:
            >>> client = APIClient({
            ...     'api_key': 'your-api-key',
            ...     'api_url': 'https://api.mosaia.ai',
            ...     'version': '1'
            ... })

            Skip token refresh (for auth flows):
            >>> client = APIClient(config, skip_token_refresh=True)
        """
        self.config = config
        self.config_manager = ConfigurationManager.get_instance()
        self.skip_token_refresh = skip_token_refresh
        self.base_url = ""
        self.headers: Dict[str, str] = {}
        # Note: We intentionally avoid holding a long-lived aiohttp.ClientSession
        # to ensure the SDK does not require callers to manage lifecycle.
        # Each request is performed with an ephemeral session that is closed
        # automatically, preventing resource leaks and unclosed-session warnings.
        self._session: Optional[aiohttp.ClientSession] = None

        # Initialize the client
        self._initialize_client()

    def _initialize_client(self) -> None:
        """
        Initialize the client with current configuration.

        Sets up the base URL, headers, and authentication for the API client.
        Handles token refresh if the current token is expired.
        """
        try:
            config = self.config

            if not self.config:
                try:
                    config = self.config_manager.get_config()
                except:
                    # If config manager fails, use defaults
                    config = MosaiaConfig()

            # Parse and validate expiration timestamp if it exists
            # Skip token refresh check when called from MosaiaAuth to prevent circular dependency
            if (
                not self.skip_token_refresh
                and config
                and hasattr(config, "session")
                and config.session
                and hasattr(config.session, "exp")
                and config.session.exp
                and is_timestamp_expired(config.session.exp)
            ):

                # Import here to avoid circular dependency
                try:
                    from ..auth.auth import MosaiaAuth

                    auth = MosaiaAuth()
                    refreshed_config = auth.refresh_token()
                    self.config_manager.set_config(refreshed_config)
                    config = refreshed_config
                except ImportError:
                    # If auth module doesn't exist, continue without refresh
                    pass

            if not config:
                raise RuntimeError("No valid config found")

            # Ensure the resolved configuration is stored on the client instance
            # so that features gated by configuration flags (e.g., verbose logging)
            # work correctly even when APIClient is instantiated without an explicit config.
            self.config = config

            api_url = (
                getattr(config, "api_url", None) or DEFAULT_CONFIG["API"]["BASE_URL"]
            )
            version = (
                getattr(config, "version", None) or DEFAULT_CONFIG["API"]["VERSION"]
            )
            api_key = getattr(config, "api_key", None) or ""

            self.base_url = f"{api_url}/v{version}"
            self.headers = {
                "Authorization": f"{DEFAULT_CONFIG['AUTH']['TOKEN_PREFIX']} {api_key}",
                "Content-Type": DEFAULT_CONFIG["API"]["CONTENT_TYPE"],
            }

        except Exception as error:
            logger.error(f"Failed to initialize API client: {error}")
            raise

    async def _update_client_config(self) -> None:
        """
        Update the client configuration.

        Reinitializes the client with updated configuration settings.
        This is useful when configuration changes at runtime, such as
        when tokens are refreshed or API settings are updated.
        """
        try:
            self._initialize_client()
        except Exception as error:
            logger.error(f"Failed to update client config: {error}")
            raise

    async def __aenter__(self):
        """Support async context management for convenience and safety."""
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    def _handle_error(
        self, error: Exception, status: Optional[int] = None
    ) -> ErrorResponse:
        """
        Handles HTTP errors and converts them to standardized error responses.

        This method processes various types of errors and converts them to a
        consistent format for error handling throughout the SDK.

        Args:
            error: Error object from HTTP request
            status: HTTP status code (optional)

        Returns:
            Standardized error response
        """
        error_response: ErrorResponse = {
            "message": str(error) or DEFAULT_CONFIG["ERRORS"]["UNKNOWN_ERROR"],
            "code": "UNKNOWN_ERROR",
            "status": status or DEFAULT_CONFIG["ERRORS"]["DEFAULT_STATUS_CODE"],
        }
        return error_response

    def _build_query_string(self, params: Optional[Dict[str, Any]] = None) -> str:
        """
        Builds query string from parameters object.

        Args:
            params: Query parameters object

        Returns:
            URLSearchParams string
        """
        if not params:
            return ""

        # Filter out None and empty values
        filtered_params = {k: v for k, v in params.items() if v is not None and v != ""}

        if not filtered_params:
            return ""

        return "?" + urlencode(filtered_params, doseq=True)

    async def _make_request(
        self,
        method: str,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Makes an HTTP request using aiohttp.

        Args:
            method: HTTP method
            path: API endpoint path
            data: Request body data
            params: Query parameters

        Returns:
            API response data
        """
        # Update client config in case it changed
        await self._update_client_config()

        # Construct the full URL with version
        if path.startswith("/"):
            path = path[1:]  # Remove leading slash
        url = f"{self.base_url}/{path}"

        if params:
            query_string = self._build_query_string(params)
            if query_string:
                url += query_string

        request_options = {
            "url": url,
            "method": method.upper(),
            "headers": self.headers,
            "timeout": aiohttp.ClientTimeout(total=30),
        }

        if data and method.upper() != "GET":
            request_options["json"] = data

        # Log request if verbose mode is enabled
        if self.config and getattr(self.config, "verbose", False):
            logger.info(f"🚀 HTTP Request: {method.upper()} {url}")
            logger.info(f"🔑 Headers: {self.headers}")

            if params:
                logger.info(f"📋 Query Params: {params}")
            if data:
                logger.info(f"📦 Request Body: {data}")

        # Use an ephemeral session per request to avoid lifecycle management
        # requirements for SDK consumers and prevent resource leaks.
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(**request_options) as response:
                    # Log response if verbose mode is enabled
                    if self.config and getattr(self.config, "verbose", False):
                        logger.info(
                            f"✅ HTTP Response: {response.status} {method.upper()} {path}"
                        )

                    # Handle 204 No Content responses
                    if response.status == 204:
                        if self.config and getattr(self.config, "verbose", False):
                            logger.info("📄 Response Data: No Content (204)")
                        return None

                    # Check if response is ok (status in 200-299 range)
                    if not response.ok:
                        try:
                            error_data = await response.json()
                        except:
                            error_data = {"message": response.reason}

                        if self.config and getattr(self.config, "verbose", False):
                            logger.error(
                                f"❌ HTTP Error: {response.status} {method.upper()} {path}"
                            )
                            logger.error(f"🚨 Error Details: {error_data}")

                        raise Exception(error_data.get("message", response.reason))

                    # Parse response data
                    content_type = response.headers.get("content-type", "")
                    if "application/json" in content_type:
                        response_data = await response.json()
                    else:
                        response_data = await response.text()

                    if self.config and getattr(self.config, "verbose", False):
                        logger.info(f"📄 Response Data: {response_data}")

                    # If response has an error parameter, raise an exception
                    if isinstance(response_data, dict) and response_data.get("error"):
                        raise Exception(response_data["error"])

                    # Remove error and meta parameters from response
                    if isinstance(response_data, dict):
                        response_data.pop("error", None)
                        response_data.pop("meta", None)

                    return response_data

        except Exception as error:
            if self.config and getattr(self.config, "verbose", False):
                logger.error(
                    f"❌ Request Error: {method.upper()} {path}", exc_info=True
                )
            raise error

    async def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Makes a GET request to the API.

        Retrieves data from the specified API endpoint. Supports query parameters
        for filtering, pagination, and other request options.

        Args:
            path: API endpoint path (e.g., '/user', '/org', '/agent')
            params: Optional query parameters for filtering and pagination

        Returns:
            API response data

        Examples:
            Basic GET request:
            >>> users = await client.get('/user')
            >>> user = await client.get('/user/123')

            With query parameters:
            >>> filtered_users = await client.get('/user', {
            ...     'limit': 10,
            ...     'offset': 0,
            ...     'search': 'john',
            ...     'active': True
            ... })
        """
        return await self._make_request("GET", path, params=params)

    async def post(self, path: str, data: Optional[Dict[str, Any]] = None) -> Any:
        """
        Makes a POST request to the API.

        Creates new resources or performs actions that require data submission.
        The request body is automatically serialized as JSON.

        Args:
            path: API endpoint path (e.g., '/user', '/org', '/agent')
            data: Request body data to be sent

        Returns:
            API response data

        Examples:
            Create a new user:
            >>> new_user = await client.post('/user', {
            ...     'email': 'user@example.com',
            ...     'first_name': 'John',
            ...     'last_name': 'Doe'
            ... })
        """
        return await self._make_request("POST", path, data=data)

    async def put(self, path: str, data: Optional[Dict[str, Any]] = None) -> Any:
        """
        Makes a PUT request to the API.

        Updates existing resources with new data. The request body is automatically
        serialized as JSON and sent to the specified endpoint.

        Args:
            path: API endpoint path (e.g., '/user/123', '/org/456', '/agent/789')
            data: Request body data for updates

        Returns:
            API response data

        Examples:
            Update user profile:
            >>> updated_user = await client.put('/user/123', {
            ...     'first_name': 'Jane',
            ...     'last_name': 'Smith',
            ...     'email': 'jane.smith@example.com'
            ... })
        """
        return await self._make_request("PUT", path, data=data)

    async def delete(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Makes a DELETE request to the API.

        Removes resources from the system. Supports optional query parameters
        for additional deletion options like force deletion or soft deletion.

        Args:
            path: API endpoint path (e.g., '/user/123', '/org/456', '/agent/789')
            params: Optional query parameters for deletion options

        Returns:
            API response data

        Examples:
            Basic deletion:
            >>> await client.delete('/user/123')
            >>> await client.delete('/agent/789')

            Force deletion:
            >>> await client.delete('/org/456', {'force': True})
            >>> await client.delete('/user/123', {
            ...     'force': True,
            ...     'reason': 'account_deletion'
            ... })
        """
        return await self._make_request("DELETE", path, params=params)

    async def post_multipart(
        self,
        path: str,
        file: Any,
        field_name: str = "file",
        extra_fields: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Makes a POST multipart/form-data request to upload files.

        Args:
            path: API endpoint path (e.g., '/user/profile/image/upload')
            file: File path (str), bytes, or a file-like object to upload
            field_name: Form field name for the file (defaults to 'file')
            extra_fields: Optional additional form fields to include
            params: Optional query parameters

        Returns:
            API response data
        """
        await self._update_client_config()

        # Construct URL
        if path.startswith("/"):
            path = path[1:]
        url = f"{self.base_url}/{path}"
        if params:
            query_string = self._build_query_string(params)
            if query_string:
                url += query_string

        # Prepare multipart form data
        form = aiohttp.FormData()

        filename: Optional[str] = None
        content_type: Optional[str] = None
        file_obj: Optional[Any] = None
        file_bytes: Optional[bytes] = None

        try:
            # Determine file input type
            if isinstance(file, (bytes, bytearray)):
                file_bytes = bytes(file)
                filename = "upload"
            elif isinstance(file, str):
                # Treat as filesystem path
                filename = file.split("/")[-1] or "upload"
                content_type = (
                    mimetypes.guess_type(filename)[0] or "application/octet-stream"
                )
                file_obj = open(file, "rb")
            elif hasattr(file, "read"):
                # File-like object
                filename = getattr(file, "name", None)
                if filename:
                    filename = str(filename).split("/")[-1]
                else:
                    filename = "upload"
                # Best-effort content type guess
                content_type = (
                    mimetypes.guess_type(filename)[0] or "application/octet-stream"
                )
                # Read into memory to avoid relying on external lifecycle management
                file_bytes = file.read()
            else:
                raise ValueError("Unsupported file type for upload")

            if file_bytes is not None:
                form.add_field(
                    field_name,
                    file_bytes,
                    filename=filename,
                    content_type=content_type
                    or mimetypes.guess_type(filename)[0]
                    or "application/octet-stream",
                )
            else:
                # file_obj is opened above for path case
                form.add_field(
                    field_name,
                    file_obj,
                    filename=filename,
                    content_type=content_type or "application/octet-stream",
                )

            # Add any extra fields
            if extra_fields:
                for k, v in extra_fields.items():
                    # Coerce to string for form fields
                    form.add_field(k, "" if v is None else str(v))

            # Build request options; let aiohttp set Content-Type with boundary
            headers = self.headers.copy()
            headers.pop("Content-Type", None)

            if self.config and getattr(self.config, "verbose", False):
                logger.info(f"🚀 HTTP Request: POST {url} (multipart)")
                logger.info(f"🔑 Headers: {headers}")

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    data=form,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    if self.config and getattr(self.config, "verbose", False):
                        logger.info(f"✅ HTTP Response: {response.status} POST {path}")

                    if response.status == 204:
                        return None

                    if not response.ok:
                        try:
                            error_data = await response.json()
                        except:
                            error_data = {"message": response.reason}
                        if self.config and getattr(self.config, "verbose", False):
                            logger.error(
                                f"❌ HTTP Error: {response.status} POST {path}"
                            )
                            logger.error(f"🚨 Error Details: {error_data}")
                        raise Exception(error_data.get("message", response.reason))

                    content_type_header = response.headers.get("content-type", "")
                    if "application/json" in content_type_header:
                        response_data = await response.json()
                    else:
                        response_data = await response.text()

                    if isinstance(response_data, dict):
                        response_data.pop("error", None)
                        response_data.pop("meta", None)

                    return response_data
        finally:
            # Ensure we close file handles we opened
            if file_obj is not None and not file_obj.closed:
                try:
                    file_obj.close()
                except Exception:
                    pass

    async def close(self) -> None:
        """Close any retained session (no-op for ephemeral usage)."""
        if self._session and not self._session.closed:
            await self._session.close()
        self._session = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        # Note: This is a sync context manager, but the client is async
        # In practice, you should use async context manager or manually close
        pass

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
