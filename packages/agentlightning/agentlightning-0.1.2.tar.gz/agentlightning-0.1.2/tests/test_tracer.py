"""
Integration tests for various agent frameworks with AgentLightning.

This module tests the integration of AgentLightning with:
- Autogen AgentChat
- LangChain/LangGraph
- OpenAI Agent SDK
- AgentOps
- Reward tracking functionality

Uses real agent frameworks but defaults to a mock OpenAI API server.
Set ``OPENAI_BASE_URL`` and ``OPENAI_API_KEY`` environment variables to run
against the real API with the ``OPENAI_MODEL`` of your choice (``gpt-4.1-nano``
by default).
"""

import pytest
import inspect
import json
import asyncio
import time
import os
import re
import httpx
import difflib
import pprint
from contextlib import contextmanager
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from typing import Dict, Any, List, Optional
import threading
import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field

from agentlightning.tracer.agentops import AgentOpsTracer, LightningSpanProcessor
from agentlightning.tracer.triplet import TraceTree
from agentlightning.tracer.http import HttpTracer
from agentlightning.tracer.triplet import TripletExporter
from agentlightning.reward import reward
from agentlightning.types import Triplet

import openai
from openai import OpenAI, AsyncOpenAI

from langchain import hub
from langchain.chat_models import init_chat_model
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, BaseMessage, AIMessage, ToolMessage
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import tool, AgentExecutor, create_react_agent
from langchain_core.messages import AIMessage
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode
from typing import Literal

from langgraph.graph import StateGraph, END, MessagesState
from typing_extensions import TypedDict

import autogen_agentchat
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import ExternalTermination, TextMentionTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.tools.mcp import McpWorkbench, StdioServerParams

from agents import Agent, Runner, AgentHooks, InputGuardrail, GuardrailFunctionOutput, function_tool, RunConfig
from agents.mcp import MCPServerStdio
from agents.models.openai_provider import OpenAIProvider

import litellm

import agentops

USE_OPENAI = os.environ.get("USE_OPENAI", "false").lower() == "true"
if USE_OPENAI:
    OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", os.environ["OPENAI_API_BASE"])
    OPENAI_MODEL = "gpt-4.1-mini"
    OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
else:
    OPENAI_BASE_URL = "http://127.0.0.1:8000/v1"
    OPENAI_MODEL = "gpt-4.1-mini"
    OPENAI_API_KEY = "token-abc123"


_langchain_callback_handler = None


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Dict[str, Any]]
    stream: bool = False
    tools: Optional[List[Any]] = None
    tool_choice: Optional[Any] = None


class MockOpenAICompatibleServer:
    """
    A mock server that mimics the OpenAI Chat Completions API for testing purposes.
    It provides deterministic, canned responses based on the content of the prompt.
    Now supports replaying from prompt caches.
    """

    def __init__(self, host="127.0.0.1", port=8000):
        self.host = host
        self.port = port
        self.app = FastAPI()
        self.server_thread = None
        self.server = None
        self.prompt_caches = self._load_prompt_caches()
        self._setup_routes()

    def _load_prompt_caches(self):
        cache_path = os.path.join(os.path.dirname(__file__), "assets/prompt_caches.jsonl")
        caches = []
        if os.path.exists(cache_path):
            with open(cache_path, "r") as f:
                for line in f:
                    try:
                        caches.append(json.loads(line))
                    except Exception:
                        continue
        return caches

    def _find_best_cache_match(self, request_dict):
        """
        Find the cached request with the highest similarity to the incoming request.
        Returns (response, similarity_score) or (None, 0.0) if not found.
        """

        def normalize_messages(msgs):
            # Flatten messages to a string for comparison
            if not msgs:
                return ""
            return "\n".join(f"{m.get('role','')}:{m.get('content','')}" for m in msgs)

        req_msgs = request_dict.get("messages", [])
        req_tools = request_dict.get("tools", "")
        req_str = normalize_messages(req_msgs) + f"\ntools:{req_tools}"

        best_score = 0.0
        best_response = None
        for cache in self.prompt_caches:
            cache_req = cache.get("request", {})
            cache_msgs = cache_req.get("messages", [])
            cache_tools = cache_req.get("tools", "")
            cache_str = normalize_messages(cache_msgs) + f"\ntools:{cache_tools}"

            # Use difflib for quick ratio
            score = difflib.SequenceMatcher(None, req_str, cache_str).ratio()
            if score > best_score:
                best_score = score
                best_response = cache.get("response")
        return best_response, best_score

    def _setup_routes(self):
        @self.app.post("/v1/chat/completions")
        def chat_completions(request: ChatCompletionRequest):
            # Try to find the best match in prompt caches
            request_dict = request.model_dump()
            cached_response, score = self._find_best_cache_match(request_dict)
            if cached_response and score > 0.8:
                time.sleep(0.1)  # Simulate network delay
                # Return the cached response directly
                cached_response["prompt_token_ids"] = [1, 2, 3]
                cached_response["response_token_ids"] = [[4, 5, 6]]
                return cached_response
            raise ValueError("No suitable cached response found. Please ensure the prompt caches are populated.")

    async def __aenter__(self):
        # Start the server manually
        config = uvicorn.Config(self.app, host=self.host, port=self.port, log_level="error")
        self.server = uvicorn.Server(config)
        self.server_thread = threading.Thread(target=self.server.run, daemon=True)
        self.server_thread.start()

        # Wait for server to start
        max_wait = 10  # seconds
        wait_time = 0
        while not getattr(self.server, "started", False) and wait_time < max_wait:
            await asyncio.sleep(0.1)
            wait_time += 0.1

        if not getattr(self.server, "started", False):
            raise RuntimeError("Server failed to start within timeout")

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.server:
            self.server.should_exit = True
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(timeout=5)


async def run_agent(agent_func):
    """
    Run an agent function with mock server, handling both sync and async functions.

    This function starts a mock OpenAI server and then detects whether the agent
    function is async or sync, executing it appropriately within the server context.

    Args:
        agent_func: The agent function to execute (sync or async)

    Returns:
        The result of the agent function execution
    """
    # Use the mock server only when pointing to the default local URL
    if OPENAI_BASE_URL.startswith("http://127.0.0.1"):
        async with MockOpenAICompatibleServer():
            if inspect.iscoroutinefunction(agent_func):
                return await agent_func()
            else:
                return agent_func()
    else:
        # Check if the function is async
        if inspect.iscoroutinefunction(agent_func):
            # Handle async function - run directly since we're already in async context
            return await agent_func()
        else:
            # Handle sync function - run without threading
            return agent_func()


def agent_pure_openai():
    """A simple agent using the `openai` library."""
    client = OpenAI(base_url=OPENAI_BASE_URL, api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=OPENAI_MODEL, messages=[{"role": "user", "content": "What is the capital of France?"}]
    )
    assert "Paris" in response.choices[0].message.content


def agent_litellm():
    """Agent using `litellm` to call the mock server."""
    response = litellm.completion(
        model="openai/" + OPENAI_MODEL,
        messages=[{"role": "user", "content": "What is 2 + 2?"}],
        base_url=OPENAI_BASE_URL,
        api_key=OPENAI_API_KEY,
    )
    assert "4" in response.choices[0].message.content


def agent_langchain():
    """A simple LangChain agent."""
    llm = ChatOpenAI(model=OPENAI_MODEL, openai_api_base=OPENAI_BASE_URL, openai_api_key=OPENAI_API_KEY)
    prompt = ChatPromptTemplate.from_messages([("human", "{input}")])
    chain = prompt | llm | StrOutputParser()
    result = chain.invoke({"input": "What is the capital of France?"})
    assert "Paris" in result


def agent_langchain_tooluse():
    """A LangChain agent that uses a calculator tool."""

    @tool
    def multiply(a_and_b: str) -> int:
        """A simple calculator tool that multiplies two integers."""
        a, b = re.search(r"(\d+).*?(\d+)", a_and_b).groups()
        return int(a) * int(b)

    llm = ChatOpenAI(
        model=OPENAI_MODEL,
        temperature=0,
        openai_api_base=OPENAI_BASE_URL,
        openai_api_key=OPENAI_API_KEY,
        disable_streaming=True,
    )
    tools = [multiply]
    agent = create_react_agent(llm, tools, hub.pull("hwchase17/react"))
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)
    result = agent_executor.invoke(
        {"input": "what is 42 * 12"},
        {"callbacks": [_langchain_callback_handler]} if _langchain_callback_handler else None,
    )
    assert "504" in result["output"]


def agent_langgraph():
    """An agent built with LangGraph for stateful, cyclical workflows."""
    llm = init_chat_model("openai:" + OPENAI_MODEL, openai_api_base=OPENAI_BASE_URL, openai_api_key=OPENAI_API_KEY)
    db = SQLDatabase.from_uri("sqlite:///" + os.path.join(os.path.dirname(__file__), "assets/chinook.db"))
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    tools = toolkit.get_tools()

    def get_tool(name):
        return next(t for t in tools if t.name == name)

    get_schema_tool = next(tool for tool in tools if tool.name == "sql_db_schema")
    get_schema_node = ToolNode([get_schema_tool], name="get_schema")

    run_query_tool = next(tool for tool in tools if tool.name == "sql_db_query")
    run_query_node = ToolNode([run_query_tool], name="run_query")

    def list_tables(state: MessagesState):
        tool_call = {
            "name": "sql_db_list_tables",
            "args": {},
            "id": "abc123",
            "type": "tool_call",
        }
        tool_call_message = AIMessage(content="", tool_calls=[tool_call])

        list_tables_tool = next(tool for tool in tools if tool.name == "sql_db_list_tables")
        tool_message = list_tables_tool.invoke(tool_call)
        response = AIMessage(f"Available tables: {tool_message.content}")

        return {"messages": [tool_call_message, tool_message, response]}

    def call_get_schema(state: MessagesState):
        # Note that LangChain enforces that all models accept `tool_choice="any"`
        # as well as `tool_choice=<string name of tool>`.
        llm_with_tools = llm.bind_tools([get_schema_tool], tool_choice="any")
        response = llm_with_tools.invoke(state["messages"])

        return {"messages": [response]}

    # Generate SQL Query
    def generate_query(state: MessagesState):
        prompt = f"""
    You are an agent for SQL ({db.dialect}). 
    Write a query to answer the user. Limit results to 5. Do not modify data.
    """
        msg = {"role": "system", "content": prompt}
        llm_with_tools = llm.bind_tools([get_tool("sql_db_query")])
        resp = llm_with_tools.invoke([msg] + state["messages"])
        return {"messages": [resp]}

    # Double-check SQL Query
    def check_query(state: MessagesState):
        prompt = f"""
    You are a SQL expert. Double check the following {db.dialect} query for mistakes.
    Rewrite if needed. Otherwise, output as is.
    """
        user_query = state["messages"][-1].tool_calls[0]["args"]["query"]
        llm_with_tools = llm.bind_tools([get_tool("sql_db_query")], tool_choice="any")
        resp = llm_with_tools.invoke([{"role": "system", "content": prompt}, {"role": "user", "content": user_query}])
        resp.id = state["messages"][-1].id  # keep consistent ID for trace
        return {"messages": [resp]}

    # Conditional edge: if query tool-call exists, check query, else done
    def should_continue(state: MessagesState) -> Literal[END, "check_query"]:
        last = state["messages"][-1]
        return "check_query" if getattr(last, "tool_calls", None) else END

    # 5. Build the agent graph
    builder = StateGraph(MessagesState)
    builder.add_node(list_tables)
    builder.add_node(call_get_schema)
    builder.add_node(get_schema_node, "get_schema")
    builder.add_node(generate_query)
    builder.add_node(check_query)
    builder.add_node(run_query_node, "run_query")
    builder.add_edge(START, "list_tables")
    builder.add_edge("list_tables", "call_get_schema")
    builder.add_edge("call_get_schema", "get_schema")
    builder.add_edge("get_schema", "generate_query")
    builder.add_conditional_edges(
        "generate_query",
        should_continue,
    )
    builder.add_edge("check_query", "run_query")
    builder.add_edge("run_query", "generate_query")
    agent = builder.compile()

    # 6. Run a sample question
    question = "Which sales agent made the most in sales in 2009?"
    result = agent.invoke(
        {"messages": [{"role": "user", "content": question}]},
        {"callbacks": [_langchain_callback_handler]} if _langchain_callback_handler else None,
    )
    assert "Steve Johnson" in result["messages"][-1].content
    assert len(result["messages"]) > 5


async def agent_autogen_multiagent():
    """A multi-agent conversation with AutoGen."""

    model_client = OpenAIChatCompletionClient(
        model=OPENAI_MODEL,
        base_url=OPENAI_BASE_URL,
        api_key=OPENAI_API_KEY,
    )

    primary_agent = AssistantAgent(
        "primary",
        model_client=model_client,
        system_message="You are a helpful AI assistant.",
    )

    critic_agent = AssistantAgent(
        "critic",
        model_client=model_client,
        system_message="Provide constructive feedback. Respond with 'APPROVE' to when your feedbacks are addressed.",
    )

    text_termination = TextMentionTermination("APPROVE")

    # Create a team with the primary and critic agents.
    team = RoundRobinGroupChat([primary_agent, critic_agent], termination_condition=text_termination, max_turns=4)

    result = await team.run(task="Write a short poem about the fall season.")
    sources = [msg.source for msg in result.messages]
    assert "primary" in sources
    assert "critic" in sources


async def agent_autogen_mcp():
    """An AutoGen agent using the Multi-agent Conversation Platform (MCP) and a tool (fixed usage)."""
    calculator_mcp_server = StdioServerParams(command="uvx", args=["mcp-server-calculator"])

    async with McpWorkbench(calculator_mcp_server) as workbench:
        model_client = OpenAIChatCompletionClient(
            model=OPENAI_MODEL,
            base_url=OPENAI_BASE_URL,
            api_key=OPENAI_API_KEY,
        )
        agent = AssistantAgent(name="calc_agent", model_client=model_client, workbench=workbench)
        # Simulate a tool-use message
        response = await agent.run(task="What is 42 * 12?")
        assert "504" in response.messages[-1].content


def openai_agents_sdk_run_config():
    return RunConfig(
        model=OPENAI_MODEL,
        model_provider=OpenAIProvider(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL, use_responses=False),
    )


async def openai_agents_sdk_eval_hook_and_guardrail():
    class HomeworkOutput(BaseModel):
        is_homework: bool
        reasoning: str

    class EvalHook(AgentHooks):
        @reward
        def evaluate(self, context, agent, output):
            # Custom reward logic: reward if the answer contains 'homework'
            return 1.0 if output and "no" in str(output).lower() else 0.0

        async def on_end(self, context, agent, output):
            nonlocal final_reward
            final_reward = final_reward or self.evaluate(context, agent, output)

    guardrail_agent = Agent(
        name="Guardrail check",
        instructions="Check if the user is asking about homework.",
        output_type=HomeworkOutput,
        hooks=EvalHook(),
    )

    async def homework_guardrail(ctx, agent, input_data):
        result = await Runner.run(
            guardrail_agent, input_data, context=ctx.context, run_config=openai_agents_sdk_run_config()
        )
        final_output = result.final_output_as(HomeworkOutput)
        return GuardrailFunctionOutput(
            output_info=final_output,
            tripwire_triggered=not final_output.is_homework,
        )

    main_agent = Agent(
        name="Main Agent",
        instructions="Answer questions. If it's about homework, say so.",
        input_guardrails=[InputGuardrail(guardrail_function=homework_guardrail)],
        hooks=EvalHook(),
    )
    final_reward = None
    result = await Runner.run(
        main_agent,
        "The teacher asks to answer whether hummingbirds are mammals.",
        run_config=openai_agents_sdk_run_config(),
    )
    # Should trigger the guardrail and reward should be 1.0
    assert final_reward == 1.0, f"Expected reward to be 1.0, got {final_reward}"
    assert hasattr(result, "final_output")


async def openai_agents_sdk_mcp_tool_use():
    async with MCPServerStdio(params={"command": "uvx", "args": ["mcp-server-calculator"]}) as mcp_server:
        agent = Agent(
            name="MCP Tool Agent",
            instructions="Use the tools to answer the question.",
            mcp_servers=[mcp_server],
        )
        # The actual tool list and invocation will depend on the MCP server implementation
        # Here we just check that the agent can run with the MCP server attached
        result = await Runner.run(agent, "What is 43*57?", run_config=openai_agents_sdk_run_config())
        assert hasattr(result, "final_output")
        assert "2451" in result.final_output_as(str)


async def openai_agents_sdk_handoff_tool_output_type_and_reward():

    class MathOutput(BaseModel):
        answer: int

    @function_tool
    def add(a: int, b: int) -> int:
        return a + b

    class RewardHook(AgentHooks):
        @reward
        async def evaluate(self, context, agent, output):
            # Use another agent to check the answer and compute reward
            checker = Agent(
                name="Checker",
                instructions="Return 1.0 if the answer is 8, else 0.0.",
                output_type=float,
            )
            result = await Runner.run(
                checker, str(getattr(output, "answer", "")), run_config=openai_agents_sdk_run_config()
            )
            return float(result.final_output)

        async def on_end(self, context, agent, output):
            nonlocal final_reward
            final_reward = await self.evaluate(context, agent, output)

    math_agent = Agent(
        name="MathAgent",
        instructions="Add two numbers.",
        tools=[add],
        output_type=MathOutput,
        hooks=RewardHook(),
    )

    history_agent = Agent(
        name="HistoryAgent",
        instructions="Answer history questions.",
        output_type=str,
    )

    triage_agent = Agent(
        name="TriageAgent",
        instructions="If the question is about math, handoff to MathAgent. Otherwise, handoff to HistoryAgent.",
        handoffs=[math_agent, history_agent],
    )

    # Math handoff
    final_reward = None
    result = await Runner.run(triage_agent, "What is 3+5?", run_config=openai_agents_sdk_run_config())
    assert isinstance(result.final_output, MathOutput)
    assert result.final_output.answer == 8
    # The reward should be 1.0 (computed by the checker agent)
    assert final_reward == 1.0
    # History handoff
    result2 = await Runner.run(
        triage_agent, "Who was the first president of the US?", run_config=openai_agents_sdk_run_config()
    )
    assert isinstance(result2.final_output, str)
    assert "president" in result2.final_output.lower()


AGENTOPS_EXPECTED_TREES = {
    "agent_pure_openai": [("openai.chat.completion", "openai.chat.completion")],
    "agent_litellm": [("openai.chat.completion", "openai.chat.completion")],
    "agent_langchain": [("openai.chat.completion", "openai.chat.completion")],
    "agent_langchain_tooluse": [
        ("chat_model.llm", "openai.chat.completion"),
        ("chat_model.llm", "openai.chat.completion"),
    ],
    "agent_langgraph": [
        ("call_get_schema", "openai.chat.completion"),
        ("generate_query", "openai.chat.completion"),
        ("check_query", "openai.chat.completion"),
        ("run_query", "tool.tool"),
    ],
    "agent_autogen_multiagent": [
        ("primary", "openai.chat.completion"),
        ("critic", "openai.chat.completion"),
    ],
    "agent_autogen_mcp": [
        ("calc_agent", "openai.chat.completion"),
    ],
    "openai_agents_sdk_eval_hook_and_guardrail": [
        ("homework_guardrail", "openai.chat.completion"),
        ("Main Agent", "openai.chat.completion"),
        ("Main Agent", "agentops_reward_operation.task"),
    ],
    "openai_agents_sdk_mcp_tool_use": [
        ("MCP Tool Agent", "openai.chat.completion"),
        ("MCP Tool Agent", "calculate"),
        ("MCP Tool Agent", "openai.chat.completion"),
    ],
    "openai_agents_sdk_handoff_tool_output_type_and_reward": [
        ("TriageAgent", "openai.chat.completion"),
        ("MathAgent", "openai.chat.completion"),
        ("MathAgent", "openai.chat.completion"),
        ("MathAgent", "agentops_reward_operation.task"),
        ("HistoryAgent", "openai.chat.completion"),
    ],
}

AGENTOPS_EXPECTED_TRIPLETS_NUMBER = {
    "agent_pure_openai": 1,
    "agent_litellm": 1,
    "agent_langchain": 1,
    "agent_langchain_tooluse": 2,
    "agent_langgraph": 4,
    "agent_autogen_multiagent": 4,
    "agent_autogen_mcp": 1,
    "openai_agents_sdk_eval_hook_and_guardrail": 2,
    "openai_agents_sdk_mcp_tool_use": 2,
    "openai_agents_sdk_handoff_tool_output_type_and_reward": 5,
}

AGENTOPS_EXPECTED_REWARDS = {
    "openai_agents_sdk_eval_hook_and_guardrail": ([1.0, None], [None, 1.0]),
    "openai_agents_sdk_handoff_tool_output_type_and_reward": [None, None, 1.0, None, None],
}


def assert_expected_pairs_in_tree(root_tuple, expected_pairs):
    """
    Assert that every (ancestor_name, child_name) pair in `expected_pairs`
    occurs somewhere in the tree produced by TraceTree.names_tuple().
    """

    # Collect every node's full path from root → node
    paths = []  # e.g. [["root", "A", "B"], …]

    def _collect(node_tuple, prefix):
        name, children = node_tuple
        cur_path = prefix + [name]
        paths.append(cur_path)
        for child in children:
            _collect(child, cur_path)

    _collect(root_tuple, [])

    # Greedy—but safe—matching of each expected pair
    used_child_paths: set[tuple] = set()

    for anc_name, child_name in expected_pairs:
        matched = False
        for p in paths:
            if child_name not in p[-1] or tuple(p) in used_child_paths:
                continue
            if any(anc_name in pv for pv in p[:-1]):  # ancestor appears anywhere above
                used_child_paths.add(tuple(p))
                matched = True
                break
        if not matched:
            raise AssertionError(
                f"Expected ancestor/child pair ({anc_name!r}, {child_name!r}) "
                "not found or child already matched.\n"
                f"Root tuple: {pprint.pformat(root_tuple)}\n",
                f"Expected pairs: {expected_pairs}",
            )


def iterate_over_agents():
    yield from [
        agent_pure_openai,
        agent_litellm,
        agent_langchain,
        agent_langchain_tooluse,
        agent_langgraph,
        agent_autogen_multiagent,
        agent_autogen_mcp,
        openai_agents_sdk_eval_hook_and_guardrail,
        openai_agents_sdk_mcp_tool_use,
        openai_agents_sdk_handoff_tool_output_type_and_reward,
    ]


def run_one(agent_func):
    asyncio.get_event_loop().run_until_complete(run_agent(agent_func))


def run_all():
    for agent_func in iterate_over_agents():
        run_one(agent_func)


def run_with_agentops_tracer():
    tracer = AgentOpsTracer()
    tracer.init()
    tracer.init_worker(0)
    from agentlightning.tracer.triplet import TraceTree

    global _langchain_callback_handler
    _langchain_callback_handler = tracer.get_langchain_callback_handler()

    for agent_func in iterate_over_agents():
        tracer.trace_run(
            run_one,
            agent_func,
        )
        tree = TraceTree.from_spans(tracer.get_last_trace())
        # for span in tree.traverse():
        #     print(span.span.__dict__)
        tree.repair_hierarchy()
        tree.visualize(f"debug/{agent_func.__name__}")

        assert_expected_pairs_in_tree(tree.names_tuple(), AGENTOPS_EXPECTED_TREES[agent_func.__name__])

        # for triplet in TripletExporter().export(tracer.get_last_trace()):
        #     print(triplet)
        triplets = TripletExporter().export(tracer.get_last_trace())
        assert (
            len(triplets) == AGENTOPS_EXPECTED_TRIPLETS_NUMBER[agent_func.__name__]
        ), f"Expected {AGENTOPS_EXPECTED_TRIPLETS_NUMBER[agent_func.__name__]} triplets, but got: {triplets}"
        if agent_func.__name__ in AGENTOPS_EXPECTED_REWARDS:
            if isinstance(AGENTOPS_EXPECTED_REWARDS[agent_func.__name__], tuple):
                # If the expected rewards are a tuple, make sure at least one of them matches
                assert any(
                    [
                        r.reward in expected
                        for r in triplets
                        for expected in AGENTOPS_EXPECTED_REWARDS[agent_func.__name__]
                    ]
                ), (
                    f"Expected rewards {AGENTOPS_EXPECTED_REWARDS[agent_func.__name__]}, "
                    f"but got: {pprint.pformat(triplets)}"
                )
            else:
                assert [r.reward for r in triplets] == AGENTOPS_EXPECTED_REWARDS[agent_func.__name__], (
                    f"Expected rewards {AGENTOPS_EXPECTED_REWARDS[agent_func.__name__]}, "
                    f"but got: {pprint.pformat(triplets)}"
                )

    _langchain_callback_handler = None

    tracer.teardown_worker(0)
    tracer.teardown()


def run_with_http_tracer():
    import httpdbg.hooks.all

    @contextmanager
    def empty_hook(*args, **kwargs):
        yield

    httpdbg.hooks.all.hook_fastapi = empty_hook
    httpdbg.hooks.all.hook_uvicorn = empty_hook

    tracer = HttpTracer()
    tracer.init()
    tracer.init_worker(0)

    for agent_func in iterate_over_agents():
        print(agent_func)
        if "mcp" in agent_func.__name__ or "openai_agents_sdk" in agent_func.__name__:
            # FIXME: MCP server is not yet supported with HTTP tracer
            continue
        tracer.trace_run(
            run_one,
            agent_func,
        )

        print(tracer.get_last_trace())

    tracer.teardown_worker(0)
    tracer.teardown()


def create_prompt_caches():
    """Create prompt caches for the agent frameworks.
    This should only be run once to populate the caches.
    """

    if USE_OPENAI:
        tracer = HttpTracer()
        with tracer.trace_context():
            run_all()

        with open(os.path.join(os.path.dirname(__file__), "assets/prompt_caches.jsonl"), "w") as f:
            for span in tracer._last_records.requests.values():
                if span.url.startswith(OPENAI_BASE_URL) and span.status_code < 400 and span.response.content:
                    f.write(
                        json.dumps(
                            {
                                "request": json.loads(span.request.content.decode()),
                                "response": json.loads(span.response.content.decode()),
                            }
                        )
                        + "\n"
                    )

    else:
        run_all()


@pytest.mark.parametrize("agent_func", list(iterate_over_agents()), ids=lambda f: f.__name__)
def test_run_with_agentops_tracer(agent_func):
    tracer = AgentOpsTracer()
    tracer.init()
    tracer.init_worker(0)

    global _langchain_callback_handler
    _langchain_callback_handler = tracer.get_langchain_callback_handler()

    try:
        tracer.trace_run(
            run_one,
            agent_func,
        )
        tree = TraceTree.from_spans(tracer.get_last_trace())

        tree.repair_hierarchy()

        assert_expected_pairs_in_tree(tree.names_tuple(), AGENTOPS_EXPECTED_TREES[agent_func.__name__])

        triplets = TripletExporter().export(tracer.get_last_trace())
        assert (
            len(triplets) == AGENTOPS_EXPECTED_TRIPLETS_NUMBER[agent_func.__name__]
        ), f"Expected {AGENTOPS_EXPECTED_TRIPLETS_NUMBER[agent_func.__name__]} triplets, but got: {triplets}"
        if agent_func.__name__ in AGENTOPS_EXPECTED_REWARDS:
            if isinstance(AGENTOPS_EXPECTED_REWARDS[agent_func.__name__], tuple):
                # If the expected rewards are a tuple, make sure at least one of them matches
                assert any(
                    [
                        r.reward in expected
                        for r in triplets
                        for expected in AGENTOPS_EXPECTED_REWARDS[agent_func.__name__]
                    ]
                ), (
                    f"Expected rewards {AGENTOPS_EXPECTED_REWARDS[agent_func.__name__]}, "
                    f"but got: {pprint.pformat(triplets)}"
                )
            else:
                assert [r.reward for r in triplets] == AGENTOPS_EXPECTED_REWARDS[agent_func.__name__], (
                    f"Expected rewards {AGENTOPS_EXPECTED_REWARDS[agent_func.__name__]}, "
                    f"but got: {pprint.pformat(triplets)}"
                )

        _langchain_callback_handler = None

    finally:
        tracer.teardown_worker(0)
        tracer.teardown()


@pytest.mark.parametrize("agent_func", list(iterate_over_agents()), ids=lambda f: f.__name__)
def test_run_with_http_tracer(agent_func):
    pytest.skip("HTTP tracer tests are disabled for now due to issues on GitHub Actions.")

    import httpdbg.hooks.all

    @contextmanager
    def empty_hook(*args, **kwargs):
        yield

    httpdbg.hooks.all.hook_fastapi = empty_hook
    httpdbg.hooks.all.hook_uvicorn = empty_hook

    tracer = HttpTracer()
    tracer.init()
    tracer.init_worker(0)

    try:
        tracer.trace_run(
            run_one,
            agent_func,
        )
        assert len(tracer.get_last_trace()) > 0
    finally:
        tracer.teardown_worker(0)
        tracer.teardown()


def _debug_with_agentops():
    """This function is for debugging purposes only."""
    assert "AGENTOPS_API_KEY" in os.environ, "AGENTOPS_API_KEY is not set"
    from agentlightning.instrumentation.agentops_langchain import instrument_agentops_langchain

    instrument_agentops_langchain()
    agentops.init()
    from agentops.integration.callbacks.langchain import LangchainCallbackHandler

    global _langchain_callback_handler
    _langchain_callback_handler = LangchainCallbackHandler(api_key=os.environ["AGENTOPS_API_KEY"])
    for agent_func in [agent_langchain_tooluse]:
        run_one(agent_func)


if __name__ == "__main__":
    # run_with_agentops_tracer()
    run_with_http_tracer()
    # _debug_with_agentops()
