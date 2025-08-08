"""
Example usage of GitScribe MCP Server.
"""

import asyncio
import logging
from gitscribe.server import GitScribeServer
from gitscribe.config import GitScribeConfig
from gitscribe.git_integration import GitIntegration
from gitscribe.utils import setup_logging


async def example_scrape_repository():
    """Example: Scrape a public repository's documentation."""
    
    # Setup
    config = GitScribeConfig()
    setup_logging(debug=True)
    logger = logging.getLogger(__name__)
    
    # Initialize Git integration
    git_integration = GitIntegration(config)
    
    # Parse a repository URL
    repo_url = "https://github.com/microsoft/vscode"
    repo = git_integration.parse_git_url(repo_url)
    
    if not repo:
        logger.error(f"Failed to parse repository URL: {repo_url}")
        return
    
    logger.info(f"Parsed repository: {repo.owner}/{repo.repo}")
    
    # Discover documentation structure
    structure = git_integration.discover_documentation_structure(repo)
    
    logger.info(f"Found {len(structure['documentation_files'])} documentation files")
    logger.info(f"Found {len(structure['readme_files'])} README files")
    logger.info(f"Found {len(structure['api_docs'])} API documentation files")
    
    # Download and process a few files
    for file_info in structure['readme_files'][:3]:
        logger.info(f"Processing: {file_info['path']}")
        content = git_integration.download_file_content(file_info)
        
        if content:
            logger.info(f"Downloaded {len(content)} characters from {file_info['path']}")
            # Here you would normally parse and index the content
        else:
            logger.warning(f"Failed to download {file_info['path']}")


async def example_mcp_server():
    """Example: Run the GitScribe MCP server."""
    
    config = GitScribeConfig()
    setup_logging(debug=True)
    
    server = GitScribeServer(config)
    
    print("Starting GitScribe MCP Server...")
    print("Use this server with any MCP-compatible client.")
    print("Press Ctrl+C to stop.")
    
    try:
        await server.run()
    except KeyboardInterrupt:
        print("\\nShutting down GitScribe server...")


async def example_rag_search():
    """Example: Demonstrate RAG search functionality."""
    
    from gitscribe.rag import RAGSystem
    
    config = GitScribeConfig()
    setup_logging(debug=True)
    logger = logging.getLogger(__name__)
    
    # Initialize RAG system
    rag = RAGSystem(config)
    await rag.initialize()
    
    # Sample documents for indexing
    sample_docs = [
        {
            "content": "React is a JavaScript library for building user interfaces. It uses a component-based architecture.",
            "title": "React Introduction",
            "source": "react-docs",
            "url": "https://reactjs.org/docs"
        },
        {
            "content": "Vue.js is a progressive JavaScript framework. It is incrementally adoptable and focuses on the view layer.",
            "title": "Vue.js Guide", 
            "source": "vue-docs",
            "url": "https://vuejs.org/guide"
        },
        {
            "content": "Python is a high-level programming language. It emphasizes code readability and simplicity.",
            "title": "Python Tutorial",
            "source": "python-docs", 
            "url": "https://python.org/tutorial"
        }
    ]
    
    # Index the documents
    indexed_count = await rag.index_documents(sample_docs)
    logger.info(f"Indexed {indexed_count} sample documents")
    
    # Perform some searches
    queries = [
        "How to build user interfaces?",
        "What is a progressive framework?",
        "Tell me about Python programming"
    ]
    
    for query in queries:
        logger.info(f"\\nSearching for: {query}")
        results = await rag.search(query, limit=2)
        
        for i, result in enumerate(results, 1):
            logger.info(f"  Result {i}: {result['metadata'].get('title', 'Unknown')}")
            logger.info(f"    Score: {result['relevance_score']:.3f}")
            logger.info(f"    Content: {result['content'][:100]}...")
    
    # Cleanup
    await rag.cleanup()


async def main():
    """Run examples."""
    
    print("GitScribe Examples")
    print("==================")
    print()
    print("1. Scrape Repository Documentation")
    print("2. Run MCP Server")
    print("3. RAG Search Demo")
    print("4. All Examples")
    print()
    
    choice = input("Select an example (1-4): ").strip()
    
    if choice == "1":
        await example_scrape_repository()
    elif choice == "2":
        await example_mcp_server()
    elif choice == "3":
        await example_rag_search()
    elif choice == "4":
        print("Running all examples...")
        await example_scrape_repository()
        print("\\n" + "="*50 + "\\n")
        await example_rag_search()
    else:
        print("Invalid choice. Please select 1-4.")


if __name__ == "__main__":
    asyncio.run(main())
