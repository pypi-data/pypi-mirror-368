from typing import List, Union, Any
from langchain_core.tools import BaseTool
from pathlib import Path
from vinagent.agent.agent import Agent

class AgentGroup():
    def __init__(self,
        name: str = "", 
        agents: dict[Agent] = [],
        description: str = "You are a helpful assistant who can use the following tools to complete a task.",
        background: list[str] = ["You can answer the user question with tools"],
        memory_path: Path = None,
        is_reset_memory: bool = False,
        num_buffered_messages: int = 10
    ):
        self.name = name
        self.agents = agents
        self.description = description
        self.background = background
        self.memory_path = memory_path
        self.is_reset_memory = is_reset_memory
        self.num_buffered_messages = num_buffered_messages

    def launch(self):
        # Step 1: Initialize agents

    def invoke(self, query: str) -> str:
        # Step 1: Ask supervisor Agent -> Next Agent.
        # Step 2: Ask the next agent. -> Return message to Supervior Agent.
        # Step 3: Pass message back to the supervior Agent
