"""
Configuration settings for GitScribe MCP Server.
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass 
class GitScribeConfig:
    """Configuration class for GitScribe server."""
    
    # Server settings
    server_name: str = "gitscribe"
    server_version: str = "1.0.0"
    debug: bool = False
    
    # Scraping settings
    max_depth: int = 3
    max_pages: int = 100
    request_delay: float = 1.0
    timeout: int = 30
    user_agent: str = "GitScribe/1.0.0 (Documentation Scraper)"
    
    # RAG system settings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_results: int = 10
    similarity_threshold: float = 0.5
    
    # ChromaDB settings
    chroma_persist_directory: str = "./chroma_db"
    chroma_collection_name: str = "gitscribe_docs"
    
    # Supported file formats
    supported_formats: List[str] = field(default_factory=lambda: [
        "html", "htm", "md", "markdown", "rst", "txt",
        "py", "js", "ts", "java", "cpp", "c", "go", "rs"
    ])
    
    # Git platforms
    git_platforms: List[str] = field(default_factory=lambda: [
        "github.com", "gitlab.com", "bitbucket.org", "dev.azure.com"
    ])
    
    # Rate limiting
    rate_limit_per_minute: int = 60
    concurrent_requests: int = 5
    
    # Content filters
    ignore_patterns: List[str] = field(default_factory=lambda: [
        "*/node_modules/*", "*/venv/*", "*/env/*", "*/.git/*",
        "*/build/*", "*/dist/*", "*/__pycache__/*", "*.pyc"
    ])
    
    @classmethod
    def from_env(cls) -> "GitScribeConfig":
        """Create configuration from environment variables."""
        return cls(
            debug=os.getenv("GITSCRIBE_DEBUG", "false").lower() == "true",
            max_depth=int(os.getenv("GITSCRIBE_MAX_DEPTH", "3")),
            max_pages=int(os.getenv("GITSCRIBE_MAX_PAGES", "100")),
            request_delay=float(os.getenv("GITSCRIBE_REQUEST_DELAY", "1.0")),
            timeout=int(os.getenv("GITSCRIBE_TIMEOUT", "30")),
            embedding_model=os.getenv("GITSCRIBE_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
            chunk_size=int(os.getenv("GITSCRIBE_CHUNK_SIZE", "1000")),
            chunk_overlap=int(os.getenv("GITSCRIBE_CHUNK_OVERLAP", "200")),
            chroma_persist_directory=os.getenv("GITSCRIBE_CHROMA_DIR", "./chroma_db"),
            rate_limit_per_minute=int(os.getenv("GITSCRIBE_RATE_LIMIT", "60")),
            concurrent_requests=int(os.getenv("GITSCRIBE_CONCURRENT_REQUESTS", "5"))
        )
    
    def get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for requests."""
        return {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,text/markdown,text/plain",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive"
        }
    
    def is_supported_format(self, file_path: str) -> bool:
        """Check if file format is supported."""
        extension = file_path.split('.')[-1].lower()
        return extension in self.supported_formats
    
    def should_ignore(self, path: str) -> bool:
        """Check if path should be ignored based on patterns."""
        import fnmatch
        return any(fnmatch.fnmatch(path, pattern) for pattern in self.ignore_patterns)
