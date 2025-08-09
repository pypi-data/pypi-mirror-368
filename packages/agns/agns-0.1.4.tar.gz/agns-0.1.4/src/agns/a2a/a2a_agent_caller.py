import httpx
from a2a.client import A2AClient
from a2a.types import AgentCard as A2AAgentCard
from ..model.agent_card import AgentCard

class A2AAgentCaller:
    def __init__(self, agent_card: A2AAgentCard):
        self.agent_card = agent_card
    
    async def call(self, tool_name: str, arguments: dict = None) -> dict:
        """Call a specific tool on the agent with given arguments."""
        async with httpx.AsyncClient() as http_client:
            try:
                # Initialize A2AClient
                client = A2AClient(self.agent_card.url, http_client=http_client)
                
                # Verify tool exists in AgentCard
                skill_ids = [skill.id for skill in self.agent_card.skills]
                if tool_name not in skill_ids:
                    raise ValueError(f"Tool '{tool_name}' not found. Available tools: {skill_ids} for agent: {self.agent_card.name}")
                
                # Call the tool with arguments (default to empty dict if None)
                response = await client.call_tool(tool_name=tool_name, arguments=arguments or {})
                return response
            except Exception as e:
                raise Exception(f"Error calling tool '{tool_name} for agent: {self.agent_card.name}': {e}")