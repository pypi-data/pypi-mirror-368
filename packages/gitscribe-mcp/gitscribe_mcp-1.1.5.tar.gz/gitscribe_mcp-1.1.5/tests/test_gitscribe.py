"""
Test suite for GitScribe components.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from gitscribe.config import GitScribeConfig
from gitscribe.git_integration import GitIntegration, GitRepository
from gitscribe.parsers import DocumentParserFactory, MarkdownParser
from gitscribe.utils import chunk_text, clean_text, is_valid_url


class TestGitScribeConfig:
    """Test GitScribeConfig class."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = GitScribeConfig()
        
        assert config.server_name == "gitscribe"
        assert config.server_version == "1.0.0"
        assert config.max_depth == 3
        assert config.timeout == 30
        assert "html" in config.supported_formats
        assert "github.com" in config.git_platforms
    
    def test_config_from_env(self):
        """Test configuration from environment variables."""
        with patch.dict('os.environ', {
            'GITSCRIBE_DEBUG': 'true',
            'GITSCRIBE_MAX_DEPTH': '5',
            'GITSCRIBE_TIMEOUT': '60'
        }):
            config = GitScribeConfig.from_env()
            
            assert config.debug is True
            assert config.max_depth == 5
            assert config.timeout == 60
    
    def test_get_headers(self):
        """Test HTTP headers generation."""
        config = GitScribeConfig()
        headers = config.get_headers()
        
        assert "User-Agent" in headers
        assert "GitScribe" in headers["User-Agent"]
        assert headers["Accept"] == "text/html,application/xhtml+xml,text/markdown,text/plain"
    
    def test_is_supported_format(self):
        """Test file format support checking."""
        config = GitScribeConfig()
        
        assert config.is_supported_format("readme.md") is True
        assert config.is_supported_format("index.html") is True
        assert config.is_supported_format("script.py") is True
        assert config.is_supported_format("image.png") is False
    
    def test_should_ignore(self):
        """Test path ignoring logic."""
        config = GitScribeConfig()
        
        assert config.should_ignore("node_modules/package.json") is True
        assert config.should_ignore("venv/lib/python") is True
        assert config.should_ignore("src/main.py") is False


class TestGitIntegration:
    """Test GitIntegration class."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return GitScribeConfig()
    
    @pytest.fixture
    def git_integration(self, config):
        """Create GitIntegration instance."""
        return GitIntegration(config)
    
    def test_parse_github_url(self, git_integration):
        """Test parsing GitHub URLs."""
        url = "https://github.com/microsoft/vscode"
        repo = git_integration.parse_git_url(url)
        
        assert repo is not None
        assert repo.platform == "github.com"
        assert repo.owner == "microsoft"
        assert repo.repo == "vscode"
        assert repo.branch == "main"
    
    def test_parse_github_url_with_branch(self, git_integration):
        """Test parsing GitHub URLs with specific branch."""
        url = "https://github.com/microsoft/vscode/tree/release/1.80"
        repo = git_integration.parse_git_url(url)
        
        assert repo is not None
        assert repo.branch == "release/1.80"
    
    def test_parse_gitlab_url(self, git_integration):
        """Test parsing GitLab URLs."""
        url = "https://gitlab.com/gitlab-org/gitlab"
        repo = git_integration.parse_git_url(url)
        
        assert repo is not None
        assert repo.platform == "gitlab.com"
        assert repo.owner == "gitlab-org"
        assert repo.repo == "gitlab"
    
    def test_parse_invalid_url(self, git_integration):
        """Test parsing invalid URLs."""
        url = "not-a-valid-url"
        repo = git_integration.parse_git_url(url)
        
        assert repo is None


class TestDocumentParsers:
    """Test document parsing functionality."""
    
    @pytest.fixture
    def parser_factory(self):
        """Create parser factory."""
        return DocumentParserFactory()
    
    def test_markdown_parser_detection(self, parser_factory):
        """Test Markdown parser detection."""
        content = "# Hello World\\n\\nThis is markdown content."
        parser = parser_factory.get_parser("readme.md", content)
        
        assert isinstance(parser, MarkdownParser)
    
    def test_markdown_parsing(self, parser_factory):
        """Test Markdown content parsing."""
        content = """# Sample Document
        
This is a sample markdown document with:

- Lists
- **Bold text**
- `code snippets`

## Code Block

```python
def hello():
    print("Hello, World!")
```

[Link to example](https://example.com)
"""
        
        parser = parser_factory.get_parser("sample.md", content)
        doc = parser.parse(content, "sample.md")
        
        assert doc.title == "Sample Document"
        assert len(doc.sections) >= 2
        assert len(doc.code_blocks) >= 1
        assert len(doc.links) >= 1
        assert doc.format_type == "markdown"
    
    def test_html_parser_detection(self, parser_factory):
        """Test HTML parser detection."""
        content = "<html><head><title>Test</title></head><body>Content</body></html>"
        parser = parser_factory.get_parser("index.html", content)
        
        assert parser is not None
        assert parser.can_parse("index.html", content)
    
    def test_code_parser_detection(self, parser_factory):
        """Test code parser detection."""
        content = "def main():\\n    print('Hello, World!')"
        parser = parser_factory.get_parser("script.py", content)
        
        assert parser is not None
        assert parser.can_parse("script.py", content)


class TestUtils:
    """Test utility functions."""
    
    def test_clean_text(self):
        """Test text cleaning."""
        dirty_text = "  This   has    excessive   whitespace  "
        clean = clean_text(dirty_text)
        
        assert clean == "This has excessive whitespace"
    
    def test_chunk_text(self):
        """Test text chunking."""
        text = " ".join([f"word{i}" for i in range(100)])
        chunks = chunk_text(text, chunk_size=20, overlap=5)
        
        assert len(chunks) > 1
        assert chunks[0]['word_count'] == 20
        assert chunks[0]['start_word'] == 0
        assert chunks[1]['start_word'] == 15  # 20 - 5 overlap
    
    def test_is_valid_url(self):
        """Test URL validation."""
        assert is_valid_url("https://example.com") is True
        assert is_valid_url("http://localhost:3000") is True
        assert is_valid_url("not-a-url") is False
        assert is_valid_url("") is False
    
    def test_chunk_text_small_input(self):
        """Test chunking with small input."""
        text = "short text"
        chunks = chunk_text(text, chunk_size=100)
        
        assert len(chunks) == 1
        assert chunks[0]['text'] == text


@pytest.mark.asyncio
class TestAsyncComponents:
    """Test async components."""
    
    async def test_rag_initialization(self):
        """Test RAG system initialization."""
        # This would require actual RAG implementation
        # For now, just test that the import works
        try:
            from gitscribe.rag import GitScribeRAG
            config = GitScribeConfig()
            rag = GitScribeRAG(config)
            # Test basic initialization without actually connecting to DB
            assert rag.config == config
        except ImportError:
            pytest.skip("RAG module not fully implemented")


# Test fixtures and utilities
@pytest.fixture
def sample_markdown_content():
    """Sample Markdown content for testing."""
    return """---
title: Sample Document
author: Test Author
tags: [sample, test]
---

# Sample Document

This is a sample document for testing purposes.

## Introduction

This document contains various elements:

- Lists
- **Bold text**
- *Italic text*
- `inline code`

### Code Example

```python
def hello_world():
    print("Hello, World!")
    return True
```

## Links and References

- [Python Documentation](https://docs.python.org/)
- [GitHub](https://github.com)

![Sample Image](https://example.com/image.png)

## Conclusion

This concludes our sample document.
"""


@pytest.fixture
def sample_html_content():
    """Sample HTML content for testing."""
    return """<!DOCTYPE html>
<html>
<head>
    <title>Sample HTML Document</title>
    <meta name="description" content="A sample HTML document">
</head>
<body>
    <h1>Sample HTML Document</h1>
    
    <p>This is a paragraph with <strong>bold text</strong> and <em>italic text</em>.</p>
    
    <h2>Code Example</h2>
    <pre><code class="python">
def example():
    return "Hello, World!"
    </code></pre>
    
    <h2>Links</h2>
    <ul>
        <li><a href="https://example.com">Example Link</a></li>
        <li><a href="https://python.org">Python</a></li>
    </ul>
    
    <img src="https://example.com/image.jpg" alt="Sample Image">
</body>
</html>"""


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
