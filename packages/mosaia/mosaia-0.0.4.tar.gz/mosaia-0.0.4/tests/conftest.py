"""
Pytest configuration and shared fixtures for the Mosaia Python SDK tests.

This module provides common test fixtures and configuration that can be
used across all test modules.
"""

import asyncio
from typing import Any, Dict

import pytest

from mosaia import ConfigurationManager


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def config_manager():
    """Provide a clean ConfigurationManager instance for each test."""
    manager = ConfigurationManager.get_instance()
    manager.reset()  # Reset for clean test
    yield manager
    manager.reset()  # Clean up after test


@pytest.fixture(scope="function")
def test_config():
    """Provide test configuration data."""
    return {
        "api_key": "test-api-key",
        "api_url": "https://test-api.mosaia.ai",
        "version": "1",
        "client_id": "test-client-id",
        "client_secret": "test-client-secret",
        "verbose": True,
    }


@pytest.fixture(scope="function")
def initialized_config_manager(config_manager, test_config):
    """Provide a ConfigurationManager initialized with test config."""
    config_manager.initialize(test_config)
    return config_manager


@pytest.fixture(scope="function")
def sample_user_data():
    """Provide sample user data for testing."""
    return {
        "id": "user-123",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "username": "testuser",
        "name": "Test User",
        "description": "A test user",
    }


@pytest.fixture(scope="function")
def sample_organization_data():
    """Provide sample organization data for testing."""
    return {
        "id": "org-456",
        "name": "Test Organization",
        "short_description": "A test organization",
    }


@pytest.fixture(scope="function")
def sample_agent_data():
    """Provide sample agent data for testing."""
    return {
        "id": "agent-789",
        "name": "Test Agent",
        "short_description": "A test AI agent",
        "model": "gpt-4",
        "temperature": 0.7,
        "system_prompt": "You are a helpful test agent.",
    }


@pytest.fixture(scope="function")
def sample_app_data():
    """Provide sample app data for testing."""
    return {
        "id": "app-101",
        "name": "Test App",
        "short_description": "A test application",
        "external_app_url": "https://test-app.example.com",
    }


@pytest.fixture(scope="function")
def sample_tool_data():
    """Provide sample tool data for testing."""
    return {
        "id": "tool-202",
        "name": "Test Tool",
        "friendly_name": "Test Tool",
        "short_description": "A test tool",
        "tool_schema": '{"type": "object", "properties": {"test": {"type": "string"}}}',
    }


@pytest.fixture(scope="function")
def valid_object_ids():
    """Provide valid MongoDB ObjectIDs for testing."""
    return [
        "507f1f77bcf86cd799439011",
        "507f1f77bcf86cd799439012",
        "507f1f77bcf86cd799439013",
    ]


@pytest.fixture(scope="function")
def invalid_object_ids():
    """Provide invalid ObjectIDs for testing."""
    return [
        "invalid-id",
        "123",
        "507f1f77bcf86cd79943901",  # 23 chars
        "507f1f77bcf86cd7994390111",  # 25 chars
        "507f1f77bcf86cd79943901g",  # invalid char
        "",
        None,
    ]


@pytest.fixture(scope="function")
def sample_query_params():
    """Provide sample query parameters for testing."""
    return {
        "limit": 10,
        "offset": 0,
        "search": "test",
        "active": True,
        "tags": ["ai", "automation", "test"],
        "categories": ["featured", "popular"],
        "sort_by": "created_at",
        "sort_order": "desc",
    }


@pytest.fixture(scope="function")
def sample_error_data():
    """Provide sample error data for testing."""
    return {
        "message": "Test error message",
        "code": "TEST_ERROR",
        "status": 400,
        "more_info": {"details": "Additional error details", "field": "test_field"},
    }
