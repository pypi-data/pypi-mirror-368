"""
API client for the Mosaia Python SDK.

This module re-exports the APIClient from the utils module for convenience.
"""

from .utils.api_client import APIClient

__all__ = ["APIClient"]
