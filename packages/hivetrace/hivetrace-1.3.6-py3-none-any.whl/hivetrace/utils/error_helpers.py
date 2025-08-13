"""
Utils for working with errors in HiveTrace SDK.
"""

from typing import Optional

from ..models.responses import HivetraceResponse


def is_error_response(response: HivetraceResponse) -> bool:
    """Checks if the response is an error."""
    if isinstance(response, dict):
        return "error" in response
    return hasattr(response, "error") and hasattr(response, "error_type")


def get_error_type(response: HivetraceResponse) -> Optional[str]:
    """Gets the error type from the response."""
    if isinstance(response, dict) and "error_type" in response:
        return response["error_type"]
    elif hasattr(response, "error_type"):
        return response.error_type
    return None


def is_connection_error(response: HivetraceResponse) -> bool:
    """Checks if the response is a connection error."""
    return get_error_type(response) == "connection_error"


def is_timeout_error(response: HivetraceResponse) -> bool:
    """Checks if the response is a timeout error."""
    return get_error_type(response) == "timeout_error"


def is_http_error(response: HivetraceResponse) -> bool:
    """Checks if the response is an HTTP error."""
    return get_error_type(response) == "http_error"


def is_json_decode_error(response: HivetraceResponse) -> bool:
    """Checks if the response is a JSON decoding error."""
    return get_error_type(response) == "json_decode_error"


def is_request_error(response: HivetraceResponse) -> bool:
    """Checks if the response is a request error."""
    return get_error_type(response) == "request_error"


def is_validation_error(response: HivetraceResponse) -> bool:
    """Checks if the response is a validation error."""
    return get_error_type(response) == "validation_error"


def get_error_details(response: HivetraceResponse) -> Optional[str]:
    """Gets the error details from the response."""
    if isinstance(response, dict) and "details" in response:
        return response["details"]
    elif hasattr(response, "details"):
        return response.details
    return None


def get_status_code(response: HivetraceResponse) -> Optional[int]:
    """Gets the HTTP status code from the error."""
    if isinstance(response, dict) and "status_code" in response:
        return response["status_code"]
    elif hasattr(response, "status_code"):
        return response.status_code
    return None


def is_success_response(response: HivetraceResponse) -> bool:
    """Checks if the response is a success."""
    if isinstance(response, dict):
        return response.get("success", True) and "error" not in response
    return hasattr(response, "success") and getattr(response, "success", True)
