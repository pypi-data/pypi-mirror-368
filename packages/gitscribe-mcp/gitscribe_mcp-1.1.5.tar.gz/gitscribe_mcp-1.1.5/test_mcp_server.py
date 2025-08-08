#!/usr/bin/env python3
"""
Simple test script to debug MCP server startup issues.
"""

import asyncio
import logging
import sys
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.server.models import InitializationOptions

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_server():
    """Test basic MCP server functionality."""
    logger.info("Starting test MCP server...")
    
    server = Server("test-server")
    
    @server.list_tools()
    async def handle_list_tools():
        """List available tools."""
        from mcp.types import Tool
        return [
            Tool(
                name="test_tool",
                description="A simple test tool",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "Test message"
                        }
                    },
                    "required": ["message"]
                }
            )
        ]
    
    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict):
        """Handle tool calls."""
        from mcp.types import CallToolResult, TextContent
        if name == "test_tool":
            message = arguments.get("message", "Hello!")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Test response: {message}")]
            )
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    try:
        logger.info("Setting up stdio server...")
        async with stdio_server() as (read_stream, write_stream):
            logger.info("Running server with stdio transport...")
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="test-server",
                    server_version="1.0.0",
                    capabilities=server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities={}
                    )
                )
            )
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise
    finally:
        logger.info("Server shutting down...")

if __name__ == "__main__":
    try:
        asyncio.run(test_server())
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server failed: {e}")
        sys.exit(1)
