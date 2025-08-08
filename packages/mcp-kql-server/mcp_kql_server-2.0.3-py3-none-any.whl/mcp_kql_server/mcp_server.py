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
from .schema_memory import (
    extract_tables_from_query,
    get_context_for_tables,
    update_memory_after_query,
    _normalize_cluster_uri,
)
from .unified_memory import get_unified_memory
from .constants import SERVER_NAME, __version__, ERROR_MESSAGES, SUCCESS_MESSAGES
from .utils import format_error_message, is_debug_mode

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

class SchemaMemoryResult(BaseModel):
    cluster_uri: str
    database_count: int
    total_tables: int
    memory_file_path: str
    timestamp: str
    discovery_summary: Dict[str, Any]

class SchemaMemoryOutput(BaseModel):
    status: str
    result: Optional[SchemaMemoryResult] = None
    error: Optional[str] = None

# Note: Authentication check moved to tool execution to avoid import-time failures

# Define the MCP server
server = FastMCP(
    name=SERVER_NAME
)

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
        viz_data = None
        context_tokens = None
        for row in result:
            if "visualization" in row:
                viz_data = row.get("visualization")
                if "schema_context" in row:
                    context_tokens = row.get("schema_context", {}).get("context_tokens")
                break
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

# Define the schema memory tool
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
    if is_debug_mode():
        logger.debug("Received schema memory request: %s", input.dict())
    
    cluster_uri = input.cluster_uri.strip()
    if not cluster_uri:
        return SchemaMemoryOutput(status="error", error="Cluster URI cannot be empty")

    try:
        from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
        
        # Use unified memory system for schema discovery
        memory = get_unified_memory(input.memory_path)
        
        # Normalize cluster URI
        normalized_uri = _normalize_cluster_uri(cluster_uri)
        
        # Connect to cluster and discover all tables
        kcsb = KustoConnectionStringBuilder.with_az_cli_authentication(normalized_uri)
        client = KustoClient(kcsb)
        
        total_tables = 0
        database_count = 0
        tables_discovered = []
        
        try:
            # Get list of databases
            databases_query = ".show databases"
            db_response = client.execute_mgmt("", databases_query)
            databases = []
            
            for row in db_response.primary_results[0]:
                db_name = row['DatabaseName']
                if db_name not in ['$systemdb']:  # Skip system databases
                    databases.append(db_name)
            
            database_count = len(databases)
            logger.info(f"Found {database_count} databases: {databases}")
            
            # For each database, discover tables and save to unified memory
            for db_name in databases:
                try:
                    # Get tables in database
                    tables_query = ".show tables"
                    table_response = client.execute_mgmt(db_name, tables_query)
                    
                    for table_row in table_response.primary_results[0]:
                        table_name = table_row['TableName']
                        try:
                            # Use unified memory system for schema discovery
                            if memory.discover_and_save_table_schema(normalized_uri, db_name, table_name):
                                tables_discovered.append(f"{db_name}.{table_name}")
                                total_tables += 1
                                logger.info(f"Discovered schema for {db_name}.{table_name}")
                            else:
                                logger.warning(f"Failed to discover schema for {db_name}.{table_name}")
                        except Exception as e:
                            logger.warning(f"Failed to discover schema for {db_name}.{table_name}: {str(e)}")
                            
                except Exception as e:
                    logger.warning(f"Failed to process database {db_name}: {str(e)}")
                    
        finally:
            client.close()
        
        # Get memory statistics
        memory_stats = memory.get_memory_stats()
        
        # Create summary
        discovery_summary = {
            "action": "discovered_unified_memory",
            "databases": databases,
            "total_tables": total_tables,
            "tables_discovered": tables_discovered,
            "memory_stats": memory_stats,
            "message": f"Successfully discovered {total_tables} tables across {database_count} databases using unified memory"
        }
        
        logger.info(f"Schema discovery completed successfully for {normalized_uri}")
        
        return SchemaMemoryOutput(
            status="success",
            result=SchemaMemoryResult(
                cluster_uri=normalized_uri,
                database_count=database_count,
                total_tables=total_tables,
                memory_file_path=str(memory.memory_path),
                timestamp=datetime.now().isoformat(),
                discovery_summary=discovery_summary
            )
        )
        
    except Exception as e:
        error_msg = format_error_message(e, "Schema memory discovery")
        logger.error(error_msg)
        return SchemaMemoryOutput(status="error", error=error_msg)

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