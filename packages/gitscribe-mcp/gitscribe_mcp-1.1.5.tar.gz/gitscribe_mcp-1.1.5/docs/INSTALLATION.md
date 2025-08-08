# Installation Guide

This guide will help you install and set up GitScribe on your system.

## Prerequisites

- Python 3.9 or higher
- Git (for repository cloning)
- (Optional) GitHub/GitLab tokens for private repositories

## Installation Methods

### Method 1: Using uv (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-username/gitscribe.git
cd gitscribe

# Install with uv
uv sync

# Activate the environment
uv shell
```

### Method 2: Using pip

```bash
# Clone the repository
git clone https://github.com/your-username/gitscribe.git
cd gitscribe

# Install in development mode
pip install -e .

# Or install from PyPI (when published)
pip install gitscribe-mcp
```

### Method 3: From Source

```bash
# Clone the repository
git clone https://github.com/your-username/gitscribe.git
cd gitscribe

# Install dependencies
pip install -r requirements-gitscribe.txt
```

## Configuration

### Environment Variables

Create a `.env` file in your project directory or set environment variables:

```bash
# Basic configuration
GITSCRIBE_DEBUG=false
GITSCRIBE_MAX_DEPTH=3
GITSCRIBE_MAX_PAGES=100
GITSCRIBE_REQUEST_DELAY=1.0
GITSCRIBE_TIMEOUT=30

# RAG system configuration
GITSCRIBE_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
GITSCRIBE_CHUNK_SIZE=1000
GITSCRIBE_CHUNK_OVERLAP=200
GITSCRIBE_CHROMA_DIR=./chroma_db

# Rate limiting
GITSCRIBE_RATE_LIMIT=60
GITSCRIBE_CONCURRENT_REQUESTS=5

# Git platform tokens (optional, for private repos)
GITHUB_TOKEN=your_github_personal_access_token
GITLAB_TOKEN=your_gitlab_access_token
```

### Creating Tokens

#### GitHub Token
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate a new token with `repo` and `public_repo` scopes
3. Copy the token and set it as `GITHUB_TOKEN`

#### GitLab Token
1. Go to GitLab User Settings → Access Tokens
2. Create a token with `read_repository` scope
3. Copy the token and set it as `GITLAB_TOKEN`

## Verification

Test your installation:

```bash
# Check if GitScribe is installed
gitscribe --help

# Test the server (Ctrl+C to stop)
gitscribe server --debug

# Test scraping (in another terminal)
gitscribe scrape https://docs.python.org --depth 1 --output test.json
```

## Troubleshooting

### Common Issues

#### 1. Module Import Errors
```bash
# Make sure you're in the right environment
which python
pip list | grep -E "(gitscribe|chromadb|sentence-transformers)"
```

#### 2. ChromaDB Issues
```bash
# Clear ChromaDB cache if needed
rm -rf ./chroma_db
```

#### 3. Network/Timeout Issues
```bash
# Increase timeout and reduce concurrency
export GITSCRIBE_TIMEOUT=60
export GITSCRIBE_CONCURRENT_REQUESTS=2
```

#### 4. Memory Issues
```bash
# Reduce chunk size and embedding dimensions
export GITSCRIBE_CHUNK_SIZE=500
export GITSCRIBE_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L12-v2
```

### Getting Help

- Check the [FAQ](FAQ.md)
- Open an issue on [GitHub](https://github.com/your-username/gitscribe/issues)
- Join our discussions on [GitHub Discussions](https://github.com/your-username/gitscribe/discussions)

## Next Steps

Once installed, check out:
- [Usage Guide](USAGE.md) for detailed usage instructions
- [Configuration Guide](CONFIGURATION.md) for advanced configuration
- [Examples](../examples/) for code examples
