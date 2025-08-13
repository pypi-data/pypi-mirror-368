import warnings
from typing import Any, Dict, Optional, Union

import httpx

from ..handlers import ErrorHandler, ResponseBuilder
from ..models import HivetraceResponse
from .base import BaseHivetraceSDK


class AsyncHivetraceSDK(BaseHivetraceSDK):
    """
    Async implementation of HiveTrace SDK.

    Uses httpx.AsyncClient for non-blocking HTTP operations.

    Usage:
        async with AsyncHivetraceSDK() as client:
            result = await client.input(app_id, message)
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(config)
        self.session = httpx.AsyncClient()
        # SDK асинхронный, задаем флаг для адаптеров
        self.async_mode = True

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def _send_request(
        self, endpoint: str, payload: Dict[str, Any]
    ) -> HivetraceResponse:
        request_args = self._build_request_args(endpoint, payload)
        try:
            response = await self.session.post(**request_args)
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

    async def input(
        self,
        application_id: str,
        message: str,
        additional_parameters: Optional[Dict[str, Any]] = None,
    ) -> HivetraceResponse:
        payload = self._build_message_payload(
            application_id, message, additional_parameters
        )
        return await self._send_request("/process_request/", payload)

    async def output(
        self,
        application_id: str,
        message: str,
        additional_parameters: Optional[Dict[str, Any]] = None,
    ) -> HivetraceResponse:
        payload = self._build_message_payload(
            application_id, message, additional_parameters
        )
        return await self._send_request("/process_response/", payload)

    async def function_call(
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
        return await self._send_request("/process_tool_call/", payload)

    async def close(self) -> None:
        """Asyncly closes the HTTP session."""
        if self._closed:
            return
        self._closed = True
        await self.session.aclose()

    def __del__(self):
        """Destructor with warning for async session."""
        if hasattr(self, "session") and not self._closed:
            warnings.warn(
                "AsyncHivetraceSDK was not properly closed. "
                "Use 'async with AsyncHivetraceSDK()' or call 'await client.close()' explicitly.",
                ResourceWarning,
                stacklevel=2,
            )
