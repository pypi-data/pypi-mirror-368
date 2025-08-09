import asyncio
import os
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from ..model.agent_card import AgentCard

class MCPAgentCaller:
    def __init__(self, agent_card: AgentCard):
        self.agent_card = agent_card

    async def call(self, tool_name: str, arguments: dict = None) -> dict:
        async with streamablehttp_client(self.agent_card.url) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()    

                result = await session.call_tool(tool_name, arguments)
                print(f"{tool_name, arguments}, result: {result.structuredContent if hasattr(result, 'structuredContent') else result}")
                return result