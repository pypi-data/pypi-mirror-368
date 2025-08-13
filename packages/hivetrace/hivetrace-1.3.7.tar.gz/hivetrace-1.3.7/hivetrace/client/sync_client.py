import weakref
from typing import Any, Dict, Optional, Union

import httpx

from ..handlers import ErrorHandler, ResponseBuilder
from ..models import HivetraceResponse
from .base import BaseHivetraceSDK


class SyncHivetraceSDK(BaseHivetraceSDK):
    """
    Sync implementation of HiveTrace SDK.

    Uses httpx.Client for blocking HTTP operations.

    Usage:
        with SyncHivetraceSDK() as client:
            result = client.input(app_id, message)
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(config)
        self.session = httpx.Client()
        self.async_mode = False

        self._finalizer = weakref.finalize(
            self, self._cleanup_sync_session, self.session
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @staticmethod
    def _cleanup_sync_session(session):
        """Safely closes sync session through finalizer."""
        try:
            if hasattr(session, "_transport") and not session.is_closed:
                session.close()
        except Exception:
            pass

    def _send_request(
        self, endpoint: str, payload: Dict[str, Any]
    ) -> HivetraceResponse:
        request_args = self._build_request_args(endpoint, payload)
        try:
            response = self.session.post(**request_args)
            response.raise_for_status()

            api_data = response.json()
            return ResponseBuilder.build_response_from_api(api_data)

        except httpx.HTTPStatusError as e:
            return ErrorHandler.handle_http_error(e)
        except httpx.ConnectError as e:
            return ErrorHandler.handle_connection_error(e)
        except httpx.TimeoutException as e:
            return ErrorHandler.handle_timeout_error(e)
        except httpx.RequestError as e:
            return ErrorHandler.handle_request_error(e)
        except ValueError as e:
            return ErrorHandler.handle_json_decode_error(e)
        except Exception as e:
            return ErrorHandler.handle_unexpected_error(e)

    def input(
        self,
        application_id: str,
        message: str,
        additional_parameters: Optional[Dict[str, Any]] = None,
    ) -> HivetraceResponse:
        payload = self._build_message_payload(
            application_id, message, additional_parameters
        )
        return self._send_request("/process_request/", payload)

    def output(
        self,
        application_id: str,
        message: str,
        additional_parameters: Optional[Dict[str, Any]] = None,
    ) -> HivetraceResponse:
        payload = self._build_message_payload(
            application_id, message, additional_parameters
        )
        return self._send_request("/process_response/", payload)

    def function_call(
        self,
        application_id: str,
        tool_call_id: str,
        func_name: str,
        func_args: str,
        func_result: Optional[Union[Dict, str]] = None,
        additional_parameters: Optional[Dict[str, Any]] = None,
    ) -> HivetraceResponse:
        payload = self._build_function_call_payload(
            application_id,
            tool_call_id,
            func_name,
            func_args,
            func_result,
            additional_parameters,
        )
        return self._send_request("/process_tool_call/", payload)

    def close(self) -> None:
        """Syncly closes HTTP session."""
        if self._closed:
            return
        self._closed = True
        self.session.close()
