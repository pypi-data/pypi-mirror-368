"""
GitScribe: Web Scraping RAG MCP Server for Git-based Documentation

A Model Context Protocol (MCP) server that enables intelligent web scraping
of Git-based documentation with Retrieval Augmented Generation (RAG) capabilities.
"""

__version__ = "1.0.0"
__author__ = "AI Assistant"
__email__ = "ai@example.com"
__description__ = "Web Scraping RAG MCP Server for Git-based Documentation"

from .server import GitScribeServer
from .scraper import DocumentationScraper
from .rag import RAGSystem

__all__ = [
    "GitScribeServer",
    "DocumentationScraper", 
    "RAGSystem"
]
