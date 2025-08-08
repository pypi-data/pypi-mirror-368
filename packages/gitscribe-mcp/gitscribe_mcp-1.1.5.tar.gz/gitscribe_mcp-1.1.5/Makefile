# GitScribe Makefile
# Provides shortcuts for common development tasks

.PHONY: help install test lint format clean run-server run-examples

# Default target
help:
	@echo "GitScribe Development Commands"
	@echo "=============================="
	@echo "install     - Install dependencies and setup development environment"
	@echo "test        - Run all tests"
	@echo "lint        - Run linting checks"
	@echo "format      - Format code with black"
	@echo "clean       - Clean up generated files"
	@echo "run-server  - Start the GitScribe MCP server"
	@echo "run-examples - Run usage examples"
	@echo "docs        - Generate documentation"
	@echo "build       - Build the package"
	@echo "publish     - Publish to PyPI"

# Development setup
install:
	@echo "Installing GitScribe for development..."
	uv sync
	@echo "Development environment ready!"

# Testing
test:
	@echo "Running tests..."
	uv run pytest -v
	@echo "Tests completed!"

test-coverage:
	@echo "Running tests with coverage..."
	uv run pytest --cov=gitscribe --cov-report=html --cov-report=term
	@echo "Coverage report generated in htmlcov/"

# Code quality
lint:
	@echo "Running linting checks..."
	uv run flake8 gitscribe tests
	uv run mypy gitscribe
	@echo "Linting completed!"

format:
	@echo "Formatting code..."
	uv run black gitscribe tests examples
	@echo "Code formatted!"

# Cleanup
clean:
	@echo "Cleaning up..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf chroma_db/
	rm -rf example_chroma_db/
	rm -rf workflow_chroma_db/
	@echo "Cleanup completed!"

# Running
run-server:
	@echo "Starting GitScribe MCP server..."
	uv run gitscribe server --debug

run-examples:
	@echo "Running usage examples..."
	uv run python examples/comprehensive_examples.py

# Documentation
docs:
	@echo "Generating documentation..."
	# Add documentation generation commands here
	@echo "Documentation would be generated here"

# Building and publishing
build:
	@echo "Building package..."
	uv build
	@echo "Package built in dist/"

publish: build
	@echo "Publishing to PyPI..."
	uv publish
	@echo "Package published!"

# Development utilities
check: lint test
	@echo "All checks passed!"

dev-setup: install
	@echo "Setting up git hooks and development tools..."
	# Add any additional development setup here
	@echo "Development setup complete!"

# Quick commands
quick-test:
	@echo "Running quick tests..."
	uv run pytest tests/test_config.py tests/test_utils.py -v

scrape-test:
	@echo "Testing scraping functionality..."
	uv run gitscribe scrape https://httpbin.org --depth 1 --output test_output.json
	@echo "Scraping test completed, output saved to test_output.json"

search-test:
	@echo "Testing search functionality..."
	uv run python -c "
import asyncio
from gitscribe.rag import RAGSystem
from gitscribe.config import GitScribeConfig

async def test():
    config = GitScribeConfig()
    rag = RAGSystem(config)
    await rag.initialize()
    stats = await rag.get_collection_stats()
    print(f'Collection stats: {stats}')
    await rag.cleanup()

asyncio.run(test())
"

# Version management
version-patch:
	@echo "Bumping patch version..."
	# Add version bumping logic here
	@echo "Version bumped!"

version-minor:
	@echo "Bumping minor version..."
	# Add version bumping logic here
	@echo "Version bumped!"

# CI/CD related
ci-test: test lint
	@echo "CI tests completed!"

# Database management
reset-db:
	@echo "Resetting ChromaDB..."
	rm -rf chroma_db/
	@echo "Database reset!"

# Docker commands (if using Docker)
docker-build:
	@echo "Building Docker image..."
	docker build -t gitscribe:latest .

docker-run:
	@echo "Running GitScribe in Docker..."
	docker run -it --rm gitscribe:latest

# Help for specific targets
help-install:
	@echo "Install target: Sets up development environment using uv"

help-test:
	@echo "Test target: Runs pytest with verbose output"

help-clean:
	@echo "Clean target: Removes build artifacts, cache files, and test databases"
