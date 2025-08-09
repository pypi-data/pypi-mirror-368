"""
MCP KQL Server - AI-Powered KQL Query Execution with Intelligent Schema Memory

A Model Context Protocol (MCP) server that provides intelligent KQL (Kusto Query Language)
query execution with AI-powered schema caching and context assistance for Azure Data Explorer clusters.

This package automatically sets up the required directories and configuration on import.

Author: Arjun Trivedi
Email: arjuntrivedi42@yahoo.com
"""

import os
import logging
from pathlib import Path

# Version information
__version__ = "2.0.5"
__author__ = "Arjun Trivedi"
__email__ = "arjuntrivedi42@yahoo.com"

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def _setup_memory_directories():
    """Automatically set up memory directories on package import."""
    try:
        from .utils import get_default_cluster_memory_path
        
        # Get and ensure memory path exists
        memory_path = get_default_cluster_memory_path()
        
        if memory_path.exists():
            logger.info(f"KQL MCP memory initialized at: {memory_path}")
        else:
            logger.warning(f"Could not initialize memory directory: {memory_path}")
            
    except Exception as e:
        logger.debug(f"Memory directory setup skipped: {e}")

def _suppress_azure_logs():
    """Suppress verbose Azure SDK logs by default."""
    try:
        # Set Azure Core to only show errors
        os.environ.setdefault('AZURE_CORE_ONLY_SHOW_ERRORS', 'true')
        
        # Suppress Azure SDK debug logs
        azure_loggers = [
            'azure.core.pipeline.policies.http_logging_policy',
            'azure.kusto.data',
            'urllib3.connectionpool',
            'azure.identity'
        ]
        
        for logger_name in azure_loggers:
            logging.getLogger(logger_name).setLevel(logging.WARNING)
            
    except Exception:
        pass  # Ignore if loggers don't exist yet

def _suppress_fastmcp_branding():
    """Suppress FastMCP branding and verbose output."""
    try:
        # Set environment variables to suppress FastMCP branding
        os.environ['FASTMCP_QUIET'] = 'true'
        os.environ['FASTMCP_NO_BANNER'] = 'true'
        os.environ['FASTMCP_SUPPRESS_BRANDING'] = 'true'
        os.environ['FASTMCP_NO_LOGO'] = 'true'
        os.environ['FASTMCP_SILENT'] = 'true'
        os.environ['NO_COLOR'] = 'true'
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        
        # Suppress FastMCP and related loggers
        fastmcp_loggers = [
            'fastmcp',
            'rich',
            'rich.console',
            'rich.progress'
        ]
        
        for logger_name in fastmcp_loggers:
            logging.getLogger(logger_name).setLevel(logging.ERROR)
            
    except Exception:
        pass  # Ignore if loggers don't exist yet

# Perform automatic setup on import
_suppress_fastmcp_branding()
_suppress_azure_logs()
_setup_memory_directories()

# Export main components
from .mcp_server import server
from .execute_kql import execute_kql_query
from .constants import __version__ as VERSION

__all__ = [
    'server',
    'execute_kql_query',
    'VERSION',
    '__version__'
]