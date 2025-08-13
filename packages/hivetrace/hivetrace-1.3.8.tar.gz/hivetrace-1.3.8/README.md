# Hivetrace SDK

## Overview

The Hivetrace SDK lets you integrate with the Hivetrace service to monitor user prompts and LLM responses. It supports both synchronous and asynchronous workflows and can be configured via environment variables.

---

## Installation

Install from PyPI:

```bash
pip install hivetrace[base]
```

---

## Quick Start

```python
from hivetrace import SyncHivetraceSDK, AsyncHivetraceSDK
```

You can use either the synchronous client (`SyncHivetraceSDK`) or the asynchronous client (`AsyncHivetraceSDK`). Choose the one that fits your runtime.

---

## Synchronous Client

### Initialize (Sync)

```python
# The sync client reads configuration from environment variables or accepts an explicit config
client = SyncHivetraceSDK()
```

### Send a user prompt (input)

```python
response = client.input(
    application_id="your-application-id",  # Obtained after registering the application in the UI
    message="User prompt here",
)
```

### Send an LLM response (output)

```python
response = client.output(
    application_id="your-application-id",
    message="LLM response here",
)
```

---

## Asynchronous Client

### Initialize (Async)

```python
# The async client can be used as a context manager
client = AsyncHivetraceSDK()
```

### Send a user prompt (input)

```python
response = await client.input(
    application_id="your-application-id",
    message="User prompt here",
)
```

### Send an LLM response (output)

```python
response = await client.output(
    application_id="your-application-id",
    message="LLM response here",
)
```

---

## Example with Additional Parameters

```python
response = client.input(
    application_id="your-application-id",
    message="User prompt here",
    additional_parameters={
        "session_id": "your-session-id",
        "user_id": "your-user-id",
        "agents": {
            "agent-1-id": {"name": "Agent 1", "description": "Agent description"},
            "agent-2-id": {"name": "Agent 2"},
            "agent-3-id": {}
        }
    }
)
```

> **Note:** `session_id`, `user_id`, and all agent IDs must be valid UUIDs.

---

## API

### `input`

```python
# Sync
def input(application_id: str, message: str, additional_parameters: dict | None = None) -> dict: ...

# Async
async def input(application_id: str, message: str, additional_parameters: dict | None = None) -> dict: ...
```

Sends a **user prompt** to Hivetrace.

* `application_id` — Application identifier (must be a valid UUID, created in the UI)
* `message` — The user prompt
* `additional_parameters` — Optional dictionary with extra context (session, user, agents, etc.)

**Response example:**

```json
{
  "status": "processed",
  "monitoring_result": {
    "is_toxic": false,
    "type_of_violation": "benign",
    "token_count": 9,
    "token_usage_warning": false,
    "token_usage_unbounded": false
  }
}
```

---

### `output`

```python
# Sync
def output(application_id: str, message: str, additional_parameters: dict | None = None) -> dict: ...

# Async
async def output(application_id: str, message: str, additional_parameters: dict | None = None) -> dict: ...
```

Sends an **LLM response** to Hivetrace.

* `application_id` — Application identifier (must be a valid UUID, created in the UI)
* `message` — The LLM response
* `additional_parameters` — Optional dictionary with extra context (session, user, agents, etc.)

**Response example:**

```json
{
  "status": "processed",
  "monitoring_result": {
    "is_toxic": false,
    "type_of_violation": "safe",
    "token_count": 21,
    "token_usage_warning": false,
    "token_usage_unbounded": false
  }
}
```

---

## Sending Requests in Sync Mode

```python
def main():
    # option 1: context manager
    with SyncHivetraceSDK() as client:
        response = client.input(
            application_id="your-application-id",
            message="User prompt here",
        )

    # option 2: manual close
    client = SyncHivetraceSDK()
    try:
        response = client.input(
            application_id="your-application-id",
            message="User prompt here",
        )
    finally:
        client.close()

main()
```

---

## Sending Requests in Async Mode

```python
import asyncio

async def main():
    # option 1: context manager
    async with AsyncHivetraceSDK() as client:
        response = await client.input(
            application_id="your-application-id",
            message="User prompt here",
        )

    # option 2: manual close
    client = AsyncHivetraceSDK()
    try:
        response = await client.input(
            application_id="your-application-id",
            message="User prompt here",
        )
    finally:
        await client.close()

asyncio.run(main())
```

### Closing the Async Client

```python
await client.close()
```

---

## Configuration

The SDK reads configuration from environment variables:

* `HIVETRACE_URL` — Base URL allowed to call.
* `HIVETRACE_ACCESS_TOKEN` — API token used for authentication.

These are loaded automatically when you create a client.


### Configuration Sources

Hivetrace SDK can retrieve configuration from the following sources:

**.env File:**

```bash
HIVETRACE_URL=https://your-hivetrace-instance.com
HIVETRACE_ACCESS_TOKEN=your-access-token  # obtained in the UI (API Tokens page)
```

The SDK will automatically load these settings.

You can also pass a config dict explicitly when creating a client instance.
```bash
client = SyncHivetraceSDK(
    config={
        "HIVETRACE_URL": HIVETRACE_URL,
        "HIVETRACE_ACCESS_TOKEN": HIVETRACE_ACCESS_TOKEN,
    },
)
```

## Environment Variables

Set up your environment variables for easier configuration:

```bash
# .env file
HIVETRACE_URL=https://your-hivetrace-instance.com
HIVETRACE_ACCESS_TOKEN=your-access-token
HIVETRACE_APP_ID=your-application-id
```

# CrewAI Integration

**Demo repository**

[https://github.com/anntish/multiagents-crew-forge](https://github.com/anntish/multiagents-crew-forge)

## Step 1: Install the dependency

**What to do:** Add the HiveTrace SDK to your project

**Where:** In `requirements.txt` or via pip

```bash
# Via pip (for quick testing)
pip install hivetrace[crewai]>=1.3.5

# Or add to requirements.txt (recommended)
echo "hivetrace[crewai]>=1.3.3" >> requirements.txt
pip install -r requirements.txt
```

**Why:** The HiveTrace SDK provides decorators and clients for sending agent activity data to the monitoring platform.

---

## Step 2: **ADD** unique IDs for each agent

**Example:** In `src/config.py`

```python
PLANNER_ID = "333e4567-e89b-12d3-a456-426614174001"
WRITER_ID = "444e4567-e89b-12d3-a456-426614174002"
EDITOR_ID = "555e4567-e89b-12d3-a456-426614174003"
```

**Why agents need IDs:** HiveTrace tracks each agent individually. A UUID ensures the agent can be uniquely identified in the monitoring system.

---

## Step 3: Create an agent mapping

**What to do:** Map agent roles to their HiveTrace IDs

**Example:** In `src/agents.py` (where your agents are defined)

```python
from crewai import Agent
# ADD: import agent IDs
from src.config import EDITOR_ID, PLANNER_ID, WRITER_ID

# ADD: mapping for HiveTrace (REQUIRED!)
agent_id_mapping = {
    "Content Planner": {  # ← Exactly the same as Agent(role="Content Planner")
        "id": PLANNER_ID,
        "description": "Creates content plans"
    },
    "Content Writer": {   # ← Exactly the same as Agent(role="Content Writer")
        "id": WRITER_ID,
        "description": "Writes high-quality articles"
    },
    "Editor": {           # ← Exactly the same as Agent(role="Editor")
        "id": EDITOR_ID,
        "description": "Edits and improves articles"
    },
}

# Your existing agents (NO CHANGES)
planner = Agent(
    role="Content Planner",  # ← Must match key in agent_id_mapping
    goal="Create a structured content plan for the given topic",
    backstory="You are an experienced analyst...",
    verbose=True,
)

writer = Agent(
    role="Content Writer",   # ← Must match key in agent_id_mapping
    goal="Write an informative and engaging article",
    backstory="You are a talented writer...",
    verbose=True,
)

editor = Agent(
    role="Editor",           # ← Must match key in agent_id_mapping
    goal="Improve the article",
    backstory="You are an experienced editor...",
    verbose=True,
)
```

**Important:** The keys in `agent_id_mapping` must **exactly** match the `role` of your agents. Otherwise, HiveTrace will not be able to associate activity with the correct agent.

---

## Step 4: Integrate with tools (if used)

**What to do:** Add HiveTrace support to tools

**Example:** In `src/tools.py`

```python
from crewai.tools import BaseTool
from typing import Optional

class WordCountTool(BaseTool):
    name: str = "WordCountTool"
    description: str = "Count words, characters and sentences in text"
    # ADD: HiveTrace field (REQUIRED!)
    agent_id: Optional[str] = None
    
    def _run(self, text: str) -> str:
        word_count = len(text.split())
        return f"Word count: {word_count}"
```

**Example:** In `src/agents.py`

```python
from src.tools import WordCountTool
from src.config import PLANNER_ID, WRITER_ID, EDITOR_ID

# ADD: create tools for each agent
planner_tools = [WordCountTool()]
writer_tools = [WordCountTool()]
editor_tools = [WordCountTool()]

# ADD: assign tools to agents
for tool in planner_tools:
    tool.agent_id = PLANNER_ID

for tool in writer_tools:
    tool.agent_id = WRITER_ID

for tool in editor_tools:
    tool.agent_id = EDITOR_ID

# Use tools in agents
planner = Agent(
    role="Content Planner",
    tools=planner_tools,  # ← Agent-specific tools
    # ... other parameters
)
```

**Why:** HiveTrace tracks tool usage. The `agent_id` field in the tool class and its assignment let HiveTrace know which agent used which tool.

---

## Step 5: Initialize HiveTrace in FastAPI (if used)

**What to do:** Add the HiveTrace client to the application lifecycle

**Example:** In `main.py`

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
# ADD: import HiveTrace SDK
from hivetrace import SyncHivetraceSDK
from src.config import HIVETRACE_ACCESS_TOKEN, HIVETRACE_URL

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ADD: initialize HiveTrace client
    hivetrace = SyncHivetraceSDK(
        config={
            "HIVETRACE_URL": HIVETRACE_URL,
            "HIVETRACE_ACCESS_TOKEN": HIVETRACE_ACCESS_TOKEN,
        }
    )
    # Store client in app state
    app.state.hivetrace = hivetrace
    try:
        yield
    finally:
        # IMPORTANT: close connection on shutdown
        hivetrace.close()

app = FastAPI(lifespan=lifespan)
```

---

## Step 6: Integrate into business logic

**What to do:** Wrap Crew creation with the HiveTrace decorator

**Example:** In `src/services/topic_service.py`

```python
import uuid
from typing import Optional
from crewai import Crew
# ADD: HiveTrace imports
from hivetrace import SyncHivetraceSDK
from hivetrace import crewai_trace as trace

from src.agents import agent_id_mapping, planner, writer, editor
from src.tasks import plan_task, write_task, edit_task
from src.config import HIVETRACE_APP_ID

def process_topic(
    topic: str,
    hivetrace: SyncHivetraceSDK,  # ← ADD parameter
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
):
    # ADD: generate unique conversation ID
    agent_conversation_id = str(uuid.uuid4())
    
    # ADD: common trace parameters
    common_params = {
        "agent_conversation_id": agent_conversation_id,
        "user_id": user_id,
        "session_id": session_id,
    }

    # ADD: log user request
    hivetrace.input(
        application_id=HIVETRACE_APP_ID,
        message=f"Requesting information from agents on topic: {topic}",
        additional_parameters={
            **common_params,
            "agents": agent_id_mapping,  # ← pass agent mapping
        },
    )

    # ADD: @trace decorator for monitoring Crew
    @trace(
        hivetrace=hivetrace,
        application_id=HIVETRACE_APP_ID,
        agent_id_mapping=agent_id_mapping,  # ← REQUIRED!
    )
    def create_crew():
        return Crew(
            agents=[planner, writer, editor],
            tasks=[plan_task, write_task, edit_task],
            verbose=True,
        )

    # Execute with monitoring
    crew = create_crew()
    result = crew.kickoff(
        inputs={"topic": topic},
        **common_params  # ← pass common parameters
    )

    return {
        "result": result.raw,
        "execution_details": {**common_params, "status": "completed"},
    }
```

**How it works:**

1. **`agent_conversation_id`** — unique ID for grouping all actions under a single request
2. **`hivetrace.input()`** — sends the user’s request to HiveTrace for inspection
3. **`@trace`**:

   * Intercepts all agent actions inside the Crew
   * Sends data about each step to HiveTrace
   * Associates actions with specific agents via `agent_id_mapping`
4. **`**common_params`** — passes metadata into `crew.kickoff()` so all events are linked

**Critical:** The `@trace` decorator must be applied to the function that creates and returns the `Crew`, **not** the function that calls `kickoff()`.

---

## Step 7: Update FastAPI endpoints (if used)

**What to do:** Pass the HiveTrace client to the business logic

**Example:** In `src/routers/topic_router.py`

```python
from fastapi import APIRouter, Body, Request
# ADD: import HiveTrace type
from hivetrace import SyncHivetraceSDK

from src.services.topic_service import process_topic
from src.config import SESSION_ID, USER_ID

router = APIRouter(prefix="/api")

@router.post("/process-topic")
async def api_process_topic(request: Request, request_body: dict = Body(...)):
    # ADD: get HiveTrace client from app state
    hivetrace: SyncHivetraceSDK = request.app.state.hivetrace
    
    return process_topic(
        topic=request_body["topic"],
        hivetrace=hivetrace,  # ← pass client
        user_id=USER_ID,
        session_id=SESSION_ID,
    )
```

**Why:** The API endpoint must pass the HiveTrace client to the business logic so monitoring data can be sent.

---

## 🚨 Common mistakes

1. **Role mismatch** — make sure keys in `agent_id_mapping` exactly match `role` in agents
2. **Missing `agent_id_mapping`** — the `@trace` decorator must receive the mapping
3. **Decorator on wrong function** — `@trace` must be applied to the Crew creation function, not `kickoff`
4. **Client not closed** — remember to call `hivetrace.close()` in the lifespan
5. **Invalid credentials** — check your HiveTrace environment variables


# LangChain Integration

**Demo repository**

[https://github.com/anntish/multiagents-langchain-forge](https://github.com/anntish/multiagents-langchain-forge)

This project implements monitoring of a multi-agent system in LangChain via the HiveTrace SDK.

### Step 1. Install Dependencies

```bash
pip install hivetrace[langchain]>=1.3.5
# optional: add to requirements.txt and install
echo "hivetrace[langchain]>=1.3.3" >> requirements.txt
pip install -r requirements.txt
```

What the package provides: SDK clients (sync/async), a universal callback for LangChain agents, and ready-to-use calls for sending inputs/logs/outputs to HiveTrace.

### Step 2. Configure Environment Variables

* `HIVETRACE_URL`: HiveTrace address
* `HIVETRACE_ACCESS_TOKEN`: HiveTrace access token
* `HIVETRACE_APP_ID`: your application ID in HiveTrace
* `OPENAI_API_KEY`: key for the LLM provider (example with OpenAI)
* Additionally: `OPENAI_MODEL`, `USER_ID`, `SESSION_ID`

### Step 3. Assign Fixed UUIDs to Your Agents

Create a dictionary of fixed UUIDs for all "agent nodes" (e.g., orchestrator, specialized agents). This ensures unambiguous identification in tracing.

Example: file `src/core/constants.py`:

```python
PREDEFINED_AGENT_IDS = {
    "MainHub": "111e1111-e89b-12d3-a456-426614174099",
    "text_agent": "222e2222-e89b-12d3-a456-426614174099",
    "math_agent": "333e3333-e89b-12d3-a456-426614174099",
    "pre_text_agent": "444e4444-e89b-12d3-a456-426614174099",
    "pre_math_agent": "555e5555-e89b-12d3-a456-426614174099",
}
```

Tip: dictionary keys must match the actual node names appearing in logs (`tool`/agent name in LangChain calls).

### Step 4. Attach the Callback to Executors and Tools

Create and use `AgentLoggingCallback` — it should be passed:

* as a callback in `AgentExecutor` (orchestrator), and
* as `callback_handler` in your tools/agent wrappers (`BaseTool`).

Example: file `src/core/orchestrator.py` (fragment):

```python
from hivetrace.adapters.langchain import AgentLoggingCallback
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

class OrchestratorAgent:
    def __init__(self, llm, predefined_agent_ids=None):
        self.llm = llm
        self.logging_callback = AgentLoggingCallback(
            default_root_name="MainHub",
            predefined_agent_ids=predefined_agent_ids,
        )
        # Example: wrapper agents as tools
        # MathAgentTool/TextAgentTool internally pass self.logging_callback further
        agent = create_openai_tools_agent(self.llm, self.tools, ChatPromptTemplate.from_messages([
            ("system", "You are the orchestrator agent of a multi-agent system."),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]))
        self.executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            callbacks=[self.logging_callback],
        )
```

Important: all nested agents/tools that create their own `AgentExecutor` or inherit from `BaseTool` must also receive this `callback_handler` so their steps are included in tracing.

### Step 5. One-Line Integration in a Business Method

Use the `run_with_tracing` helper from `hivetrace/adapters/langchain/api.py`. It:

* logs the input with agent mapping and metadata;
* calls your orchestrator;
* collects and sends accumulated logs/final answer.

Minimal example (script):

```python
import os, uuid
from langchain_openai import ChatOpenAI
from src.core.orchestrator import OrchestratorAgent
from src.core.constants import PREDEFINED_AGENT_IDS
from hivetrace.adapters.langchain import run_with_tracing

llm = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), temperature=0.2, streaming=False)
orchestrator = OrchestratorAgent(llm, predefined_agent_ids=PREDEFINED_AGENT_IDS)

result = run_with_tracing(
    orchestrator=orchestrator,
    query="Format this text and count the number of words",
    application_id=os.getenv("HIVETRACE_APP_ID"),
    user_id=os.getenv("USER_ID"),
    session_id=os.getenv("SESSION_ID"),
    conversation_id=str(uuid.uuid4()),
)
print(result)
```

FastAPI variant (handler fragment):

```python
from fastapi import APIRouter, Request
from hivetrace.adapters.langchain import run_with_tracing
import uuid

router = APIRouter()

@router.post("/query")
async def process_query(payload: dict, request: Request):
    orchestrator = request.app.state.orchestrator
    conv_id = str(uuid.uuid4()) # always create a new agent_conversation_id for each request to group agent work for the same question
    result = run_with_tracing(
        orchestrator=orchestrator,
        query=payload["query"],
        application_id=request.app.state.HIVETRACE_APP_ID,
        user_id=request.app.state.USER_ID,
        session_id=request.app.state.SESSION_ID,
        conversation_id=conv_id,
    )
    return {"status": "success", "result": result}
```

### Step 6. Reusing the HiveTrace Client (Optional)

Helpers automatically create a short-lived client if none is provided. If you want to reuse a client — create it once during the application's lifecycle and pass it to helpers.

FastAPI (lifespan):

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from hivetrace import SyncHivetraceSDK

@asynccontextmanager
async def lifespan(app: FastAPI):
    hivetrace = SyncHivetraceSDK()
    app.state.hivetrace = hivetrace
    try:
        yield
    finally:
        hivetrace.close()

app = FastAPI(lifespan=lifespan)
```

Then:

```python
result = run_with_tracing(
    orchestrator=orchestrator,
    query=payload.query,
    hivetrace=request.app.state.hivetrace,  # pass your own client
    application_id=request.app.state.HIVETRACE_APP_ID,
)
```

### How Logs Look in HiveTrace

* **Agent nodes**: orchestrator nodes and specialized "agent wrappers" (`text_agent`, `math_agent`, etc.).
* **Actual tools**: low-level tools (e.g., `text_analyzer`, `text_formatter`) are logged on start/end events.
* **Service records**: automatically added `return_result` (returning result to parent) and `final_answer` (final answer of the root node) steps.

This gives a clear call graph with data flow direction and the final answer.

### Common Mistakes and How to Avoid Them

* **Name mismatch**: key in `PREDEFINED_AGENT_IDS` must match the node/tool name in logs.
* **No agent mapping**: either pass `agents_mapping` to `run_with_tracing` or define `predefined_agent_ids` in `AgentLoggingCallback` — the SDK will build the mapping automatically.
* **Callback not attached**: add `AgentLoggingCallback` to all `AgentExecutor` and `BaseTool` wrappers via the `callback_handler` parameter.
* **Client not closed**: use lifespan/context manager for `SyncHivetraceSDK`.


# OpenAI Agents Integration

**Demo repository**

[https://github.com/anntish/openai-agents-forge](https://github.com/anntish/openai-agents-forge)

### 1. Installation

```bash
pip install hivetrace[openai_agents]==1.3.5
```

---

### 2. Environment Setup

Set the environment variables (via `.env` or export):

```bash
HIVETRACE_URL=http://localhost:8000          # Your HiveTrace URL
HIVETRACE_ACCESS_TOKEN=ht_...                # Your HiveTrace access token
HIVETRACE_APPLICATION_ID=00000000-...-0000   # Your HiveTrace application ID

SESSION_ID=
USERID=

OPENAI_API_KEY=
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

---

### 3. Attach the Trace Processor in Code

Add 3 lines before creating/using your agents:

```python
from agents import set_trace_processors
from hivetrace.adapters.openai_agents.tracing import HivetraceOpenAIAgentProcessor

set_trace_processors([
    HivetraceOpenAIAgentProcessor()  # will take config from env
])
```

Alternative (explicit configuration if you don’t want to rely on env):

```python
from agents import set_trace_processors
from hivetrace import SyncHivetraceSDK
from hivetrace.adapters.openai_agents.tracing import HivetraceOpenAIAgentProcessor

hivetrace = SyncHivetraceSDK(config={
    "HIVETRACE_URL": "http://localhost:8000",
    "HIVETRACE_ACCESS_TOKEN": "ht_...",
})

set_trace_processors([
    HivetraceOpenAIAgentProcessor(
        application_id="00000000-0000-0000-0000-000000000000",
        hivetrace_instance=hivetrace,
    )
])
```

Important:

* Register the processor only once at app startup.
* Attach it before the first agent run (`Runner.run(...)` / `Runner.run_sync(...)`).

---

### 4. Minimal "Before/After" Example

Before:

```python
from agents import Agent, Runner

assistant = Agent(name="Assistant", instructions="Be helpful.")
print(Runner.run_sync(assistant, "Hi!"))
```

After (with HiveTrace monitoring):

```python
from agents import Agent, Runner, set_trace_processors
from hivetrace.adapters.openai_agents.tracing import HivetraceOpenAIAgentProcessor

set_trace_processors([HivetraceOpenAIAgentProcessor()])

assistant = Agent(name="Assistant", instructions="Be helpful.")
print(Runner.run_sync(assistant, "Hi!"))
```

From this moment, all agent calls, handoffs, and tool invocations will be logged in HiveTrace.

---

### 5. Tool Tracing

If you use tools, decorate them with `@function_tool` so their calls are automatically traced:

```python
from agents import function_tool

@function_tool(description_override="Adds two numbers")
def calculate_sum(a: int, b: int) -> int:
    return a + b
```

Add this tool to your agent’s `tools=[...]` — and its calls will appear in HiveTrace with inputs/outputs.

---

License
========

This project is licensed under Apache License 2.0.