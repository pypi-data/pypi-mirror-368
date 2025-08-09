import asyncio
import os
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

# Replace with your actual MCP server URL
MCP_SERVER_URL = "http://localhost:8000/mcp"

async def main():
    async with streamablehttp_client(MCP_SERVER_URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("Available tools:")
            for tool in tools.tools:
                print(f"- {tool.name}: {tool.description}")
            
            # Call the 'add' tool
            result = await session.call_tool("add", {"a": 2, "b": 3})
            print(f"add(2, 3) result: {result.structuredContent if hasattr(result, 'structuredContent') else result}")

if __name__ == "__main__":
    asyncio.run(main())
