"""Main entry point for the computer-split-screen-mcp package."""

import asyncio
import sys
from .server import main


def run_server():
    """Synchronous entry point for uvx compatibility."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_server()
