import os
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union

import httpx
from pydantic import ValidationError

from ..errors import InvalidParameterError, MissingConfigError
from ..handlers import ErrorHandler
from ..models import (
    FunctionCallRequest,
    HivetraceResponse,
    InputRequest,
)


class BaseHivetraceSDK(ABC):
    """
    Base class for HiveTrace SDK with common business logic.

    Contains validation, payload building and other common functionality,
    but delegates HTTP operations to specific implementations.
    """

    _DEFAULT_TIMEOUT = httpx.Timeout(connect=120.0, read=120.0, write=120.0, pool=120.0)

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or self._load_config_from_env()
        self.hivetrace_url = self._get_required_config("HIVETRACE_URL")
        self.hivetrace_access_token = self._get_required_config(
            "HIVETRACE_ACCESS_TOKEN"
        )
        self._closed = False

    def _load_config_from_env(self) -> Dict[str, Any]:
        return {
            "HIVETRACE_URL": os.getenv("HIVETRACE_URL", "").strip(),
            "HIVETRACE_ACCESS_TOKEN": os.getenv("HIVETRACE_ACCESS_TOKEN", "").strip(),
        }

    def _get_required_config(self, key: str) -> str:
        value = self.config.get(key, "").strip()
        if not value:
            raise MissingConfigError(key)

        if key == "HIVETRACE_URL":
            if not (value.startswith("http://") or value.startswith("https://")):
                raise InvalidParameterError(
                    parameter="HIVETRACE_URL",
                    message=f"Invalid URL format for {key}. Must start with http:// or https://",
                )
            return value.rstrip("/")

        return value

    @staticmethod
    def _validate_application_id(application_id: str) -> str:
        try:
            return str(uuid.UUID(application_id))
        except ValueError as e:
            raise InvalidParameterError(
                parameter="application_id", message="Invalid application_id format"
            ) from e

    @staticmethod
    def _validate_message(message: str) -> None:
        if not isinstance(message, str) or not message.strip():
            raise InvalidParameterError(
                parameter="message", message="Message must be non-empty"
            )

    @staticmethod
    def _validate_additional_parameters(
        additional_parameters: Optional[Dict[str, Any]],
    ) -> None:
        if additional_parameters is not None and not isinstance(
            additional_parameters, dict
        ):
            raise InvalidParameterError(
                parameter="additional_parameters",
                message="Additional parameters must be a dict or None",
            )

    def _build_request_args(
        self, endpoint: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        url = f"{self.hivetrace_url}/{endpoint.lstrip('/')}"
        headers = {"Authorization": f"Bearer {self.hivetrace_access_token}"}
        return {
            "url": url,
            "json": payload,
            "headers": headers,
            "timeout": self._DEFAULT_TIMEOUT,
        }

    def _handle_http_error(self, error: httpx.HTTPStatusError) -> HivetraceResponse:
        return ErrorHandler.handle_http_error(error)

    def _build_message_payload(
        self,
        application_id: str,
        message: str,
        additional_parameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Builds payload for message with validation through Pydantic."""
        try:
            request_model = InputRequest(
                application_id=application_id,
                message=message,
                additional_parameters=additional_parameters,
            )
            return request_model.dict()
        except ValidationError as e:
            raise InvalidParameterError(
                parameter="request_data", message=f"Validation failed: {e}"
            ) from e

    def _build_function_call_payload(
        self,
        application_id: str,
        tool_call_id: str,
        func_name: str,
        func_args: str,
        func_result: Optional[Union[Dict, str]] = None,
        additional_parameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Builds payload for function call with validation through Pydantic."""
        try:
            request_model = FunctionCallRequest(
                application_id=application_id,
                tool_call_id=tool_call_id,
                func_name=func_name,
                func_args=func_args,
                func_result=func_result,
                additional_parameters=additional_parameters,
            )
            return request_model.dict()
        except ValidationError as e:
            raise InvalidParameterError(
                parameter="request_data", message=f"Validation failed: {e}"
            ) from e

    @abstractmethod
    def input(
        self,
        application_id: str,
        message: str,
        additional_parameters: Optional[Dict[str, Any]] = None,
    ) -> HivetraceResponse:
        """Sends user request to HiveTrace."""
        pass

    @abstractmethod
    def output(
        self,
        application_id: str,
        message: str,
        additional_parameters: Optional[Dict[str, Any]] = None,
    ) -> HivetraceResponse:
        """Sends LLM response to HiveTrace."""
        pass

    @abstractmethod
    def function_call(
        self,
        application_id: str,
        tool_call_id: str,
        func_name: str,
        func_args: str,
        func_result: Optional[Union[Dict, str]] = None,
        additional_parameters: Optional[Dict[str, Any]] = None,
    ) -> HivetraceResponse:
        """Sends function call to HiveTrace."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Closes HTTP session and frees resources."""
        pass
