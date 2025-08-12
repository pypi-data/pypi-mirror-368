"""
Tool class for managing agent capabilities.

This class represents an external integration or utility that extends
agent capabilities in the Mosaia platform. Tools enable agents to
interact with external services, process data, and perform specialized
tasks through well-defined interfaces.

Features:
- Schema validation
- Environment management
- API integration
- Data transformation
- Error handling

Tools provide:
- External service integration
- Data processing capabilities
- API access management
- Input/output validation
- Environment configuration

Common tool types:
- API integrations
- Database connectors
- File processors
- Data transformers
- Service clients
"""

from typing import Any, Dict, Optional

from .base import BaseModel


class Tool(BaseModel[Dict[str, Any]]):
    """
    Tool class for managing agent capabilities.

    This class represents an external integration or utility that extends
    agent capabilities in the Mosaia platform. Tools enable agents to
    interact with external services, process data, and perform specialized
    tasks through well-defined interfaces.

    Features:
    - Schema validation
    - Environment management
    - API integration
    - Data transformation
    - Error handling

    Tools provide:
    - External service integration
    - Data processing capabilities
    - API access management
    - Input/output validation
    - Environment configuration

    Common tool types:
    - API integrations
    - Database connectors
    - File processors
    - Data transformers
    - Service clients

    Examples:
        Basic API tool:
        >>> # Create a weather API tool
        >>> weather_tool = Tool({
        ...     'name': 'weather-api',
        ...     'friendly_name': 'Weather Service',
        ...     'short_description': 'Get weather forecasts',
        ...     'tool_schema': json.dumps({
        ...         'type': 'object',
        ...         'properties': {
        ...             'location': {
        ...                 'type': 'string',
        ...                 'description': 'City name or coordinates'
        ...             },
        ...             'units': {
        ...                 'type': 'string',
        ...                 'enum': ['metric', 'imperial'],
        ...                 'default': 'metric'
        ...             }
        ...         },
        ...         'required': ['location']
        ...     }),
        ...     'required_environment_variables': ['WEATHER_API_KEY'],
        ...     'source_url': 'https://api.weather.com'
        ... })
        >>>
        >>> await weather_tool.save()

        Database tool:
        >>> # Create a database query tool
        >>> db_tool = Tool({
        ...     'name': 'db-query',
        ...     'friendly_name': 'Database Query',
        ...     'short_description': 'Execute database queries',
        ...     'tool_schema': json.dumps({
        ...         'type': 'object',
        ...         'properties': {
        ...             'query': {
        ...                 'type': 'string',
        ...                 'description': 'SQL query to execute'
        ...             },
        ...             'params': {
        ...                 'type': 'array',
        ...                 'items': {'type': 'string'},
        ...                 'description': 'Query parameters'
        ...             },
        ...             'timeout': {
        ...                 'type': 'number',
        ...                 'default': 30000
        ...             }
        ...         },
        ...         'required': ['query']
        ...     }),
        ...     'required_environment_variables': [
        ...         'DB_HOST',
        ...         'DB_USER',
        ...         'DB_PASS',
        ...         'DB_NAME'
        ...     ],
        ...     'metadata': {
        ...         'type': 'database',
        ...         'engine': 'postgresql',
        ...         'version': '14',
        ...         'max_connections': 10
        ...     }
        ... })
        >>>
        >>> if db_tool.is_active():
        ...     print('Database tool ready')
        ...     print('Schema:', json.loads(db_tool.tool_schema))
    """

    def __init__(self, data: Dict[str, Any], uri: Optional[str] = None):
        """
        Create a new tool configuration.

        Initializes a tool that extends agent capabilities through external
        integrations. Tools provide a standardized interface for agents to
        interact with external services and process data.

        Args:
            data: Configuration data including:
                  - name: Tool identifier
                  - friendly_name: Display name
                  - short_description: Brief description
                  - tool_schema: JSON Schema for inputs
                  - required_environment_variables: Required env vars
                  - source_url: Integration endpoint
                  - metadata: Additional tool data
            uri: Optional custom URI path for the tool endpoint. Defaults to '/tool'

        Examples:
            Basic file processor:
            >>> file_tool = Tool({
            ...     'name': 'file-processor',
            ...     'friendly_name': 'File Processor',
            ...     'short_description': 'Process and transform files',
            ...     'tool_schema': json.dumps({
            ...         'type': 'object',
            ...         'properties': {
            ...             'file_path': {
            ...                 'type': 'string',
            ...                 'description': 'Path to input file'
            ...             },
            ...             'output_format': {
            ...                 'type': 'string',
            ...                 'enum': ['json', 'csv', 'xml'],
            ...                 'default': 'json'
            ...             }
            ...         },
            ...         'required': ['file_path']
            ...     })
            ... })

            API integration:
            >>> api_tool = Tool({
            ...     'name': 'api-client',
            ...     'friendly_name': 'API Integration',
            ...     'short_description': 'Make API requests',
            ...     'tool_schema': json.dumps({
            ...         'type': 'object',
            ...         'properties': {
            ...             'method': {
            ...                 'type': 'string',
            ...                 'enum': ['GET', 'POST', 'PUT', 'DELETE']
            ...             },
            ...             'endpoint': {
            ...                 'type': 'string',
            ...                 'pattern': '^/'
            ...             },
            ...             'headers': {
            ...                 'type': 'object',
            ...                 'additionalProperties': True
            ...             },
            ...             'body': {
            ...                 'type': 'object',
            ...                 'additionalProperties': True
            ...             }
            ...         },
            ...         'required': ['method', 'endpoint']
            ...     }),
            ...     'required_environment_variables': [
            ...         'API_KEY',
            ...         'API_SECRET'
            ...     ],
            ...     'source_url': 'https://api.service.com',
            ...     'metadata': {
            ...         'version': '1.0',
            ...         'rate_limit': 100,
            ...         'timeout': 5000
            ...     }
            ... }, '/integrations/tool')
        """
        super().__init__(data, uri or "/tool")
