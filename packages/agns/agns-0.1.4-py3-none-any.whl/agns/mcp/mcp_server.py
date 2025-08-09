from mcp.server.fastmcp import FastMCP

# Create a FastMCP server instance
mcp = FastMCP("Quickstart Server")

# Add a simple tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool()
def hello(name: str = "World") -> str:
    """Say hello to someone."""
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
