import uuid

from hivetrace.adapters.base_adapter import BaseAdapter
from hivetrace.adapters.openai_agents.models import AgentCall, Call


class OpenaiAgentsAdapter(BaseAdapter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def log_traces(self, trace_calls: dict[str, Call | None], conversation_uuid: str):
        _trace_calls = self._join_handoff_spans(trace_calls)
        _trace_calls = self._join_agent_calling_tool_spans(_trace_calls)
        source_agent = _trace_calls[list(_trace_calls.keys())[0]]
        self._log_start_message(source_agent, conversation_uuid)

        for trace_call in _trace_calls.values():
            if trace_call is None or trace_call.span_parent_id is None:
                continue

            parent_agent: AgentCall = _trace_calls[trace_call.span_parent_id]
            if trace_call.type == "agent":
                additional_params = {
                    "agent_conversation_id": conversation_uuid,
                    "is_final_answer": False,
                    "agents": {
                        trace_call.agent_uuid: {
                            "agent_parent_id": parent_agent.agent_uuid,
                            "name": trace_call.name,
                            "description": trace_call.instructions,
                        },
                    },
                }
                self.output(
                    message=trace_call.output,
                    additional_params=additional_params,
                )

            elif trace_call.type == "tool":
                self._prepare_and_log(
                    log_method_name_stem="function_call",
                    is_async=False,
                    tool_call_details={
                        "application_id": self.application_id,
                        "tool_call_id": str(uuid.uuid4()),
                        "func_name": trace_call.name,
                        "func_args": f"{trace_call.input}",
                        "func_result": f"{trace_call.output}",
                        "additional_parameters": {
                            "agent_conversation_id": conversation_uuid,
                            "agents": {
                                parent_agent.agent_uuid: {
                                    "name": parent_agent.name,
                                    "description": parent_agent.instructions,
                                },
                            },
                        },
                    },
                )
        self._log_final_message(source_agent, conversation_uuid)

    def _join_agent_calling_tool_spans(
        self, trace_calls: dict[str, Call | None]
    ) -> dict[str, Call | None]:
        for span_id, span in trace_calls.items():
            if span.type == "agent" and span.span_parent_id is not None:
                parent = trace_calls[span.span_parent_id]
                if parent.type == "tool":
                    trace_calls[span.span_parent_id] = None
                    trace_calls[span_id].span_parent_id = parent.span_parent_id
                    trace_calls[span_id].input = (
                        parent.input if span.input is None else span.input
                    )
                    trace_calls[span_id].output = (
                        parent.output if span.output is None else span.output
                    )
        return trace_calls

    def _join_handoff_spans(
        self, trace_calls: dict[str, Call | None]
    ) -> dict[str, Call | None]:
        for span in reversed(trace_calls.values()):
            if span.type == "handoff" and span.span_parent_id is not None:
                parent = trace_calls[span.span_parent_id]
                child = next(
                    (
                        call
                        for call in trace_calls.values()
                        if call.name == span.to_agent
                    ),
                    None,
                )
                if parent is None:
                    continue
                child.span_parent_id = span.span_parent_id
                if parent.output is None:
                    parent.output = child.output
                if parent.input is None:
                    parent.input = child.input
        return trace_calls

    def _log_start_message(self, trace_call: AgentCall, conversation_uuid: str):
        self.input(
            message=trace_call.input,
            additional_params={
                "agent_conversation_id": conversation_uuid,
                "agents": {
                    trace_call.agent_uuid: {
                        "name": trace_call.name,
                        "description": trace_call.instructions,
                    },
                },
            },
        )

    def _log_final_message(self, trace_call: AgentCall, conversation_uuid: str):
        self.output(
            message=trace_call.output,
            additional_params={
                "agent_conversation_id": conversation_uuid,
                "is_final_answer": True,
                "agents": {
                    trace_call.agent_uuid: {
                        "name": trace_call.name,
                        "description": trace_call.instructions,
                    },
                },
            },
        )
