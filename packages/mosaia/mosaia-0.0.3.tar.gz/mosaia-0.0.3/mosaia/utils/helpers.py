"""
Helper utility functions for the Mosaia Python SDK.

This module contains common utility functions used throughout the SDK
for validation, error handling, query generation, and other common tasks.
"""

import re
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union


@dataclass
class FailureResponse:
    """Type for standardized failure responses."""

    data: None = None
    error: str = ""


@dataclass
class SuccessResponse:
    """Type for standardized success responses."""

    data: Any = None
    error: None = None


def is_valid_object_id(id_str: str) -> bool:
    """
    Validates if a string is a valid MongoDB ObjectID.

    MongoDB ObjectIDs are 24-character hexadecimal strings that serve as unique
    identifiers for documents in collections. This function validates
    the format and structure of ObjectID strings.

    Args:
        id_str: The string to validate as an ObjectID

    Returns:
        True if the string is a valid ObjectID, False otherwise

    Examples:
        Valid ObjectIDs:
        >>> is_valid_object_id('507f1f77bcf86cd799439011')
        True
        >>> is_valid_object_id('507f1f77bcf86cd799439012')
        True
        >>> is_valid_object_id('507f1f77bcf86cd799439013')
        True

        Invalid ObjectIDs:
        >>> is_valid_object_id('invalid-id')
        False
        >>> is_valid_object_id('123')
        False
        >>> is_valid_object_id('507f1f77bcf86cd79943901')  # 23 chars
        False
        >>> is_valid_object_id('507f1f77bcf86cd7994390111')  # 25 chars
        False
        >>> is_valid_object_id('507f1f77bcf86cd79943901g')  # invalid char
        False
    """
    if not isinstance(id_str, str):
        return False

    # MongoDB ObjectID is a 24-character hexadecimal string
    object_id_regex = re.compile(r"^[a-fA-F0-9]{24}$")
    return bool(object_id_regex.match(id_str))


def parse_error(error: Any) -> Dict[str, Any]:
    """
    Parses and standardizes error objects.

    This function takes any error object and converts it to a standardized format
    with consistent properties for error handling throughout the SDK. It ensures
    that all errors have the same structure regardless of their source.

    Args:
        error: Any error object to parse and standardize

    Returns:
        Standardized error object with consistent structure

    Examples:
        Basic error parsing:
        >>> try:
        ...     # Some operation that might fail
        ...     raise ValueError("Test error")
        ... except Exception as error:
        ...     standardized_error = parse_error(error)
        ...     print(standardized_error['message'])
        Test error

        Error handling in API calls:
        >>> try:
        ...     response = requests.get('/api/data')
        ...     response.raise_for_status()
        ... except requests.RequestException as error:
        ...     standardized_error = parse_error(error)
        ...     print(f"API Error: {standardized_error['message']}")
    """
    error_dict = {
        "message": getattr(error, "message", str(error)) or "Unknown Error",
        "status_code": getattr(error, "status_code", 400),
        "status": getattr(error, "status", "UNKNOWN"),
        "more_info": getattr(error, "more_info", {}),
    }

    # If more_info has a message, use it as the primary message
    if error_dict["more_info"].get("message"):
        error_dict["message"] = error_dict["more_info"]["message"]

    return error_dict


def query_generator(params: Optional[Dict[str, Any]] = None) -> str:
    """
    Generates a URL query string from an object of parameters.

    This function converts an object of key-value pairs into a properly formatted
    URL query string, handling both simple values and arrays. It automatically
    handles URL encoding and array notation for query parameters.

    Args:
        params: Object containing query parameters (optional)

    Returns:
        URL query string (e.g., "?key1=value1&key2=value2&key3[]=value3&key3[]=value4")

    Examples:
        Basic query parameters:
        >>> params = {
        ...     'limit': 10,
        ...     'offset': 0,
        ...     'search': 'john',
        ...     'active': True
        ... }
        >>> query_generator(params)
        '?limit=10&offset=0&search=john&active=True'

        With array parameters:
        >>> params = {
        ...     'tags': ['ai', 'automation', 'support'],
        ...     'categories': ['featured', 'popular'],
        ...     'exclude': ['archived', 'draft']
        ... }
        >>> query_generator(params)
        '?tags[]=ai&tags[]=automation&tags[]=support&categories[]=featured&categories[]=popular&exclude[]=archived&exclude[]=draft'

        Complex filtering:
        >>> filter_params = {
        ...     'user': 'user-123',
        ...     'org': 'org-456',
        ...     'status': ['active', 'pending'],
        ...     'created_after': '2024-01-01',
        ...     'sort_by': 'created_at',
        ...     'sort_order': 'desc',
        ...     'include_metadata': True
        ... }
        >>> query_generator(filter_params)
        '?user=user-123&org=org-456&status[]=active&status[]=pending&created_after=2024-01-01&sort_by=created_at&sort_order=desc&include_metadata=True'
    """
    if not params:
        return ""

    query_parts = []

    for key, value in params.items():
        if value is None or value == "":
            continue

        if isinstance(value, (list, tuple)):
            # Handle array parameters
            for item in value:
                if item is not None and item != "":
                    query_parts.append(f"{key}[]={item}")
        else:
            # Handle simple values
            query_parts.append(f"{key}={value}")

    if not query_parts:
        return ""

    return "?" + "&".join(query_parts)


def is_timestamp_expired(timestamp: Union[str, int, float]) -> bool:
    """
    Validates if a timestamp string is expired.

    This function parses a timestamp string (typically from JWT tokens) and checks
    if it represents a time that has already passed.

    Args:
        timestamp: The timestamp to validate (can be string, int, or float)

    Returns:
        True if the timestamp is in the past (expired), False otherwise

    Examples:
        >>> is_timestamp_expired('1754078962511')  # True if current time > 1754078962511
        True
        >>> is_timestamp_expired('9999999999999')  # False (future timestamp)
        False
        >>> is_timestamp_expired('')  # False (invalid timestamp)
        False
        >>> is_timestamp_expired(1754078962511)  # True if current time > 1754078962511
        True
    """
    if not timestamp:
        return False

    # Convert to string if it's a number
    timestamp_str = str(timestamp).strip()

    if not timestamp_str:
        return False

    # Check if the string contains non-numeric characters (except for the first character which could be a minus sign)
    if not re.match(r"^-?\d+$", timestamp_str):
        return False

    try:
        parsed_timestamp = int(timestamp_str)
        if parsed_timestamp <= 0:
            return False

        return parsed_timestamp < int(time.time() * 1000)
    except (ValueError, TypeError):
        return False


def failure(error: str) -> FailureResponse:
    """
    Creates a standardized failure response.

    Args:
        error: Error message describing the failure

    Returns:
        FailureResponse object with None data and the error message

    Examples:
        >>> result = failure('User not found')
        >>> result.data
        None
        >>> result.error
        'User not found'
    """
    return FailureResponse(data=None, error=error)


def success(data: Any = None) -> SuccessResponse:
    """
    Creates a standardized success response.

    Args:
        data: The data to include in the success response

    Returns:
        SuccessResponse object with the data and None error

    Examples:
        >>> result = success({'id': '123', 'name': 'John'})
        >>> result.data
        {'id': '123', 'name': 'John'}
        >>> result.error
        None
    """
    return SuccessResponse(data=data, error=None)


def server_error_to_string(err: Any) -> str:
    """
    Converts server errors to readable string format.

    This function takes server error objects and converts them to human-readable
    string messages, handling cases where errors have digest information.

    Args:
        err: Server error object

    Returns:
        Formatted error string

    Examples:
        >>> try:
        ...     # Some server operation
        ...     raise Exception("Database connection failed")
        ... except Exception as error:
        ...     error_message = server_error_to_string(error)
        ...     print('Server error:', error_message)
        Server error: Database connection failed
    """
    message_str = getattr(err, "message", str(err))

    if hasattr(err, "digest") and err.digest:
        print(f"{err.digest}: {message_str}")
        message_str = "Unexpected Error"
        digest_str = f" (digest: {err.digest})"
        return f"{message_str}{digest_str}"

    return message_str


def is_sdk_error(err: Any) -> bool:
    """
    Type guard to check if an error is an SDK error.

    This function checks if an error object has the structure of an SDK error
    by verifying it has the required properties: message, code, and status.

    Args:
        err: Any error object to check

    Returns:
        True if the error is an SDK error, False otherwise

    Examples:
        >>> try:
        ...     # Some SDK operation
        ...     raise Exception("SDK error")
        ... except Exception as error:
        ...     if is_sdk_error(error):
        ...         print('SDK Error:', error.message)
        ...     else:
        ...         print('Unexpected error:', error)
    """
    if not isinstance(err, dict) and not hasattr(err, "__dict__"):
        return False

    # Check if it's a dictionary-like object
    if isinstance(err, dict):
        return all(key in err for key in ["message", "code", "status"])

    # Check if it's an object with attributes
    return all(hasattr(err, attr) for attr in ["message", "code", "status"])
