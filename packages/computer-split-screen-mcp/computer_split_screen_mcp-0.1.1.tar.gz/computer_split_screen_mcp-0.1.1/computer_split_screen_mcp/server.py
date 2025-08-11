"""Model Context Protocol (MCP) server for window management."""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

from mcp import ClientSession, StdioServerParameters
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
)

from .window_manager import (
    minimize_active_window,
    toggle_fullscreen,
    relocate_to_top_half,
    relocate_to_bottom_half,
    relocate_to_left_half,
    relocate_to_right_half,
    move_to_top_left_quadrant,
    move_to_top_right_quadrant,
    move_to_bottom_left_quadrant,
    move_to_bottom_right_quadrant,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WindowManagementMCPServer:
    """MCP server for cross-platform window management operations."""

    def __init__(self):
        """Initialize the MCP server."""
        self.server = Server("window-management")
        self._setup_handlers()

    def _setup_handlers(self):
        """Set up MCP server handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """List available window management tools."""
            tools = [
                Tool(
                    name="minimize_window",
                    description="Minimize the currently active window",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="toggle_fullscreen",
                    description="Toggle fullscreen mode for the active window",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="move_to_top_half",
                    description="Move the active window to the top half of the screen",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="move_to_bottom_half",
                    description="Move the active window to the bottom half of the screen",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="move_to_left_half",
                    description="Move the active window to the left half of the screen",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="move_to_right_half",
                    description="Move the active window to the right half of the screen",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="move_to_top_left_quadrant",
                    description="Move the active window to the top-left quadrant of the screen",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="move_to_top_right_quadrant",
                    description="Move the active window to the top-right quadrant of the screen",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="move_to_bottom_left_quadrant",
                    description="Move the active window to the bottom-left quadrant of the screen",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="move_to_bottom_right_quadrant",
                    description="Move the active window to the bottom-right quadrant of the screen",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
            ]
            return ListToolsResult(tools=tools)

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Handle tool calls for window management operations."""
            try:
                result = None
                content = []
                
                if name == "minimize_window":
                    success = minimize_active_window()
                    result = {"success": success}
                    content.append({
                        "type": "text",
                        "text": f"Window minimize operation {'succeeded' if success else 'failed'}"
                    })
                
                elif name == "toggle_fullscreen":
                    success = toggle_fullscreen()
                    result = {"success": success}
                    content.append({
                        "type": "text",
                        "text": f"Fullscreen toggle operation {'succeeded' if success else 'failed'}"
                    })
                
                elif name == "move_to_top_half":
                    success = relocate_to_top_half()
                    result = {"success": success}
                    content.append({
                        "type": "text",
                        "text": f"Move to top half operation {'succeeded' if success else 'failed'}"
                    })
                
                elif name == "move_to_bottom_half":
                    success = relocate_to_bottom_half()
                    result = {"success": success}
                    content.append({
                        "type": "text",
                        "text": f"Move to bottom half operation {'succeeded' if success else 'failed'}"
                    })
                
                elif name == "move_to_left_half":
                    success = relocate_to_left_half()
                    result = {"success": success}
                    content.append({
                        "type": "text",
                        "text": f"Move to left half operation {'succeeded' if success else 'failed'}"
                    })
                
                elif name == "move_to_right_half":
                    success = relocate_to_right_half()
                    result = {"success": success}
                    content.append({
                        "type": "text",
                        "text": f"Move to right half operation {'succeeded' if success else 'failed'}"
                    })
                
                elif name == "move_to_top_left_quadrant":
                    success = move_to_top_left_quadrant()
                    result = {"success": success}
                    content.append({
                        "type": "text",
                        "text": f"Move to top-left quadrant operation {'succeeded' if success else 'failed'}"
                    })
                
                elif name == "move_to_top_right_quadrant":
                    success = move_to_top_right_quadrant()
                    result = {"success": success}
                    content.append({
                        "type": "text",
                        "text": f"Move to top-right quadrant operation {'succeeded' if success else 'failed'}"
                    })
                
                elif name == "move_to_bottom_left_quadrant":
                    success = move_to_bottom_left_quadrant()
                    result = {"success": success}
                    content.append({
                        "type": "text",
                        "text": f"Move to bottom-left quadrant operation {'succeeded' if success else 'failed'}"
                    })
                
                elif name == "move_to_bottom_right_quadrant":
                    success = move_to_bottom_right_quadrant()
                    result = {"success": success}
                    content.append({
                        "type": "text",
                        "text": f"Move to bottom-right quadrant operation {'succeeded' if success else 'failed'}"
                    })
                
                else:
                    raise ValueError(f"Unknown tool: {name}")
                
                return CallToolResult(
                    content=content,
                    isError=False,
                    result=result
                )
                
            except Exception as e:
                logger.error(f"Error executing tool {name}: {e}")
                return CallToolResult(
                    content=[{
                        "type": "text",
                        "text": f"Error executing {name}: {str(e)}"
                    }],
                    isError=True
                )

    async def run(self):
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="window-management",
                    server_version="0.1.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities=None,
                    ),
                ),
            )


async def main():
    """Main entry point for the MCP server."""
    server = WindowManagementMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
