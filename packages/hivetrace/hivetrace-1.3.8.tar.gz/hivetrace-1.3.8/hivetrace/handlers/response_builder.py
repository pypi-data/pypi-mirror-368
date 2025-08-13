from datetime import datetime
from typing import Any, Dict, Optional

from ..models.responses import HivetraceResponse, ProcessResponse, SuccessResponse


class ResponseBuilder:
    """
    Response builder for creating structured responses.
    """

    @staticmethod
    def build_success_response(
        data: Dict[str, Any] = None, request_id: Optional[str] = None
    ) -> SuccessResponse:
        """Builds a successful response."""
        return SuccessResponse(
            success=True,
            timestamp=datetime.utcnow().isoformat(),
            request_id=request_id,
            **(data or {}),
        )

    @staticmethod
    def build_process_response(
        message_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        request_id: Optional[str] = None,
        additional_data: Dict[str, Any] = None,
    ) -> ProcessResponse:
        """Builds a response to process a message."""
        return ProcessResponse(
            success=True,
            timestamp=datetime.utcnow().isoformat(),
            message_id=message_id,
            trace_id=trace_id,
            request_id=request_id,
            **(additional_data or {}),
        )

    @staticmethod
    def build_response_from_api(
        api_response: Dict[str, Any], request_id: Optional[str] = None
    ) -> HivetraceResponse:
        """
        Builds a response from API data.

        Automatically determines the response type and creates the corresponding model.
        """
        if (
            api_response.get("success")
            or "message_id" in api_response
            or "trace_id" in api_response
        ):
            return ResponseBuilder.build_process_response(
                message_id=api_response.get("message_id"),
                trace_id=api_response.get("trace_id"),
                request_id=request_id,
                additional_data={
                    k: v
                    for k, v in api_response.items()
                    if k not in ["message_id", "trace_id", "request_id"]
                },
            )

        return api_response

    @staticmethod
    def add_request_id(
        response: HivetraceResponse, request_id: str
    ) -> HivetraceResponse:
        """Adds request_id to an existing response."""
        if isinstance(response, dict):
            response["request_id"] = request_id
            return response
        elif hasattr(response, "request_id"):
            response.request_id = request_id
            return response
        else:
            return response
