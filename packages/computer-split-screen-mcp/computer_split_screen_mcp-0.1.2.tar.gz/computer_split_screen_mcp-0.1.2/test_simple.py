#!/usr/bin/env python3
"""Simple test script to isolate the MCP server issue."""

import asyncio
import sys
from computer_split_screen_mcp.server import WindowManagementMCPServer

async def test_server():
    """Test the MCP server."""
    try:
        print("Creating MCP server...")
        server = WindowManagementMCPServer()
        print("MCP server created successfully!")
        print("Server object:", server)
        return True
    except Exception as e:
        print(f"Error creating server: {e}")
        return False

def main():
    """Main function."""
    try:
        print("Testing MCP server...")
        result = asyncio.run(test_server())
        if result:
            print("✅ Test passed!")
        else:
            print("❌ Test failed!")
        return 0
    except Exception as e:
        print(f"❌ Error in main: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
