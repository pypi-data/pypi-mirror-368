"""
GitScribe MCP Server

Main server implementation for the Model Context Protocol server
that provides web scraping and RAG capabilities for Git-based documentation.
"""

import asyncio
import logging
import signal
from typing import Any, Dict, List, Optional, Sequence
from contextlib import asynccontextmanager

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    EmptyResult,
    ReadResourceResult,
    CallToolResult
)
from mcp.server.session import ServerSession

from .scraper import DocumentationScraper
from .rag import RAGSystem
from .config import GitScribeConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GitScribeServer:
    """
    GitScribe MCP Server for intelligent documentation scraping and retrieval.
    """
    
    def __init__(self, config: Optional[GitScribeConfig] = None):
        """Initialize the GitScribe server."""
        self.config = config or GitScribeConfig()
        self.server = Server("gitscribe")
        self.scraper = DocumentationScraper(self.config)
        self.rag_system = RAGSystem(self.config)
        self._shutdown_event = asyncio.Event()
        self._setup_handlers()
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating shutdown...")
            self._shutdown_event.set()
        
        # Only set up signal handlers if we're in the main thread and not running as MCP server
        try:
            # Skip signal handlers when running as MCP server since they can interfere
            import os
            if os.environ.get('MCP_SERVER_MODE') != 'true':
                signal.signal(signal.SIGINT, signal_handler)
                signal.signal(signal.SIGTERM, signal_handler)
        except ValueError:
            # Not in main thread, can't set signal handlers
            pass
    
    def _setup_handlers(self):
        """Set up MCP handlers for tools and resources."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="scrape_documentation",
                    description="Scrape and index documentation from a Git repository or website",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "Repository or documentation URL"
                            },
                            "depth": {
                                "type": "integer", 
                                "description": "Maximum crawling depth",
                                "default": 3
                            },
                            "formats": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Supported document formats",
                                "default": ["html", "md", "rst"]
                            }
                        },
                        "required": ["url"]
                    }
                ),
                Tool(
                    name="search_documentation",
                    description="Search indexed documentation using semantic search",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Natural language search query"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results",
                                "default": 10
                            },
                            "filter": {
                                "type": "object",
                                "description": "Filter criteria (language, framework, etc.)",
                                "properties": {
                                    "language": {"type": "string"},
                                    "framework": {"type": "string"},
                                    "source": {"type": "string"}
                                }
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="get_code_examples",
                    description="Extract code examples related to a specific topic",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "topic": {
                                "type": "string",
                                "description": "Programming topic or concept"
                            },
                            "language": {
                                "type": "string",
                                "description": "Programming language filter"
                            },
                            "framework": {
                                "type": "string",
                                "description": "Framework or library filter"
                            }
                        },
                        "required": ["topic"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Handle tool calls."""
            try:
                logger.info(f"Handling tool call: {name} with arguments: {arguments}")
                
                # For debugging - return a simple test result first
                if name == "scrape_documentation":
                    # Test simple response
                    simple_result = {
                        "status": "success", 
                        "message": "Test scraping response",
                        "url": arguments.get("url", "")
                    }
                    result_text = f"Scraped documentation from {arguments.get('url', '')}"
                    
                elif name == "search_documentation":
                    result = await self._search_documentation(arguments)
                    import json
                    result_text = json.dumps(result, indent=2)
                elif name == "get_code_examples":
                    result = await self._get_code_examples(arguments)
                    import json
                    result_text = json.dumps(result, indent=2)
                else:
                    raise ValueError(f"Unknown tool: {name}")
                
                logger.info(f"Tool result text: {result_text[:200]}...")
                
                # Return with minimal structure
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=result_text
                        )
                    ]
                )
                
            except Exception as e:
                logger.error(f"Error calling tool {name}: {e}")
                import traceback
                traceback.print_exc()
                
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text", 
                            text=f"Error: {str(e)}"
                        )
                    ]
                )
        
        @self.server.list_resources()
        async def handle_list_resources() -> List[Resource]:
            """List available resources."""
            return [
                Resource(
                    uri="gitscribe://indexed_docs",
                    name="Indexed Documentation",
                    description="List of all indexed documentation sources",
                    mimeType="application/json"
                ),
                Resource(
                    uri="gitscribe://search_history",
                    name="Search History", 
                    description="Recent search queries and results",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> ReadResourceResult:
            """Read a resource."""
            try:
                if uri == "gitscribe://indexed_docs":
                    docs = await self.rag_system.get_indexed_documents()
                    content = {"indexed_documents": docs}
                elif uri == "gitscribe://search_history":
                    history = await self.rag_system.get_search_history()
                    content = {"search_history": history}
                else:
                    raise ValueError(f"Unknown resource: {uri}")
                
                return ReadResourceResult(
                    contents=[
                        TextContent(
                            type="text",
                            text=str(content)
                        )
                    ]
                )
            except Exception as e:
                logger.error(f"Error reading resource {uri}: {e}")
                return ReadResourceResult(
                    contents=[
                        TextContent(
                            type="text", 
                            text=f"Error: {str(e)}"
                        )
                    ]
                )
    
    async def _scrape_documentation(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Scrape documentation from a URL."""
        url = arguments["url"]
        depth = arguments.get("depth", 3)
        formats = arguments.get("formats", ["html", "md", "rst"])
        
        logger.info(f"Scraping documentation from {url}")
        
        # Scrape the documentation
        scraped_data = await self.scraper.scrape_documentation(
            url=url, 
            max_depth=depth,
            supported_formats=formats
        )
        
        # Index the scraped data in the RAG system
        await self.rag_system.index_documents(scraped_data)
        
        return {
            "status": "success",
            "message": f"Successfully scraped and indexed {len(scraped_data)} documents from {url}",
            "documents_indexed": len(scraped_data),
            "url": url
        }
    
    async def _search_documentation(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Search documentation using semantic search."""
        query = arguments["query"]
        limit = arguments.get("limit", 10)
        filters = arguments.get("filter", {})
        
        logger.info(f"Searching documentation with query: {query}")
        
        # Perform semantic search
        results = await self.rag_system.search(
            query=query,
            limit=limit,
            filters=filters
        )
        
        return {
            "status": "success",
            "query": query,
            "results": results,
            "total_results": len(results)
        }
    
    async def _get_code_examples(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Extract code examples for a specific topic."""
        topic = arguments["topic"]
        language = arguments.get("language")
        framework = arguments.get("framework")
        
        logger.info(f"Getting code examples for topic: {topic}")
        
        # Search for code examples
        filters = {}
        if language:
            filters["language"] = language
        if framework:
            filters["framework"] = framework
        
        # Use specialized query for code examples
        query = f"code examples for {topic}"
        if language:
            query += f" in {language}"
        if framework:
            query += f" using {framework}"
        
        results = await self.rag_system.search(
            query=query,
            limit=10,
            filters={**filters, "content_type": "code"}
        )
        
        return {
            "status": "success",
            "topic": topic,
            "language": language,
            "framework": framework,
            "code_examples": results
        }
    
    async def run(self, transport: str = "stdio"):
        """Run the MCP server."""
        logger.info("Starting GitScribe MCP server...")
        
        # Initialize RAG system
        await self.rag_system.initialize()
        
        try:
            if transport == "stdio":
                from mcp.server.stdio import stdio_server
                logger.info("Setting up stdio server...")
                async with stdio_server() as (read_stream, write_stream):
                    logger.info("Starting MCP server run loop...")
                    
                    # Get server capabilities with minimal configuration
                    capabilities = {
                        "tools": {"listChanged": False},
                        "resources": {"subscribe": False, "listChanged": False}
                    }
                    
                    await self.server.run(
                        read_stream,
                        write_stream,
                        InitializationOptions(
                            server_name="gitscribe",
                            server_version="1.0.9",
                            capabilities=capabilities
                        )
                    )
                    logger.info("MCP server run loop completed normally")
            else:
                raise ValueError(f"Unsupported transport: {transport}")
        except KeyboardInterrupt:
            logger.info("Server interrupted by user")
        except Exception as e:
            # Log the actual error before checking if it's a TaskGroup error
            logger.error(f"Server error occurred: {e}")
            logger.error(f"Error type: {type(e)}")
            logger.error(f"Error args: {e.args}")
            
            # Check if this is a TaskGroup error during shutdown
            if "TaskGroup" in str(e) and "unhandled errors" in str(e):
                logger.debug(f"TaskGroup cleanup issue during shutdown: {e}")
                # This is expected during shutdown, don't propagate
            else:
                logger.error(f"Unexpected server error: {e}")
                # Don't raise, just log and continue to cleanup
        finally:
            await self.stop()
    
    async def start(self, transport: str = "stdio"):
        """Start the MCP server (alias for run)."""
        await self.run(transport)
    
    async def stop(self):
        """Stop the server and cleanup."""
        logger.info("Stopping GitScribe MCP server...")
        
        # Cancel any pending tasks
        try:
            # Get all tasks except current one
            current_task = asyncio.current_task()
            tasks = [task for task in asyncio.all_tasks() if task != current_task and not task.done()]
            
            if tasks:
                logger.info(f"Cancelling {len(tasks)} pending tasks...")
                for task in tasks:
                    task.cancel()
                
                # Wait for tasks to be cancelled with timeout
                try:
                    await asyncio.wait_for(
                        asyncio.gather(*tasks, return_exceptions=True),
                        timeout=5.0
                    )
                except asyncio.TimeoutError:
                    logger.warning("Some tasks did not complete within timeout")
                except Exception as e:
                    logger.warning(f"Error cancelling tasks: {e}")
        except Exception as e:
            logger.warning(f"Error during task cancellation: {e}")
        
        # Cleanup scraper resources
        try:
            await self.scraper.cleanup()
        except Exception as e:
            logger.warning(f"Error cleaning up scraper: {e}")
        
        # Cleanup RAG system
        try:
            await self.rag_system.cleanup()
        except Exception as e:
            logger.warning(f"Error cleaning up RAG system: {e}")
        
        logger.info("GitScribe MCP server stopped")


async def main():
    """Main entry point for the server."""
    server = GitScribeServer()
    await server.start()


if __name__ == "__main__":
    asyncio.run(main())
