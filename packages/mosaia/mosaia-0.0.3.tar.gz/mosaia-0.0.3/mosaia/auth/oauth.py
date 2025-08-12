"""
OAuth client for handling OAuth2 Authorization Code flow with PKCE.

This module implements the OAuth2 Authorization Code flow with PKCE (Proof Key for Code Exchange)
for secure authentication. It provides a complete OAuth2 implementation including:
- Authorization URL generation with PKCE
- Token exchange with code verifier
- Token refresh
- State parameter support for CSRF protection
"""

import base64
import hashlib
import secrets
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode, urljoin

from ..config import DEFAULT_CONFIG, ConfigurationManager
from ..types import MosaiaConfig


class OAuth:
    """
    OAuth client for handling OAuth2 Authorization Code flow with PKCE.

    This class implements the OAuth2 Authorization Code flow with PKCE (Proof Key for Code Exchange)
    for secure authentication. It provides a complete OAuth2 implementation including:
    - Authorization URL generation with PKCE
    - Token exchange with code verifier
    - Token refresh
    - State parameter support for CSRF protection

    The implementation follows RFC 7636 for PKCE, ensuring secure authentication
    even for public clients.

    Examples:
        Basic OAuth flow:
        >>> # Initialize OAuth client
        >>> oauth = OAuth({
        ...     'client_id': 'your-client-id',
        ...     'redirect_uri': 'https://your-app.com/callback',
        ...     'app_url': 'https://mosaia.ai',
        ...     'scopes': ['read', 'write']
        ... })
        >>>
        >>> # Step 1: Get authorization URL and code verifier
        >>> auth_data = oauth.get_authorization_url_and_code_verifier()
        >>> url = auth_data['url']
        >>> code_verifier = auth_data['code_verifier']
        >>>
        >>> # Store code verifier securely (e.g., session storage)
        >>> session_storage.set_item('code_verifier', code_verifier)
        >>>
        >>> # Step 2: Redirect user to authorization URL
        >>> # window.location.href = url
        >>>
        >>> # Step 3: Handle OAuth callback
        >>> code = url_params.get('code')
        >>> stored_verifier = session_storage.get_item('code_verifier')
        >>>
        >>> if code and stored_verifier:
        ...     config = await oauth.authenticate_with_code_and_verifier(code, stored_verifier)
        ...     mosaia = MosaiaClient(config)

        With state parameter for CSRF protection:
        >>> import secrets
        >>> state = secrets.token_hex(32)
        >>> session_storage.set_item('oauth_state', state)
        >>>
        >>> oauth = OAuth({
        ...     'client_id': 'your-client-id',
        ...     'redirect_uri': 'https://your-app.com/callback',
        ...     'scopes': ['read', 'write'],
        ...     'state': state
        ... })
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Creates a new OAuth instance.

        Initializes an OAuth client with the provided configuration. If certain
        configuration values are missing, it attempts to use values from the
        ConfigurationManager.

        Args:
            config: OAuth configuration object
                - client_id: OAuth client ID for application identification
                - redirect_uri: URI where the OAuth provider will redirect after authorization
                - app_url: Base URL for authorization endpoints (e.g., https://mosaia.ai)
                - scopes: Array of permission scopes to request (e.g., ['read', 'write'])
                - state: Optional state parameter for CSRF protection
                - api_url: Optional API URL override (defaults to ConfigurationManager value)
                - api_version: Optional API version override (defaults to ConfigurationManager value)

        Raises:
            Error: When required configuration values (client_id, api_url, api_version) are missing

        Examples:
            # Basic initialization
            >>> oauth = OAuth({
            ...     'client_id': 'your-client-id',
            ...     'redirect_uri': 'https://your-app.com/callback',
            ...     'scopes': ['read', 'write']
            ... })

            # Full configuration
            >>> oauth = OAuth({
            ...     'client_id': 'your-client-id',
            ...     'redirect_uri': 'https://your-app.com/callback',
            ...     'app_url': 'https://mosaia.ai',
            ...     'scopes': ['read', 'write'],
            ...     'state': 'random-state-string',
            ...     'api_url': 'https://api.mosaia.ai',
            ...     'api_version': '1'
            ... })
        """
        config = config or {}
        config_manager = ConfigurationManager.get_instance()

        try:
            default_config = config_manager.get_config()
        except RuntimeError:
            # Configuration not initialized, use defaults
            default_config = None

        if not config.get("app_url"):
            config["app_url"] = DEFAULT_CONFIG.get("APP", {}).get(
                "URL", "https://mosaia.ai"
            )

        if default_config:
            if not config.get("client_id"):
                config["client_id"] = default_config.client_id
            if not config.get("api_url"):
                config["api_url"] = default_config.api_url
            if not config.get("api_version"):
                config["api_version"] = default_config.version

        if not config.get("client_id"):
            raise Exception("client_id is required in OAuth config")
        if not config.get("api_url"):
            raise Exception("api_url is required in OAuth config")
        if not config.get("api_version"):
            raise Exception("api_version is required in OAuth config")

        self.config = config

    def _generate_pkce(self) -> Dict[str, str]:
        """
        Generates a PKCE code verifier and code challenge.

        This method implements the PKCE (Proof Key for Code Exchange) protocol
        as specified in RFC 7636. It generates:
        1. A cryptographically secure random code verifier (128 characters)
        2. A code challenge using SHA256 and base64url encoding

        The code verifier must be stored securely (e.g., in session storage)
        and used later during the token exchange step.

        Returns:
            Object containing the PKCE values
                - code_verifier: 128-character random code verifier
                - code_challenge: Base64url-encoded SHA256 hash of verifier

        Examples:
            >>> pkce_data = oauth._generate_pkce()
            >>> print('Verifier length:', len(pkce_data['code_verifier']))  # 128
            >>> print('Challenge:', pkce_data['code_challenge'])  # Base64url-encoded string
        """
        # Generate code verifier using base64url encoding (RFC 7636 compliant)
        # Use 96 bytes to ensure we get 128 characters after base64url encoding
        code_verifier_bytes = secrets.token_bytes(96)
        code_verifier = (
            base64.urlsafe_b64encode(code_verifier_bytes).decode("utf-8").rstrip("=")
        )

        # Generate code challenge using SHA256 hash and base64url encoding
        code_challenge_bytes = hashlib.sha256(code_verifier.encode("utf-8")).digest()
        code_challenge = (
            base64.urlsafe_b64encode(code_challenge_bytes).decode("utf-8").rstrip("=")
        )

        return {"code_verifier": code_verifier, "code_challenge": code_challenge}

    def get_authorization_url_and_code_verifier(self) -> Dict[str, str]:
        """
        Generates the authorization URL and PKCE code verifier for the OAuth flow.

        This method prepares everything needed to start the OAuth authorization flow:
        1. Generates a PKCE code verifier and challenge
        2. Constructs the authorization URL with all required parameters
        3. Returns both the URL and verifier for the next steps

        The authorization URL includes:
        - client_id
        - redirect_uri
        - response_type=code
        - code_challenge (PKCE)
        - code_challenge_method=S256
        - scopes (if provided)
        - state (if provided)

        Returns:
            Authorization data for the OAuth flow
                - url: Complete authorization URL to redirect users to
                - code_verifier: PKCE code verifier (store securely)

        Raises:
            Error: When required configuration (scopes, redirect_uri) is missing

        Examples:
            Basic usage:
            >>> auth_data = oauth.get_authorization_url_and_code_verifier()
            >>> url = auth_data['url']
            >>> code_verifier = auth_data['code_verifier']
            >>>
            >>> # Store verifier securely
            >>> session_storage.set_item('code_verifier', code_verifier)
            >>>
            >>> # Redirect to authorization URL
            >>> # window.location.href = url

            With error handling:
            >>> try:
            ...     auth_data = oauth.get_authorization_url_and_code_verifier()
            ...
            ...     # Store both verifier and current URL for later
            ...     session_storage.set_item('code_verifier', auth_data['code_verifier'])
            ...     session_storage.set_item('return_to', window.location.href)
            ...
            ...     # Redirect to authorization
            ...     # window.location.href = auth_data['url']
            ... except Exception as error:
            ...     print(f'Failed to start OAuth flow: {error}')
        """
        if not self.config.get("scopes") or len(self.config["scopes"]) == 0:
            raise Exception(
                "scopes are required in OAuth config to generate authorization url and code verifier"
            )

        if not self.config.get("redirect_uri"):
            raise Exception(
                "redirect_uri is required in OAuth config to generate authorization url and code verifier"
            )

        pkce_data = self._generate_pkce()
        code_verifier = pkce_data["code_verifier"]
        code_challenge = pkce_data["code_challenge"]

        params = {
            "client_id": self.config["client_id"],
            "redirect_uri": self.config["redirect_uri"],
            "response_type": "code",
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }

        if self.config.get("scopes") and len(self.config["scopes"]) > 0:
            params["scope"] = ",".join(self.config["scopes"])

        if self.config.get("state"):
            params["state"] = self.config["state"]

        url = f"{self.config['app_url']}/oauth?{urlencode(params)}"

        return {"url": url, "code_verifier": code_verifier}

    async def authenticate_with_code_and_verifier(
        self, code: str, code_verifier: str
    ) -> MosaiaConfig:
        """
        Exchanges an authorization code for access and refresh tokens.

        This method completes the OAuth flow by exchanging the authorization code
        for access and refresh tokens. It includes the PKCE code verifier in the
        token request for additional security.

        The method:
        1. Validates required parameters
        2. Constructs the token request with PKCE verification
        3. Exchanges the code for tokens
        4. Returns a complete MosaiaConfig with the new tokens

        Args:
            code: Authorization code from the OAuth callback
            code_verifier: Original PKCE code verifier from get_authorization_url_and_code_verifier

        Returns:
            Complete MosaiaConfig

        Raises:
            Error: When required configuration (redirect_uri) is missing
            OAuthErrorResponse: When token exchange fails
            OAuthErrorResponse: When code is invalid or expired
            OAuthErrorResponse: When code verifier doesn't match challenge

        Examples:
            Basic OAuth callback handling:
            >>> # In your OAuth callback route/page
            >>> code = url_params.get('code')
            >>> verifier = session_storage.get_item('code_verifier')
            >>>
            >>> if code and verifier:
            ...     try:
            ...         config = await oauth.authenticate_with_code_and_verifier(code, verifier)
            ...
            ...         # Initialize SDK with the new config
            ...         mosaia = MosaiaClient(config)
            ...
            ...         # Clean up stored values
            ...         session_storage.remove_item('code_verifier')
            ...
            ...         # Return to original page
            ...         return_to = session_storage.get_item('return_to') or '/'
            ...         # window.location.href = return_to
            ...     except Exception as error:
            ...         print(f'Token exchange failed: {error}')
            ...         # Handle error (e.g., redirect to login)

            With state verification:
            >>> params = url_params
            >>> code = params.get('code')
            >>> state = params.get('state')
            >>> verifier = session_storage.get_item('code_verifier')
            >>> saved_state = session_storage.get_item('oauth_state')
            >>>
            >>> # Verify state to prevent CSRF
            >>> if state != saved_state:
            ...     raise Exception('OAuth state mismatch')
            >>>
            >>> if code and verifier:
            ...     config = await oauth.authenticate_with_code_and_verifier(code, verifier)
            ...     # Use the config...
        """
        if not self.config.get("redirect_uri"):
            raise Exception(
                "redirect_uri is required in OAuth config to authenticate with code and verifier"
            )

        params = {
            "client_id": self.config["client_id"],
            "redirect_uri": self.config["redirect_uri"],
            "code": code,
            "code_verifier": code_verifier,
            "grant_type": "authorization_code",
        }

        try:
            import aiohttp

            api_url = self.config["api_url"]
            api_version = self.config["api_version"]

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{api_url}/v{api_version}/auth/token",
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    data=urlencode(params),
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
                            **self.config,
                            "api_key": session_data["access_token"],
                            "session": session_data,
                        }
                    )
        except Exception as error:
            raise error
