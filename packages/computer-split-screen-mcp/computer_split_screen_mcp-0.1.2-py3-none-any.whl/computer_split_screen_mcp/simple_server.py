"""Minimal MCP server for testing."""

import asyncio
import sys
from mcp import Server
from mcp.server.stdio import stdio_server
from mcp.server.models import InitializationOptions


def create_minimal_server():
    """Create a minimal MCP server."""
    server = Server("window-management")
    
    @server.list_tools()
    async def handle_list_tools():
        from mcp.types import ListToolsResult, Tool
        return ListToolsResult(tools=[
            Tool(
                name="test_tool",
                description="A test tool",
                inputSchema={"type": "object", "properties": {}, "required": []}
            )
        ])
    
    @server.call_tool()
    async def handle_call_tool(name: str, arguments):
        from mcp.types import CallToolResult
        return CallToolResult(
            content=[{"type": "text", "text": f"Tool {name} called successfully"}],
            isError=False
        )
    
    return server


async def run_minimal_server():
    """Run the minimal MCP server."""
    server = create_minimal_server()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="window-management",
                server_version="0.1.1",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                ),
            ),
        )


def main_sync():
    """Synchronous entry point."""
    try:
        asyncio.run(run_minimal_server())
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main_sync()
