#!/usr/bin/env python3
"""
Command Line Interface for GitScribe.
Provides tools for testing and managing the GitScribe server.
"""

import asyncio
import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional

from .config import GitScribeConfig
from .server import GitScribeServer
from .scraper import DocumentationScraper
from .rag import RAGSystem
from .git_integration import GitIntegration, create_git_integration
from .utils import setup_logging


def setup_cli_logging(verbose: bool = False):
    """Setup logging for CLI operations."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )


async def cmd_server(args):
    """Start the GitScribe MCP server."""
    config = GitScribeConfig.from_env()
    config.debug = args.debug
    
    setup_logging(config.debug)
    logger = logging.getLogger(__name__)
    
    logger.info(f"Starting GitScribe MCP Server v{config.server_version}")
    
    server = GitScribeServer(config)
    try:
        await server.start()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        # Check if this is a TaskGroup error during shutdown
        if "TaskGroup" in str(e) and "unhandled errors" in str(e):
            logger.debug(f"TaskGroup cleanup issue during shutdown: {e}")
            # This is a known issue with async cleanup, not a real error
        else:
            logger.error(f"Server error: {e}")
            # Ensure proper cleanup
            try:
                await server.stop()
            except Exception as cleanup_error:
                logger.debug(f"Cleanup error: {cleanup_error}")
            raise


async def cmd_scrape(args):
    """Scrape documentation from a URL."""
    config = GitScribeConfig.from_env()
    config.debug = args.verbose
    
    setup_cli_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    scraper = DocumentationScraper(config)
    
    try:
        logger.info(f"Scraping documentation from: {args.url}")
        documents = await scraper.scrape_documentation(
            url=args.url,
            max_depth=args.depth,
            supported_formats=args.formats or config.supported_formats
        )
        
        logger.info(f"Successfully scraped {len(documents)} documents")
        
        if args.output:
            output_path = Path(args.output)
            with open(output_path, 'w') as f:
                json.dump(documents, f, indent=2, default=str)
            logger.info(f"Results saved to {output_path}")
        else:
            # Print summary
            for doc in documents[:5]:  # Show first 5
                print(f"- {doc.get('title', 'Untitled')}: {doc.get('url', 'No URL')}")
            if len(documents) > 5:
                print(f"... and {len(documents) - 5} more documents")
                
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        sys.exit(1)


async def cmd_index(args):
    """Index scraped documents into the RAG system."""
    config = GitScribeConfig.from_env()
    config.debug = args.verbose
    
    setup_cli_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    # Load documents from file
    if not Path(args.input).exists():
        logger.error(f"Input file not found: {args.input}")
        sys.exit(1)
    
    with open(args.input, 'r') as f:
        documents = json.load(f)
    
    # Initialize RAG system
    rag_system = RAGSystem(config)
    await rag_system.initialize()
    
    try:
        logger.info(f"Indexing {len(documents)} documents...")
        indexed_count = await rag_system.index_documents(documents)
        logger.info(f"Successfully indexed {indexed_count} documents")
        
        # Show stats
        stats = await rag_system.get_collection_stats()
        print(f"Collection Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
            
    except Exception as e:
        logger.error(f"Indexing failed: {e}")
        sys.exit(1)
    finally:
        await rag_system.cleanup()


async def cmd_search(args):
    """Search indexed documents."""
    config = GitScribeConfig.from_env()
    config.debug = args.verbose
    
    setup_cli_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    # Initialize RAG system
    rag_system = RAGSystem(config)
    await rag_system.initialize()
    
    try:
        logger.info(f"Searching for: {args.query}")
        results = await rag_system.search(
            query=args.query,
            limit=args.limit,
            filters={}
        )
        
        print(f"Found {len(results)} results:\n")
        
        for i, result in enumerate(results, 1):
            metadata = result['metadata']
            score = result['relevance_score']
            content = result['content'][:200] + "..." if len(result['content']) > 200 else result['content']
            
            print(f"{i}. {metadata.get('title', 'Untitled')} (Score: {score:.3f})")
            print(f"   URL: {metadata.get('url', 'No URL')}")
            print(f"   Content: {content}")
            print()
            
    except Exception as e:
        logger.error(f"Search failed: {e}")
        sys.exit(1)
    finally:
        await rag_system.cleanup()


async def cmd_repo_info(args):
    """Get information about a Git repository."""
    config = GitScribeConfig.from_env()
    config.debug = args.verbose
    
    setup_cli_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    git_integration = GitIntegration(config)
    
    try:
        repo = git_integration.parse_git_url(args.url)
        if not repo:
            logger.error(f"Could not parse Git URL: {args.url}")
            sys.exit(1)
        
        logger.info(f"Analyzing repository: {repo.url}")
        
        # Get repository info
        repo_info = git_integration.get_repository_info(repo)
        structure = git_integration.discover_documentation_structure(repo)
        
        print(f"Repository: {repo.owner}/{repo.repo}")
        print(f"Platform: {repo.platform}")
        print(f"Branch: {repo.branch}")
        print(f"Description: {repo_info.get('description', 'No description')}")
        print()
        
        print("Documentation Structure:")
        for category, files in structure.items():
            if isinstance(files, list) and files:
                print(f"  {category}: {len(files)} files")
                for file in files[:3]:  # Show first 3
                    print(f"    - {file.get('path', 'Unknown')}")
                if len(files) > 3:
                    print(f"    ... and {len(files) - 3} more")
        
    except Exception as e:
        logger.error(f"Repository analysis failed: {e}")
        sys.exit(1)


async def cmd_clear(args):
    """Clear the RAG collection."""
    config = GitScribeConfig.from_env()
    config.debug = args.verbose
    
    setup_cli_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    if not args.confirm:
        response = input("Are you sure you want to clear all indexed documents? (y/N): ")
        if response.lower() != 'y':
            logger.info("Operation cancelled")
            return
    
    # Initialize RAG system
    rag_system = RAGSystem(config)
    await rag_system.initialize()
    
    try:
        await rag_system.clear_collection()
        logger.info("Collection cleared successfully")
    except Exception as e:
        logger.error(f"Clear operation failed: {e}")
        sys.exit(1)
    finally:
        await rag_system.cleanup()


def create_parser():
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        description="GitScribe - Documentation Scraping and RAG MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  gitscribe server                           # Start MCP server
  gitscribe scrape https://docs.python.org  # Scrape documentation
  gitscribe search "async await python"      # Search indexed docs
  gitscribe repo-info https://github.com/microsoft/vscode  # Analyze repo
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Server command
    server_parser = subparsers.add_parser('server', help='Start the MCP server')
    server_parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    server_parser.set_defaults(func=cmd_server)
    
    # Scrape command
    scrape_parser = subparsers.add_parser('scrape', help='Scrape documentation')
    scrape_parser.add_argument('url', help='URL to scrape')
    scrape_parser.add_argument('--depth', type=int, default=3, help='Maximum crawl depth')
    scrape_parser.add_argument('--formats', nargs='+', help='Supported file formats')
    scrape_parser.add_argument('--output', '-o', help='Output file for results')
    scrape_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    scrape_parser.set_defaults(func=cmd_scrape)
    
    # Index command
    index_parser = subparsers.add_parser('index', help='Index documents into RAG system')
    index_parser.add_argument('input', help='JSON file with scraped documents')
    index_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    index_parser.set_defaults(func=cmd_index)
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search indexed documents')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--limit', type=int, default=10, help='Maximum results')
    search_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    search_parser.set_defaults(func=cmd_search)
    
    # Repository info command
    repo_parser = subparsers.add_parser('repo-info', help='Analyze Git repository')
    repo_parser.add_argument('url', help='Repository URL')
    repo_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    repo_parser.set_defaults(func=cmd_repo_info)
    
    # Clear command
    clear_parser = subparsers.add_parser('clear', help='Clear RAG collection')
    clear_parser.add_argument('--confirm', action='store_true', help='Skip confirmation')
    clear_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    clear_parser.set_defaults(func=cmd_clear)
    
    return parser


async def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Run the selected command
    await args.func(args)


def cli_main():
    """Entry point for setuptools console script."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli_main()
