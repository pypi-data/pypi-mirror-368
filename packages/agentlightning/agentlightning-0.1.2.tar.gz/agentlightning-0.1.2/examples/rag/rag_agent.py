from __future__ import annotations

import os
import re
import shutil
import sys
import tempfile
import time
from typing import Any, Literal, Optional

import dotenv
import termcolor
from agents import (
    Agent,
    Runner,
    function_tool,
    gen_trace_id,
    set_trace_processors,
    set_tracing_disabled,
    trace,
)
from agents.extensions.models.litellm_model import LitellmModel
from agents.mcp import MCPServer, MCPServerSse
from agents.model_settings import ModelSettings
from agents.tracing.processors import BatchTraceProcessor, ConsoleSpanExporter
from utils import compute_scores

import agentlightning
from agentlightning import (
    LLM,
    LitAgent,
    NamedResources,
    Trainer,
    configure_logger,
    reward,
)

configure_logger()

agent_prompt = """You are an assistant who answers questions using Wikipedia retriever. Answer the question using only the retrieved passages. Verify your answer directly against the text.

After each search:
- Summarize findings.
- Decide if info is sufficient.
  - If sufficient: reply in <answer>...</answer> with your answer. The answer must be extremely concise: a single word or a few words only.
  - If not: suggest the next search needed to fill info gaps. The system will return top 3 relevant Wikipedia chunks.
- Explain your reasoning for the chosen action.

Repeat as needed. When done, wrap your final, concise answer in <answer> tags."""


class RAGAgent(LitAgent):
    def __init__(self):
        self.mcp_server_url = "http://127.0.0.1:8099/sse"

    async def training_rollout_async(self, task: Any, rollout_id: str, resources: NamedResources) -> Any:
        llm: LLM = resources.get("main_llm")
        print("Training with model:", llm.model, "on endpoint:", llm.endpoint)
        async with MCPServerSse(
            name="wiki_retriever_mcp",
            params={"url": self.mcp_server_url},
        ) as server:
            agent = Agent(
                model=LitellmModel(model="hosted_vllm/" + llm.model, base_url=llm.endpoint),
                model_settings=ModelSettings(
                    max_tokens=4096,
                    temperature=0.7,
                ),
                name="Assistant",
                instructions=agent_prompt,
                mcp_servers=[server],
            )
            result = await Runner.run(agent, task["question"])
            answer = result.final_output
            reward = compute_scores(answer, str(task["answer"]))
            print(
                "question:{} answer: {} ground_truth: {} reward: {}".format(
                    task["question"], answer, task["answer"], reward
                )
            )
            return reward

    async def validation_rollout_async(self, task: Any, rollout_id: str, resources: NamedResources) -> Any:
        llm: LLM = resources.get("main_llm")
        resources = {
            "main_llm": LLM(
                endpoint=llm.endpoint,
                model=llm.model,
                sampling_parameters={"temperature": 0.7},
            )
        }
        return await self.training_rollout_async(task, rollout_id, resources)


if __name__ == "__main__":
    Trainer(n_workers=12).fit(RAGAgent(), "http://localhost:9999/")
