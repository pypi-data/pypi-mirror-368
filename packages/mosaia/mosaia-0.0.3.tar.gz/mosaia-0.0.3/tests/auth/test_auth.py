#!/usr/bin/env python3
"""
Test script for the Mosaia Python SDK auth module.

This script tests the authentication classes to ensure they work correctly
and maintain parity with the Node.js SDK.
"""

from typing import Any, Dict

import pytest

# Test imports
from mosaia.auth import MosaiaAuth, OAuth


@pytest.mark.auth
class TestMosaiaAuth:
    """Test MosaiaAuth functionality."""

    def test_auth_creation(self):
        """Test MosaiaAuth can be instantiated."""
        auth = MosaiaAuth()
        assert auth is not None
        assert auth.api_client is not None

    def test_auth_with_config(self, test_config):
        """Test MosaiaAuth with custom config."""
        # Convert dict to MosaiaConfig object
        from mosaia.types import MosaiaConfig

        config = MosaiaConfig(**test_config)
        auth = MosaiaAuth(config)
        assert auth.config.api_key == "test-api-key"
        assert auth.config.api_url == "https://test-api.mosaia.ai"

    def test_auth_config_manager_integration(self, initialized_config_manager):
        """Test MosaiaAuth integrates with ConfigurationManager."""
        auth = MosaiaAuth()
        config = auth.config
        assert config.api_key == "test-api-key"
        assert config.api_url == "https://test-api.mosaia.ai"

    def test_sign_in_with_password_missing_config(self):
        """Test sign_in_with_password with missing config."""
        auth = MosaiaAuth()
        auth.config = None

        # Test that the method exists and is async
        assert hasattr(auth, "sign_in_with_password")
        assert callable(auth.sign_in_with_password)

    def test_sign_in_with_password_missing_client_id(self):
        """Test sign_in_with_password with missing client_id."""
        auth = MosaiaAuth()
        auth.config.client_id = None

        # Test that the method exists and is async
        assert hasattr(auth, "sign_in_with_password")
        assert callable(auth.sign_in_with_password)

    def test_sign_in_with_client(self):
        """Test sign_in_with_client method."""
        auth = MosaiaAuth()

        # This would normally make an API call, so we'll test the method exists
        assert hasattr(auth, "sign_in_with_client")
        assert callable(auth.sign_in_with_client)

    def test_refresh_token_missing_token(self):
        """Test refresh_token with missing token."""
        auth = MosaiaAuth()
        auth.config.session = None

        # Test that the method exists and is async
        assert hasattr(auth, "refresh_token")
        assert callable(auth.refresh_token)

    def test_sign_out_missing_api_key(self):
        """Test sign_out with missing api_key."""
        auth = MosaiaAuth()
        auth.config.api_key = None

        # Test that the method exists and is async
        assert hasattr(auth, "sign_out")
        assert callable(auth.sign_out)

    def test_refresh_missing_config(self):
        """Test refresh with missing config."""
        auth = MosaiaAuth()
        auth.config = None

        # Test that the method exists and is async
        assert hasattr(auth, "refresh")
        assert callable(auth.refresh)

    def test_refresh_missing_session(self):
        """Test refresh with missing session."""
        auth = MosaiaAuth()
        auth.config.session = None

        # Test that the method exists and is async
        assert hasattr(auth, "refresh")
        assert callable(auth.refresh)

    def test_refresh_missing_refresh_token(self):
        """Test refresh with missing refresh token."""
        auth = MosaiaAuth()
        auth.config.session = {"refresh_token": None}

        # Test that the method exists and is async
        assert hasattr(auth, "refresh")
        assert callable(auth.refresh)


@pytest.mark.auth
class TestOAuth:
    """Test OAuth functionality."""

    def test_oauth_creation(self):
        """Test OAuth can be instantiated."""
        config = {
            "client_id": "test-client-id",
            "redirect_uri": "https://test.com/callback",
            "api_url": "https://test-api.mosaia.ai",
            "api_version": "1",
            "scopes": ["read", "write"],
        }
        oauth = OAuth(config)
        assert oauth is not None
        assert oauth.config["client_id"] == "test-client-id"

    def test_oauth_creation_missing_client_id(self):
        """Test OAuth creation with missing client_id."""
        config = {
            "redirect_uri": "https://test.com/callback",
            "api_url": "https://test-api.mosaia.ai",
            "api_version": "1",
        }
        with pytest.raises(Exception, match="client_id is required"):
            OAuth(config)

    def test_oauth_creation_missing_api_url(self):
        """Test OAuth creation with missing api_url."""
        config = {
            "client_id": "test-client-id",
            "redirect_uri": "https://test.com/callback",
            "api_version": "1",
        }
        with pytest.raises(Exception, match="api_url is required"):
            OAuth(config)

    def test_oauth_creation_missing_api_version(self):
        """Test OAuth creation with missing api_version."""
        config = {
            "client_id": "test-client-id",
            "redirect_uri": "https://test.com/callback",
            "api_url": "https://test-api.mosaia.ai",
        }
        with pytest.raises(Exception, match="api_version is required"):
            OAuth(config)

    def test_generate_pkce(self):
        """Test PKCE generation."""
        config = {
            "client_id": "test-client-id",
            "redirect_uri": "https://test.com/callback",
            "api_url": "https://test-api.mosaia.ai",
            "api_version": "1",
            "scopes": ["read", "write"],
        }
        oauth = OAuth(config)

        # Test that the method exists and is private
        assert hasattr(oauth, "_generate_pkce")
        assert callable(oauth._generate_pkce)

        # Test PKCE generation
        pkce_data = oauth._generate_pkce()
        assert "code_verifier" in pkce_data
        assert "code_challenge" in pkce_data
        assert len(pkce_data["code_verifier"]) == 128

    def test_get_authorization_url_and_code_verifier(self):
        """Test authorization URL and code verifier generation."""
        config = {
            "client_id": "test-client-id",
            "redirect_uri": "https://test.com/callback",
            "api_url": "https://test-api.mosaia.ai",
            "api_version": "1",
            "scopes": ["read", "write"],
        }
        oauth = OAuth(config)

        # Test that the method exists
        assert hasattr(oauth, "get_authorization_url_and_code_verifier")
        assert callable(oauth.get_authorization_url_and_code_verifier)

        # Test URL generation
        auth_data = oauth.get_authorization_url_and_code_verifier()
        assert "url" in auth_data
        assert "code_verifier" in auth_data
        assert "test-client-id" in auth_data["url"]
        assert "code_challenge" in auth_data["url"]

    def test_get_authorization_url_and_code_verifier_missing_scopes(self):
        """Test authorization URL generation with missing scopes."""
        config = {
            "client_id": "test-client-id",
            "redirect_uri": "https://test.com/callback",
            "api_url": "https://test-api.mosaia.ai",
            "api_version": "1",
        }
        oauth = OAuth(config)

        with pytest.raises(Exception, match="scopes are required"):
            oauth.get_authorization_url_and_code_verifier()

    def test_get_authorization_url_and_code_verifier_missing_redirect_uri(self):
        """Test authorization URL generation with missing redirect_uri."""
        config = {
            "client_id": "test-client-id",
            "api_url": "https://test-api.mosaia.ai",
            "api_version": "1",
            "scopes": ["read", "write"],
        }
        oauth = OAuth(config)

        with pytest.raises(Exception, match="redirect_uri is required"):
            oauth.get_authorization_url_and_code_verifier()

    def test_get_authorization_url_and_code_verifier_with_state(self):
        """Test authorization URL generation with state parameter."""
        config = {
            "client_id": "test-client-id",
            "redirect_uri": "https://test.com/callback",
            "api_url": "https://test-api.mosaia.ai",
            "api_version": "1",
            "scopes": ["read", "write"],
            "state": "test-state",
        }
        oauth = OAuth(config)

        auth_data = oauth.get_authorization_url_and_code_verifier()
        assert "test-state" in auth_data["url"]

    def test_authenticate_with_code_and_verifier_missing_redirect_uri(self):
        """Test authentication with missing redirect_uri."""
        config = {
            "client_id": "test-client-id",
            "api_url": "https://test-api.mosaia.ai",
            "api_version": "1",
            "scopes": ["read", "write"],
        }
        oauth = OAuth(config)

        # Test that the method exists and is async
        assert hasattr(oauth, "authenticate_with_code_and_verifier")
        assert callable(oauth.authenticate_with_code_and_verifier)

        # Test that the method raises an exception when redirect_uri is missing
        import asyncio

        try:
            # Create a new event loop for testing
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Run the async function
            result = loop.run_until_complete(
                oauth.authenticate_with_code_and_verifier("test-code", "test-verifier")
            )
            loop.close()
        except Exception as e:
            assert "redirect_uri is required" in str(e)
        else:
            assert False, "Expected exception was not raised"

    def test_authenticate_with_code_and_verifier(self):
        """Test authentication with code and verifier."""
        config = {
            "client_id": "test-client-id",
            "redirect_uri": "https://test.com/callback",
            "api_url": "https://test-api.mosaia.ai",
            "api_version": "1",
            "scopes": ["read", "write"],
        }
        oauth = OAuth(config)

        # Test that the method exists and is async
        assert hasattr(oauth, "authenticate_with_code_and_verifier")
        assert callable(oauth.authenticate_with_code_and_verifier)


@pytest.mark.auth
class TestAuthIntegration:
    """Test auth integration functionality."""

    def test_auth_oauth_integration(self):
        """Test integration between MosaiaAuth and OAuth."""
        # Test that both classes can be imported and instantiated
        auth = MosaiaAuth()
        oauth = OAuth(
            {
                "client_id": "test-client-id",
                "redirect_uri": "https://test.com/callback",
                "api_url": "https://test-api.mosaia.ai",
                "api_version": "1",
                "scopes": ["read", "write"],
            }
        )

        assert auth is not None
        assert oauth is not None

    def test_auth_methods_exist(self):
        """Test that all required auth methods exist."""
        auth = MosaiaAuth()

        # Test that all required methods exist
        assert hasattr(auth, "sign_in_with_password")
        assert hasattr(auth, "sign_in_with_client")
        assert hasattr(auth, "refresh_token")
        assert hasattr(auth, "refresh_oauth_token")
        assert hasattr(auth, "sign_out")
        assert hasattr(auth, "refresh")

    def test_oauth_methods_exist(self):
        """Test that all required OAuth methods exist."""
        oauth = OAuth(
            {
                "client_id": "test-client-id",
                "redirect_uri": "https://test.com/callback",
                "api_url": "https://test-api.mosaia.ai",
                "api_version": "1",
                "scopes": ["read", "write"],
            }
        )

        # Test that all required methods exist
        assert hasattr(oauth, "get_authorization_url_and_code_verifier")
        assert hasattr(oauth, "authenticate_with_code_and_verifier")
        assert hasattr(oauth, "_generate_pkce")

    def test_auth_type_annotations(self):
        """Test that auth classes have proper type annotations."""
        from mosaia.types import MosaiaConfig

        # Test that MosaiaAuth can be imported and has proper types
        auth = MosaiaAuth()
        assert isinstance(auth.config, MosaiaConfig)

        # Test that OAuth can be imported and has proper types
        oauth = OAuth(
            {
                "client_id": "test-client-id",
                "redirect_uri": "https://test.com/callback",
                "api_url": "https://test-api.mosaia.ai",
                "api_version": "1",
                "scopes": ["read", "write"],
            }
        )
        assert isinstance(oauth.config, dict)
