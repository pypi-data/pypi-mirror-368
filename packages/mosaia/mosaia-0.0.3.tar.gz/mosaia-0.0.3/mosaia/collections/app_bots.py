"""
App Bots API client for the Mosaia SDK.

Provides CRUD operations for managing application-bot integrations in the Mosaia platform.
App Bots are specialized integrations that connect applications with AI agents
through webhook-style interactions.
"""

from typing import Any, Dict, Optional

from ..models.app_bot import AppBot
from .base_collection import BaseCollection


class AppBots(BaseCollection[Dict[str, Any], AppBot, Any, Any]):
    """
    App Bots API client for the Mosaia SDK.

    Provides CRUD operations for managing application-bot integrations in the Mosaia platform.
    App Bots are specialized integrations that connect applications with AI agents
    through webhook-style interactions.

    Examples:
        >>> from mosaia import Mosaia
        >>>
        >>> mosaia = Mosaia(api_key='your-api-key')
        >>> app_bots = mosaia.app_bots
        >>>
        # Get all app bots
        >>> all_app_bots = await app_bots.get()
        >>>
        # Get a specific app bot
        >>> app_bot = await app_bots.get({}, 'app-bot-id')
        >>>
        # Create a new app bot
        >>> new_app_bot = await app_bots.create({
        ...     'app': 'app-id',
        ...     'response_url': 'https://myapp.com/webhook',
        ...     'agent': 'agent-id',
        ...     'active': True
        ... })
    """

    def __init__(self, uri: str = ""):
        """
        Creates a new AppBots API client instance.

        Args:
            uri: Optional base URI path. If provided, the endpoint will be `${uri}/bot`.
                  If not provided, defaults to `/bot`.
        """
        super().__init__(f"{uri}/bot", AppBot)
