# GitScribe 📜

> *Scribing knowledge from the Git universe*

GitScribe is a powerful Model Context Protocol (MCP) server that enables intelligent web scraping of Git-based documentation with Retrieval Augmented Generation (RAG) capabilities. This tool helps code assistants and developers efficiently extract, process, and retrieve information from documentation websites, GitHub repositories, and other Git-based resources to accelerate application development.

## ✨ Features

- **🌐 Universal Git Support**: Works with GitHub, GitLab, Bitbucket, and Azure DevOps
- **🧠 Intelligent RAG System**: ChromaDB + Sentence Transformers for semantic search
- **📄 Multi-Format Parsing**: Markdown, HTML, reStructuredText, and source code files
- **⚡ High Performance**: Async scraping with intelligent rate limiting
- **🔧 MCP Integration**: Full Model Context Protocol compliance for AI assistants
- **📊 Rich CLI**: Command-line interface for testing and management
- **🎯 Smart Filtering**: Automatic content filtering and relevance scoring

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI (recommended)
pip install gitscribe-mcp

# Or install with uv (recommended for development)
uv sync

# Or install with pip for development
pip install -e .

# Or install dependencies manually
pip install -r requirements-gitscribe.txt
```

### Verify Installation

```bash
# Check if installation was successful
gitscribe-mcp --help

# Test the server (should start without errors)
gitscribe-mcp server --help
```

### Basic Usage

#### 1. Start the MCP Server
```bash
# Start the server for use with AI assistants
gitscribe-mcp server

# Or run directly with uv
uv run gitscribe-mcp server
```

#### 2. Scrape Documentation
```bash
# Scrape Python documentation
gitscribe-mcp scrape https://docs.python.org --depth 2 --output python_docs.json

# Scrape a GitHub repository
gitscribe-mcp scrape https://github.com/microsoft/vscode --formats md html rst
```

#### 3. Index Documents
```bash
# Index scraped documents into the RAG system
gitscribe-mcp index python_docs.json
```

#### 4. Search Documentation
```bash
# Search indexed documentation
gitscribe-mcp search "async await python examples"
gitscribe-mcp search "VSCode extension API" --limit 5
```

#### 5. Analyze Repositories
```bash
# Get repository information and structure
gitscribe-mcp repo-info https://github.com/microsoft/vscode
```

## 🤖 Using as MCP Server

GitScribe is designed to work as a Model Context Protocol (MCP) server with AI assistants like Claude Desktop. Once installed and configured, you can interact with it naturally through your AI assistant.

### Example Interactions

**Scraping Documentation:**
```
"Can you scrape the FastAPI documentation and index it for me?"
```

**Searching for Information:**
```
"Search the indexed documentation for examples of async database operations"
```

**Getting Code Examples:**
```
"Show me code examples for implementing JWT authentication in Python"
```

**Repository Analysis:**
```
"Analyze the structure of the React repository and tell me about its testing setup"
```

### Available MCP Tools

When configured as an MCP server, GitScribe provides these tools to AI assistants:

## 📋 MCP Tools

GitScribe provides the following MCP tools:

### `scrape_documentation`
Scrape and index documentation from a Git repository or website.

**Parameters:**
- `url` (string, required): Repository or documentation URL
- `depth` (integer, optional): Maximum crawling depth (default: 3)
- `formats` (array, optional): Supported document formats

### `search_documentation`
Search indexed documentation using semantic search.

**Parameters:**
- `query` (string, required): Natural language search query
- `limit` (integer, optional): Maximum number of results (default: 10)
- `filter` (object, optional): Filter criteria (language, framework, etc.)

### `get_code_examples`
Extract code examples related to a specific topic.

**Parameters:**
- `topic` (string, required): Programming topic or concept
- `language` (string, optional): Programming language filter
- `framework` (string, optional): Framework or library filter

## 🛠️ Configuration

GitScribe can be configured through environment variables:

```bash
# Server settings
export GITSCRIBE_DEBUG=true
export GITSCRIBE_MAX_DEPTH=3
export GITSCRIBE_MAX_PAGES=100

# RAG system settings
export GITSCRIBE_EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"
export GITSCRIBE_CHUNK_SIZE=1000
export GITSCRIBE_CHROMA_DIR="./chroma_db"

# Rate limiting
export GITSCRIBE_REQUEST_DELAY=1.0
export GITSCRIBE_CONCURRENT_REQUESTS=5

# Git platform authentication (optional)
export GITHUB_TOKEN="your_github_token"
export GITLAB_TOKEN="your_gitlab_token"
```

## 📖 Claude Desktop Integration

To use GitScribe as an MCP server with Claude Desktop, you need to configure it in your Claude Desktop settings.

### Prerequisites

First, install the package from PyPI:
```bash
pip install gitscribe-mcp
```

### Configuration

Add the following configuration to your Claude Desktop config file:

**MacOS:** `~/Library/Application\ Support/Claude/claude_desktop_config.json`  
**Windows:** `%APPDATA%/Claude/claude_desktop_config.json`

#### Using the PyPI Package (Recommended)
```json
{
  "mcpServers": {
    "gitscribe": {
      "command": "gitscribe-mcp",
      "args": ["server"],
      "env": {
        "GITSCRIBE_DEBUG": "false",
        "GITSCRIBE_MAX_DEPTH": "3",
        "GITSCRIBE_CHROMA_DIR": "./chroma_db"
      }
    }
  }
}
```

#### Using uvx (Alternative)
```json
{
  "mcpServers": {
    "gitscribe": {
      "command": "uvx",
      "args": ["gitscribe-mcp", "server"],
      "env": {
        "GITSCRIBE_DEBUG": "false"
      }
    }
  }
}
```

#### Development Configuration (Local Development)
```json
{
  "mcpServers": {
    "gitscribe": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/your/gitscribe",
        "run",
        "gitscribe-mcp",
        "server"
      ],
      "env": {
        "GITSCRIBE_DEBUG": "true"
      }
    }
  }
}
```

### Verification

After adding the configuration:

1. Restart Claude Desktop
2. Start a new conversation
3. You should see GitScribe available as an MCP server
4. Try using commands like: "Can you scrape the Python documentation and help me find examples of async/await?"

## 🧪 Development

### Building and Publishing

1. Sync dependencies:
```bash
uv sync
```

2. Build package:
```bash
uv build
```

3. Publish to PyPI:
```bash
uv publish
```

### Debugging

Use the [MCP Inspector](https://github.com/modelcontextprotocol/inspector) for debugging:

```bash
# Debug the PyPI package
npx @modelcontextprotocol/inspector gitscribe-mcp server

# Debug local development version
npx @modelcontextprotocol/inspector uv --directory /path/to/gitscribe run gitscribe-mcp server
```

### Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=gitscribe

# Run specific tests
uv run pytest tests/test_scraper.py
```

## 📚 Supported Formats

- **Documentation**: Markdown (`.md`), HTML (`.html`), reStructuredText (`.rst`)
- **Code Files**: Python (`.py`), JavaScript (`.js`), TypeScript (`.ts`), Java (`.java`), C++ (`.cpp`), Go (`.go`), Rust (`.rs`)
- **Configuration**: JSON, YAML, TOML
- **Web Content**: Dynamic HTML pages, static sites

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   MCP Client    │───▶│   MCP Server    │───▶│  Web Scraper    │
│ (Code Assistant)│    │   (GitScribe)   │    │ (Beautiful Soup)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   RAG System    │
                       │  - ChromaDB     │
                       │  - Embeddings   │
                       │  - Search       │
                       └─────────────────┘
```

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) for HTML parsing
- [ChromaDB](https://www.trychroma.com/) for vector database capabilities
- [Sentence Transformers](https://www.sbert.net/) for embeddings
- [Model Context Protocol](https://modelcontextprotocol.io/) for AI assistant integration

---

**GitScribe** - Making documentation accessible to AI assistants, one commit at a time! 🚀