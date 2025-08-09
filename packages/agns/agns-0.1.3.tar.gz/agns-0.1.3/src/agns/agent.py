# src/aans_sdk/agent.py
from typing import Any, Dict
import requests
from .model.agent_card import AgentCard
from .a2a.a2a_agent_caller import A2AAgentCaller
from .mcp.mcp_agent_caller import MCPAgentCaller
from .agent_resolver import AgentResolver

# from pydantic_ai import Agent as PydanticAgent

class Agent:
    def __init__(self, card: AgentCard):
        # self.agent = PydanticAgent(**card.model_dump())
        self.card = card

    def ask(self, question: Dict[str, Any]) -> Dict[str, Any]:
        print(f"Asking agent {self.card.name} with type of {self.card.type} with question: {question}")
        agent_resolve = AgentResolver()
        (agent_card, tool_name) = agent_resolve.resolve(question, [self.card])
        if (self.card.type == AgentCard.TYPE_A2A):
            a2a_agent = A2AAgentCaller(agent_card)
            return a2a_agent.call(tool_name, question)
        if (self.card.type == AgentCard.TYPE_MCP):
            mcp_agent = MCPAgentCaller(agent_card)
            return mcp_agent.call(tool_name, question)
        response = requests.post(self.card.url, json=question)
        response.raise_for_status()
        return response.json()
    
    def invoke(self, verb: str, question: Dict[str, Any]) -> Dict[str, Any]:
        print(f"Performing verb '{verb}' on agent {self.card.name} with question: {question}")
        # Assuming the agent's URL can handle different verbs as part of the path or query
        # This is a placeholder; you might need to adjust the URL or request body
        # based on how your agent API is designed to handle different verbs.
        tool_name = verb # assume verb is the tool_name
        if (self.card.type == AgentCard.TYPE_A2A):
            a2a_agent = A2AAgentCaller(self.card)
            return a2a_agent.call(tool_name, question)
        if (self.card.type == AgentCard.TYPE_MCP):
            mcp_agent = MCPAgentCaller(self.card)
            return mcp_agent.call(tool_name, question)
        response = requests.post(f"{self.card.url}/{verb}", json=question)
        response.raise_for_status()
        return response.json()

    def describe(self) -> Dict[str, Any]:
        return self.card.model_dump()
