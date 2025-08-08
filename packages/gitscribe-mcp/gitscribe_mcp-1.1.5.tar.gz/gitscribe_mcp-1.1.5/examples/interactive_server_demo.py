#!/usr/bin/env python3
"""
Interactive GitScribe MCP Server Demo
Shows how to interact with the MCP server programmatically.
"""

import asyncio
import json
import logging
from gitscribe.server import GitScribeServer
from gitscribe.config import GitScribeConfig
from gitscribe.utils import setup_logging


async def interactive_server_demo():
    """Demonstrate interactive server usage."""
    
    config = GitScribeConfig()
    setup_logging(debug=True)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting GitScribe MCP Server Demo")
    
    # Initialize server
    server = GitScribeServer(config)
    
    # Initialize components
    await server.rag_system.initialize()
    
    print("\n" + "="*50)
    print("GitScribe MCP Server - Interactive Demo")
    print("="*50)
    
    # Simulate tool calls
    tools = [
        {
            "name": "scrape_documentation",
            "args": {
                "url": "https://docs.python.org/3/tutorial/",
                "max_depth": 2
            }
        },
        {
            "name": "search_documentation", 
            "args": {
                "query": "async await python",
                "limit": 3
            }
        }
    ]
    
    try:
        for i, tool in enumerate(tools, 1):
            print(f"\n--- Tool Call {i}: {tool['name']} ---")
            print(f"Arguments: {json.dumps(tool['args'], indent=2)}")
            
            # Simulate MCP tool calls by calling server methods directly
            try:
                if tool['name'] == 'scrape_documentation':
                    result = await server._scrape_documentation(tool['args'])
                elif tool['name'] == 'search_documentation':
                    result = await server._search_documentation(tool['args'])
                else:
                    result = {"error": f"Unknown tool: {tool['name']}"}
                
                print(f"Result: {json.dumps(result, indent=2)[:300]}...")
            except Exception as e:
                print(f"Error: {e}")
            
            print("-" * 40)
        
        # Keep server running for a while
        print(f"\nServer components initialized and ready...")
        print("In a real MCP setup, this would wait for client connections")
        print("Press Ctrl+C to stop")
        
        await asyncio.sleep(30)  # Run for 30 seconds
        
    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        await server.stop()


if __name__ == "__main__":
    asyncio.run(interactive_server_demo())
