#!/usr/bin/env python3
"""
Test script for the Mosaia Python SDK utils module.

This script tests the utility functions to ensure they work correctly
and maintain parity with the Node.js SDK.
"""

import time
from typing import Any, Dict

import pytest

# Test imports
from mosaia.utils import (
    failure,
    is_sdk_error,
    is_timestamp_expired,
    is_valid_object_id,
    parse_error,
    query_generator,
    server_error_to_string,
    success,
)


@pytest.mark.utils
class TestUtils:
    """Test utility functions."""

    def test_is_valid_object_id(self, valid_object_ids, invalid_object_ids):
        """Test ObjectID validation."""
        # Valid ObjectIDs
        for obj_id in valid_object_ids:
            assert is_valid_object_id(obj_id) is True

        # Invalid ObjectIDs
        for obj_id in invalid_object_ids:
            assert is_valid_object_id(obj_id) is False

    def test_parse_error(self):
        """Test error parsing."""
        # Test with Exception
        error = Exception("Test error")
        parsed = parse_error(error)
        assert parsed["message"] == "Test error"
        assert parsed["status_code"] == 400
        assert parsed["status"] == "UNKNOWN"

        # Test with custom error object
        class CustomError:
            def __init__(self):
                self.message = "Custom error"
                self.status_code = 404
                self.status = "NOT_FOUND"
                self.more_info = {"details": "test"}

        error = CustomError()
        parsed = parse_error(error)
        assert parsed["message"] == "Custom error"
        assert parsed["status_code"] == 404
        assert parsed["status"] == "NOT_FOUND"
        assert parsed["more_info"] == {"details": "test"}

    def test_query_generator(self, sample_query_params):
        """Test query string generation."""
        # Basic parameters
        params = {"limit": 10, "offset": 0, "search": "john", "active": True}
        query = query_generator(params)
        assert "limit=10" in query
        assert "offset=0" in query
        assert "search=john" in query
        assert "active=True" in query

        # Array parameters
        params = {
            "tags": ["ai", "automation", "support"],
            "categories": ["featured", "popular"],
        }
        query = query_generator(params)
        assert "tags[]=ai" in query
        assert "tags[]=automation" in query
        assert "tags[]=support" in query
        assert "categories[]=featured" in query
        assert "categories[]=popular" in query

        # Empty parameters
        assert query_generator({}) == ""
        assert query_generator(None) == ""

        # Complex parameters
        query = query_generator(sample_query_params)
        assert "limit=10" in query
        assert "search=test" in query
        assert "active=True" in query
        assert "tags[]=ai" in query
        assert "sort_by=created_at" in query

    def test_is_timestamp_expired(self):
        """Test timestamp expiration check."""
        # Future timestamp (should not be expired)
        future_timestamp = str(int(time.time() * 1000) + 3600000)  # 1 hour from now
        assert is_timestamp_expired(future_timestamp) is False

        # Past timestamp (should be expired)
        past_timestamp = str(int(time.time() * 1000) - 3600000)  # 1 hour ago
        assert is_timestamp_expired(past_timestamp) is True

        # Invalid timestamps
        assert is_timestamp_expired("") is False
        assert is_timestamp_expired("invalid") is False
        assert is_timestamp_expired(None) is False

    def test_failure(self):
        """Test failure response creation."""
        result = failure("User not found")
        assert result.data is None
        assert result.error == "User not found"

    def test_success(self):
        """Test success response creation."""
        data = {"id": "123", "name": "John"}
        result = success(data)
        assert result.data == data
        assert result.error is None

    def test_server_error_to_string(self):
        """Test server error to string conversion."""
        # Regular error
        error = Exception("Database connection failed")
        result = server_error_to_string(error)
        assert result == "Database connection failed"

        # Error with digest
        class DigestError:
            def __init__(self):
                self.message = "Test error"
                self.digest = "abc123"

        error = DigestError()
        result = server_error_to_string(error)
        assert "Unexpected Error" in result
        assert "abc123" in result

    def test_is_sdk_error(self, sample_error_data):
        """Test SDK error detection."""
        # SDK error
        sdk_error = {"message": "API error", "code": "API_ERROR", "status": 400}
        assert is_sdk_error(sdk_error) is True

        # Non-SDK error
        regular_error = Exception("Regular error")
        assert is_sdk_error(regular_error) is False

        # Partial SDK error
        partial_error = {"message": "API error", "code": "API_ERROR"}
        assert is_sdk_error(partial_error) is False

        # Test with sample error data
        assert is_sdk_error(sample_error_data) is True
