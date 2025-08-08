#!/usr/bin/env python3
"""
GitScribe - Main entry point for the MCP server.
"""

import sys
import asyncio
import logging
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from gitscribe.cli import cli_main


def main():
    """Main entry point for GitScribe."""
    try:
        cli_main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
