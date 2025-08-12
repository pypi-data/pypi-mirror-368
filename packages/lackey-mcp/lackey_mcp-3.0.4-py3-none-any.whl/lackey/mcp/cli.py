#!/usr/bin/env python3
"""CLI for running the Lackey MCP server."""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

from .server import LackeyMCPServer


def setup_logging(level: str = "INFO") -> None:
    """Set up logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stderr)],
    )


async def main() -> None:
    """Run the MCP server CLI."""
    parser = argparse.ArgumentParser(
        description="Lackey MCP Server - Task chain management via MCP protocol"
    )
    parser.add_argument(
        "--workspace",
        "-w",
        default=".lackey",
        help="Workspace directory for Lackey data (default: .lackey)",
    )
    parser.add_argument(
        "--log-level",
        "-l",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)",
    )

    args = parser.parse_args()

    # Set up logging
    setup_logging(args.log_level)

    # Create workspace directory if it doesn't exist
    workspace_path = Path(args.workspace)
    workspace_path.mkdir(parents=True, exist_ok=True)

    # Initialize and run the server
    server = LackeyMCPServer(str(workspace_path))

    try:
        await server.run()
    except KeyboardInterrupt:
        logging.info("Received interrupt signal, shutting down...")
        await server.stop()
    except Exception as e:
        logging.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
