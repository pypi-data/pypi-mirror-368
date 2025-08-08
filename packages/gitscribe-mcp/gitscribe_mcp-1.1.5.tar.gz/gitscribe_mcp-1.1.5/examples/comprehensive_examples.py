#!/usr/bin/env python3
"""
GitScribe Usage Examples

This file demonstrates various ways to use GitScribe for documentation
scraping, indexing, and search operations.
"""

import asyncio
import json
import logging
from pathlib import Path
import sys

# Add the parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from gitscribe.config import GitScribeConfig
from gitscribe.scraper import DocumentationScraper
from gitscribe.rag import RAGSystem
from gitscribe.git_integration import GitIntegration
from gitscribe.parsers import DocumentParserFactory
from gitscribe.utils import setup_logging


async def example_1_basic_scraping():
    """Example 1: Basic documentation scraping."""
    print("=== Example 1: Basic Documentation Scraping ===")
    
    config = GitScribeConfig()
    config.debug = True
    setup_logging(True)
    
    scraper = DocumentationScraper(config)
    
    # Scrape a small documentation site
    url = "https://docs.python.org/3/tutorial/"
    print(f"Scraping: {url}")
    
    documents = await scraper.scrape_documentation(
        url=url,
        max_depth=2,
        supported_formats=["html", "htm"]
    )
    
    print(f"Scraped {len(documents)} documents")
    
    # Show sample results
    for i, doc in enumerate(documents[:3]):
        print(f"\nDocument {i+1}:")
        print(f"  Title: {doc.get('title', 'No title')}")
        print(f"  URL: {doc.get('url', 'No URL')}")
        print(f"  Content length: {len(doc.get('content', ''))}")
    
    return documents


async def example_2_github_repository():
    """Example 2: Scraping a GitHub repository."""
    print("\n=== Example 2: GitHub Repository Scraping ===")
    
    config = GitScribeConfig()
    scraper = DocumentationScraper(config)
    
    # Scrape a popular GitHub repository
    repo_url = "https://github.com/pallets/flask"
    print(f"Scraping repository: {repo_url}")
    
    documents = await scraper.scrape_documentation(
        url=repo_url,
        max_depth=1,  # Only top-level files
        supported_formats=["md", "rst", "txt"]
    )
    
    print(f"Found {len(documents)} documentation files")
    
    # Group by file type
    by_type = {}
    for doc in documents:
        file_type = doc.get('file_type', 'unknown')
        by_type[file_type] = by_type.get(file_type, 0) + 1
    
    print("Files by type:")
    for file_type, count in by_type.items():
        print(f"  {file_type}: {count}")
    
    return documents


async def example_3_rag_indexing_and_search():
    """Example 3: RAG system indexing and search."""
    print("\n=== Example 3: RAG Indexing and Search ===")
    
    config = GitScribeConfig()
    config.chroma_persist_directory = "./example_chroma_db"
    
    # Create some sample documents
    sample_docs = [
        {
            "url": "https://example.com/doc1",
            "title": "Python Async Programming",
            "content": "Python async and await keywords allow you to write asynchronous code. Use async def to define coroutines and await to call them.",
            "code_blocks": [
                {
                    "language": "python",
                    "code": "async def main():\n    await some_function()\n    return 'done'",
                    "context": "Basic async function example"
                }
            ],
            "source_type": "website",
            "scraped_at": 1234567890
        },
        {
            "url": "https://example.com/doc2",
            "title": "FastAPI Documentation",
            "content": "FastAPI is a modern, fast web framework for building APIs with Python. It supports async/await and automatic API documentation.",
            "code_blocks": [
                {
                    "language": "python",
                    "code": "from fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get('/')\nasync def root():\n    return {'message': 'Hello World'}",
                    "context": "Basic FastAPI application"
                }
            ],
            "source_type": "website", 
            "scraped_at": 1234567890
        }
    ]
    
    # Initialize RAG system
    rag_system = RAGSystem(config)
    await rag_system.initialize()
    
    try:
        # Index documents
        print("Indexing sample documents...")
        indexed_count = await rag_system.index_documents(sample_docs)
        print(f"Indexed {indexed_count} documents")
        
        # Search examples
        queries = [
            "python async programming",
            "FastAPI web framework",
            "async def function examples",
            "API documentation"
        ]
        
        for query in queries:
            print(f"\nSearching for: '{query}'")
            results = await rag_system.search(query, limit=2)
            
            for i, result in enumerate(results, 1):
                metadata = result['metadata']
                score = result['relevance_score']
                content = result['content'][:100] + "..." if len(result['content']) > 100 else result['content']
                
                print(f"  {i}. {metadata.get('title', 'No title')} (score: {score:.3f})")
                print(f"     {content}")
        
        # Show collection stats
        stats = await rag_system.get_collection_stats()
        print(f"\nCollection stats: {stats}")
        
    finally:
        await rag_system.cleanup()


async def example_4_git_integration():
    """Example 4: Git platform integration."""
    print("\n=== Example 4: Git Platform Integration ===")
    
    config = GitScribeConfig()
    git_integration = GitIntegration(config)
    
    # Analyze different repository URLs
    test_urls = [
        "https://github.com/microsoft/vscode",
        "https://github.com/python/cpython",
        "https://gitlab.com/gitlab-org/gitlab"
    ]
    
    for url in test_urls:
        print(f"\nAnalyzing: {url}")
        
        # Parse the URL
        repo = git_integration.parse_git_url(url)
        if repo:
            print(f"  Platform: {repo.platform}")
            print(f"  Owner: {repo.owner}")
            print(f"  Repository: {repo.repo}")
            print(f"  Branch: {repo.branch}")
            
            # Get repository structure
            try:
                structure = git_integration.discover_documentation_structure(repo)
                print(f"  Documentation structure:")
                for category, files in structure.items():
                    if isinstance(files, list) and files:
                        print(f"    {category}: {len(files)} files")
            except Exception as e:
                print(f"  Error analyzing structure: {e}")
        else:
            print("  Could not parse repository URL")


async def example_5_document_parsing():
    """Example 5: Document parsing with different formats."""
    print("\n=== Example 5: Document Parsing ===")
    
    parser_factory = DocumentParserFactory()
    
    # Sample documents in different formats
    test_docs = {
        "sample.md": """# Sample Markdown Document

This is a **markdown** document with:

- Lists
- `code snippets`
- [links](https://example.com)

## Code Example

```python
def hello_world():
    print("Hello, World!")
    return True
```

That's all folks!
""",
        
        "sample.html": """<!DOCTYPE html>
<html>
<head>
    <title>Sample HTML Document</title>
</head>
<body>
    <h1>Sample HTML Document</h1>
    <p>This is an <strong>HTML</strong> document.</p>
    
    <h2>Code Example</h2>
    <pre><code class="python">
def greet(name):
    return f"Hello, {name}!"
    </code></pre>
    
    <p><a href="https://example.com">Visit Example</a></p>
</body>
</html>""",
        
        "sample.py": '''#!/usr/bin/env python3
"""
Sample Python file for parsing demonstration.
"""

def fibonacci(n):
    """Calculate the nth Fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

class Calculator:
    """A simple calculator class."""
    
    def add(self, a, b):
        """Add two numbers."""
        return a + b
    
    def multiply(self, a, b):
        """Multiply two numbers."""
        return a * b

if __name__ == "__main__":
    calc = Calculator()
    print(f"2 + 3 = {calc.add(2, 3)}")
'''
    }
    
    # Parse each document
    for filename, content in test_docs.items():
        print(f"\nParsing: {filename}")
        
        parsed_doc = parser_factory.parse_document(filename, content)
        
        if parsed_doc:
            print(f"  Title: {parsed_doc.title}")
            print(f"  Format: {parsed_doc.format_type}")
            print(f"  Sections: {len(parsed_doc.sections)}")
            print(f"  Code blocks: {len(parsed_doc.code_blocks)}")
            print(f"  Links: {len(parsed_doc.links)}")
            print(f"  Content length: {len(parsed_doc.content)}")
            
            # Show sections
            if parsed_doc.sections:
                print("  Section titles:")
                for section in parsed_doc.sections[:3]:
                    print(f"    - {section.get('title', 'No title')}")
            
            # Show code blocks
            if parsed_doc.code_blocks:
                print("  Code languages:")
                languages = [block.get('language', 'unknown') for block in parsed_doc.code_blocks]
                unique_langs = list(set(languages))
                print(f"    {', '.join(unique_langs)}")
        else:
            print("  Failed to parse document")


async def main():
    """Run all examples."""
    print("GitScribe Usage Examples")
    print("========================")
    
    examples = [
        # example_1_basic_scraping,  # Skip to avoid hitting real sites
        # example_2_github_repository,  # Skip to avoid GitHub API limits
        example_3_rag_indexing_and_search,
        example_4_git_integration,
        example_5_document_parsing,
    ]
    
    for i, example_func in enumerate(examples, 1):
        try:
            await example_func()
            print(f"\n✅ Example {i} completed successfully")
        except Exception as e:
            print(f"\n❌ Example {i} failed: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "="*50)
    
    print("\nAll examples completed! 🎉")


if __name__ == "__main__":
    asyncio.run(main())
