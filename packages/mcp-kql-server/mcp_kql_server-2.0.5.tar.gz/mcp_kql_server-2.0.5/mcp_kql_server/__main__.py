#!/usr/bin/env python3
"""
MCP KQL Server - Main Entry Point

This module provides the main entry point for running the MCP KQL Server
as a Python module using: python -m mcp_kql_server

Author: Arjun Trivedi
Email: arjuntrivedi42@yahoo.com
"""

import sys
import logging
from pathlib import Path

def main():
    """Main entry point for the MCP KQL Server."""
    try:
        # Import the server after ensuring proper setup
        from .mcp_server import main as server_main
        
        # Run the server
        server_main()
        
    except ImportError as e:
        logging.error(f"Failed to import MCP server: {e}")
        print("Error: Missing dependencies. Please install the package with:")
        print("  pip install mcp-kql-server")
        sys.exit(1)
        
    except Exception as e:
        logging.error(f"Failed to start MCP KQL Server: {e}")
        print(f"Error starting MCP KQL Server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()