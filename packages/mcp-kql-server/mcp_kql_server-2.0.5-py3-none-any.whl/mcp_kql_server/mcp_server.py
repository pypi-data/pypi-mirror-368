"""
MCP KQL Server - Main Server Implementation

This module implements the FastMCP server with KQL query execution and schema memory tools.
Provides intelligent KQL query execution with AI-powered schema caching and context assistance.

Author: Arjun Trivedi
Email: arjuntrivedi42@yahoo.com
"""

import os
import sys
import logging
from datetime import datetime
from typing import List, Any, Union, Optional, Dict
from azure.kusto.data import KustoClient
from .memory import UnifiedSchemaMemory as UnifiedMemory

# Suppress all possible FastMCP branding output
os.environ['FASTMCP_QUIET'] = 'true'
os.environ['FASTMCP_NO_BANNER'] = 'true'
os.environ['FASTMCP_SUPPRESS_BRANDING'] = 'true'
os.environ['FASTMCP_NO_LOGO'] = 'true'
os.environ['FASTMCP_SILENT'] = 'true'
os.environ['NO_COLOR'] = 'true'
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Configure logging to suppress FastMCP and Rich logs
logging.getLogger('fastmcp').setLevel(logging.ERROR)
logging.getLogger('rich').setLevel(logging.ERROR)
logging.getLogger('rich.console').setLevel(logging.ERROR)

# Monkey patch rich console to suppress output
try:
    from rich.console import Console
    original_print = Console.print
    def suppressed_print(self, *args, **kwargs):
        # Only suppress if it contains FastMCP branding
        if args and isinstance(args[0], str):
            content = str(args[0])
            if 'FastMCP' in content or 'gofastmcp.com' in content or 'fastmcp.cloud' in content:
                return
        return original_print(self, *args, **kwargs)
    Console.print = suppressed_print
except:
    pass

from fastmcp import FastMCP
from pydantic import BaseModel
from .kql_auth import authenticate
from .execute_kql import execute_kql_query
from .memory import (
    get_unified_memory,
    get_context_for_tables,
    update_memory_after_query,
)
from .constants import SERVER_NAME, __version__, ERROR_MESSAGES, SUCCESS_MESSAGES
from .utils import format_error_message, is_debug_mode, extract_tables_from_query, normalize_cluster_uri as _normalize_cluster_uri

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for input and output schemas
class KQLInput(BaseModel):
    query: str
    visualize: bool = False
    cluster_memory_path: Optional[str] = None
    use_schema_context: bool = True

class KQLResult(BaseModel):
    columns: List[str]
    rows: List[List[Any]]
    row_count: int
    visualization: Optional[str] = None
    schema_context: Optional[List[str]] = None  # Now a list of AI tokens

class KQLOutput(BaseModel):
    status: str
    result: Optional[KQLResult] = None
    error: Optional[str] = None

class SchemaMemoryInput(BaseModel):
    cluster_uri: str
    memory_path: Optional[str] = None
    force_refresh: bool = False

class SchemaMemoryOutput(BaseModel):
    status: str
    message: str
    cluster_uri: str
    discovered_databases: Optional[int] = None
    discovered_tables: Optional[int] = None
    memory_location: Optional[str] = None

# Note: Authentication check moved to tool execution to avoid import-time failures

# Define the MCP server
server = FastMCP(
    name=SERVER_NAME
)

# Helper function for extracting visualization data
def _extract_viz_and_context(result: List[Dict[str, Any]]) -> (Optional[str], Optional[List[str]]):
    """Extracts visualization data and schema context from KQL results."""
    viz_data = None
    context_tokens = None
    for row in result:
        if "visualization" in row:
            viz_data = row.get("visualization")
            if "schema_context" in row:
                context_tokens = row.get("schema_context", {}).get("context_tokens")
            break
    return viz_data, context_tokens


# Define the enhanced KQL execution tool
@server.tool()
async def kql_execute(input: KQLInput) -> KQLOutput:
    """
    Execute a KQL query against an Azure Data Explorer cluster with intelligent schema context.

    Args:
        input: Input model containing query execution parameters:
            - query: The KQL query to execute (e.g., cluster('mycluster').database('mydb').MyTable | take 10)
            - visualize: If true, include a Markdown table visualization
            - cluster_memory_path: Optional custom path for cluster memory storage (default: %appdata%/KQL_MCP/cluster_memory)
            - use_schema_context: If true, automatically load schema context for AI assistance (default: True)

    Returns:
        KQLOutput: Output model with execution status, results, and optional visualization with schema context.
    """
    if is_debug_mode():
        logger.debug("Received KQL execute request: %s", input.dict())
    
    query = input.query
    if not query or not query.strip():
        return KQLOutput(status="error", error=ERROR_MESSAGES["empty_query"])

    try:
        # Extract relevant tables for context
        tables = extract_tables_from_query(query)
        schema_context = []
        if input.use_schema_context and tables:
            # Only load relevant table memory
            cluster_uri, database = None, None
            try:
                from .utils import extract_cluster_and_database_from_query
                cluster_uri, database = extract_cluster_and_database_from_query(query)
            except Exception:
                pass
            if cluster_uri and database:
                schema_context = get_context_for_tables(cluster_uri, database, tables, input.cluster_memory_path)
        result = execute_kql_query(
            query=query,
            visualize=input.visualize,
            cluster_memory_path=input.cluster_memory_path,
            use_schema_context=input.use_schema_context
        )
        # Separate data rows from visualization
        data_rows = [row for row in result if "visualization" not in row and "schema_context" not in row]
        viz_data, context_tokens = _extract_viz_and_context(result)
        table_response = KQLResult(
            columns=list(data_rows[0].keys()) if data_rows else [],
            rows=[list(row.values()) for row in data_rows],
            row_count=len(data_rows),
            visualization=viz_data,
            schema_context=context_tokens or schema_context
        )
        logger.info("Query executed successfully. Rows returned: %d", table_response.row_count)
        return KQLOutput(status="success", result=table_response)
    except Exception as e:
        error_msg = format_error_message(e, "KQL execution")
        logger.error(error_msg)
        return KQLOutput(status="error", error=error_msg)


@server.tool()
async def kql_schema_memory(input: SchemaMemoryInput) -> SchemaMemoryOutput:
    """
    Discover and manage cluster schema memory for AI-powered query assistance.

    This tool connects to a KQL cluster, discovers its schema (databases, tables, columns),
    generates AI-powered descriptions for each table, and stores the schema intelligence
    in persistent per-table memory for fast context retrieval.

    Args:
        input: Input model containing schema discovery parameters:
            - cluster_uri: URI of the KQL cluster to analyze (e.g., 'mycluster' or 'https://mycluster.kusto.windows.net')
            - memory_path: Optional custom path for schema storage (default: %appdata%/KQL_MCP/cluster_memory)
            - force_refresh: If true, rediscover schema even if cached version exists (default: False)

    Returns:
        SchemaMemoryOutput: Output model with discovery status, statistics, and memory file location.
    """
    try:
        memory = get_unified_memory(input.memory_path)
        
        success, db_count, table_count = memory.discover_and_save_cluster_schema(
            input.cluster_uri,
            force_refresh=input.force_refresh
        )

        if success:
            return SchemaMemoryOutput(
                status="success",
                message=f"Successfully discovered schema for {db_count} databases and {table_count} tables.",
                cluster_uri=input.cluster_uri,
                discovered_databases=db_count,
                discovered_tables=table_count,
                memory_location=str(memory.memory_path)
            )
        else:
            return SchemaMemoryOutput(
                status="error",
                message="Failed to discover cluster schema. Check logs for details.",
                cluster_uri=input.cluster_uri
            )
    except Exception as e:
        error_msg = format_error_message(e, "Schema memory discovery")
        logger.error(error_msg)
        return SchemaMemoryOutput(status="error", message=error_msg, cluster_uri=input.cluster_uri)


def main():
    """Main entry point for the MCP KQL Server."""
    print("Starting MCP KQL Server...", file=sys.stderr)
    sys.stderr.flush()
    
    # Check authentication before starting server
    print("Checking Azure authentication...", file=sys.stderr)
    sys.stderr.flush()
    
    auth_status = authenticate()
    if not auth_status.get("authenticated"):
        logger.error("Authentication failed: %s", auth_status.get("message"))
        print("Authentication failed. Please run 'az login' and try again.", file=sys.stderr)
        sys.stderr.flush()
        sys.exit(1)
    
    print("Authentication successful. Starting server...", file=sys.stderr)
    sys.stderr.flush()
    
    try:
        server.run()
    except KeyboardInterrupt:
        print("\nServer stopped by user.", file=sys.stderr)
        sys.stderr.flush()
    except Exception as e:
        logger.error(f"Server error: {e}")
        print(f"Server error: {e}", file=sys.stderr)
        sys.stderr.flush()
        sys.exit(1)

# Run the server
if __name__ == "__main__":
    main()