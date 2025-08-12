"""
Tests for configuration management functionality.

This module tests the ConfigurationManager class and DEFAULT_CONFIG object,
ensuring proper singleton pattern, configuration initialization, and validation.
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from mosaia import DEFAULT_CONFIG, ConfigurationManager, MosaiaConfig, SessionInterface


class TestDEFAULT_CONFIG:
    """Test DEFAULT_CONFIG object."""

    def test_should_have_correct_api_configuration(self):
        """Test that DEFAULT_CONFIG has correct API configuration."""
        assert DEFAULT_CONFIG["API"] == {
            "BASE_URL": "https://api.mosaia.ai",
            "VERSION": "1",
            "CONTENT_TYPE": "application/json",
        }

    def test_should_have_correct_auth_configuration(self):
        """Test that DEFAULT_CONFIG has correct AUTH configuration."""
        assert DEFAULT_CONFIG["AUTH"] == {"TOKEN_PREFIX": "Bearer"}

    def test_should_have_correct_error_messages(self):
        """Test that DEFAULT_CONFIG has correct ERROR messages."""
        assert DEFAULT_CONFIG["ERRORS"] == {
            "UNKNOWN_ERROR": "An unknown error occurred",
            "DEFAULT_STATUS_CODE": 400,
        }


class TestConfigurationManager:
    """Test ConfigurationManager class."""

    def setup_method(self):
        """Reset the singleton instance before each test."""
        # Reset the singleton instance
        ConfigurationManager._instance = None
        ConfigurationManager._config = None

    def test_get_instance_should_return_same_instance_when_called_multiple_times(self):
        """Test that getInstance returns the same instance when called multiple times."""
        instance1 = ConfigurationManager.get_instance()
        instance2 = ConfigurationManager.get_instance()
        assert instance1 is instance2

    def test_initialize_should_initialize_with_default_values_when_no_config_provided(
        self,
    ):
        """Test initialization with default values when no config provided."""
        config_manager = ConfigurationManager.get_instance()
        config_manager.initialize({})
        config = config_manager.get_config()

        assert config.api_url == "https://api.mosaia.ai"
        assert config.version == "1"

    def test_initialize_should_initialize_with_custom_values(self):
        """Test initialization with custom values."""
        config_manager = ConfigurationManager.get_instance()
        custom_config = {
            "api_key": "test-api-key",
            "api_url": "https://custom-api.mosaia.ai",
            "version": "2",
            "client_id": "test-client-id",
            "client_secret": "test-client-secret",
            "verbose": True,
            "session": {
                "access_token": "test-access-token",
                "refresh_token": "test-refresh-token",
                "auth_type": "oauth",
                "sub": "test-sub",
                "iat": "1640995200",
                "exp": "1640998800",
            },
        }

        config_manager.initialize(custom_config)
        config = config_manager.get_config()

        assert config.api_key == "test-api-key"
        assert config.api_url == "https://custom-api.mosaia.ai"
        assert config.version == "2"
        assert config.client_id == "test-client-id"
        assert config.client_secret == "test-client-secret"
        assert config.verbose is True
        assert config.session is not None
        assert config.session.access_token == "test-access-token"

    def test_initialize_should_merge_custom_values_with_defaults(self):
        """Test that custom values are merged with defaults."""
        config_manager = ConfigurationManager.get_instance()
        custom_config = {"api_key": "test-api-key", "client_id": "test-client-id"}

        config_manager.initialize(custom_config)
        config = config_manager.get_config()

        assert config.api_key == "test-api-key"
        assert config.client_id == "test-client-id"
        assert config.api_url == "https://api.mosaia.ai"

    def test_get_config_should_throw_error_when_not_initialized(self):
        """Test that getConfig throws error when not initialized."""
        config_manager = ConfigurationManager.get_instance()

        with pytest.raises(RuntimeError, match="Configuration not initialized"):
            config_manager.get_config()

    def test_set_config_should_set_configuration_directly(self):
        """Test that setConfig sets configuration directly."""
        config_manager = ConfigurationManager.get_instance()
        new_config = MosaiaConfig(api_key="new-key")

        config_manager.set_config(new_config)
        config = config_manager.get_config()

        assert config.api_key == "new-key"

    def test_reset_should_clear_configuration(self):
        """Test that reset clears the configuration."""
        config_manager = ConfigurationManager.get_instance()
        config_manager.initialize({"api_key": "test-key"})

        config_manager.reset()

        with pytest.raises(RuntimeError, match="Configuration not initialized"):
            config_manager.get_config()

    def test_update_config_should_update_specific_values(self):
        """Test that updateConfig updates specific values."""
        config_manager = ConfigurationManager.get_instance()
        config_manager.initialize({"api_key": "original-key"})

        config_manager.update_config({"verbose": True})
        config = config_manager.get_config()

        assert config.api_key == "original-key"
        assert config.verbose is True

    def test_update_config_should_throw_error_when_not_initialized(self):
        """Test that updateConfig throws error when not initialized."""
        config_manager = ConfigurationManager.get_instance()

        with pytest.raises(RuntimeError, match="Configuration not initialized"):
            config_manager.update_config({"verbose": True})

    @patch.dict(
        os.environ,
        {
            "MOSAIA_API_KEY": "env-api-key",
            "MOSAIA_API_URL": "https://env-api.mosaia.ai",
            "MOSAIA_VERSION": "2",
            "MOSAIA_CLIENT_ID": "env-client-id",
            "MOSAIA_CLIENT_SECRET": "env-client-secret",
            "MOSAIA_VERBOSE": "true",
        },
    )
    def test_initialize_from_env_should_read_environment_variables(self):
        """Test that initializeFromEnv reads environment variables."""
        config_manager = ConfigurationManager.get_instance()
        config_manager.initialize_from_env()
        config = config_manager.get_config()

        assert config.api_key == "env-api-key"
        assert config.api_url == "https://env-api.mosaia.ai"
        assert config.version == "2"
        assert config.client_id == "env-client-id"
        assert config.client_secret == "env-client-secret"
        assert config.verbose is True

    def test_initialize_from_env_should_handle_missing_environment_variables(self):
        """Test that initializeFromEnv handles missing environment variables."""
        config_manager = ConfigurationManager.get_instance()

        # Clear environment variables
        with patch.dict(os.environ, {}, clear=True):
            config_manager.initialize_from_env()
            config = config_manager.get_config()

            # Should use defaults
            assert config.api_url == "https://api.mosaia.ai"
            assert config.version == "1"

    def test_initialize_should_handle_session_data(self):
        """Test that initialize handles session data correctly."""
        config_manager = ConfigurationManager.get_instance()
        session_data = {
            "access_token": "test-token",
            "refresh_token": "test-refresh",
            "auth_type": "oauth",
        }

        config_manager.initialize({"session": session_data})
        config = config_manager.get_config()

        assert config.session is not None
        assert config.session.access_token == "test-token"
        assert config.session.refresh_token == "test-refresh"
        assert config.session.auth_type == "oauth"

    def test_initialize_should_handle_none_session_data(self):
        """Test that initialize handles None session data."""
        config_manager = ConfigurationManager.get_instance()
        config_manager.initialize({"session": None})
        config = config_manager.get_config()

        assert config.session is None

    def test_initialize_should_handle_empty_session_data(self):
        """Test that initialize handles empty session data."""
        config_manager = ConfigurationManager.get_instance()
        config_manager.initialize({"session": {}})
        config = config_manager.get_config()

        assert config.session is not None
        assert config.session.access_token is None
