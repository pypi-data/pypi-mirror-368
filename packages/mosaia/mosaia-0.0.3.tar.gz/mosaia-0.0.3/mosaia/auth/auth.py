"""
Authentication API client for the Mosaia SDK.

This module provides comprehensive authentication functionality for the Mosaia SDK,
supporting multiple authentication flows:
- Password-based authentication
- Client credentials authentication
- Token refresh operations
- OAuth token management
- Session handling
"""

import asyncio
from typing import Any, Dict, Optional, Union
from urllib.parse import urlencode

from ..config import ConfigurationManager
from ..types import MosaiaConfig, SessionInterface
from ..utils.api_client import APIClient


class MosaiaAuth:
    """
    Authentication API client for the Mosaia SDK.

    This class provides comprehensive authentication functionality for the Mosaia SDK,
    supporting multiple authentication flows:
    - Password-based authentication
    - Client credentials authentication
    - Token refresh operations
    - OAuth token management
    - Session handling

    The class integrates with ConfigurationManager for centralized configuration
    management and uses APIClient for making authenticated HTTP requests.

    Examples:
        Basic usage with password authentication:
        >>> auth = MosaiaAuth()
        >>> try:
        ...     config = await auth.sign_in_with_password('user@example.com', 'password')
        ...     mosaia = MosaiaClient(config)
        ... except Exception as error:
        ...     print(f'Authentication failed: {error}')

        Client credentials authentication:
        >>> auth = MosaiaAuth()
        >>> try:
        ...     config = await auth.sign_in_with_client('client-id', 'client-secret')
        ...     mosaia = MosaiaClient(config)
        ... except Exception as error:
        ...     print(f'Client auth failed: {error}')

        Token refresh and sign out:
        >>> # Refresh token when needed
        >>> new_config = await auth.refresh_token()
        >>> mosaia.config = new_config
        >>>
        >>> # Sign out when done
        >>> await auth.sign_out()
    """

    def __init__(self, config: Optional[MosaiaConfig] = None):
        """
        Creates a new Authentication API client instance.

        Initializes the authentication client with an optional configuration.
        If no configuration is provided, it uses the ConfigurationManager to
        get the current configuration.

        Args:
            config: Optional configuration object
                - api_key: API key for authentication
                - api_url: Base URL for API requests
                - client_id: OAuth client ID
                - session: Current session information

        Examples:
            # Create with default configuration
            >>> auth = MosaiaAuth()

            # Create with custom configuration
            >>> auth = MosaiaAuth({
            ...     'api_url': 'https://api.mosaia.ai',
            ...     'client_id': 'your-client-id'
            ... })

        Raises:
            Error: When required configuration values are missing
        """
        self.config = config
        if not self.config:
            self.config_manager = ConfigurationManager.get_instance()
            try:
                self.config = self.config_manager.get_config()
            except RuntimeError:
                # Configuration not initialized, create a default one
                self.config = MosaiaConfig()
        else:
            self.config_manager = None

        # Skip token refresh to prevent circular dependency
        self.api_client = APIClient(self.config, skip_token_refresh=True)

    async def sign_in_with_password(self, email: str, password: str) -> MosaiaConfig:
        """
        Sign in using email and password authentication.

        Authenticates a user with their email and password credentials.
        Returns a configured Mosaia client instance with the obtained access token.

        Args:
            email: The user's email address
            password: The user's password

        Returns:
            Configured Mosaia client instance

        Raises:
            Error: When authentication fails or network errors occur

        Examples:
            >>> auth = MosaiaAuth()
            >>> try:
            ...     mosaia_config = await auth.sign_in_with_password('user@example.com', 'password')
            ...     mosaia.config = mosaia_config
            ...     print('Successfully authenticated')
            ... except Exception as error:
            ...     print(f'Authentication failed: {error}')
        """
        if not self.config:
            raise Exception("No config found")

        client_id = self.config.client_id
        if not client_id:
            raise Exception("client_id is required and not found in config")

        request = {
            "grant_type": "password",
            "email": email,
            "password": password,
            "client_id": client_id,
        }

        try:
            response = await self.api_client.post("/auth/signin", request)

            if "error" in response:
                raise Exception(response["error"]["message"])

            data = response.get("data", {})
            session = {
                "access_token": data["access_token"],
                "refresh_token": data["refresh_token"],
                "sub": data["sub"],
                "iat": data["iat"],
                "exp": data["exp"],
                "auth_type": "password",
            }

            return MosaiaConfig(
                **{
                    **self.config.__dict__,
                    "api_key": session["access_token"],
                    "session": session,
                }
            )
        except Exception as error:
            if hasattr(error, "message"):
                raise Exception(str(error.message))
            raise Exception("Unknown error occurred")

    async def sign_in_with_client(
        self, client_id: str, client_secret: str
    ) -> MosaiaConfig:
        """
        Sign in using client credentials authentication.

        Authenticates an application using client ID and client secret.
        This flow is typically used for server-to-server authentication
        where no user interaction is required.

        Args:
            client_id: The OAuth client ID
            client_secret: The OAuth client secret

        Returns:
            Configured Mosaia client instance

        Raises:
            Error: When authentication fails or network errors occur

        Examples:
            >>> auth = MosaiaAuth()
            >>> try:
            ...     mosaia_config = await auth.sign_in_with_client('client-id', 'client-secret')
            ...     mosaia.config = mosaia_config
            ...     print('Successfully authenticated with client credentials')
            ... except Exception as error:
            ...     print(f'Client authentication failed: {error}')
        """
        request = {
            "grant_type": "client",
            "client_id": client_id,
            "client_secret": client_secret,
        }

        try:
            response = await self.api_client.post("/auth/signin", request)

            if "error" in response:
                raise Exception(response["error"]["message"])

            data = response.get("data", {})
            session = {
                "access_token": data["access_token"],
                "refresh_token": data["refresh_token"],
                "sub": data["sub"],
                "iat": data["iat"],
                "exp": data["exp"],
                "auth_type": "client",
            }

            return MosaiaConfig(
                **{
                    **self.config.__dict__,
                    "api_key": data["access_token"],
                    "session": session,
                }
            )
        except Exception as error:
            if hasattr(error, "message"):
                raise Exception(str(error.message))
            raise Exception("Unknown error occurred")

    async def refresh_token(self, token: Optional[str] = None) -> MosaiaConfig:
        """
        Refresh an access token using a refresh token.

        Obtains a new access token using an existing refresh token.
        This method can be used to extend a user's session without requiring
        them to re-enter their credentials.

        Args:
            token: Optional refresh token. If not provided, attempts to use
                   the refresh token from the current configuration

        Returns:
            Updated MosaiaConfig

        Raises:
            Error: When refresh token is missing or refresh fails

        Examples:
            >>> auth = MosaiaAuth()
            >>> try:
            ...     # Use refresh token from config
            ...     mosaia = await auth.refresh_token()
            ...
            ...     # Or provide a specific refresh token
            ...     mosaia_config = await auth.refresh_token('specific-refresh-token')
            ...     mosaia.config = mosaia_config
            ... except Exception as error:
            ...     print(f'Token refresh failed: {error}')
        """
        refresh_token = token or (
            self.config.session.refresh_token if self.config.session else None
        )

        if not refresh_token:
            raise Exception("Refresh token is required and not found in config")

        request = {"grant_type": "refresh", "refresh_token": refresh_token}

        try:
            response = await self.api_client.post("/auth/signin", request)

            if "error" in response:
                raise Exception(response["error"]["message"])

            data = response.get("data", {})
            session = {
                "access_token": data["access_token"],
                "refresh_token": data["refresh_token"],
                "sub": data["sub"],
                "iat": data["iat"],
                "exp": data["exp"],
                "auth_type": "refresh",
            }

            return MosaiaConfig(
                **{
                    **self.config.__dict__,
                    "api_key": session["access_token"],
                    "session": session,
                }
            )
        except Exception as error:
            if hasattr(error, "message"):
                raise Exception(str(error.message))
            raise Exception("Unknown error occurred")

    async def refresh_oauth_token(self, refresh_token: str) -> MosaiaConfig:
        """
        Refreshes an OAuth access token using a refresh token.

        This method exchanges a refresh token for a new access token when the current
        access token expires. This allows for long-term authentication without requiring
        user re-authentication.

        Args:
            refresh_token: The refresh token received from the initial token exchange

        Returns:
            New OAuth token response

        Raises:
            OAuthErrorResponse: When the refresh fails (invalid refresh token, expired, etc.)

        Examples:
            # When access token expires, use refresh token to get new tokens
            >>> try:
            ...     mosaia_config = await oauth.refresh_oauth_token(refresh_token)
            ...     mosaia.config = mosaia_config
            ...     print('New access token:', mosaia_config.api_key)
            ...     print('New refresh token:', mosaia_config.refresh_token)
            ... except Exception as error:
            ...     # Refresh token expired, user needs to re-authenticate
            ...     print(f'Token refresh failed: {error}')
        """
        params = urlencode(
            {"refresh_token": refresh_token, "grant_type": "refresh_token"}
        )

        try:
            import aiohttp

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.config.api_url}/auth/token",
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    data=params,
                ) as response:
                    data = await response.json()

                    if not response.ok:
                        raise Exception(data)

                    session_data = {
                        "access_token": data["access_token"],
                        "refresh_token": data["refresh_token"],
                        "sub": data["sub"],
                        "iat": data["iat"],
                        "exp": data["exp"],
                        "auth_type": "oauth",
                    }

                    return MosaiaConfig(
                        **{
                            **self.config.__dict__,
                            "api_key": session_data["access_token"],
                            "session": session_data,
                        }
                    )
        except Exception as error:
            raise error

    async def sign_out(self, api_key: Optional[str] = None) -> None:
        """
        Sign out and invalidate the current session.

        Invalidates the current access token and clears the configuration.
        This method should be called when a user logs out or when you want
        to ensure the current session is terminated.

        Args:
            api_key: Optional API key to sign out. If not provided, uses
                     the API key from the current configuration

        Raises:
            Error: When API key is missing or sign out fails

        Examples:
            >>> auth = MosaiaAuth()
            >>> try:
            ...     # Sign out using API key from config
            ...     await auth.sign_out()
            ...
            ...     # Or provide a specific API key
            ...     await auth.sign_out('specific-api-key')
            ...     print('Successfully signed out')
            ... except Exception as error:
            ...     print(f'Sign out failed: {error}')
        """
        token = api_key or self.config.api_key

        if not token:
            raise Exception("api_key is required and not found in config")

        try:
            await self.api_client.delete("/auth/signout", {"token": token})

            if self.config_manager:
                self.config_manager.reset()
        except Exception as error:
            if hasattr(error, "message"):
                raise Exception(str(error.message))
            raise Exception("Unknown error occurred")

    async def refresh(self) -> MosaiaConfig:
        """
        Refresh the current session using the appropriate method.

        This method automatically determines the authentication type and
        uses the appropriate refresh method (OAuth or standard).

        Returns:
            Updated MosaiaConfig

        Raises:
            Error: When no valid config or session is found
        """
        if not self.config:
            raise Exception("No valid config found")

        session = self.config.session
        if not session:
            raise Exception("No session found in config")

        if not session.refresh_token:
            raise Exception("No refresh token found in config")

        if session.auth_type == "oauth":
            return await self.refresh_oauth_token(session.refresh_token)

        return await self.refresh_token(session.refresh_token)
