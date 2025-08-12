#!/usr/bin/env python3
"""
Test script for the Mosaia Python SDK functions module.

This script tests the function classes to ensure they work correctly
and maintain parity with the Node.js SDK.
"""

from typing import Any, Dict

import pytest

# Test imports
from mosaia.functions import BaseFunctions, Chat, Completions


@pytest.mark.functions
class TestBaseFunctions:
    """Test BaseFunctions functionality."""

    def test_base_functions_creation(self):
        """Test BaseFunctions can be instantiated."""

        class TestFunctions(BaseFunctions):
            pass

        functions = TestFunctions("/test")
        assert functions.uri == "/test"
        assert functions.api_client is not None
        assert functions.config_manager is not None

    def test_config_property(self, initialized_config_manager):
        """Test config property returns configuration."""

        class TestFunctions(BaseFunctions):
            pass

        functions = TestFunctions()
        config = functions.config
        assert config.api_key == "test-api-key"
        assert config.api_url == "https://test-api.mosaia.ai"

    def test_handle_error(self):
        """Test error handling."""

        class TestFunctions(BaseFunctions):
            pass

        functions = TestFunctions()

        # Test with Exception
        error = Exception("Test error")
        handled_error = functions._handle_error(error)
        assert str(handled_error) == "Test error"

        # Test with dict
        error_dict = {"message": "Dict error"}
        handled_error = functions._handle_error(error_dict)
        assert str(handled_error) == "Dict error"

        # Test with string
        string_error = "String error"
        handled_error = functions._handle_error(string_error)
        assert str(handled_error) == "String error"

        # Test with unknown error: should still coerce to a generic message
        unknown_error = object()
        handled_error = functions._handle_error(unknown_error)
        assert str(handled_error) == "Unknown error occurred"


@pytest.mark.functions
class TestChat:
    """Test Chat functionality."""

    def test_chat_creation(self):
        """Test Chat can be instantiated."""
        chat = Chat("/agent/123")
        assert chat.uri == "/agent/123/chat"
        assert chat.api_client is not None

    def test_chat_completions_property(self):
        """Test chat completions property."""
        chat = Chat("/agent/123")
        completions = chat.completions

        assert isinstance(completions, Completions)
        assert completions.uri == "/agent/123/chat/completions"

    def test_chat_with_different_uris(self):
        """Test Chat with different URI patterns."""
        # Agent chat
        agent_chat = Chat("/agent/agent-id")
        assert agent_chat.uri == "/agent/agent-id/chat"

        # Model chat
        model_chat = Chat("/model/model-id")
        assert model_chat.uri == "/model/model-id/chat"

        # Agent group chat
        group_chat = Chat("/agent-group/group-id")
        assert group_chat.uri == "/agent-group/group-id/chat"

        # Empty URI
        empty_chat = Chat()
        assert empty_chat.uri == "/chat"


@pytest.mark.functions
class TestCompletions:
    """Test Completions functionality."""

    def test_completions_creation(self):
        """Test Completions can be instantiated."""
        completions = Completions("/agent/123/chat")
        assert completions.uri == "/agent/123/chat/completions"
        assert completions.api_client is not None

    def test_completions_with_empty_uri(self):
        """Test Completions with empty URI."""
        completions = Completions()
        assert completions.uri == "/completions"

    def test_completions_inheritance(self):
        """Test Completions inherits from BaseFunctions."""
        completions = Completions("/test")
        assert isinstance(completions, BaseFunctions)
        assert hasattr(completions, "get")
        assert hasattr(completions, "create")
        assert hasattr(completions, "update")
        assert hasattr(completions, "delete")


@pytest.mark.functions
class TestAsyncFunctions:
    """Test async functionality of functions."""

    def test_base_functions_async_methods(self):
        """Test BaseFunctions async methods exist."""

        class TestFunctions(BaseFunctions):
            pass

        functions = TestFunctions("/test")

        # Check that methods are async
        import inspect

        assert inspect.iscoroutinefunction(functions.get)
        assert inspect.iscoroutinefunction(functions.create)
        assert inspect.iscoroutinefunction(functions.update)
        assert inspect.iscoroutinefunction(functions.delete)

    def test_chat_async_integration(self):
        """Test Chat async integration."""
        chat = Chat("/agent/123")
        completions = chat.completions

        # Check that completions methods are async
        import inspect

        assert inspect.iscoroutinefunction(completions.get)
        assert inspect.iscoroutinefunction(completions.create)
        assert inspect.iscoroutinefunction(completions.update)
        assert inspect.iscoroutinefunction(completions.delete)


@pytest.mark.functions
class TestFunctionsIntegration:
    """Test functions integration."""

    def test_chat_completions_integration(self):
        """Test Chat and Completions integration."""
        # Create chat instance
        chat = Chat("/agent/123")

        # Get completions
        completions = chat.completions

        # Verify the relationship
        assert completions.uri == "/agent/123/chat/completions"
        assert isinstance(completions, Completions)
        assert isinstance(chat, BaseFunctions)

    def test_functions_inheritance_chain(self):
        """Test the inheritance chain of functions."""
        # BaseFunctions is the base class
        assert issubclass(Chat, BaseFunctions)
        assert issubclass(Completions, BaseFunctions)

        # Chat and Completions are not related by inheritance
        assert not issubclass(Chat, Completions)
        assert not issubclass(Completions, Chat)

    def test_functions_type_annotations(self):
        """Test that functions have proper type annotations."""
        import inspect

        # Check BaseFunctions
        sig = inspect.signature(BaseFunctions.__init__)
        assert "uri" in sig.parameters

        # Check Chat
        sig = inspect.signature(Chat.__init__)
        assert "uri" in sig.parameters

        # Check Completions
        sig = inspect.signature(Completions.__init__)
        assert "uri" in sig.parameters
