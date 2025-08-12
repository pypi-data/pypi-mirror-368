"""
AppBot class for managing webhook-based AI integrations.

This class represents a specialized integration that connects external
applications with AI agents through webhook-style interactions. AppBots
enable automated responses and workflows by bridging the gap between
applications and AI capabilities.

Features:
- Webhook endpoint management
- Secure API key handling
- Agent/group assignment
- Response routing
- Event handling

AppBots are particularly useful for:
- Chat platform integrations (Slack, Discord, etc.)
- Custom application webhooks
- Automated response systems
- Event-driven AI interactions
- Secure API access management
"""

from typing import Any, Dict, Optional

from .base import BaseModel


class AppBot(BaseModel[Dict[str, Any]]):
    """
    AppBot class for managing webhook-based AI integrations.

    This class represents a specialized integration that connects external
    applications with AI agents through webhook-style interactions. AppBots
    enable automated responses and workflows by bridging the gap between
    applications and AI capabilities.

    Features:
    - Webhook endpoint management
    - Secure API key handling
    - Agent/group assignment
    - Response routing
    - Event handling

    Examples:
        Basic bot setup:
        >>> # Create a Slack integration bot
        >>> slack_bot = AppBot({
        ...     'app': 'slack-app-id',
        ...     'response_url': 'https://slack.example.com/webhook',
        ...     'agent': 'support-agent-id',
        ...     'name': 'Slack Support Bot'
        ... })
        >>>
        >>> await slack_bot.save()
        >>> print('Bot API Key:', slack_bot.api_key)

        Custom webhook integration:
        >>> # Create a custom webhook bot
        >>> webhook_bot = AppBot({
        ...     'app': 'custom-app-id',
        ...     'response_url': 'https://api.example.com/ai-webhook',
        ...     'agent_group': 'expert-team-id',
        ...     'name': 'API Integration Bot',
        ...     'metadata': {
        ...         'team': 'engineering',
        ...         'environment': 'production'
        ...     }
        ... })
        >>>
        >>> # Configure and activate
        >>> await webhook_bot.save()
        >>> if webhook_bot.is_active():
        ...     print('Webhook URL:', webhook_bot.response_url)
        ...     print('API Key:', webhook_bot.api_key)
    """

    def __init__(self, data: Dict[str, Any], uri: Optional[str] = None):
        """
        Create a new AppBot instance.

        Initializes an app bot that connects external applications with AI agents
        through webhook-style interactions. The bot manages webhook endpoints,
        API keys, and routing of responses.

        Args:
            data: Configuration data including:
                  - app: Parent application ID
                  - response_url: Webhook endpoint URL
                  - agent: Associated agent ID (optional)
                  - agent_group: Associated agent group ID (optional)
                  - name: Bot display name
                  - metadata: Custom metadata object
            uri: Optional custom URI path for the bot endpoint. Defaults to '/bot'

        Examples:
            Basic webhook bot:
            >>> bot = AppBot({
            ...     'app': 'app-123',
            ...     'response_url': 'https://api.example.com/webhook',
            ...     'agent': 'agent-456',
            ...     'name': 'API Bot'
            ... })

            Advanced configuration:
            >>> bot = AppBot({
            ...     'app': 'app-123',
            ...     'response_url': 'https://chat.example.com/events',
            ...     'agent_group': 'group-789',
            ...     'name': 'Chat Integration',
            ...     'metadata': {
            ...         'platform': 'slack',
            ...         'channel': 'support',
            ...         'team': 'customer-success'
            ...     }
            ... }, '/integrations/bot')
        """
        super().__init__(data, uri or "/bot")
